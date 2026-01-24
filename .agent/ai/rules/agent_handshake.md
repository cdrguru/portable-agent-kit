# Agent Handshake Protocol

This document defines the coordination mechanisms (status markers, file locking, handoff triggers) used by the multi-agent system.

---

## 1. Shared State: Task File

The checklist in `tasks/todo.md` (or equivalent) serves as the **mutex** for work coordination.

### Status Indicators

| Marker | Meaning | Rule |
|--------|---------|------|
| `[ ]` | **Pending** | Available for any qualified agent to pick up |
| `[/]` | **In Progress** | LOCKED by an agent. Do not touch unless you are the owner |
| `[x]` | **Complete** | Verified and done |
| `[-]` | **Blocked** | Requires Human Director intervention |

### In-Progress Convention

When claiming a task, mark it with your agent name:

```markdown
[/] (Builder) Implement login component
```

---

## 2. Handoff Triggers

### Code -> Docs (Builder -> Docs Agent)

When Builder completes a feature:

1. Mark implementation task as `[x]`
2. Append/verify a documentation task exists:
   - `[ ] Document <FeatureName> in <DocFile>`

### Plan -> Code (Planner -> Builder)

When Planner updates the plan:

1. Planner writes the new steps to the task file
2. Planner notifies: "Plan updated. Ready for Builder."

### Review -> Merge (Reviewer -> Human Director)

When Reviewer approves:

1. Mark review task as `[x]`
2. Handoff to Human Director for merge approval

---

## 3. Conflict Resolution

If two agents attempt to edit the same file (other than the task file):

1. **Stop** - Do not proceed with the edit
2. **Revert** - Return to the last clean state
3. **Escalate** - Request Human Director arbitration
4. **Prevent** - Future task items should target disjoint file sets

---

## 4. Simplicity Audit

Before marking any task `[x]`, the agent must ask:

> "Did I make this as simple as possible? Did I remove unnecessary code?"

- **No** -> Refactor immediately before completing
- **Yes** -> Mark complete

---

## 5. Communication Protocol

### Required Fields in Every Handoff

| Field | Description |
|-------|-------------|
| `Agent` | Who is handing off |
| `Summary` | One-line description of what was done |
| `HandoffTo` | Who should pick up next |

### Optional Fields

| Field | Description |
|-------|-------------|
| `References` | File paths or URLs related to the work |
| `Tasks` | Follow-up items for the next agent |
| `Status` | Current state: ready, blocked, wip |
| `Context` | Category: setup, refactor, bugfix, feature |

---

## 6. File Ownership Guidelines

To minimize conflicts, follow these ownership patterns:

| Agent | Primary Ownership |
|-------|-------------------|
| Planner | `tasks/`, `todo/`, planning docs |
| Builder | `src/`, `lib/`, feature code |
| Reviewer | Test files, review comments |
| Docs | `docs/`, README files, inline comments |

---

*Protocol Version: 1.0.0 | Portable Agent Collaboration Kit*
