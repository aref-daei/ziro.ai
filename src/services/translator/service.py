from .schemas import Translator


class TranslatorService:
    def __init__(self, provider: Translator):
        self.provider = provider

    def translate(self, texts: list[str], src_lang: str, tgt_lang: str) -> list[str]:
        """Batch translation of texts"""
        return self.provider.translate(texts, src_lang, tgt_lang)
