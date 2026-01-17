import platform
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import requests
import torch
from packaging.version import Version

from core.config import (
    PROJECT_NAME,
    PROJECT_VERSION,
    PROJECT_LICENSE,
    PROJECT_URL,
    PROJECT_LATEST_RELEASE_URL,
    DEBUG,
)
from core.exceptions import ConnectionError, TranscriptionError, TranslationError
from core.paths import PATHS
from services.audio_extractor.service import AudioExtractorService
from services.subtitle_generator.service import SubtitleGeneratorService
from services.video_processor.service import VideoProcessorService
from services.transcriber.providers.whisper_provider import WhisperTranscriber
from services.transcriber.service import TranscriberService
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
        width, height = 400, 700
        scaling = ctk.ScalingTracker.get_window_scaling(self)
        x = (self.winfo_screenwidth() - width) * scaling / 2
        y = (self.winfo_screenheight() - height) * scaling / 2
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
        self.resizable(False, False)

        # Theme
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")

        # Variables
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.video_path = ""
        self.processing = False
        self.languages = {
            "Persian": "fa",
            "English": "en",
            "French": "fr",
        }

        # Logger
        self.logger = Logger()

        self.setup_ui()

        if self.is_update_available():
            self.after(
                500,
                messagebox.showinfo,
                "Update Available",
                (
                    f"A new version of {PROJECT_NAME} is available.\n"
                    "Please download the latest release from GitHub."
                ),
            )

    def setup_ui(self):
        # Title
        title_label = ctk.CTkLabel(
            self, text=f"{PROJECT_NAME}", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        # File selection frame
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(pady=12, padx=24, fill="x")

        self.file_label = ctk.CTkLabel(
            file_frame, text="No files selected", font=ctk.CTkFont(size=12)
        )
        self.file_label.pack(pady=8)

        self.select_btn = ctk.CTkButton(
            file_frame,
            text="Video selection",
            command=self.select_video,
            width=220,
            height=40,
        )
        self.select_btn.pack(pady=8)

        # Settings
        settings_frame = ctk.CTkFrame(self)
        settings_frame.pack(pady=12, padx=24, fill="both", expand=True)

        settings_label = ctk.CTkLabel(
            settings_frame, text="Settings", font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_label.pack(pady=8)

        ctk.CTkLabel(
            settings_frame,
            text=f"Using device: {self.device.upper()}",
            font=ctk.CTkFont(size=12),
        ).pack()

        # Choosing languages
        lang_frame = ctk.CTkFrame(settings_frame)
        lang_frame.pack(pady=8, padx=16, fill="x")
        lang_frame.grid_rowconfigure(0, weight=1)

        self.src_lang = ctk.CTkOptionMenu(
            lang_frame,
            values=["Auto"] + [*self.languages],
            width=120,
        )
        self.src_lang.set("Auto")
        self.src_lang.grid(row=0, column=0, pady=2, padx=10)

        ctk.CTkLabel(
            lang_frame, text="  →  ", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=1, padx=6)

        self.tgt_lang = ctk.CTkOptionMenu(
            lang_frame,
            values=[*self.languages],
            width=120,
        )
        self.tgt_lang.set("Persian")
        self.tgt_lang.grid(row=0, column=2, pady=2, padx=10)

        # Choosing a Transcription accuracy
        whisper_frame = ctk.CTkFrame(settings_frame)
        whisper_frame.pack(pady=8, padx=16, fill="x")

        ctk.CTkLabel(
            whisper_frame, text="Transcription accuracy:", font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=10)

        self.whisper_model = ctk.CTkOptionMenu(
            whisper_frame,
            values=[var.name.title() for var in WhisperTranscriber.Variant],
            width=150,
        )
        self.whisper_model.set(WhisperTranscriber.Variant.BASE.name.title())
        self.whisper_model.pack(side="right", pady=2, padx=10)

        # Choosing a translation model
        trans_frame = ctk.CTkFrame(settings_frame)
        trans_frame.pack(pady=8, padx=16, fill="x")

        ctk.CTkLabel(
            trans_frame, text="Translation model:", font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=10)

        self.translation_model = ctk.CTkOptionMenu(
            trans_frame,
            values=["Google Translate", "DeepL (by key)"],
            width=150,
        )
        self.translation_model.set("Google Translate")
        self.translation_model.pack(side="right", pady=2, padx=10)

        # Entering Auth key for DeepL
        auth_key_frame = ctk.CTkFrame(settings_frame)
        auth_key_frame.pack(pady=8, padx=16, fill="x")

        ctk.CTkLabel(
            auth_key_frame, text="Auth key for DeepL:", font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=10)

        self.auth_key = ctk.CTkEntry(
            auth_key_frame,
            placeholder_text="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            width=150,
            border_width=0,
        )
        self.auth_key.pack(side="right", pady=2, padx=10)

        # Checkboxes
        options_frame = ctk.CTkFrame(settings_frame)
        options_frame.pack(pady=8, padx=16, fill="x")

        self.embed_subtitles = ctk.CTkCheckBox(
            options_frame, text="Add subtitles to video", font=ctk.CTkFont(size=12)
        )
        self.embed_subtitles.pack(pady=4)
        self.embed_subtitles.select()

        # Progress bar
        self.status_label = ctk.CTkLabel(
            self, text="Ready", wraplength=250, font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=4)

        self.progress_bar = ctk.CTkProgressBar(self, width=260)
        self.progress_bar.pack(pady=4)
        self.progress_bar.set(0)

        # Processing button
        self.process_btn = ctk.CTkButton(
            self,
            text="Start processing",
            command=self.start_processing,
            width=350,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled",
        )
        self.process_btn.pack(pady=12)

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

    def start_processing(self):
        """Start processing in a separate thread"""
        if self.processing:
            return

        if not self.video_path:
            messagebox.showwarning(
                "No video selected", "Please select a video file first"
            )
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
            if not (self.is_internet_access() or DEBUG):
                messagebox.showwarning(
                    "No internet access", "Start processing requires internet access"
                )
                self.processing = False
                self.process_btn.configure(state="normal")
                self.disable_controls(False)
                return

            video_name = Path(self.video_path).stem

            # 1. Sound extraction (0-20%)
            self.update_status("Extracting audio ...", 0.0)
            audio_extractor_service = AudioExtractorService()
            audio_path = audio_extractor_service.extract(self.video_path)
            self.update_status("Audio extracted", 0.2)

            # 2. Transcription (20-50%)
            self.update_status("Converting speech to text ...", 0.2)
            transcriber = WhisperTranscriber(
                WhisperTranscriber.Variant[self.whisper_model.get().upper()],
                self.device,
            )
            transcriber_service = TranscriberService(transcriber)
            transcription = transcriber_service.transcribe(
                audio_path,
                (
                    None
                    if self.src_lang.get() == "Auto"
                    else self.languages[self.src_lang.get()]
                ),
            )
            segments_en = transcriber_service.get_segments(transcription)
            self.update_status("Transcription completed", 0.5)

            # 3. Save English subtitles
            srt_en_path = PATHS["temp"] / f"{video_name}_en.srt"
            subtitle_generator_service = SubtitleGeneratorService()
            subtitle_generator_service.generate_srt(segments_en, srt_en_path)

            # 4. Translation (50-80%)
            self.update_status(f"Translating into {self.tgt_lang.get()} ...", 0.5)
            if self.translation_model.get() == "Google Translate":
                translator = GoogleTranslator()
            else:
                translator = DeepLTranslator(self.auth_key.get())
            translator_service = TranslatorService(translator)

            texts_en = [seg["text"] for seg in segments_en]
            texts_tgt_lang = translator_service.translate(
                texts_en, "en", self.languages[self.tgt_lang.get()]
            )

            # Creating target language segments
            segments_tgt_lang = []
            for seg_en, text_tgt_lang in zip(segments_en, texts_tgt_lang):
                segments_tgt_lang.append(
                    {
                        "text": text_tgt_lang,
                        "start": seg_en["start"],
                        "end": seg_en["end"],
                    }
                )

            self.update_status("Translation completed", 0.8)

            # 5. Save Persian subtitles
            srt_tgt_lang_path = (
                PATHS["temp"]
                / f"{video_name}_{self.languages[self.tgt_lang.get()]}.srt"
            )
            subtitle_generator_service.generate_srt(
                segments_tgt_lang, srt_tgt_lang_path
            )

            # 7. Add subtitles to the video (80-100%)
            output_video = ""
            if self.embed_subtitles.get():
                self.update_status("Adding subtitles to video ...", 0.8)

                subtitle_paths = {
                    "eng": str(srt_en_path),
                    "per": str(srt_tgt_lang_path),
                }

                video_processor_service = VideoProcessorService()
                output_video = video_processor_service.add_subtitles(
                    self.video_path, subtitle_paths, f"{video_name}_subtitled.mkv"
                )

            self.update_status("Processing complete!", 1.0)

            # Show success message
            self.after(
                100,
                self._show_success,
                srt_en_path,
                srt_tgt_lang_path,
                Path(output_video),
            )

        except ConnectionError as e:
            self.update_status(f"Connection failed", 0.0)
            self.logger.error(f"{e}")
            self.after(
                100,
                messagebox.showerror,
                "Connection failed",
                f"Try:\n  • Checking the network cables, modem, and router\n  • Reconnecting to Wi-Fi",
            )

        except TranscriptionError as e:
            self.update_status(f"Transcription failed", 0.0)
            self.logger.error(f"{e}")
            self.after(
                100,
                messagebox.showerror,
                "Transcription failed",
                f"Try:\n  • Checking the network and internet\n  • Starting processing again\n  • Informing us of the problem",
            )

        except TranslationError as e:
            self.update_status(f"Translation failed", 0.0)
            self.logger.error(f"{e}")
            self.after(
                100,
                messagebox.showerror,
                "Translation failed",
                f"Try:\n  • Checking the network and internet\n  • Starting processing again\n  • Informing us of the problem",
            )

        except RuntimeError as e:
            self.update_status(f"Processing failed", 0.0)
            self.logger.error(f"{e}")
            self.after(
                100,
                messagebox.showerror,
                "Processing failed",
                f"Try:\n  • Checking the video format\n  • Starting processing again\n  • Informing us of the problem",
            )

        except Exception as e:
            self.update_status(f"Unexpected error", 0.0)
            self.logger.error(f"{e}")
            self.after(
                100,
                messagebox.showerror,
                "Unexpected error",
                f"Try:\n  • Starting processing again\n  • Informing us of the problem!",
            )

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
        message = f"{"Video with subtitles: " + ov.name if self.embed_subtitles.get() else ""}"
        if DEBUG or not self.embed_subtitles.get():
            message = (
                f"English subtitles: {en.name}\n"
                f"{self.tgt_lang.get()} subtitles: {fa.name}"
                f"{"\nVideo with subtitles: " + ov.name if self.embed_subtitles.get() else ""}"
            )
        messagebox.showinfo("Processing complete!", message)
        FileHandler.open_path(
            ov.parent if self.embed_subtitles.get() else PATHS["temp"]
        )

    def _get_icon_path(self) -> Path:
        if platform.system() == "Windows":
            return PATHS["base"] / "assets" / "Ziro.ico"
        elif platform.system() == "Darwin":
            return PATHS["base"] / "assets" / "Ziro.icns"
        else:
            return PATHS["base"] / "assets" / "Ziro.png"

    def is_internet_access(self) -> bool:
        try:
            response = requests.get("https://www.google.com", timeout=3)
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    def is_update_available(self) -> bool:
        try:
            response = requests.get(
                PROJECT_LATEST_RELEASE_URL, allow_redirects=True, timeout=1
            )
            final_url = response.url
            latest_tag = final_url.rstrip("/").split("/")[-1]
            latest_version = latest_tag.lstrip("v")
            return Version(latest_version) > Version(PROJECT_VERSION)
        except Exception:
            return False
