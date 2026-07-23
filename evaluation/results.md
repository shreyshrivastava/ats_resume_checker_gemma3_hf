# Evaluation Results

Synthetic, anonymized resume/job-description pairs are used to check deterministic ranking behavior.

- Generated at: `2026-07-23T15:01:46.701578+00:00`
- Cases: `6`
- Ranking groups: `2`
- Ranking consistency rate: `100.00%`

## Ranking Groups

### applied_ai_engineer (pass)

- Expected: `ai_strong, ai_moderate, ai_weak`
- Actual: `ai_strong, ai_moderate, ai_weak`

### staff_nurse (pass)

- Expected: `nurse_strong, nurse_moderate, nurse_weak`
- Actual: `nurse_strong, nurse_moderate, nurse_weak`

## Case Scores

- `ai_strong`: score `83`, verdict `Strong match`
- `ai_moderate`: score `21`, verdict `Needs improvement`
- `ai_weak`: score `11`, verdict `Needs improvement`
- `nurse_strong`: score `77`, verdict `Strong match`
- `nurse_moderate`: score `21`, verdict `Needs improvement`
- `nurse_weak`: score `16`, verdict `Needs improvement`
