# Goal

Add a **Prompt Attribution & Clarification Protocol** to this repository's agent/AI conventions. This protocol ensures all agents know who authored a prompt, whether it was interpreted from speech-to-text, and when to pause for clarification instead of executing on potentially compounded misinterpretations.

---

> **Prompt Origin:** Human-authored (direct text)
> **Interpretation Confidence:** High
> **Clarification Recommended:** No

---

# Context Inputs

- **Primary file to update**: `${InstructionsFile}` (e.g., `.github/copilot-instructions.md`, `CLAUDE.md`, `AGENTS.md`, or equivalent)
- **Fallback**: If no agent instructions file exists, create one at `${InstructionsFile}`
- **Style reference**: Match existing formatting conventions in the target file

# Problem Being Solved

When prompts pass through multiple interpretation layers:

```
Human (speech) → Speech-to-text → AI rewrite → Executing agent
```

Each layer can introduce errors. Without attribution, the executing agent:
- Doesn't know the original source was speech (error-prone)
- Doesn't know an AI rewrote it (potential misinterpretation)
- Executes confidently on compounded errors
- Has no signal to pause and ask for clarification

# Constraints & Style

- Keep the rule concise (agents should parse it quickly)
- Use a structured format that's easy to copy into prompts
- Define when clarification is **required** vs **recommended**
- Match the tone and formatting of existing documentation in the repo

# Plan Shape

1. Identify the appropriate agent instructions file (or create one)
2. Add new section: `## Prompt Attribution & Clarification Protocol`
3. Define the **Prompt Origin block** format
4. Define **clarification triggers** (when agents must ask before executing)
5. Add examples of good attribution and ambiguous cases
6. If multiple agent files exist, add cross-references

# Protocol Content to Add

```markdown
## Prompt Attribution & Clarification Protocol

When a prompt passes through interpretation layers (speech → transcription → AI rewrite → executing agent), each layer can introduce errors. This protocol prevents agents from executing confidently on compounded misinterpretations.

### Prompt Origin Block

When an AI agent rewrites or interprets a human prompt, include this block immediately after the Goal heading:

> **Prompt Origin:** [Source description]
> **Interpretation Confidence:** [High | Medium | Low]
> **Clarification Recommended:** [Yes/No — if Yes, list specific unclear points]

**Source descriptions** (use the most specific that applies):

| Tag | Meaning |
|-----|---------|
| `Human-authored (direct text)` | Typed by human, no interpretation layer |
| `Interpreted from human speech-to-text` | Transcribed speech, may contain errors |
| `AI-generated (model: X)` | Written entirely by an AI agent |
| `AI-rewritten from human speech-to-text (model: X)` | AI interpreted transcribed speech |

### Clarification Triggers

**MUST ask before executing if:**
- Prompt Origin indicates speech-to-text AND Interpretation Confidence is Medium or Low
- Instructions contain logical contradictions
- Key terms are ambiguous (e.g., "run them again" without a clear antecedent)
- Scope is unclear (affects 1 file vs many files)

**SHOULD ask before executing if:**
- Prompt was AI-rewritten and you disagree with the interpretation
- You're about to make destructive changes (delete, overwrite, force-push)
- Direction seems uncertain and the task has broad scope

### Example: AI-Rewritten Prompt

> **Prompt Origin:** AI-rewritten from human speech-to-text (GitHub Copilot, Claude Opus 4.5)
> **Interpretation Confidence:** Medium
> **Clarification Recommended:** Yes — "run them again" is ambiguous. Does "them" refer to the tests or the scripts?

### Example: Direct Human Prompt

Direct human-typed prompts with clear instructions do not require a Prompt Origin block. If you add one:

> **Prompt Origin:** Human-authored (direct text)
> **Interpretation Confidence:** High
> **Clarification Recommended:** No
```

# Tool Policy

- Search for existing agent instruction files first
- Read target file to understand existing structure before modifying
- Do not modify unrelated sections

# Exit Criteria

- Protocol section added to appropriate file with clear formatting
- Clarification triggers are specific and actionable
- Examples show both good attribution and ambiguous cases
- Protocol integrates with existing documentation style

# Review Checklist

- [ ] Identified correct file for agent instructions
- [ ] Section fits stylistically with existing content
- [ ] Prompt Origin block format is copy-paste ready
- [ ] Clarification triggers distinguish MUST vs SHOULD
- [ ] Examples cover common scenarios
- [ ] No excessive friction (agents shouldn't ask about everything)

# Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `${InstructionsFile}` | Path to agent instructions file | `.github/copilot-instructions.md`, `CLAUDE.md`, `AGENTS.md` |
