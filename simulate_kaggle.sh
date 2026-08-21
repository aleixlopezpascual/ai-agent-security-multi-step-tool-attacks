#!/bin/bash
echo "=== Starting Full Kaggle Leaderboard Simulation ==="
echo "This will run both models simulating the exact T4x2 hardware speeds."
.venv/bin/python evaluate_local.py --model both --budget 9000 --simulate-kaggle-hardware
echo "=== Simulation Complete ==="
