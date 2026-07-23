from io import BytesIO

import fitz
import pytest

from utils.pdf_reader import PDFReadError, PDFTooLargeError, extract_text_from_pdf


def make_pdf(text: str) -> BytesIO:
    document = fitz.open()
    page = document.new_page()
    if text:
        page.insert_text((72, 72), text)
    data = document.tobytes()
    document.close()
    file_obj = BytesIO(data)
    file_obj.name = "synthetic_resume.pdf"
    return file_obj


def test_extract_text_from_valid_pdf():
    pdf = make_pdf("Summary Python FastAPI LLM evaluation")

    text = extract_text_from_pdf(pdf)

    assert "Python FastAPI" in text


def test_extract_text_resets_seekable_file_position():
    pdf = make_pdf("Skills pytest CI deployment")
    pdf.seek(5)

    text = extract_text_from_pdf(pdf)

    assert "pytest CI deployment" in text


def test_malformed_pdf_returns_controlled_error():
    bad_pdf = BytesIO(b"not a real pdf")
    bad_pdf.name = "bad.pdf"

    with pytest.raises(PDFReadError, match="valid PDF"):
        extract_text_from_pdf(bad_pdf)


def test_empty_pdf_returns_controlled_error():
    empty_pdf = BytesIO(b"")
    empty_pdf.name = "empty.pdf"

    with pytest.raises(PDFReadError, match="empty"):
        extract_text_from_pdf(empty_pdf)


def test_image_only_pdf_returns_controlled_error():
    pdf = make_pdf("")

    with pytest.raises(PDFReadError, match="No extractable text"):
        extract_text_from_pdf(pdf)


def test_pdf_size_limit_is_enforced():
    pdf = make_pdf("Summary Python")

    with pytest.raises(PDFTooLargeError):
        extract_text_from_pdf(pdf, max_bytes=10)
