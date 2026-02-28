from abc import ABC, abstractmethod

from core.settings import BATCH_SIZE


class Translator(ABC):
    def translate(self, texts: list[str], src_lang: str, tgt_lang: str) -> list[str]:
        translations = []

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]

            # Filter empty strings
            non_empty = [t for t in batch if t.strip()]
            if not non_empty:
                translations.extend([""] * len(batch))
                continue

            # Delegate to subclass
            translated = self._translate_batch_impl(non_empty, src_lang, tgt_lang)

            # Reconstruct with empty strings
            idx = 0
            for t in batch:
                if t.strip():
                    translations.append(translated[idx])
                    idx += 1
                else:
                    translations.append("")

        return translations

    @abstractmethod
    def _translate_batch_impl(
        self, texts: list[str], src_lang: str, tgt_lang: str
    ) -> list[str]:
        pass


class LocalTranslator(Translator):
    def _translate_batch_impl(
        self, texts: list[str], src_lang: str, tgt_lang: str
    ) -> list[str]:
        # Subclass implements native batch translation
        return self._translate_batch(texts, src_lang, tgt_lang)

    @abstractmethod
    def _translate_batch(
        self, texts: list[str], src_lang: str, tgt_lang: str
    ) -> list[str]:
        pass


class ApiTranslator(Translator):
    def _translate_batch_impl(
        self, texts: list[str], src_lang: str, tgt_lang: str
    ) -> list[str]:
        # Convert single-text API to batch by looping
        return [self._translate_text(t, src_lang, tgt_lang) for t in texts]

    @abstractmethod
    def _translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
        pass
