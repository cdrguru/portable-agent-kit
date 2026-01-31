# Scanner Prompt — Parallel Cloud Task Generator (Portable Kit)

> **Usage**: Copy this entire directory into any repo, edit the CONFIG block
> below, then paste this file into a **Local Claude Code** session.
> It will analyze the repo, identify 5 parallel-safe tasks, and generate
> self-contained prompts for 5 Cloud sessions.

---

## CONFIG — Edit These for Your Repo

```yaml
PROJECT_NAME: "Your Project Name"
PROJECT_DESCRIPTION: "One-sentence description of what this project does."
SOURCE_DIRS: ["src/", "lib/"]          # Where your source code lives
TEST_DIRS: ["tests/"]                  # Where your tests live
ASSET_DIRS: ["assets/", "docs/"]       # Non-code files that matter
TEST_COMMAND: "python -m pytest tests/ -v --tb=short"
BASE_BRANCH: "main"                    # or "master", "develop", etc.
LANGUAGE: "python"                     # python, typescript, go, rust, etc.
PACKAGE_MANAGER: "pip"                 # pip, npm, cargo, go mod, etc.
OUTPUT_DIR: "cloud_tasks"  # Where to write generated files (scanner creates this)
```

> **Adjust the values above** to match your repo. The rest of this prompt
> is generic and works unchanged.

---

## Your Role

You are a **Task Scanner and Prompt Generator**. Your job:

1. Analyze this repo's current state
2. Identify the 5 highest-impact improvement tasks
3. Ensure each task modifies a **disjoint set of files** (no two tasks touch the same file)
4. Generate a `manifest.json` and 5 self-contained `task_N.md` prompt files

Do not implement any fixes yourself. Your only output is the manifest and the 5 prompt files.

---

## Step 1: Gather State

Run these commands and record the results:

```bash
git status
git log --oneline -20
<TEST_COMMAND> 2>&1 | tail -30
```

Record:
- Current branch and commit SHA
- Number of tests, pass/fail counts
- Any uncommitted changes

If the project has no tests, note that. Test presence is not required but
shapes which tasks are viable.

---

## Step 2: Build File Dependency Map

For every source file in `<SOURCE_DIRS>`, determine:
- Which other source files import/require/use it
- Which test files cover it
- Which asset files it references

Build a table in context (do not write it to a file):

```
| Source File | Imported By | Test Files | Asset Files |
|-------------|-------------|------------|-------------|
| ...         | ...         | ...        | ...         |
```

This map is how you enforce disjoint ownership. If the project is small
(< 15 source files), you can hold this mentally. For larger projects,
write it out explicitly.

---

## Step 3: Identify Candidate Tasks

Scan the codebase for improvement candidates across these 5 buckets:

| Bucket | What to look for |
|--------|-----------------|
| **Bug fixes** | Failing tests, wrong behavior, crash-prone code paths |
| **Validation** | Missing error handling, unchecked inputs, silent failures |
| **Features** | New capabilities, missing functionality, enhancement gaps |
| **Refactoring** | Code duplication, long functions, naming inconsistencies |
| **Documentation** | Stale references, missing examples, outdated comments |

For each candidate, note:
- One-line description
- Files it would modify
- Bucket category
- Impact score (1-5)
- Complexity (small / medium / large)

### Quality Gates

Every candidate must:
- Be completable in a single focused Cloud session
- Have concrete acceptance criteria expressible as checkboxes
- NOT require API keys, external services, or network access
- NOT require installing new packages
- Be verifiable (with tests, or with a clear manual check if no test suite)
- Produce real, mergeable improvements (not just adding tests for coverage)

---

## Step 4: Select 5 Disjoint Tasks

Apply this algorithm:

```
1. Sort candidates by impact score descending
2. selected = [], owned_files = set()
3. For each candidate:
   a. If candidate.files INTERSECTS owned_files → SKIP
   b. If len(selected) >= 5 → STOP
   c. Add candidate to selected
   d. Add candidate.files to owned_files
4. Return selected
```

### File Ownership Rules

1. Each file appears in **at most one** task's owned list
2. Multiple tasks may **read** the same file — only modifications count
3. Test files are co-owned with their corresponding source files
4. Entry points and init files (`__init__.py`, `index.ts`, `main.go`) are trivial — avoid owning them unless the task specifically changes exports
5. Config files (`.env.example`, `tsconfig.json`, `Cargo.toml`) should only be owned if the task modifies them
6. README / primary docs file: owned by at most one task (typically a docs task)

If fewer than 5 disjoint tasks exist, generate fewer. Do not create filler tasks.

---

## Step 5: Generate manifest.json

Write to `<OUTPUT_DIR>/manifest.json`:

```json
{
  "generated_at": "<ISO8601 timestamp>",
  "project": "<PROJECT_NAME>",
  "base_branch": "<BASE_BRANCH>",
  "base_commit": "<current SHA>",
  "test_command": "<TEST_COMMAND>",
  "test_baseline": {
    "total": 0,
    "passed": 0,
    "failed": 0
  },
  "tasks": [
    {
      "id": 1,
      "slug": "<kebab-case-task-name>",
      "category": "<bug|validation|feature|refactor|docs>",
      "branch": "cloud/<slug>",
      "title": "<Short PR title, under 70 chars>",
      "description": "<What and why, 2-3 sentences>",
      "files_owned": [],
      "files_readonly": [],
      "acceptance_criteria": [],
      "complexity": "<small|medium|large>",
      "impact": 0
    }
  ],
  "file_ownership_map": {}
}
```

---

## Step 6: Generate 5 Task Prompt Files

For each task, generate `<OUTPUT_DIR>/task_N.md` using `CLOUD_SESSION_TEMPLATE.md`
from this kit (locate it in the repo, read it, then fill in every placeholder).

Read that template file, then fill in every `{{PLACEHOLDER}}` with values
from the manifest and your analysis.

Each generated file must be **fully self-contained** — a Cloud session
receiving only that file must have enough context to complete the task
without reading any other documentation.

### Filling in the Project Context section

This is the part that varies most between repos. Include:
- What the project does (from CONFIG)
- Architecture: list the main modules/packages and what each does
- Key files table: the 10-15 most important files with one-line descriptions
- Test baseline numbers

Do NOT paste the entire README. Summarize the relevant parts.

---

## Step 7: Print Summary

After generating all files, print:

```
## Cloud Task Batch Summary

| # | Task | Category | Branch | Files Owned | Impact |
|---|------|----------|--------|-------------|--------|
| 1 | ...  | ...      | cloud/... | N files  | N/5    |
| ...

Files generated:
- <OUTPUT_DIR>/manifest.json
- <OUTPUT_DIR>/task_1.md through task_5.md

Next: Open 5 Claude Code Cloud sessions, paste one task_N.md into each.
After all 5 complete, use MERGE_PROTOCOL.md to review and merge.
```

---

## What NOT to Do

- Do NOT implement any fixes yourself
- Do NOT modify any source code, tests, or configuration
- Do NOT create branches or PRs
- Do NOT run the application or make API calls
- ONLY generate the manifest and task files
