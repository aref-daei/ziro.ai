from services.transcriber.schemas import Transcriber


class TranscriberService:
    def __init__(self, provider: Transcriber):
        self.provider = provider

    def transcribe(self, audio_path: str, language: str) -> dict:
        """Convert voice to text"""
        return self.provider.transcribe(audio_path, language)

    def get_segments(self, transcription_result: dict) -> list[dict]:
        """Extract segments with scheduling"""
        return self.provider.get_segments(transcription_result)
