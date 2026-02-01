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

If a task matches a skill, follow the relevant SKILL.md procedure under `.agent/skills/`.

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

## Prompt Attribution & Clarification Protocol

When a prompt passes through interpretation layers (speech → transcription → AI rewrite → executing agent), each layer can introduce errors. This protocol prevents agents from executing confidently on compounded misinterpretations.

### Prompt Origin Block

When an AI agent rewrites or interprets a human prompt, include this block immediately after the Goal heading:

> **Prompt Origin:** [Source description]
> **Interpretation Confidence:** [High | Medium | Low]
> **Clarification Recommended:** [Yes/No — if Yes, list specific unclear points]

**Source descriptions** (use the most specific that applies):

| Tag | Meaning |
| --- | ------- |
| `Human-authored (direct text)` | Typed by human, no interpretation layer |
| `Interpreted from human speech-to-text` | Transcribed speech, may contain errors |
| `AI-generated (model: X)` | Written entirely by an AI agent |
| `AI-rewritten from human speech-to-text (model: X)` | AI interpreted transcribed speech |

### Clarification Triggers

**MUST ask before executing if:**

- Prompt Origin indicates speech-to-text AND Interpretation Confidence is Medium or Low
- Instructions contain logical contradictions
- Key terms are ambiguous (e.g., "run them again" without a clear antecedent)
- Scope is unclear (affects 1 file vs many files)

**SHOULD ask before executing if:**

- Prompt was AI-rewritten and you disagree with the interpretation
- You're about to make destructive changes (delete, overwrite, force-push)
- Direction seems uncertain and the task has broad scope

### Example: AI-Rewritten Prompt

> **Prompt Origin:** AI-rewritten from human speech-to-text (GitHub Copilot, Claude Opus 4.5)
> **Interpretation Confidence:** Medium
> **Clarification Recommended:** Yes — "run them again" is ambiguous. Does "them" refer to the tests or the scripts?

### Example: Direct Human Prompt

Direct human-typed prompts with clear instructions do not require a Prompt Origin block. If you add one:

> **Prompt Origin:** Human-authored (direct text)
> **Interpretation Confidence:** High
> **Clarification Recommended:** No

---

*Protocol Version: 1.1.0 | Portable Agent Collaboration Kit*
