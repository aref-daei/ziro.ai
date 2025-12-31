from abc import ABC, abstractmethod
from typing import Dict, List


class Transcriber(ABC):

    @abstractmethod
    def transcribe(self, audio_path: str, language: str) -> Dict:
        pass

    @abstractmethod
    def get_segments(self, transcription_result: Dict) -> List[Dict]:
        pass
