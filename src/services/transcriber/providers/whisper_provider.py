from enum import Enum
from typing import Dict, List

import torch
import whisper
from ..schemas import Transcriber


class WhisperTranscriber(Transcriber):
    class Variant(Enum):
        TINY = "tiny"
        BASE = "base"
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    def __init__(self, variant: Variant) -> None:
        self._model_name = variant.value

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self._model = whisper.load_model(self._model_name, device=self._device)

    def transcribe(self, audio_path: str, language: str) -> Dict:
        result = self._model.transcribe(
            audio_path,
            language=language,
            task="transcribe",
            verbose=False,
            word_timestamps=False,
        )

        return result

    def get_segments(self, transcription_result: Dict) -> List[Dict]:
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
