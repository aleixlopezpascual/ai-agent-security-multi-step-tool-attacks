# Local-Kaggle Alignment — Completion Record (corrected)

> **Superseded plan notice:** This file originally proposed a "hardware speed calibration"
> fix (`--simulate-kaggle-hardware`, dividing the local budget by 3.45x/4.0x, and switching
> to `EnvSelection.SANDBOX`). That plan was **not implemented as written** — verification
> against the vendored Kaggle gateway (`competition_data/kaggle_evaluation/jed_attack_134815/`)
> showed its core premise was backwards. This file now records what was actually found and
> done. See `docs/guides/LOCAL_EVALUATION.md` and `docs/guides/VERSIONING_WORKFLOW.md` for
> the live documentation.

## What the original plan got wrong

- **Claimed:** local M2 Pro is ~3.5x faster than Kaggle T4x2, so local *over*-inflates scores
  and the budget should be divided down.
- **Actual data:** identical V1 code scored **49.68 local (900s) vs 88.74 Kaggle (9000s
  official / 8750s gateway)** — local *under*-reported by ~1.8x. Dividing the budget further
  would have widened the gap, not closed it.
- **Claimed:** should switch to `EnvSelection.SANDBOX` "to mirror Kaggle's backend security
  wrappers."
- **Actual:** the real attack gateway (`jed_attack_gateway.py`) hard-requires
  `EnvSelection.GYM` and raises `ValueError` on anything else — `SANDBOX` is the *defense*
  gateway's environment. Using `SANDBOX` locally was itself a major source of the gap.
- **Claimed:** scoring mechanics include "Unique Cell Decay" (a decaying +2 bonus) and a
  `HARD_N_CAP` under a different name. Neither exists in `aicomp_sdk/scoring.py` — the +2
  bonus is a flat, non-decaying set-membership count, and the real cap is
  `MAX_REPLAY_FINDINGS = 2000` (`aicomp_sdk/evaluation/ops.py`).

## What was actually verified and fixed

1. **`evaluate_local.py`**: `env_selection` → `EnvSelection.GYM`; default `--budget` → `8750`
   (the gateway's real `DEFAULT_BUDGET_S`); removed the `--simulate-kaggle-hardware` flag and
   its ÷3.45/÷4.0 scaling entirely; every run now appends a summary line to
   `results/results.jsonl`.
2. **`simulate_kaggle.sh`**: runs `--model both --budget 8750` against a chosen attack
   version (default `versions/v7_k1_live.py`), with an honest note that local wall-clock is
   not Kaggle's T4 and needs calibration, not a divisor.
3. **`docs/guides/LOCAL_EVALUATION.md`**: rewritten section-by-section against the verified
   SDK source — real scoring formula, real cap name/value, real budget constant, the `gym`
   requirement, the ~2x-budget wall-clock behavior (generate + replay each get a fresh
   deadline), and a calibration procedure anchored on the known V1 = 88.74 Kaggle score
   (instead of an invented hardware divisor).
4. **Smoke-tested end-to-end**: a 20s budget run correctly reaches the replay phase before
   timing out (proves the `gym` path constructs and runs); a 300s run completes cleanly with
   `raw = findings × 18` matching the scoring formula exactly under the new `gym` env.
5. **Calibration run launched**: `versions/v1_original.py` (the 88.74 anchor) at the real
   `--budget 8750` on Gemma, to establish the local↔Kaggle calibration constant under the
   corrected conditions. Log: `local_eval_artifacts/calibration_gemma_v1_8750.log`.

## Follow-on scope (versioning system)

The user clarified there is no single fixed baseline — they iterate across many attack
variants and public Kaggle notebooks. This grew into a small versioning system, documented
separately in `docs/guides/VERSIONING_WORKFLOW.md`:
- `versions/` — canonical catalog of standalone `AttackAlgorithm` `.py` files.
- `extract_attack.py` — pulls an `AttackAlgorithm` out of any notebook (own or public).
- `package_submission.py` — packages a `.py` into a submission notebook (replaces the
  orphaned, quoting-fragile `inject_code.py`, which has been removed).

## Status

- [x] Root-caused the local↔Kaggle scoring gap (env + budget, not the attack code).
- [x] Fixed `evaluate_local.py` and `simulate_kaggle.sh`.
- [x] Corrected `docs/guides/LOCAL_EVALUATION.md`.
- [x] Built and tested the versioning/extraction/packaging tooling.
- [ ] Calibration run result (V1 @ 8750s/gym vs the 88.74 Kaggle anchor) — pending, in
      progress as of this commit; record the result in `versions/README.md` once it lands.
