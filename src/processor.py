"""
Placeholder for the sheet music → HTML guide pipeline.

TODO: replace `analyze()` with the real implementation:
  1. Convert PDF pages / images to per-page images (PyMuPDF / pdf2image)
  2. Send each image to Claude Vision API
  3. Parse the structured JSON response (notes, chords, fingering, time-sig …)
  4. Render the JSON into an HTML guide via a template

Input  : raw bytes of the uploaded PDF or image file + original filename
Output : rendered HTML string (same structure as assets/sample_output.html)
"""

import time
from pathlib import Path

_SAMPLE = Path(__file__).parent.parent / "assets" / "sample_output.html"


def analyze(file_bytes: bytes, filename: str) -> str:
    time.sleep(1.5)  # simulate API latency
    return _SAMPLE.read_text(encoding="utf-8")
