import streamlit as st
from frontend.ui import render_ui
from backend.processor import process_resume

APP_PASSKEY = "2127"

st.set_page_config(page_title="ATS Resume Checker (GPT-OSS via Hugging Face)", layout="centered")
st.title("ATS Resume Checker with GPT-OSS via Hugging Face")

passkey = st.text_input("Passkey", type="password")
if passkey != APP_PASSKEY:
    if passkey:
        st.error("Invalid passkey.")
    st.stop()

resume_file, job_description, submit = render_ui()

if submit and resume_file and job_description:
    with st.spinner("Analyzing with GPT-OSS model..."):
        feedback = process_resume(resume_file, job_description)
    st.subheader("ATS Feedback")
    st.markdown(feedback)
