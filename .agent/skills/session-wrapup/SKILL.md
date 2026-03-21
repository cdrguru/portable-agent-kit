---
name: session-wrapup
description: End-of-session workflow — survey changes, group into logical commits, push to remote, verify clean state. Works in any git repo.
allowed_tools: ["Bash", "Read", "Glob", "Grep"]
---

# Session Wrapup (Portable)

Review, commit, and sync all session changes. Works in any git repository.

## Steps

1. **Check for workspace-level context**:
   - If the repo lives inside a larger local workspace and a parent `WORKSPACE_MAP.md` exists, read it first
   - Use that file to classify the repo before proposing commit groups
   - Repo-local `CLAUDE.md` and `AGENTS.md` still override the workspace map

2. **Survey the worktree** — run these in parallel:
   - `git status --short` (never `-uall`)
   - `git diff --stat` (staged + unstaged)
   - `git log --oneline -5` (recent commits for message style)
   - `git remote -v` (available remotes)
   - `git rev-parse --abbrev-ref HEAD` (current branch)

3. **Categorize changes into logical commit groups** by path convention:
   - Source code (`src/`, `lib/`, `app/`, `pkg/`, language-specific source dirs)
   - Tests (`test/`, `tests/`, `spec/`, `__tests__/`, `*_test.*`, `*.spec.*`)
   - Documentation (`docs/`, `README*`, `CHANGELOG*`, `*.md` in root)
   - Configuration (dotfiles, `*.config.*`, `*.yaml`, `*.yml`, `*.toml`, `*.json` in root, `Makefile`, `Dockerfile*`, CI configs)
   - Infrastructure / tooling (`.claude/`, `.agent/`, `.github/`, `scripts/`, build tooling)
   - Dependencies (lock files, `requirements*.txt`, `package.json`, `go.sum`, etc.)
   - Assets (`public/`, `static/`, `assets/`, images, fonts)
   - Everything else → miscellaneous updates
   - **Adapt categories to the repo** — if a repo has domain-specific top-level dirs (e.g., `emails/`, `tasks/`, `drafts/`), create categories for those instead of forcing generic ones
   - If `WORKSPACE_MAP.md` defines a repo class or preferred buckets, prefer those over generic defaults
   - Present proposed groups to user with file lists; skip empty categories

4. **Wait for user approval** — adjust groups if requested before any commit

5. **Commit each approved group**:
   - `git add <file1> <file2> ...` (never `git add -A` or `git add .`)
   - Commit message format: `<type>(<scope>): <brief description>`
     - Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`, `ci`
     - Follow the repo's existing commit message style if one is apparent from recent history
   - Append `Co-Authored-By: Claude <model> <noreply@anthropic.com>` trailer

6. **Push to remote**:
   - Auto-detect remote: use the first available from `macstudio`, `origin`, or the only configured remote
   - If `WORKSPACE_MAP.md` defines a preferred branch or remote policy, obey it unless repo-local instructions say otherwise
   - If repo-specific CLAUDE.md restricts remotes, obey that restriction
   - If no remote is configured, skip push and inform the user
   - `git push <remote> <current-branch>`
   - If push requires `--set-upstream`, use `-u` flag

7. **Verify clean state**:
   - `git status` — confirm working tree is clean
   - `git log --oneline -N` — show the new commits (N = number of commits made)

## Guardrails

- Present all groups for user approval before any commit
- Never use `git add -A` or `git add .` — add files by explicit path per group
- Use `--stat` for diffs to avoid dumping binary content
- Never bypass pre-commit or pre-push hooks (`--no-verify`)
- Do not force-push
- If the repo has a CLAUDE.md with protected paths or remote restrictions, obey them
- Skip files that look like secrets (`.env`, `*.key`, `*.pem`, `credentials.*`) — flag them to the user instead of staging
