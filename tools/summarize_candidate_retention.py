from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any


DEFAULT_BASELINE_ATTACK = "attack.py"
DEFAULT_DENSITY_ATTACK = "versions/v22_multipost4_margin0995.py"
DEFAULT_BOOTSTRAP_SAMPLES = 10_000
DEFAULT_BOOTSTRAP_SEED = 123

METRICS = (
    "candidates_returned",
    "findings_validated",
    "replay_survival_rate",
    "generation_time_s",
    "replay_time_s_approx",
    "returned_per_generation_s",
    "raw_per_returned_candidate",
    "raw_per_validated_finding",
    "score_normalized_0_to_1000",
    "score_raw",
    "evaluation_time_s",
)


def read_jsonl(paths: Sequence[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        with path.open() as source:
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"{path}:{line_number} is not a JSON object")
                records.append(value)
    return records


def select_records(
    records: Iterable[dict[str, Any]],
    *,
    budget: float,
    seed: int,
) -> list[dict[str, Any]]:
    selected = [
        record
        for record in records
        if float(record.get("budget_s", -1)) == float(budget)
        and int(record.get("seed", -1)) == seed
    ]
    if not selected:
        raise ValueError(f"No records match budget={budget:g} and seed={seed}")

    required = {
        "attack",
        "model",
        "candidates_returned",
        "findings_validated",
        "score_normalized_0_to_1000",
    }
    for record in selected:
        missing = sorted(required - record.keys())
        if missing:
            raise ValueError(
                f"Record for {record.get('attack', '<unknown>')} is missing: "
                + ", ".join(missing)
            )
    return selected


def _percentile(sorted_values: Sequence[float], quantile: float) -> float:
    if not sorted_values:
        raise ValueError("Cannot calculate a percentile of an empty sequence")
    position = (len(sorted_values) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = position - lower
    return (
        sorted_values[lower] * (1.0 - fraction)
        + sorted_values[upper] * fraction
    )


def bootstrap_mean_ci(
    values: Sequence[float],
    *,
    rng: random.Random,
    samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
) -> list[float]:
    if not values:
        raise ValueError("Cannot bootstrap an empty sequence")
    if samples < 1:
        raise ValueError("Bootstrap sample count must be positive")
    n_values = len(values)
    estimates = sorted(
        statistics.fmean(values[rng.randrange(n_values)] for _ in range(n_values))
        for _ in range(samples)
    )
    return [
        _percentile(estimates, 0.025),
        _percentile(estimates, 0.975),
    ]


def bootstrap_ratio_ci(
    numerator: Sequence[float],
    denominator: Sequence[float],
    *,
    rng: random.Random,
    samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
) -> list[float]:
    if not numerator or not denominator:
        raise ValueError("Both ratio samples must be non-empty")
    if any(value <= 0.0 for value in denominator):
        raise ValueError("Ratio denominator samples must be positive")

    numerator_n = len(numerator)
    denominator_n = len(denominator)
    estimates = []
    for _ in range(samples):
        numerator_mean = statistics.fmean(
            numerator[rng.randrange(numerator_n)] for _ in range(numerator_n)
        )
        denominator_mean = statistics.fmean(
            denominator[rng.randrange(denominator_n)]
            for _ in range(denominator_n)
        )
        estimates.append(numerator_mean / denominator_mean)
    estimates.sort()
    return [
        _percentile(estimates, 0.025),
        _percentile(estimates, 0.975),
    ]


def _numeric_values(
    records: Sequence[dict[str, Any]],
    metric: str,
) -> list[float]:
    values = [record.get(metric) for record in records]
    return [float(value) for value in values if value is not None]


def _metric_summary(
    values: Sequence[float],
    *,
    rng: random.Random,
    bootstrap_samples: int,
) -> dict[str, Any]:
    if not values:
        return {
            "n": 0,
            "mean": None,
            "stdev": None,
            "min": None,
            "max": None,
            "mean_ci95": None,
        }
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "mean_ci95": bootstrap_mean_ci(
            values,
            rng=rng,
            samples=bootstrap_samples,
        ),
    }


def summarize_records(
    records: Sequence[dict[str, Any]],
    *,
    baseline_attack: str = DEFAULT_BASELINE_ATTACK,
    density_attack: str = DEFAULT_DENSITY_ATTACK,
    bootstrap_samples: int = DEFAULT_BOOTSTRAP_SAMPLES,
    bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(str(record["attack"]), str(record["model"]))].append(record)

    rng = random.Random(bootstrap_seed)
    attacks: dict[str, dict[str, Any]] = {}
    for (attack, model), group in sorted(grouped.items()):
        attack_summary = attacks.setdefault(attack, {"models": {}})
        attack_summary["models"][model] = {
            "runs": len(group),
            "metrics": {
                metric: _metric_summary(
                    _numeric_values(group, metric),
                    rng=rng,
                    bootstrap_samples=bootstrap_samples,
                )
                for metric in METRICS
            },
        }

    for attack, attack_summary in attacks.items():
        models = attack_summary["models"]
        if "gemma" not in models or "gpt_oss" not in models:
            continue
        gemma_values = _numeric_values(
            grouped[(attack, "gemma")],
            "candidates_returned",
        )
        gpt_values = _numeric_values(
            grouped[(attack, "gpt_oss")],
            "candidates_returned",
        )
        estimate = statistics.fmean(gemma_values) / statistics.fmean(gpt_values)
        attack_summary["gemma_to_gpt_returned_ratio"] = {
            "estimate": estimate,
            "ci95": bootstrap_ratio_ci(
                gemma_values,
                gpt_values,
                rng=rng,
                samples=bootstrap_samples,
            ),
        }

    comparison = _blended_score_comparison(
        grouped,
        baseline_attack=baseline_attack,
        density_attack=density_attack,
        rng=rng,
        bootstrap_samples=bootstrap_samples,
    )
    return {
        "bootstrap": {
            "samples": bootstrap_samples,
            "seed": bootstrap_seed,
        },
        "attacks": attacks,
        "density_minus_baseline_blended_score": comparison,
    }


def _blended_score_comparison(
    grouped: dict[tuple[str, str], list[dict[str, Any]]],
    *,
    baseline_attack: str,
    density_attack: str,
    rng: random.Random,
    bootstrap_samples: int,
) -> dict[str, Any] | None:
    samples: dict[tuple[str, str], list[float]] = {}
    for attack in (baseline_attack, density_attack):
        for model in ("gpt_oss", "gemma"):
            key = (attack, model)
            if key not in grouped:
                return None
            samples[key] = _numeric_values(
                grouped[key],
                "score_normalized_0_to_1000",
            )

    baseline = statistics.fmean(
        [
            statistics.fmean(samples[(baseline_attack, "gpt_oss")]),
            statistics.fmean(samples[(baseline_attack, "gemma")]),
        ]
    )
    density = statistics.fmean(
        [
            statistics.fmean(samples[(density_attack, "gpt_oss")]),
            statistics.fmean(samples[(density_attack, "gemma")]),
        ]
    )

    estimates = []
    for _ in range(bootstrap_samples):
        bootstrapped: dict[tuple[str, str], float] = {}
        for key, values in samples.items():
            n_values = len(values)
            bootstrapped[key] = statistics.fmean(
                values[rng.randrange(n_values)] for _ in range(n_values)
            )
        baseline_sample = statistics.fmean(
            [
                bootstrapped[(baseline_attack, "gpt_oss")],
                bootstrapped[(baseline_attack, "gemma")],
            ]
        )
        density_sample = statistics.fmean(
            [
                bootstrapped[(density_attack, "gpt_oss")],
                bootstrapped[(density_attack, "gemma")],
            ]
        )
        estimates.append(density_sample - baseline_sample)
    estimates.sort()

    return {
        "baseline_attack": baseline_attack,
        "density_attack": density_attack,
        "baseline_blended_mean": baseline,
        "density_blended_mean": density,
        "difference": density - baseline,
        "difference_ci95": [
            _percentile(estimates, 0.025),
            _percentile(estimates, 0.975),
        ],
    }


def _format_estimate(summary: dict[str, Any], digits: int = 2) -> str:
    mean = summary["mean"]
    ci = summary["mean_ci95"]
    if mean is None or ci is None:
        return "n/a"
    return f"{mean:.{digits}f} [{ci[0]:.{digits}f}, {ci[1]:.{digits}f}]"


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "| Attack | Model | n | Returned mean [95% CI] | "
        "Validated mean | Survival mean | Raw/returned | Returned/s |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for attack, attack_summary in summary["attacks"].items():
        for model, model_summary in attack_summary["models"].items():
            metrics = model_summary["metrics"]
            lines.append(
                f"| `{attack}` | {model} | {model_summary['runs']} | "
                f"{_format_estimate(metrics['candidates_returned'])} | "
                f"{_format_estimate(metrics['findings_validated'])} | "
                f"{_format_estimate(metrics['replay_survival_rate'], 4)} | "
                f"{_format_estimate(metrics['raw_per_returned_candidate'])} | "
                f"{_format_estimate(metrics['returned_per_generation_s'], 4)} |"
            )

    for attack, attack_summary in summary["attacks"].items():
        ratio = attack_summary.get("gemma_to_gpt_returned_ratio")
        if ratio is not None:
            lines.append(
                f"\n- `{attack}` Gemma/GPT-OSS returned ratio: "
                f"{ratio['estimate']:.3f} "
                f"[{ratio['ci95'][0]:.3f}, {ratio['ci95'][1]:.3f}]"
            )

    comparison = summary["density_minus_baseline_blended_score"]
    if comparison is not None:
        lines.append(
            "\n- Density minus baseline blended score: "
            f"{comparison['difference']:.3f} "
            f"[{comparison['difference_ci95'][0]:.3f}, "
            f"{comparison['difference_ci95'][1]:.3f}]"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize per-model retained-candidate evaluation records"
    )
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--budget", type=float, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument(
        "--baseline-attack",
        default=DEFAULT_BASELINE_ATTACK,
    )
    parser.add_argument(
        "--density-attack",
        default=DEFAULT_DENSITY_ATTACK,
    )
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    records = select_records(
        read_jsonl(args.paths),
        budget=args.budget,
        seed=args.seed,
    )
    summary = summarize_records(
        records,
        baseline_attack=args.baseline_attack,
        density_attack=args.density_attack,
    )
    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(summary, indent=2) + "\n")
    print(render_markdown(summary))


if __name__ == "__main__":
    main()
