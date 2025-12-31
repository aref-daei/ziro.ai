from typing import Dict, List
from .schemas import Transcriber


class TranscriberService:
    def __init__(self, provider: Transcriber):
        self.provider = provider

    def transcribe(self, audio_path: str, language: str) -> Dict:
        return self.provider.transcribe(audio_path, language)
    
    def get_segments(self, transcription_result: Dict) -> List[Dict]:
        return self.provider.get_segments(transcription_result)
