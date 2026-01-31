# Merge Protocol — Cloud Task Batch Review (Portable)

> **Usage**: Paste this into **Local Claude Code** after all Cloud sessions
> have completed and created their PRs.

---

## CONFIG — Edit These for Your Repo

```yaml
TEST_COMMAND: "python -m pytest tests/ -v --tb=short"
BASE_BRANCH: "main"
OUTPUT_DIR: "cloud_tasks"
MANIFEST_PATH: "cloud_tasks/manifest.json"
```

---

## Your Role

You are the **reviewer and merger** for a batch of Cloud task PRs.
Each PR modifies a disjoint set of files, so they should merge without
conflicts. Your job: verify each PR, merge them, and confirm final state.

---

## Step 1: Load the Manifest

```bash
git fetch origin
cat <MANIFEST_PATH>
```

Note the expected branches, file ownership map, and test baseline.

List open PRs:

```bash
gh pr list --state open
```

If any expected PR is missing, note it and proceed with what's available.

---

## Step 2: Review Each PR

For each PR, repeat:

### 2a. Check the diff

```bash
gh pr diff <PR_NUMBER>
```

Verify:
- [ ] All modified files are within this task's `files_owned` from the manifest
- [ ] No files outside the boundary were touched
- [ ] Code quality is acceptable (no debug prints, no commented-out code, no TODOs)
- [ ] Commit messages follow `<type>(<scope>): <description>` convention

### 2b. Checkout and test

```bash
git checkout <branch-name>
<TEST_COMMAND>
```

Verify:
- [ ] All tests pass
- [ ] Test count >= baseline from manifest

### 2c. Record result

```
| # | Task | PR | Files OK | Tests OK | Approved |
|---|------|----|----------|----------|----------|
| 1 |      |    | [ ]      | [ ]      | [ ]      |
| 2 |      |    | [ ]      | [ ]      | [ ]      |
| 3 |      |    | [ ]      | [ ]      | [ ]      |
| 4 |      |    | [ ]      | [ ]      | [ ]      |
| 5 |      |    | [ ]      | [ ]      | [ ]      |
```

---

## Step 3: Merge in Priority Order

Recommended order (adjust as needed):

1. **Bug fixes** — most critical
2. **Validation / hardening**
3. **Refactoring**
4. **Feature work**
5. **Documentation** — may reference changes from other PRs

For each approved PR:

```bash
git checkout <BASE_BRANCH>
git pull origin <BASE_BRANCH>
gh pr merge <PR_NUMBER> --squash --delete-branch
```

After each merge, pull and test:

```bash
git pull origin <BASE_BRANCH>
<TEST_COMMAND>
```

**If tests fail after a merge:**
1. STOP merging further PRs
2. Identify which change caused the failure
3. Fix on the base branch with a follow-up commit, or revert
4. Resume merging remaining PRs

---

## Step 4: Final Verification

After all PRs are merged:

```bash
git checkout <BASE_BRANCH>
git pull origin <BASE_BRANCH>
<TEST_COMMAND>
```

Confirm:
- [ ] All tests pass
- [ ] Test count >= baseline plus any new tests
- [ ] `git status` is clean
- [ ] No leftover remote branches: `git branch -r | grep cloud/`

---

## Step 5: Clean Up Artifacts

The generated task files have served their purpose:

```bash
rm -f <OUTPUT_DIR>/task_*.md
rm -f <OUTPUT_DIR>/manifest.json
```

If these are gitignored (they should be), no commit is needed.

---

## Troubleshooting

### Merge conflict despite disjoint ownership

Two tasks touched the same file (scanner missed a dependency).
- Check the manifest's `file_ownership_map` for the conflict
- Resolve manually, preferring the higher-impact task's version
- Re-run tests

### Tests pass individually but fail after merge

Cross-task interaction the scanner didn't catch (shared state, import order).
- Identify the interaction
- Fix on the base branch as a follow-up commit
- Note it for the next scan cycle

### Cloud session didn't complete

- Check if a partial branch exists: `git branch -r | grep cloud/`
- If usable partial work exists, review it
- Otherwise skip the task and note it for the next scan
