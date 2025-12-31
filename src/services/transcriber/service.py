from typing import Dict, List
from .schemas import Transcriber


class TranscriberService:
    def __init__(self, provider: Transcriber):
        self.provider = provider

    def transcribe(self, audio_path: str, language: str) -> Dict:
        """Convert voice to text"""
        return self.provider.transcribe(audio_path, language)

    def get_segments(self, transcription_result: Dict) -> List[Dict]:
        """Extract segments with scheduling"""
        return self.provider.get_segments(transcription_result)
