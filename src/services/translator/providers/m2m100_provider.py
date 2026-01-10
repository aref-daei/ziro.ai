from enum import Enum

import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from huggingface_hub.errors import HfHubHTTPError, HFValidationError

from core.config import MAX_TRANSLATION_LENGTH
from core.exceptions import ConnectionError
from core.paths import PATHS
from services.translator.schemas import LocalTranslator


class M2M100Translator(LocalTranslator):
    """Text translation with HuggingFace Transformers"""

    class Variant(Enum):
        SMALL = "418M"
        LARGE = "1.2B"

    def __init__(self, variant: Variant) -> None:
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model_dir_path = PATHS["base"] / "models" / "m2m100" / variant.value

        try:
            self._model = M2M100ForConditionalGeneration.from_pretrained(
                f"{model_dir_path}", local_files_only=True
            )
            self._tokenizer = M2M100Tokenizer.from_pretrained(
                f"{model_dir_path}", local_files_only=True
            )

        except HFValidationError as e:
            model_dir_path.mkdir(parents=True, exist_ok=True)

            # huggingface-cli download facebook/m2m100_418M --local-dir ./models/m2m100/418M --local-dir-use-symlinks False

            self._model = M2M100ForConditionalGeneration.from_pretrained(
                f"{model_dir_path}", local_files_only=True
            )
            self._tokenizer = M2M100Tokenizer.from_pretrained(
                f"{model_dir_path}", local_files_only=True
            )
        
        except HfHubHTTPError as e:
            raise ConnectionError(f"{e}")

        except Exception as e:
            raise RuntimeError(f"Error translating: {e}")

        self._model.to(self._device)  # type: ignore

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
