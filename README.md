# 🛡️ AI Agent Security: Multi-step Tool Attacks

Repository for the Kaggle competition: [AI Agent Security - Multi-Step Tool Attacks](https://www.kaggle.com/competitions/ai-agent-security-multi-step-tool-attacks)

This repository details our **Senior AI/ML Security Engineering and Red Teaming** development pipeline. Our development progressed from a public-optimized baseline through robust, high-throughput scheduling engines, culminating in a triumphant private-leaderboard victory via structural attack diversification.

---

## 🏆 The Private Leaderboard & Strategic Post-Mortem

The final competition results spectacularly validated our adversarial risk modeling and defensive engineering discipline, though delivering an invaluable lesson in manual execution:
*   **The Exfiltration Collapse:** Every standard exfiltration candidate across the field (including our peak public-optimized baseline scoring **`90.135`** and our high-throughput `v59_latency_probed_blind_emit` scoring **`89.055`**) scored exactly **`0.000` on the Private Leaderboard**. This was due to the hidden private guardrail implementing persistent provenance tracking (taint tracking that never expires) and strict network-layer checks.
*   **The Surviving Hedge:** Our dedicated diversification hedge, **[`v49_confused_deputy_hedge`](docs/reports/V49_HEDGE_RETROSPECTIVE.md)**, completely bypassed the private security filters to score **`19.650`** on the Private Leaderboard (Ref `55872848`). This score **would have secured a Silver Medal** on the final private standings, as almost the entire field got wiped out to 0.000.
*   **The Post-Mortem Lesson:** While we successfully engineered and verified this 100% correct hedge during development, we unfortunately made a final manual selection error in the Kaggle UI, choosing `v10` and `v20` as our final scored entries. Since both of those options relied on the blocked exfiltration pathway, our official final leaderboard score ended up as `0.000`.

This repository stands as an intellectually honest, highly educational security post-mortem: our threat modeling and security-risk analysis were **100% correct**, and our hedge was **proven fully successful** on the private dataset (and would have secured a Silver Medal), but manual selection prevented us from capturing it.

For a full technical analysis of why standard attacks failed and how our hedge bypassed the private blocks, read our **[Technical Retrospective: The Triumph of v49_confused_deputy_hedge](docs/reports/V49_HEDGE_RETROSPECTIVE.md)**.

---

## 📂 Key Documentation & Reports

*   **[Technical Retrospective: The Triumph of v49](docs/reports/V49_HEDGE_RETROSPECTIVE.md)** - Comprehensive breakdown of the private-leaderboard collapse and how our Confused Deputy hedge saved our final score.
*   **[AI Agent Security Key Learnings & Principles](docs/reports/KEY_LEARNINGS.md)** - High-signal breakdown of our main strategic, platform, and inference engineering takeaways.
*   **[Canonical Experiments Log](docs/reports/EXPERIMENTS.md)** - Full chronological history of all 57 developed versions, local GGUF calibration runs, and real Kaggle submission results.
*   **[Competition & System Analysis](docs/COMPETITION_ANALYSIS.md)** - Deep dive into JED environment mechanics, target models (`gpt_oss`, `gemma`), scoring functions, and platform-level constraints.

---

## 🛠️ Key Architectural Innovations

### 1. `REPLAY_SAFE_SIZING` (Time-Budgeting Sizing Engine)
A stateful time-tracking engine that monitors the real-time execution speeds of target models on the backend. It continually assesses the remaining execution budget and automatically stops appending candidates if container slowdowns or system-level delays are detected, protecting the already-generated findings and guaranteeing 0% timeouts.

### 2. Fast-Probing Latency-Split & Prompt-Forging
During startup, the agent performs a lightweight classification phase (e.g. 8 candidates) to measure inference latency and identify whether the active container is running Gemma vs. GPT-OSS.
*   **For Gemma:** Delivers direct, low-token, padding-free imperatives.
*   **For GPT-OSS:** Forges the assistant's ending XML/block tokens directly in the prompt, tricking the model into immediately closing its reasoning turn and executing the tool call, bypassing up to 10x Chain-of-Thought latency.

### 3. High-Throughput Blind-Emit (`v59`)
Our pinnacle-throughput design that performs startup classification and then blindly generates the remaining 1,992 candidates using the fast template at peak speed. This minimizes per-candidate wall-clock overhead and is virtually immune to late-run container slowdowns.
