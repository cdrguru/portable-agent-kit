# Portable Agent Collaboration Kit

A **zero-dependency, model-agnostic** kit for enabling consistent multi-agent collaboration in any repository.

---

## What This Kit Provides

| Component | Purpose |
|-----------|---------|
| `AGENTS.md` | Agent roster, roles, and coordination rules |
| `ai/prompts/multi_agent_orchestration_system.md` | Shared orchestration protocol |
| `ai/prompts/agent_profiles/` | Role profiles for codex/ag/hp |
| `ai/rules/agent_handshake.md` | Task locking and handoff mechanics |
| `context/agent_environment.md` | Shared roles + interaction policy |
| `.agent/docs/agent_handoffs/` | Append-only handoff log |
| `conversation.compact.md.template` | Template for local session logs |
| `skills/` | Optional skills (repeatable workflows) |
| `tools/utilities/update_agent_conversation_log.py` | CLI helper for logging handoffs |
| `tools/utilities/print_agent_init.py` | Print a combined session-init prompt |
| `tools/utilities/skills.py` | List/show/search skills |

---

## Quick Install

### Option 1: Using the Deploy Script

From the kit source repository:

```bash
python3 deploy_agent_kit.py --dest /path/to/your/repo
```

Flags:

- `--force` - Overwrite existing files
- `--dry-run` - Preview what would be copied

### Option 2: Manual Copy

Copy the `.agent/` folder to your repository root:

```bash
cp -r .agent /path/to/your/repo/
```

Then ensure your `.gitignore` includes:

```
conversation.compact.md
.reports/
```

---

## Post-Install Customization

1. **Edit `AGENTS.md`**:
   - Rename agent roles to match your team
   - Update file paths for your project structure
   - Add repo-specific commands (test, lint, build)

2. **Edit `ai/prompts/multi_agent_orchestration_system.md`**:
   - Replace placeholder project context
   - Keep the required sections (Goal, Constraints, Exit Criteria)

3. **Set environment variables** (optional):

   ```bash
   export PROJECT_NAME="my-project"
   export AGENT_CONVERSATION_LOG=".agent/docs/agent_handoffs/agent_conversation_log.md"
   ```

---

## Usage

### Recording a Handoff

```bash
python3 .agent/tools/utilities/update_agent_conversation_log.py \
  --agent builder \
  --summary "Implemented feature X; tests passing" \
  --handoff reviewer \
  --task "Review auth flow" \
  --reference "src/feature.py" \
  --reference "tests/test_feature.py"
```

### Starting a Session

1. Copy the template to create your local log:

   ```bash
   cp .agent/conversation.compact.md.template conversation.compact.md
   ```

2. Update the objective and start logging changes

3. The local log is gitignored - use it freely for session notes

---

## Using Skills (Optional)

List available skills and show a skill procedure (print for copy/paste):

```bash
python3 .agent/tools/utilities/skills.py list
python3 .agent/tools/utilities/skills.py show handoff-log-update
```

---

## Gemini CLI Integration (Optional)

The kit includes optional integration with Google Gemini CLI for automated plan auditing.

### Prerequisites

- Gemini CLI v0.24.0+: `npm install -g @google/gemini-cli`
- **Node.js v20+**: Required for the latest models. Use `nvm install 20 && nvm use 20` if necessary.
- Google account with Gemini API access

### Setup

Initialize Gemini CLI integration using the skill (recommended):

```bash
python3 .agent/tools/utilities/skills.py show gemini-cli-init
```

Or manually:

```bash
mkdir -p .gemini/personas
cp .agent/gemini/settings.json.template .gemini/settings.json
cp .agent/gemini/personas/auditor.md .gemini/personas/auditor.md
export GEMINI_SYSTEM_MD="./.gemini/personas/auditor.md"
```

### Running an Audit

Before implementing a plan, run the Gemini auditor:

```bash
python3 .agent/tools/utilities/gemini_audit.py --auto
# Or use the shell script:
./.agent/tools/bin/audit_task.sh
```

The auditor will:

1. Read `.agent/task.md` and `.agent/implementation_plan.md`
2. Validate alignment between task and plan
3. Output APPROVE / REJECT / NEEDS_INFO decision
4. Log result to agent_conversation_log.md

See `.agent/gemini/README.md` for full documentation.

---

## Key Principles

1. **Append-only logs**: Never edit or delete handoff entries
2. **Minimal diffs**: Keep changes focused and justified
3. **Cite file paths**: Always reference affected files
4. **Simplicity audit**: Before completing, ask "Is this as simple as possible?"

---

## Communication Conventions

Use these prefixes for clarity:

```
Decision: We will use approach X because...
Action: Implement function Y in file Z
Question: Should we support edge case W?
```

---

## File Structure After Install

```text
your-repo/
+-- .agent/
|   +-- AGENTS.md
|   +-- README.md (this file)
|   +-- conversation.compact.md.template
|   +-- skills/
|   |   +-- README.md
|   |   +-- SKILL.md.template
|   |   +-- handoff-log-update/
|   |   |   +-- SKILL.md
|   |   +-- handoff-log-condense/
|   |   |   +-- SKILL.md
|   |   +-- session-bootstrap/
|   |       +-- SKILL.md
|   +-- context/
|   |   +-- agent_environment.md
|   +-- ai/
|   |   +-- prompts/
|   |   |   +-- multi_agent_orchestration_system.md
|   |   |   +-- agent_profiles/
|   |   +-- rules/
|   |       +-- agent_handshake.md
|   +-- docs/
|   |   +-- agent_handoffs/
|   |       +-- README.md
|   |       +-- agent_conversation_log.md
|   +-- tools/
|       +-- utilities/
|           +-- update_agent_conversation_log.py
|           +-- print_agent_init.py
|           +-- skills.py
+-- conversation.compact.md (gitignored, created per session)
+-- .gitignore (updated to ignore local logs)
```

---

## Compatibility

- **Python**: 3.8+ (stdlib only)
- **AI Models**: Any (Gemini, Claude, GPT, Codex, local LLMs)
- **Platforms**: macOS, Linux, Windows

---

*Portable Agent Collaboration Kit v1.0.0*
