# ATS Resume Checker with GPT-OSS via Hugging Face

This Streamlit app compares a PDF resume against a pasted job description and returns structured ATS-style feedback using a local MLX model.

Live app: https://atsresumecheckershrey.streamlit.app/

The default backend model is:

```text
mlx-community/gemma-3-1b-it-4bit
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
- mlx-lm
- Apple Silicon Mac for local MLX inference

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

To use a different MLX model, set it in Streamlit secrets:

```toml
MLX_MODEL = "path-or-mlx-model-repo"
```

## Deploy on Streamlit Cloud

Use these settings when creating the app in Streamlit Cloud:

- Repository: `shreyshrivastava/ats_resume_checker_gemma3_hf`
- Branch: `streamlit-cloud`
- Main file path: `app.py`

Note: MLX is designed for Apple Silicon Macs. Streamlit Cloud typically runs Linux containers, so this branch is best for local MLX use unless your deployment runtime supports MLX.

## Project Structure

```text
app.py                 # Streamlit entry point
backend/processor.py   # Prompt construction and Hugging Face model call
frontend/ui.py         # Streamlit input controls
utils/pdf_reader.py    # PDF text extraction
```
