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

### PACK-Native Skills

| Skill | Description | Invocation |
| --- | --- | --- |
| agentic-audit | Audit repo against 24-item agentic development checklist | $agentic-audit |
| claude-code-handoff | Record handoff from Claude Code to next agent | $claude-code-handoff |
| claude-code-init | Bootstrap Claude Code session with PACK context | $claude-code-init |
| claude-md-init | Generate CLAUDE.md for any repo | $claude-md-init |
| gemini-audit | Audit task via Gemini | $gemini-audit |
| gemini-cli-init | Setup Gemini CLI as auditor | $gemini-cli-init |
| handoff-log-condense | Summarize recent handoff entries into a new file | $handoff-log-condense |
| handoff-log-update | Append a structured handoff entry to the log | $handoff-log-update |
| prompt-library-setup | Set up an organized prompt library with categories, catalog, and inbox | $prompt-library-setup |
| session-bootstrap | Initialize a local session log from the template | $session-bootstrap |
| session-to-templates | Mine prompt templates from AI coding sessions | $session-to-templates |
| skill-porter | Port skills from any AI assistant format to PACK | $skill-porter |

### Google Workspace Skills

| Skill | Description | Invocation |
| --- | --- | --- |
| gws-calendar | Google Calendar: Manage calendars and events | $gws-calendar |
| gws-calendar-agenda | Google Calendar: Show upcoming events | $gws-calendar-agenda |
| gws-calendar-insert | Google Calendar: Create a new event | $gws-calendar-insert |
| gws-docs | Read and write Google Docs | $gws-docs |
| gws-docs-write | Google Docs: Append text to a document | $gws-docs-write |
| gws-drive | Google Drive: Manage files, folders, shared drives | $gws-drive |
| gws-drive-upload | Google Drive: Upload a file with metadata | $gws-drive-upload |
| gws-gmail | Gmail: Send, read, and manage email | $gws-gmail |
| gws-gmail-forward | Gmail: Forward a message | $gws-gmail-forward |
| gws-gmail-reply | Gmail: Reply to a message | $gws-gmail-reply |
| gws-gmail-send | Gmail: Send an email | $gws-gmail-send |
| gws-gmail-triage | Gmail: Show unread inbox summary | $gws-gmail-triage |
| gws-shared | gws CLI: Shared auth, flags, and output patterns | $gws-shared |
| gws-sheets | Google Sheets: Read and write spreadsheets | $gws-sheets |
| gws-sheets-append | Google Sheets: Append a row | $gws-sheets-append |
| gws-sheets-read | Google Sheets: Read values | $gws-sheets-read |
| gws-workflow | Google Workflow: Cross-service productivity | $gws-workflow |
| gws-workflow-email-to-task | Google Workflow: Email to Google Tasks | $gws-workflow-email-to-task |
| gws-workflow-meeting-prep | Google Workflow: Meeting prep | $gws-workflow-meeting-prep |
| gws-workflow-standup-report | Google Workflow: Standup summary | $gws-workflow-standup-report |
| gws-workflow-weekly-digest | Google Workflow: Weekly digest | $gws-workflow-weekly-digest |

### Persona Skills

| Skill | Description | Invocation |
| --- | --- | --- |
| persona-exec-assistant | Manage schedule, inbox, and communications | $persona-exec-assistant |
| persona-sales-ops | Track deals, schedule calls, client comms | $persona-sales-ops |

### Recipe Skills

| Skill | Description | Invocation |
| --- | --- | --- |
| recipe-draft-email-from-doc | Draft email body from a Google Doc | $recipe-draft-email-from-doc |
| recipe-find-free-time | Find meeting slots via free/busy query | $recipe-find-free-time |
| recipe-find-large-files | Identify large Drive files consuming quota | $recipe-find-large-files |
| recipe-log-deal-update | Append deal status to a tracking sheet | $recipe-log-deal-update |

### Utility Skills

| Skill | Description | Invocation |
| --- | --- | --- |
| agent-skills-guide | Generate HTML reference of all agents and skills | $agent-skills-guide |
| redact-pii | Scan files for sensitive identifiers and redact | $redact-pii |
| security-audit | 3-part security and configuration audit | $security-audit |
| session-wrapup | End-of-session: survey, commit, push, verify | $session-wrapup |
| tax-return-cleanup | Clean PDF-converted IRS forms into markdown | $tax-return-cleanup |
