#!/bin/bash
# Faithful full Kaggle evaluation of one attack version over both models.
# Usage: ./simulate_kaggle.sh [ATTACK_PY]   (default: versions/v7_k1_live.py)
ATTACK="${1:-versions/v7_k1_live.py}"
echo "=== Faithful Kaggle Evaluation: $ATTACK (both models) ==="
echo "Mirrors the real gateway: EnvSelection.GYM, seed=123, 8750s budget per model."
echo "NOTE: local runs on your machine's wall-clock, not a Kaggle T4. A faster"
echo "machine generates more candidates in 8750s and may over-report until the"
echo "2000-candidate cap binds. Calibrate against a known Kaggle score (see LOCAL_EVALUATION.md)."
echo "Wall-clock ~= 2x budget per model (generate + replay), i.e. up to ~9.7h for both."
.venv/bin/python evaluate_local.py --attack "$ATTACK" --model both --budget 8750
echo "=== Simulation Complete (results appended to results/results.jsonl) ==="
