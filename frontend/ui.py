def render_ui():
    # Remove Ollama section completely
    st.markdown("---")
    resume_file = st.file_uploader("📄 Upload Resume (PDF)", type="pdf")
    job_description = st.text_area("📋 Paste Job Description", height=200)
    submit = st.button("📝 Get ATS Feedback")

    return resume_file, job_description, submit
