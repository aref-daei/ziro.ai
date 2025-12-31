from enum import Enum
from typing import List

import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from core.config import MAX_TRANSLATION_LENGTH, BATCH_SIZE
from ..schemas import Translator


class M2M100Translator(Translator):
    class Variant(Enum):
        SMALL = "418M"
        LARGE = "1.2B"

    def __init__(self, variant: Variant, src_lang: str, tgt_lang: str) -> None:
        self._model_name = f"facebook/m2m100_{variant.value}"

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self._model = M2M100ForConditionalGeneration.from_pretrained(self._model_name)
        self._model.to(self._device)  # type: ignore

        self._tokenizer = M2M100Tokenizer.from_pretrained(self._model_name)
        self._tokenizer.src_lang = src_lang

        self._tgt_lang = tgt_lang

    def translate(self, texts: List[str]) -> List[str]:
        translations = []

        # Batch processing
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]

            # Remove empty text
            non_empty_batch = [t for t in batch if t.strip()]

            if not non_empty_batch:
                translations.extend([""] * len(batch))
                continue

            # Tokenize
            inputs = self._tokenizer(
                non_empty_batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=MAX_TRANSLATION_LENGTH,
            ).to(self._device)

            # Translation
            with torch.no_grad():
                translated = self._model.generate(
                    **inputs,
                    max_length=MAX_TRANSLATION_LENGTH,
                    num_beams=4,
                    early_stopping=True,
                    forced_bos_token_id=self._tokenizer.get_lang_id(self._tgt_lang),
                )

            # Decode
            batch_translations = [
                self._tokenizer.decode(t, skip_special_tokens=True).strip()
                for t in translated
            ]

            translations.extend(batch_translations)

        return translations
