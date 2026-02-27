---
name: agentic-audit
description: Audit a repository against a 24-item agentic development checklist covering safety, permissions, secrets, concurrency, telemetry, and runbooks.
metadata:
  short-description: Audit repo for agentic development best practices
---

# Agentic Development Audit

## When to use

Use when onboarding a repository for AI-assisted (agentic/vibe coding) development, or when
verifying that an existing repo meets safety and governance standards for multi-agent workflows.

Triggering phrases: "audit for agentic development", "check vibe coding compliance",
"run the agentic checklist", or `$agentic-audit`.

## Procedure

1. Run the evidence-gathering commands below for each of the 24 checklist items.
2. Mark each item as PASS, PARTIAL, FAIL, or UNKNOWN.
3. Generate a structured report (see Output Format).
4. For FAIL items, reference the bundled templates in `templates/` as starting points.
5. Optionally populate `templates/remediation-queue.yaml.template` for parallel remediation.

## Inputs and outputs

- Inputs: A git repository to audit (run from the repository root)
- Outputs: Markdown audit report with scores, gaps, and remediation recommendations

## Constraints

- Read-only audit -- do not modify any files during the audit phase
- ASCII-only output
- Model-agnostic -- works with any AI coding assistant
- Human approval required before any remediation changes

---

## Checklist Items (24)

### A) Agentic Lifecycle Guardrails

#### A1: Plan-before-execute workflow (MUST)

**Check for:** `--permission-mode plan` in docs, scripts, Makefile, or shell aliases

```bash
grep -r "permission-mode plan" . --include="*.md" --include="*.sh" --include="Makefile" 2>/dev/null
grep -r "opusplan" . --include="*.md" --include="*.sh" --include="Makefile" 2>/dev/null
```

**Pass:** Documented workflow or wrapper script enforces plan mode for initial task ingestion
**Fail:** No tooling to enforce plan mode; agents default to auto-accept editing

#### A2: Human merge gate (MUST)

**Check for:** Branch protection, `CODEOWNERS`, or CI requiring human approval

```bash
cat .github/CODEOWNERS 2>/dev/null
ls .github/workflows/*.yml 2>/dev/null
```

**Pass:** At least one human approval required for merges to main branch
**Fail:** Agents can autonomously merge to production without human review

#### A3: Deterministic rollback (MUST)

**Check for:** Runbooks with `git restore`, `git reset`, `git revert`, `git reflog`

```bash
grep -r "git restore\|git reset\|git revert\|git reflog" docs/ --include="*.md" 2>/dev/null
find docs/ -name "*rollback*" -o -name "*emergency*" 2>/dev/null
```

**Pass:** Explicit Git commands documented for uncommitted, committed, pushed, and corrupted states
**Fail:** No documented rollback procedures

---

### B) Model Routing, Version Pinning, Economics

#### B1: Routing strategy (SHOULD)

**Check for:** Dual-model routing (e.g., opusplan alias)

```bash
grep -r "opusplan\|opus.*plan\|sonnet.*build" . --include="Makefile" --include="*.sh" 2>/dev/null
```

**Pass:** Tooling bifurcates a stronger model for planning, faster model for execution
**Fail:** Single model for all tasks

#### B2: Version pinning (MUST)

**Check for:** Model version environment variables with date-stamped IDs

```bash
grep -r "ANTHROPIC_DEFAULT_.*_MODEL\|MODEL_VERSION\|model.*pin" . --include=".env*" --include="*.json" 2>/dev/null
cat .env.example 2>/dev/null | grep -i "model"
```

**Pass:** Environment variables pin models to immutable date-stamped IDs
**Fail:** Configuration uses dynamic aliases

#### B3: Token governance (MUST)

**Check for:** Token usage monitoring integration

```bash
grep -r "ccusage\|claude-code-usage\|token.*budget\|cost.*monitor" . --include="*.sh" --include="*.md" --include="Makefile" 2>/dev/null
```

**Pass:** Token monitoring documented and integrated into developer workflow
**Fail:** No local token monitoring; relies on delayed cloud billing

---

### C) Permissions, Sandboxing, Hooks

#### C1: Deny-first permission matrix (MUST)

**Check for:** Settings file with explicit allow/deny arrays

```bash
cat .claude/settings.json 2>/dev/null
cat .agent/ai/rules/*.md 2>/dev/null | head -50
```

**Pass:** Matrix exists with deny-first posture, blocks destructive commands
**Fail:** Missing settings or overly permissive configuration

#### C2: OS sandboxing (MUST)

**Check for:** `sandbox-exec` (macOS) or `bwrap`/`bubblewrap` (Linux) wrapper scripts

```bash
grep -r "sandbox-exec\|bwrap\|bubblewrap" . --include="*.sh" --include="Makefile" 2>/dev/null
find scripts/ -name "*sandbox*" 2>/dev/null
```

**Pass:** Execution scripts wrap AI coding assistant in OS sandbox
**Fail:** AI assistant runs directly on host without isolation

#### C3: PreToolUse hook (MUST)

**Check for:** Hook script with `jq`, regex patterns, `exit 2`

```bash
ls .claude/hooks/ 2>/dev/null
cat .claude/hooks/pre_tool_use.sh 2>/dev/null
cat .claude/hooks.json 2>/dev/null
```

**Pass:** Deterministic hook parses JSON, blocks destructive commands, exits with code 2
**Fail:** Relies on probabilistic LLM instructions instead of shell script intercept

---

### D) Repo Integrity and Secret Prevention

#### D1: Pre-commit hooks (MUST)

**Check for:** `.pre-commit-config.yaml` with security hooks

```bash
cat .pre-commit-config.yaml 2>/dev/null
```

**Pass:** Hooks include `check-merge-conflict`, `check-added-large-files`, `detect-private-key`
**Fail:** No pre-commit hooks or missing security hooks

#### D2: Secret scanning - Gitleaks (SHOULD - Option 1)

**Check for:** `gitleaks` in pre-commit config or `.gitleaks.toml`

```bash
grep "gitleaks" .pre-commit-config.yaml 2>/dev/null
ls .gitleaks.toml 2>/dev/null
```

**Pass:** Gitleaks configured as pre-commit hook
**Fail:** No Gitleaks (acceptable if D3 is used)

#### D3: Secret scanning - detect-secrets (SHOULD - Option 2)

**Check for:** `detect-secrets` in pre-commit config and `.secrets.baseline`

```bash
grep "detect-secrets" .pre-commit-config.yaml 2>/dev/null
ls .secrets.baseline 2>/dev/null
```

**Pass:** detect-secrets configured with baseline file
**Fail:** No detect-secrets (acceptable if D2 is used)

#### D4: CI enforcement backstop (MUST)

**Check for:** Secret scanning in CI pipeline

```bash
grep -r "gitleaks\|trufflehog\|secret" .github/workflows/ --include="*.yml" 2>/dev/null
```

**Pass:** CI includes mandatory secret scanning step on PRs
**Fail:** Secret scanning relies solely on bypassable local hooks

---

### E) Concurrency Management

#### E1: Git worktree workflow (MUST)

**Check for:** `git worktree add/remove` in docs or scripts

```bash
grep -r "git worktree" . --include="*.md" --include="*.sh" 2>/dev/null
find docs/ -name "*worktree*" 2>/dev/null
```

**Pass:** Documentation standardizes worktree-based agent isolation
**Fail:** Multiple agents share the same directory

#### E2: Task decomposition rules (MUST)

**Check for:** Module ownership rules in contributing docs

```bash
cat CONTRIBUTING.md 2>/dev/null | head -100
grep -r "module ownership\|task decomposition\|file ownership" docs/ --include="*.md" 2>/dev/null
```

**Pass:** Explicit rules forbid agents from working on sequential dependencies simultaneously
**Fail:** No guidelines for task decomposition

#### E3: Main integration worktree (MUST)

**Check for:** Integration hub workflow documentation

```bash
grep -r "integration hub\|main worktree\|human.*merge" docs/ --include="*.md" 2>/dev/null
```

**Pass:** One worktree designated for human-led integration
**Fail:** Agents merge directly into each other's worktrees

---

### F) Risk-Tiered Review

#### F1: Red/Yellow/Green classification (MUST)

**Check for:** Path restrictions in `CODEOWNERS` or CI scripts

```bash
cat .github/CODEOWNERS 2>/dev/null
grep -r "red\|yellow\|green" .github/ --include="*.yml" --include="CODEOWNERS" -i 2>/dev/null
```

**Pass:** Paths mapped to Red (auth, security), Yellow (API), Green (docs)
**Fail:** All PRs treated equally

#### F2: Auto-approve Green diffs (MUST)

**Check for:** Conditional auto-merge workflow

```bash
ls .github/workflows/auto-approve*.yml 2>/dev/null
grep -r "auto-approve\|auto-merge" .github/workflows/ --include="*.yml" 2>/dev/null
```

**Pass:** Auto-merge gated on CI success, no Red/Yellow paths, no secrets
**Fail:** Auto-merge enabled globally or lacks path restrictions

---

### G) Telemetry and MCP

#### G1: MCP observability (MUST)

**Check for:** Sentry/Slack MCP in settings or documentation

```bash
cat .mcp.json 2>/dev/null
cat .mcp.json.example 2>/dev/null
grep -r "mcp.*sentry\|mcp.*slack" . --include="*.json" --include="*.md" -i 2>/dev/null
```

**Pass:** MCP servers configured for telemetry backends
**Fail:** Manual copy-paste of stack traces required

#### G2: Daily triage workflow (SHOULD)

**Check for:** Script automating error triage

```bash
find scripts/ -name "*triage*" 2>/dev/null
grep -r "sentry.*24h\|daily.*triage\|unresolved.*issues" . --include="*.sh" --include="*.md" 2>/dev/null
```

**Pass:** Automated script executes triage prompt
**Fail:** Triage is entirely manual

#### G3: PII redaction pipeline (MUST)

**Check for:** Presidio or NLP masking in config

```bash
grep -r "presidio\|pii.*redact\|anonymizer" . --include="*.yml" --include="*.yaml" --include="docker-compose*" -i 2>/dev/null
```

**Pass:** Explicit NLP redaction step before data enters LLM context
**Fail:** Raw PII exposed to observability backend and LLM

---

### H) Memory Architecture

#### H1: Root instructions file (MUST)

**Check for:** Concise, stable instructions file (CLAUDE.md, .cursorrules, etc.)

```bash
ls -la CLAUDE.md .cursorrules AGENTS.md 2>/dev/null
wc -l CLAUDE.md 2>/dev/null
```

**Pass:** File exists and is optimized (<500 lines), contains stable rules only
**Fail:** Bloated with tutorials, external API docs, or styling rules

#### H2: Path-scoped rules (MUST)

**Check for:** Rules directory with domain-specific files

```bash
ls .claude/rules/ .agent/ai/rules/ 2>/dev/null
```

**Pass:** Rules directory exists with topic-specific files
**Fail:** All rules dumped into root instructions file

#### H3: Local overrides (MUST)

**Check for:** Local override files in `.gitignore`

```bash
grep "CLAUDE.local.md\|settings.local" .gitignore 2>/dev/null
```

**Pass:** Local overrides separated and ignored by version control
**Fail:** Local context bleeds into global repository

---

### I) Runbooks and Adoption

#### I1: Operational runbooks (MUST)

**Check for:** Start-of-Day, New Feature, Emergency Stop, Rollback, Weekly Maintenance

```bash
ls docs/runbooks/ 2>/dev/null
find docs/ -name "*runbook*" -o -name "*start-of-day*" -o -name "*rollback*" -o -name "*maintenance*" 2>/dev/null
```

**Pass:** All five runbooks exist with specific operational steps
**Fail:** Missing runbooks

#### I2: 30/60/90 adoption plan (MUST)

**Check for:** Phased adoption and KPI scorecard documentation

```bash
find docs/ -name "*adoption*" -o -name "*kpi*" -o -name "*30-60-90*" 2>/dev/null
grep -r "30.*60.*90\|KPI.*scorecard\|phased.*adoption" docs/ --include="*.md" 2>/dev/null
```

**Pass:** Framework and KPI metrics explicitly documented
**Fail:** No structured adoption plan

---

## Template Reference

This skill bundles templates in `templates/` for remediating failed items.
Copy to the target path and customize for the repository.

| Checklist Item | Template | Target Path |
| --- | --- | --- |
| C3: PreToolUse hook | `templates/pre-tool-use-hook.sh.template` | `.claude/hooks/pre_tool_use.sh` |
| C3: Hook registration | `templates/hooks.json.template` | `.claude/hooks.json` |
| C1: Permission matrix | `templates/settings.json.template` | `.claude/settings.json` |
| G1: MCP observability | `templates/mcp-config.json.template` | `.mcp.json` |
| C2: OS sandboxing | `templates/sandbox-wrapper.sh.template` | `scripts/sandbox_claude.sh` |
| B1: Model routing | `templates/makefile-routing.snippet` | Append to `Makefile` |
| F1: Risk tiers | `templates/codeowners.template` | `.github/CODEOWNERS` |
| A3: Rollback | `templates/emergency-stop.md.template` | `docs/runbooks/emergency-stop.md` |
| F2: Auto-approve | `templates/auto-approve-workflow.yml.template` | `.github/workflows/auto-approve.yml` |
| Audit worksheet | `templates/checklist.md.template` | Copy to repo root |
| Remediation queue | `templates/remediation-queue.yaml.template` | `tasks/swarm/queue.yaml` |

---

## Output Format

Generate a markdown report:

```text
# Agentic Development Audit Report

**Repository:** {repo_path}
**Date:** {date}
**Score:** {pass_count} PASS / {partial_count} PARTIAL / {fail_count} FAIL / {unknown_count} UNKNOWN

## Summary Table

| ID | Priority | Item | Status | Evidence |
|:---|:---------|:-----|:------:|:---------|
| A1 | MUST | Plan-before-execute | PASS/PARTIAL/FAIL | {evidence_notes} |
...

## Critical Gaps

{List FAIL items with priority MUST}

## Recommendations

{Prioritized remediation steps, referencing templates/}

## Files to Create/Modify

| Action | Path | Template |
|--------|------|----------|
| CREATE | `.claude/hooks/pre_tool_use.sh` | pre-tool-use-hook.sh.template |
...
```

---

## Quick Audit Commands

Run these read-only commands to gather evidence rapidly:

```bash
# Permission matrix
cat .claude/settings.json 2>/dev/null || echo "NOT FOUND"

# Version pinning
grep -r "MODEL" . --include=".env*" 2>/dev/null

# PreToolUse hook
cat .claude/hooks/pre_tool_use.sh 2>/dev/null || echo "NOT FOUND"

# Pre-commit and secrets
cat .pre-commit-config.yaml 2>/dev/null
ls .secrets.baseline 2>/dev/null

# Git worktree docs
grep -r "git worktree" docs/ 2>/dev/null

# Instructions file architecture
ls -la CLAUDE.md .cursorrules .agent/MANIFEST.md 2>/dev/null
ls .claude/rules/ .agent/ai/rules/ 2>/dev/null
grep "CLAUDE.local.md\|settings.local" .gitignore 2>/dev/null

# Token governance
grep -r "ccusage\|opusplan\|token.*budget" . 2>/dev/null

# Sandboxing
grep -r "sandbox-exec\|bwrap" scripts/ 2>/dev/null

# Runbooks and KPIs
ls docs/runbooks/ 2>/dev/null
find docs/ -name "*adoption*" -o -name "*kpi*" 2>/dev/null

# MCP and telemetry
cat .mcp.json.example 2>/dev/null
grep -r "presidio" docker-compose* 2>/dev/null
```

## Examples

- $agentic-audit
