from datetime import time

from pawpal_system import FeedingTask, MedicationTask, Owner, Pet, ScheduleItem, SchedulerEngine


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


def format_schedule(owner: Owner, plan: list[ScheduleItem]) -> str:
    """Render a human-readable schedule from the selected plan items."""
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

    for index, item in enumerate(plan, start=1):
        pet = item.pet
        task = item.task
        time_label = task.scheduled_time_label
        lines.append(f"{index}. {time_label} — {pet.name} ({pet.species.value})")
        lines.append(f"   • {task.title} ({task.duration_minutes} min)")

        if isinstance(task, MedicationTask):
            lines.append(f"   • Dosage: {task.dosage}")
        elif isinstance(task, FeedingTask):
            lines.append(f"   • Food: {task.food_type} ({task.amount_grams}g)")

    return "\n".join(lines)


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
        print(f"- {task.scheduled_time_label} :: {task.title} ({task.pet_name or 'Unassigned'})")

    print("\nFiltered pending tasks for Mochi:")
    print("--------------------------------")
    if not filtered_tasks:
        print("No pending tasks for Mochi.")
    else:
        for task in filtered_tasks:
            print(f"- {task.scheduled_time_label} :: {task.title}")
