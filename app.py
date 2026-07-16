import streamlit as st
from frontend.ui import render_ui, render_feedback
from backend.processor import process_resume

st.set_page_config(page_title="ATS Resume Checker", page_icon="🔍", layout="centered")

resume_file, job_description, submit = render_ui()

if submit:
    if not resume_file or not job_description.strip():
        st.warning("Upload a resume and paste a job description.")
    else:
        with st.spinner("Analyzing your resume..."):
            feedback = process_resume(resume_file, job_description)
        render_feedback(feedback)
