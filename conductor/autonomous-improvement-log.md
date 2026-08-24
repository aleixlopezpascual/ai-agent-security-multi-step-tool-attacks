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
| 1 | `versions/v1_original.py` (unchanged) | v8 | 2026-08-21 ~21:15 | Revert live kernel from V7 (45.0) back to proven V1 design | **COMPLETE** | **81.225** |
| 2 | `versions/v10_no_split.py` | v9 | 2026-08-21 ~21:40 | Single-variable ablation: `SPLIT_BY_LATENCY=False`. Local evidence: GPT-OSS 2.61 raw/sec vs v1's 2.53 (+3%), Gemma parity (noise-level) | **COMPLETE** | **58.545** |
| 3 | `versions/v8b_multiturn3.py` | v10 | 2026-08-21 ~22:10 | Uniform 3-turn EXFILTRATION chain (no per-model branching). Local GPT-OSS peak of N-sweep: 3.21 raw/sec vs v1's 2.53 (+27%), Gemma neutral | **COMPLETE** | **58.750 -- REGRESSION** |

Submissions remaining today after #3: 2 (quota did NOT reset with the calendar date — see cycle update above).

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

- Submission #1 (v1 revert, kernel v8): **SubmissionStatus.PENDING** — ~5h elapsed.
- Submission #2 (v10_no_split, kernel v9): **SubmissionStatus.PENDING** — ~4.5h elapsed.
- Still no score on either. Competition rules allow up to 15h per run, and deadline
  (2026-08-25) proximity likely means GPU queue contention across all competitors —
  this long a wait isn't necessarily abnormal, no evidence of an error/stuck state.
  Nothing new to act on this cycle; not forcing a 3rd submission without fresh data.
- **Do not submit a 3rd candidate until at least one of #1/#2 has a real score** —
  follow the decision tree above once that happens. If either is STILL pending after
  ~10-12h total (i.e. a few more cron cycles from now), that would be worth flagging
  as unusual and re-checking `kaggle kernels status` for the underlying kernel for any
  error state, rather than assuming it's just queue delay indefinitely.

**Cycle update (+1):** still both PENDING, no change. `kaggle kernels status` for
`aleixlopez/ai-agent-security-v15` shows COMPLETE, but that only reflects the last
push's cheap dev-mode run (kernel version 9), not the real competition-rerun grading
job triggered by `kaggle competitions submit` — no evidence of an error/stuck state,
just still queued/running. No local runs in progress. No action taken this cycle.

**Cycle update (+2):** still both PENDING, no change on Kaggle. Used the wait
productively: `v8_multiturn.py`/`v9_confused_deputy.py` were only ever tested on
Gemma (both underperformed plain K=1 there — see earlier sections). GPT-OSS has a
very different cost structure (long chain-of-thought reasoning per turn), so the
Gemma-only conclusion may not transfer — worth checking before ruling these ideas out
entirely, and it costs no submission slot. Launched
`versions/v9_confused_deputy.py` on GPT-OSS, 300s budget, PID 83257
(`local_eval_artifacts/v9_gptoss_300s.log`). Compare against v1's existing GPT-OSS
300s baseline (2.53 raw/sec) once done.

**Result: 24 findings, raw 624, 445.95s → 1.40 raw/sec.** Only ~55% of v1's 2.53
raw/sec baseline on GPT-OSS — the hypothesis that GPT-OSS's different (reasoning-
heavy) cost structure might favor the EXFILTRATION+CONFUSED_DEPUTY combo is
**refuted**; if anything the extra turn is proportionally about as costly there as on
Gemma (which was ~52% of baseline). Curiosity: raw/candidate averaged 26, not the
expected 22 (16 EXFIL + 4 DEPUTY + 2 cell bonus) — some candidates apparently
triggered an extra predicate beyond the two explicitly gated on. Didn't chase this
further (would need trace inspection) since it doesn't change the throughput verdict:
**v9_confused_deputy.py is now refuted on BOTH models and should not be pursued
further as a real candidate.** `versions/v8_multiturn.py` (2-turn pure exfil chain)
remains untested on GPT-OSS — lower priority than v9 was, since it was already only a
"wash" on Gemma rather than a clear loss, but could still be checked if time allows
and nothing else is more pressing.

**Cycle update (+3): recalibrating wait-time expectations.** Both submissions still
PENDING after many cron cycles. Re-derived expected grading duration from the
mechanics rather than assuming anomaly: each model gets a FRESH full budget for BOTH
generation (up to 8750s) AND replay (up to another 8750s) — up to ~4.86h/model, ~9.7h
for both models, even with zero queue delay. On Kaggle's slower T4 hardware (vs our
local Apple Silicon, where GPT-OSS alone took 3.85h at full budget), a many-hour real
grading time is EXPECTED, not unusual. No longer treating this wait as a signal
something's wrong; continuing to check each cycle without escalating.

Launched `versions/v8_multiturn.py` on GPT-OSS, 300s budget, PID 88367
(`local_eval_artifacts/v8_gptoss_300s.log`) — the last untested local
experiment from the decision tree.

**Result: 39 findings, raw 1326 (39×34 exactly), 441.4s → 3.00 raw/sec — a genuine
+19% over v1's GPT-OSS baseline (2.53 raw/sec).** This is a DIFFERENT outcome than
Gemma, where v8 was a wash/slight loss (5.36 vs 5.49, ~-2.4%). Plausible mechanism:
GPT-OSS's expensive per-turn reasoning overhead may be partially amortized when split
across two SEPARATE simple asks rather than reasoning once about a combined complex
ask — the opposite of a "cognitive overload" penalty, an "amortization" benefit,
specific to the slow/reasoning-heavy model.

**Important restraint: NOT submitting this yet, on purpose.** Two reasons: (1) my own
rule above says don't spend another slot until #1 or #2 has real feedback — this is
a genuinely different axis from the SPLIT_BY_LATENCY question, but I still have zero
real Kaggle confirmation that ANY local raw/sec signal predicts real score direction,
and burning 3 slots blind risks learning nothing if there's a systemic mismatch; (2)
the OBVIOUS next move (apply multi-turn ONLY on the classified-slow model, keep K=1 on
the classified-fast model) is EXACTLY the model-adaptive-branching pattern that
regressed hard in V6/V7 (46.955, 45.000) -- do NOT do that. If this idea is pursued,
it must be `v8_multiturn.py` applied UNIFORMLY to both models (no classification, no
branching) exactly as already built and tested -- letting the natural
mean(gemma_public, gpt_oss_public) capture GPT-OSS's gain while Gemma stays roughly
neutral, without reintroducing the risky per-model-decision mechanism.

**v8_multiturn.py is now the strongest untested-on-Kaggle candidate** — validated on
both models locally, dual-model-neutral-to-positive, no model-classification risk.
Queue this for submission once #1 or #2 lands (see updated decision tree below).

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
- **New option (added after v8's GPT-OSS result, see above): once #1 or #2 lands,
  `versions/v8_multiturn.py` (UNIFORM, no per-model branching) is a strong candidate
  regardless of which branch above fires** — it's a genuinely different axis
  (candidate structure, not per-model classification) with dual-model local validation
  (Gemma: neutral/-2.4%, GPT-OSS: +19%). Consider it as the NEXT submission after
  whichever branch-specific candidate above is chosen, or in its place if none of the
  above branches yield a clear next idea.

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

## Cycle update (+4): both still PENDING (~8-9h). Deepening the v8 finding.

No change on Kaggle. Created `versions/v8b_multiturn3.py` (identical to
`v8_multiturn.py` except `N_TURNS=3` instead of 2) to check whether the GPT-OSS
amortization benefit continues scaling with a 3rd turn or peaks/reverses at 2 —
informs which N to eventually submit, purely local/no Kaggle risk. Launched on
GPT-OSS, 300s budget, PID 99230 (`local_eval_artifacts/v8b_gptoss_300s.log`).

**Result: 24 findings, raw 1200 (24×50 exactly), 374.1s → 3.21 raw/sec.** The trend
CONTINUES improving: N=1 (v1) = 2.53, N=2 (v8) = 3.00 (+19%), N=3 (v8b) = 3.21 (+27%
vs N=1, +7% vs N=2 — diminishing marginal gain but still positive). Mapping the curve
further: created `versions/v8c_multiturn4.py` (N_TURNS=4), launched on GPT-OSS 300s,
PID 2954 (`local_eval_artifacts/v8c_gptoss_300s.log`), to see if it keeps improving,
plateaus, or reverses.

**Result: 14 findings, raw 924 (14×66 exactly), 299.4s → 3.09 raw/sec — slightly
BELOW N=3's 3.21.** Full GPT-OSS amortization curve now mapped (300s budget):

| N_TURNS | raw/sec | vs N=1 |
|---|---|---|
| 1 (v1_original.py) | 2.53 | baseline |
| 2 (v8_multiturn.py) | 3.00 | +19% |
| 3 (v8b_multiturn3.py) | 3.21 | +27% |
| 4 (v8c_multiturn4.py) | 3.09 | +22% (down from N=3) |

**Caveat on N=4's data quality:** its `evaluation_time_s` (299.4s) landed almost
exactly at the 300s budget itself (unlike N=1-3, which all finished comfortably under
budget via their own internal stopping logic) and its kept-candidate sample is much
smaller (14 vs 24 for N=2/N=3) — plausibly because each 4-turn chain's fill attempt
takes long enough that fewer full attempts fit before the fill's own wall-clock
deadline. Smaller sample = more variance, so treat the N=4 dip as suggestive, not
conclusive, that the curve peaks and reverses right at N=3 rather than being a firm
result. **Working conclusion: N=3 (`v8b_multiturn3.py`) is the leading local
candidate for GPT-OSS improvement** — clearest peak, largest same-size sample (24,
matching N=2's 24) as N=2's, real informative comparison. Stopping the N-sweep here;
diminishing returns from further local mapping without any real Kaggle feedback yet
to calibrate against. Note: `v8_multiturn.py`/`v8b`/`v8c` never used
`SPLIT_BY_LATENCY`/`FRAME_TEMPLATE` at all (standalone implementations, plain
`TEMPLATE` for every turn) — so v8b_multiturn3.py already IS the "no per-model
branching + multi-turn" combination; no separate merge step needed.

## Cycle update (+5): both still PENDING (~10h). Confirmed no diagnostic visibility
into the real grading run's progress exists via the CLI.

Downloaded `kaggle kernels output` for the live kernel to check for any stuck/error
signal — it only returns the CHEAP DEV-MODE run's output (14.5s, mock all-zero
`submission.csv`, "Set GPU T4 x2, Internet Off, then Submit." message), confirming
this endpoint reflects the push's dev-run, not the actual competition-rerun grading
job triggered by `kaggle competitions submit`. There is no CLI-exposed way to see
intermediate progress of the real grading run — `SubmissionStatus.PENDING` is opaque
by design until it flips to COMPLETE. No error/stuck-state evidence found; ~10h is
within the 15h-per-run ceiling. Local research (multi-turn N-sweep, confused_deputy,
no_split ablation, all validated on both models) is now fairly exhaustive for the
ideas identified so far — no new local experiment queued this cycle. Waiting for
real feedback before the next action.

## Cycle update (+6): system date rolled to 2026-08-22, but Kaggle's day boundary
had NOT — submitted candidate #3, learned an important quota correction.

Environment date changed to 2026-08-22; assumed (incorrectly, see below) this meant
the daily submission quota had reset to a fresh 5. Given #1/#2 had been PENDING
12+ hours with zero information gained, and the competition deadline (2026-08-25) is
close enough that pure waiting has a real opportunity cost, decided this was the
right moment to submit the strongest locally-validated candidate rather than wait
indefinitely on stale information — this is a deliberate, reasoned decision per the
mandate ("continue until better score"), not a rash one.

Ran a quick Gemma sanity check on `versions/v8b_multiturn3.py` first (never tested
there before, only on GPT-OSS): 2 findings, raw 100 (2×50 exactly — math checks out),
22.07s. Small sample is an expected artifact of testing a 3-turn design at a short
local budget (same conservative-margin-at-short-budget caveat noted for timing knobs
earlier) — not a bug, no errors, structurally sound. Packaged, pushed as kernel v10,
verified round-trip, and submitted (submission #3, `55677868`).

**Correction: the daily quota did NOT reset.** `kaggle competitions submit` returned
"2 submissions remaining today" — meaning only 3 total have been used, not a fresh 5.
The new submission's OWN timestamp still reads `2026-08-21 22:10:04`, confirming
Kaggle's internal day boundary (likely UTC-based) had not actually rolled over yet,
regardless of what date this environment's clock shows. **Lesson for future cycles:
never assume the quota reset from the environment's date alone — trust only the
literal "N submissions remaining" text from the `submit` command's own response.**

**Current state: 3 submissions pending (#1, #2, #3), 2 slots left.** Given this, do
NOT submit again until at least one of the three lands — we have less runway than
previously assumed and should not risk using both remaining slots blind.

**Cycle update (+7):** all 3 still PENDING, no change. No local runs in progress.
Nothing new to act on; holding discipline, not submitting further.

**Cycle update (+8):** all 3 STILL PENDING, no change, spanning many cron cycles now
across the 08-21/08-22 boundary. This is a genuinely extended wait — likely at or
past the ~15h/run ceiling implied by the competition rules, though I don't have a
precise elapsed-time readout to state an exact number confidently. No error status,
no diagnostic signal available (confirmed no CLI visibility into the real grading
job in an earlier cycle). **Flagging clearly for the user's attention when they
return: 3 submissions have been pending unusually long; worth checking the Kaggle
web UI directly (may show more detail than the CLI, e.g. a specific error message or
queue position) if this is still unresolved.** Continuing to hold discipline — not
submitting a 4th blind candidate, no local experiments left that would add new
information without fresh Kaggle feedback to calibrate against. Local research is
exhausted for now (see prior cycles); this cycle's only action is documentation.

**Cycle update (+9):** all 3 still PENDING, no change. No local runs. Nothing new.

**Cycle update (+10):** all 3 still PENDING, no change. Tried checking the leaderboard directly (in case of API sync lag between submissions/leaderboard endpoints) — no new info, team not found on first page, submissions endpoint remains the authoritative source and says PENDING. No local runs. Nothing new to act on.

## Real scores landed (user returned, checked live) — CRITICAL findings

**Submission #1 (`v1_original.py`, byte-identical to the historical 88.740 code):
scored 81.225.** Confirms real run-to-run stochastic variance in the actual Kaggle
score for IDENTICAL code (~8.5% swing). 88.740 was a good roll, not a guaranteed
floor — treat "beat 88.740" as needing real margin, not a razor-thin win, since a
lucky/unlucky generation run could account for several points either way.

**Submission #2 (`v10_no_split.py`, `SPLIT_BY_LATENCY=False`): scored 58.545 — a
~28% DROP from v1's reconfirmed 81.225.** This REFUTES the local GPT-OSS smoke
signal (+3% raw/sec), which pointed the wrong direction. Per the decision tree
written before this landed: **the split-by-latency/Harmony-bypass-framing mechanism
has REAL value on the actual Kaggle grader that our short local budget tests could
not detect.** Do NOT remove `SPLIT_BY_LATENCY` again without a much stronger reason.

**Important methodological lesson:** local raw/sec at short budgets (120-300s) is
NOT a reliable predictor of real Kaggle score direction — v10 looked flat-to-slightly-
positive locally but was substantially worse for real. This raises real doubt about
whether `v8b_multiturn3.py`'s strong local signal (+27% on GPT-OSS) will hold up
either; treat its still-pending result with real uncertainty, not confidence, until
it lands. Going forward, weight actual submission feedback far more heavily than
local smoke signals when they conflict.

**Submission #3 (`v8b_multiturn3.py`) still PENDING** — this is our best remaining
hope to beat 88.740 from the current batch. **Current best real, confirmed score
remains 88.740** (2026-08-17, not yet beaten by anything reconfirmed or tested since).

**1 submission slot left today** (confirmed via the last `submit` response text, not
assumed from date). Do not spend it until v8b's result is known — if v8b also
underperforms, the safest next move is very likely simply re-submitting
`v1_original.py` again to get a second real data point on its true variance range
(is 81-89 the real band, or was 81.225 itself an unlucky draw?), rather than
introducing more untested structural changes, given local smoke signals have now
proven unreliable for at least one real case.

## CORRECTION (user pushback, verified via `kaggle forums topics show`): score differences are NOT primarily "stochastic sampling" — real, documented evaluator changes are the better explanation

User rightly pushed back on "stochastic generation" as the explanation for 88.740 -> 81.225
(identical code) and v10's 58.545. Checked the competition's actual discussion forum via
`kaggle forums topics list`/`show` (CLI reads raw content directly, bypassing search-engine
indexing gaps and JS-rendering issues that blocked WebFetch). Found two organizer threads:

**Topic 712642 (2026-06-23), "Evaluator update and FAQ":** confirmed 9000s/phase budget,
raised the GLOBAL job ceiling to 15h, fixed secret-exfiltration scoring to use authoritative
replay traces + reversible-encoding detection. Explicitly: "If replay exceeds its budget,
the submission fails without a score" (at that time).

**Topic 733058 (2026-08-05), "[IMPORTANT] Upcoming Evaluation Updates and Leaderboard
Refresh"** — the important one:
- Organizers found "some Gemma tool calls were parsed" incorrectly: "Gemma wrapped
  subsequent tool-call responses in {}, which prevented them from being parsed correctly."
- Changed replay-timeout behavior: "Public and private replays will now preserve the score
  accumulated before a timeout instead of returning 0.0" (previously all-or-nothing).
- Because of these changes, **the organizers INVALIDATED THE ENTIRE LEADERBOARD**: "results
  from the previous and updated evaluation setups are not directly comparable... we will
  invalidate the current leaderboard."
- With ~68,000 submissions, a full rerun was infeasible; offered 2 free reruns/team
  (selection deadline 2026-08-07 9am PT, else auto-select the team's 2 highest-scoring).
- **Multiple participants report the Gemma tool-call parsing bug is STILL NOT FULLY FIXED**
  as late as 2026-08-18 (Renee: "Just dropping in again to say Gemma tool calls are still
  broken"; Syed Asad Ali, 2026-08-08, confirmed independently: asked Gemma for 2/3/4
  sequential http.post calls, "got exactly 1 pos[t]" back each time) — i.e. asking for
  MULTIPLE tool calls in a row can still silently drop all but the first.

**Corrected understanding:**
1. Both our 88.740 (2026-08-17) and 81.225 (2026-08-21) submissions post-date the Aug 5
   evaluator update and leaderboard reset — so they're NOT comparing across evaluator
   versions in the way "old vs new leaderboard" would be; the drop is real variance WITHIN
   the current evaluator regime, not a stale-baseline artifact for this specific pair.
2. BUT the mechanism for that real variance is much more concrete than generic "LLM
   sampling stochasticity": there is a DOCUMENTED, still-unresolved parsing bug that can
   silently drop tool calls, PLUS genuine model-sampling non-determinism (no fixed seed,
   confirmed in the vendored SDK), PLUS GPU/infra speed variance affecting how many
   candidates fit in the time budget, PLUS the new partial-credit-on-timeout mechanic
   adding another source of run-to-run outcome variability. "Stochastic" undersold this —
   it's a real, reported, partially-understood bug interacting with inherent non-determinism,
   not pure token-sampling noise.
3. **Confound for our own experiments:** the multi-tool-call parsing bug specifically affects
   designs asking Gemma for MULTIPLE sequential tool calls in a row. Our K=1 designs
   (`v1_original.py`, `v10_no_split.py`) and multi-TURN designs (`v8_multiturn.py` family —
   separate `env.interact()` calls, each asking for exactly ONE call) should be unaffected,
   since each turn's post is the FIRST tool call of that turn, not a "subsequent" one. This
   makes v8b_multiturn3.py's still-pending result MORE trustworthy on this specific axis than
   it would be for a BURST_K>1-style single-message multi-post design (which WOULD hit this
   bug directly — consistent with why V3/V6/V7's BURST_K>1 approaches regressed).
4. v10's 58.545 vs v1's 81.225 comparison could still be partly confounded by this bug/
   variance rather than being a completely clean causal read on SPLIT_BY_LATENCY alone —
   worth keeping appropriate uncertainty about the magnitude of that specific effect, even
   though the DIRECTION (don't remove SPLIT_BY_LATENCY) is still the safer conclusion given
   it's the only evidence we have.

Sources: [Evaluator update and FAQ](https://www.kaggle.com/competitions/ai-agent-security-multi-step-tool-attacks/discussion/712642), [Upcoming Evaluation Updates and Leaderboard Refresh](https://www.kaggle.com/competitions/ai-agent-security-multi-step-tool-attacks/discussion/733058), [Evaluator update planned for Monday](https://www.kaggle.com/competitions/ai-agent-security-multi-step-tool-attacks/discussion/710234) — all read directly via `kaggle forums topics show <id>`.

## Submission #3 confirmed: 58.750 — REGRESSION, 6th in a row

`v8b_multiturn3.py` (our strongest local candidate at +27% raw/sec on GPT-OSS) scored
**58.750** — a regression from v1's 81.225, same pattern as v10. **Local raw/sec has now
failed to predict real score direction twice in a row** (v10: +3% local -> -28% real; v8b:
+27% local -> regression again). Current best real, confirmed score remains **88.740**
(2026-08-17) / **81.225** (2026-08-21 re-run) — nothing from this session's 3 submissions
has beaten it. 1 submission slot remains today; holding it pending a better-reasoned
candidate rather than continuing to trust local raw/sec signals blindly.

## Deeper research since (parallel session, 2026-08-22) — source-verified guardrail limits

A separate session did further research, captured in memory (`optimal-guardrail-source-
verified`, `kaggle-community-intel-aug22`) and now folded into `versions/README.md`:

- **Source-proved (not hearsay): only `EXFILTRATION` and `CONFUSED_DEPUTY` are reachable at
  all** under the public `OptimalGuardrail` — `UNTRUSTED_TO_ACTION` and `DESTRUCTIVE_WRITE`
  are structurally blocked by the guardrail's taint-window check before their predicates can
  ever fire (window(2) ⊆ window(5), same trace/index — no timing trick escapes it). Stop
  chasing those two predicate types.
- Real leaderboard gap: top teams score ~124-138 vs our 88.740 anchor. Since our K=1 ceiling
  (18 raw/candidate) and the 2-predicate limit are both confirmed, top teams are winning via
  either higher throughput or a stacking approach we haven't found — not yet identified.
- No live private-guardrail feedback exists (candidates replay blind against it) — portfolio
  diversification is the only lever against private-guardrail risk.
- Unconfirmed (forum thread #736246, flagged not verified): the Gemma tool-call bug may be
  worse than documented — predicate outcomes possibly flipping entirely run-to-run even under
  nominally identical settings, not just "drops subsequent calls." If true, this could help
  explain why local signals keep failing to predict real outcomes.
- Process suggestion worth adopting: hash-track each submitted `attack.py`; only count a "win"
  after a REPEAT run beats the prior anchor, given the documented 88.740->81.225 variance.

**Where this leaves us:** 6 consecutive real-Kaggle regressions for anything beyond plain
K=1 V1. The two reachable predicates (EXFIL, CONFUSED_DEPUTY) and their obvious combination
have already been tried and refuted. The most promising unexplored direction per the
leaderboard-gap analysis is throughput (why do top teams get so much higher volume?), not
new predicate combinations — worth focused investigation before spending the last submission
slot today.

## Submission #4: v11_multiturn_harmony.py — combines multi-turn WITH the Harmony bypass

Built to resolve the confound identified in v8b's regression: the entire v8/v8b/v8c
multi-turn family was a from-scratch reimplementation that never included
SPLIT_BY_LATENCY/FRAME_TEMPLATE — the same mechanism v10 independently proved worth
~28%. So v8b's real-world loss (58.750) couldn't distinguish "multi-turn hurts" from
"multi-turn loses the same ~28% v10 lost, on top of whatever multi-turn itself does."

`v11_multiturn_harmony.py` starts from v1_original.py's EXACT proven code (fill loop,
adaptive margin, REPLAY_SAFE_SIZING, SPLIT_BY_LATENCY/FRAME_TEMPLATE all intact) and
changes only the exfil structure to a 3-turn chain, using whichever template the
classifier already chose for each turn. Verified before submitting:
- `N_TURNS=1` config produces byte-identical candidates to v1_original.py (confirmed
  programmatically) -- the refactor is provably safe for the baseline case.
- Smoke-tested on both models: Gemma 150 raw/3 findings (3x50 exactly, 120s), GPT-OSS
  1250 raw/25 findings (25x50 exactly, 300s, ~3.24 raw/sec) -- no errors, math checks
  out exactly on both. This validates CORRECTNESS only, not a real-score prediction,
  given local signals have failed twice already.

Packaged, pushed as kernel v11, submitted (submission 55694099, PENDING).
**Quota correction: "4 submissions remaining" after this one** -- Kaggle's own day
boundary rolled over since yesterday's submissions, giving more runway than the
"2 remaining" tracked at the end of the previous session. Confirms: always read the
literal remaining-count text, never assume from the environment's date.

This is now the most carefully-reasoned candidate of the session -- if it also
regresses, that's strong evidence multi-turn chaining itself (not the missing Harmony
bypass) is the real problem, and the multi-turn line of inquiry should be closed. If
it beats v10/v8b but still not 88.740, that confirms the confound was real and
points toward further Harmony-bypass-preserving refinements. If it beats 88.740,
mandate achieved.

## Submission #4 confirmed (2026-08-23): 75.875 — confound resolved, multi-turn closed

Both hypotheses cleanly confirmed:
1. **Confound was real**: v11 (3-turn + Harmony bypass) = 75.875, recovering ~17 points
   over v10/v8b's 58.5-58.7 (both missing the Harmony bypass). Confirms
   SPLIT_BY_LATENCY/FRAME_TEMPLATE is the dominant lever, worth ~28% on its own,
   independent of turn count.
2. **Multi-turn chaining is a genuine, smaller net negative** even properly combined
   (75.875 vs v1's 81.225, -6.6%) — not just an artifact of the missing Harmony bypass.
   **Closing the multi-turn line of inquiry** — don't build more N-variants expecting a
   different result once combined with the bypass; the mechanism itself costs real
   score, plausibly via compounding replay-risk (more turns = more chances for
   non-determinism to drop a call during the FRESH replay environment) rather than the
   BURST_K-specific Gemma parsing bug (shouldn't apply to separate turns/messages).

**7 consecutive regressions now.** Best real result remains plain `v1_original.py`
(K=1, single-turn, Harmony bypass intact) — 81.225/88.740, real variance band roughly
81-89 on 2 data points. No structural change found yet that beats it.

Quota: 4 submissions were available after v11's submit yesterday; check fresh count
before spending more.

## Research: what are top teams (124-138) doing? Real forum + public-kernel investigation

Pulled and diffed 6 of the highest-engagement public kernels for this competition
(up to 401 votes). Findings:
- One kernel (401 votes) is **byte-identical** to our own `v1_original.py`; two others
  are byte-identical to each other. The public ecosystem has converged on our exact
  same architecture, not a different mechanism.
- A creative-looking idea (378 votes: pairing `http.post` with `fs.delete
  path=secret.txt` for a claimed +8 raw via DESTRUCTIVE_WRITE) was checked against the
  actual guardrail source and is WRONG -- `secret.txt` contains "secret", so
  `_is_ultra_dangerous` denies that call unconditionally (`ok=False`), and
  `DESTRUCTIVE_WRITE` requires `ok is True`. Confirms our source-verified guardrail
  analysis; popular does not mean correct.
- **The real lead**: a June 2026 forum thread (55 votes, topic 711457) reported real
  Kaggle replay throughput of only ~600-800 candidates per 9000s budget -- far below
  our 2000-candidate local ceiling. A follow-up thread (topic 715259) says this got
  WORSE after a mid-competition update (~300), before the 2026-08-05 partial-credit
  fix we'd already found. Backward-computing from our own 81.225 real score implies
  ~900 candidates/model actually scored; reaching 124-138 (top real scores) implies
  ~1400-1500 -- a throughput gap, not a missing mechanism.
- **REPLAY_SAFE_SIZING was built (pre-Aug-5) specifically to avoid a catastrophic
  failure mode (replay overrun zeroing the WHOLE model row) that no longer exists**
  post the Aug-5 partial-credit-preserved-on-timeout fix. It's very likely now
  over-conservative, trading real throughput for protection against a neutralized risk.
- Found direct external validation: `probe-and-flood-strategy` (60 votes), the SAME
  architecture as ours, already runs `FILL_BUDGET_FRAC=0.99`/`REPLAY_SAFE_FRAC=0.99`
  (vs our 0.95/0.98) -- another team has already proven these tighter margins don't
  catastrophically fail.

## Submission #5: v12_tight_margins.py -- new axis, margin/timing not structure

Single-variable change: `FILL_BUDGET_FRAC` 0.95->0.99, `REPLAY_SAFE_FRAC` 0.98->0.99,
matching the externally-validated public kernel's values. Smoke-tested clean on both
models (Gemma 50x18=900 exactly, GPT-OSS 74x18=1332 exactly, no errors) -- correctness
only, since short local budgets can't validate timing changes (a 47s-scale margin is a
huge fraction of a 120-300s test but tiny at the real 8750-9000s budget).

Packaged, pushed as kernel v12, submitted (submission 55711937, PENDING). Quota: 4
remaining after this one (5 were available today -- quota DID reset since yesterday,
confirming it's tied to Kaggle's own day boundary as documented).

This is the first candidate targeting THROUGHPUT rather than candidate CONTENT/
structure -- a genuinely different axis from every prior attempt (all 7 of which
changed what candidates say, not how conservatively the fill loop stops). If this
doesn't move the needle, the more aggressive next step (REPLAY_SAFE_SIZING=False
entirely, reverting to the flat MARGIN_S-only stop) is the natural follow-up.

## Reconciled parallel-session work (2026-08-23)

Discovered a second parallel Claude session working in a sibling worktree
(`session/dashing-magpie-6gad`, sharing this project's persistent memory but a
separate git branch). It had done rigorous, valuable, UNCOMMITTED research:
- Proved `PROBE_HOPS` structurally dead under `REPLAY_SAFE_SIZING` (not just
  mis-tuned) — the replay-cost ledger, not fill wall-clock, binds achievable
  candidate count, and that ceiling is invariant to fill-loop probe speed. Built
  and smoke-tested `versions/v11_probe_hops.py` (regressed locally on both models,
  consistent with the analytical proof). Never submitted.
- Had ALREADY analyzed the exact `REPLAY_SAFE_FRAC` retuning I submitted as v12,
  and the user had agreed there to pause it as bad risk/reward (<1pt expected gain
  vs a catastrophic-void downside) — a decision I wasn't aware of when I proposed
  and submitted v12_tight_margins.py. Root cause of my error: `REPLAY_SAFE_FRAC`
  also controls `wall_deadline` (fill-phase overrun protection), a risk the Aug-5
  partial-credit fix does NOT cover (that fix only applies to REPLAY-phase
  timeouts; attack.py-phase overruns still hard-fail per the organizers' own
  words). `FILL_BUDGET_FRAC`'s change was inert (dead code path under
  `REPLAY_SAFE_SIZING=True`) -- only `REPLAY_SAFE_FRAC` had real, risky effect.
- Its own notes, on observing my submission, reframed it fairly: their pause
  assumed the code's "voids the whole submission" comment is still accurate
  post-Aug-5 -- itself unverified. My submission is a legitimate live test of
  that open question, not simply an ignored warning.
- Corrected `docs/reports/EXPERIMENTS.md`'s stale "PENDING/projected" claims with
  real confirmed scores (Experiments 7, 8, 12) and current status.

Merged into this branch: `docs/reports/EXPERIMENTS.md` (clean apply, no conflict),
`versions/v11_probe_hops.py` (new file), and a `versions/README.md` entry for it,
plus an explicit self-correction note on the v12_tight_margins entry documenting
this exact coordination gap so it isn't repeated. **Lesson for future cycles:
before proposing/submitting a throughput/margin-tuning lever, check whether a
parallel session has already analyzed and decided on it** -- this is a real risk
specific to multi-worktree/multi-session work on the same shared memory.

v12_tight_margins.py (submission 55711937) still PENDING.

## v13_same_turn_deputy.py — parallel work while v12 pends, closes stacking permanently

While v12_tight_margins.py (submission 55711937) remained PENDING, tested the one gap left
open by prior CONFUSED_DEPUTY research: `v9_confused_deputy.py` used 2 SEPARATE
`env.interact()` turns; the "same-turn" variant (both tool calls in ONE message, using
v1's already-unused `max_tool_hops=8` headroom) was flagged as "deprioritized, likely hits
the Gemma parsing bug" but never actually built or tested.

Built `versions/v13_same_turn_deputy.py`, smoke-tested head-to-head against v1_original.py
at 180s on both models. **Result: regresses badly on BOTH models, worse than even v9.**
Gemma: 2.68 raw/sec vs v1's 5.60 (-52%). GPT-OSS: 0.26 raw/sec vs ~4.62 (-94%,
catastrophic). Per-candidate raw was actually 26 (Gemma called email.send TWICE, once per
recipient) -- the value hypothesis was right, but latency killed it: planning + emitting 2
tool calls in one turn costs far more generation time than the extra raw recovers. Same
Multi-Tool Latency Trap pattern as every BURST_K>1 variant, just via a second predicate
type. **EXFIL+CONFUSED_DEPUTY stacking is now closed in BOTH forms (2-turn and same-turn),
permanently.** No submission made -- local result was decisive enough not to warrant one,
per this candidate's own docstring policy (research-only, requires explicit approval).

Checked submission #5 (v12_tight_margins) again: still PENDING. No new local experiments
queued this cycle -- the remaining unexplored options (BURST_K root-cause re-examination,
first-principles guardrail review) need more thought before building anything, not more
throughput-lever guessing.

## v14_slow_multipost -- convergent idea with parallel session, closes last "beat 18 raw" avenue

Independently proposed activating v1_original.py's own dormant `SLOW_MULTIPOST_N`/
`_forge_plan_msg` mechanism (Harmony-forged multi-post for the classified-slow row) --
this exact idea, at the exact same N=4 value, was found ALSO independently underway in
the parallel session (`versions/v14_slow_multipost_test.py`, running concurrently).
Avoided duplicating GPU-heavy work: watched their process rather than racing a competing
local test (two prior concurrent attempts crashed with `llama_decode returned -3` --
confirmed via a control run of unmodified v1_original.py, which crashed identically,
proving it was GPU/Metal resource contention from the two simultaneous processes, not a
bug in either file).

**Result (their completed run): 1332 raw / 74 findings = exactly 18.0 raw/candidate --
IDENTICAL to plain K=1, zero uplift.** The base file's old docstring claim ("4.0 firing
posts/candidate at N=4") does not hold under the corrected gym-env harness with genuine
independent replay -- same "cold independent replay" compounding-failure mechanism that
already closed multi-turn and EXFIL+CONFUSED_DEPUTY stacking. **This closes the last
untested "exceed 18 raw/candidate" avenue** -- every mechanism for packing more value
into one candidate slot (BURST_K, multi-turn, predicate stacking, forged multi-post) is
now refuted or closed. K=1 @ 18 raw/candidate is a hard ceiling; the only remaining
lever for beating v1_original.py is throughput/margin tuning (v12, still pending) or a
genuinely new mechanism not yet identified. No submission made -- decisive local result.

Submission #5 (v12_tight_margins) still PENDING.

## CORRECTION (2026-08-23, later cycle): the v14 "closed, zero uplift" conclusion above was CONFOUNDED

The "1332 raw / 74 findings = 18.0 raw/candidate, zero uplift" result above was a **silent
no-op control run, not a genuine null result**. Root cause (found and documented by the
parallel session, `slow-multipost-n-first-positive-lever` memory): `SPLIT_THRESHOLD_S=12.0`
was calibrated from REAL Kaggle 2xT4 timings (real GPT-OSS ~20.4s/candidate, real Gemma
~8.5s/candidate). On this local Mac GGUF setup, GPT-OSS's actual local latency is only
~3.5s/candidate -- well under 12.0s -- so `split_on` NEVER fires locally at the default
threshold, and even the already-proven-valuable `FRAME_TEMPLATE` bypass silently no-ops in
any naive local smoke test at default settings. The first v14 test never actually exercised
`_forge_plan_msg` at all.

**Re-tested correctly**: forced `SPLIT_THRESHOLD_S=0.5` (LOCAL-OBSERVABILITY-ONLY change,
guarantees the slow branch fires on this hardware) in `versions/v15_forced_split_control.py`
(N=1, control) and `versions/v14_slow_multipost_test.py` (N=4, test), 300s GPT-OSS runs:

| run | variant | kept findings | raw | raw/sec |
|---|---|---|---|---|
| 1st (parallel session) | v15 control | 194 | 3492 | 6.60 |
| 1st (parallel session) | v14 test (N=4) | 60 | 3576 | 6.85 (+3.8%) |
| 2nd (this session, repeat) | v15 control | 185 | 3330 | 6.33 |
| 2nd (this session, repeat) | v14 test (N=4) | 60 | 3576 | 6.85 (byte-identical to 1st run) |

**This reproduces cleanly**: v14/N=4 landed at the exact same raw/candidate (59.6) and
raw/sec (6.85) on two fully independent runs, while the N=1 control varied 6.60→6.33 (the
actual noise source). Combined delta vs the control's mean (6.465) is **+5.9%**, not the
single-run +3.8% first estimated -- and it's the **first structural change all session to
come back net POSITIVE on a repeat run**, not just less-negative (every prior gamble --
BURST_K, PROBE_HOPS, multi-turn, CONFUSED_DEPUTY 2-turn and same-turn -- regressed both
times it was tried). `_forge_plan_msg` is a token-level Harmony channel forge (near-100%
compliance per the code's own historical probe comment), categorically different from the
natural-language "call K times" instructions that failed for BURST_K/v9/v13.

**Real-Kaggle safety check before acting on this**: does the SAME threshold miscalibration
also affect real Kaggle (i.e. is real GPT-OSS ALSO misclassified as "fast")? No --
`SPLIT_THRESHOLD_S`'s own comment states real GPT-OSS latency is ~20.4s/candidate, already
well above the 12.0s threshold (correctly classified "slow" today, which is why
`v10_no_split`'s real 58.545 regression already proved `FRAME_TEMPLATE` has genuine live
value). Real Gemma (~8.5s) stays correctly under threshold too. The local hardware being
unusually fast is why local smoke tests need the threshold forced down to observe the
effect at all -- **this is a local-observability-only change; SPLIT_THRESHOLD_S must NOT be
changed for a real submission.** (I independently derived and then discarded a competing
hypothesis that the 12.0s threshold might ALSO misfire on real Kaggle, based on the
back-solved ~8.7s real per-candidate cost in `k1-ceiling-decision-2026-08-23` appearing to
match a "misclassified GPT-OSS" prediction almost exactly (8.58s) -- but that ~8.7s figure
is a blended/Gemma-ballpark calibration constant, not GPT-OSS-specific, and is superseded
by the code's own explicit ~20.4s GPT-OSS real-latency comment. Recorded here so this
plausible-but-wrong lead isn't re-investigated by a future cycle.)

## v16_slow_multipost_n4.py -- submitting the validated lever (single-variable: SLOW_MULTIPOST_N 1->4)

Built `versions/v16_slow_multipost_n4.py`: byte-identical to `v1_original.py` except
`SLOW_MULTIPOST_N = 1` -> `4` (confirmed via `diff`, only the docstring header and that one
line differ). `SPLIT_THRESHOLD_S` stays at the default 12.0 (untouched) -- on real Kaggle
this only activates the multi-post Harmony-forge on the row already correctly classified
"slow" (GPT-OSS), never Gemma. Does not touch `REPLAY_SAFE_FRAC`/`FILL_BUDGET_FRAC` (the
still-live-risk wall_deadline knob paused after the v12 analysis) -- this is a genuinely
independent, previously-never-activated variable on a real submission. Compiles clean,
packaged via `package_submission.py --sync-metadata`, dry-run emit smoke-tested (5
candidates, no crash).

Risk framing: this is the single most locally-validated (2 independent reproductions,
consistent direction, mechanistically distinct from every previously-refuted lever) and
lowest-incremental-risk candidate found this session. Proceeding to submit per the
standing mandate ("continue until a submission beats 88.740 by a real margin"), using one
of today's remaining submission slots.

**Submitted**: pushed as a new kernel `aleixlopez/v16-slow-multipost-n4` (kernel-metadata.json
auto-derives id from the attack filename; ran COMPLETE on first status check), submission
`55725150` at 2026-08-23 20:52:51, status PENDING. 3 submissions remaining today after this
one. `v12_tight_margins` (55711937, submitted 10:01:30 same day) is STILL PENDING ~11h later
-- unusually long even for this evaluator; keep checking both each cycle.

## Cron check-in (2026-08-23, no new information)

Both `v12_tight_margins` (55711937, ~12h pending) and `v16_slow_multipost_n4` (55725150,
~2h pending) remain `SubmissionStatus.PENDING` -- no scores yet. Checked shared memory dir:
no new files since my own `v16-slow-multipost-submitted-2026-08-23.md`/`MEMORY.md` writes
last cycle (mtimes unchanged, no parallel-session activity). No competing local
`evaluate_local.py` processes running. Nothing to reconcile or act on this cycle.

Per the standing rule ("if no new lever is clearly justified, it's fine to pause and report
status rather than force a low-confidence submission"): both pending submissions each
resolve a real open question (v12: does the Aug-5 partial-credit fix cover fill-phase
wall-clock overruns; v16: does the corrected SLOW_MULTIPOST_N finding transfer to real
Kaggle). Spending more quota on a new speculative lever before either resolves would waste
information value -- pausing here, not taking action, letting the cron continue.

## Cron check-in (2026-08-23, later, still no new information)

`v12_tight_margins` (55711937) now ~14h pending, `v16_slow_multipost_n4` (55725150) now
~4h pending -- both still `SubmissionStatus.PENDING`, unusually slow even for this
evaluator but not yet alarming. Memory dir unchanged since last check (no new files, no
new mtimes past my own prior writes). No competing local processes. Nothing to act on --
pausing again per the same reasoning as the prior check-in.

## Cron check-in (2026-08-23 23:41): still both PENDING, found a useful calibration datum

Third consecutive check-in with zero new memory files/results. Both `v12_tight_margins`
(now ~13h40m pending) and `v16_slow_multipost_n4` (~2h50m pending) unchanged. Verified via
`kaggle kernels status` that BOTH underlying kernels (`aleixlopez/ai-agent-security-v15`
for v12, `aleixlopez/v16-slow-multipost-n4` for v16) show `KernelWorkerStatus.COMPLETE` --
i.e. the cheap dev-mode kernel run finished fine; `SubmissionStatus.PENDING` reflects only
the separate, asynchronous full-budget replay+scoring pipeline, not a stuck/broken kernel.

Checked forums for an active outage: no current-competition complaints in the last few
days. Found one relevant historical reference (topic 712828, 2026-06-23, "[FIXED]
Submission Scoring Delays/Errors Due to GPU Capacity Constraints"): during a past T4
capacity incident, organizers cited a **15-hour maximum runtime limit**, after which a
submission that never started executing fails outright (not silently). This is 2 months
old and may not reflect current limits, but it's the only concrete number available, and
v12 (~13h40m) is now approaching that ballpark. Also worth noting: at 8750s/model x2
models plus replay, a fully normal (non-backlogged) run could easily take many hours on
its own, so long PENDING alone isn't necessarily a bad sign -- treating this as "watch
closely, don't panic" rather than "something is broken."

**Action for next cycle**: if v12 flips to a hard failure/error status (rather than
COMPLETE with a score) around the ~15h mark, that's a data point worth recording (possible
capacity-related failure, not necessarily a verdict on the REPLAY_SAFE_FRAC lever itself)
-- don't conflate a queue-capacity failure with a "the margin change caused an overrun"
result if it happens. No action taken this cycle; still pausing.

## Cron check-in (2026-08-23 23:57): still pending, nothing new

v12 ~13h56m pending (not yet at the ~15h watch-point), v16 ~3h pending. No new memory
files, no competing local processes. Pausing, no action.

## Cron check-in (2026-08-24 00:13): v12 now ~14h12m, still pending, nothing new

Approaching the ~15h historical watch-point noted last cycle. No new memory files, no
competing local processes. Pausing, no action -- will watch closely next cycle for either
a resolved score or a failure around the 15h mark.

## Correction: previous commit accidentally included a parallel-session file, mis-attributed

My previous commit's `git add -A` swept up `versions/v17_slow_multipost_n2.py` (mtime
2026-08-23 23:57), which I did NOT write -- this is the parallel session (sibling worktree
`session/dashing-magpie-6gad`) writing directly into this shared worktree, as previously
documented for v13/v14/v15. The commit message didn't mention it, which is misleading; not
rewriting the already-pushed commit (no force-push/history-rewrite without explicit
instruction), documenting the correction here instead.

**What the file claims vs what's actually verified**: its docstring says it was "submitted
BEFORE v16's real score is known (user explicitly chose to spend a slot on this now...)" --
but `kaggle competitions submissions` shows NO v17 entry, and no shared-memory file
documents this decision or user sign-off yet. Most likely this is an in-progress draft
written in anticipation of a submission that hasn't happened yet (or is about to), not
evidence of a completed action. **I have NOT submitted this file, altered it, or acted on
its claims** -- leaving it for the parallel session to handle via its own workflow, and
noting it here so my own future cycles don't mistake it for something I built or verified.
Will re-check the submissions list and memory dir next cycle for confirmation either way.

## Cron check-in (2026-08-24 00:35): v17/v18 confirmed real, new user directive found, quota nearly exhausted

Yesterday's v17 draft was in fact submitted (memory `v17-slow-multipost-n2-submitted.md`,
written by the parallel session): a genuine, direct user instruction was given --
*"yeah let's submit, we have 5 submissions per day which i want to exhaust every day to
have more possibilities of winning."* This changes the standing risk posture for the
DAILY QUOTA specifically: exhausting all 5 slots/day is now an explicit user goal, not
just "submit when evidence is strong." The parallel session acted on it: submitted
`v17_slow_multipost_n2` (55726389, SLOW_MULTIPOST_N=2) and `v18_slow_multipost_n3`
(55726522, SLOW_MULTIPOST_N=3), filling out the N=2/3/4 sweep alongside my own `v16`
(N=4, 55725150). `kaggle competitions submission-limits` confirms: **4/5 used today,
1 remaining.** All four of today's submissions (v12, v16, v17, v18) are still PENDING.

Also picked up two useful procedural findings from that memory: the correct submission
CLI form is `-k <owner/kernel-slug> -f submission.csv -v <kernel-version>` (bare `-f`
alone 400s), and `kaggle competitions submission-limits -c <slug>` is the authoritative
quota check (the daily boundary does not track local midnight -- confirmed).

**Decision on the last slot**: the parallel session's own documented plan is to wait for
v16/v17/v18 to resolve so the 5th slot is evidence-based (three real SLOW_MULTIPOST_N data
points instead of another guess) rather than spend it immediately. Deferring to that plan
-- both sessions draw from the SAME shared daily quota, so racing to spend the last slot
independently right now (before anything new has resolved to justify a choice) risks
wasting it on an uncoordinated guess. Not submitting anything this cycle. Continuing to
monitor v12 (~14h34m, past the informal ~15h historical watch-point territory now -- worth
watching very closely next cycle) and the three SLOW_MULTIPOST_N submissions.

## Cron check-in (2026-08-24 00:58): v12 RESOLVED -- 88.290, breaks the 6-for-6 regression streak; quota now fully exhausted

**v12_tight_margins (55711937) is COMPLETE: public score 88.290**, after ~12.5h pending --
the longest pending duration this session. This resolves the standing open question from
`k1-ceiling-decision-2026-08-23`: does the Aug-5 partial-credit-on-timeout fix also cover
the fill-phase `wall_deadline` overrun risk? **Answer: no catastrophic void occurred** --
`REPLAY_SAFE_FRAC`/`FILL_BUDGET_FRAC` 0.99/0.99 completed normally and scored within the
established 81.225-88.740 variance band (near the top), not a hard zero. This is the
**first structural change all session to NOT clearly regress** -- breaks the prior 6-for-6
regression pattern (V3, V6, V7, v10_no_split, v9, v8b all regressed 25-90%). Caveat: 88.290
is still below the 88.740 anchor and inside the ~8.5% run-to-run noise band from the two
identical-code V1 submissions, so this is "not dangerous, plausibly neutral-to-mildly-positive"
evidence, not a confirmed win -- do not treat REPLAY_SAFE_FRAC as fully validated, but the
catastrophic-downside framing that justified pausing this lever is now specifically refuted
for the 0.99 value tested.

**Quota fully exhausted today**: the parallel session used the 4th slot on `v18_slow_multipost_n3`
(55726522, N=3, PENDING) and the 5th/final slot on `v19_slow_multipost_n8` (55726763, N=8,
PENDING) -- per explicit user choice via AskUserQuestion to push the sweep past the
originally-tested range rather than wait. **5/5 submissions used today (v12, v16, v17, v18,
v19), 0 remaining** -- confirmed both via `submission-limits` and the submit command's own
"0 submissions remaining today" response. Full `SLOW_MULTIPOST_N` sweep now in flight:
N=2 (55726389), N=3 (55726522), N=4 (55725150), N=8 (55726763) -- ALL still PENDING as of
this writing, alongside the resolved v12.

**Decision this cycle**: nothing to submit (0 slots remain today regardless of any new
lever's merit). Updated `versions/README.md`'s submission history table and regression-
pattern note with the 88.290 result. Next cycle: check whether any of the four
SLOW_MULTIPOST_N submissions have resolved -- once they do, we'll have real N=2/3/4/8 data
points to inform tomorrow's plan (continue the sweep further, pick the best N and retest
for confirmation, or combine with the now-partially-validated REPLAY_SAFE_FRAC=0.99).

## Cron check-in (2026-08-24 01:13): no new results, quota confirmed 0/5 remaining today

v16/v17/v18/v19 (N=4/2/3/8) all still `SubmissionStatus.PENDING`. `submission-limits`
confirms "Submissions today: 5, Remaining today: 0" -- nothing can be submitted regardless
of any new lever's merit. No new memory files since last cycle's own writes (k1-ceiling-
decision/MEMORY.md at 00:58 are mine). Nothing to act on; pausing, letting the cron
continue until either a sweep result resolves or tomorrow's quota resets.

## Deep dig on v12's 88.290 (user request: "dig about the results we got recently")

Re-examined the standing explanation for the 88.740/81.225 identical-code variance and
found a real gap: the documented Aug-5 Gemma parsing-bug fix explicitly does NOT apply to
K=1 designs (our own doc says so), but `v1_original.py` IS K=1 -- so that explanation
never actually accounted for V1's own variance. Traced a better-fitting mechanism instead:

- `REPLAY_SAFE_SIZING`'s fill loop (`versions/v1_original.py` ~L142-165) is
  latency-adaptive, not fixed-count -- it stops once the *measured* per-candidate replay
  cost ledger would exceed `REPLAY_SAFE_FRAC * replay_budget`. Identical code can
  therefore return a different-sized candidate set purely from real-time backend latency
  during that specific run.
- Forum research (topic 711457, `hiyodori411`, 2026-06-21) independently reports this
  competition's actual scoring backend GPU throughput doesn't match a standalone Kaggle
  T4 notebook's expected speed ("replaying just 600-800 findings consumes nearly the
  entire 9,000-second budget") -- consistent with shared/contended backend infrastructure,
  not a code bug. Organizer FAQ (topic 712642) confirms separate 9,000s budgets per phase
  plus a 15h global ceiling, consistent with this being a real, variable, shared-resource
  system rather than a simple fixed-timing model.

**Conclusion, and what it means for v12**: v12_tight_margins' 88.290 is subject to this
SAME backend-load-driven fill-size variance as the 88.740/81.225 anchor runs, on top of
whatever real effect its `REPLAY_SAFE_FRAC` 0.99 change had. The predicted effect size for
that change (+0.4-0.9 points per the `k1-ceiling-decision` sizing estimate) is likely
smaller than this noise source -- which is consistent with 88.290 landing inconclusively
inside the variance band rather than clearly above or below it. This isn't evidence the
margin change did nothing; it's a limitation on how confidently ANY single submission
(including the in-flight N=2/3/4/8 sweep) can be read. Documented in full in
`versions/README.md` and a new shared memory entry
(`k1-variance-mechanism-backend-throughput-2026-08-24`) so the parallel session sees it
too before drawing strong conclusions from the sweep results once they resolve.

## Cron check-in (2026-08-24 01:40): no new results, quota still 0/5

v16/v17/v18/v19 (N=4/2/3/8) all still `SubmissionStatus.PENDING`. Quota confirmed 0/5
remaining today. No new memory files since last cycle's own writes. Nothing to act on;
pausing.

## Cron check-in (2026-08-24 01:57): no new results, quota still 0/5

Same state as last cycle. Pausing again.

## Cron check-in (2026-08-24 02:13): quota RESET (fresh 5/5), submitted v20_tighter_margins_0995

`submission-limits` shows Kaggle's daily quota reset: "Submissions today: 0, Remaining
today: 5" -- new day's clock rolled over. All four SLOW_MULTIPOST_N sweep submissions
(v16/v17/v18/v19) still PENDING, no new memory files from the parallel session.

**Decision**: rather than pause with a fresh, unused quota, or blindly extend the
still-unresolved SLOW_MULTIPOST_N sweep further, verified the exact fill-loop mechanics
first (`versions/v1_original.py` L376: `wall_deadline = run_start + replay_safe_frac *
budget` -- confirms `FILL_BUDGET_FRAC` is genuinely dead code under
`REPLAY_SAFE_SIZING=True`, only `REPLAY_SAFE_FRAC` matters). Built
`versions/v20_tighter_margins_0995.py` = `v12_tight_margins.py` (already proven safe at
88.290, no void) with exactly one further change: `REPLAY_SAFE_FRAC` 0.99 -> 0.995 --
directly answering the open follow-up flagged in `k1-ceiling-decision-2026-08-23`'s own
resolution note ("NOT evidence pushing the margin further is equally safe -- needs its
own test"). One small, bounded increment (halfway to the theoretical 1.0 ceiling, not
jumping straight there), not a blind guess.

Confirmed single-variable via `diff` (only docstring + the one value differ), compiled
clean, smoke-tested the emit path (5 candidates, no crash). Pushed as kernel
`aleixlopez/v20-tighter-margins-0995` (ran COMPLETE), submitted as **55728233**, PENDING.
4 submissions remaining today. Documented the noise-floor caveat
(`k1-variance-mechanism-backend-throughput-2026-08-24`) directly in the file's own
docstring so this isn't over-read as proof either way once it resolves.

## Cron check-in (2026-08-24 02:40): no new results

All five submissions today (v12 resolved 88.290; v16/v17/v18/v19/v20 all PENDING) --
unchanged since last cycle. Quota confirmed 1 used/4 remaining. No new memory files from
the parallel session. Nothing to act on; pausing.

## Cron check-in (2026-08-24 02:57): no new results

Same state as last cycle. Pausing again.

## Cron check-in (2026-08-24 03:13): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining). No new memory files. Pausing again.

## Cron check-in (2026-08-24 03:40): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining). No new memory files. Pausing again.

## Cron check-in (2026-08-24 03:57): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining). No new memory files. Pausing again.

## Cron check-in (2026-08-24 04:13): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~7.5h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 04:40): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~7.8h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 04:57): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~8h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 05:13): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~8.4h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 05:40): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~8.8h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 05:57): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~9h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 06:13): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~9.4h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 06:40): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~9.8h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 06:57): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~10.1h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 07:13): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~10.4h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 07:40): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~10.8h pending, approaching the historical ~15h
watch-point from earlier this session -- worth close attention over the next few cycles).
No new memory files. Pausing again.

## Cron check-in (2026-08-24 07:57): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~11.1h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 08:13): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~11.4h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 08:40): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~11.8h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 08:57): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~12.1h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 09:13): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~12.4h pending, closer to the ~15h historical
watch-point). No new memory files. Pausing again.

## Cron check-in (2026-08-24 09:40): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~12.8h pending). No new memory files. Pausing again.

## Cron check-in (2026-08-24 10:13): no new results

Same state as last cycle (v12 resolved 88.290; v16/v17/v18/v19/v20 all still PENDING,
quota 1 used/4 remaining; v16 now ~13.4h pending, getting close to the ~15h historical
watch-point -- worth close attention over the next couple cycles). No new memory files.
Pausing again.

## v16_slow_multipost_n4 RESOLVED (2026-08-24 10:40): 87.815 -- second consecutive non-regression

**v16 (55725150, SLOW_MULTIPOST_N=4) resolved at 87.815, COMPLETE**, after ~13.8h
pending. This is genuinely good news: 87.815 is within 1 point of the 88.740 anchor,
well above the 81.225 baseline-noise floor, and very close to v12's 88.290. **This is the
SECOND consecutive structural change to NOT regress** (after v12) -- the prior "6-for-6
regression" pattern is now broken twice in a row, not a one-off. It also confirms the
locally-repeated (+5.9% raw/sec, reproduced twice) SLOW_MULTIPOST_N finding transfers to
real Kaggle, unlike every earlier positive local signal this session (v10's +3%, v8b's
+27%) which both regressed for real. Updated `versions/README.md`'s submission history
table and pattern-update note with the full analysis and the mechanistic distinction
(Harmony-forge near-100%-compliance mechanisms transfer; natural-language multi-ask
compliance mechanisms don't).

v17/v18/v19 (N=2/3/8) still PENDING -- will further calibrate where the real optimum on
this axis sits. No new memory files from the parallel session yet on this result.

**Decision on today's remaining 4 slots**: rather than wait for the full sweep (unknown
timing, v16 alone took ~13.8h) or guess a new unrelated lever, the best-reasoned next step
is combining the TWO independently-real-confirmed-non-regressive axes:
`REPLAY_SAFE_FRAC=0.99` (v12, proven safe) + `SLOW_MULTIPOST_N=4` (v16, proven safe/positive).
Checked the fill-loop safety mechanism (`REPLAY_SAFE_SIZING`'s adaptive ledger uses
OBSERVED per-candidate latency, generic to whatever design produces it) -- no
mechanism-specific reason combining these should introduce a NEW risk beyond what each
already tests independently. Building `v21_combined_margins_multipost.py` next.

Built `versions/v21_combined_margins_multipost.py` = `v16_slow_multipost_n4.py` with
exactly one further change (`REPLAY_SAFE_FRAC` 0.98 -> 0.99, matching v12's proven-safe
value; confirmed via `diff` -- only docstring + that one value differ). Compiled clean,
smoke-tested the emit path (5 candidates, no crash), packaged, pushed as kernel
`aleixlopez/v21-combined-margins-multipost`. **This kernel push itself got stuck in
`KernelWorkerStatus.QUEUED` for several minutes** (unusual -- prior dev-mode pushes this
session completed in 1-3 status checks) -- consistent with the documented backend GPU
capacity variance (topic 712828), not an error in the code. Not forcing further polling
this cycle; the kernel version exists and will clear the queue on its own. **Not yet
submitted to the competition** (submission requires the kernel to reach COMPLETE first) --
next cycle should check `kaggle kernels status aleixlopez/v21-combined-margins-multipost`
and, once COMPLETE, run `kaggle competitions submit -k aleixlopez/v21-combined-margins-multipost
-f submission.csv -v 1 -m "..."` to actually use one of today's 4 remaining slots.

**Update**: the kernel cleared the queue shortly after (QUEUED -> RUNNING -> COMPLETE within
~1 more minute of polling) -- confirms it was transient backend capacity, not stuck.
Submitted as **55738097**, PENDING. 3 submissions remain today.

**Today's submission tally**: v12 (COMPLETE, 88.290), v16 (COMPLETE, 87.815), v17/v18/v19
(N=2/3/8 sweep, still PENDING), v20 (REPLAY_SAFE_FRAC=0.995, PENDING), v21 (combined
margins+multipost, PENDING). 2 used of today's fresh 5, 3 remaining -- pausing here rather
than forcing a 3rd guess before any of v17/v18/v19/v20/v21 resolve to inform the next one.

## Cron check-in (2026-08-24 10:57): no new results

v12/v16 remain resolved (88.290/87.815); v17/v18/v19/v20/v21 all still PENDING. Quota
2 used/3 remaining today. No new memory files from the parallel session. Pausing --
nothing new to act on until one of the in-flight submissions resolves.

## Cron check-in (2026-08-24 11:13): no new results

Same state as last cycle (v12/v16 resolved; v17/v18/v19/v20/v21 all still PENDING, quota
2 used/3 remaining today). No new memory files. Pausing again.

## Cron check-in (2026-08-24 11:40): no new results

Same state as last cycle (v12/v16 resolved; v17/v18/v19/v20/v21 all still PENDING, quota
2 used/3 remaining today). No new memory files. Pausing again.

## Cron check-in (2026-08-24 11:57): no new results

Same state as last cycle (v12/v16 resolved; v17/v18/v19/v20/v21 all still PENDING, quota
2 used/3 remaining today). No new memory files. Pausing again.

## v18 (N=3) and v19 (N=8) RESOLVED (2026-08-24 12:13): sweep shows an inverted-U peaking near N=4

**v18_slow_multipost_n3 (55726522): 86.620. v19_slow_multipost_n8 (55726763): 85.000.**
Combined with v16's 87.815 (N=4), the SLOW_MULTIPOST_N sweep now has three real data
points: N=3 (86.620) -> N=4 (87.815, peak) -> N=8 (85.000, drops off). Consistent with an
inverted-U shape, similar in shape (not mechanism) to the earlier GPT-OSS multi-turn
amortization curve (which peaked at N_TURNS=3 then reversed). **None of N=3/4/8
individually beats the 88.740 anchor** -- N=4 remains the best of the sweep, comfortably
inside the 81.225-88.740 variance band. `v17` (N=2) is the last unresolved sweep point --
needed to know if the true peak is at N=2, N=3, or N=4. Full table and analysis written
into `versions/README.md`.

**Decision this cycle**: no new memory files from the parallel session on this update yet.
Rather than spend one of today's 3 remaining slots on a further sweep refinement (e.g.
N=5/N=6 to pin down the peak more precisely) before the picture is complete, waiting for
`v17` (N=2, PENDING) and especially `v21_combined_margins_multipost` (N=4 +
`REPLAY_SAFE_FRAC=0.99`, PENDING) to resolve first -- v21 is the current best shot at
actually beating the anchor, since it stacks the sweep's best point with the separately
proven-safe margin change, and its result should inform whether stacking further (e.g. N=4
+ REPLAY_SAFE_FRAC=0.995) is worth a future slot. No new submission this cycle.

## v17 (N=2) RESOLVED (2026-08-24 12:40): 82.855 -- sweep now COMPLETE, confirms N=4 is the real peak

**v17_slow_multipost_n2 (55726389): 82.855.** This is the WORST of all four sweep points
-- barely above the 81.225 noise floor. Full sweep now resolved: N=2 (82.855) -> N=3
(86.620) -> N=4 (87.815, peak) -> N=8 (85.000). A clean inverted-U with the peak firmly
confirmed at N=4 -- N=2's poor result rules out "the true peak is actually below N=3",
so N=4 is genuinely the best-performing value tested, not a lucky outlier. Full updated
table and analysis written into `versions/README.md`.

**Decision this cycle**: still no new memory files from the parallel session on this.
`v21_combined_margins_multipost` (N=4 + `REPLAY_SAFE_FRAC=0.99`) remains the single most
promising in-flight candidate and is still PENDING -- not spending a new slot until it
resolves, since its result directly determines whether further stacking (N=4 +
REPLAY_SAFE_FRAC=0.995, or exploring N=5/N=6 around the confirmed peak) is worth pursuing.
3 submissions remain today; no new submission this cycle.

## Cron check-in (2026-08-24 12:57): no new results

Sweep complete and documented last cycle; v20/v21 still PENDING, quota 2 used/3 remaining
today. No new memory files. Pausing again.

## Cron check-in (2026-08-24 13:13): no new results

v20/v21 still PENDING, quota 2 used/3 remaining today. No new memory files. Pausing again.

## Cron check-in (2026-08-24 13:40): no new results

v20/v21 still PENDING, quota 2 used/3 remaining today. No new memory files. Pausing again.

## Cron check-in (2026-08-24 13:57): no new results

v20/v21 still PENDING, quota 2 used/3 remaining today. No new memory files. Pausing again.
