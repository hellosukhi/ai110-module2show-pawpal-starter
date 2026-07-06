from datetime import time

from pawpal_system import FeedingTask, MedicationTask, Owner, Pet, ScheduleItem, SchedulerEngine

try:
    from tabulate import tabulate
except ImportError:  # pragma: no cover - fallback for environments without tabulate
    tabulate = None


def build_demo_schedule():
    """Build a demo owner, pets, and scheduling scenario for local testing."""
    owner = Owner(name="Jordan", daily_time_budget_minutes=60)

    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=2)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    morning_medication = MedicationTask(
        task_id="med-1",
        title="Morning medicine",
        duration_minutes=10,
        base_priority=8,
        dosage="1 tablet",
        dosage_window="morning",
        scheduled_time="07:30",
        is_recurring=True,
        recurring_occurrences=2,
    )
    lunch_feeding = FeedingTask(
        task_id="feed-1",
        title="Lunch feeding",
        duration_minutes=8,
        base_priority=5,
        food_type="wet food",
        amount_grams=180,
        scheduled_time="12:00",
    )
    dinner_feeding = FeedingTask(
        task_id="feed-2",
        title="Dinner feeding",
        duration_minutes=15,
        base_priority=4,
        food_type="dry food",
        amount_grams=220,
        scheduled_time="19:00",
    )
    overlapping_feeding = FeedingTask(
        task_id="feed-3",
        title="Overlap feeding",
        duration_minutes=15,
        base_priority=5,
        food_type="wet food",
        amount_grams=180,
        scheduled_time="07:35",
    )
    same_time_feeding = FeedingTask(
        task_id="feed-4",
        title="Same-time feeding",
        duration_minutes=10,
        base_priority=6,
        food_type="dry food",
        amount_grams=180,
        scheduled_time="07:30",
    )

    engine = SchedulerEngine()
    next_medication = engine.mark_task_complete(morning_medication, pet=mochi)
    if next_medication is not None:
        mochi.add_task(next_medication)

    mochi.add_task(dinner_feeding)
    mochi.add_task(overlapping_feeding)
    mochi.add_task(morning_medication)
    luna.add_task(lunch_feeding)
    luna.add_task(same_time_feeding)

    plan = engine.generate_global_plan(owner)
    sorted_plan = sorted(
        plan,
        key=lambda item: item.task.scheduled_time_value or time(23, 59),
    )
    filtered_plan = engine.filter_schedule_items(sorted_plan, pet=mochi, include_completed=False)
    conflicts = engine.detect_conflicts(sorted_plan)
    return owner, sorted_plan, filtered_plan, conflicts


def _task_icon(task: object) -> str:
    """Return a user-friendly emoji for the task type."""
    if isinstance(task, MedicationTask):
        return "💊"
    if isinstance(task, FeedingTask):
        return "🥣"
    return "📝"


def _status_icon(task: object) -> str:
    """Return a status indicator for completed vs pending work."""
    return "✅" if getattr(task, "is_completed", False) else "⏳"


def _priority_badge(task: object) -> str:
    """Return a small priority label for display."""
    priority = getattr(task, "priority", None)
    if priority is None:
        return "[MEDIUM]"
    # TaskPriority is a str-Enum; use .value so we render "HIGH" not "TaskPriority.HIGH".
    priority_text = getattr(priority, "value", priority)
    return f"[{str(priority_text).upper()}]"


def _task_details(task: object) -> str:
    """Return a short task-specific detail string for table display."""
    if isinstance(task, MedicationTask):
        return f"Dosage: {task.dosage}" if task.dosage else "Medication"
    if isinstance(task, FeedingTask):
        return f"{task.food_type} ({task.amount_grams}g)" if task.food_type else "Feeding"
    return "—"


def format_schedule(owner: Owner, plan: list[ScheduleItem]) -> str:
    """Render the selected plan as a professional fancy_grid table."""
    lines = [
        "Today's Schedule",
        "================",
        f"Owner: {owner.name}",
        f"Daily budget: {owner.daily_time_budget_minutes} min",
        "",
    ]

    if not plan:
        lines.append("No tasks scheduled today.")
        return "\n".join(lines)

    headers = ["#", "Time", "Pet", "Type", "Task", "Duration", "Priority", "Details"]
    rows = []
    for index, item in enumerate(plan, start=1):
        pet = item.pet
        task = item.task
        rows.append(
            [
                index,
                task.scheduled_time_label,
                f"{pet.name} ({pet.species.value})",
                f"{_status_icon(task)} {_task_icon(task)}",
                task.title,
                f"{task.duration_minutes} min",
                _priority_badge(task),
                _task_details(task),
            ]
        )

    if tabulate is None:
        # Fallback to plain text when tabulate is unavailable.
        for row in rows:
            lines.append(
                f"{row[0]}. {row[1]} — {row[2]} | {row[3]} {row[4]} "
                f"({row[5]}) {row[6]} | {row[7]}"
            )
        return "\n".join(lines)

    lines.append(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    return "\n".join(lines)


def format_task_table(tasks: list[object]) -> str:
    """Return a simple CLI table of pending tasks when tabulate is available."""
    if tabulate is None:
        return ""

    rows = []
    for task in tasks:
        rows.append(
            [
                _status_icon(task),
                _task_icon(task),
                getattr(task, "scheduled_time_label", "Unscheduled"),
                task.title,
                getattr(task, "pet_name", "Unassigned"),
                f"{task.duration_minutes} min",
                _priority_badge(task),
            ]
        )

    return tabulate(
        rows,
        headers=["Status", "Type", "Time", "Task", "Pet", "Duration", "Priority"],
        tablefmt="fancy_grid",
    )


def format_debug_summary(owner: Owner, plan: list[ScheduleItem], filtered_plan: list[ScheduleItem], conflicts: list[dict]) -> str:
    """Summarize the generated plan, filtered view, and detected conflicts."""
    lines = [
        format_schedule(owner, plan),
        "",
        "Filtered for Mochi:",
        "-------------------",
    ]
    if not filtered_plan:
        lines.append("No tasks for Mochi.")
    else:
        for item in filtered_plan:
            lines.append(f"- {item.task.title} at {item.task.scheduled_time_label}")

    lines.extend(["", "Detected conflicts:", "------------------"])
    if not conflicts:
        lines.append("None")
    else:
        lines.append(f"Warning: {len(conflicts)} scheduling conflict(s) detected.")
        for conflict in conflicts:
            first = conflict["first"]
            second = conflict["second"]
            lines.append(
                f"- {first.task.title} vs {second.task.title} ({first.task.scheduled_time_label} to {second.task.scheduled_time_label})"
            )
    return "\n".join(lines)


if __name__ == "__main__":
    owner, plan, filtered_plan, conflicts = build_demo_schedule()
    engine = SchedulerEngine()
    all_tasks = [task for pet in owner.pets for task in pet.tasks]
    sorted_tasks = engine.sort_by_time(all_tasks)
    filtered_tasks = engine.filter_tasks(sorted_tasks, completed=False, pet_name="Mochi")

    print(format_debug_summary(owner, plan, filtered_plan, conflicts))
    print("\nSorted tasks by time:")
    print("---------------------")
    for task in sorted_tasks:
        print(f"- {_status_icon(task)} {task.scheduled_time_label} :: {task.title} ({task.pet_name or 'Unassigned'}) {_priority_badge(task)}")

    print("\nFiltered pending tasks for Mochi:")
    print("--------------------------------")
    if not filtered_tasks:
        print("No pending tasks for Mochi.")
    else:
        table_output = format_task_table(filtered_tasks)
        if table_output:
            print(table_output)
        else:
            for task in filtered_tasks:
                print(f"- {_status_icon(task)} {task.scheduled_time_label} :: {task.title}")
