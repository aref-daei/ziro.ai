from deepl import DeepLClient
from deepl.exceptions import ConnectionException

from core.exceptions import ConnectionError, TranslationError
from ..interfaces import ApiTranslator

MAX_RETRIES = 3


class DeepLTranslator(ApiTranslator):
    """Text translation with DeepL Translate API"""

    def __init__(self, auth_key: str) -> None:
        self.deepl_client = DeepLClient(auth_key)

    def _translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str | None:
        text = text.strip()
        if not text:
            return text

        # local counter: thread-safe, resets per call
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return self.deepl_client.translate_text(
                    text, source_lang=src_lang.upper(), target_lang=tgt_lang.upper()
                ).text

            except ConnectionException as e:
                if attempt >= MAX_RETRIES:
                    raise ConnectionError(f"{e}")

            except Exception as e:
                if attempt >= MAX_RETRIES:
                    raise TranslationError(f"DeepL loading failed with error: {e}")
        return None
