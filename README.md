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

## 🖥️ Sample Output

Running the terminal script prints a readable daily schedule like this:

```text
Today's Schedule
================
Owner: Jordan
Daily budget: 60 min

1. 07:30 — Mochi (dog)
   • Morning medicine (10 min)
   • Dosage: 1 tablet
2. 12:00 — Luna (cat)
   • Lunch feeding (8 min)
   • Food: wet food (180g)
3. 19:00 — Mochi (dog)
   • Dinner feeding (15 min)
   • Food: dry food (220g)
```

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

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
