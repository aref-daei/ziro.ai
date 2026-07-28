from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from src.core.settings import BATCH_SIZE

try:
    from src.core.settings import MAX_WORKERS
except ImportError:
    MAX_WORKERS = 5  # default worker count


class Translator(ABC):

    def translate(self, texts: list[str], src_lang: str, tgt_lang: str) -> list[str]:
        translations = [""] * len(texts)

        non_empty_indices = [i for i, t in enumerate(texts) if t.strip()]
        if not non_empty_indices:
            return translations

        non_empty_texts = [texts[i] for i in non_empty_indices]
        translated = self._translate_impl(non_empty_texts, src_lang, tgt_lang)

        # restore original positions
        for idx, translation in zip(non_empty_indices, translated):
            translations[idx] = translation

        return translations

    @abstractmethod
    def _translate_impl(
            self, texts: list[str], src_lang: str, tgt_lang: str
    ) -> list[str]:
        pass


class LocalTranslator(Translator):

    def _translate_impl(
            self, texts: list[str], src_lang: str, tgt_lang: str
    ) -> list[str]:
        translations = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i: i + BATCH_SIZE]
            translations.extend(self._translate_batch(batch, src_lang, tgt_lang))
        return translations

    @abstractmethod
    def _translate_batch(
            self, texts: list[str], src_lang: str, tgt_lang: str
    ) -> list[str]:
        pass


class ApiTranslator(Translator):

    def _translate_impl(
            self, texts: list[str], src_lang: str, tgt_lang: str
    ) -> list[str]:
        def call(text: str) -> str:
            return self._translate_text(text, src_lang, tgt_lang)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # executor.map preserves input order
            return list(executor.map(call, texts))

    @abstractmethod
    def _translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
        pass
