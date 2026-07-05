# PawPal+ Project Reflection

## 1. System Design

+-----------------------------------+
|               Pet                 |
+-----------------------------------+
| - name: str                       |
| - species: str                    |
| - age: int                        |
| - health_flags: list[str]         |
+-----------------------------------+
| + add_health_flag(flag: str): void|
| + get_profile(): dict             |
+-----------------------------------+

+-------------------------------------+
|                Owner                |
+-------------------------------------+
| - name: str                         |
| - daily_time_budget: int            |
+-------------------------------------+
| + update_budget(mins: int): void    |
+-------------------------------------+

+-----------------------------------+
|          <<Abstract>>             |
|              Task                 |
+-----------------------------------+
| - task_id: str                    |
| - title: str                      |
| - duration: int                   |
| - base_priority: int              |
| - is_completed: bool              |
+-----------------------------------+
| + mark_complete(): void           |
| + calculate_urgency(): float [Abs]|
+-----------------------------------+
                  ^
                  | (Inheritance)
     +------------+------------+
     |                         |
+----+-------------------+ +---+--------------------+
|     MedicationTask     | |      FeedingTask       |
+------------------------+ +------------------------+
| - dosage: str          | | - food_type: str       |
| - dosage_window: str   | | - amount_grams: int    |
+------------------------+ +------------------------+
| + calculate_urgency()  | | + calculate_urgency()  |
+------------------------+ +------------------------+

+-----------------------------------+
|          SchedulerEngine          |
+-----------------------------------+
| - task_pool: list[Task]           |
+-----------------------------------+
| + add_task(task: Task): void      |
| + generate_daily_plan(            |
|     owner: Owner                  |
|   ): list[Task]                   |
+-----------------------------------+

**a. Initial design**

- Briefly describe your initial UML design.

My initial design maps a resource-constrained scheduling engine using a clean, decoupled three-layer architecture:

* **`Pet` & `Owner` (The State Layer):** Responsible for capturing static context. `Pet` holds biological constraints (age, species) and health-critical flags, while `Owner` manages global daily variables (total available care hours).
  
* **`Task` & Subclasses (The Domain Layer):** An abstract base class (`Task`) that defines core telemetry (duration, base priority, urgency). Concrete subclasses—such as `MedicationTask`, `FeedingTask`, and `ActivityTask`—override or extend these parameters to represent highly specific domain rules.
  
* **`SchedulerEngine` (The Orchestration Layer):** A pure service class responsible for running the optimization logic. It ingests the active task pool, filters them against the `Owner`'s daily time budget, resolves conflicts, and outputs the prioritized linear plan.

- What classes did you include, and what responsibilities did you assign to each?

My initial UML design models a resource-constrained scheduling engine via a decoupled, three-tier architecture to completely separate data state from the execution orchestration pipeline. 

* **`Pet` (State Layer)**
  * **Responsibility:** Encapsulates the biological profile and invariant constraints of the animal. It tracks properties like species and health flags required to validate downstream scheduling rules.

* **`Owner` (State Layer)**
  * **Responsibility:** Captures the operator context and manages global execution variables, specifically the total daily available time budget allocated for care tasks.

* **`Task` (Domain Layer)**
  * **Responsibility:** An abstract base class serving as the core data primitive. It defines the foundational interface for task telemetry, including temporal duration, base priority, and urgency metrics.

* **`MedicationTask` / `FeedingTask` / `ActivityTask` (Domain Layer)**
  * **Responsibility:** Concrete extensions of the base `Task` class that inject domain-specific parameters and validation rules (e.g., dosage strictness for medications vs. energy expenditure for activities).

* **`SchedulerEngine` (Orchestration Layer)**
  * **Responsibility:** A pure service class that executes the optimization pipeline. It ingests the active task pool, filters them against the `Owner`'s daily time budget, resolves scheduling conflicts, and synthesizes a prioritized, linear execution plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
