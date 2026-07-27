import shutil
from pathlib import Path

import requests
from PySide6.QtCore import QObject, Signal, Slot

from src.core.app_config import AppConfig
from src.core.paths import PATHS
from src.gui.widgets import QueueStatus
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


class ProcessingWorker(QObject):
    process_started = Signal()
    status = Signal(str, QueueStatus)
    progress = Signal(str, int)
    process_finished = Signal()

    def __init__(self, config: AppConfig, selected_files: list[str]):
        super().__init__()
        self.config = config
        self.selected_files = selected_files

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

                # 2. Transcription (10-40%)
                transcription = registry.transcriber().transcribe(
                    audio_path,
                    (
                        None
                        if config.source_language[0] == "auto"
                        else config.source_language[0]
                    )
                )
                segments_en = registry.transcriber().get_segments(transcription)
                self.progress.emit(video_path, 40)

                # 3. Save English subtitles
                srt_en_path = PATHS["temp"] / f"{video_name}_en.srt"
                registry.subtitle_generator().generate_srt(segments_en, srt_en_path)

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

            except RuntimeError:
                self.status.emit(video_path, QueueStatus.FAILED)
                break

            except Exception as e:
                # TODO: At this point, it should logs with the text e
                self.status.emit(video_path, QueueStatus.FAILED)
                break

        self.process_finished.emit()
