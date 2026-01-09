import platform
import requests
import threading
from pathlib import Path
from packaging.version import Version
from tkinter import filedialog, messagebox

import torch
import customtkinter as ctk

from core.config import (
    PROJECT_NAME,
    PROJECT_VERSION,
    PROJECT_LICENSE,
    PROJECT_URL,
    PROJECT_LATEST_RELEASE_URL,
    DEBUG,
)
from core.paths import PATHS
from services.audio_extractor.service import AudioExtractorService
from services.subtitle_generator.service import SubtitleGeneratorService
from services.video_processor.service import VideoProcessorService
from services.transcriber.providers.whisper_provider import WhisperTranscriber
from services.transcriber.service import TranscriberService
from services.translator.providers.m2m100_provider import M2M100Translator
from services.translator.providers.google_provider import GoogleTranslator
from services.translator.providers.deepl_provider import DeepLTranslator
from services.translator.service import TranslatorService
from utils.file_handler import FileHandler
from utils.logger import Logger


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window settings
        self.title(f"{PROJECT_NAME}")
        self.iconbitmap(f"{self._get_icon_path()}")
        width, height = 400, 720
        scaling = ctk.ScalingTracker.get_window_scaling(self)
        x = (self.winfo_screenwidth() - width) * scaling / 2
        y = (self.winfo_screenheight() - height) * scaling / 2
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
        self.minsize(width, height)

        # Theme
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")

        # Variables
        self.video_path = ""
        self.processing = False

        # Logger
        self.logger = Logger()

        self.setup_ui()

        try:
            if self.is_update_available(PROJECT_VERSION):
                messagebox.showinfo(
                    title="Update Available",
                    message=(
                        "A new version of Ziro is available.\n"
                        "Please download the latest release from GitHub."
                    ),
                )
        except:
            self.after(100, self._show_error, "You are offline!")

    def setup_ui(self):
        # Title
        title_label = ctk.CTkLabel(
            self, text=f"{PROJECT_NAME}", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        # File selection frame
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(pady=20, padx=30, fill="x")

        self.file_label = ctk.CTkLabel(
            file_frame, text="No files selected", font=ctk.CTkFont(size=12)
        )
        self.file_label.pack(pady=10)

        self.select_btn = ctk.CTkButton(
            file_frame,
            text="Video selection",
            command=self.select_video,
            width=200,
            height=40,
        )
        self.select_btn.pack(pady=10)

        # Settings
        settings_frame = ctk.CTkFrame(self)
        settings_frame.pack(pady=20, padx=30, fill="both", expand=True)

        settings_label = ctk.CTkLabel(
            settings_frame, text="Settings", font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_label.pack(pady=10)

        ctk.CTkLabel(
            settings_frame,
            text=f"Using device: {"CUDA" if torch.cuda.is_available() else "CPU"}",
            font=ctk.CTkFont(size=12),
        ).pack()

        # Choosing a Transcription accuracy
        whisper_frame = ctk.CTkFrame(settings_frame)
        whisper_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            whisper_frame, text="Transcription accuracy:", font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=10)

        self.whisper_model = ctk.CTkOptionMenu(
            whisper_frame,
            values=[var.name.title() for var in WhisperTranscriber.Variant],
            width=150,
        )
        self.whisper_model.set(WhisperTranscriber.Variant.BASE.name.title())
        self.whisper_model.pack(side="right", padx=10)

        # Choosing a translation model
        trans_frame = ctk.CTkFrame(settings_frame)
        trans_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            trans_frame, text="Translation model:", font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=10)

        self.translation_model = ctk.CTkOptionMenu(
            trans_frame,
            values=["M2M100 418M", "M2M100 1.2B", "Google Translate", "DeepL"],
            command=lambda val: (
                self.after(100, self._show_error, "You are offline!")
                if val in ("Google Translate", "DeepL") and not self._check_internet()
                else None
            ),
            width=150,
        )
        self.translation_model.set("Google Translate")
        self.translation_model.pack(side="right", padx=10)

        # Choosing a translation model
        auth_key_frame = ctk.CTkFrame(settings_frame)
        auth_key_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            auth_key_frame, text="Auth key for DeepL:", font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=10)

        self.auth_key = ctk.CTkEntry(
            auth_key_frame,
            placeholder_text="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            width=150,
            border_width=0,
        )
        self.auth_key.pack(side="right", padx=10)

        # Checkboxes
        options_frame = ctk.CTkFrame(settings_frame)
        options_frame.pack(pady=10, padx=20, fill="x")

        self.embed_subtitles = ctk.CTkCheckBox(
            options_frame, text="Add subtitles to video", font=ctk.CTkFont(size=12)
        )
        self.embed_subtitles.pack(pady=5)
        self.embed_subtitles.select()

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, width=260)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self, text="Ready", wraplength=250, font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)

        # Processing button
        self.process_btn = ctk.CTkButton(
            self,
            text="Start processing",
            command=self.start_processing,
            width=300,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled",
        )
        self.process_btn.pack(pady=16)

        # Project info
        ctk.CTkLabel(
            self,
            text=f"{PROJECT_LICENSE}\nSource code: {PROJECT_URL}\n",
            font=ctk.CTkFont(size=10),
        ).pack()

    def select_video(self):
        """Select video file"""
        file_path = filedialog.askopenfilename(
            title="Video selection",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mkv *.mov *.flv"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            self.video_path = file_path
            self.file_label.configure(text=Path(file_path).name)
            self.process_btn.configure(state="normal")

    def update_status(self, message: str, progress: float):
        """Status and progress updates"""
        self.after(0, self._update_status_ui, message, progress)

    def _update_status_ui(self, message: str, progress: float):
        """Update UI from main thread"""
        self.status_label.configure(text=message)
        self.progress_bar.set(progress)

        progress_percent = int(progress * 100)
        self.title(f"{PROJECT_NAME} - {progress_percent}%")
        self.logger.info(message)

    def start_processing(self):
        """Start processing in a separate thread"""
        if self.processing:
            return

        if not self.video_path:
            messagebox.showwarning("Warning", "Please select a video file first")
            return

        self.processing = True
        self.process_btn.configure(state="disabled")

        self.disable_controls(True)

        # Run in a separate thread so that the UI does not freeze.
        thread = threading.Thread(target=self.process_video, daemon=True)
        thread.start()

    def process_video(self):
        """Full video processing"""
        try:
            video_name = Path(self.video_path).stem

            # 1. Sound extraction (0-20%)
            self.update_status("Extracting audio ...", 0.0)
            audio_extractor_service = AudioExtractorService()
            audio_path = audio_extractor_service.extract(self.video_path)
            self.update_status("Audio extracted", 0.2)

            # 2. Transcription (20-50%)
            self.update_status("Converting speech to text ...", 0.2)
            whisper_transcriber = WhisperTranscriber(
                WhisperTranscriber.Variant[self.whisper_model.get().upper()]
            )
            transcriber_service = TranscriberService(whisper_transcriber)
            transcription = transcriber_service.transcribe(audio_path, "en")
            segments_en = transcriber_service.get_segments(transcription)
            self.update_status("Transcription completed", 0.5)

            # 3. Save English subtitles
            srt_en_path = PATHS["temp"] / f"{video_name}_en.srt"
            subtitle_generator_service = SubtitleGeneratorService()
            subtitle_generator_service.generate_srt(segments_en, str(srt_en_path))

            # 4. Translation (50-80%)
            self.update_status("Translating into Persian ...", 0.5)
            if self.translation_model.get() == "Google Translate":
                translator = GoogleTranslator()
            elif self.translation_model.get() == "DeepL":
                translator = DeepLTranslator(self.auth_key.get())
            else:
                translator = M2M100Translator(M2M100Translator.Variant.SMALL)
            translator_service = TranslatorService(translator)

            texts_en = [seg["text"] for seg in segments_en]
            texts_fa = translator_service.translate(texts_en, "en", "fa")

            # Creating Persian segments
            segments_fa = []
            for seg_en, text_fa in zip(segments_en, texts_fa):
                segments_fa.append(
                    {"text": text_fa, "start": seg_en["start"], "end": seg_en["end"]}
                )

            self.update_status("Translation completed", 0.8)

            # 5. Save Persian subtitles
            srt_fa_path = PATHS["temp"] / f"{video_name}_fa.srt"
            subtitle_generator_service.generate_srt(segments_fa, str(srt_fa_path))

            # 7. Add subtitles to the video (80-100%)
            output_video = ""
            if self.embed_subtitles.get():
                self.update_status("Adding subtitles to video ...", 0.8)

                subtitle_paths = {"eng": str(srt_en_path), "per": str(srt_fa_path)}

                video_processor_service = VideoProcessorService()
                output_video = video_processor_service.add_subtitles(
                    self.video_path, subtitle_paths, f"{video_name}_subtitled.mkv"
                )

            self.update_status("Processing complete! ✓", 1.0)

            # Show success message
            self.after(
                100, self._show_success, srt_en_path, srt_fa_path, Path(output_video)
            )

        except RuntimeError as e:
            self.update_status(f"Error: Please try again", 0.0)
            self.title(f"{PROJECT_NAME} - Error")
            self.after(100, self._show_error, e)
            self.logger.error(f"{type(e)}: {e}")

        except Exception as e:
            self.update_status(f"Error: Close the app then open it again", 0.0)
            self.title(f"{PROJECT_NAME} - Error")
            self.after(100, self._show_error, e)
            self.logger.error(f"Unexpected error: {e}")

        finally:
            self.processing = False
            self.process_btn.configure(state="normal")
            self.disable_controls(False)
            if not DEBUG and self.embed_subtitles.get():
                try:
                    FileHandler.clean_temp_files()
                except RuntimeError as e:
                    self.logger.error(str(e))

    def disable_controls(self, disabled: bool):
        """Enable/disable UI controls during processing"""
        state = "disabled" if disabled else "normal"

        controls = [
            self.select_btn,
            self.whisper_model,
            self.translation_model,
            self.auth_key,
            self.embed_subtitles,
        ]

        for control in controls:
            control.configure(state=state)

    def _show_success(self, en: Path, fa: Path, ov: Path):
        message = (
            f"Processing complete!"
            f"{"\n\nVideo with subtitles: " + ov.name if self.embed_subtitles.get() else ""}"
        )
        if DEBUG or not self.embed_subtitles.get():
            message = (
                f"Processing complete!\n\n"
                f"English subtitles: {en.name}\n"
                f"Persian subtitles: {fa.name}"
                f"{"\nVideo with subtitles: " + ov.name if self.embed_subtitles.get() else ""}"
            )
        messagebox.showinfo("Success", message)
        FileHandler.open_path(
            ov.parent if self.embed_subtitles.get() else PATHS["temp"]
        )

    def _show_error(self, e):
        """Show error"""
        message = f"Error processing:\n{e}"
        messagebox.showerror("Error", message)

    def _check_internet(self):
        try:
            response = requests.get("https://www.google.com", timeout=3)
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    def _get_icon_path(self) -> Path:
        if platform.system() == "Windows":
            return PATHS["base"] / "assets" / "Ziro.ico"
        elif platform.system() == "Darwin":
            return PATHS["base"] / "assets" / "Ziro.icns"
        else:
            return PATHS["base"] / "assets" / "Ziro.png"

    def is_update_available(self, current_version: str) -> bool:
        response = requests.get(
            PROJECT_LATEST_RELEASE_URL, allow_redirects=True, timeout=3
        )
        final_url = response.url
        latest_tag = final_url.rstrip("/").split("/")[-1]
        latest_version = latest_tag.lstrip("v")
        return Version(latest_version) > Version(current_version.lstrip("v"))
