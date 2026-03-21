---
name: session-wrapup
description: End-of-session workflow for surveying changes, grouping logical commits, respecting workspace-level repo boundaries, and pushing safely.
metadata:
  short-description: Wrap up a repo safely
allowed_tools: ["Bash", "Read", "Glob", "Grep"]
---

# Session Wrapup

Use this skill when the user wants to review, commit, and sync session changes without mixing repo boundaries.

## Workflow

1. Check for workspace-level context first.
   - If the repo lives inside a larger local workspace and a parent `WORKSPACE_MAP.md` exists, read it before proposing commit groups.
   - Use that file to classify the repo and prefer its repo-specific grouping rules or remote policy.
   - Repo-local `AGENTS.md` and `CLAUDE.md` override the workspace map.

2. Survey the worktree in parallel.
   - `git status --short` (never `-uall`)
   - `git diff --stat` (staged + unstaged)
   - `git log --oneline -5` (recent commits for message style)
   - `git remote -v`
   - `git rev-parse --abbrev-ref HEAD`

3. Triage untracked files before grouping.
   - If an untracked path looks like generated output or OS noise (for example `dist/`, `.DS_Store`, `__pycache__/`, `*.pyc`, `node_modules/`), suggest ignoring it instead of staging it.
   - If an untracked path looks intentional, include it in the commit grouping step.
   - Flag ambiguous untracked files to the user before staging.

4. Build commit groups from the actual repo structure.
   - Start with repo-specific buckets from `WORKSPACE_MAP.md` when present.
   - Otherwise use practical defaults:
     - source code
     - tests
     - documentation
     - configuration
     - infrastructure/tooling
     - dependencies
     - assets
     - miscellaneous
   - If the repo has domain-specific folders such as `emails/`, `tasks/`, `drafts/`, `statements/`, or tax-year folders, use those instead of forcing generic buckets.

5. Present the proposed groups before any commit.
   - Show explicit file paths per group.
   - Skip empty groups.
   - Adjust group boundaries if the user asks.
   - If some files appear unfinished, ask whether they should stay out of scope or be stashed with explicit paths before continuing.

6. Commit each approved group with explicit paths only.
   - `git add <file1> <file2> ...`
   - Never use `git add -A` or `git add .`.
   - Follow the repo's existing commit style if it is clear from recent history.
   - Keep commit scopes coherent with the group boundaries you presented.

7. Push safely.
   - Respect remote policy from `WORKSPACE_MAP.md`, then repo-local `AGENTS.md` or `CLAUDE.md`.
   - If no policy constrains the choice, use the first practical remote from `macstudio`, `origin`, or the only configured remote.
   - Before pushing, check whether an upstream branch exists and whether local branch or remote policy requires an extra user decision.
   - If a remote refresh is needed to check divergence accurately, ask before running networked git commands.
   - Never force-push.

8. Verify clean state.
   - `git status`
   - `git log --oneline -N`
   - If you excluded or stashed files earlier, remind the user exactly what remains out of scope.

## Guardrails

1. Present all groups for user approval before any commit.
2. Never mix files from different repos into one commit.
3. Never use `git add -A` or `git add .`; add files by explicit path per group.
4. Use `git diff --stat` and targeted diffs instead of dumping binary content.
5. Never bypass hooks with `--no-verify`.
6. Do not force-push.
7. Respect protected paths and remote restrictions defined by repo-local instructions.
8. Skip likely secret files such as `.env`, `*.key`, `*.pem`, or `credentials.*` and flag them explicitly.

## Workspace-Specific Rule

If `WORKSPACE_MAP.md` describes a repo family, treat "workspace wrapup" as a multi-repo survey with per-repo commits and per-repo pushes, never a single combined commit across sibling repos.
