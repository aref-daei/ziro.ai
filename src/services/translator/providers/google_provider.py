import asyncio

from googletrans import Translator
from httpx import ConnectError

from core.exceptions import ConnectionError, TranslationError
from ..interfaces import ApiTranslator

MAX_RETRIES = 3


class GoogleTranslator(ApiTranslator):
    """Text translation with Google Translate API (Unofficial)"""

    def _translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str | None:
        text = text.strip()
        if not text:
            return text

        # local counter: thread-safe, resets per call
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return asyncio.run(self._translate_text_async(text, src_lang, tgt_lang))

            except ConnectError as e:
                if attempt >= MAX_RETRIES:
                    raise ConnectionError(f"{e}")

            except Exception as e:
                if attempt >= MAX_RETRIES:
                    raise TranslationError(f"Google Translate loading failed with error: {e}")
        return None

    async def _translate_text_async(self, text, src_lang, tgt_lang):
        # new client per call: each thread has its own event loop
        async with Translator() as translator:
            result = await translator.translate(text, src=src_lang, dest=tgt_lang)
            return result.text
