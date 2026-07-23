# Deployment

## Recommended Target

Use Streamlit Cloud for a lightweight public demo in deterministic mode.

Recommended settings:

- Repository: `shreyshrivastava/ats-resume-checker`
- Branch: `main` after these changes are merged
- Main file path: `app.py`
- Environment/secrets: `ATS_ENABLE_MLX=0`

The app should not require MLX, Apple Silicon, a GPU, paid APIs, private model downloads, or private credentials in cloud mode.

## MLX Deployment Decision

MLX is preserved for local Apple Silicon use. It is intentionally outside `requirements.txt` because typical Linux CI and Streamlit Cloud environments do not expose Apple Metal.

For local MLX demos:

```bash
pip install -r requirements-mlx.txt
ATS_ENABLE_MLX=1 streamlit run app.py
```

## Usage Limit Configuration

The public-demo limiter allows two analysis runs per client address by default.

Useful settings:

```bash
ATS_USAGE_LIMIT=2
ATS_USAGE_LIMIT_ENABLED=1
ATS_USAGE_LIMIT_PATH=/tmp/ats_resume_checker_usage.json
ATS_USAGE_SALT=<streamlit-secret-value>
```

Set `ATS_USAGE_LIMIT_ENABLED=0` for unrestricted local development.

## Current Live URL Status

`https://atsresumecheckershrey.streamlit.app/` was checked on 2026-07-23 and redirected to Streamlit login, so it was not verified as a publicly accessible demo.

Remaining manual step:

1. Push this branch after review.
2. Merge or deploy the updated branch on Streamlit Cloud.
3. Set `ATS_ENABLE_MLX=0` and optionally `ATS_USAGE_SALT`.
4. Enable public sharing/access for the Streamlit app.
5. Recheck the public URL and update the README if it loads without authentication.

## CI/CD

`.github/workflows/ci.yml` runs linting, compilation, tests, evaluation, and a benchmark smoke test.

`.github/workflows/benchmark.yml` runs deterministic benchmarks manually or on a weekly schedule and uploads result artifacts.

Streamlit Cloud handles deployment from the connected branch. A separate GitHub Actions deployment workflow is not included because Streamlit Cloud deployments are managed by Streamlit's service.
