from datetime import date, timedelta

import pytest

from pawpal_system import (
    FeedingTask,
    MedicationTask,
    Owner,
    Pet,
    PetSpecies,
    ScheduleItem,
    Scheduler,
    SchedulerEngine,
    Task,
    TaskFrequency,
)


def test_task_completion():
    """Verify that calling mark_complete() mutates the task state to True."""
    # 1. Arrange
    task = FeedingTask(
        task_id="t-comp-1",
        title="Morning Kibble",
        duration_minutes=15,
        base_priority=5,
        food_type="dry food",
        amount_grams=150,
        scheduled_time="08:00",
    )

    # 2. Act
    assert task.is_completed is False, "Task should initialize as uncompleted."
    result = task.mark_complete()

    # 3. Assert
    assert task.is_completed is True, "Calling mark_complete() must set is_completed to True."
    assert result is None, "Non-recurring tasks should not create a new occurrence."


def test_mark_complete_creates_next_daily_occurrence():
    task = FeedingTask(
        task_id="feed-11",
        title="Daily brushing",
        duration_minutes=10,
        base_priority=3,
        food_type="dry food",
        amount_grams=150,
        scheduled_time="08:00",
        is_recurring=True,
        frequency="daily",
    )

    next_task = task.mark_complete()

    assert task.is_completed is True
    assert next_task is not None
    assert next_task.task_id == "feed-11-next"
    assert next_task.is_completed is False
    assert next_task.frequency is TaskFrequency.DAILY
    assert next_task.scheduled_time == "08:00"
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_task_addition_increments_count():
    """Verify that appending a task to a Pet increases its internal itinerary collection count."""
    # 1. Arrange
    pet = Pet(name="Mochi", species="dog", age=3)
    task = FeedingTask(
        task_id="t-add-1",
        title="Dinner feeding",
        duration_minutes=15,
        base_priority=4,
        food_type="dry food",
        amount_grams=220,
        scheduled_time="19:00",
    )

    # 2. Act & Assert
    assert len(pet.tasks) == 0, "Pet task collection should initialize empty."

    pet.add_task(task)

    assert len(pet.tasks) == 1, "Adding a task must increment the pet's task count by exactly 1."
    assert pet.tasks[0].task_id == "t-add-1", "The stored task must match the appended instance."


def test_task_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        Task(task_id="t1", title="Generic", duration_minutes=10, base_priority=3)


def test_medication_task_uses_custom_urgency_logic():
    task = MedicationTask(
        task_id="med-1",
        title="Medicine",
        duration_minutes=10,
        base_priority=5,
        dosage="1 tablet",
        dosage_window="morning",
    )

    assert task.calculate_urgency() > 0


def test_task_can_store_a_scheduled_time():
    task = FeedingTask(
        task_id="feed-1",
        title="Dinner",
        duration_minutes=10,
        base_priority=4,
        food_type="dry food",
        amount_grams=200,
        scheduled_time="19:00",
    )

    assert task.scheduled_time == "19:00"


def test_scheduler_selects_tasks_that_fit_budget():
    owner = Owner(name="Jordan", daily_time_budget_minutes=30)
    pet = Pet(name="Mochi", species="dog", age=3)

    short_task = MedicationTask(
        task_id="med-1",
        title="Medicine",
        duration_minutes=10,
        base_priority=8,
        dosage="1 pill",
        dosage_window="morning",
    )
    long_task = FeedingTask(
        task_id="feed-1",
        title="Dinner",
        duration_minutes=25,
        base_priority=4,
        food_type="dry food",
        amount_grams=200,
    )

    plan = SchedulerEngine().generate_plan(owner, pet, [long_task, short_task])

    assert plan == [short_task]


def test_scheduler_uses_pet_health_context_for_urgency():
    owner = Owner(name="Jordan", daily_time_budget_minutes=30)
    pet = Pet(
        name="Mochi",
        species="dog",
        age=3,
        health_flags=["pain", "needs monitoring"],
    )

    medication_task = MedicationTask(
        task_id="med-2",
        title="Pain relief",
        duration_minutes=10,
        base_priority=1,
        dosage="1 tablet",
        dosage_window="evening",
    )
    feeding_task = FeedingTask(
        task_id="feed-2",
        title="Dinner",
        duration_minutes=10,
        base_priority=8,
        food_type="wet food",
        amount_grams=200,
    )

    plan = SchedulerEngine().generate_plan(owner, pet, [feeding_task, medication_task])

    assert plan[0] == medication_task


def test_owner_context_and_global_plan_use_all_registered_tasks():
    owner = Owner(name="Jordan", daily_time_budget_minutes=10)
    first_pet = Pet(name="Mochi", species="dog", age=3)
    second_pet = Pet(name="Luna", species="cat", age=2)

    medication_task = MedicationTask(
        task_id="med-3",
        title="Medicine",
        duration_minutes=10,
        base_priority=8,
        dosage="1 pill",
        dosage_window="morning",
    )
    feeding_task = FeedingTask(
        task_id="feed-3",
        title="Dinner",
        duration_minutes=8,
        base_priority=4,
        food_type="wet food",
        amount_grams=200,
    )

    first_pet.add_task(medication_task)
    second_pet.add_task(feeding_task)
    owner.add_pet(first_pet)
    owner.add_pet(second_pet)

    contextual_tasks = owner.get_all_tasks_contextual()
    assert contextual_tasks == [
        ScheduleItem(first_pet, medication_task),
        ScheduleItem(second_pet, feeding_task),
    ]

    plan = SchedulerEngine().generate_global_plan(owner)
    assert plan == [ScheduleItem(first_pet, medication_task)]


def test_pet_species_and_task_frequency_are_normalized_to_enums():
    pet = Pet(name="Mochi", species="DOG", age=3)
    task = FeedingTask(
        task_id="feed-4",
        title="Breakfast",
        duration_minutes=10,
        base_priority=4,
        food_type="dry food",
        amount_grams=200,
        frequency="daily",
    )

    assert pet.species is PetSpecies.DOG
    assert task.frequency is TaskFrequency.DAILY


def test_scheduler_sorts_tasks_by_time_and_keeps_unscheduled_last():
    scheduler = SchedulerEngine()
    late_task = FeedingTask(
        task_id="feed-5",
        title="Late feed",
        duration_minutes=10,
        base_priority=4,
        food_type="dry food",
        amount_grams=200,
        scheduled_time="12:00",
    )
    early_task = MedicationTask(
        task_id="med-4",
        title="Early medicine",
        duration_minutes=10,
        base_priority=8,
        dosage="1 tablet",
        dosage_window="morning",
        scheduled_time="07:30",
    )
    unscheduled_task = FeedingTask(
        task_id="feed-6",
        title="Unscheduled",
        duration_minutes=10,
        base_priority=3,
        food_type="wet food",
        amount_grams=150,
    )

    ordered = scheduler.sort_tasks_by_time([late_task, unscheduled_task, early_task])

    assert ordered == [early_task, late_task, unscheduled_task]


def test_scheduler_sort_by_time_uses_a_lambda_key_for_hh_mm_strings():
    scheduler = SchedulerEngine()
    late_task = FeedingTask(
        task_id="feed-9",
        title="Late feed",
        duration_minutes=10,
        base_priority=4,
        food_type="dry food",
        amount_grams=200,
        scheduled_time="12:00",
    )
    early_task = MedicationTask(
        task_id="med-7",
        title="Early medicine",
        duration_minutes=10,
        base_priority=8,
        dosage="1 tablet",
        dosage_window="morning",
        scheduled_time="07:30",
    )

    ordered = scheduler.sort_by_time([late_task, early_task])

    assert ordered == [early_task, late_task]


def test_scheduler_filters_tasks_by_completion_status_and_pet_name():
    scheduler = SchedulerEngine()
    completed_task = FeedingTask(
        task_id="feed-10",
        title="Completed feed",
        duration_minutes=10,
        base_priority=4,
        food_type="dry food",
        amount_grams=200,
        scheduled_time="09:00",
    )
    completed_task.mark_complete()
    pending_task = MedicationTask(
        task_id="med-8",
        title="Pending medicine",
        duration_minutes=10,
        base_priority=8,
        dosage="1 tablet",
        dosage_window="morning",
        scheduled_time="10:00",
    )
    pending_task.pet_name = "Mochi"
    completed_task.pet_name = "Mochi"

    filtered = scheduler.filter_tasks(
        [completed_task, pending_task],
        completed=False,
        pet_name="Mochi",
    )

    assert filtered == [pending_task]


def test_scheduler_filters_schedule_items_by_pet_and_completion_status():
    scheduler = SchedulerEngine()
    owner = Owner(name="Jordan", daily_time_budget_minutes=30)
    first_pet = Pet(name="Mochi", species="dog", age=3)
    second_pet = Pet(name="Luna", species="cat", age=2)

    first_task = FeedingTask(
        task_id="feed-7",
        title="Dinner",
        duration_minutes=10,
        base_priority=4,
        food_type="dry food",
        amount_grams=200,
    )
    second_task = MedicationTask(
        task_id="med-5",
        title="Medicine",
        duration_minutes=10,
        base_priority=8,
        dosage="1 pill",
        dosage_window="morning",
    )
    second_task.mark_complete()

    first_pet.add_task(first_task)
    second_pet.add_task(second_task)
    owner.add_pet(first_pet)
    owner.add_pet(second_pet)

    filtered = scheduler.filter_schedule_items(
        owner.get_all_tasks_contextual(),
        pet=first_pet,
        include_completed=False,
    )

    assert filtered == [ScheduleItem(first_pet, first_task)]


def test_scheduler_expands_recurring_tasks_and_detects_conflicts():
    scheduler = SchedulerEngine()
    pet = Pet(name="Mochi", species="dog", age=3)
    recurring_task = FeedingTask(
        task_id="feed-8",
        title="Breakfast",
        duration_minutes=10,
        base_priority=4,
        food_type="dry food",
        amount_grams=200,
        scheduled_time="08:00",
        is_recurring=True,
        recurring_occurrences=2,
    )
    conflicting_task = MedicationTask(
        task_id="med-6",
        title="Medicine",
        duration_minutes=15,
        base_priority=8,
        dosage="1 pill",
        dosage_window="morning",
        scheduled_time="08:05",
    )

    expanded = scheduler.expand_recurring_tasks([recurring_task], max_occurrences=2)
    conflicts = scheduler.detect_conflicts([
        ScheduleItem(pet, recurring_task),
        ScheduleItem(pet, conflicting_task),
    ])

    assert len(expanded) == 2
    assert conflicts


def test_scheduler_detects_same_time_conflicts_for_different_pets():
    scheduler = Scheduler()
    first_pet = Pet(name="Mochi", species="dog", age=3)
    second_pet = Pet(name="Luna", species="cat", age=2)
    first_task = MedicationTask(
        task_id="med-9",
        title="Morning medicine",
        duration_minutes=10,
        base_priority=8,
        dosage="1 tablet",
        dosage_window="morning",
        scheduled_time="08:00",
    )
    second_task = FeedingTask(
        task_id="feed-12",
        title="Breakfast feeding",
        duration_minutes=10,
        base_priority=4,
        food_type="dry food",
        amount_grams=200,
        scheduled_time="08:00",
    )

    conflicts = scheduler.detect_conflicts([
        ScheduleItem(first_pet, first_task),
        ScheduleItem(second_pet, second_task),
    ])

    assert len(conflicts) == 1
    assert conflicts[0]["first"].task.task_id == "med-9"
    assert conflicts[0]["second"].task.task_id == "feed-12"
