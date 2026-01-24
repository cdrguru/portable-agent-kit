# THE STRATEGIC LAYER: Portable Agent Kit (PACK)

## 1. The Obsessional Goal (North Star)

**Make agent coordination so seamless it disappears.**

> "Good tooling should be invisible." - PACK Philosophy

The measure of success is not adoption, features, or protocol compliance. It is:

* **Zero friction** from task start to productive work
* **Zero context loss** between sessions or agents
* **Zero ceremony** that doesn't directly enable collaboration

## 2. The Constraints (The Filter)

* **Simplicity Tax:** Every new feature must reduce net complexity. If adding X requires explaining Y, reconsider X.
* **Portability Mandate:** No dependencies. No platform-specific code. If it doesn't work everywhere, it doesn't ship.
* **Append-Only Truth:** Never delete collaboration history. Context is sacred.

## 3. Tie-Breaking Heuristics

When two approaches seem equal:

1. **Friction Priority:** Choose the path with fewer user steps.
2. **Recovery Priority:** Choose the path that fails gracefully and preserves state.
3. **Silence Priority:** Choose the path that requires less explanation.

## 4. System Components

| Type | Name | Purpose | Location |
|:-----|:-----|:--------|:---------|
| **Agent** | Friction Hunter | Identify and eliminate coordination pain points | `.pde/agents/friction_hunter.md` |
| **Agent** | Context Preserver | Ensure no context is lost between handoffs | `.pde/agents/context_preserver.md` |
| **Workflow** | Friction Audit | Periodic review of user experience | `.pde/workflows/friction_audit.md` |
| **Workflow** | Release Check | Pre-release validation against North Star | `.pde/workflows/release_check.md` |
| **State** | Friction Log | Running list of identified pain points | `.pde/state/friction_log.md` |
| **State** | Roadmap | Prioritized improvements | `.pde/state/roadmap.md` |

## 5. Harmony with .agent

The `.pde/` layer is **strategic** (why and what). The `.agent/` layer is **operational** (how).

```
.pde/           <- Strategic: Goals, constraints, direction
  MANIFEST.md   <- North Star for the project itself
  agents/       <- Meta-agents for maintaining PACK
  workflows/    <- Rituals for PACK development
  state/        <- PACK project state

.agent/         <- Operational: Coordination protocol
  AGENTS.md     <- Roles for users of PACK
  skills/       <- Procedures for users of PACK
  tools/        <- Utilities for users of PACK
```

The PDE governs how we build PACK. The .agent governs how users use PACK.

## 6. Evolution Principle

* **Friction is Signal:** If users struggle, the kit is wrong, not the users.
* **Dogfooding Required:** Use PACK to build PACK.
* **Quarterly Review:** Revisit this Manifest every quarter.
