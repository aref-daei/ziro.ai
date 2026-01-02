import asyncio
from deepl import DeepLClient
from ..schemas import ApiTranslator


class DeepLTranslator(ApiTranslator):
    """Text translation with DeepL Translate API"""

    def __init__(self, auth_key: str) -> None:
        self.deepl_client = DeepLClient(auth_key)
        self.effort = 1

    def _translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
        try:
            text = text.strip()
            if not text:
                return text

            return self.deepl_client.translate_text(
                text, source_lang=src_lang.upper(), target_lang=tgt_lang.upper()
            ).text # type: ignore

        except Exception as e:
            if self.effort >= 3:
                raise RuntimeError(f"Error translating: {str(e)}")
            self.effort += 1
            return self._translate_text(text, src_lang, tgt_lang)
