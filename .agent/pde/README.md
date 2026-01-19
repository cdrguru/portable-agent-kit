# The Paul Davis Experience (PDE) Engine

**Design**: A system that replaces willpower with architecture.

## Structure

* `MANIFEST.md`: The North Star. Update quarterly.
* `agents/`: Invokable personas (`@ruthless_prioritizer`, `@librarian`).
* `workflows/`: Automated habits (`daily_startup`, `brain_dump`).
* `state/`: The living memory (`active_tasks`, `metrics`).

## Quick Start

**Morning Routine:**

```bash
gemini -p "$(cat .pde/workflows/daily_startup.md)"
```

**New Idea / Intake:**

```bash
gemini -p "$(cat .pde/workflows/brain_dump.md)" "My idea..."
```

**Manual Agent Call:**

```bash
gemini -p "$(cat .pde/agents/ruthless_prioritizer.md)" "Should I buy a boat?"
```
