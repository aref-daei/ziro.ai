from dataclasses import dataclass


@dataclass
class AppConfig:

    transcriber: str

    whisper_variant: str

    translator: str

    device: str

    source_language: str

    target_language: str
