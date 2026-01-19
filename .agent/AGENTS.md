# Agent Collaboration Playbook

A **portable, model-agnostic** playbook for multi-agent collaboration coordinated by a Human Director.

---

## Quick Start

1. **Human Director** sets objectives and approves plans
2. Agents coordinate via:
   - `.agent/docs/agent_handoffs/agent_conversation_log.md` (append-only handoff log)
   - `conversation.compact.md` (local-only condensed log; gitignored)
3. All agents load: `ai/prompts/multi_agent_orchestration_system.md`

---

## System Instruction

All agents should load and follow the shared coordination protocol:

```
ai/prompts/multi_agent_orchestration_system.md
```

---

## Files That Matter

| File | Purpose |
|------|---------|
| `AGENTS.md` | This file; who does what, how to hand off |
| `ai/prompts/multi_agent_orchestration_system.md` | Shared orchestration protocol |
| `ai/rules/agent_handshake.md` | Lock/handoff mechanics |
| `.agent/docs/agent_handoffs/agent_conversation_log.md` | Shared append-only handoff log |
| `conversation.compact.md` | Local session log (gitignored) |

---

## Communication Conventions

Use these prefixes in handoffs to ensure clarity:

- `Decision: ...` - A commitment or approval made
- `Action: ...` - A concrete next step to take
- `Question: ...` - Something the Human Director must answer

Keep handoffs **short and actionable**:

- 3 bullets for what changed
- 3 bullets for what's next
- Always include file paths

---

## Registered Agents

> **Customize these for your project.** The roles below are templates.

### Agent: codex (Planner / Orchestrator)

- **Purpose**: Maintain the plan and coordinate work across agents
- **Owns**: Task breakdowns, acceptance criteria, sequencing, handoffs
- **Rules**:
  - Delegate execution to ag
  - Route detailed clarifications/writing to hp
  - Minimize Human Director typing; prefer y/no questions

### Agent: ag (Builder / Executor)

- **Purpose**: Implement code changes with minimal diffs; run verification
- **Note**: ag can be "Antigravity or Copilot Agent" (same role)
- **Rules**:
  - Default to safe execution without waiting
  - If a decision is required, ask a single y/no question
  - If requirements are missing, request hp to gather them

### Agent: hp (Human Proxy / Clarifier)

- **Purpose**: Gather detailed requirements and produce a short paste-back
- **Rules**:
  - Ask only what is needed to unblock
  - Prefer y/no questions
  - Provide: Decision, Assumptions, Requirements, Acceptance criteria, paste-back

### Agent: Planner

- **Purpose**: Break objectives into checkable tasks and acceptance criteria
- **Owns**: `tasks/` or `todo/` (single source of truth for the plan)
- **Triggers**: New user request, completed milestone, scope change

### Agent: Builder

- **Purpose**: Implement code changes; keep diffs minimal and focused
- **Owns**: Feature branches, implementation PRs
- **Triggers**: `[ ]` items assigned to "Builder" in task list

### Agent: Reviewer

- **Purpose**: Verify correctness; run tests; audit for regressions
- **Triggers**: Completion of builder tasks, before merge

### Agent: Docs

- **Purpose**: Keep documentation aligned with code reality
- **Triggers**: Completion of code tasks, documentation gaps identified

---

## Handoff Contract

When finishing work, append a log entry:

```bash
python3 tools/utilities/update_agent_conversation_log.py \
  --agent builder \
  --summary "Implemented feature X; tests passing" \
  --task "Review files A/B" \
  --handoff reviewer \
  --reference "src/feature_x.py" \
  --reference "tests/test_feature_x.py"
```

### Required Fields

| Field | Description |
|-------|-------------|
| `--agent` | Name of the agent completing work |
| `--summary` | One-line summary of what was done |
| `--handoff` | Who should pick up next (agent name or "human") |

### Optional Fields

| Field | Description |
|-------|-------------|
| `--task` | Follow-up task (repeatable) |
| `--reference` | File path or URL (repeatable) |
| `--context` | Short label: setup, refactor, bugfix |
| `--status` | Status indicator: ready, blocked, wip |

---

## Task Status Indicators

Use these in `tasks/todo.md` to coordinate:

| Marker | Meaning |
|--------|---------|
| `[ ]` | **Pending** - Available for pickup |
| `[/]` | **In Progress** - Locked by an agent |
| `[x]` | **Complete** - Verified and done |
| `[-]` | **Blocked** - Requires Human Director |

Convention for in-progress: `[/] (AgentName) Task description...`

---

## Conflict Resolution

If two agents need to edit the same file:

1. **Stop** - Do not proceed
2. **Revert** - Return to last clean state
3. **Escalate** - Request Human Director arbitration
4. **Prevent** - Task items should target disjoint file sets

---

## Simplicity Audit

Before marking any task `[x]`, ask:

> "Did I make this as simple as possible? Did I remove unnecessary code?"

- **No** -> Refactor immediately
- **Yes** -> Mark complete

---

## PDE (Paul Davis Experience) Agents

The following agents provide strategic focus and knowledge management capabilities.

### Agent: ruthless-prioritizer

```yaml
id: ruthless-prioritizer
label: Ruthless Prioritizer
description: >
  A focus protection agent that aggressively filters tasks against the MANIFEST.md North Star goals.
  Uses a binary KEEP/KILL decision tree to eliminate distractions and "shiny objects."
primary_user_role: owner

entrypoint:
  type: code
  path: .agent/ai/prompts/agent_profiles/ruthless_prioritizer.md
  notes: System 2 reasoning agent with explicit alignment checks.

knowledge_sources:
  - name: North Star Manifest
    description: Obsessional goals, constraints, and tie-breaking heuristics.
    location: .agent/MANIFEST.md

tasks:
  - id: filter-tasks
    label: Filter Task List
    description: >
      Analyzes tasks against the North Star goals and returns a prioritized table
      with KEEP/KILL status and P0/P1/P2 priority levels.
    trigger_examples:
      - "@ruthless_prioritizer 'Fix login bug vs research new framework'"
      - "Prioritize my task list"
    required_inputs:
      - Task list or brain dump
    output_format: markdown-table
    related_knowledge:
      - North Star Manifest
```

### Agent: librarian

```yaml
id: librarian
label: The Librarian
description: >
  A knowledge compounding agent that extracts reusable assets from completed work
  and links them to existing knowledge. Categorizes insights into Code Patterns,
  Decision Frameworks, Prompts, Processes, and Failure Lessons.
primary_user_role: owner

entrypoint:
  type: code
  path: .agent/ai/prompts/agent_profiles/librarian.md
  notes: Triggered when work is completed successfully.

knowledge_sources:
  - name: Knowledge Base
    description: Atomic notes organized by category.
    location: .agent/knowledge/

tasks:
  - id: extract-knowledge
    label: Extract Knowledge Asset
    description: >
      Analyzes completed work, identifies the core "Unit of Knowledge,"
      and creates an atomic note in the knowledge base.
    trigger_examples:
      - "@librarian 'We solved the auth issue with retry logic'"
      - "That worked - save this pattern"
    required_inputs:
      - Description of what was learned/solved
    output_format: markdown
    related_knowledge:
      - Knowledge Base
```

---

## PDE Workflows

| Workflow | Purpose | Location |
|----------|---------|----------|
| **Daily Startup** | Morning ritual to set the "One Thing" and flight plan | `.agent/workflows/daily_startup.md` |
| **Brain Dump** | Intake raw ideas, validate against North Star, structure into tasks | `.agent/workflows/brain_dump.md` |

## PDE State Files

| File | Purpose |
|------|---------|
| `.agent/state/active_tasks.md` | Single source of truth for todos |
| `.agent/state/inbox.md` | Brain dump inbox for raw ideas |
| `.agent/state/metrics.md` | PDE metrics dashboard |
| `.agent/MANIFEST.md` | North Star goals and constraints |

---

*Template Version: 1.0.0 | Portable Agent Collaboration Kit*
