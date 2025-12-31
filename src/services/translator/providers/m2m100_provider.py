from enum import Enum
from typing import List

import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from core.config import MAX_TRANSLATION_LENGTH, BATCH_SIZE
from ..schemas import Translator


class M2M100Translator(Translator):
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

    def translate(self, texts: list[str], src_lang: str, tgt_lang: str) -> list[str]:
        translations = []

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]

            non_empty = [t for t in batch if t.strip()]
            if not non_empty:
                translations.extend([""] * len(batch))
                continue

            # API path → one-to-one
            # translated = [
            #     self._translate_text(t, src_lang, tgt_lang) for t in non_empty
            # ]

            # Model path → actual batch
            translated = self._translate_batch_model(non_empty, src_lang, tgt_lang)

            idx = 0
            for t in batch:
                if t.strip():
                    translations.append(translated[idx])
                    idx += 1
                else:
                    translations.append("")

        return translations

    def _translate_batch_model(
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
