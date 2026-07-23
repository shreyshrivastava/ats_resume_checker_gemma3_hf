import logging
import os
import platform
import subprocess
import sys
from importlib.util import find_spec

import streamlit as st

from backend.scorer import analyze_resume, format_ats_report
from utils.pdf_reader import PDFReadError, extract_text_from_pdf

DEFAULT_MLX_MODEL = "mlx-community/gemma-3-1b-it-4bit"
MAX_TOKENS = 900
DEFAULT_MLX_TIMEOUT_SECONDS = 300
logger = logging.getLogger(__name__)


def _secret_or_env(name, default=None):
    if name in os.environ:
        return os.environ[name]
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def get_mlx_model_name():
    return _secret_or_env("MLX_MODEL", DEFAULT_MLX_MODEL)


def is_ci_or_sandbox():
    return any(
        os.getenv(name)
        for name in ("CI", "GITHUB_ACTIONS", "CODEX_SANDBOX", "CODEX_CI")
    )


def _flag_value(name, default="auto"):
    return str(_secret_or_env(name, default)).strip().lower()


def mlx_package_available():
    return find_spec("mlx_lm") is not None


def should_use_mlx():
    mode = _flag_value("ATS_ENABLE_MLX", "auto")
    if mode in {"0", "false", "no", "off", "disabled", "never"}:
        return False
    if mode in {"1", "true", "yes", "on", "enabled", "always"}:
        return True

    return (
        platform.system() == "Darwin"
        and platform.machine().lower().startswith("arm")
        and not is_ci_or_sandbox()
        and mlx_package_available()
    )


def get_mlx_timeout_seconds():
    raw_timeout = _secret_or_env("ATS_MLX_TIMEOUT_SECONDS", DEFAULT_MLX_TIMEOUT_SECONDS)
    try:
        return max(1, int(raw_timeout))
    except (TypeError, ValueError):
        return DEFAULT_MLX_TIMEOUT_SECONDS


def build_mlx_prompt(ats_report, job_description):
    return f"""
You are an ATS resume advisor. Explain the deterministic ATS-style analysis below in clear, helpful language.
Do not change the score, matched keywords, missing keywords, or scoring evidence. Your job is only to explain what the user should fix.

=== ATS ANALYSIS ===
{ats_report}

=== JOB DESCRIPTION ===
{job_description[:4000]}

Return the same headings as the ATS analysis. Add one short "How to improve" section with practical resume edits.
"""


def generate_with_mlx(prompt, max_tokens=MAX_TOKENS):
    model_name = get_mlx_model_name()
    logger.info("Starting MLX generation: model=%s prompt_chars=%s", model_name, len(prompt))
    code = """
import sys
from mlx_lm import generate, load

model_name = sys.argv[1]
max_tokens = int(sys.argv[2])
prompt = sys.stdin.read()

model, tokenizer = load(model_name)
output = generate(
    model,
    tokenizer,
    prompt=prompt,
    max_tokens=max_tokens,
    temp=0.4,
    verbose=False,
)
print(output)
"""
    result = subprocess.run(
        [sys.executable, "-c", code, model_name, str(max_tokens)],
        input=prompt,
        text=True,
        capture_output=True,
        timeout=get_mlx_timeout_seconds(),
    )
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "Unknown MLX error."
        logger.warning("MLX generation failed: returncode=%s error=%s", result.returncode, error[:500])
        if "No Metal device available" in error or "metal" in error.lower():
            return (
                "Error: MLX needs Apple Metal/GPU access, but this runtime does not expose a Metal device. "
                "Run the app from your normal Mac Terminal for real MLX generation."
            )
        return f"Error: MLX generation failed. {error}"
    logger.info("MLX generation completed: output_chars=%s", len(result.stdout))
    return result.stdout.strip()


def process_resume(resume_file, job_description):
    logger.info(
        "Processing resume: file=%s job_description_chars=%s",
        getattr(resume_file, "name", "uploaded.pdf"),
        len(job_description),
    )
    try:
        resume_text = extract_text_from_pdf(resume_file)
    except PDFReadError as exc:
        logger.warning("PDF extraction failed: file=%s error=%s", getattr(resume_file, "name", "uploaded.pdf"), exc)
        return (
            "ATS Match Score: 0/100\n\n"
            "Verdict: Unable to analyze resume\n\n"
            "Target Role: Target role\n\n"
            f"What this means:\n{exc}\n\n"
            "Recommended Fixes:\n"
            "- Upload a text-based PDF exported from your resume editor.\n"
            "- Avoid scanned images unless OCR has been applied.\n"
            "- Keep the file size within the configured upload limit.\n\n"
            "Fit: 0/10"
        )

    logger.info("PDF extracted: resume_chars=%s resume_words=%s", len(resume_text), len(resume_text.split()))
    analysis = analyze_resume(resume_text, job_description)
    ats_report = format_ats_report(analysis)
    logger.info(
        "ATS score computed: score=%s verdict=%s matched_terms=%s missing_terms=%s",
        analysis["score"],
        analysis["verdict"],
        len(analysis["matched_terms"]),
        len(analysis["missing_terms"]),
    )

    if not should_use_mlx():
        logger.info("Returning deterministic ATS report without MLX")
        return ats_report

    prompt = build_mlx_prompt(ats_report, job_description)

    try:
        explanation = generate_with_mlx(prompt)
        if explanation.startswith("Error:"):
            logger.info("Using deterministic ATS report because MLX returned an error")
            return ats_report
        return explanation
    except Exception as e:
        logger.exception("Processing failed; returning deterministic ATS report: %s", e)
        return ats_report
