import streamlit as st
from frontend.ui import render_ui, render_feedback
from backend.processor import process_resume
from utils.logging_config import configure_logging
import logging


configure_logging()
logger = logging.getLogger(__name__)

st.set_page_config(page_title="ATS Resume Checker", page_icon="🔍", layout="centered")
logger.info("ATS Resume Checker app started")

resume_file, job_description, submit = render_ui()

if submit:
    if not resume_file or not job_description.strip():
        logger.warning("Submit blocked: missing resume_file=%s job_description_present=%s", bool(resume_file), bool(job_description.strip()))
        st.warning("Upload a resume and paste a job description.")
    else:
        logger.info("Submit accepted: file=%s job_description_chars=%s", getattr(resume_file, "name", "uploaded.pdf"), len(job_description))
        with st.spinner("Analyzing your resume..."):
            feedback = process_resume(resume_file, job_description)
        logger.info("Feedback rendered: chars=%s", len(feedback))
        render_feedback(feedback)
