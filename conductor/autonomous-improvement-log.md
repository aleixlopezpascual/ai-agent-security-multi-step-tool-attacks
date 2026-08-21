# Autonomous Improvement Log (2026-08-21, unattended session)

Mandate from user: create a version that scores better than our current best on the
real Kaggle public leaderboard (currently confirmed **88.740**, from `v1_original.py`
submitted 2026-08-17). Continue submitting/iterating autonomously for hours until a
better public score is achieved.

## Ground truth discovered before starting (important — corrects prior docs)

- `kaggle competitions submissions` shows our REAL submission history. Best-ever real
  score: **88.740** (V1, BURST_K=1, plain, 2026-08-17). Every subsequent "improvement"
  scored LOWER: V3 (BURST_K=3) 52.055, unnamed 54.960/51.820, V6 (Model-Adaptive
  cap=1500/400) 46.955, **V7 (Model-Adaptive cap=1600/500) 45.000 — the CURRENTLY LIVE
  kernel before this session's revert**. `docs/reports/EXPERIMENTS.md`'s "V7 PENDING,
  projected ~106.2" was stale/wrong — it had already completed and scored far below
  baseline. Pattern: every structural addition (density stacking, per-model cap
  throttling) has made the real score WORSE, matching what today's local v8/v9
  experiments also found (multi-turn/additive-predicate ideas underperform plain K=1).
- Pulled the live kernel (`aleixlopez/ai-agent-security-v15`) directly via
  `kaggle kernels pull` and confirmed its attack code is byte-identical to our
  `versions/v7_k1_live.py` catalog copy — our catalog is accurate.

## Submission log

| # | Version pushed | Kernel ver | Submitted (UTC-ish) | Change | Status | Public score |
|---|---|---|---|---|---|---|
| 1 | `versions/v1_original.py` (unchanged) | v8 | 2026-08-21 ~21:15 | Revert live kernel from V7 (45.0) back to proven V1 design | submitted, awaiting score | **pending** |

Submissions remaining today after #1: 4.

## Process being used (fully CLI-automated, no UI needed)

```
.venv/bin/python package_submission.py --attack versions/<name>.py --notebook notebooks/ai-agent-security-v15.ipynb
kaggle kernels push -p .                                    # creates a new kernel version, runs it in cheap dev mode
kaggle kernels status aleixlopez/ai-agent-security-v15       # poll until COMPLETE
kaggle competitions submit -c ai-agent-security-multi-step-tool-attacks \
  -k aleixlopez/ai-agent-security-v15 -v <version> -f submission.csv -m "<message>"
kaggle competitions submissions -c ai-agent-security-multi-step-tool-attacks   # poll for score
```

## Next candidate being prepared while #1 is scored

`versions/v10_no_split.py`: `v1_original.py` with `SPLIT_BY_LATENCY=False` (the one
active, non-default-off complexity layer in the anchor file — everything else in v1
that's dormant/knobbed is at its documented "byte-identical to today's behavior"
default). Rationale: isolate whether the per-model latency-classification branching
itself helped or hurt the 88.740 result, since it was active in that run and we've
never tested it OFF. Lowest-risk, highest-information single-variable ablation
available, given the strong pattern that added complexity has hurt every time so far.

## Rules of engagement for this autonomous run

- Max 5 submissions/day (competition rule) — spend them on genuinely different,
  reasoned hypotheses, not blind retries.
- Every candidate must be validated to compile and pass a structural smoke check
  (`evaluate_local.py --attack ... --budget 120-300` or `--n_candidates` override)
  before spending a submission slot on it.
- Record every submission and score here and in `versions/README.md`, win or lose.
- Prefer the smallest, most reversible change over a new structural rewrite, given
  the consistent evidence that complexity has hurt every time on the real grader.
- Competition deadline: 2026-08-25 (per public competition page) — plenty of runway
  for a "some hours" session, but don't be wasteful.
