# PDE → .agent Integration Manifest

**Date**: 2026-01-19
**Status**: Complete

## Migration Summary

The Paul Davis Experience (PDE) system has been successfully integrated into the `.agent/` framework.

## File Inventory

### Agent Profiles

| Source | Target | Status |
| ------ | ------ | ------ |
| `.pde/agents/ruthless_prioritizer.md` | `.agent/profiles/ruthless_prioritizer.md` | ✅ Migrated |
| `.pde/agents/librarian.md` | `.agent/profiles/librarian.md` | ✅ Migrated |

### Workflows

| Source | Target | Status |
| ------ | ------ | ------ |
| `.pde/workflows/daily_startup.md` | `.agent/workflows/daily_startup.md` | ✅ Migrated |
| `.pde/workflows/brain_dump.md` | `.agent/workflows/brain_dump.md` | ✅ Migrated |

### State Files

| Source | Target | Status |
| ------ | ------ | ------ |
| `.pde/state/active_tasks.md` | `.agent/state/active_tasks.md` | ✅ Migrated |
| `.pde/state/metrics.md` | `.agent/state/metrics.md` | ✅ Migrated |
| `.pde/state/inbox.md` | `.agent/state/inbox.md` | ✅ Migrated |
| `.pde/state/daily/.gitkeep` | `.agent/state/daily/.gitkeep` | ✅ Migrated |

### Manifest & Documentation

| Source | Target | Status |
| ------ | ------ | ------ |
| `.pde/MANIFEST.md` | `.agent/MANIFEST.md` | ✅ Migrated |
| `.pde/README.md` | `.agent/pde/README.md` | ✅ Migrated |
| `.pde/INSTALL.md` | `.agent/pde/INSTALL.md` | ✅ Migrated |

### New Directories Created

| Directory | Purpose |
| --------- | ------- |
| `.agent/profiles/` | Agent profile definitions |
| `.agent/state/` | Task tracking and metrics |
| `.agent/state/daily/` | Daily roadmap logs |
| `.agent/knowledge/` | Atomic knowledge notes |
| `.agent/pde/` | Original PDE documentation |

## Path Transformations

All internal references updated from `.pde/` to `.agent/`:

- `ruthless_prioritizer.md`: `.pde/MANIFEST.md` → `.agent/MANIFEST.md`
- `librarian.md`: `.pde/knowledge/` → `.agent/knowledge/`
- `daily_startup.md`: All state paths updated
- `brain_dump.md`: All state paths updated
- `MANIFEST.md`: Component table paths updated

## Verification Checks

| Check | Result |
| ----- | ------ |
| All target files exist | ✅ Pass |
| No absolute paths (`/Users/`) | ✅ Pass |
| AGENTS.md updated (append only) | ✅ Pass |
| No file collisions | ✅ Pass |

## AGENTS.md Updates

The following agents were appended to `.agent/AGENTS.md`:

1. **ruthless-prioritizer** - Focus protection agent with KEEP/KILL decision tree
2. **librarian** - Knowledge compounding agent for extracting reusable assets

Also added:
- PDE Workflows table
- PDE State Files table

## Original Source Preserved

The original `.pde/` directory remains intact. It can be safely removed after confirming the integration works correctly:

```bash
# After verification, optionally remove:
# rm -rf .pde/
```
