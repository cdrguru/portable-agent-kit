# Gemini CLI Integration

Optional integration for using Google Gemini CLI as a specialized Auditor agent.

## Prerequisites

- Gemini CLI v0.24.0 or higher: `npm install -g @google/gemini-cli`
- Google account with Gemini API access

## Quick Start

1. Initialize Gemini CLI for this project:
   ```bash
   # Follow the gemini-cli-init skill procedure
   python3 .agent/tools/utilities/skills.py show gemini-cli-init
   ```

2. Run an audit:
   ```bash
   python3 .agent/tools/utilities/gemini_audit.py --auto
   # Or use the shell script:
   ./.agent/tools/bin/audit_task.sh
   ```

## Configuration

### Project Settings

Copy `settings.json.template` to your project's `.gemini/settings.json`:

```bash
mkdir -p .gemini
cp .agent/gemini/settings.json.template .gemini/settings.json
```

Customize as needed for your project.

### Persona

The auditor persona is defined in `personas/auditor.md`. This file is loaded as the system instruction when running Gemini CLI in auditor mode.

## Files

| File | Purpose |
|------|---------|
| `settings.json.template` | Template for project-level Gemini configuration |
| `personas/auditor.md` | System instruction for auditor persona |
| `README.md` | This file |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_SYSTEM_MD` | Path to persona file (set automatically by scripts) |
| `GEMINI_MODEL` | Model to use (default: gemini-2.5-pro) |

## Related Skills

- `gemini-cli-init`: Initialize Gemini CLI integration
- `gemini-audit`: Run audit workflow via Gemini CLI
