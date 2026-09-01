from __future__ import annotations

import pytest

from tools.summarize_candidate_retention import (
    render_markdown,
    select_records,
    summarize_records,
)


BASELINE = "attack.py"
DENSITY = "versions/v22_multipost4_margin0995.py"


def _record(
    attack: str,
    model: str,
    returned: int,
    validated: int,
    score: float,
) -> dict:
    return {
        "attack": attack,
        "model": model,
        "budget_s": 300,
        "seed": 123,
        "candidates_returned": returned,
        "findings_validated": validated,
        "replay_survival_rate": validated / returned,
        "generation_time_s": 100.0,
        "replay_time_s_approx": 100.0,
        "returned_per_generation_s": returned / 100.0,
        "raw_per_returned_candidate": validated * 18.0 / returned,
        "raw_per_validated_finding": 18.0,
        "score_normalized_0_to_1000": score,
        "score_raw": validated * 18.0,
        "evaluation_time_s": 200.0,
    }


def test_summarize_records_groups_models_and_compares_attacks():
    records = [
        _record(BASELINE, "gpt_oss", 10, 10, 1.0),
        _record(BASELINE, "gpt_oss", 12, 12, 1.2),
        _record(BASELINE, "gemma", 20, 20, 2.0),
        _record(BASELINE, "gemma", 24, 24, 2.4),
        _record(DENSITY, "gpt_oss", 8, 8, 1.5),
        _record(DENSITY, "gpt_oss", 10, 10, 1.7),
        _record(DENSITY, "gemma", 18, 18, 1.8),
        _record(DENSITY, "gemma", 22, 22, 2.2),
    ]

    summary = summarize_records(
        records,
        bootstrap_samples=200,
        bootstrap_seed=7,
    )

    baseline_gpt = summary["attacks"][BASELINE]["models"]["gpt_oss"]
    assert baseline_gpt["runs"] == 2
    assert baseline_gpt["metrics"]["candidates_returned"]["mean"] == 11.0
    assert (
        summary["attacks"][BASELINE]["gemma_to_gpt_returned_ratio"]["estimate"]
        == 2.0
    )
    comparison = summary["density_minus_baseline_blended_score"]
    assert comparison is not None
    assert comparison["difference"] == pytest.approx(0.15)
    assert "Gemma/GPT-OSS returned ratio" in render_markdown(summary)


def test_select_records_filters_budget_and_seed():
    matching = _record(BASELINE, "gpt_oss", 10, 10, 1.0)
    wrong_budget = {**matching, "budget_s": 120}
    wrong_seed = {**matching, "seed": 999}

    assert select_records(
        [matching, wrong_budget, wrong_seed],
        budget=300,
        seed=123,
    ) == [matching]


def test_select_records_rejects_legacy_rows_without_retention_metrics():
    legacy = {
        "attack": BASELINE,
        "model": "gpt_oss",
        "budget_s": 300,
        "seed": 123,
        "findings_count": 78,
        "score_normalized_0_to_1000": 7.02,
    }

    with pytest.raises(ValueError, match="candidates_returned"):
        select_records([legacy], budget=300, seed=123)
