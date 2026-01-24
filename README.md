# Portable Agent Collaboration Kit (PACK)

> **A zero-dependency framework for multi-agent AI collaboration and strategic project alignment.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![Node.js 20+](https://img.shields.io/badge/node-20+-brightgreen.svg)](#requirements)

---

## Why This Kit?

Modern AI-assisted development involving multiple agents (planners, coders, reviewers, auditors) requires more than just code; it requires **strategic orchestration**. Without clear coordination:

- Agents overwrite each other's work
- Context "drifts" from the original requirements
- Handoffs are unclear and messy
- Environmental friction (Node versions, script paths) blocks progress

**PACK solves these problems** with a dual-layer framework: an **Operational Layer** (`.agent/`) for day-to-day work, and a **Strategic Layer** (`.pde/`) for maintaining project integrity.

---

## Features

| Feature | Description |
|---------|-------------|
| **Model-Agnostic** | Works with Claude, GPT, Gemini, local LLMs, or any AI |
| **PDE Strategy Engine** | Keep your project aligned with its "North Star" (`.pde/`) |
| **Agentic Auditing** | Optional Gemini-powered architecture and plan reviewer |
| **Skill System** | Repeatable playbooks (bootstrap, logs, gemini-audit) |
| **Unified Setup** | One command to bootstrap any repository |
| **Zero Dependencies** | Pure Python stdlib - no pip install needed |
| **ASCII-Only** | Maximum compatibility across systems and editors |
| **Append-Only Logs** | Preserve collaboration history, never lose context |

---

## Quick Start

### 1. Install & Deploy

```bash
python3 deploy_agent_kit.py --dest /path/to/your/repo
```

### 2. Unified Initialization

For a fresh repository, run the all-in-one setup:

```bash
./.agent/tools/bin/pack-init.sh
```

### 3. Start Collaborating

1. Set your project name: `export PROJECT_NAME="my-project"`
2. Edit `.agent/AGENTS.md` to define your agent roles.

---

## The Dual-Layer Architecture

### Layer 1: Operational (`.agent/`)

The **Operational Layer** handles asynchronous coordination between agents.

- **`AGENTS.md`**: Roster of roles (Builder, Planner, Auditor).
- **`HANDOFF.md`**: Current state of the active session.
- **`skills/`**: Reusable workflows (e.g., `gemini-audit`).

### Layer 2: Strategic (`.pde/`)

The **PACK Development Engine (PDE)** provides structural maintenance for the kit itself.

- **`MANIFEST.md`**: The project's North Star and quarterly objectives.
- **`friction_log.md`**: Tracking and resolving workflow pain points.
- **`roadmap.md`**: Strategic evolution of the collaboration model.

---

## What's Included

```text
.
+-- .agent/                       # Operational coordination
|   +-- AGENTS.md                 # Agent roster and rules
|   +-- skills/                   # Repeatable workflows
|   +-- ai/                       # Persona profiles & protocols
|   +-- tools/
|       +-- bin/
|           +-- pack-init.sh      # Unified setup script
|           +-- audit_task.sh     # Headless auditor
+-- .pde/                         # Strategic alignment (maintainers)
|   +-- MANIFEST.md               # The North Star
|   +-- state/                    # friction_log, roadmap
+-- deploy_agent_kit.py           # Installer script
+-- lmstudio_mcp.py               # Context-aware offline model bridge
```

---

## Usage Highlights

### Recording a Handoff

```bash
python3 .agent/tools/utilities/update_agent_conversation_log.py \
  --agent builder \
  --summary "Implemented login feature" \
  --handoff reviewer
```

### Context-Aware Offline AI

If using **LM Studio**, the `lmstudio_mcp.py` bridge includes a **`get_pack_context`** tool, allowing local models to "reach into" the `.agent` folder to read the current task and handoff state automatically.

---

## Requirements

- **Python 3.8+** (uses only standard library)
- **Node.js v20+** (required for Gemini CLI integration)
- **Any AI Model**: Claude, GPT, Gemini, Codex, or local LLMs

---

## License

MIT License - see [LICENSE](LICENSE) details.

---

**Stop losing context. Start collaborating.**
