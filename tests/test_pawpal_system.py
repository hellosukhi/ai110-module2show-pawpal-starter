import pytest

from pawpal_system import (
    FeedingTask,
    MedicationTask,
    Owner,
    Pet,
    SchedulerEngine,
    Task,
)


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
    assert contextual_tasks == [(first_pet, medication_task), (second_pet, feeding_task)]

    plan = SchedulerEngine().generate_global_plan(owner)
    assert plan == [(first_pet, medication_task)]
