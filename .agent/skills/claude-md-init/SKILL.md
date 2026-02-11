---
name: claude-md-init
description: Generate a CLAUDE.md project file that orients Claude Code to the repo's structure, commands, and constraints.
metadata:
  short-description: Generate CLAUDE.md for any repo
---

# CLAUDE.md Generator

## When to use
Use when a repository needs a `CLAUDE.md` file so Claude Code automatically understands the project's structure, commands, and conventions at session start.

## Procedure
1. Copy the template to the repo root:

```bash
cp .agent/skills/claude-md-init/templates/CLAUDE.md.template CLAUDE.md
```

2. Replace the placeholders:
   - `${PROJECT_NAME}` -- repo or project name
   - `${PROJECT_DESCRIPTION}` -- one-line description
   - Fill in the Architecture, Commands, and Constraints sections

3. Scan the repo and add relevant details:
   - Key directories and their purpose
   - Build/test/lint commands (from Makefile, package.json, etc.)
   - Available skills (if PACK is deployed)
   - Project-specific constraints and conventions

4. Verify Claude Code picks it up:

```bash
cat CLAUDE.md
```

## Inputs and outputs
- Inputs: Repository with established structure, optional `.agent/` directory
- Outputs: `CLAUDE.md` at the repo root

## Constraints
- Keep it concise -- Claude Code loads this on every interaction
- Do not duplicate content that lives in other files -- reference them instead
- ASCII-only

## Examples
- $claude-md-init
