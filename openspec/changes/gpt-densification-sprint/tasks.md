## 1. Baseline and gating setup

- [x] 1.1 Capture same-session control metrics for `attack.py` on `gpt_oss` and `gemma` (budget=300, seed=123)
- [x] 1.2 Define and document gating thresholds (GPT raw/sec continuation >=1.8x; Gemma regression <=5%)

## 2. Variant implementation

- [x] 2.1 Create `versions/v65_gpt_dense_slow_n2.py` from current control with `SLOW_MULTIPOST_N=2` only
- [x] 2.2 Create `versions/v66_gpt_dense_slow_n3.py` from current control with `SLOW_MULTIPOST_N=3` only
- [x] 2.3 Create `versions/v67_gpt_dense_mail_notify.py` from current control with slow-row EXFIL+mail-notify wording that avoids `send`/`email`/`upload` in user text

## 3. Evaluation and decision

- [x] 3.1 Run `gpt_oss` local evaluations for control and all three variants with identical settings
- [x] 3.2 Compute GPT raw/sec uplift ratios vs control and kill non-qualifying variants
- [x] 3.3 Run Gemma local evaluation for surviving finalists and apply <=5% regression guard
- [x] 3.4 Update `docs/reports/EXPERIMENTS.md` with measured results and final go/no-go
- [x] 3.5 If a variant passes all gates, package and submit that variant to Kaggle
