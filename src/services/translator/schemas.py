from abc import ABC, abstractmethod
from typing import List


class Translator(ABC):

    @abstractmethod
    def translate(self, texts: List[str]) -> List[str]:
        pass
