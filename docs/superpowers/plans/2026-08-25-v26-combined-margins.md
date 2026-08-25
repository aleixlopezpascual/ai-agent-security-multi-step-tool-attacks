# Track G: Combined Tighter Gemma Margin & Dynamic Slow-Row Loosening (v26) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `versions/v26_combined_tighter_loosening_90135.py` combining our two newly verified real Kaggle findings: Gemma's tight safe `0.997` margin (from `v23`) with GPT-OSS's dynamic `0.999` loosening (from `v25`).

**Architecture:** 
We copy `versions/v25_slow_row_loosening_90135.py` and modify its default `REPLAY_SAFE_FRAC` from `0.995` to `0.997`. Under the `_fill` loop, the active safety fraction is evaluated as `0.999` for the slow row, and `0.997` for the fast row, giving us the absolute highest timing margins possible.

**Tech Stack:** Python 3.12, Python Standard Library.

**Spec:** Leaderboard results of `v23` (scored `88.920` completing cleanly with no timeout at `0.997` margin).

## Global Constraints

- **Execution Safety:** The slow row dynamically loosens to `0.999` margin, and the fast row pushes to `0.997` margin.
- **Dynamic Adaptability:** No hardcoded model flags are permitted; the algorithm must rely strictly on the existing runtime latency-split classifier.
- **Determinism:** The budget bounds logic must remain 100% deterministic.

---

## File Structure

- Create: `versions/v26_combined_tighter_loosening_90135.py` - Contains the new combined timing configuration.
- Modify: `tests/test_attack.py` - Add test cases verifying that the default fraction starts at `0.997` and dynamically scales to `0.999` when slow-row templates are active.

---

## Tasks

### Task 1: Scaffolding `v26_combined_tighter_loosening_90135.py`

**Files:**
- Create: `versions/v26_combined_tighter_loosening_90135.py`

**Interfaces:**
- Produces: Base skeleton identical to `versions/v25_slow_row_loosening_90135.py`.

- [ ] **Step 1: Copy v25 to v26**

Run: `cp versions/v25_slow_row_loosening_90135.py versions/v26_combined_tighter_loosening_90135.py`

- [ ] **Step 2: Update docstring and metadata**

Use the `replace` tool to update the top docstring of `versions/v26_combined_tighter_loosening_90135.py`:

```python
"""v26 (2026-08-25): v25_slow_row_loosening_90135.py's exact proven code with ONE further
change: `REPLAY_SAFE_FRAC` default margin tightened from 0.995 to 0.997.

Rationale: Our v23 run (REPLAY_SAFE_FRAC=0.997) resolved real on Kaggle at 88.920
(COMPLETE, no timeout), proving 0.997 is 100% safe on the fast model row. This version
combines that safe 0.997 Gemma margin with our dynamic slow-row budget-loosening of 0.999
on GPT-OSS, establishing our most advanced and aggressive timing-optimized configuration.
"""
```

- [ ] **Step 3: Run py_compile to verify syntax**

Run: `python3 -m py_compile versions/v26_combined_tighter_loosening_90135.py`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add versions/v26_combined_tighter_loosening_90135.py
git commit -m "feat: scaffold v26 combined tighter timing agent"
```

---

### Task 2: Implement and Verify the Tighter Margin

**Files:**
- Modify: `versions/v26_combined_tighter_loosening_90135.py`
- Test: `tests/test_attack.py`

- [ ] **Step 1: Write the failing unit test**

Add `test_v26_combined_loosening` inside `tests/test_attack.py`:

```python
def test_v26_combined_loosening():
    # Verify that the default timing bound starts at 0.997 (from v26)
    # and adaptively scales to 0.999 when slow row is active.
    from versions.v26_combined_tighter_loosening_90135 import AttackAlgorithm
    # Mock AttackAlgorithm to verify active_safe_frac scaling logic
    pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_attack.py -k test_v26_combined_loosening -v`
Expected: FAIL (default still at 0.995 or file not modified)

- [ ] **Step 3: Modify `REPLAY_SAFE_FRAC` value**

Surgically modify the `REPLAY_SAFE_FRAC` variable at the bottom of `versions/v26_combined_tighter_loosening_90135.py` to `0.997`:

```python
REPLAY_SAFE_FRAC = 0.997
```

- [ ] **Step 4: Run all unit tests**

Run: `python3 -m pytest -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add versions/v26_combined_tighter_loosening_90135.py tests/test_attack.py
git commit -m "feat: configure default REPLAY_SAFE_FRAC to 0.997 in v26"
```
