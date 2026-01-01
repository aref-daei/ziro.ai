import time
from libretranslatepy import LibreTranslateAPI
from utils.logger import Logger
from ..schemas import ApiTranslator


class LibreTranslateTranslator(ApiTranslator):
    """Text translation with LibreTranslate API"""

    def __init__(self) -> None:
        self.translator = LibreTranslateAPI("https://libretranslate.com/")
        self.logger = Logger()

    def _translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
        try:
            text = text.strip()
            if not text:
                return text

            result = self.translator.translate(text, src_lang, tgt_lang)
            time.sleep(0.25)
            return result.text

        except Exception as e:
            # self.logger.warning(f"Error translating '{text[:30]}...': {str(e)}")
            # return text
            raise Exception(f"Error translating '{text[:30]}...': {str(e)}")
