from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

# IMPORTANT:
# Must be set BEFORE importing paddleocr.
#
# This avoids the current PIR + oneDNN CPU issue:
# ConvertPirAttribute2RuntimeAttribute
# not support [pir::ArrayAttribute<pir::DoubleAttribute>]
os.environ["FLAGS_enable_pir_api"] = "0"

from paddleocr import PaddleOCR


class OCRService:

    def __init__(self) -> None:
        self.ocr: PaddleOCR | None = None

    def _load_model(self) -> PaddleOCR:

        if self.ocr is not None:
            return self.ocr

        print("=" * 70)
        print("Loading PaddleOCR")
        print("Mode: CPU")
        print("Document orientation: OFF")
        print("Document unwarping: OFF")
        print("Text-line orientation: OFF")
        print("MKL-DNN / oneDNN: OFF")
        print("=" * 70)

        self.ocr = PaddleOCR(
            lang="en",
            device="cpu",

            # IMPORTANT FIX
            enable_mkldnn=False,

            # Disable unnecessary document processing
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,

            # Use OCR models directly
            text_detection_model_name="PP-OCRv5_server_det",
            text_recognition_model_name="en_PP-OCRv5_mobile_rec",

            # CPU performance
            cpu_threads=8,
        )

        print("PaddleOCR model loaded.")
        print("=" * 70)

        return self.ocr

    def process(self, input_path: str | Path) -> list[Any]:

        input_path = str(input_path)

        ocr = self._load_model()

        start_time = time.perf_counter()

        print(f"OCR processing: {input_path}")

        results = list(
            ocr.predict(
                input=input_path
            )
        )

        elapsed = time.perf_counter() - start_time

        print(
            f"OCR completed in {elapsed:.2f} seconds"
        )

        return results


# IMPORTANT:
# routes.py expects this exact variable.
ocr_service = OCRService()