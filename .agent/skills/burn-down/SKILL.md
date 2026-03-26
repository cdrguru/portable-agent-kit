---
name: burn-down
description: Use when starting an end-of-week or end-of-cycle session with remaining tokens/time to spend productively before reset, or when the user provides a prioritized task backlog to work through autonomously
metadata:
  short-description: Autonomously burn through a prioritized task backlog before token/time reset
---

# Burn Down

Work through a prioritized task backlog autonomously, maximizing value delivered before a token or time budget expires. Commits after every task so interruption at any point leaves the user better off.

## When to use

- User says they have X hours or Y% tokens remaining before weekly reset
- User provides a task backlog and wants autonomous execution
- End-of-week "use it or lose it" sessions
- Any time-boxed autonomous work sprint

## Inputs

- **Budget**: Time remaining and/or token % remaining (e.g., "15h 54m, 60% of Max plan")
- **Task backlog**: Ordered list of tasks, highest priority first. Each task should be a concrete, completable unit of work.
- **Repos/workspaces**: Which directories or repos to work in (defaults to cwd)

## Procedure

### 1. Assess and plan (fast -- under 2 minutes)

Parse the user's budget and backlog. Classify each task:

| Size | Description | Guideline |
|------|-------------|-----------|
| S | Single-file edit, config change, small fix | < 10% context |
| M | Multi-file feature, refactor, skill creation | 10-25% context |
| L | Cross-repo change, new system, deep research | 25-50% context |

Flag any task sized L or larger -- these risk consuming the whole session. Ask the user whether to attempt them or break them down.

Create a TodoWrite list from the backlog with size estimates.

### 2. Set phase boundaries

Map the user's budget to phases. Use token % as the primary constraint (time is secondary -- context fills before clock runs out in most sessions):

| Phase | Context range | Strategy |
|-------|--------------|----------|
| **Sprint** | 0-60% | Full-speed execution. Use parallel agents for independent tasks. Take on M and L tasks. |
| **Steady** | 60-80% | Continue execution but only S and M tasks. No new L tasks. |
| **Wind-down** | 80-90% | Finish in-flight work only. Commit everything. Update PROGRESS.md. |
| **Stop** | 90%+ | No new work. Final commit, session-wrapup, report to user. |

If the user's session is already partway through (e.g., "session at 30%"), shift boundaries accordingly.

### 3. Execute tasks in priority order

For each task:

1. Mark it `in_progress` in TodoWrite
2. Do the work
3. **Commit immediately** after completion -- never batch commits across tasks
4. Mark it `completed` in TodoWrite
5. Append a one-line entry to PROGRESS.md (create if it doesn't exist):
   ```
   - [x] <task name> -- <what was done> (<timestamp>)
   ```

**Parallel execution**: If two or more S/M tasks are independent (different files/repos), dispatch them as parallel agents. This is the single biggest throughput multiplier.

**Skip rules**: If a task is blocked, taking more than ~30 minutes of wall time with no progress, or requires information you don't have, skip it:
```
- [ ] <task name> -- SKIPPED: <reason>
```
Move to the next task. Do not spin.

### 4. Monitor and shift phases

You cannot read session % programmatically. Use these heuristics:

- **Count completed tasks**: If you've finished several M-sized tasks, you're likely past 40% context
- **Conversation length**: Long back-and-forth with many tool calls = high context usage
- **Compression warnings**: If you see system messages about context compression, you're in wind-down territory -- stop starting new tasks

When you estimate you've entered a new phase, announce it:
> Shifting to **Steady** phase -- focusing on smaller tasks only.

### 5. Wind down and report

When you reach wind-down phase:

1. Finish any in-flight task and commit
2. Update PROGRESS.md with final status of all tasks
3. Run session-wrapup if available
4. Present a summary to the user:

```
## Burn-down complete

**Completed**: N tasks
**Skipped**: N tasks (with reasons)
**Remaining**: N tasks (carry forward to next session)

### What got done
- Task A -- committed in abc1234
- Task B -- committed in def5678

### Carry-forward backlog
1. Task X (was next in queue)
2. Task Y (skipped: blocked on Z)
```

The carry-forward list is the user's starting point for their next session.

## Constraints

- **Never start a task you can't meaningfully finish** -- prefer completing 5 tasks over starting 8
- **Commit after every task** -- this is non-negotiable; uncommitted work is lost work
- **Priority order is sacred** -- do not reorder tasks for convenience unless the user approves
- **No exploratory rabbit holes** -- if research exceeds 10 minutes without a clear path, skip and note why
- **Respect repo boundaries** -- don't mix commits across repos; use session-wrapup conventions
- **Don't over-communicate** -- brief status at phase transitions, not after every file edit

## Examples

```
User: I have 15 hours and 60% of my Claude Max left. Here's what I need done:

1. Add the burn-down skill to the library
2. Fix the login redirect bug in the dashboard app
3. Write integration tests for the /api/tasks endpoint
4. Refactor the notification service to use the new queue
5. Update the README with the new API docs
6. Clean up stale branches in all repos

You: Using burn-down to work through your backlog.

Assessed sizes: S, M, M, L, S, S
Task 4 (refactor notification service) is L-sized -- it may consume 25-50% of context.
Want me to attempt it as-is, or break it into smaller pieces?

[After user confirms]
Starting Sprint phase (0-60% context). Tasks 2 and 5 are independent -- dispatching in parallel.
```
