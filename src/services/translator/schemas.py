from abc import ABC, abstractmethod
from typing import List


class Translator(ABC):

    @abstractmethod
    def translate(self, texts: List[str], src_lang: str, tgt_lang: str) -> List[str]:
        pass
