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
| 2 | `versions/v10_no_split.py` | v9 | 2026-08-21 ~21:40 | Single-variable ablation: `SPLIT_BY_LATENCY=False`. Local evidence: GPT-OSS 2.61 raw/sec vs v1's 2.53 (+3%), Gemma parity (noise-level) | submitted, awaiting score | **pending** |

Submissions remaining today after #2: 3.

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

**Local Gemma-only test of v10 was uninformative by design** (53 vs 52 findings,
within noise) — `SPLIT_BY_LATENCY` only changes behavior on the model classified as
*slow* (GPT-OSS branch, using `FRAME_TEMPLATE`); Gemma converges to the same plain
`TEMPLATE` either way after the 8-candidate classification window. Started a GPT-OSS
local comparison instead (the model where this setting can actually matter), 300s
budget, `versions/v1_original.py` vs `versions/v10_no_split.py`. **Ran these
SEQUENTIALLY, not in parallel** — running two GGUF models simultaneously nearly
exhausted free memory (34GB total, ~24GB combined RSS, ~126MB free pages left) and
would have confounded the timing comparison via resource contention anyway.

- `local_eval_artifacts/v1_gptoss_300s.log` — **FINISHED**: 71 findings, raw 1278
  (71×18 exactly), 504.75s → **2.53 raw/sec** on GPT-OSS.
- `local_eval_artifacts/v10_gptoss_300s.log` — **FINISHED**: 76 findings, raw 1368
  (76×18 exactly), 523.6s → **2.61 raw/sec** on GPT-OSS (+3% vs v1). Modest but
  consistent-direction evidence that `SPLIT_BY_LATENCY=False` doesn't hurt and may
  help slightly on the model it targets. Not a huge effect, but real local signal was
  the bar for spending a submission slot, and this cleared it.
- **Submitted v10_no_split.py as submission #2** (kernel v9, `kaggle competitions
  submit`) — see Submission log table above.

## Status as of last update in this log (check `git log` / this file's mtime for freshness)

- Submission #1 (v1 revert, kernel v8): **SubmissionStatus.PENDING** — no score yet,
  ~2h20m elapsed since submit.
- Submission #2 (v10_no_split, kernel v9): **SubmissionStatus.PENDING** — just submitted.
- Local GPT-OSS comparison complete: v1=2.53 raw/sec, v10=2.61 raw/sec.
- Next actions for the cron continuation: (1) check both submissions for scores; (2)
  once EITHER lands, record it here and in versions/README.md; (3) if v10 (submission
  #2) beats 88.740, mandate achieved — stop submitting and report; if v10 doesn't beat
  it but beats v1's reconfirmed score, that's still useful signal for the next
  candidate; if neither beats 88.740, move to "ideas not yet tried" below with 3
  submission slots remaining today; (4) don't submit a 3rd candidate until at least
  one of #1/#2 has landed, to avoid submitting blind without fresh information.

## Ideas not yet tried (for the cron to consider if v10 doesn't pan out)

- Simply re-submitting v1_original.py again to check for run-to-run stochastic
  variance in the REAL Kaggle score (generation is non-deterministic — see
  docs/guides/LOCAL_EVALUATION.md) — informative but costs a slot for no design change.
- Loosening v1's own conservative safety margins slightly (MARGIN_S, REPLAY_SAFE_FRAC,
  FILL_BUDGET_FRAC) to reclaim a bit more fill capacity within budget, IF local
  evidence suggests margin is being left on the table without risking the replay-wall
  timeout that voids a whole model row.
  - Only pursue this AFTER checking local logs for how much margin is actually unused
    (e.g. wall_time_s vs the nominal 2x budget) — don't tune blind.
- Testing on the ACTUAL competition deadline pressure (2026-08-25) — don't let
  experimentation run past leaving enough days for a final confirmed-good submission.

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
