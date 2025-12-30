from typing import List

import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

from exceptions.translator_exc import UnsupportedModelError
from settings import TRANSLATION_MODEL, MAX_TRANSLATION_LENGTH, BATCH_SIZE


class Translator:
    """Text translation with HuggingFace Transformers"""

    def __init__(self, model_name: str = TRANSLATION_MODEL):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """Loading translation model"""
        if self.model is None:
            if "m2m100_418M" in self.model_name:
                # M2M100 418M models
                self.model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
                self.tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

                # Offline Model Setup
                # self.model = M2M100ForConditionalGeneration.from_pretrained("./models/m2m100", local_files_only=True)
                # self.tokenizer = M2M100Tokenizer.from_pretrained("./models/m2m100", local_files_only=True)

            elif "m2m100_1.2B" in self.model_name:
                # M2M100 1.2B models
                self.model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_1.2B")
                self.tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_1.2B")

                # Offline Model Setup
                # self.model = M2M100ForConditionalGeneration.from_pretrained("./models/m2m100", local_files_only=True)
                # self.tokenizer = M2M100Tokenizer.from_pretrained("./models/m2m100", local_files_only=True)

            else:
                raise UnsupportedModelError(f"Unsupported model: {self.model_name}")

            self.tokenizer.src_lang = "en"
            self.model.to(self.device)

    def translate_text(self, text: str) -> str:
        """Translating a text"""
        self.load_model()

        if not text.strip():
            return ""

        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_TRANSLATION_LENGTH
        ).to(self.device)

        # Translation
        with torch.no_grad():
            translated = self.model.generate(
                **inputs,
                max_length=MAX_TRANSLATION_LENGTH,
                num_beams=4,
                early_stopping=True,
                forced_bos_token_id=self.tokenizer.get_lang_id("fa")
            )

        # Decode
        translated_text = self.tokenizer.decode(
            translated[0],
            skip_special_tokens=True
        )

        return translated_text.strip()

    def translate_batch(self, texts: List[str]) -> List[str]:
        """Batch translation of texts"""
        self.load_model()

        translations = []

        # Batch processing
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i + BATCH_SIZE]

            # Remove empty text
            non_empty_batch = [t for t in batch if t.strip()]

            if not non_empty_batch:
                translations.extend([""] * len(batch))
                continue

            # Tokenize
            inputs = self.tokenizer(
                non_empty_batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=MAX_TRANSLATION_LENGTH
            ).to(self.device)

            # Translation
            with torch.no_grad():
                translated = self.model.generate(
                    **inputs,
                    max_length=MAX_TRANSLATION_LENGTH,
                    num_beams=4,
                    early_stopping=True,
                    forced_bos_token_id=self.tokenizer.get_lang_id("fa")
                )

            # Decode
            batch_translations = [
                self.tokenizer.decode(t, skip_special_tokens=True).strip()
                for t in translated
            ]

            translations.extend(batch_translations)

        return translations
