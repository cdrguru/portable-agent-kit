# Agent Handoffs

Coordination folder for agent handoffs and conversation logs.

**Last Updated**: 2025-12-21  
**Status**: Active coordination folder

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `agent_conversation_log.md` | Append-only handoff log (primary coordination) |
| `README.md` | This file |

---

## Usage

### Appending Entries

Use the helper script to add handoff entries:

```bash
python3 .agent/tools/utilities/update_agent_conversation_log.py \
  --agent <name> \
  --summary "Short description of what was done" \
  --handoff <next_agent|human> \
  --task "Follow-up item 1" \
  --task "Follow-up item 2" \
  --reference "path/to/file.py"
```

### Manual Entry Format

If adding entries manually, use this format:

```
=== MESSAGE BOUNDARY ===
TimestampUTC: 2025-01-01T12:00:00Z
Project: [PROJECT_NAME]
Agent: builder
Role: assistant
Status: ready
HandoffTo: reviewer

Summary: Implemented feature X with tests

Tasks:
- Review implementation in src/feature.py
- Run test suite

References:
- src/feature.py
- tests/test_feature.py
```

---

## Rules

1. **Append-only**: Never edit or delete existing entries
2. **Timestamps**: Always use UTC
3. **References**: Always include file paths
4. **Keep it short**: 3 bullets max per section

---

## Archiving

Periodically move old entries to `archive/` subdirectory to keep the main log manageable.

---

*Template Version: 1.0.0 | Portable Agent Collaboration Kit*
