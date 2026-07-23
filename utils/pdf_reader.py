from __future__ import annotations

import os
from typing import BinaryIO

import fitz  # PyMuPDF

DEFAULT_MAX_PDF_BYTES = 8 * 1024 * 1024


class PDFReadError(ValueError):
    """Raised when an uploaded PDF cannot be read safely."""


class PDFTooLargeError(PDFReadError):
    """Raised when an uploaded PDF exceeds the configured size limit."""


def get_max_pdf_bytes() -> int:
    raw_limit = os.getenv("ATS_MAX_PDF_BYTES")
    if not raw_limit:
        return DEFAULT_MAX_PDF_BYTES
    try:
        return max(1, int(raw_limit))
    except ValueError:
        return DEFAULT_MAX_PDF_BYTES


def _read_uploaded_bytes(uploaded_file: BinaryIO) -> bytes:
    if hasattr(uploaded_file, "getvalue"):
        data = uploaded_file.getvalue()
    else:
        try:
            uploaded_file.seek(0)
        except (AttributeError, OSError):
            pass
        data = uploaded_file.read()
        try:
            uploaded_file.seek(0)
        except (AttributeError, OSError):
            pass

    if isinstance(data, str):
        data = data.encode("utf-8")
    return data or b""


def extract_text_from_pdf(uploaded_file: BinaryIO, max_bytes: int | None = None) -> str:
    pdf_bytes = _read_uploaded_bytes(uploaded_file)
    limit = max_bytes if max_bytes is not None else get_max_pdf_bytes()

    if not pdf_bytes:
        raise PDFReadError("The uploaded PDF is empty.")
    if len(pdf_bytes) > limit:
        raise PDFTooLargeError(
            f"The uploaded PDF is too large. Limit: {limit // (1024 * 1024)} MB."
        )

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            text = "\n".join(page.get_text("text") for page in doc)
    except Exception as exc:
        raise PDFReadError("The uploaded file could not be read as a valid PDF.") from exc

    if not text.strip():
        raise PDFReadError(
            "No extractable text was found. Scanned or image-only PDFs are not supported yet."
        )
    return text
