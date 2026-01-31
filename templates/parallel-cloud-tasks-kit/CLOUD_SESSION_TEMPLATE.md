# Cloud Session Template (Portable)

> **This is a template, not a task.** The scanner uses this to generate
> `task_1.md` through `task_5.md`. Placeholders use `{{VARIABLE}}` notation.
>
> This template is repo-agnostic. The scanner fills in project-specific
> details when generating each task file.

---

Everything below this line is the structure each generated `task_N.md` must follow.

---

# Cloud Task {{TASK_ID}}: {{TASK_TITLE}}

> **Branch**: `{{BRANCH_NAME}}`
> **Category**: {{CATEGORY}}
> **Base commit**: `{{BASE_COMMIT}}`

---

## Project Context

{{PROJECT_DESCRIPTION}}

### Architecture

{{ARCHITECTURE_SUMMARY}}

### Key Files

| File | Purpose |
|------|---------|
{{KEY_FILES_TABLE}}

### Test Baseline

{{TEST_BASELINE_SUMMARY}}

---

## Your Task

{{TASK_DESCRIPTION}}

---

## Files You CAN Modify

Only these files. Do not create, edit, or delete anything else.

| File | Why |
|------|-----|
{{FILES_OWNED_TABLE}}

## Files You Must NOT Modify

Everything not listed above. These files are owned by other parallel
Cloud sessions running right now:

{{FILES_FORBIDDEN_LIST}}

You may read any file for context. You may only write to your owned files.

---

## Acceptance Criteria

All must be true before creating the PR:

{{ACCEPTANCE_CRITERIA_CHECKLIST}}

- [ ] All existing tests still pass ({{TEST_BASELINE}} baseline)
- [ ] No files outside the owned set were modified
- [ ] Changes are committed with descriptive messages

---

## Branch, Commit, and PR Instructions

### 1. Create your branch

```bash
git checkout -b {{BRANCH_NAME}}
```

### 2. Work and commit incrementally

After each logical change:

```bash
{{TEST_COMMAND}}
git add <your owned files only>
git commit -m "$(cat <<'EOF'
<type>({{SLUG}}): <what changed>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

Commit types: `fix`, `feat`, `refactor`, `test`, `docs`

### 3. Push and create PR

```bash
git push -u origin {{BRANCH_NAME}}
gh pr create --title "{{PR_TITLE}}" --body "$(cat <<'EOF'
## Summary
{{PR_SUMMARY_BULLETS}}

## Cloud Task {{TASK_ID}} of {{TOTAL_TASKS}}

Part of a parallel cloud task batch.
See `manifest.json` in the scanner output directory (`<OUTPUT_DIR>/manifest.json`) for full context.

## Acceptance Criteria
{{ACCEPTANCE_CRITERIA_CHECKLIST}}

## Test Results
<!-- Paste final test output here -->

---
Generated with Claude Code Cloud
EOF
)"
```

### 4. Do NOT merge

The local Claude Code session will review and merge your PR.
Your job ends at PR creation.

---

## General Rules

- **Run tests after every change** — do not push broken tests
- **No API calls** — no external services, no network requests
- **No package installs** — do not modify dependency files or run install commands
- **No secrets** — do not read, log, or commit environment/credential files
- **Stay in your lane** — only modify files listed in your owned set above
- **If tests fail and you cannot fix them**, describe the issue in the PR body instead of force-pushing broken code
- **Write production-quality code** — not scaffolding, not placeholders, not TODOs
