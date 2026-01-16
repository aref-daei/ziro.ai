from deepl import DeepLClient
from deepl.exceptions import ConnectionException

from core.exceptions import ConnectionError, TranslationError
from services.translator.schemas import ApiTranslator


class DeepLTranslator(ApiTranslator):
    """Text translation with DeepL Translate API"""

    def __init__(self, auth_key: str) -> None:
        self.deepl_client = DeepLClient(auth_key)
        self._effort = 1

    def _translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
        try:
            text = text.strip()
            if not text:
                return text

            return self.deepl_client.translate_text(
                text, source_lang=src_lang.upper(), target_lang=tgt_lang.upper()
            ).text  # type: ignore

        except ConnectionException as e:
            if self._effort >= 3:
                raise ConnectionError(f"{e}")
            self._effort += 1
            return self._translate_text(text, src_lang, tgt_lang)

        except Exception as e:
            if self._effort >= 3:
                raise TranslationError(f"DeepL loading failed with error: {e}")
            self._effort += 1
            return self._translate_text(text, src_lang, tgt_lang)
