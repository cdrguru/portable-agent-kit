# Parallel Cloud Tasks — Portable Kit

A 3-file system for running 5 parallel Claude Code Cloud sessions against any repo without merge conflicts.

## Quick Start

1. From this repo, copy `templates/parallel-cloud-tasks-kit/` into your target repo (keep the folder name or rename it to `portable/`)
2. Edit the `CONFIG` block at the top of `SCANNER_PROMPT.md` (project name, source dirs, test command, base branch)
3. Edit the `CONFIG` block at the top of `MERGE_PROTOCOL.md` (same test command and base branch)
4. Add these lines to your `.gitignore`:

```gitignore
# Generated cloud task files
cloud_tasks/task_*.md
cloud_tasks/manifest.json
```
The scanner will create `cloud_tasks/` for you. If you change `OUTPUT_DIR`, update these paths to match.

5. Run the workflow:
   - Paste `SCANNER_PROMPT.md` into Local Claude Code → generates `manifest.json` + `task_1..5.md`
   - Open 5 Cloud sessions, paste one `task_N.md` into each
   - When all 5 finish, paste `MERGE_PROTOCOL.md` into Local Claude Code

## Files

| File | Who uses it | What it does |
|------|------------|--------------|
| `SCANNER_PROMPT.md` | Local Claude Code | Analyzes repo, generates 5 disjoint tasks |
| `CLOUD_SESSION_TEMPLATE.md` | Scanner (internal) | Template for generating each task_N.md |
| `MERGE_PROTOCOL.md` | Local Claude Code | Reviews and merges the 5 PRs |

## How It Prevents Conflicts

The scanner builds a **file dependency map** of the repo, then selects 5 tasks where no two tasks modify the same file. Each generated `task_N.md` includes an explicit **files you CAN modify** list and a **files you CANNOT modify** list. Cloud sessions are instructed to stay within their boundaries.

## Language Support

Works with any language. Edit the CONFIG block to set your test command:

- Python: `python -m pytest tests/ -v --tb=short`
- TypeScript: `npm test`
- Go: `go test ./...`
- Rust: `cargo test`

## Adapting for Fewer Sessions

If you don't need 5 parallel sessions, the scanner will generate fewer tasks when fewer disjoint opportunities exist. You can also edit the scanner prompt to change `>= 5` to any number.

## Related

- **`templates/iterative-dev-protocol.md`** — wraps this kit into a repeatable Generate/Execute/Merge/Archive cycle with state-machine resumption and batch archiving. Use it when you want to run multiple rounds of parallel tasks back-to-back.
