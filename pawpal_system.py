"""Core logic layer for the PawPal+ pet care scheduling app."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union


class PetSpecies(str, Enum):
    """Allowed pet species values for the scheduling domain."""

    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    RABBIT = "rabbit"
    OTHER = "other"

    @classmethod
    def from_value(cls, value: Union["PetSpecies", str]) -> "PetSpecies":
        """Normalize string input into a validated enum member."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            normalized_value = value.strip().lower()
            for member in cls:
                if member.value == normalized_value:
                    return member
        raise ValueError(f"Unsupported pet species: {value}")


class TaskFrequency(str, Enum):
    """Supported cadence values for scheduled tasks."""

    DAILY = "daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as-needed"

    @classmethod
    def from_value(cls, value: Union["TaskFrequency", str]) -> "TaskFrequency":
        """Normalize string input into a validated enum member."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            normalized_value = value.strip().lower()
            for member in cls:
                if member.value == normalized_value:
                    return member
        raise ValueError(f"Unsupported task frequency: {value}")


_HEALTH_CONTEXT_FLAG_GROUPS = {
    "high": {"pain", "critical", "monitoring", "urgent", "injury", "sick"},
    "moderate": {"sensitive", "diet", "recovery"},
}
_HEALTH_CONTEXT_BOOSTS = {
    "high": {"medication": 30.0, "feeding": 6.0},
    "moderate": {"medication": 2.0, "feeding": 2.0},
}


@dataclass
class Pet:
    """Represents the pet whose care tasks are being planned."""

    name: str
    species: Union[PetSpecies, str]
    age: int
    health_flags: List[str] = field(default_factory=list)
    tasks: List["Task"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize species values to the constrained enum type."""
        self.species = PetSpecies.from_value(self.species)

    def add_task(self, task: "Task") -> None:
        """Assign a care task directly to this pet's itinerary."""
        if task not in self.tasks:
            task.pet_name = self.name
            self.tasks.append(task)

    def add_health_flag(self, flag: str) -> None:
        """Add a health-related flag to the pet profile."""
        if flag and flag not in self.health_flags:
            self.health_flags.append(flag)

    def get_profile(self) -> Dict[str, object]:
        """Return a simple dictionary describing the pet profile."""
        return {
            "name": self.name,
            "species": self.species.value,
            "age": self.age,
            "health_flags": list(self.health_flags),
            "task_count": len(self.tasks),
        }


@dataclass
class Owner:
    """Represents the owner who manages the pet and daily care time."""

    name: str
    daily_time_budget_minutes: int = 0
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Attach a pet to this owner."""
        if pet not in self.pets:
            self.pets.append(pet)

    def update_time_budget(self, minutes: int) -> None:
        """Adjust the owner's available daily care time."""
        self.daily_time_budget_minutes = max(0, minutes)

    def get_all_tasks_contextual(self) -> List["ScheduleItem"]:
        """Return all tasks associated with the owner's pets, preserving pet context."""
        aggregated_context: List[ScheduleItem] = []
        for pet in self.pets:
            for task in pet.tasks:
                aggregated_context.append(ScheduleItem(pet=pet, task=task))
        return aggregated_context


@dataclass(frozen=True)
class ScheduleItem:
    """Immutable transport object for pet-task plan entries."""

    pet: Pet
    task: "Task"


@dataclass
class Task(ABC):
    """Abstract base class for a pet care task."""

    task_id: str
    title: str
    duration_minutes: int
    base_priority: int
    pet_name: Optional[str] = None
    is_completed: bool = False
    scheduled_time: Optional[str] = None
    due_date: Optional[date] = None
    frequency: Union[TaskFrequency, str] = TaskFrequency.DAILY
    is_recurring: bool = False
    recurring_occurrences: int = 1
    scheduled_time_value: Optional[time] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate task creation parameters and normalize scheduling metadata."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than zero")
        if self.base_priority < 0:
            raise ValueError("base_priority must be non-negative")

        self.frequency = TaskFrequency.from_value(self.frequency)
        if self.recurring_occurrences < 1:
            raise ValueError("recurring_occurrences must be at least 1")
        self.scheduled_time_value = self._parse_scheduled_time(self.scheduled_time)
        if self.scheduled_time_value is not None:
            self.scheduled_time = self.scheduled_time_value.strftime("%H:%M")

    def mark_complete(self) -> Optional["Task"]:
        """Mark the task as completed and return the next recurring instance if applicable."""
        self.is_completed = True
        if not self.is_recurring:
            return None

        if self.frequency == TaskFrequency.DAILY:
            delta = timedelta(days=1)
        elif self.frequency == TaskFrequency.WEEKLY:
            delta = timedelta(weeks=1)
        else:
            return None

        return self._create_next_occurrence(delta)

    def _create_next_occurrence(self, delta: timedelta) -> "Task":
        """Return a new task instance representing the next occurrence."""
        next_task_id = f"{self.task_id}-next"
        next_due_date = (self.due_date or date.today()) + delta
        return replace(
            self,
            task_id=next_task_id,
            is_completed=False,
            due_date=next_due_date,
        )

    @property
    def due_date_label(self) -> str:
        """Return a human-readable due date label."""
        if self.due_date is None:
            return "No due date"
        return self.due_date.isoformat()

    @property
    def time(self) -> Optional[str]:
        """Return the task's scheduled time as a string for convenient sorting."""
        return self.scheduled_time

    def _minutes_since_midnight(self) -> Optional[int]:
        """Return the task's scheduled time as minutes after midnight."""
        if self.scheduled_time_value is None:
            return None
        return (self.scheduled_time_value.hour * 60) + self.scheduled_time_value.minute

    @property
    def scheduled_time_label(self) -> str:
        """Return the human-readable scheduled time label."""
        if self.scheduled_time_value is None:
            return "Unscheduled"
        return self.scheduled_time_value.strftime("%H:%M")

    def _parse_scheduled_time(self, scheduled_time: Optional[str]) -> Optional[time]:
        """Parse a HH:MM time string into a datetime.time object."""
        if scheduled_time in (None, ""):
            return None
        if isinstance(scheduled_time, time):
            return scheduled_time
        if not isinstance(scheduled_time, str):
            raise TypeError("scheduled_time must be a string or datetime.time")

        components = scheduled_time.strip().split(":")
        if len(components) != 2:
            raise ValueError("scheduled_time must be in HH:MM format")

        hour_text, minute_text = components
        try:
            hour = int(hour_text)
            minute = int(minute_text)
        except ValueError as exc:
            raise ValueError("scheduled_time must contain numeric hour and minute values") from exc

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("scheduled_time must be a valid time")

        return time(hour=hour, minute=minute)

    def _health_context_boost(self, pet: Optional[Pet]) -> float:
        """Return a small urgency boost when a pet has health concerns."""
        if pet is None:
            return 0.0

        normalized_flags = {flag.lower() for flag in pet.health_flags}
        for group_name, flag_set in _HEALTH_CONTEXT_FLAG_GROUPS.items():
            if normalized_flags.intersection(flag_set):
                task_type = "medication" if isinstance(self, MedicationTask) else "feeding"
                return _HEALTH_CONTEXT_BOOSTS[group_name][task_type]
        return 0.0

    @abstractmethod
    def calculate_base_urgency(self) -> float:
        """Compute the task's urgency independent of pet-health context."""

    def calculate_urgency(self) -> float:
        """Return the task urgency using the base urgency calculation."""
        return self.calculate_base_urgency()


@dataclass
class MedicationTask(Task):
    """A medication task with a dosage and administration window."""

    dosage: str = ""
    dosage_window: str = ""

    def calculate_base_urgency(self) -> float:
        """Compute urgency for medication tasks."""
        return (self.base_priority * 4.0) - (self.duration_minutes * 0.25)


@dataclass
class FeedingTask(Task):
    """A feeding task with food type and amount."""

    food_type: str = ""
    amount_grams: int = 0

    def calculate_base_urgency(self) -> float:
        """Compute urgency for feeding tasks."""
        return (self.base_priority * 3.0) - (self.duration_minutes * 0.2)


@dataclass
class SchedulerEngine:
    """Builds a simple daily care plan from owner, pet, and task data."""

    def generate_plan(
        self,
        owner: Owner,
        pet: Pet,
        tasks: List[Task],
    ) -> List[Task]:
        """Return a sorted list of tasks that fit within the owner's time budget."""
        available_minutes = owner.daily_time_budget_minutes
        selected_tasks: List[Task] = []
        total_minutes = 0

        for task in self.sort_tasks(tasks, pet):
            if task.is_completed:
                continue
            if total_minutes + task.duration_minutes <= available_minutes:
                selected_tasks.append(task)
                total_minutes += task.duration_minutes

        return selected_tasks

    def generate_global_plan(self, owner: Owner) -> List[ScheduleItem]:
        """Retrieve tasks from the owner's pets and build a budget-aware global plan."""
        available_minutes = owner.daily_time_budget_minutes
        selected_plan: List[ScheduleItem] = []
        total_minutes = 0

        contextual_tasks = self.expand_recurring_schedule_items(owner.get_all_tasks_contextual())
        for item in self.sort_tasks_contextual(contextual_tasks):
            if item.task.is_completed:
                continue
            if total_minutes + item.task.duration_minutes <= available_minutes:
                selected_plan.append(item)
                total_minutes += item.task.duration_minutes

        return selected_plan

    def sort_tasks(self, tasks: List[Task], pet: Optional[Pet] = None) -> List[Task]:
        """Sort tasks by urgency descending and then by shorter duration first."""
        return sorted(
            tasks,
            key=lambda task: (
                -self._effective_urgency(task, pet),
                task.duration_minutes,
                task.title,
            ),
        )

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks chronologically by HH:MM time, leaving unscheduled tasks at the end."""
        return sorted(
            tasks,
            key=lambda task: (
                self._task_time_sort_key(task),
                task.title,
            ),
        )

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Backward-compatible wrapper for sorting tasks chronologically."""
        return self.sort_by_time(tasks)

    def filter_tasks(
        self,
        tasks: List[Task],
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Filter tasks by completion state and/or pet name."""
        normalized_pet_name = None
        if isinstance(pet_name, str) and pet_name.strip():
            normalized_pet_name = pet_name.strip().lower()

        filtered_tasks: List[Task] = []
        for task in tasks:
            if completed is not None and task.is_completed != completed:
                continue
            if normalized_pet_name is not None:
                task_pet_name = None
                if isinstance(task.pet_name, str) and task.pet_name.strip():
                    task_pet_name = task.pet_name.strip().lower()
                if task_pet_name != normalized_pet_name:
                    continue
            filtered_tasks.append(task)
        return filtered_tasks

    def filter_schedule_items(
        self,
        contextual_tasks: List[ScheduleItem],
        pet: Optional[Union[Pet, str]] = None,
        include_completed: bool = False,
    ) -> List[ScheduleItem]:
        """Filter contextual tasks by pet and completion status."""
        filtered_items: List[ScheduleItem] = []
        for item in contextual_tasks:
            if pet is not None:
                pet_name = pet.name if isinstance(pet, Pet) else pet
                if item.pet.name != pet_name:
                    continue
            if item.task.is_completed and not include_completed:
                continue
            filtered_items.append(item)
        return filtered_items

    def expand_recurring_tasks(self, tasks: List[Task], max_occurrences: int = 3) -> List[Task]:
        """Create repeated task instances for recurring tasks."""
        expanded_tasks: List[Task] = []
        for task in tasks:
            if not task.is_recurring:
                expanded_tasks.append(task)
                continue

            occurrence_count = max(1, min(task.recurring_occurrences, max_occurrences))
            for occurrence in range(occurrence_count):
                if occurrence == 0:
                    expanded_tasks.append(task)
                else:
                    expanded_tasks.append(
                        replace(
                            task,
                            task_id=f"{task.task_id}-{occurrence + 1}",
                            is_completed=False,
                        )
                    )
        return expanded_tasks

    def expand_recurring_schedule_items(
        self, contextual_tasks: List[ScheduleItem], max_occurrences: int = 3
    ) -> List[ScheduleItem]:
        """Expand recurring tasks into schedule items while preserving pet context."""
        expanded_items: List[ScheduleItem] = []
        for item in contextual_tasks:
            expanded_tasks = self.expand_recurring_tasks([item.task], max_occurrences=max_occurrences)
            for expanded_task in expanded_tasks:
                expanded_items.append(ScheduleItem(pet=item.pet, task=expanded_task))
        return expanded_items

    def detect_conflicts(self, contextual_tasks: List[ScheduleItem]) -> List[Dict[str, object]]:
        """Report conflicts when two scheduled tasks share the same clock time or overlap."""
        conflicts: List[Dict[str, object]] = []
        active_items = [
            item for item in contextual_tasks if not item.task.is_completed and item.task.scheduled_time_value is not None
        ]

        for index, first_item in enumerate(active_items):
            for second_item in active_items[index + 1 :]:
                if self._tasks_conflict(first_item.task, second_item.task):
                    conflicts.append(
                        {
                            "first": first_item,
                            "second": second_item,
                            "reason": self._conflict_reason(first_item.task, second_item.task),
                        }
                    )
        return conflicts

    def sort_tasks_contextual(self, contextual_tasks: List[ScheduleItem]) -> List[ScheduleItem]:
        """Sort contextual pet-task pairs by effective urgency and duration."""
        return sorted(
            contextual_tasks,
            key=lambda item: (
                -self._effective_contextual_urgency(item.pet, item.task),
                item.task.duration_minutes,
                item.task.title,
                item.pet.name,
            ),
        )

    def _task_time_sort_key(self, task: Task) -> tuple[int, int, int]:
        """Return a sort key that places scheduled tasks first and uses HH:MM ordering."""
        task_time = getattr(task, "time", None)
        if task_time is None:
            task_time = getattr(task, "scheduled_time", None)

        if isinstance(task_time, time):
            return (0, task_time.hour, task_time.minute)

        if isinstance(task_time, str):
            components = task_time.strip().split(":")
            if len(components) == 2:
                try:
                    return (0, int(components[0]), int(components[1]))
                except ValueError:
                    pass

        return (1, 23, 59)

    def _tasks_conflict(self, first_task: Task, second_task: Task) -> bool:
        """Return True when two tasks share the same scheduled time or overlap."""
        if first_task.scheduled_time_value is None or second_task.scheduled_time_value is None:
            return False

        first_start = self._minutes_from_time(first_task.scheduled_time_value)
        second_start = self._minutes_from_time(second_task.scheduled_time_value)
        first_end = first_start + first_task.duration_minutes
        second_end = second_start + second_task.duration_minutes
        if first_start == second_start:
            return True
        return first_start < second_end and second_start < first_end

    def _conflict_reason(self, first_task: Task, second_task: Task) -> str:
        """Describe whether the conflict is caused by an identical start time or an overlap."""
        if first_task.scheduled_time_value is None or second_task.scheduled_time_value is None:
            return "overlapping scheduled time"
        if self._minutes_from_time(first_task.scheduled_time_value) == self._minutes_from_time(second_task.scheduled_time_value):
            return "same scheduled time"
        return "overlapping scheduled time"

    def _minutes_from_time(self, scheduled_time: time) -> int:
        """Convert a datetime.time to minutes after midnight."""
        return (scheduled_time.hour * 60) + scheduled_time.minute

    def _effective_urgency(self, task: Task, pet: Optional[Pet]) -> float:
        """Combine the task's base urgency with any pet-health context."""
        if pet is not None:
            task.pet_name = pet.name
        return task.calculate_urgency() + task._health_context_boost(pet)

    def mark_task_complete(self, task: Task, pet: Optional[Pet] = None) -> Optional[Task]:
        """Mark a task complete and attach the next recurring occurrence to a pet if provided."""
        next_task = task.mark_complete()
        if next_task is not None and pet is not None:
            pet.add_task(next_task)
        return next_task

    def _effective_contextual_urgency(self, pet: Pet, task: Task) -> float:
        """Combine the task's urgency and the pet's health context for global planning."""
        task.pet_name = pet.name
        return task.calculate_urgency() + task._health_context_boost(pet)


class Scheduler(SchedulerEngine):
    """Backward-compatible public scheduler interface."""

    pass
