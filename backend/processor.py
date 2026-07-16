import os

import streamlit as st
from huggingface_hub import InferenceClient
from utils.pdf_reader import extract_text_from_pdf


def get_hf_token():
    return st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")


def process_resume(resume_file, job_description):
    resume_text = extract_text_from_pdf(resume_file)

    prompt = f"""
You are an expert ATS (Applicant Tracking System) analyst and professional resume consultant with 15+ years of experience in technical recruiting and career coaching.

Analyze the candidate's resume against the job description below and produce a structured, actionable evaluation.

=== JOB DESCRIPTION ===
{job_description}

=== CANDIDATE RESUME ===
{resume_text}

=== INSTRUCTIONS ===
Evaluate strictly based on the content provided. Do not assume skills or experience not explicitly stated or clearly implied. Be honest and specific.

Provide your analysis in the following format:

## 1. Overall ATS Match Score
Give a score from 0-100 with brief justification.

## 2. Matched Skills & Qualifications
List specific matches between resume and job description.

## 3. Missing or Weak Areas
Identify specific gaps, prioritized by importance.

## 4. Keyword Optimization
List 5-8 missing keywords that would improve ATS parsing.

## 5. Actionable Recommendations
Provide 3-5 concrete suggestions to improve alignment.

## 6. Summary Verdict
One short paragraph on overall fit.

Keep the tone professional, direct, and constructive.
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
