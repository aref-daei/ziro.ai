import asyncio

from googletrans import Translator
from httpx import ConnectError

from core.exceptions import ConnectionError
from services.translator.schemas import ApiTranslator


class GoogleTranslator(ApiTranslator):
    """Text translation with Google Translate API (Unofficial)"""

    def __init__(self) -> None:
        self._effort = 1

    def _translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
        try:
            text = text.strip()
            if not text:
                return text

            return asyncio.run(self._translate_text_async(text, src_lang, tgt_lang))
        
        except ConnectError as e:
            if self._effort >= 3:
                raise ConnectionError(f"{e}")
            self._effort += 1
            return self._translate_text(text, src_lang, tgt_lang)
        
        except Exception as e:
            if self._effort >= 3:
                raise RuntimeError(f"Error translating: {e}")
            self._effort += 1
            return self._translate_text(text, src_lang, tgt_lang)

    async def _translate_text_async(self, text, src_lang, tgt_lang):
        async with Translator() as translator:
            result = await translator.translate(text, src=src_lang, dest=tgt_lang)
            return result.text
