from __future__ import annotations

import pytest

import retention_metrics
from retention_metrics import (
    GenerationTelemetry,
    derive_retention_metrics,
    instrument_attack_class,
)


def test_instrument_attack_class_preserves_candidates(monkeypatch):
    candidates = [object(), object(), object()]

    class FakeAttack:
        def run(self, env, config):
            return candidates

    times = iter((10.0, 12.5))
    monkeypatch.setattr(retention_metrics.time, "monotonic", lambda: next(times))

    instrumented = instrument_attack_class(FakeAttack)
    result = instrumented().run(object(), object())

    assert result is candidates
    assert instrumented.generation_telemetry == GenerationTelemetry(
        candidates_returned=3,
        generation_time_s=2.5,
    )


def test_derive_retention_metrics():
    metrics = derive_retention_metrics(
        telemetry=GenerationTelemetry(
            candidates_returned=4,
            generation_time_s=2.0,
        ),
        findings_validated=3,
        score_raw=54.0,
        evaluation_time_s=5.0,
    )

    assert metrics == {
        "candidates_returned": 4,
        "findings_validated": 3,
        "replay_dropped": 1,
        "replay_survival_rate": 0.75,
        "generation_time_s": 2.0,
        "replay_time_s_approx": 3.0,
        "returned_per_generation_s": 2.0,
        "raw_per_returned_candidate": 13.5,
        "raw_per_validated_finding": 18.0,
    }


def test_derive_retention_metrics_handles_zero_candidates():
    metrics = derive_retention_metrics(
        telemetry=GenerationTelemetry(
            candidates_returned=0,
            generation_time_s=0.0,
        ),
        findings_validated=0,
        score_raw=0.0,
        evaluation_time_s=0.0,
    )

    assert metrics["replay_survival_rate"] is None
    assert metrics["returned_per_generation_s"] is None
    assert metrics["raw_per_returned_candidate"] is None
    assert metrics["raw_per_validated_finding"] is None


def test_derive_retention_metrics_rejects_impossible_counts():
    with pytest.raises(
        ValueError,
        match="Validated findings cannot exceed returned candidates",
    ):
        derive_retention_metrics(
            telemetry=GenerationTelemetry(
                candidates_returned=2,
                generation_time_s=1.0,
            ),
            findings_validated=3,
            score_raw=54.0,
            evaluation_time_s=2.0,
        )
