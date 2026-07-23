# Limitations

- The ATS score is a heuristic score from this project, not a score from a commercial ATS vendor.
- The evaluation dataset is small and synthetic. It is useful for regression checks, not broad accuracy claims.
- Scanned or image-only PDFs are rejected unless OCR has already been applied.
- PDF extraction quality depends on how the resume PDF is generated.
- The public-demo usage limiter is file-backed and can reset when the deployment restarts or changes instance.
- The usage limiter is not designed for high-security abuse prevention or multi-replica deployments.
- MLX explanations require Apple Silicon with Apple Metal and the optional `mlx-lm` dependency.
- Public cloud deployments should run deterministic mode unless the runtime explicitly supports MLX.
- No license file is currently present.

## Recommended Next Improvements

- Add OCR support for scanned PDFs.
- Expand the synthetic evaluation dataset across more job families.
- Add screenshots for successful analysis output.
- Add a durable usage-counter backend if the public demo receives real traffic.
- Add an explicit license.
