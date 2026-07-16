import os

import streamlit as st
from huggingface_hub import InferenceClient
from utils.pdf_reader import extract_text_from_pdf


def get_hf_token():
    return st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")


def process_resume(resume_file, job_description):
    resume_text = extract_text_from_pdf(resume_file)

    prompt = f"""
You are an expert ATS analyst and career advisor. Compare the candidate's resume against the job description and produce a concise, recruiter-style fit report.

=== JOB DESCRIPTION ===
{job_description}

=== CANDIDATE RESUME ===
{resume_text}

=== OUTPUT FORMAT ===
Use this exact structure and style:

1. [Company Name if available] — [Role Title if available]

Location: [Location from job description, or "Not specified"]
Freshness: [Use "Not specified" unless the job description includes a posting date or urgency.]

Why it matches
- [Short reason based only on resume evidence.]
- [Short reason based only on resume evidence.]
- [Short reason based only on resume evidence.]

Key requirements
- [Requirement from the job description]
- [Requirement from the job description]
- [Requirement from the job description]
- [Requirement from the job description]

Likely gaps
- [Gap or weaker area. If there are no major gaps, say "No major gaps found from the provided resume."]
- [Optional second gap]

Resume keywords

[Comma-separated keywords the candidate should add or emphasize if accurate.]

Fit: [score]/10

=== RULES ===
- Be direct, specific, and concise.
- Do not invent experience, dates, locations, companies, or skills.
- If company or role is unclear, infer a simple title from the job description and mark uncertain details as "Not specified".
- Keep each bullet to one sentence.
- Score honestly based on evidence in the resume.
"""

    try:
        hf_token = get_hf_token()
        if not hf_token:
            return "Error: HF_TOKEN is not configured. Add it to Streamlit Cloud secrets or your local environment."

        client = InferenceClient(token=hf_token)

        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b:cerebras",
            max_tokens=1024,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {e}"
