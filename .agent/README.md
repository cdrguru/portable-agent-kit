# Portable Agent Collaboration Kit

A **zero-dependency, model-agnostic** kit for enabling consistent multi-agent collaboration in any repository.

---

## What This Kit Provides

| Component | Purpose |
|-----------|---------|
| `AGENTS.md` | Agent roster, roles, and coordination rules |
| `ai/prompts/multi_agent_orchestration_system.md` | Shared orchestration protocol |
| `ai/rules/agent_handshake.md` | Task locking and handoff mechanics |
| `.agent/docs/agent_handoffs/` | Append-only handoff log |
| `conversation.compact.md.template` | Template for local session logs |
| `tools/utilities/update_agent_conversation_log.py` | CLI helper for logging handoffs |

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
|   +-- ai/
|   |   +-- prompts/
|   |   |   +-- multi_agent_orchestration_system.md
|   |   +-- rules/
|   |       +-- agent_handshake.md
|   +-- docs/
|   |   +-- agent_handoffs/
|   |       +-- README.md
|   |       +-- agent_conversation_log.md
|   +-- tools/
|       +-- utilities/
|           +-- update_agent_conversation_log.py
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
