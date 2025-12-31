from typing import List
from .schemas import Translator


class TranslatorService:
    def __init__(self, provider: Translator):
        self.provider = provider

    def translate(self, texts: List[str]) -> List[str]:
        if not texts:
            raise ValueError("Empty input")

        return self.provider.translate(texts)
