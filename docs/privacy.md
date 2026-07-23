# Privacy

## Data Processed

The app processes:

- uploaded PDF resume files
- pasted job descriptions
- Streamlit client context used for best-effort client identification

The resume and job description are used to generate a deterministic ATS-style report. When MLX is enabled locally, the deterministic report and a truncated job description are sent to the local MLX subprocess for explanation.

## Data Stored

The app does not intentionally store uploaded resumes or pasted job descriptions.

Runtime logs are written to `logs/ats_resume_checker.log` by default. Logs include filenames, input lengths, score metadata, error categories, and fallback events. Logs should not include full resume text, full job-description text, raw IP addresses, API keys, or model outputs.

The usage limiter stores a local JSON file at `/tmp/ats_resume_checker_usage.json` by default. It contains:

- a generated salt when `ATS_USAGE_SALT` is not set
- salted client hashes
- run counts
- update timestamps

It does not store raw IP addresses.

## Local Versus Cloud Processing

Deterministic mode runs locally in the Python process and does not call paid APIs.

MLX mode runs locally through `mlx-lm` and is intended for Apple Silicon machines with Apple Metal. The normal CI and Streamlit Cloud path disables MLX.

## External Services

The application does not use external LLM APIs. Streamlit Cloud, if used, receives the uploaded content as part of normal app hosting. Do not claim end-to-end private processing on Streamlit Cloud because the deployment platform still handles user uploads.

## User Guidance

Use synthetic or anonymized resumes for demos. Do not upload sensitive resumes to a public deployment unless the hosting and logging configuration are acceptable for that data.
