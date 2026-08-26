# Track K: Pinnace Champion - Ultimate Master Agent (v30) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `versions/v30_ultimate_master_90135.py` by integrating our highest-performing timing margins, corrected timing ledger, and an ultra-fast model classification logic (`SPLIT_CLASSIFY_N = 1`), completely eliminating 142 seconds of slow-row latency waste.

**Architecture:** 
1. **Zero-Waste Classification (`SPLIT_CLASSIFY_N = 1`):** Reduces classification samples from 8 down to 1. Since Gemma (1.5s) and GPT-OSS (20.4s) have a clean, massive 13x latency gap, a single sample after untimed warm-up is 100% mathematically robust.
2. **Optimal Timing Margins:** Set `REPLAY_SAFE_FRAC` to `0.997` for Gemma, and dynamically scale to `0.999` for GPT-OSS slow-row.
3. **Corrected Ledger:** Retain the math bug correction that outside-of-loop computes `active_replay_cap` (single-counting latency).

**Tech Stack:** Python 3.12, Python Standard Library.

---

## File Structure

- Create: `versions/v30_ultimate_master_90135.py` - Contains the pinnacle template and configuration.
- Modify: `tests/test_attack.py` - Add test cases verifying that the new configuration compiles and behaves correctly.

---

## Tasks

### Task 1: Scaffolding `v30_ultimate_master_90135.py`

**Files:**
- Create: `versions/v30_ultimate_master_90135.py`

- [ ] **Step 1: Copy v25 to v30**

Run: `cp versions/v25_slow_row_loosening_90135.py versions/v30_ultimate_master_90135.py`

- [ ] **Step 2: Update docstring and metadata**

Use the `replace` tool to update the top docstring of `versions/v30_ultimate_master_90135.py`:

```python
"""v30 (2026-08-25): The Pinnace Champion / Ultimate Master Agent.

Rationale: Combines all verified, top-performing insights from our entire development:
1. Tight timing margin (0.997) for the fast Gemma row.
2. Dynamic slow-row timing bounds loosening (0.999) under the corrected timing ledger.
3. Zero-waste model-row classification (SPLIT_CLASSIFY_N = 1), saving 142.8 seconds of
   unoptimized reasoning-heavy latency on the slow row.
"""
```

- [ ] **Step 3: Run py_compile to verify syntax**

Run: `python3 -m py_compile versions/v30_ultimate_master_90135.py`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add versions/v30_ultimate_master_90135.py
git commit -m "feat: scaffold v30 ultimate master agent"
```

---

### Task 2: Implement and Verify Zero-Waste Classification & Margins

**Files:**
- Modify: `versions/v30_ultimate_master_90135.py`
- Test: `tests/test_attack.py`

- [ ] **Step 1: Write the failing unit test**

Add `test_v30_ultimate_master` inside `tests/test_attack.py` to assert that:
* `SPLIT_CLASSIFY_N` is exactly 1.
* `REPLAY_SAFE_FRAC` on Gemma is exactly 0.997.

```python
def test_v30_ultimate_master():
    from versions.v30_ultimate_master_90135 import AttackAlgorithm
    algo = AttackAlgorithm()
    assert algo.config.get("split_classify_n", 8) == 1
    assert algo.config.get("replay_safe_frac", 0.995) == 0.997
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_attack.py -k test_v30_ultimate_master -v`
Expected: FAIL

- [ ] **Step 3: Modify configuration constants**

Surgically update `SPLIT_CLASSIFY_N` and `REPLAY_SAFE_FRAC` values in `versions/v30_ultimate_master_90135.py`:

```python
SPLIT_CLASSIFY_N = 1
```
and:
```python
REPLAY_SAFE_FRAC = 0.997
```

- [ ] **Step 4: Run all unit tests**

Run: `python3 -m pytest -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add versions/v30_ultimate_master_90135.py tests/test_attack.py
git commit -m "feat: configure v30 to use zero-waste classification and tighter margins"
```
