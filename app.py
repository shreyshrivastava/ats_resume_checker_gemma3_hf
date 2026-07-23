import logging

import streamlit as st

from backend.processor import process_resume
from frontend.ui import render_feedback, render_ui
from utils.logging_config import configure_logging
from utils.usage_limiter import consume_usage, get_client_identifier

configure_logging()
logger = logging.getLogger(__name__)

st.set_page_config(page_title="ATS Resume Checker", page_icon="🔍", layout="centered")
logger.info("ATS Resume Checker app started")


resume_file, job_description, submit = render_ui()

if submit:
    if not resume_file or not job_description.strip():
        logger.warning(
            "Submit blocked: missing resume_file=%s job_description_present=%s",
            bool(resume_file),
            bool(job_description.strip()),
        )
        st.warning("Upload a resume and paste a job description.")
    else:
        usage_decision = consume_usage(get_client_identifier(st))
        if not usage_decision.allowed:
            logger.warning("Usage limit reached: client_key=%s", usage_decision.client_key)
            st.error(f"Analysis limit reached. Each IP address can run {usage_decision.max_runs} reports.")
            st.stop()

        logger.info(
            "Submit accepted: file=%s job_description_chars=%s",
            getattr(resume_file, "name", "uploaded.pdf"),
            len(job_description),
        )
        with st.spinner("Analyzing your resume..."):
            feedback = process_resume(resume_file, job_description)
        logger.info("Feedback rendered: chars=%s", len(feedback))
        render_feedback(feedback)
        st.download_button(
            "Download report",
            feedback,
            file_name="ats_resume_report.md",
            mime="text/markdown",
        )
        if usage_decision.runs_remaining:
            st.caption(f"{usage_decision.runs_remaining} analysis run remaining from this IP address.")
        else:
            st.caption("No analysis runs remaining from this IP address.")
