# CLAUDE.md

This is the Portable Agent Collaboration Kit (PACK) -- a zero-dependency framework for multi-agent AI collaboration.

## Architecture

- `.agent/` -- Operational layer (agents, skills, tools, handoff logs)
- `.pde/` -- Strategic layer (North Star manifest, friction log, roadmap)
- `templates/` -- Reusable add-ons (parallel cloud tasks, iterative dev protocol)

## Key Files

| File | Purpose |
| ---- | ------- |
| `.agent/AGENTS.md` | Agent roster, roles, and coordination rules |
| `.agent/ai/prompts/multi_agent_orchestration_system.md` | Shared orchestration protocol |
| `.agent/skills/README.md` | Skills index and invocation guide |
| `.agent/MANIFEST.md` | Operational goals and constraints |
| `.pde/MANIFEST.md` | Strategic North Star |

## Commands

```bash
python3 deploy_agent_kit.py --dest /path/to/repo   # Deploy kit to a repo
./.agent/tools/bin/pack-init.sh                     # Unified repo bootstrap
python3 .agent/tools/utilities/skills.py list       # List all skills
python3 .agent/tools/utilities/skills.py show <name> # Show a skill
```

## Skills

| Skill | Invocation |
| ----- | ---------- |
| session-bootstrap | `$session-bootstrap` |
| handoff-log-update | `$handoff-log-update` |
| handoff-log-condense | `$handoff-log-condense` |
| claude-code-init | `$claude-code-init` |
| claude-code-handoff | `$claude-code-handoff` |
| claude-md-init | `$claude-md-init` |
| gemini-cli-init | `$gemini-cli-init` |
| gemini-audit | `$gemini-audit` |
| prompt-library-setup | `$prompt-library-setup` |

## Constraints

- **Zero dependencies** -- Python stdlib only, no pip install
- **ASCII-only** -- Maximum compatibility across systems and editors
- **Append-only logs** -- Handoff logs are never rewritten
- **Model-agnostic** -- Works with Claude, GPT, Gemini, local LLMs
- **Human approval** before risky operations

## Handoff Protocol

When finishing work, log the handoff:

```bash
python3 .agent/tools/utilities/update_agent_conversation_log.py \
  --agent claude_code \
  --summary "What was done" \
  --handoff <next_agent_or_human>
```
