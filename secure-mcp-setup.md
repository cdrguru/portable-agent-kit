# Secure MCP Environment: Setup Guide

> **Architecture**: "Isolation by Copy"
> **Scope**: Filesystem-Only (Read/Search)
> **Root**: `$HOME/AI/workspaces` (customize for your system)

---

## 1. Onboarding Your Code (Clean Copy)

To work on a repo safely, you must create a secret-stripped copy in the AI workspace.

**Run this in Terminal:**

```bash
./scripts/ai-onboard.sh [repo_name]
```

> **Security Guarantee**:
>
> - Strips `.git`, `.env`, secrets, and huge build folders.
> - Scans for secrets with `gitleaks` before finalizing.
> - **The AI never sees your original files.**

---

## 2. Configure MCP Connector

Use this JSON block in your AI tool's MCP configuration.

### Connector A: Secure Filesystem

**Server Name**: `secure-filesystem`

```json
{
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "<YOUR_WORKSPACE_PATH>"
  ],
  "env": {},
  "useBuiltInNode": true
}
```

> **Model**: Read/Search/Analyze.
> **Isolation**: The AI is physically confined to the workspace folder. It cannot see parent directories or system files.

---

## 3. Workflow Recipe

| Step | Action | Command |
|------|--------|---------|
| **1. Prep** | "I want the AI to analyze Repo X" | `./scripts/ai-onboard.sh RepoX` |
| **2. Research** | Ask AI to read code | "Analyze `portable-agent-kit/README.md`..." |
| **3. Fix** | Apply code changes | **Manually apply** suggestions to your *real* repo |

---

## 4. Smoke Tests (Final Verified Set)

1. **Verify Visibility**:
   `Using the filesystem, list the contents of the 'portable-agent-kit' folder.`
   *(Should succeed if onboarded)*

2. **Verify Secret Absence**:
   `Using the filesystem, search for "API_KEY" in the workspace. Report count + paths only.`
   *(Should return 0 matches)*

3. **Verify Boundary**:
   `Using the filesystem, try to list the parent directory.`
   *(Should FAIL - blocked by server scope)*

---

## 5. Session Closure

- **Changed**: Removed iTerm connector entirely.
- **Support**: Strictly filesystem-only analysis via MCP.
- **Agentic Support**: Fully compatible with **Gemini CLI** (Auditor) and **Claude Code** (Executor).
- **Out of Scope**: No direct terminal execution from agents (safety decision).
- **Onboarding**: Use `ai-onboard.sh` to mirror repos safely into the sandbox.

**Status**: SECURE & VERIFIED
