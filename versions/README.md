# Attack Version Catalog

Each file here is a standalone `class AttackAlgorithm` runnable with
`evaluate_local.py --attack versions/<file>.py` (see `../docs/guides/VERSIONING_WORKFLOW.md`).
Kaggle scores below are the recorded public-leaderboard results from `docs/reports/EXPERIMENTS.md`.

| File | Description | Local (Gemma) | Local (GPT-OSS) | Local mean | Kaggle public (mean) | Status |
|---|---|---|---|---|---|---|
| `v1_original.py` | BURST_K=1 ground-truth original | **180.0** @8750s/gym (2000/2000 cap, 105min — 2026-08-21) | **180.0** @8750s/gym (2000/2000 cap, 3.85h — 2026-08-21) | **180.0** | **88.740** | Calibration anchor — do not delete |
| `v6_adaptive.py` | Model-Adaptive Sizing, BURST_K=2, warm-up latency classification | 37.85 @900s/sandbox (stale env, historical) | not yet run | — | — (not submitted standalone) | Superseded by v7 |
| `v7_k1_live.py` | Ultra-Stable K=1 Model-Adaptive Sizing (extracted from `notebooks/ai-agent-security-v15.ipynb`, the current live submission) | not yet run | not yet run | — | pending (~106.2 projected) | **Current live submission** |
| `v8_multiturn.py` | EXPERIMENTAL: 2-turn chain, each turn an independent `http.post` EXFILTRATION to a unique URL (same candidate/env-session, testing whether splitting posts across turns avoids the single-turn "Multi-Post Latency Trap") | 476-510 raw @120s smoke (14-15 findings) — see below | not yet run | — | not submitted | Hypothesis NOT confirmed — see note below |

### v8_multiturn.py result (2026-08-21, Gemma, 120s smoke, throughput comparison)

Head-to-head at the identical short budget (raw/sec is the fair metric since each
attack's own internal stopping logic decides how much of the budget it actually uses):

| Attack | Findings | Raw | Time (s) | Raw/sec |
|---|---|---|---|---|
| `v1_original.py` (K=1, single-turn) | 52 | 936 (52×18) | 170.5 | **5.49** |
| `v8_multiturn.py` (2-turn chain) | 15 | 510 (15×34) | 95.1 | **5.36** |
| `v8_multiturn.py` (+ early-exit on doomed chains) | 14 | 476 (14×34) | 95.2 | 5.00 |

**Verdict: roughly a wash, not a win.** Per-candidate raw is ~1.9x higher with 2 turns
(34 vs 18 — note: the +2 unique-cell bonus is per-*finding*, not per-turn, so it's
`N_TURNS×16 + 2`, not `N_TURNS×18` as the module's original docstring assumed before this
was verified empirically), but per-candidate time cost is also ~2x, netting out close to
even. Adding an early-exit for chains already doomed to fail their strict fire requirement
didn't help — fire rate per turn on Gemma is already near 100%, so there were no "doomed"
chains to short-circuit. This refutes (for this specific design, on Gemma) the hypothesis
that splitting posts across turns avoids the per-turn latency cost that hurt `BURST_K>=2`
single-turn stacking; two turns just cost roughly what two turns cost. Not yet tested on
GPT-OSS, where per-turn context-reprocessing cost could behave differently either way.

## Calibration constant (established 2026-08-21)

`v1_original.py` @ `--budget 8750`/`gym`, both models: **local_public_mean = 180.0** vs
**Kaggle = 88.740** → **local ≈ 2.03x Kaggle** for this attack under these conditions.

**What's confirmed (arithmetic, not a bug):** `180.0` is NOT the max possible score (max is
`1000`) — it's the deterministic ceiling of a K=1 (one `http.post`/candidate) strategy once
it produces >2000 valid, uniquely-celled candidates: `2000 × 18 raw/candidate = 36000 →
normalized 180`. Both models landing on the identical number is mechanical, not a
coincidence or evidence of a bug — it's what happens whenever a run's valid-candidate count
exceeds the cap with a uniform per-candidate value (16 severity-5 + 2 unique-cell = 18,
every time, for every candidate that validates).

**What's genuinely uncertain:** *why* the Kaggle mean (`88.740`) is lower. The obvious guess
is that Kaggle's slower T4 hardware doesn't generate 2000 valid candidates per model within
8750s, so the same code scores less there. This is plausible but **not verified** — we have
no real per-model Kaggle candidate counts. Numbers like "GPT-OSS ~350" or "Gemma 140+" that
appear in `docs/reports/EXPERIMENTS.md` are **self-imposed candidate caps a prior session's
attack code was configured to target** (based on guesses from an earlier broken local run),
not observed Kaggle telemetry — do not treat them as ground truth about Kaggle's real
throughput.

**Practical implication for judging new versions either way:** once a local run hits the
2000 cap (as this one did on both models), its absolute score stops discriminating between
versions — anything that overflows the cap scores the same 180. Prefer comparing
candidates-generated-per-second (`findings_count / evaluation_time_s`) between versions,
since that's the metric more likely to matter if the real Kaggle bottleneck is throughput.

Notes:
- **Kaggle public score is `mean(gemma_public, gpt_oss_public)`, not per-model.** Compare
  `local_public_mean` from a `--model both` run (or `./simulate_kaggle.sh`), not a
  single-model score, against the Kaggle number. See `../docs/guides/LOCAL_EVALUATION.md` §5.
- Older local scores marked "stale env" ran under `EnvSelection.SANDBOX` at 900s (pre-fix) —
  treat as historical only, not comparable to new `gym`/8750s runs.
- New runs auto-append to `../results/results.jsonl`. Add a row here whenever a new version
  gets extracted, evaluated, or submitted.
