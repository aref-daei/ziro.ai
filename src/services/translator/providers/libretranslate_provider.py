import time
from libretranslatepy import LibreTranslateAPI
from core.config import BATCH_SIZE
from utils.logger import Logger
from ..schemas import Translator


class LibreTranslateTranslator(Translator):
    """Text translation with LibreTranslate API"""

    def __init__(self) -> None:
        self.translator = LibreTranslateAPI("https://libretranslate.com/")
        self.logger = Logger()

    def translate(self, texts: list[str], src_lang: str, tgt_lang: str) -> list[str]:
        translations = []

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]

            non_empty = [t for t in batch if t.strip()]
            if not non_empty:
                translations.extend([""] * len(batch))
                continue

            # API path → one-to-one
            translated = [
                self._translate_text(t, src_lang, tgt_lang) for t in non_empty
            ]

            # Model path → actual batch
            # translated = self._translate_batch_model(non_empty, src_lang, tgt_lang)

            idx = 0
            for t in batch:
                if t.strip():
                    translations.append(translated[idx])
                    idx += 1
                else:
                    translations.append("")

        return translations

    def _translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
        try:
            text = text.strip()
            if not text:
                return text

            result = self.translator.translate(text, src_lang, tgt_lang)
            time.sleep(0.25)
            return result.text

        except Exception as e:
            self.logger.warning(f"Error translating '{text[:30]}...': {str(e)}")
            return text
