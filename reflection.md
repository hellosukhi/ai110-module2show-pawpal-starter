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

Yes. During implementation, I tightened the model in two ways so the design matched the scheduler’s real behavior more closely:

1. **Explicit pet-task relationship:** I added an optional pet reference to each task and made the scheduler attach the current pet context when planning. This closes a gap in the original design, where the pet object was available to the engine but not meaningfully connected to the task objects being ranked.

2. **Health-aware urgency scoring:** The original design treated urgency as a generic numeric property, but the implementation now uses pet health flags to boost medically sensitive tasks when a pet is under stress or needs monitoring. That change was important because a medication task for a pet in pain should be prioritized more aggressively than a routine feeding task, even if the base priority is lower.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff in the current scheduler is that conflict detection is intentionally lightweight: it flags tasks when they share the exact same start time or overlap in time, but it does not attempt a full optimization or rescheduling pass. This keeps the implementation simple, fast, and easy to understand, which is appropriate for a small pet-care planning demo. In a more complex real-world system, a richer approach might suggest alternative slots, rebalance priorities, or resolve conflicts automatically, but that would add more logic and complexity than this project needs.

---

## 3. AI Collaboration

**a. How you used AI**

I used the AI coding assistant as a pair-programming partner rather than as an autopilot. The most effective features were its ability to help me turn a high-level design into concrete class responsibilities, generate small implementation steps that fit a larger architecture, and explain tradeoffs in plain language when I was deciding between simpler and more sophisticated approaches. It was especially useful for debugging, refactoring, and writing tests once the core structure was already in place.

The most helpful prompts were architecture-oriented questions such as: “What is the cleanest way to separate state, domain logic, and orchestration?” and “How can I keep this scheduler maintainable while still making the urgency logic feel intelligent?” I also found it valuable when I asked the assistant to compare two implementation options and justify the tradeoffs, because that helped me stay aligned with a senior-level design mindset rather than just chasing a quick solution.

Using separate chat sessions for different phases was very helpful. I kept one session focused on system design and UML decisions, another on implementation details, and a later one for testing and debugging. That made it easier to preserve context, avoid mixing concerns, and keep each phase intellectually clean.

**b. Judgment and verification**

One example of an AI suggestion I rejected was the idea of pushing more scheduling logic down into each task subclass and making the engine rely on a larger set of conditional rules. That would have made the system more fragmented and harder to reason about. I modified the suggestion by keeping task classes focused on their data and domain-specific attributes while allowing the scheduler to remain the single orchestrator for urgency, filtering, conflicts, and plan generation.

I evaluated the suggestion by checking whether it preserved the architecture’s boundaries and whether it would still be easy to test. I verified the final approach by running the test suite and confirming that the behavior remained clear and predictable rather than becoming overly clever.

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

I am most satisfied with how I kept the system architecture coherent while still benefiting from the speed and flexibility of AI assistance. The scheduler feels like a well-bounded service with clear responsibilities, and that is exactly the kind of design discipline I wanted to preserve.

**b. What you would improve**

If I had another iteration, I would deepen the scheduler’s scoring model and make its reasoning more explicit so the plan could explain itself with even more confidence. I would also consider adding a bit more sophistication around constraint handling, while still avoiding unnecessary complexity.

**c. Key takeaway**

The most important lesson was that being the lead architect means setting the structure first and then using AI as a force multiplier rather than a substitute for judgment. My preference for senior-level top-down architecture and bottom-up rigor meant I needed to keep the assistant anchored to clean abstractions, strong boundaries, and testable behavior. The strongest results came when I treated the AI as a collaborator for acceleration and exploration, but still made the final architectural calls myself.
