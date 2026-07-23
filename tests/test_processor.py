from io import BytesIO

import fitz

from backend import processor


def make_pdf(text: str) -> BytesIO:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    data = document.tobytes()
    document.close()
    file_obj = BytesIO(data)
    file_obj.name = "resume.pdf"
    return file_obj


def test_should_use_mlx_false_in_ci(monkeypatch):
    monkeypatch.setenv("CI", "1")
    monkeypatch.delenv("ATS_ENABLE_MLX", raising=False)

    assert processor.should_use_mlx() is False


def test_should_use_mlx_can_be_disabled(monkeypatch):
    monkeypatch.setenv("ATS_ENABLE_MLX", "0")

    assert processor.should_use_mlx() is False


def test_process_resume_returns_deterministic_report_without_mlx(monkeypatch):
    monkeypatch.setenv("ATS_ENABLE_MLX", "0")
    resume = make_pdf("Summary Applied AI Engineer. Skills Python FastAPI LLM evaluation.")
    job = "Role: Applied AI Engineer. Python FastAPI LLM evaluation deployment."

    report = processor.process_resume(resume, job)

    assert "ATS Match Score:" in report
    assert "Matched Keywords:" in report
    assert "Fit:" in report


def test_mlx_error_does_not_replace_score_evidence(monkeypatch):
    monkeypatch.setenv("ATS_ENABLE_MLX", "1")
    monkeypatch.setattr(processor, "generate_with_mlx", lambda prompt: "Error: MLX unavailable")
    resume = make_pdf("Summary Applied AI Engineer. Skills Python FastAPI LLM evaluation.")
    job = "Role: Applied AI Engineer. Python FastAPI LLM evaluation deployment."

    report = processor.process_resume(resume, job)

    assert "ATS Match Score:" in report
    assert "Error: MLX unavailable" not in report


def test_malformed_pdf_returns_user_facing_message(monkeypatch):
    monkeypatch.setenv("ATS_ENABLE_MLX", "0")
    bad_pdf = BytesIO(b"bad pdf")
    bad_pdf.name = "bad.pdf"

    report = processor.process_resume(bad_pdf, "Role: AI Engineer")

    assert "Unable to analyze resume" in report
    assert "valid PDF" in report


def test_build_mlx_prompt_preserves_deterministic_boundaries():
    prompt = processor.build_mlx_prompt("ATS Match Score: 72/100", "Python role")

    assert "Do not change the score" in prompt
    assert "ATS Match Score: 72/100" in prompt
