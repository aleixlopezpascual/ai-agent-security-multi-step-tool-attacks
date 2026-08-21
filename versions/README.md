# Attack Version Catalog

Each file here is a standalone `class AttackAlgorithm` runnable with
`evaluate_local.py --attack versions/<file>.py` (see `../docs/guides/VERSIONING_WORKFLOW.md`).
Kaggle scores below are the recorded public-leaderboard results from `docs/reports/EXPERIMENTS.md`.

| File | Description | Local (Gemma) | Local (GPT-OSS) | Kaggle public (mean) | Status |
|---|---|---|---|---|---|
| `v1_original.py` | BURST_K=1 ground-truth original | **180.0** @8750s/gym (2000/2000 cap hit — 2026-08-21) | not yet run | **88.740** | Calibration anchor — do not delete |
| `v6_adaptive.py` | Model-Adaptive Sizing, BURST_K=2, warm-up latency classification | 37.85 @900s/sandbox (stale env, historical) | not yet run | — (not submitted standalone) | Superseded by v7 |
| `v7_k1_live.py` | Ultra-Stable K=1 Model-Adaptive Sizing (extracted from `notebooks/ai-agent-security-v15.ipynb`, the current live submission) | not yet run | not yet run | pending (~106.2 projected) | **Current live submission** |

Notes:
- **Kaggle public score is `mean(gemma_public, gpt_oss_public)`, not per-model.** Don't
  compare a single-model local run directly to `88.740` — run `--model both` (or
  `./simulate_kaggle.sh`) and compare `local_public_mean`. See
  `../docs/guides/LOCAL_EVALUATION.md` §5 for the full calibration procedure and the caveat
  behind the v1_original Gemma-only 180.0 figure.
- Older local scores marked "stale env" ran under `EnvSelection.SANDBOX` at 900s (pre-fix) —
  treat as historical only, not comparable to new `gym`/8750s runs.
- New runs auto-append to `../results/results.jsonl`. Add a row here whenever a new version
  gets extracted, evaluated, or submitted.
