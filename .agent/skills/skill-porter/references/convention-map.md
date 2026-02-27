# Convention Map: Source Formats to PACK

Quick reference for converting skills from common AI coding assistant formats
into the PACK `.agent/skills/` convention.

---

## Directory Structure

| Source Format | Location | PACK Equivalent |
| --- | --- | --- |
| Claude Code | `.claude/skills/<snake_name>/skill.md` | `.agent/skills/<kebab-name>/SKILL.md` |
| Claude Code agents | `.claude/agents/<name>.md` | `.agent/agents/<name>.md` |
| Claude Code rules | `.claude/rules/<topic>.md` | `.agent/ai/rules/<topic>.md` |
| Cursor | `.cursor/rules/*.md` | `.agent/ai/rules/*.md` or skill |
| Cursor | `.cursorrules` (root) | `CLAUDE.md` or `.agent/MANIFEST.md` |
| Copilot | `.github/copilot-instructions.md` | `CLAUDE.md` or `.agent/MANIFEST.md` |
| Windsurf | `.windsurfrules` | `.agent/ai/rules/*.md` or skill |
| Aider | `.aider.conf.yml` | `.agent/MANIFEST.md` (constraints section) |
| Raw playbook | `docs/playbooks/*.md` | `.agent/skills/<name>/SKILL.md` |
| Shell script | `scripts/<name>.sh` | `.agent/skills/<name>/scripts/<name>.sh` |

---

## Naming Conventions

| Element | Source (varies) | PACK |
| --- | --- | --- |
| Skill directory | `snake_case`, `camelCase`, `PascalCase` | `kebab-case` |
| Main skill file | `skill.md`, `README.md`, `PLAYBOOK.md` | `SKILL.md` (uppercase) |
| Template files | `*.example`, `*.sample`, `*.tpl` | `*.template` |
| Snippet files | `*.snippet`, `*.partial` | `*.snippet` |
| Supporting docs | `exemplars/`, `examples/`, `assets/` | `references/` |
| Runnable helpers | `scripts/`, `bin/` | `scripts/` |

---

## Frontmatter

### Claude Code `.claude/skills/` format

```yaml
---
name: my_skill_name
description: What this skill does
allowed-tools: Read, Edit, Bash, Grep, Glob
---
```

### PACK `.agent/skills/` format

```yaml
---
name: my-skill-name
description: What this skill does, in one sentence.
metadata:
  short-description: User-facing summary
---
```

**Key differences:**
- `name:` uses kebab-case (not snake_case)
- `allowed-tools:` is removed (PACK is model-agnostic; tools vary by agent)
- `metadata.short-description:` is added for index display

---

## Invocation

| Format | Pattern | Example |
| --- | --- | --- |
| Claude Code | `/skill_name` | `/agentic_audit` |
| PACK | `$skill-name` | `$agentic-audit` |
| Cursor | Reference in `.cursorrules` | N/A |
| Copilot | Reference in instructions | N/A |

---

## Tool-Specific Language to Genericize

| Tool-Specific | Model-Agnostic Replacement |
| --- | --- |
| "Use the Read tool to..." | "Read the file..." |
| "Use the Edit tool to..." | "Edit the file to..." |
| "Use the Bash tool to..." | "Run:" (with code block) |
| "Use the Grep tool to..." | "Search for..." |
| "Use the Glob tool to..." | "Find files matching..." |
| "Claude Code will..." | "The AI assistant will..." |
| "Cursor will..." | "The AI assistant will..." |
| "In your Claude session..." | "In your session..." |
| "Ask Claude to..." | "Ask the AI assistant to..." |
| "The LLM should..." | "The agent should..." |

---

## Section Mapping

| Source Section | PACK Section |
| --- | --- |
| Description / Overview | `## When to use` |
| Steps / Instructions / How-to | `## Procedure` |
| Requirements / Prerequisites | `## Inputs and outputs` (Inputs) |
| Output / Result / Deliverable | `## Inputs and outputs` (Outputs) |
| Rules / Guardrails / Limits | `## Constraints` |
| Usage / Invocation | `## Examples` |
| References / See also | `## References` (optional) |

---

## Placeholder Tokens

When genericizing hardcoded values, use these standard placeholders:

| Placeholder | Meaning |
| --- | --- |
| `${REPO_ROOT}` | Repository root path |
| `${PROJECT_NAME}` | Project or repo name |
| `${ORG_NAME}` | Organization name |
| `@org/team-name` | GitHub team placeholder |
| `${BRANCH_NAME}` | Target branch |
| `${MAIN_BRANCH}` | Default branch (main/master) |
| `your-project.example.com` | Domain placeholder |
| `your-api-key-here` | API key placeholder |

---

## Portability Checklist

Run these checks after porting a skill:

```bash
SKILL_DIR=".agent/skills/<skill-name>"

# 1. No absolute paths
grep -rn "^/" "$SKILL_DIR" && echo "FAIL: absolute paths found" || echo "PASS"

# 2. No tool-specific references
grep -rin "claude code\|cursor\|copilot\|windsurf\|aider" "$SKILL_DIR" \
  && echo "FAIL: tool-specific refs" || echo "PASS"

# 3. No repo-specific paths
grep -rn "/Users/\|/home/\|C:\\\\" "$SKILL_DIR" \
  && echo "FAIL: user-specific paths" || echo "PASS"

# 4. No external dependencies
grep -rn "pip install\|npm install\|brew install\|cargo install" "$SKILL_DIR" \
  && echo "WARN: external deps" || echo "PASS"

# 5. Kebab-case directory name
basename "$SKILL_DIR" | grep -E "^[a-z][a-z0-9-]*$" \
  && echo "PASS" || echo "FAIL: not kebab-case"

# 6. SKILL.md exists
test -f "$SKILL_DIR/SKILL.md" && echo "PASS" || echo "FAIL: missing SKILL.md"

# 7. Frontmatter has required fields
head -10 "$SKILL_DIR/SKILL.md" | grep -q "name:" && echo "PASS: name" || echo "FAIL: no name"
head -10 "$SKILL_DIR/SKILL.md" | grep -q "short-description:" \
  && echo "PASS: short-description" || echo "FAIL: no short-description"

# 8. Template files use .template or .snippet extension
find "$SKILL_DIR/templates/" -type f 2>/dev/null | grep -v -E "\.(template|snippet|md)$" \
  && echo "WARN: non-standard extensions" || echo "PASS"
```
