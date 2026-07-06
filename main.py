from pawpal_system import FeedingTask, MedicationTask, Owner, Pet, SchedulerEngine


def build_demo_schedule():
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

    mochi.add_task(morning_medication)
    luna.add_task(lunch_feeding)
    mochi.add_task(dinner_feeding)

    plan = SchedulerEngine().generate_global_plan(owner)
    sorted_plan = sorted(plan, key=lambda item: item[1].scheduled_time or "99:99")
    return owner, sorted_plan


def format_schedule(owner: Owner, plan: list[tuple[Pet, object]]) -> str:
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

    for index, (pet, task) in enumerate(plan, start=1):
        time_label = task.scheduled_time or "Unscheduled"
        lines.append(f"{index}. {time_label} — {pet.name} ({pet.species})")
        lines.append(f"   • {task.title} ({task.duration_minutes} min)")

        if isinstance(task, MedicationTask):
            lines.append(f"   • Dosage: {task.dosage}")
        elif isinstance(task, FeedingTask):
            lines.append(f"   • Food: {task.food_type} ({task.amount_grams}g)")

    return "\n".join(lines)


if __name__ == "__main__":
    owner, plan = build_demo_schedule()
    print(format_schedule(owner, plan))
