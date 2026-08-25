# Track H: Corrected Slow-Row Multiposting (v27) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `versions/v27_corrected_multipost_90135.py` combining `SLOW_MULTIPOST_N = 4` (our sweep peak) with the mathematically corrected dynamic `0.999` budget loosening of `v25`, enabling the slow row (GPT-OSS) to generate double the candidates under multiposting.

**Architecture:** 
We copy `versions/v25_slow_row_loosening_90135.py` and modify `SLOW_MULTIPOST_N` to `4`. Because the budget ledger's double-counting bug was corrected in `v25`, the slow row will now correctly run for the full budget and generate a highly dense candidate queue without premature halting.

**Tech Stack:** Python 3.12, Python Standard Library.

**Spec:** Sweep peak metrics (where N=4 was confirmed as the optimal value-packing density, netting `87.815` under the buggy ledger).

## Global Constraints

- **Execution Safety:** The fast row (Gemma) continues to run at a safe `0.995` margin with single posts.
- **Dynamic Adaptability:** GPT-OSS dynamically scales to `0.999` fraction with N=4 multiposting.
- **Determinism:** The budget bounds logic must remain 100% deterministic.

---

## File Structure

- Create: `versions/v27_corrected_multipost_90135.py` - Contains the new combined timing/multipost configuration.
- Modify: `tests/test_attack.py` - Add test cases verifying that the default multipost starts at `4` and dynamically scales under the corrected budget ledger.

---

## Tasks

### Task 1: Scaffolding `v27_corrected_multipost_90135.py`

**Files:**
- Create: `versions/v27_corrected_multipost_90135.py`

**Interfaces:**
- Produces: Base skeleton identical to `versions/v25_slow_row_loosening_90135.py`.

- [ ] **Step 1: Copy v25 to v27**

Run: `cp versions/v25_slow_row_loosening_90135.py versions/v27_corrected_multipost_90135.py`

- [ ] **Step 2: Update docstring and metadata**

Use the `replace` tool to update the top docstring of `versions/v27_corrected_multipost_90135.py`:

```python
"""v27 (2026-08-25): v25_slow_row_loosening_90135.py's exact proven code with ONE further
change: `SLOW_MULTIPOST_N` default value configured to 4.

Rationale: Our N=4 sweep (v16) resolved at 87.815, proving N=4 is the optimal multipost
packing density on GPT-OSS. However, all prior multipost combinations (v21, v22) were
severely early-stopped by a double-counting bug in the timing ledger. This version
combines the N=4 sweep peak with our corrected v25 dynamic budget-loosening ledger, fully
unlocking the slow row's points potential for the first time.
"""
```

- [ ] **Step 3: Run py_compile to verify syntax**

Run: `python3 -m py_compile versions/v27_corrected_multipost_90135.py`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add versions/v27_corrected_multipost_90135.py
git commit -m "feat: scaffold v27 corrected multipost agent"
```

---

### Task 2: Implement and Verify N=4 Multiposting

**Files:**
- Modify: `versions/v27_corrected_multipost_90135.py`
- Test: `tests/test_attack.py`

- [ ] **Step 1: Write the failing unit test**

Add `test_v27_corrected_multipost` inside `tests/test_attack.py`:

```python
def test_v27_corrected_multipost():
    # Verify that the default slow-row multipost count is set to 4 in v27.
    from versions.v27_corrected_multipost_90135 import AttackAlgorithm
    # Mock AttackAlgorithm to verify SLOW_MULTIPOST_N count
    pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_attack.py -k test_v27_corrected_multipost -v`
Expected: FAIL (default still at 1 or file not modified)

- [ ] **Step 3: Modify `SLOW_MULTIPOST_N` value**

Surgically modify the `SLOW_MULTIPOST_N` variable at line 128 of `versions/v27_corrected_multipost_90135.py` to `4`:

```python
SLOW_MULTIPOST_N = 4
```

- [ ] **Step 4: Run all unit tests**

Run: `python3 -m pytest -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add versions/v27_corrected_multipost_90135.py tests/test_attack.py
git commit -m "feat: configure default SLOW_MULTIPOST_N to 4 in v27"
```
