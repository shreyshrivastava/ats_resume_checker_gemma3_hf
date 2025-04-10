import os
import requests
from utils.pdf_reader import extract_text_from_pdf
import streamlit as st

def process_resume(resume_file, job_description):
    resume_text = extract_text_from_pdf(resume_file)

    prompt = f"""
You are a smart ATS resume analyzer powered by Gemma.

Job Description:
{job_description}

Candidate Resume:
{resume_text}

Provide a short ATS-style match report:
1. Skills matched
2. Missing qualifications or gaps
3. Suggestions to improve the resume
4. Overall ATS match score (0-100)
"""

    hf_token = os.getenv("HF_TOKEN")
    api_url = "https://api-inference.huggingface.co/models/google/gemma-7b-it"

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 512
        }
    }

    response = requests.post(api_url, headers=headers, json=payload)

    try:
        result = response.json()
        if isinstance(result, list):
            return result[0]['generated_text']
        return result.get('generated_text', str(result))
    except Exception as e:
        return f"❌ Error: {e}\nRaw response: {response.text}"
