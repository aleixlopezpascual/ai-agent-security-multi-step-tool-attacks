from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass(frozen=True, slots=True)
class GenerationTelemetry:
    candidates_returned: int
    generation_time_s: float


def instrument_attack_class(attack_cls: type[Any]) -> type[Any]:
    """Wrap an attack class and capture aggregate generation telemetry."""

    class InstrumentedAttack(attack_cls):
        generation_telemetry: ClassVar[GenerationTelemetry | None] = None

        def run(self, env: Any, config: Any) -> list[Any]:
            started_at = time.monotonic()
            candidates = super().run(env, config)
            generation_time_s = time.monotonic() - started_at
            if not isinstance(candidates, list):
                raise TypeError("AttackAlgorithm.run must return list[AttackCandidate]")
            type(self).generation_telemetry = GenerationTelemetry(
                candidates_returned=len(candidates),
                generation_time_s=generation_time_s,
            )
            return candidates

    InstrumentedAttack.__name__ = f"Instrumented{attack_cls.__name__}"
    InstrumentedAttack.__qualname__ = InstrumentedAttack.__name__
    return InstrumentedAttack


def derive_retention_metrics(
    *,
    telemetry: GenerationTelemetry,
    findings_validated: int,
    score_raw: float,
    evaluation_time_s: float,
) -> dict[str, int | float | None]:
    returned = telemetry.candidates_returned
    generation_time_s = telemetry.generation_time_s

    if returned < 0 or findings_validated < 0:
        raise ValueError("Candidate and finding counts must be non-negative")
    if findings_validated > returned:
        raise ValueError("Validated findings cannot exceed returned candidates")
    if score_raw < 0.0:
        raise ValueError("Raw score must be non-negative")
    if generation_time_s < 0.0 or evaluation_time_s < 0.0:
        raise ValueError("Durations must be non-negative")

    replay_time_s = evaluation_time_s - generation_time_s
    if replay_time_s < -1e-6:
        raise ValueError("Generation time cannot exceed total evaluation time")

    return {
        "candidates_returned": returned,
        "findings_validated": findings_validated,
        "replay_dropped": returned - findings_validated,
        "replay_survival_rate": (
            findings_validated / returned if returned else None
        ),
        "generation_time_s": generation_time_s,
        "replay_time_s_approx": max(0.0, replay_time_s),
        "returned_per_generation_s": (
            returned / generation_time_s if generation_time_s else None
        ),
        "raw_per_returned_candidate": score_raw / returned if returned else None,
        "raw_per_validated_finding": (
            score_raw / findings_validated if findings_validated else None
        ),
    }
