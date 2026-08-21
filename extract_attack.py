#!/usr/bin/env python3
"""Extract a standalone AttackAlgorithm source (.py) from a Jupyter notebook.

Handles three notebook shapes:

  1. Wrapped embed (our v15 style):  a cell assigns
         attack_code = r'''...full attack.py source...'''
     The string constant is extracted verbatim.

  2. Writefile magic (common in public Kaggle notebooks): a cell begins with
         %%writefile /kaggle/working/attack.py
     The cell body after the magic is taken as the attack module.

  3. Direct definition: a cell contains
         class AttackAlgorithm(...):
     That cell's source (with leading Jupyter magics stripped) is taken.

The extracted source is validated (must parse and define `class AttackAlgorithm`)
and written to a standalone .py that `evaluate_local.py --attack` can run.

Usage:
    python extract_attack.py notebooks/ai-agent-security-v15.ipynb
    python extract_attack.py path/to/public_kernel.ipynb --out versions/public_x.py
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

_MAGIC_RE = re.compile(r"^\s*[%!]")
_WRITEFILE_RE = re.compile(r"^\s*%%writefile\s+(\S+)", re.MULTILINE)


def _cell_text(cell) -> str:
    src = cell.get("source", "")
    return src if isinstance(src, str) else "".join(src)


def _strip_magics(text: str) -> str:
    """Drop leading Jupyter magic / shell lines (%..., %%..., !...) so the rest parses."""
    lines = text.splitlines()
    return "\n".join(ln for ln in lines if not _MAGIC_RE.match(ln))


def _find_writefile_attack(cell_text: str) -> str | None:
    """If the cell is `%%writefile <...attack.py>`, return the body after the magic."""
    m = _WRITEFILE_RE.search(cell_text)
    if not m or not m.group(1).endswith(".py"):
        return None
    # Everything after the writefile magic line is the file body.
    idx = cell_text.index("\n", m.start()) if "\n" in cell_text[m.start():] else len(cell_text)
    body = cell_text[idx + 1:]
    return body if _defines_attack_algorithm(body) else None


def _find_wrapped_attack_code(cell_text: str) -> str | None:
    """Return the value of a `<name> = <str literal>` assignment whose string defines
    AttackAlgorithm. The embed variable is often `attack_code`, but public notebooks use
    other names (e.g. ATTACK_SRC), so match by content rather than variable name.
    Prefers an `attack_code`-named assignment when several qualify."""
    try:
        tree = ast.parse(cell_text)
    except SyntaxError:
        return None
    fallback = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            value = node.value.value
            if not _defines_attack_algorithm(value):
                continue
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "attack_code" in names:
                return value
            if fallback is None:
                fallback = value
    return fallback


def _defines_attack_algorithm(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return any(
        isinstance(n, ast.ClassDef) and n.name == "AttackAlgorithm"
        for n in ast.walk(tree)
    )


def extract(notebook_path: Path) -> str:
    nb = json.loads(notebook_path.read_text())
    code_cells = [_cell_text(c) for c in nb.get("cells", []) if c.get("cell_type") == "code"]

    # 1. Prefer the wrapped `attack_code = r'''...'''` embed.
    for text in code_cells:
        wrapped = _find_wrapped_attack_code(text)
        if wrapped and _defines_attack_algorithm(wrapped):
            return wrapped

    # 2. `%%writefile ...attack.py` cell: the body is the module source.
    for text in code_cells:
        body = _find_writefile_attack(text)
        if body is not None:
            return body

    # 3. Fall back to a cell that directly defines class AttackAlgorithm
    #    (after stripping any leading Jupyter magics / shell lines).
    for text in code_cells:
        stripped = _strip_magics(text)
        if _defines_attack_algorithm(stripped):
            return stripped

    raise ValueError(
        f"No AttackAlgorithm found in {notebook_path}. Looked for an "
        "`attack_code = '''...'''` wrapper, a `%%writefile ...attack.py` cell, "
        "and a direct `class AttackAlgorithm` cell."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("notebook", type=Path, help="Path to the .ipynb to extract from")
    parser.add_argument("--out", type=Path, default=None,
                        help="Output .py path (default: versions/<notebook-stem>.py)")
    args = parser.parse_args()

    if not args.notebook.exists():
        print(f"Error: notebook not found: {args.notebook}", file=sys.stderr)
        return 1

    try:
        source = extract(args.notebook)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    out = args.out or (Path("versions") / f"{args.notebook.stem}.py")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source)
    print(f"Extracted AttackAlgorithm -> {out} ({len(source)} chars)")
    print(f"Validate/run it with:  .venv/bin/python evaluate_local.py --attack {out} --model gemma --budget 300")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
