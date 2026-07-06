import uuid

import streamlit as st

from pawpal_system import FeedingTask, MedicationTask, Owner, Pet, SchedulerEngine

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")

st.markdown(
    """
This view now uses the backend classes from the logic layer so your UI creates real
owner, pet, and task objects that persist during the session.
"""
)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", daily_time_budget_minutes=60)

if "scheduler" not in st.session_state:
    st.session_state.scheduler = SchedulerEngine()

owner = st.session_state.owner
scheduler = st.session_state.scheduler

st.sidebar.header("Owner profile")
owner.name = st.sidebar.text_input("Owner name", value=owner.name, key="owner_name_input")
owner.update_time_budget(
    int(
        st.sidebar.number_input(
            "Daily time budget (minutes)",
            min_value=0,
            max_value=480,
            value=owner.daily_time_budget_minutes,
            key="budget_input",
        )
    )
)

st.subheader("Add a pet")
with st.expander("Create a pet profile", expanded=True):
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
    species = st.selectbox("Species", ["dog", "cat", "other"], key="pet_species_input")
    age = st.number_input("Age", min_value=0, max_value=30, value=3, key="pet_age_input")

    if st.button("Add pet", key="add_pet_button"):
        new_pet = Pet(name=pet_name.strip() or "Unnamed pet", species=species, age=int(age))
        owner.add_pet(new_pet)
        st.session_state.owner = owner
        st.success(f"Added {new_pet.name} to {owner.name}'s care plan.")

st.divider()

st.subheader("Your pets")
if owner.pets:
    for pet in owner.pets:
        with st.container():
            st.write(f"- {pet.name} ({pet.species}, age {pet.age})")
            if pet.tasks:
                for task in pet.tasks:
                    st.caption(f"  • {task.title} ({task.duration_minutes} min)")
            else:
                st.caption("  • No tasks yet")
else:
    st.info("No pets yet. Add one above to start building a plan.")

st.divider()

st.subheader("Add a task")
if owner.pets:
    selected_pet_name = st.selectbox(
        "Choose a pet",
        [pet.name for pet in owner.pets],
        key="task_pet_select",
    )
    selected_pet = next(pet for pet in owner.pets if pet.name == selected_pet_name)

    task_type = st.selectbox("Task type", ["feeding", "medication"], key="task_type_select")
    task_title = st.text_input("Task title", value="Meal time", key="task_title_input")
    duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=240, value=10, key="task_duration_input"
    )
    priority = st.number_input("Priority", min_value=0, max_value=10, value=5, key="task_priority_input")

    if task_type == "feeding":
        food_type = st.text_input("Food type", value="dry food", key="food_type_input")
        amount_grams = st.number_input(
            "Amount (grams)", min_value=1, max_value=1000, value=200, key="amount_input"
        )
        if st.button("Add task", key="add_feeding_task_button"):
            task = FeedingTask(
                task_id=uuid.uuid4().hex,
                title=task_title.strip() or "Feeding",
                duration_minutes=int(duration),
                base_priority=int(priority),
                food_type=food_type,
                amount_grams=int(amount_grams),
            )
            selected_pet.add_task(task)
            st.session_state.owner = owner
            st.success(f"Added {task.title} for {selected_pet.name}.")
    else:
        dosage = st.text_input("Dosage", value="1 tablet", key="dosage_input")
        dosage_window = st.text_input("Window", value="morning", key="dosage_window_input")
        if st.button("Add task", key="add_medication_task_button"):
            task = MedicationTask(
                task_id=uuid.uuid4().hex,
                title=task_title.strip() or "Medication",
                duration_minutes=int(duration),
                base_priority=int(priority),
                dosage=dosage,
                dosage_window=dosage_window,
            )
            selected_pet.add_task(task)
            st.session_state.owner = owner
            st.success(f"Added {task.title} for {selected_pet.name}.")
else:
    st.info("Add a pet first so you can attach tasks to it.")

st.divider()

st.subheader("Build schedule")
if st.button("Generate schedule", key="generate_schedule_button"):
    if not owner.pets or not any(pet.tasks for pet in owner.pets):
        st.info("Add at least one pet and one task before generating a schedule.")
    else:
        plan = scheduler.generate_global_plan(owner)
        if not plan:
            st.warning("No tasks fit within the current daily time budget.")
        else:
            st.success("Here is the current plan:")
            for pet, task in plan:
                st.write(f"- {pet.name}: {task.title} ({task.duration_minutes} min)")
