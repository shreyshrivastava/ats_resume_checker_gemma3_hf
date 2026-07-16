# Project Architecture

The app is designed as a deterministic ATS checker:

- A deterministic scoring engine creates the ATS score and evidence.
- The UI renders the score, role gaps, keyword matches, and resume changes as readable feedback.
- A passcode gate protects the deployed Streamlit app from casual public usage.

## System Diagram

```mermaid
flowchart TD
    A["User uploads PDF resume"] --> B["Streamlit UI<br/>app.py + frontend/ui.py"]
    C["User pastes job description"] --> B
    L["User enters passcode"] --> B
    B --> D["PDF text extraction<br/>utils/pdf_reader.py"]
    D --> E["Field-agnostic ATS scoring<br/>backend/scorer.py"]
    C --> E
    E --> F["Deterministic ATS report<br/>score, keywords, role gaps, fixes"]
    F --> J["Polished feedback UI"]
    B --> K["Runtime logs<br/>logs/ats_resume_checker.log"]
    D --> K
    E --> K
```

## Runtime Flow

1. `app.py` configures logging and renders the Streamlit page.
2. `frontend/ui.py` collects the PDF resume and job description.
3. `utils/pdf_reader.py` extracts plain text from the uploaded PDF using PyMuPDF.
4. `backend/scorer.py` calculates deterministic ATS signals:
   - matched keywords
   - missing or weak keywords
   - role/title alignment
   - resume section structure
   - content depth
   - role gaps
   - resume changes for the target job
5. `backend/processor.py` returns the deterministic report.
6. `frontend/ui.py` renders the score ring, keyword lists, role gaps, resume-change guidance, and score breakdown.

## Logging

Runtime logs are written to:

```text
logs/ats_resume_checker.log
```

The log file is intentionally ignored by git. It captures:

- app startup
- blocked submissions
- accepted submissions
- uploaded filename and job-description length
- extracted resume text size
- computed score and verdict
- passcode validation events

## Key Files

```text
app.py                    Streamlit entry point and submit flow
frontend/ui.py            UI styling, input controls, and feedback rendering
backend/scorer.py         Deterministic field-agnostic ATS scoring
backend/processor.py      PDF-to-report orchestration
utils/pdf_reader.py       PDF text extraction
utils/logging_config.py   Console and file logging setup
```
