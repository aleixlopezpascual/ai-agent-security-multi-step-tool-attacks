# 🔁 Attack Versioning & Experimentation Workflow

There is no single fixed baseline for this competition — we continuously try new attack
variants and public Kaggle notebooks against the aligned local evaluator (see
`docs/guides/LOCAL_EVALUATION.md`) before spending a Kaggle submission on them. This doc
describes the tooling and loop for that.

## The canonical unit: `versions/*.py`

Every attack variant we care about — ours or a public notebook's — ends up as a standalone
`.py` file in `versions/` defining `class AttackAlgorithm`. Standalone `.py` is easy to diff,
easy to run directly with `evaluate_local.py --attack`, and is the thing both the extractor
and packer operate on.

```
versions/
  v1_original.py               # BURST_K=1 ground-truth baseline — scored 88.740 on Kaggle (Gemma)
  v20_tighter_margins_0995.py  # REPLAY_SAFE_FRAC 0.995 — best real score (90.135)
  v23_tighter_margins_0997.py  # REPLAY_SAFE_FRAC 0.997 — latest margin tightening (PENDING)
```

See `versions/README.md` for the up-to-date index and any known scores.

## The loop

```
                 ┌─────────────────────┐
 public .ipynb → │ extract_attack.py   │ → versions/NAME.py
                 └─────────────────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ evaluate_local.py   │ → results/results.jsonl (+ stdout SUMMARY)
                 │ --attack versions/  │
                 │   NAME.py           │
                 └─────────────────────┘
                            │  looks promising?
                            ▼
                 ┌─────────────────────┐
                 │ package_submission  │ → notebooks/NAME.ipynb (+ kernel-metadata.json
                 │ .py --sync-metadata │    if --sync-metadata)
                 └─────────────────────┘
                            │
                            ▼
                     kaggle kernels push  (Kaggle run; get public score)
                            │
                            ▼
                 record the Kaggle score in versions/README.md
```

### 1. Bring in a version

- **Your own idea:** write it directly as `versions/NAME.py` (copy an existing version as a
  starting point, e.g. `cp versions/v7_k1_live.py versions/v8_experiment.py`).
- **A public Kaggle notebook:** extract its `AttackAlgorithm` automatically:
  ```bash
  python3 extract_attack.py path/to/public_kernel.ipynb --out versions/public_name.py
  ```
  Handles the three conventions seen in practice: a wrapped `attack_code = '''...'''`
  (or similarly-named) string embed, a `%%writefile .../attack.py` magic cell, and a cell
  that directly defines `class AttackAlgorithm`.

### 2. Evaluate locally

```bash
# Fast smoke test — confirms it runs and finds something (NOT leaderboard-comparable)
python3 evaluate_local.py --attack versions/NAME.py --model gemma --budget 300

# Faithful single-model run at the real Kaggle budget
python3 evaluate_local.py --attack versions/NAME.py --model gemma --budget 8750

# Faithful full run, both models
./simulate_kaggle.sh versions/NAME.py
```

Every run appends a JSON line to `results/results.jsonl`: `attack`, `model`, `budget_s`,
`score_normalized_0_to_1000`, `score_raw`, `findings_count`, timestamps. Compare versions
with e.g.:
```bash
jq -s 'group_by(.attack) | map({attack: .[0].attack, scores: map(.score_normalized_0_to_1000)})' results/results.jsonl
```

Remember: local numbers are only comparable to Kaggle after calibration against a known
anchor (see `LOCAL_EVALUATION.md` §5) — treat local score *deltas between versions* as more
trustworthy than any single absolute number.

### 3. Package for submission

```bash
python3 package_submission.py --attack versions/NAME.py --sync-metadata
```
Writes `notebooks/NAME.ipynb` using the proven 3-cell scaffold (dataset-path setup → embed
+ write `attack.py` → serve on rerun / write placeholder `submission.csv` otherwise) and,
with `--sync-metadata`, updates `kernel-metadata.json` (`code_file`, `id`, `title`) to point
at it. Omit `--sync-metadata` to build the notebook without touching what's currently live.

### 4. Submit and record

Push with the Kaggle CLI as usual (`kaggle kernels push`), and once the public score comes
back, add a line to `versions/README.md` so the next session (or agent) has it.

## Notes

- `package_submission.py` replaces the old `inject_code.py`, which was hard-wired to a
  single stale notebook and embedded source via fragile f-string quoting. The new packer
  uses `repr()` to embed the source (safe for any quoting/escaping) and round-trips
  byte-identically with `extract_attack.py`.
- Root-level `local_attack_*.py` and `attack.py` are legacy/scratch files kept for
  historical reference (see memory `live-vs-stale-submission-files`) — new work should go
  through `versions/`.
