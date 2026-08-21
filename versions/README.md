# Attack Version Catalog

Each file here is a standalone `class AttackAlgorithm` runnable with
`evaluate_local.py --attack versions/<file>.py` (see `../docs/guides/VERSIONING_WORKFLOW.md`).
Kaggle scores below are the recorded public-leaderboard results from `docs/reports/EXPERIMENTS.md`.

| File | Description | Local (Gemma) | Local (GPT-OSS) | Local mean | Kaggle public (mean) | Status |
|---|---|---|---|---|---|---|
| `v1_original.py` | BURST_K=1 ground-truth original | **180.0** @8750s/gym (2000/2000 cap, 105min — 2026-08-21) | **180.0** @8750s/gym (2000/2000 cap, 3.85h — 2026-08-21) | **180.0** | **88.740** | Calibration anchor — do not delete |
| `v6_adaptive.py` | Model-Adaptive Sizing, BURST_K=2, warm-up latency classification | 37.85 @900s/sandbox (stale env, historical) | not yet run | — | — (not submitted standalone) | Superseded by v7 |
| `v7_k1_live.py` | Ultra-Stable K=1 Model-Adaptive Sizing (extracted from `notebooks/ai-agent-security-v15.ipynb`, the current live submission) | not yet run | not yet run | — | pending (~106.2 projected) | **Current live submission** |

## Calibration constant (established 2026-08-21)

`v1_original.py` @ `--budget 8750`/`gym`, both models: **local_public_mean = 180.0** vs
**Kaggle = 88.740** → **local ≈ 2.03x Kaggle** for this attack under these conditions.

Both models independently hit the exact same 2000-candidate cap (2000/2000 unique cells,
36000 raw = 18/candidate × 2000, the K=1 ceiling). That's the key finding: **on this local
machine V1 saturates the 2000-candidate cap for both models within 8750s; on Kaggle it
evidently does not** (prior notes: GPT-OSS historically ~350-500 findings, Gemma "140+" —
both well under 2000). So the gap here isn't about candidate *design* (both environments
would score the max 180 once they fill 2000 slots) — it's that Kaggle's T4 hardware doesn't
generate 2000 valid candidates in 8750s for this attack, especially for GPT-OSS.

**Practical implication for judging new versions:** a local score near the 180 ceiling only
tells you the design *would* be optimal *if* Kaggle could also fill 2000 slots — it does not
predict the Kaggle score, because Kaggle's real bottleneck is generation throughput on
slower hardware, not candidate quality. To improve the *actual* Kaggle score, optimize for
candidates-generated-per-second (shorter prompts/turns, avoid slow multi-post bursts — see
Experiment 11's "Multi-Post Latency Trap") rather than for the local capped score. Until a
version's local run stays *below* the 2000 cap (so throughput differences actually show up
in the score), local numbers for different versions aren't very discriminating — prefer
comparing findings_count/time (candidates-per-second) between versions over the capped
normalized score.

Notes:
- **Kaggle public score is `mean(gemma_public, gpt_oss_public)`, not per-model.** Compare
  `local_public_mean` from a `--model both` run (or `./simulate_kaggle.sh`), not a
  single-model score, against the Kaggle number. See `../docs/guides/LOCAL_EVALUATION.md` §5.
- Older local scores marked "stale env" ran under `EnvSelection.SANDBOX` at 900s (pre-fix) —
  treat as historical only, not comparable to new `gym`/8750s runs.
- New runs auto-append to `../results/results.jsonl`. Add a row here whenever a new version
  gets extracted, evaluated, or submitted.
