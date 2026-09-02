## ADDED Requirements

### Requirement: Control-preserving variant isolation
The implementation SHALL keep `attack.py` unchanged during variant screening and SHALL place GPT densification experiments in separate versioned modules under `versions/`.

#### Scenario: Screening starts
- **WHEN** the densification sprint begins
- **THEN** `attack.py` remains byte-identical to the selected control baseline and new behaviors are introduced only in separate variant files

### Requirement: GPT raw-per-second gating
The evaluation flow SHALL run each candidate variant on `gpt_oss` with budget `300` and seed `123`, compute `raw_per_generation_s`, and compare it to the same-session control value.

#### Scenario: Variant underperforms gate
- **WHEN** a variant's GPT `raw_per_generation_s` uplift versus control is below `1.8x`, or the run crashes/timeouts
- **THEN** the variant is rejected and SHALL NOT proceed to submission

### Requirement: Gemma regression guard
Any variant that passes the GPT gate SHALL be evaluated on Gemma with budget `300` and seed `123` before submission.

#### Scenario: Blended-risk regression
- **WHEN** the finalist variant's Gemma score regresses by more than `5%` versus same-session control
- **THEN** the variant is rejected for submission even if GPT metrics improved

### Requirement: Decision traceability
The sprint outcome SHALL be recorded in `docs/reports/EXPERIMENTS.md` with control metrics, variant metrics, gating decision, and submission decision.

#### Scenario: Sprint completes
- **WHEN** all targeted variants are evaluated or killed
- **THEN** the experiment report documents the measured values and explicit go/no-go rationale
