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
  - `COMPETITION_ANALYSIS.md` - Complete summary of competition goals, data, rules, and scoring.
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
6. **No Credentials/Secrets Leakage:** Never print, log, or commit API keys or session tokens (e.g., from `secret.txt` during runs).

---

## 🔄 Multi-Agent Collaboration Workflow
1. **Syncing State:** Always read `conductor/` track plans to understand the current phase of the implementation.
2. **Documentation & Memory:** Keep `COMPETITION_ANALYSIS.md` updated as we discover new behaviors or target model weaknesses.
3. **Task Completion:** When finishing a task, update the corresponding `conductor/tracks.md` and any relevant metadata.