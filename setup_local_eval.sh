#!/bin/bash
set -euo pipefail
exec > setup_local_eval.log 2>&1
echo "=== Starting Local Evaluation Setup ==="
date

if ! command -v kaggle >/dev/null 2>&1; then
  echo "ERROR: kaggle CLI not found in PATH."
  exit 1
fi

echo "[1/3] Installing llama-cpp-python with Metal support..."
# Using the project's .venv to keep it clean
CMAKE_ARGS="-DGGML_METAL=on" .venv/bin/pip install llama-cpp-python --no-cache-dir

mkdir -p local_models

echo "[2/3] Downloading GPT-OSS Model (14GB)..."
kaggle models instances versions download llkh0a/gpt-oss-20b-gguf/pytorch/default/1 -p local_models/gpt_oss --untar

echo "[3/3] Downloading Gemma Model (18GB)..."
kaggle models instances versions download llkh0a/gemma-4-26b-a4b-it-ud-q4-k-m-gguf/pytorch/default/1 -p local_models/gemma --untar

echo "=== Setup Complete! ==="
date
