# Workflow: Friction Audit

**Trigger:** Before any release, or when user feedback suggests pain points.

## Purpose

Systematically evaluate PACK against its North Star: zero friction coordination.

## Procedure

### 1. Fresh Eyes Test (15 min)

Pretend you've never seen PACK. Starting from the README:

- [ ] Can you understand what PACK does in 30 seconds?
- [ ] Can you install it in under 1 minute?
- [ ] Can you log your first handoff in under 2 minutes?

**If any answer is "no", stop and fix before continuing.**

### 2. Step Count Audit (10 min)

For each core workflow, count the steps:

| Workflow | Target Steps | Actual Steps | Pass? |
|----------|--------------|--------------|-------|
| Deploy to new repo | 1 | | |
| Start a session | 2 | | |
| Log a handoff | 1 | | |
| Resume from another agent | 2 | | |
| Run an audit | 1 | | |

**Any workflow over target = friction to fix.**

### 3. Error Recovery Test (10 min)

Deliberately break things and see if you can recover:

- [ ] Delete the task file - can you continue?
- [ ] Corrupt the log - is history preserved elsewhere?
- [ ] Run a command wrong - is the error message helpful?

### 4. Documentation Scan (5 min)

- [ ] Is any concept explained more than once? (Consolidate)
- [ ] Is any file referenced that doesn't exist? (Fix or remove)
- [ ] Are there warnings about "gotchas"? (Fix the gotcha instead)

### 5. Log Findings

```bash
# Add each finding to the friction log
echo "- [ ] <finding>" >> .pde/state/friction_log.md
```

## Output

Update `.pde/state/friction_log.md` with all findings.
Prioritize fixes before release.

## Frequency

- **Pre-release:** Required
- **Monthly:** Recommended
- **On user complaint:** Mandatory
