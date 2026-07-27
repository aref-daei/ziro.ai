from src.core.app_config import AppConfig
from .audio_extractor import AudioExtractorService
from .subtitle_generator import SubtitleGeneratorService
from .transcriber import TranscriberService
from .transcriber.providers import WhisperTranscriber
from .translator import TranslatorService
from .translator.providers import GoogleTranslator, DeepLTranslator
from .video_processor import VideoProcessorService


class ServiceRegistry:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def audio_extractor(self) -> AudioExtractorService:
        return AudioExtractorService()

    def transcriber(self) -> TranscriberService | None:
        if self.config.transcriber[0] == "whisper":
            provider = WhisperTranscriber(
                WhisperTranscriber.Variant[self.config.transcriber[1].upper()],
                self.config.device,
            )
            return TranscriberService(provider)

        else:
            return None

    def subtitle_generator(self):
        return SubtitleGeneratorService()

    def translate(self) -> TranslatorService | None:
        if self.config.translator[0] == "google":
            provider = GoogleTranslator()
            return TranslatorService(provider)

        elif self.config.translator[0] == "deepl":
            provider = DeepLTranslator(self.config.translator[1])
            return TranslatorService(provider)

        else:
            return None

    def video_processor(self):
        return VideoProcessorService()
