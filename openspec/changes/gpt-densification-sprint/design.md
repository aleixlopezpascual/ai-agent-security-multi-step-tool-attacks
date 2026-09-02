## Context

The repo already contains a strong baseline attack architecture and many historical variants. Recent evidence shows the live bottleneck is not replay retention but candidate economics: K=1 single-post findings have fixed per-candidate value and are constrained by GPT throughput. We need a narrow sprint that tests only high-EV GPT densification moves while preserving Gemma stability.

## Goals / Non-Goals

**Goals:**
- Compare control vs three GPT-focused variants using identical local settings (300s, seed 123).
- Use a strict quantitative gate (`raw_per_generation_s`) to decide whether a variant has real headroom.
- Preserve baseline behavior and avoid destabilizing the primary attack path unless a variant clearly wins.

**Non-Goals:**
- Re-open broad margin/threshold tuning.
- Rewrite the attack architecture.
- Add new tooling or external dependencies.

## Decisions

1. **Use variant files rather than mutating control first.**  
   Rationale: isolates risk and keeps `attack.py` stable during screening.

2. **Target only slow-row densification levers for GPT.**  
   Rationale: prior evidence indicates Gemma is less constrained; GPT row is the likely binding limiter.

3. **Gate on `raw_per_generation_s` instead of findings count alone.**  
   Rationale: score uplift requires better value per unit time, not just occasional higher counts.

4. **Apply a Gemma regression guard before any submission.**  
   Rationale: blended leaderboard score can regress even if GPT improves.

## Risks / Trade-offs

- **Risk:** multipost variants increase per-candidate latency and reduce total retained candidates.  
  **Mitigation:** strict GPT raw/sec threshold and immediate kill for underperformers.

- **Risk:** mail-notify wording fails to induce stable second-tool behavior.  
  **Mitigation:** treat it as experimental; keep as a standalone branch with independent measurement.

- **Risk:** local-to-live transfer mismatch.  
  **Mitigation:** submit only the best gated candidate and keep baseline fallback available.

## Migration Plan

1. Implement variants in `versions/`.
2. Run local control + variant benchmark sequence with consistent parameters.
3. Promote only the winner (if any) to submission flow.
4. Update experiment log with measured outcomes and go/no-go result.

Rollback: retain `attack.py` unchanged unless a candidate is explicitly promoted.

## Open Questions

- Whether any GPT densification branch can exceed the 1.8x raw/sec continuation gate in this environment.
- Whether the mail-notify branch can produce repeatable multi-predicate uplift without unacceptable latency.
