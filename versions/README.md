# Attack Version Catalog

Each file here is a standalone `class AttackAlgorithm` runnable with
`evaluate_local.py --attack versions/<file>.py` (see `../docs/guides/VERSIONING_WORKFLOW.md`).
Kaggle scores below are the recorded public-leaderboard results from `docs/reports/EXPERIMENTS.md`.

| File | Description | Local (Gemma) | Kaggle public | Status |
|---|---|---|---|---|
| `v1_original.py` | BURST_K=1 ground-truth original | 49.68 @900s / sandbox (stale env) — recalibrating @8750s/gym | **88.740** | Calibration anchor — do not delete |
| `v6_adaptive.py` | Model-Adaptive Sizing, BURST_K=2, warm-up latency classification | 37.85 @900s / sandbox (stale env) | — (not submitted standalone) | Superseded by v7 |
| `v7_k1_live.py` | Ultra-Stable K=1 Model-Adaptive Sizing (extracted from `notebooks/ai-agent-security-v15.ipynb`, the current live submission) | — | pending (~106.2 projected) | **Current live submission** |

Notes:
- Local scores recorded above predate the environment/budget alignment fix (they ran under
  `EnvSelection.SANDBOX` at 900s, not the real `EnvSelection.GYM` at 8750s) — treat them as
  historical, not comparable to new runs. New runs land in `../results/results.jsonl`.
- Add a row here whenever a new version gets extracted, evaluated, or submitted.
