# Track A: Dynamic Budget Sizing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement dynamic candidate capping based on real-time execution speeds to eliminate Kaggle evaluator timeouts ("Green 0").

**Architecture:** We will modify the `AttackAlgorithm` to track the wall-clock time required for successful `env.interact()` calls. Using an exponentially smoothed or rolling average of these times, the algorithm will project the cost of replaying all discovered candidates against the hidden Kaggle guardrails. If the projected replay time threatens the remaining evaluator budget, the search phase halts immediately.

**Tech Stack:** Python, `aicomp_sdk`

**Spec:** `conductor/ROADMAP.md` (Track A section)

## Global Constraints

- Avoid any credentials logging.
- Do not remove existing logic for Phase A, B, and C (Exfiltration and Confused Deputy).
- Retain the baseline's core `Verify-and-Keep` search pattern.

---

### Task 1: Implement Dynamic Time Tracking in `attack.py`

**Files:**
- Modify: `attack.py`

**Interfaces:**
- Consumes: The existing `AttackAlgorithm.run` structure.
- Produces: An updated `keep()` function and updated loop conditions.

- [x] **Step 1: Write the updated tracking variables and time logic**

In `attack.py`, within the `run` method of `AttackAlgorithm`, initialize tracking variables before the `keep()` function:

```python
        # Tracking for dynamic budget sizing
        interact_times = []
        # Multiplier: Replay runs against 2 guardrails + a 20% safety margin
        REPLAY_MULTIPLIER = 2.4  
```

Modify the `keep()` function to record the time taken for interactions:

```python
        def keep(messages):
            if len(findings) >= self.MAX_CANDIDATES:
                return False
            
            # Predict budget before running another interaction
            if len(interact_times) > 0:
                avg_time = sum(interact_times) / len(interact_times)
            else:
                avg_time = 2.0  # Safe default guess
            
            projected_replay_cost = len(findings) * avg_time * REPLAY_MULTIPLIER
            
            # Halt if we are within 2% of total budget limit
            if elapsed() + projected_replay_cost >= budget * 0.98:
                return False

            try:
                env.reset()
                t0 = time.time()
                for m in messages:
                    env.interact(m)
                t1 = time.time()
                fired = bool(eval_predicates(env.export_trace_dict()))
            except Exception:
                return False
                
            if fired:
                interact_times.append(t1 - t0)
                findings.append(AttackCandidate(user_messages=tuple(messages)))
            return fired
```

- [x] **Step 2: Update the Search Phase Loops to respect the new dynamic boundary**

Modify the conditions of all search loops (Phases A, B, and C) to check the dynamic budget. Add a helper function `is_budget_safe()` below `keep()`:

```python
        def is_budget_safe():
            if len(findings) >= self.MAX_CANDIDATES:
                return False
            if not interact_times:
                return True
            avg_time = sum(interact_times) / len(interact_times)
            projected_replay_cost = len(findings) * avg_time * REPLAY_MULTIPLIER
            return elapsed() + projected_replay_cost < budget * 0.98
```

Update the three `while` loops to include `is_budget_safe()`:

```python
        # Phase A
        while elapsed() < a_end and is_budget_safe():
            urls = [host("exfil") for _ in range(self.ENDPOINTS_PER_MSG)]
            keep([_EXFIL_VARIANTS[next(vi)](urls)])

        # Phase B
        while elapsed() < b_end and is_budget_safe():
            keep([_EXFIL_VARIANTS[next(vi)]([host("uniq")])])

        # Phase C
        di = itertools.cycle(range(len(_DEPUTY_VARIANTS)))
        addr_ids = itertools.count()
        while elapsed() < c_end and is_budget_safe():
            addr = "ops" + str(next(addr_ids)) + "@status.example.net"
            keep([_DEPUTY_VARIANTS[next(di)](addr)])
```

- [x] **Step 3: Run Syntax Check**

Run `python3 -m py_compile attack.py` to ensure the syntax is valid.

- [x] **Step 4: Commit changes**

```bash
git add attack.py
git commit -m "feat: implement dynamic replay budget sizing (Track A)"
```
