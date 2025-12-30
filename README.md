# Portable Agent Collaboration Kit

> **A zero-dependency framework for multi-agent AI collaboration in any repository.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#requirements)

---

## Why This Kit?

Modern AI-assisted development often involves multiple agents (planners, coders, reviewers, docs) working alongside human developers. Without clear coordination:

- Agents overwrite each other's work
- Context gets lost between sessions
- Handoffs are unclear and messy
- Local logs pollute git history

**This kit solves these problems** with a lightweight, portable framework that works with *any* AI model.

---

## Features

| Feature | Description |
|---------|-------------|
| **Model-Agnostic** | Works with Claude, GPT, Gemini, Codex, local LLMs, or any AI |
| **Zero Dependencies** | Pure Python stdlib - no pip install needed |
| **Portable** | Copy to any repo and start collaborating |
| **ASCII-Only** | Maximum compatibility across systems and editors |
| **Append-Only Logs** | Preserve collaboration history, never lose context |
| **CLI Tooling** | Simple scripts for logging handoffs |

---

## Quick Start

### Install with One Command

```bash
python3 deploy_agent_kit.py --dest /path/to/your/repo
```

### Or Copy Manually

```bash
cp -r .agent /path/to/your/repo/
```

### Then Customize

1. Edit `.agent/AGENTS.md` to define your agent roles
2. Set your project name: `export PROJECT_NAME="my-project"`
3. Start collaborating!

---

## What's Included

```text
.agent/
+-- AGENTS.md                     # Agent roster and coordination rules
+-- README.md                     # Installation guide
+-- conversation.compact.md.template  # Local session log template
+-- context/
|   +-- agent_environment.md      # Shared role + interaction policy
+-- ai/
|   +-- prompts/
|   |   +-- multi_agent_orchestration_system.md  # Shared protocol
|   |   +-- agent_profiles/       # Role profiles (ag/hp/codex)
|   +-- rules/
|       +-- agent_handshake.md    # Handoff mechanics
+-- docs/
|   +-- agent_handoffs/
|       +-- README.md
|       +-- agent_conversation_log.md  # Append-only handoff log
+-- tools/
    +-- utilities/
        +-- update_agent_conversation_log.py  # CLI helper
        +-- print_agent_init.py   # Print a combined session-init prompt
```

---

## Core Concepts

### Agent Roles

Define roles that match your workflow:

| Role | Responsibility |
|------|----------------|
| **Planner** | Decomposes objectives into tasks |
| **Builder** | Implements code changes |
| **Reviewer** | Validates correctness, runs tests |
| **Docs** | Keeps documentation current |
| **Human Director** | Approves scope and makes decisions |

### Task Status Markers

Coordinate work with simple markers in your task files:

| Marker | Meaning |
|--------|---------|
| `[ ]` | Pending - available for pickup |
| `[/]` | In Progress - locked by an agent |
| `[x]` | Complete - verified and done |
| `[-]` | Blocked - needs human decision |

### Communication Prefixes

Structure your logs for clarity:

```text
Decision: We will use approach X because...
Action: Implement function Y in file Z
Question: Should we support edge case W?
```

---

## Usage

### Recording a Handoff

After completing work, log the handoff:

```bash
python3 .agent/tools/utilities/update_agent_conversation_log.py \
  --agent builder \
  --summary "Implemented login feature with tests" \
  --handoff reviewer \
  --task "Review auth flow in src/auth.py" \
  --task "Run test suite" \
  --reference "src/auth.py" \
  --reference "tests/test_auth.py"
```

### CLI Options

| Flag | Description |
|------|-------------|
| `--agent` | Name of the agent (required) |
| `--summary` | What was done (required) |
| `--handoff` | Who's next (agent name or "human") |
| `--task` | Follow-up task (repeatable) |
| `--reference` | File path or URL (repeatable) |
| `--context` | Category: setup, refactor, bugfix |
| `--status` | ready, blocked, wip (default: ready) |

### Starting a Session

```bash
# Create your local session log (gitignored)
cp .agent/conversation.compact.md.template conversation.compact.md

# Edit with your objective and start working
```

Generate a combined init prompt for a specific agent:

```bash
python3 .agent/tools/utilities/print_agent_init.py --agent ag
python3 .agent/tools/utilities/print_agent_init.py --agent hp
python3 .agent/tools/utilities/print_agent_init.py --agent codex
```

Optional: pipe to your clipboard (example for macOS):

```bash
python3 .agent/tools/utilities/print_agent_init.py --agent ag | pbcopy
```

---

## Deployment Script

The `deploy_agent_kit.py` script handles installation:

```bash
# Preview what would be installed
python3 deploy_agent_kit.py --dest /path/to/repo --dry-run

# Install the kit
python3 deploy_agent_kit.py --dest /path/to/repo

# Overwrite existing files
python3 deploy_agent_kit.py --dest /path/to/repo --force
```

### What It Does

1. Copies `.agent/` folder to your repository
2. Adds local-only entries to `.gitignore`:
   - `conversation.compact.md`
   - `.reports/`
3. Prints a summary of changes

---

## Requirements

- **Python 3.8+** (uses only standard library)
- **Any OS**: macOS, Linux, Windows
- **Any AI Model**: Claude, GPT, Gemini, Codex, Llama, or custom

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes (keep them minimal!)
4. Submit a pull request

### Development Principles

- **Simplicity first** - Every change should be as simple as possible
- **No dependencies** - Stdlib only
- **ASCII-only** - Maximum compatibility
- **Clear documentation** - If it's not documented, it doesn't exist

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

Inspired by the coordination challenges of real-world multi-agent AI development. Built with the philosophy that good tooling should be invisible.

---

**Stop losing context. Start collaborating.**
