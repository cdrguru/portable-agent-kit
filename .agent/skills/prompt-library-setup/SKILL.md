---
name: prompt-library-setup
description: Set up an organized prompt library with categories, catalog, inbox, and Makefile targets in any repository.
metadata:
  short-description: Set up a prompt library with categories, catalog, and inbox
---

# Prompt Library Setup

## When to use
Use when a repository has scattered prompt files and needs a clean, categorized library structure with an intake workflow.

## Procedure
1. Choose 3-7 categories with prefixes for this repo (defaults: `sys-` agents, `tpl-` templates, `wfl-` workflows, `sal-` sales, `doc-` docs):

```bash
mkdir -p prompts_library/{agents,templates,workflows,sales,docs,_inbox}
touch prompts_library/{agents,templates,workflows,sales,docs}/.gitkeep
```

2. Copy and customize the catalog template:

```bash
cp .agent/skills/prompt-library-setup/templates/CATALOG.md.template prompts_library/CATALOG.md
```

Replace `${REPO_NAME}` with the repo name and update the categories table.

3. Copy the inbox README:

```bash
cp .agent/skills/prompt-library-setup/templates/inbox-README.md.template prompts_library/_inbox/README.md
```

Update the prefix/folder table to match your chosen categories.

4. Append the Makefile targets:

```bash
cat .agent/skills/prompt-library-setup/templates/Makefile.snippet >> Makefile
```

Add `prompt-catalog prompt-list prompt-inbox` to the `.PHONY` line.

5. Scan the repo for existing `.md` prompt files and catalog them in `prompts_library/CATALOG.md` with relative links to their current locations. Do NOT move files.

6. Verify:

```bash
make prompt-list
git status  # Should show only new/untracked files
```

## Inputs and outputs
- Inputs: Repository with scattered prompt files, chosen category list
- Outputs: `prompts_library/` directory with categories, `CATALOG.md`, `_inbox/README.md`, Makefile targets

## Constraints
- Additive only -- never move, rename, or delete existing files
- Catalog links point to current file locations (no duplication)
- ASCII-only filenames, kebab-case slugs
- No scripts, no dependencies -- just directories + markdown + Makefile snippets

## Examples
- $prompt-library-setup
