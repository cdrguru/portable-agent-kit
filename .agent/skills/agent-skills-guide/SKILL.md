---
name: agent-skills-guide
description: "Generate a single-page HTML reference of all AI agents, skills, model routing, and orchestration protocols for the current project. Discovers .claude/skills/, .claude/agents/, ai/models.yaml, and multi-agent orchestration docs, then produces an interactive dark-themed HTML guide."
allowed-tools: Read, Glob, Grep, Write, Bash(ls:*), Bash(wc:*)
argument-hint: "[output-path] (default: ai-agent-skills-guide.html in repo root)"
---

# Agent & Skills Guide Generator

Generate a single-page interactive HTML reference documenting all AI agents, skills, sub-agents, model routing, and orchestration protocols for the **current project**.

## Discovery Phase

Before generating, scan the project to find all available configuration:

### 1. Claude Code Skills
```
Glob: .claude/skills/*/skill.md
Glob: .claude/skills/*/SKILL.md
Glob: .claude/commands/*.md
```
For each skill found, extract from frontmatter:
- `name` and `description`
- `allowed-tools`
Read the body for workflow steps and output format.

### 2. Claude Code Agents (sub-agents)
```
Glob: .claude/agents/*.md
```
For each agent, extract:
- Agent name, model directive, checklist items, output format

### 3. Model Routing Configuration
```
Glob: ai/models.yaml
Glob: **/models.yaml
Glob: **/models.yml
```
Extract agent tiers, model names, providers, and roles.

### 4. Multi-Agent Orchestration
```
Glob: ai/prompts/multi_agent*.md
Glob: **/multi_agent*.md
Glob: **/*orchestration*.md
```
Extract agent roster, parallel rules, handoff protocol, communication format.

### 5. Project Metadata
```
Read: CLAUDE.md (first 30 lines for project name and stack)
Read: README.md (first 20 lines for project description)
Read: package.json or pyproject.toml (for project name)
```

### 6. Additional Skills (global)
Note which global skills from `~/.claude/skills/` are available but mark them as "Global (all projects)" rather than project-specific.

## Generation Phase

Generate a self-contained HTML file with these sections:

### Required Sections
1. **Hero** — Project name, description, provider badges (Anthropic, OpenAI, Google, etc.)
2. **Sticky Nav** — Anchor links to each section
3. **Agent Roster** — Card for each agent with: name, model, context window, description, roles (as chips), and "How to use" code block
4. **Claude Code Skills** — Card for each skill with: name, `/trigger` command, description, numbered steps
5. **Sub-Agents** — Card for each `.claude/agents/` agent with: name, model, description, output format preview
6. **Standard Build Workflow** — Visual flow diagram (Plan → Build → Verify → Review → QA → Ship) if workflow info is found
7. **Model Routing Table** — Task type → Agent → Model → Invocation
8. **Parallel Execution Rules** — What can run concurrently vs sequentially (if found in orchestration docs)
9. **Handoff Protocol** — Steps and message format (if found)

### Sections to Skip
- Skip any section where no relevant configuration was found
- Do NOT invent agents or skills that don't exist in the project

### Design System
Use this exact design token set for consistency across all generated guides:

```css
--navy: #0f172a;        /* body background */
--slate-800: #1e293b;   /* card background */
--slate-700: #334155;   /* borders */
--slate-400: #94a3b8;   /* secondary text */
--slate-300: #cbd5e1;   /* body text */
--indigo-500: #6366f1;  /* primary accent */
--indigo-400: #818cf8;  /* heading accent */
--indigo-300: #a5b4fc;  /* light accent */
--emerald-400: #34d399; /* code text */
--amber-400: #fbbf24;   /* trigger commands */
--rose-500: #f43f5e;    /* critical/sequential */
--cyan-400: #22d3ee;    /* Google badge */
--violet-400: #a78bfa;  /* sub-agent accent */
```

Font stack: `'Segoe UI', system-ui, -apple-system, sans-serif`
Monospace: `'SF Mono', 'Fira Code', monospace`

### Card Patterns
- **Agent cards**: icon + header (name, model tag) + description + role chips + "How to use" code block
- **Skill cards**: h3 name + trigger command (amber monospace) + description + numbered step list
- **Sub-agent cards**: h3 name + model tag + description + output format preview (monospace block)

### Provider Badge Colors
- Anthropic (Claude): indigo
- OpenAI (Codex/GPT): emerald
- Google (Gemini): cyan
- Local/Offline: slate
- Other: use a neutral badge

## Output

Write the HTML file to the path specified by the user, or default to `ai-agent-skills-guide.html` in the repository root.

After writing, report:
- Number of agents, skills, and sub-agents documented
- Sections included vs skipped
- File size and path

## Example Invocation

```
/agent_skills_guide
/agent_skills_guide docs/ai-reference.html
```

## Adaptation Notes

This skill is **project-agnostic**. It works by discovering what exists rather than assuming a fixed set of agents. For projects with:
- No `ai/models.yaml` → skip model routing table
- No `.claude/agents/` → skip sub-agents section
- No orchestration docs → skip parallel rules and handoff protocol
- Only skills → generate a skills-only reference

The output is always a single self-contained HTML file with no external dependencies.
