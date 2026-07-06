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

---

## ⚖️ Multi-Model Prompt Comparison (Challenge 5)

> Evaluation of two models on the same task: designing the **complex weekly task
> rescheduling interval rules** in `pawpal_system.py`. The relevant code lives in
> `Task.mark_complete()` and `Task._create_next_occurrence()`, which advance a
> recurring task by `timedelta(weeks=1)` when `frequency == TaskFrequency.WEEKLY`.

**Task given to both models:**

> "When a weekly recurring pet-care task is marked complete, generate the next
> occurrence. The next due date must land on the same weekday one week later, must
> preserve the scheduled `HH:MM` time, must reset completion state, and must not
> mutate the original task. Explain any edge cases around `due_date` being `None`."

| | Option A — Claude (Opus 4.8) | Option B — GPT-4o |
|-|------------------------------|-------------------|
| **Model / tool used** | Claude, `claude-opus-4-8` | OpenAI GPT-4o (`gpt-4o`) |
| **Prompt** | Same prompt (above) | Same prompt (above) |
| **Response summary** | Proposed an immutable approach using `dataclasses.replace(...)` to clone the task with a new `task_id`, `is_completed=False`, and `due_date + timedelta(weeks=1)`. Explicitly flagged the `due_date is None` case and defaulted it to `date.today()` before adding the interval, preserving the original weekday. Kept `scheduled_time` untouched so the `HH:MM` value carries over automatically. | Produced a working weekly increment but mutated the original task in place before returning a copy, and initially added `timedelta(days=7)` without addressing the `due_date is None` path — it assumed a date was always present. Suggested re-parsing `scheduled_time` manually. |
| **What was useful** | The immutability guarantee (`replace`) matched our frozen-boundary design and avoided the circular-reference risks we removed earlier. The explicit `None`-date fallback prevented an `AttributeError` at runtime. | Concise and readable; the `timedelta(days=7)` math is equivalent to `weeks=1` and reads fine to newcomers. |
| **Problems noticed** | Slightly more verbose; introduced a `-next` id suffix convention we had to standardize across daily/weekly paths. | In-place mutation would have corrupted the current-day plan still referencing the original task; missing `None` guard was a latent crash; manual `scheduled_time` re-parse duplicated logic already in `_parse_scheduled_time`. |
| **Decision** | **Adopted.** Immutable `replace()` + explicit `None`-date fallback shipped in `_create_next_occurrence()`. | Not adopted; borrowed only its plain-language docstring phrasing. |

**Which approach did you use in your final implementation and why?**

We shipped Claude's immutable design. Weekly rescheduling touches state that the
same-run schedule and conflict detector are still reading, so mutating the source
task (GPT-4o's default) would have produced stale plan entries and duplicate
conflicts. Cloning via `dataclasses.replace` with `is_completed=False` and a
`(due_date or date.today()) + timedelta(weeks=1)` interval keeps the original
intact, preserves the scheduled `HH:MM`, and correctly handles tasks that were
never assigned a `due_date`. This is exactly what `Task._create_next_occurrence()`
does today, and the round-trip is covered by the recurring-task tests.
