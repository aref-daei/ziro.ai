from enum import Enum
from urllib.error import URLError

import torch
import whisper

from core.exceptions import ConnectionError
from core.paths import PATHS
from services.transcriber.schemas import Transcriber


class WhisperTranscriber(Transcriber):
    """Speech to text conversion with OpenAI Whisper"""

    class Variant(Enum):
        TINY = "tiny"
        BASE = "base"
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    def __init__(self, variant: Variant, device: str = "cpu") -> None:
        self._device = torch.device(device)

        model_dir_path = PATHS["base"] / "models" / "whisper"

        try:
            self._model = whisper.load_model(
                variant.value, device=self._device, download_root=f"{model_dir_path}"
            )

        except URLError as e:
            raise ConnectionError(f"{e}")

        except Exception as e:
            raise RuntimeError(f"Error transcribing: {e}")

    def transcribe(self, audio_path: str, language: str) -> dict:
        try:
            result = self._model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                word_timestamps=False,
            )

            return result
        except Exception as e:
            raise RuntimeError(f"Transcription failed with error: {e}")

    def get_segments(self, transcription_result: dict) -> list[dict]:
        segments = []

        for segment in transcription_result["segments"]:
            segments.append(
                {
                    "text": segment["text"].strip(),
                    "start": segment["start"],
                    "end": segment["end"],
                }
            )

        return segments
