# Technical Decisions

## Deterministic Score As Source Of Truth

The project keeps deterministic scoring as the authoritative output because resume/job matching should be reproducible and inspectable. The optional LLM layer can improve explanation quality, but it must not change the score or scoring evidence.

## Optional MLX Instead Of Required MLX

`mlx-lm` is kept in `requirements-mlx.txt`, not `requirements.txt`. This preserves Apple Silicon support while allowing Linux CI and Streamlit Cloud to run without Apple Metal.

## Synthetic Evaluation Data

The evaluation data is synthetic to avoid committing personal resumes or sensitive user data. The current evaluation checks ranking consistency for strong, moderate, and weak pairs, rather than claiming production accuracy.

## File-Backed Usage Limiter

The two-run public-demo limit uses a local JSON file because it is simple, free, and compatible with Streamlit Cloud. Raw IP addresses are not stored; client identifiers are hashed with HMAC.

This is sufficient for a portfolio demo but should be replaced with durable storage if the app needs strong abuse prevention.
