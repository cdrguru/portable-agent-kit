---
name: skill-porter
description: Convert a skill from any AI coding assistant format into a portable PACK skill with proper naming, structure, and registration.
metadata:
  short-description: Port skills from any format to PACK
---

# Skill Porter

## When to use

Use when you have a skill, workflow, or playbook in a non-PACK format and need to
convert it into a portable `.agent/skills/` skill that works across agents and repos.

Triggering phrases: "port this skill", "make this skill portable", "convert to PACK
format", "add this skill to the kit", or `$skill-porter`.

Common source formats:
- `.claude/skills/<name>/skill.md` (Claude Code native)
- `.cursor/rules/*.md` (Cursor rules)
- `.github/copilot-instructions.md` (Copilot)
- Standalone markdown playbooks or runbooks
- Shell scripts with embedded instructions

## Procedure

### Phase 1: Analyze the source skill

1. Read the source skill file(s) and identify:
   - Name and purpose
   - Steps / procedure
   - Supporting files (templates, scripts, configs, exemplars)
   - Tool-specific references (Claude Code tools, Cursor commands, etc.)
   - Hardcoded repo paths or project-specific values

2. Classify the source format using the Convention Map in `references/convention-map.md`.

### Phase 2: Create the PACK skill directory

3. Choose a kebab-case name for the skill:

```bash
mkdir -p .agent/skills/<skill-name>/
```

4. Create `SKILL.md` using the PACK template as the skeleton:

```bash
cp .agent/skills/SKILL.md.template .agent/skills/<skill-name>/SKILL.md
```

5. Fill in the SKILL.md sections:

| Section | Rule |
| --- | --- |
| Frontmatter `name:` | kebab-case, matches directory name |
| Frontmatter `description:` | One sentence, starts with verb |
| Frontmatter `metadata.short-description:` | User-facing summary (<60 chars) |
| When to use | Triggering conditions, NOT tool-specific |
| Procedure | Numbered steps with bash code blocks |
| Inputs and outputs | What goes in, what comes out |
| Constraints | Hard rules for the skill |
| Examples | `$<skill-name>` invocation |

### Phase 3: Convert supporting files

6. If the source skill has supporting files (templates, configs, scripts, exemplars),
   create a `templates/` directory:

```bash
mkdir -p .agent/skills/<skill-name>/templates/
```

7. Copy and rename each file following PACK conventions:

| Source Convention | PACK Convention |
| --- | --- |
| `snake_case.py` | `kebab-case.py` |
| `*.example` | `*.template` |
| `*.snippet` (keep as-is) | `*.snippet` |
| `exemplars/` files | `templates/` files |
| `scripts/` | `scripts/` (keep if executable) |
| `assets/` | `references/` (if documentation) |

8. In each converted file, replace:
   - Hardcoded repo paths with placeholders (`${REPO_ROOT}`, `${PROJECT_NAME}`)
   - Tool-specific commands with generic equivalents (see Convention Map)
   - Organization-specific values with `${ORG_NAME}`, `@org/team-name` placeholders

### Phase 4: Make it model-agnostic

9. Review SKILL.md and all supporting files for tool-specific language:

| Remove / Replace | With |
| --- | --- |
| "Claude Code" | "AI coding assistant" or just remove |
| "Cursor" | "AI coding assistant" or just remove |
| `/skill-name` (slash invocation) | `$skill-name` (dollar invocation) |
| `allowed-tools:` frontmatter | Remove entirely |
| Tool-specific API references | Generic descriptions |
| `Read tool`, `Edit tool` | "Read the file", "Edit the file" |

10. Verify no tool-specific or repo-specific references remain:

```bash
grep -ri "claude code\|cursor\|copilot\|allowed-tools" .agent/skills/<skill-name>/
grep -r "\.\./\.\.\|/Users/\|/home/" .agent/skills/<skill-name>/
```

### Phase 5: Register and verify

11. Add the skill to `.agent/skills/README.md`:

```markdown
| <skill-name> | <short-description> | $<skill-name> |
```

12. Add the skill to `CLAUDE.md` (if it exists):

```markdown
| <skill-name> | `$<skill-name>` |
```

13. Verify the skill is discoverable:

```bash
python3 .agent/tools/utilities/skills.py show <skill-name>
```

14. Verify portability -- the skill should work when the entire `.agent/` directory
    is copied to a fresh repo:

```bash
# Confirm no external dependencies
grep -r "pip install\|npm install\|brew install" .agent/skills/<skill-name>/ || echo "OK: no deps"

# Confirm no absolute paths
grep -r "^/" .agent/skills/<skill-name>/ || echo "OK: no absolute paths"

# Confirm all template references are self-contained
ls .agent/skills/<skill-name>/templates/ 2>/dev/null
```

## Inputs and outputs

- Inputs: A skill in any format (path to source directory or file)
- Outputs: A PACK-compliant skill directory under `.agent/skills/<skill-name>/`, registered in indexes

## Constraints

- Read-only during analysis -- do not modify the source skill
- Zero dependencies -- PACK skills use only shell, Python stdlib, and markdown
- ASCII-only filenames and content
- Model-agnostic -- no references to specific AI coding assistants
- Kebab-case for all directory and file names
- Supporting files use `.template` or `.snippet` extensions
- The ported skill must be fully self-contained within its directory
- Human approval before registering in indexes

## Examples

- $skill-porter
