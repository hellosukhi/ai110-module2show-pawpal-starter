"""Core logic layer for the PawPal+ pet care scheduling app."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Pet:
    """Represents the pet whose care tasks are being planned."""

    name: str
    species: str
    age: int
    health_flags: List[str] = field(default_factory=list)

    def add_health_flag(self, flag: str) -> None:
        """Add a health-related flag to the pet profile."""
        if flag and flag not in self.health_flags:
            self.health_flags.append(flag)

    def get_profile(self) -> Dict[str, object]:
        """Return a simple dictionary describing the pet profile."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "health_flags": list(self.health_flags),
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


@dataclass
class Task(ABC):
    """Abstract base class for a pet care task."""

    task_id: str
    title: str
    duration_minutes: int
    base_priority: int
    pet: Optional["Pet"] = None
    is_completed: bool = False

    def __post_init__(self) -> None:
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than zero")
        if self.base_priority < 0:
            raise ValueError("base_priority must be non-negative")

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.is_completed = True

    def _health_context_boost(self, pet: Optional[Pet]) -> float:
        """Return a small urgency boost when a pet has health concerns."""
        resolved_pet = self.pet or pet
        if resolved_pet is None:
            return 0.0

        normalized_flags = {flag.lower() for flag in resolved_pet.health_flags}
        if any(
            token in normalized_flags
            for token in {"pain", "critical", "monitoring", "urgent", "injury", "sick"}
        ):
            return 30.0 if isinstance(self, MedicationTask) else 6.0
        if any(token in normalized_flags for token in {"sensitive", "diet", "recovery"}):
            return 2.0
        return 0.0

    @abstractmethod
    def calculate_urgency(self) -> float:
        """Force concrete subclasses to implement custom urgency logic."""


@dataclass
class MedicationTask(Task):
    """A medication task with a dosage and administration window."""

    dosage: str = ""
    dosage_window: str = ""

    def calculate_urgency(self) -> float:
        return (self.base_priority * 4.0) - (self.duration_minutes * 0.25)


@dataclass
class FeedingTask(Task):
    """A feeding task with food type and amount."""

    food_type: str = ""
    amount_grams: int = 0

    def calculate_urgency(self) -> float:
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

    def _effective_urgency(self, task: Task, pet: Optional[Pet]) -> float:
        """Combine the task's base urgency with any pet-health context."""
        if task.pet is None and pet is not None:
            task.pet = pet
        return task.calculate_urgency() + task._health_context_boost(pet)
