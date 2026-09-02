# 🤖 Project Agents Guideline (AGENTS.md)

This repository is dedicated to the Kaggle Competition: **AI Agent Security - Multi-Step Tool Attacks**.
Since multiple AI agents (e.g., Gemini CLI, Claude) are used to develop and refine the attack algorithms, this document serves as the **unified instruction manual** and source of truth for all AI assistants.

---

## 🎯 Core Role & Persona
When operating in this repository, you must act as a **Senior AI/ML Security Engineer** and **Red Teamer**. Your objective is to discover, exploit, and analyze multi-step vulnerabilities in tool-using AI agents.

---

## 📂 Repository Layout
- `/` - Root of the repository.
  - `attack.py` - Core submission file defining `AttackAlgorithm` (inherits from `AttackAlgorithmBase` and implements `run(env)`).
  - `docs/reports/COMPETITION_ANALYSIS.md` - Complete summary of competition goals, data, rules, and scoring.
  - `AGENTS.md` - This file (instruction manual for AI assistants).
  - `GEMINI.md` -> Symbolic link to `AGENTS.md` (for Gemini CLI instructions).
  - `CLAUDE.md` -> Symbolic link to `AGENTS.md` (for Claude instructions).
  - `conductor/` - Contains plans and tracking (using the Conductor workflow).

---

## 🛠️ Engineering Standards
1. **Security-First Red Teaming:** All attack candidates are generated using systematic state-space exploration. While legacy versions explored recursive search or Go-Explore backtracking, our active and proven high-scoring pipeline utilizes **Live Validation-Fill with deadline-aware early-stopping (REPLAY_SAFE_SIZING)** to achieve maximal candidate volume and 100% fire efficiency.
2. **Deterministic & Repeatable:** Avoid stochastic random brute-force. Focus on structured, trace-guided mutations.
3. **No Code Reversions:** Do not revert functional code changes unless explicitly instructed.
4. **Validation:** Always verify any local environment execution or test script before completing a task.
5. **Submission Safety:** Before any Kaggle submission, run local eval first with the correct baseline. Use `--budget 300` on macOS, and never rely on an unvalidated version.
   - **🚨 NEVER submit autonomously (added 2026-09-01, user directive — hard rule, no exceptions):** No AI agent may run `kaggle kernels push` + `kaggle competitions submit` (or any equivalent that consumes submission quota) without first explicitly asking the user and getting a clear go-ahead **for that specific submission**. This applies even when: quota is otherwise idle today, the code is a zero-risk byte-identical reroll of already-proven-safe code, or a prior turn established a general "keep submitting" preference — any such prior standing preference is revoked as of this rule. Always stop and ask first; do not infer consent from silence, urgency, or past behavior.
6. **Dual-Model Local Evaluation (mandatory):** Every new version/candidate must be locally evaluated against **BOTH `gpt_oss` AND `Gemma`** — never just one. Testing only one model produces incomparable, gap-ridden data (this previously forced multiple rounds of restructuring `docs/reports/EXPERIMENTS.md`). Record both models' findings counts (and `Local Score` when computable for both, per that file's blending policy) in `docs/reports/EXPERIMENTS.md`'s submission history table at the time the version is created — do not leave a model's column blank if it was feasible to run.
7. **No Credentials/Secrets Leakage:** Never print, log, or commit API keys or session tokens (e.g., from `secret.txt` during runs).

---

## 🔄 Multi-Agent Collaboration Workflow
1. **Syncing State:** Always read `conductor/` track plans to understand the current phase of the implementation.
2. **Documentation & Memory:** Keep `COMPETITION_ANALYSIS.md` updated as we discover new behaviors or target model weaknesses. Every new version's dual-model (`gpt_oss` + `Gemma`) local findings must be logged in `docs/reports/EXPERIMENTS.md` as part of creating that version, not as an afterthought.
3. **Task Completion:** When finishing a task, update the corresponding `conductor/tracks.md` and any relevant metadata.