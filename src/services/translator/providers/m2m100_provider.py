from enum import Enum
import subprocess

import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

from core.config import MAX_TRANSLATION_LENGTH
from core.exceptions import ConnectionError
from core.paths import PATHS
from services.translator.schemas import LocalTranslator


class M2M100Translator(LocalTranslator):
    """Text translation with HuggingFace Transformers"""

    class Variant(Enum):
        SMALL = "418M"
        LARGE = "1.2B"

    def __init__(self, variant: Variant, device: str = "cpu") -> None:
        self._device = torch.device(device)

        model_dir_path = PATHS["base"] / "models" / "m2m100" / variant.value

        try:
            # FIXME: I Model directory path detect repo_id! I stupid!
            self._model = M2M100ForConditionalGeneration.from_pretrained(
                f"{model_dir_path}", local_files_only=True
            )
            self._tokenizer = M2M100Tokenizer.from_pretrained(
                f"{model_dir_path}", local_files_only=True
            )

        except OSError:
            model_dir_path.mkdir(parents=True, exist_ok=True)

            try:
                result = subprocess.run(
                    [
                        "huggingface-cli",
                        "download",
                        f"facebook/m2m100_{variant.value}",
                        "--local-dir",
                        model_dir_path,
                        "--local-dir-use-symlinks",
                        "False",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.stderr:
                    raise ConnectionError(f"{result.stderr.strip()}")

                self._model = M2M100ForConditionalGeneration.from_pretrained(
                    f"{model_dir_path}", local_files_only=True
                )
                self._tokenizer = M2M100Tokenizer.from_pretrained(
                    f"{model_dir_path}", local_files_only=True
                )

            except ConnectionError as e:
                raise ConnectionError(f"{e}")

            except Exception as e:
                raise RuntimeError(f"Error translating: {e}")

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
