# Workflow: Release Check

**Trigger:** Before tagging a new version or merging significant changes.

## Purpose

Validate that the release aligns with PACK's North Star and doesn't introduce friction.

## Procedure

### 1. North Star Alignment (5 min)

Review `.pde/MANIFEST.md` and answer:

- [ ] Does this release reduce friction? (Required)
- [ ] Does this release preserve context? (Required)
- [ ] Does this release maintain portability? (Required)

**If any answer is "no", reconsider the release.**

### 2. Simplicity Tax Check (5 min)

For each new feature or change:

| Change | Adds Complexity? | Reduces Net Complexity? | Pass? |
|--------|------------------|-------------------------|-------|
| | | | |

**Every addition must reduce net complexity to pass.**

### 3. Portability Verification (5 min)

- [ ] No new dependencies added
- [ ] No platform-specific code
- [ ] Python 3.8+ compatible
- [ ] Works on macOS, Linux, Windows

### 4. Friction Audit (15 min)

Run the full friction audit workflow:

```bash
cat .pde/workflows/friction_audit.md
```

### 5. Context Preservation (5 min)

- [ ] Handoff log format unchanged (backwards compatible)
- [ ] No files deleted that users might reference
- [ ] Migration path documented if breaking changes

### 6. Documentation Sync (5 min)

- [ ] README reflects current state
- [ ] .agent/README matches reality
- [ ] All new features documented
- [ ] No references to removed features

### 7. Dogfood Test (10 min)

Deploy PACK to a fresh directory and use it:

```bash
mkdir /tmp/test-pack && python3 deploy_agent_kit.py --dest /tmp/test-pack
cd /tmp/test-pack
python3 .agent/tools/utilities/update_agent_conversation_log.py \
  --agent tester --summary "Release check" --handoff human
```

## Release Checklist

```
[ ] North Star alignment verified
[ ] Simplicity tax paid (net complexity reduced)
[ ] Portability maintained
[ ] Friction audit passed
[ ] Context preservation verified
[ ] Documentation synced
[ ] Dogfood test passed
```

## Output

- If all checks pass: Proceed with release
- If any check fails: Fix before release, no exceptions
