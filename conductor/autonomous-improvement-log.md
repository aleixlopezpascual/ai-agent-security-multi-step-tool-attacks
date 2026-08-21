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

- Submission #1 (v1 revert, kernel v8): **SubmissionStatus.PENDING** — ~3h elapsed.
- Submission #2 (v10_no_split, kernel v9): **SubmissionStatus.PENDING** — ~2.5h elapsed.
- No local background runs in progress this cycle; used the wait time to analyze
  whether margin/timing tuning is a good next candidate (concluded: deprioritize, see
  above) and write the decision tree for once #1/#2 land (see above).
- **Do not submit a 3rd candidate until at least one of #1/#2 has a real score** —
  follow the decision tree above once that happens.

## Ideas not yet tried, and why margin-tuning is DEPRIORITIZED

Checked `results/results.jsonl`: at the real 8750s budget, v1_original.py hits the
2000-candidate cap comfortably on BOTH models locally (13868.9s wall for GPT-OSS, well
under the 17500s theoretical max) — meaning v1's CURRENT margins are already generous
enough locally. Margin/timing knobs (`MARGIN_S`, `REPLAY_SAFE_FRAC`,
`REPLAY_SAFE_SIZING`) are fundamentally different from content-level knobs (template
wording, `SPLIT_BY_LATENCY`) in one critical way: **they can't be reliably validated at
short local budgets.** A 47s margin is ~16% of a 300s test budget but ~0.5% of the real
8750s budget — short-budget timing behavior doesn't generalize. Properly testing a
margin change requires either an hours-long full-budget local run or a direct Kaggle
submission with NO cheap pre-validation. Given the downside of a bad margin estimate is
catastrophic (voids the WHOLE model row -> that row scores 0, not just "suboptimal"),
this is deprioritized below content-level ablations, which are safe to validate cheaply
and have no such cliff-edge failure mode.

## Decision tree for the next cron cycle once #1 and/or #2 land

- **If v10 (submission #2, SPLIT_BY_LATENCY=False) beats 88.740:** mandate achieved.
  Stop submitting, report to the user, keep it as the new live kernel (already is).
- **If v10 beats v1's reconfirmed score (#1) but not 88.740 itself:** the ablation
  direction (simplify) is validated as an improvement lever. Next candidate: dig one
  layer deeper into what ELSE can be simplified/removed. Do NOT test `SLOW_MULTIPOST_N`
  or other options gated behind `SPLIT_BY_LATENCY=True` -- those are moot if the split
  mechanism itself is a net negative.
- **If v10 underperforms v1:** the split-by-latency/Harmony-framing mechanism has real
  value after all (contradicts today's local GPT-OSS smoke signal -- local ≠ Kaggle
  hardware, revisit that assumption). Next candidate: leave `SPLIT_BY_LATENCY=True` and
  look for a DIFFERENT ablation (e.g. test disabling `REPLAY_SAFE_SIZING` instead,
  accepting the higher validation cost/risk noted above, OR simply re-submit v1
  unchanged as a clean control and pause further structural changes pending user input).
- **If both #1 and #2 come back close to each other and below 88.740:** possible grader
  drift since 2026-08-17, or real run-to-run variance (generation is stochastic, see
  docs/guides/LOCAL_EVALUATION.md) -- don't over-react to a single data point; consider
  a repeat submission of the SAME code to distinguish drift/noise from a real effect
  before concluding anything from one sample.
- In all cases: update this log + versions/README.md with the score, keep local
  smoke-test validation mandatory before any new submission, and don't spend more than
  1 submission slot per cron cycle without a fresh result to react to.

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
