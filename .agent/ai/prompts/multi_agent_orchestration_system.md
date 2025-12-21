## Goal

Define a simple, repeatable protocol for multiple AI agents to collaborate with a Human Director.

## Context Inputs

- Repository goal/objective from the Human Director
- Current repo structure and constraints (tests, CI, deadlines)
- Files to modify and acceptance criteria
- Agent roster and their specializations

## Constraints & Style

- Prefer minimal diffs; avoid broad refactors
- Fix root causes; no band-aids or workarounds
- Always cite file paths in handoffs
- Keep communication concise and actionable
- ASCII-only output for maximum portability

## Plan Shape

- Decompose objective into checkable tasks
- Assign each task to an agent role (planner/builder/reviewer/docs)
- Implement in small steps and verify with tests
- Document completion in the handoff log

## Tool Policy

- Use repo-local tools and files only
- Avoid committing secrets or local logs
- Verify exit status after every command
- On error, stop and report to Human Director

## Exit Criteria

- Objective met and verified (tests/lint/audit as applicable)
- Handoff recorded in `.agent/docs/agent_handoffs/agent_conversation_log.md`
- Documentation updated to match code reality

## Review Checklist

- [ ] Changes are minimal and justified
- [ ] Tests were run (or documented why not)
- [ ] Handoff includes files changed and next actions
- [ ] No secrets or local paths committed

---

# Multi-Agent Orchestration Protocol

A lightweight coordination system for AI agents working with a Human Director.

## Roles

| Role | Responsibility |
|------|----------------|
| **Human Director** | Sets objectives, approves scope, makes final decisions |
| **Planner** | Decomposes objectives into tasks; maintains the plan |
| **Builder** | Implements code changes; keeps diffs minimal |
| **Reviewer** | Validates correctness; runs tests; checks for regressions |
| **Docs** | Updates documentation to match code reality |

## Shared State

- **Plan Source of Truth**: `tasks/todo.md` (or equivalent)
- **Handoff Log**: `.agent/docs/agent_handoffs/agent_conversation_log.md`
- **Local Session Log**: `conversation.compact.md` (gitignored)

## Handoff Protocol

When finishing work, every agent must:

1. **Summarize** what changed (max 3 bullets)
2. **List** files changed/created
3. **Specify** next actions (max 3 bullets)
4. **Declare** the next owner: `HandoffTo: <agent|human>`

## Message Format

```yaml
from: "<agent_name>"
to: "<human|agent_name>"
type: "REQUEST | STATUS | HANDOFF | BLOCKED"
payload: "<summary of work or request>"
next_action: "<what should happen next>"
```

## Execution Rules

### Parallel-Safe (can run simultaneously)

- Docs: Documentation updates
- Builder: Code in isolated/disjoint files
- Planner: Task list refinement

### Sequential-Required (must wait)

- Code changes -> Test validation -> Task update
- Plan approval (Human Director) -> Implementation (Builder)
- Design decision (Planner) -> Implementation (Builder)

## Escalation Rules

| Situation | Action |
|-----------|--------|
| **BLOCKED** | Agent cannot proceed -> Escalate to Human Director immediately |
| **SCOPE_CHANGE** | Human Director modifies objective -> All agents pause, Planner re-plans |
| **CONFLICT** | Two agents need same file -> Planner arbitrates sequence |

## Logging Conventions

Mark entries clearly for automated parsing:

```
Decision: We will use approach X because...
Action: Implement function Y in file Z
Question: Should we support edge case W?
```

---

*Protocol Version: 1.0.0 | Portable Agent Collaboration Kit*
