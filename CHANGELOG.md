# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2025-12-21

### Added

- Initial release of Portable Agent Collaboration Kit
- `AGENTS.md` - Agent roster and coordination rules
- `multi_agent_orchestration_system.md` - Shared orchestration protocol
- `agent_handshake.md` - Task locking and handoff mechanics
- `update_agent_conversation_log.py` - CLI utility for logging handoffs
- `deploy_agent_kit.py` - Deployment script with `--dest`, `--force`, `--dry-run` flags
- `conversation.compact.md.template` - Local session log template
- Append-only handoff log in `.agent/docs/agent_handoffs/`

### Features

- Zero dependencies (Python stdlib only)
- Model-agnostic (works with any AI)
- ASCII-only content for maximum compatibility
- Comprehensive CLI for handoff logging
- Dry-run mode for safe deployment previews
