# The PACK Development Engine (PDE)

**Design:** A strategic layer that keeps PACK aligned with its North Star.

## Structure

* `MANIFEST.md`: The North Star. Update quarterly.
* `agents/`: Meta-agents for PACK development (`@friction_hunter`, `@context_preserver`).
* `workflows/`: Development rituals (`friction_audit`, `release_check`).
* `state/`: Project state (`friction_log`, `roadmap`).

## Quick Start

**Friction Audit (before release):**

```bash
cat .pde/workflows/friction_audit.md
# Then manually walk through the checklist
```

**Log a Pain Point:**

```bash
echo "- [ ] <description>" >> .pde/state/friction_log.md
```

**Invoke an Agent:**

```bash
# With Gemini CLI
gemini -p "$(cat .pde/agents/friction_hunter.md)" "Review this PR for friction..."

# With Claude Code
# Just reference the agent file in conversation
```

## Relationship to .agent/

| Layer | Purpose | Audience |
|-------|---------|----------|
| `.pde/` | Strategic direction for PACK development | PACK maintainers |
| `.agent/` | Operational coordination protocol | PACK users |

The PDE is for building PACK. The .agent is for using PACK.
