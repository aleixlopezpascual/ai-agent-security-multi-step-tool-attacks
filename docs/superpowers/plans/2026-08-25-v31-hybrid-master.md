# Track L: Pinnacle Champion - Hybrid Master Agent (v31) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `versions/v31_hybrid_master_90135.py` by integrating our zero-waste classification (`SPLIT_CLASSIFY_N = 1`), corrected dynamic timing ledger, and a highly stable Gemma multiposting strategy (`BURST_K = 2`) to cut the grader's replay verification load in half while ensuring a perfect 180.00 score cushion on the fast row.

**Architecture:** 
1. **Gemma Multiposting (`BURST_K = 2`):** Instructs Gemma to sequentially execute 2 exfiltrations per candidate turn. This cuts the required candidates to hit the 2,000 findings cap from 2,000 down to 1,000, reducing the grader's replay verification workload on the fast row by 50%.
2. **Zero-Waste Classification (`SPLIT_CLASSIFY_N = 1`):** Completely eliminates the 142-second classification waste on the slow row.
3. **Corrected Ledger & Optimal Timing Margins:** Maintains our proven `v25` math ledger and optimal timing cushions (`0.997` Gemma / `0.999` GPT-OSS).

**Tech Stack:** Python 3.12, Python Standard Library.

---

## File Structure

- Create: `versions/v31_hybrid_master_90135.py` - Contains the hybrid template and configuration.
- Modify: `tests/test_attack.py` - Add test cases verifying that the new configuration compiles and behaves correctly.

---

## Tasks

### Task 1: Scaffolding `v31_hybrid_master_90135.py`

**Files:**
- Create: `versions/v31_hybrid_master_90135.py`

- [ ] **Step 1: Copy v30 to v31**

Run: `cp versions/v30_ultimate_master_90135.py versions/v31_hybrid_master_90135.py`

- [ ] **Step 2: Update docstring and metadata**

Use the `replace` tool to update the top docstring of `versions/v31_hybrid_master_90135.py`:

```python
"""v31 (2026-08-25): The Pinnacle Champion / Hybrid Master Agent.

Rationale: Implements our ultimate hybrid exfiltration strategy:
1. Zero-waste model classification (SPLIT_CLASSIFY_N = 1) to save 142s of GPT-OSS budget.
2. Gemma multiposting (BURST_K = 2) to cut the grader's replay verification load by 50%.
3. Dynamic timing bounds loosening (0.999) under the corrected timing ledger.
"""
```

- [ ] **Step 3: Run py_compile to verify syntax**

Run: `python3 -m py_compile versions/v31_hybrid_master_90135.py`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add versions/v31_hybrid_master_90135.py
git commit -m "feat: scaffold v31 hybrid master agent"
```

---

### Task 2: Configure and Verify Hybrid Templates & Margins

**Files:**
- Modify: `versions/v31_hybrid_master_90135.py`
- Test: `tests/test_attack.py`

- [ ] **Step 1: Write the failing unit test**

Add `test_v31_hybrid_master` inside `tests/test_attack.py` to assert that:
* `SPLIT_CLASSIFY_N` is exactly 1.
* `BURST_K` is exactly 2.
* `REPLAY_SAFE_FRAC` on Gemma is exactly 0.997.

```python
def test_v31_hybrid_master():
    from versions.v31_hybrid_master_90135 import SPLIT_CLASSIFY_N, BURST_K, REPLAY_SAFE_FRAC
    assert SPLIT_CLASSIFY_N == 1
    assert BURST_K == 2
    assert REPLAY_SAFE_FRAC == 0.997
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_attack.py -k test_v31_hybrid_master -v`
Expected: FAIL

- [ ] **Step 3: Modify configuration constants**

Surgically update `BURST_K` value in `versions/v31_hybrid_master_90135.py`:

```python
BURST_K = 2
```

- [ ] **Step 4: Run all unit tests**

Run: `python3 -m pytest -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add versions/v31_hybrid_master_90135.py tests/test_attack.py
git commit -m "feat: configure v31 to use zero-waste classification, Gemma multiposting, and tighter margins"
```
