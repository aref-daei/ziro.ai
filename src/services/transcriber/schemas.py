from abc import ABC, abstractmethod


class Transcriber(ABC):

    @abstractmethod
    def transcribe(self, audio_path: str, language: str | None) -> dict:
        pass

    @abstractmethod
    def get_segments(self, transcription_result: dict) -> list[dict]:
        pass
