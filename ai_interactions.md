# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent to extend the PawPal+ scheduling engine with a third advanced capability beyond the core plan generation flow and to document the work in the project notes. The goal was to add a next-available-slot recommendation and wire it into the app without breaking the existing tests.

**What did the agent do?**

The agent updated the scheduling backend in pawpal_system.py with a new next-available-slot algorithm, exposed the recommendation in app.py so the UI can show a suggested open slot, added a regression test in tests/test_pawpal_system.py, and filled in this workflow log.

**What did you have to verify or fix manually?**

I verified the new behavior by running the test suite and corrected one edge case in the slot-selection logic so it recommends a realistic opening between existing scheduled tasks rather than the start of the day.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
