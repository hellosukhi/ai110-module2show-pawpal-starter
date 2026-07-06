# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

PawPal+ uses a lightweight scheduling engine to turn pet-care data into a practical daily plan:

- Budget-aware planning: the scheduler only selects tasks that fit within the owner’s daily time budget.
- Urgency-based prioritization: feeding and medication tasks are scored by priority, duration, and pet-health context.
- Sorting by time: tasks can be ordered chronologically by scheduled time, making the plan easier to follow.
- Conflict warnings: the planner detects same-time and overlapping tasks so the user can resolve double-booking issues.
- Daily and weekly recurrence: recurring tasks can be expanded into future occurrences for planning.
- Pet-aware filtering: the system can filter tasks by pet name or completion state for focused review.

## 🎨 Presentation & Formatting

PawPal+ ships a polished presentation layer across both the CLI and the Streamlit UI:

- **`tabulate`** (`tablefmt="fancy_grid"`) — the CLI in [main.py](main.py) renders the
  daily plan as a bordered grid with per-task-type icons (💊 for `MedicationTask`,
  🥣 for `FeedingTask`) and a `⏳`/`✅` completion indicator.
- **Streamlit native status components** — the UI in [app.py](app.py) maps each
  explicit `TaskPriority` enum to a high-visibility banner: `st.error` for **HIGH**,
  `st.warning` for **MEDIUM**, and `st.info` for **LOW**, alongside the existing
  hybrid `st.metric` dashboard.

Run the CLI demo to see the formatted grid:

```bash
python main.py
```

Example `fancy_grid` terminal output:

```text
Today's Schedule
================
Owner: Jordan
Daily budget: 60 min

╒═════╤════════╤═════════════╤════════╤═══════════════════╤════════════╤════════════╤══════════════════╕
│   # │ Time   │ Pet         │ Type   │ Task              │ Duration   │ Priority   │ Details          │
╞═════╪════════╪═════════════╪════════╪═══════════════════╪════════════╪════════════╪══════════════════╡
│   1 │ 07:30  │ Mochi (dog) │ ⏳ 💊   │ Morning medicine  │ 10 min     │ [MEDIUM]   │ Dosage: 1 tablet │
├─────┼────────┼─────────────┼────────┼───────────────────┼────────────┼────────────┼──────────────────┤
│   2 │ 07:30  │ Mochi (dog) │ ⏳ 💊   │ Morning medicine  │ 10 min     │ [MEDIUM]   │ Dosage: 1 tablet │
├─────┼────────┼─────────────┼────────┼───────────────────┼────────────┼────────────┼──────────────────┤
│   3 │ 07:30  │ Mochi (dog) │ ⏳ 💊   │ Morning medicine  │ 10 min     │ [MEDIUM]   │ Dosage: 1 tablet │
├─────┼────────┼─────────────┼────────┼───────────────────┼────────────┼────────────┼──────────────────┤
│   4 │ 07:30  │ Luna (cat)  │ ⏳ 🥣   │ Same-time feeding │ 10 min     │ [MEDIUM]   │ dry food (180g)  │
├─────┼────────┼─────────────┼────────┼───────────────────┼────────────┼────────────┼──────────────────┤
│   5 │ 07:35  │ Mochi (dog) │ ⏳ 🥣   │ Overlap feeding   │ 15 min     │ [MEDIUM]   │ wet food (180g)  │
╘═════╧════════╧═════════════╧════════╧═══════════════════╧════════════╧════════════╧══════════════════╛
```

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 💾 Persistence workflow

PawPal+ now keeps its owner, pet, and task data between application runs by writing a lightweight JSON snapshot to data.json.

How it works:
- The domain model in [pawpal_system.py](pawpal_system.py) now provides custom serialization hooks for tasks, pets, and owners.
- The Streamlit UI in [app.py](app.py) loads the saved state from data.json when the app starts and saves it again after changes such as adding pets or tasks.
- A regression test in [tests/test_pawpal_system.py](tests/test_pawpal_system.py) verifies that a full owner/pet/task tree can be written to disk and restored correctly.

Files modified for persistence:
- [pawpal_system.py](pawpal_system.py)
- [app.py](app.py)
- [tests/test_pawpal_system.py](tests/test_pawpal_system.py)
- [README.md](README.md)

If data.json is missing, the app starts with a fresh default owner profile and creates the file on the next save.

## Demo Walkthrough

PawPal+ provides a simple but practical workflow for managing pet care through the Streamlit interface:

1. Main UI features
   - Edit the owner profile and daily time budget from the sidebar.
   - Add one or more pets with species and age information.
   - Create feeding or medication tasks with duration, priority, and task-specific details.
   - Generate an optimized daily care schedule and review conflict warnings before finalizing the plan.

2. Example workflow
   - Add a pet such as Mochi.
   - Create a medication task with a scheduled time and a feeding task for the same day.
   - Click the schedule button to view the generated plan, including task ordering, time usage, and any conflicts.

3. Scheduler behaviors shown
   - Tasks are sorted by urgency and then arranged by time when a schedule is generated.
   - Conflicts are flagged when tasks share the same time or overlap.
   - Recurring tasks can expand into additional occurrences for planning.
   - Only tasks that fit within the available budget are included in the final plan.

4. Sample CLI output

```text
Today's Schedule
================
Owner: Jordan
Daily budget: 60 min

1. 07:30 — Mochi (dog)
   • Morning medicine (10 min)
   • Dosage: 1 tablet
2. 07:30 — Mochi (dog)
   • Morning medicine (10 min)
   • Dosage: 1 tablet
3. 07:30 — Luna (cat)
   • Same-time feeding (10 min)
   • Food: dry food (180g)
4. 12:00 — Luna (cat)
   • Lunch feeding (8 min)
   • Food: wet food (180g)

Detected conflicts:
------------------
Warning: 6 scheduling conflict(s) detected.
```

Optional screenshots or a short demo video can be added later for human reviewers, but the walkthrough above and the CLI example make the app easy to evaluate.

## 🔼 Priority-based scheduling

The scheduler now ranks tasks by priority level before time, so a high-priority medication reminder can be placed ahead of a lower-priority feeding task even if the latter is earlier in the day.

Example CLI output:

```text
Priority-based plan
===================
1. 07:00 — Mochi (dog)
   • High priority medicine (10 min) [HIGH]
2. 08:00 — Mochi (dog)
   • Medium priority breakfast (10 min) [MEDIUM]
3. 09:00 — Mochi (dog)
   • Low priority check-in (10 min) [LOW]
```

This makes it easier to surface urgent care tasks first while still preserving a clear chronological order within the same priority tier.

## 🧪 Testing PawPal+

Run the full test suite with:

```bash
python -m pytest
```

These tests cover the core scheduling and task-management behaviors in the system, including task completion and recurring-task behavior, pet and owner context handling, scheduling under time-budget constraints, urgency calculation, sorting and filtering, conflict detection, and recurring-task expansion.

Example successful test output:

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.0, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/star/ai110-module2show-pawpal-starter
configfile: pytest.ini
plugins: anyio-4.13.0
collected 19 items

tests/test_pawpal_system.py ...................                          [100%]

============================== 19 passed in 0.03s ==============================
```

Confidence Level: ★★★★★

## 📐 Smarter Scheduling

The scheduling engine now supports a few practical planning behaviors that make the daily plan more useful:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting behavior | `Scheduler.sort_tasks()`, `Scheduler.sort_by_time()`, `Scheduler.sort_tasks_contextual()` | Tasks are prioritized by effective urgency, shorter duration, and, when relevant, chronological time order. |
| Filtering behavior | `Scheduler.filter_tasks()`, `Scheduler.filter_schedule_items()` | The planner can filter tasks by completion state and by pet name, making it easy to focus on active or pet-specific work. |
| Conflict detection logic | `Scheduler.detect_conflicts()`, `Scheduler._tasks_conflict()`, `Scheduler._conflict_reason()` | The scheduler identifies overlapping or identical scheduled times so potential double-booking is visible. |
| Recurring task logic | `Scheduler.expand_recurring_tasks()`, `Scheduler.expand_recurring_schedule_items()` | Recurring tasks can be expanded into multiple instances for planning, including daily and weekly behavior through the task model. |

