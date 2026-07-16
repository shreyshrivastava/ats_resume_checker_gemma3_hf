# ATS Resume Checker

This Streamlit app compares a PDF resume against a pasted job description and returns field-agnostic ATS-style feedback. The core score is deterministic so it works across software, medical, business, finance, education, and other roles.

Live app: https://atsresumecheckershrey.streamlit.app/

## Features

- Upload a resume as a PDF
- Paste a job description
- Extract resume text with PyMuPDF
- Generate an ATS match score, matched keywords, missing keywords, role gaps, resume changes, recommendations, and summary verdict
- Write runtime logs for debugging and analysis

## Screenshots

![ATS Resume Checker UI](docs/screenshots/app-home.svg)

## Documentation

- [Project architecture](docs/architecture.md)
- Runtime logs: `logs/ats_resume_checker.log`

## Requirements

- Python
- Streamlit
- PyMuPDF

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud

Use these settings when creating the app in Streamlit Cloud:

- Repository: `shreyshrivastava/ats_resume_checker_gemma3_hf`
- Branch: `streamlit-cloud`
- Main file path: `app.py`

The deployed app is protected by a simple passcode gate.

## Project Structure

```text
app.py                 # Streamlit entry point
backend/scorer.py      # Deterministic field-agnostic ATS scoring
backend/processor.py   # PDF-to-report orchestration
frontend/ui.py         # Streamlit input controls
utils/pdf_reader.py    # PDF text extraction
utils/logging_config.py # Runtime logging setup
```
