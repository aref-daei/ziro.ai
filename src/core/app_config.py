from dataclasses import dataclass



@dataclass
class AppConfig:

    source_language: tuple[str, bool]

    target_language: tuple[str, bool]

    transcriber: tuple[str, str]

    translator: tuple[str, str]

    device: str

    subtitle_toggle: bool
