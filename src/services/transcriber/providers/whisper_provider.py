from enum import Enum
from urllib.error import URLError

import whisper

from src.core.exceptions import ConnectionError, TranscriptionError
from src.core.paths import PATHS
from ..interfaces import Transcriber


class WhisperTranscriber(Transcriber):
    """Speech to text conversion with OpenAI Whisper"""

    class Variant(Enum):
        TINY = "tiny"
        BASE = "base"
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    def __init__(self, variant: Variant, device: str = "cpu") -> None:
        model_dir_path = PATHS["base"] / "models" / "whisper"

        base_model_path = model_dir_path / f"{variant.value}.pt"
        if not base_model_path.exists():
            model_dir_path = PATHS["models"] / "whisper"

        try:
            self._model = whisper.load_model(
                variant.value, device=device, download_root=f"{model_dir_path}"
            )

        except URLError as e:
            raise ConnectionError(f"{e}")

        except Exception as e:
            raise TranscriptionError(f"Whisper model loading failed with error: {e}")

    def transcribe(self, audio_path: str, language: str | None) -> dict:
        try:
            kwargs = {"task": "translate", "word_timestamps": False}
            if language is not None:
                kwargs["language"] = language

            return self._model.transcribe(audio=audio_path, **kwargs)

        except Exception as e:
            raise TranscriptionError(f"Transcription failed with error: {e}")

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
