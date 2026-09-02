#!/bin/bash
set -euo pipefail

if ! command -v kaggle >/dev/null 2>&1; then
  echo "kaggle CLI not found in PATH. Install it first, then retry."
  exit 1
fi

mkdir -p local_models

echo "Downloading GPT-OSS Model (14GB)..."
# Model handle based on Kaggle Models documentation format: owner/model/framework/variation/version
kaggle models instances versions download llkh0a/gpt-oss-20b-gguf/pytorch/default/1 -p local_models/gpt_oss --untar

echo "Downloading Gemma Model (18GB)..."
kaggle models instances versions download llkh0a/gemma-4-26b-a4b-it-ud-q4-k-m-gguf/pytorch/default/1 -p local_models/gemma --untar

echo "Downloads complete!"
