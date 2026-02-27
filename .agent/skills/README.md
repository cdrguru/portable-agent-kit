# Skills (Optional)

A skill is a repeatable workflow or playbook an agent can follow. Each skill
lives under `.agent/skills/` with a required `SKILL.md` plus optional resources.
Use `python3 .agent/tools/utilities/skills.py show <skill-name>` to print a
skill for easy copy/paste into an agent session.

## Layout

```text
.agent/skills/
  <skill-name>/
    SKILL.md
    scripts/ (optional)
    assets/ (optional)
    references/ (optional)
```

## SKILL.md schema (example)

```markdown
---
name: handoff-log-update
description: Append a structured entry to the handoff log when finishing work.
metadata:
  short-description: Append a handoff entry to the log
---

# Handoff Log Update

## When to use
Use when you need to record a handoff.

## Procedure
1. Collect the required fields.
2. Run the script with explicit flags.
3. Confirm the entry was appended.

## Inputs and outputs
- Inputs: agent, summary, tasks, references, handoff target
- Outputs: appended entry in the handoff log

## Constraints
- Append-only logs are never rewritten
- ASCII-only

## Examples
- $handoff-log-update
```

## Core constraints

- Append-only logs are never rewritten
- Human approval before risky operations
- ASCII-only
- Prefer dry-run flags when scripts write files

## Skills Index

| Skill | Description | Invocation |
| --- | --- | --- |
| handoff-log-update | Append a structured handoff entry to the log | $handoff-log-update |
| handoff-log-condense | Summarize recent handoff entries into a new file | $handoff-log-condense |
| session-bootstrap | Initialize a local session log from the template | $session-bootstrap |
| gemini-cli-init | Setup Gemini CLI as auditor | $gemini-cli-init |
| gemini-audit | Audit task via Gemini | $gemini-audit |
| claude-md-init | Generate CLAUDE.md for any repo | $claude-md-init |
| claude-code-init | Bootstrap Claude Code session with PACK context | $claude-code-init |
| claude-code-handoff | Record handoff from Claude Code to next agent | $claude-code-handoff |
| prompt-library-setup | Set up an organized prompt library with categories, catalog, and inbox | $prompt-library-setup |
| agentic-audit | Audit repo against 24-item agentic development checklist | $agentic-audit |
| skill-porter | Port skills from any AI assistant format to PACK | $skill-porter |
| session-to-templates | Mine prompt templates from AI coding sessions | $session-to-templates |
