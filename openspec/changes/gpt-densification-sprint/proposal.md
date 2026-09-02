## Why

Our current live-best family is plateaued around the high-80s/low-90s blended score. The current attack is effectively K=1 throughput-bound, and repeated margin/order sweeps have not produced sustained uplift, so we need a focused GPT-row densification sprint with hard kill criteria.

## What Changes

- Keep `attack.py` unchanged as the control baseline.
- Add three GPT-focused densification variants under `versions/`:
  - slow-row multipost `N=2`
  - slow-row multipost `N=3`
  - slow-row multipost with EXFIL + mail-notify wording that avoids `send`/`email`/`upload` tokens in user text.
- Evaluate control + variants with the existing local evaluator at 300s budget and seed 123.
- Gate continuation and submission on measured GPT `raw_per_generation_s` uplift and Gemma regression limits.
- Record outcomes in `docs/reports/EXPERIMENTS.md`.

## Capabilities

### New Capabilities
- `gpt-densification-variants`: isolated, model-conditioned attack variants with explicit local gating and go/no-go thresholds.

### Modified Capabilities
- None.

## Impact

- Affected code: `versions/*.py` (new variant files), optional `attack.py` replacement only if a winner is selected for submission.
- Affected process/docs: `docs/reports/EXPERIMENTS.md` update with measured results and decision.
- No new dependencies.
