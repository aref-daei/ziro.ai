import shutil
import threading
from pathlib import Path

import requests
from PySide6.QtCore import QObject, Signal, Slot

from src.core.app_config import AppConfig
from src.core.exceptions import *
from src.core.paths import PATHS
from src.core.queue_status import QueueStatus
from src.core.settings import DEBUG
from src.filesystem import FileHandler
from src.logger import Logger
from src.services import ServiceRegistry


def has_internet(timeout=2) -> bool:
    try:
        requests.head(
            "https://www.google.com",
            timeout=timeout
        )
        return True
    except requests.RequestException:
        return False


class _StoppedByUser(Exception):
    """Internal signal used to unwind out of the per-file try block when
    request_stop() was called mid-processing."""


class ProcessingWorker(QObject):
    process_started = Signal()
    status = Signal(str, QueueStatus)
    progress = Signal(str, int)
    process_finished = Signal()

    def __init__(self, config: AppConfig, selected_files: list[str]):
        super().__init__()
        self.config = config
        self.selected_files = selected_files

        self.logger = Logger()
        self._stop_event = threading.Event()

    def request_stop(self) -> None:
        """Call this directly from the main thread (not via a queued Qt
        signal - see the note in run() for why that wouldn't work here)."""
        self._stop_event.set()

    def is_stop_requested(self) -> bool:
        return self._stop_event.is_set()

    @Slot()
    def run(self):
        config = self.config
        selected_files = self.selected_files

        if not selected_files:
            return
        self.process_started.emit()

        registry = ServiceRegistry(config)
        is_need_translate = config.target_language[0] != "en"

        for video_path in selected_files:

            if self.is_stop_requested():
                break

            self.status.emit(video_path, QueueStatus.PROCESSING)
            self.progress.emit(video_path, 0)

            if not has_internet():
                self.status.emit(video_path, QueueStatus.FAILED)
                break

            video_name = Path(video_path).stem

            try:
                # 1. Sound extraction (0-10%)
                audio_path = registry.audio_extractor().extract(video_path)
                self.progress.emit(video_path, 10)

                if self.is_stop_requested():
                    raise _StoppedByUser()

                # 2. Transcription (10-40%)
                transcription = registry.transcriber().transcribe(
                    audio_path,
                    (
                        None
                        if config.source_language[0] == ""
                        else config.source_language[0]
                    )
                )
                segments_en = registry.transcriber().get_segments(transcription)
                self.progress.emit(video_path, 40)

                # 3. Save English subtitles
                srt_en_path = PATHS["temp"] / f"{video_name}_en.srt"
                registry.subtitle_generator().generate_srt(segments_en, srt_en_path)

                if self.is_stop_requested():
                    raise _StoppedByUser()

                if is_need_translate:
                    # 4. Translation (40-80%)
                    texts_en = [seg["text"] for seg in segments_en]
                    texts_tgt_lang = registry.translate().translate(
                        texts_en, "en", config.target_language[0]
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
                    self.progress.emit(video_path, 80)

                    if self.is_stop_requested():
                        raise _StoppedByUser()

                    # 5. Save target language subtitles
                    srt_tgt_lang_path = (
                            PATHS["temp"]
                            / f"{video_name}_{config.target_language[0]}.srt"
                    )
                    registry.subtitle_generator().generate_srt(
                        segments_tgt_lang,
                        srt_tgt_lang_path,
                        config.target_language[1]
                    )

                    # 6. Add subtitles to the video (80-100%)
                    outputs = []
                    if config.subtitle_toggle:
                        subtitle_paths = {
                            "eng": str(srt_en_path),
                            f"{config.target_language[0][:3]}": str(srt_tgt_lang_path),
                        }

                        output_video = registry.video_processor().add_subtitles(
                            video_path, subtitle_paths, f"{video_name}_subtitled.mkv"
                        )

                        outputs.append(output_video)

                    else:
                        shutil.copy(srt_en_path, PATHS["output"] / srt_en_path.name)
                        shutil.copy(
                            srt_tgt_lang_path, PATHS["output"] / srt_tgt_lang_path.name
                        )
                        outputs.append(PATHS["output"] / srt_en_path.name)
                        outputs.append(PATHS["output"] / srt_tgt_lang_path.name)

                else:
                    # 4. Add subtitle to the video (40-100%)
                    outputs = []
                    if config.subtitle_toggle:
                        subtitle_paths = {"eng": str(srt_en_path)}

                        output_video = registry.video_processor().add_subtitles(
                            video_path, subtitle_paths, f"{video_name}_subtitled.mkv"
                        )

                        outputs.append(output_video)

                    else:
                        shutil.copy(srt_en_path, PATHS["output"] / srt_en_path.name)
                        outputs.append(PATHS["output"] / srt_en_path.name)

                self.progress.emit(video_path, 100)
                self.status.emit(video_path, QueueStatus.DONE)

            except _StoppedByUser:
                self.status.emit(video_path, QueueStatus.CANCELLED)
                self.logger.error(f"Processing stopped by user during: {video_path}")
                break

            except ConnectionError as e:
                self.status.emit(video_path, QueueStatus.FAILED)
                self.logger.error(f"ConnectionError: {e}")
                # UI Message:
                # "Connection failed",
                # f"Try:\n  • Checking the network cables, modem, and router\n  • Reconnecting to Wi-Fi"
                break

            except TranscriptionError as e:
                self.status.emit(video_path, QueueStatus.FAILED)
                self.logger.error(f"TranscriptionError: {e}")
                # UI Message:
                # "Transcription failed",
                # f"Try:\n  • Checking the network and internet\n  • Starting processing again\n  • Informing us of the problem"
                break

            except TranslationError as e:
                self.status.emit(video_path, QueueStatus.FAILED)
                self.logger.error(f"TranslationError: {e}")
                # UI Message:
                # "Translation failed",
                # f"Try:\n  • Checking the network and internet\n  • Starting processing again\n  • Informing us of the problem"
                break

            except RuntimeError as e:
                self.status.emit(video_path, QueueStatus.FAILED)
                self.logger.error(f"RuntimeError: {e}")
                # UI Message:
                # "Processing failed",
                # f"Try:\n  • Checking the video format\n  • Starting processing again\n  • Informing us of the problem"
                break

            except Exception as e:
                self.status.emit(video_path, QueueStatus.FAILED)
                self.logger.error(f"Error: {e}")
                # UI Message:
                # "Unexpected error",
                # f"Try:\n  • Starting processing again\n  • Informing us of the problem!"
                break

        self.process_finished.emit()

        if not DEBUG:
            try:
                FileHandler.clean_temp_files()
            except RuntimeError as e:
                self.logger.error(f"{e}")
