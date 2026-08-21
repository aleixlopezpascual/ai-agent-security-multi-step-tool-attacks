#!/usr/bin/env python3
"""Package a standalone attack .py into a Kaggle submission notebook.

Emits the proven v15 three-cell scaffold:
  cell 0 - resolve the competition dataset root onto sys.path
  cell 1 - embed the attack source and write it to /kaggle/working/attack.py
  cell 2 - serve the JED inference server on a competition rerun, else write a
           placeholder submission.csv

Optionally syncs kernel-metadata.json's code_file/id/title to the new notebook.
This replaces the older inject_code.py, which was hard-wired to a single stale
notebook and embedded the source with fragile f-string quoting.

Usage:
    python package_submission.py --attack versions/v1_original.py
    python package_submission.py --attack versions/v7_k1.py --sync-metadata
"""
import argparse
import ast
import json
import sys
from pathlib import Path

CELL0 = """import sys, glob
from pathlib import Path
sys.argv = [sys.argv[0]]
for candidate in glob.glob('/kaggle/input/**/kaggle_evaluation', recursive=True):
    root = str(Path(candidate).parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    print('Dataset root:', root)
    break
print('Setup complete')
"""

# Serve-or-mock. Uses csv.writer (no manual "\\n"), so it is quoting-safe.
CELL2 = """import os, csv
if os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
    import kaggle_evaluation.jed_attack_134815.jed_attack_inference_server as server
    server.JEDAttackInferenceServer().serve()
else:
    with open('/kaggle/working/submission.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['Id', 'Score'])
        w.writerows([['gpt_oss_public', 0.0], ['gpt_oss_private', 0.0], ['gemma_public', 0.0], ['gemma_private', 0.0]])
    print('placeholder submission.csv written. Set GPU T4 x2, Internet Off, then Submit.')
"""


def _validate_attack_source(source: str, path: Path) -> None:
    try:
        tree = ast.parse(source)
    except SyntaxError as err:
        raise ValueError(f"{path} does not parse as Python: {err}") from err
    if not any(isinstance(n, ast.ClassDef) and n.name == "AttackAlgorithm" for n in ast.walk(tree)):
        raise ValueError(f"{path} does not define `class AttackAlgorithm`.")


def _code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def build_notebook(attack_source: str) -> dict:
    # repr() embeds the source exactly and safely regardless of quotes/backslashes
    # in the attack (more robust than a raw triple-quoted literal).
    cell1 = (
        f"attack_code = {attack_source!r}\n"
        "with open('/kaggle/working/attack.py', 'w') as f:\n"
        "    f.write(attack_code)\n"
        "print('attack.py written, chars:', len(attack_code))\n"
    )
    return {
        "cells": [_code_cell(CELL0), _code_cell(cell1), _code_cell(CELL2)],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def sync_metadata(metadata_path: Path, notebook_path: Path, kernel_id: str | None) -> None:
    meta = json.loads(metadata_path.read_text())
    meta["code_file"] = str(notebook_path)
    if kernel_id:
        meta["id"] = kernel_id
        meta["title"] = kernel_id.split("/")[-1]
    else:
        # Derive title from the notebook stem, keep the existing owner prefix.
        owner = meta.get("id", "owner/x").split("/")[0]
        stem = notebook_path.stem
        meta["id"] = f"{owner}/{stem}"
        meta["title"] = stem
    metadata_path.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Synced {metadata_path}: code_file={meta['code_file']}, id={meta['id']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--attack", type=Path, required=True, help="Path to the attack .py to package")
    parser.add_argument("--notebook", type=Path, default=None,
                        help="Output notebook path (default: notebooks/<attack-stem>.ipynb)")
    parser.add_argument("--sync-metadata", action="store_true",
                        help="Update kernel-metadata.json code_file/id/title to the new notebook")
    parser.add_argument("--id", type=str, default=None,
                        help="Kaggle kernel id (owner/slug) to set when syncing metadata")
    parser.add_argument("--metadata", type=Path, default=Path("kernel-metadata.json"),
                        help="Path to kernel-metadata.json (default: ./kernel-metadata.json)")
    args = parser.parse_args()

    if not args.attack.exists():
        print(f"Error: attack file not found: {args.attack}", file=sys.stderr)
        return 1

    source = args.attack.read_text()
    try:
        _validate_attack_source(source, args.attack)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    notebook_path = args.notebook or (Path("notebooks") / f"{args.attack.stem}.ipynb")
    notebook_path.parent.mkdir(parents=True, exist_ok=True)
    nb = build_notebook(source)
    notebook_path.write_text(json.dumps(nb, indent=1) + "\n")
    print(f"Wrote submission notebook -> {notebook_path} (embeds {len(source)} chars from {args.attack})")

    if args.sync_metadata:
        if not args.metadata.exists():
            print(f"Error: metadata not found: {args.metadata}", file=sys.stderr)
            return 1
        sync_metadata(args.metadata, notebook_path, args.id)
    else:
        print("Note: kernel-metadata.json NOT changed (pass --sync-metadata to point it at this notebook).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
