from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.scorer import analyze_resume  # noqa: E402
from utils.pdf_reader import extract_text_from_pdf  # noqa: E402

RESULTS_JSON = ROOT / "benchmarks" / "results.json"
RESULTS_MD = ROOT / "benchmarks" / "results.md"

RESUME_TEXT = """
Summary Applied AI Engineer with Python, FastAPI, LLM systems, retrieval augmented
generation, evaluation, pytest, CI, Docker deployment, monitoring, data pipelines,
and production API experience.

Experience
- Built deterministic scoring services for document matching workflows.
- Added pytest coverage, GitHub Actions CI, deployment smoke tests, and benchmark scripts.
- Implemented privacy-aware PDF parsing and user-facing error handling.

Skills
Python, FastAPI, Streamlit, PyMuPDF, LLMs, RAG, evaluation, pytest, CI, Docker,
deployment, observability, benchmarking.
"""

JOB_DESCRIPTION = """
Role: Applied AI Engineer. We need Python, FastAPI, LLM systems, retrieval augmented
generation, evaluation, pytest, CI, Docker, deployment, monitoring, privacy-aware
document processing, and prompt engineering.
"""


def make_pdf(text: str) -> BytesIO:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    data = document.tobytes()
    document.close()
    file_obj = BytesIO(data)
    file_obj.name = "synthetic_resume.pdf"
    return file_obj


def timed(fn):
    start = time.perf_counter()
    value = fn()
    return value, (time.perf_counter() - start) * 1000


def summarize(samples: list[float]) -> dict:
    return {
        "runs": len(samples),
        "min_ms": min(samples),
        "median_ms": statistics.median(samples),
        "max_ms": max(samples),
        "mean_ms": statistics.mean(samples),
    }


def run_benchmarks(iterations: int) -> dict:
    pdf_extraction_ms = []
    scoring_ms = []
    total_analysis_ms = []
    score_samples = []

    for _ in range(iterations):
        pdf = make_pdf(RESUME_TEXT)
        resume_text, pdf_ms = timed(lambda pdf=pdf: extract_text_from_pdf(pdf))
        _, score_ms = timed(
            lambda resume_text=resume_text: analyze_resume(resume_text, JOB_DESCRIPTION)
        )
        analysis, total_ms = timed(
            lambda: analyze_resume(extract_text_from_pdf(make_pdf(RESUME_TEXT)), JOB_DESCRIPTION)
        )

        pdf_extraction_ms.append(pdf_ms)
        scoring_ms.append(score_ms)
        total_analysis_ms.append(total_ms)
        score_samples.append(analysis["score"])

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "processor": platform.processor(),
        },
        "methodology": {
            "iterations": iterations,
            "data": "Synthetic text-based PDF resume and synthetic job description.",
            "mlx": "Not included. This benchmark measures deterministic PDF extraction and scoring only.",
        },
        "score_reproducible": len(set(score_samples)) == 1,
        "score_samples": score_samples,
        "pdf_extraction": summarize(pdf_extraction_ms),
        "deterministic_scoring": summarize(scoring_ms),
        "total_analysis_without_mlx": summarize(total_analysis_ms),
    }


def write_markdown(results: dict, path: Path) -> None:
    lines = [
        "# Benchmark Results",
        "",
        "These results are one local run on synthetic data. They should be treated as reproducibility evidence, not universal performance claims.",
        "",
        f"- Generated at: `{results['generated_at']}`",
        f"- Python: `{results['environment']['python']}`",
        f"- Platform: `{results['environment']['platform']}`",
        f"- Iterations: `{results['methodology']['iterations']}`",
        f"- Score reproducible: `{results['score_reproducible']}`",
        "",
        "## Latency",
        "",
    ]
    for label, key in [
        ("PDF extraction", "pdf_extraction"),
        ("Deterministic scoring", "deterministic_scoring"),
        ("Total analysis without MLX", "total_analysis_without_mlx"),
    ]:
        stats = results[key]
        lines.extend(
            [
                f"### {label}",
                "",
                f"- Median latency: `{stats['median_ms']:.2f} ms`",
                f"- Mean latency: `{stats['mean_ms']:.2f} ms`",
                f"- Min/Max latency: `{stats['min_ms']:.2f} ms` / "
                f"`{stats['max_ms']:.2f} ms`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic ATS latency benchmarks.")
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--results-json", type=Path, default=RESULTS_JSON)
    parser.add_argument("--results-md", type=Path, default=RESULTS_MD)
    args = parser.parse_args()

    results = run_benchmarks(max(1, args.iterations))
    args.results_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_markdown(results, args.results_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
