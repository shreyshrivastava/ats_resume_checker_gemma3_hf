# ATS Resume Checker with GPT-OSS via Hugging Face

This Streamlit app compares a PDF resume against a pasted job description and returns structured ATS-style feedback using Hugging Face's `InferenceClient`.

The current backend model is:

```text
openai/gpt-oss-120b:cerebras
```

## Features

- Upload a resume as a PDF
- Paste a job description
- Extract resume text with PyMuPDF
- Generate an ATS match score, matched skills, gaps, keywords, recommendations, and summary verdict

## Requirements

- Python
- Streamlit
- PyMuPDF
- huggingface_hub
- A Hugging Face token available as `HF_TOKEN`

## Run Locally

```bash
pip install -r requirements.txt
export HF_TOKEN="your_hugging_face_token"
streamlit run app.py
```

## Project Structure

```text
app.py                 # Streamlit entry point
backend/processor.py   # Prompt construction and Hugging Face model call
frontend/ui.py         # Streamlit input controls
utils/pdf_reader.py    # PDF text extraction
```
