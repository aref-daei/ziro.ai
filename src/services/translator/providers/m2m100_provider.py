from enum import Enum

import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

from core.config import MAX_TRANSLATION_LENGTH
from services.translator.schemas import LocalTranslator


class M2M100Translator(LocalTranslator):
    """Text translation with HuggingFace Transformers"""

    class Variant(Enum):
        SMALL = "418M"
        LARGE = "1.2B"

    def __init__(self, variant: Variant) -> None:
        self._model_name = f"facebook/m2m100_{variant.value}"

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self._model = M2M100ForConditionalGeneration.from_pretrained(self._model_name)
        self._model.to(self._device)  # type: ignore

        self._tokenizer = M2M100Tokenizer.from_pretrained(self._model_name)

    def _translate_batch(
        self, texts: list[str], src_lang: str, tgt_lang: str
    ) -> list[str]:

        self._tokenizer.src_lang = src_lang

        inputs = self._tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_TRANSLATION_LENGTH,
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_length=MAX_TRANSLATION_LENGTH,
                num_beams=4,
                early_stopping=True,
                forced_bos_token_id=self._tokenizer.get_lang_id(tgt_lang),
            )

        return [
            self._tokenizer.decode(o, skip_special_tokens=True).strip() for o in outputs
        ]
