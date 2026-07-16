import os
import re
import subprocess
import sys
import logging

import streamlit as st
from backend.scorer import analyze_resume, format_ats_report
from utils.pdf_reader import extract_text_from_pdf

DEFAULT_MLX_MODEL = "mlx-community/gemma-3-1b-it-4bit"
MAX_TOKENS = 900
logger = logging.getLogger(__name__)


def get_mlx_model_name():
    try:
        return st.secrets.get("MLX_MODEL", DEFAULT_MLX_MODEL)
    except Exception:
        return DEFAULT_MLX_MODEL


def is_codex_sandbox():
    return os.getenv("CODEX_SANDBOX") or os.getenv("CODEX_CI")


def generate_with_mlx(prompt):
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
        [sys.executable, "-c", code, model_name, str(MAX_TOKENS)],
        input=prompt,
        text=True,
        capture_output=True,
        timeout=300,
    )
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or "Unknown MLX error."
        logger.warning("MLX generation failed: returncode=%s error=%s", result.returncode, error[:500])
        if "No Metal device available" in error:
            return (
                "Error: MLX needs Apple Metal/GPU access, but this runtime does not expose a Metal device. "
                "Run the app from your normal Mac Terminal for real MLX generation."
            )
        return f"Error: MLX generation failed. {error}"
    logger.info("MLX generation completed: output_chars=%s", len(result.stdout))
    return result.stdout.strip()


def process_resume(resume_file, job_description):
    logger.info("Processing resume: file=%s job_description_chars=%s", getattr(resume_file, "name", "uploaded.pdf"), len(job_description))
    resume_text = extract_text_from_pdf(resume_file)
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

    if is_codex_sandbox():
        logger.info("Codex sandbox detected: returning deterministic ATS report without MLX")
        return ats_report

    prompt = f"""
You are an ATS resume advisor. Explain the deterministic ATS-style analysis below in clear, helpful language.
Do not change the score, matched keywords, or missing keywords. Your job is to explain what the user should fix.

=== ATS ANALYSIS ===
{ats_report}

=== JOB DESCRIPTION ===
{job_description[:4000]}

Return the same headings as the ATS analysis. Add one short "How to improve" section with practical resume edits.
"""

    try:
        explanation = generate_with_mlx(prompt)
        if explanation.startswith("Error:"):
            logger.info("Using deterministic ATS report because MLX returned an error")
            return ats_report
        return explanation
    except Exception as e:
        logger.exception("Processing failed; returning deterministic ATS report: %s", e)
        return ats_report
