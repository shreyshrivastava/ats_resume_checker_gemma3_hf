import logging

from backend.scorer import analyze_resume, format_ats_report
from utils.pdf_reader import extract_text_from_pdf

logger = logging.getLogger(__name__)


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

    return ats_report
