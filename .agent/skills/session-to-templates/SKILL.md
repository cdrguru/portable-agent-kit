---
name: session-to-templates
description: Extract reusable prompt templates from AI coding assistant session files using LLM-powered analysis.
metadata:
  short-description: Mine prompt templates from coding sessions
---

# Session to Templates

## When to use

Use when you want to mine reusable prompt templates from past AI coding sessions.
The script discovers session files, scores them for signal strength, samples key
turns, and uses an LLM to extract structured prompt templates.

Triggering phrases: "extract templates from sessions", "mine my Claude sessions",
"turn conversations into prompts", "batch process sessions", or `$session-to-templates`.

## Prerequisites

This skill bundles a Python script that requires:

- Python 3.10+
- `requests` (HTTP client for LLM API calls)
- `python-dotenv` (loads `.env` configuration)
- An LLM API key (Azure OpenAI by default, or any OpenAI-compatible endpoint)

Install dependencies:

```bash
pip install requests python-dotenv
```

Configure environment variables (in `.env` or shell):

```bash
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5-mini
```

## Procedure

### Phase 1: Locate session files

1. Review the storage reference to understand where sessions live:

```bash
cat .agent/skills/session-to-templates/references/claude-storage-paths.md
```

Session files are typically at `~/.claude/projects/` as `.jsonl` files.

### Phase 2: Preview (read-only scan)

2. Run the script in index-only mode to see what sessions exist:

```bash
python3 .agent/skills/session-to-templates/scripts/batch-session-to-templates.py \
  --index-only
```

This lists sessions with scores but does not call the LLM.

3. Optionally use the session index for faster discovery:

```bash
python3 .agent/skills/session-to-templates/scripts/batch-session-to-templates.py \
  --use-index --index-only
```

### Phase 3: Extract templates

4. Run extraction with filters to control scope:

```bash
# Last 7 days, top 25 by score
python3 .agent/skills/session-to-templates/scripts/batch-session-to-templates.py \
  --days 7 --top 25 --azure

# Filter by project name
python3 .agent/skills/session-to-templates/scripts/batch-session-to-templates.py \
  --project my-project --azure

# Only high-signal sessions
python3 .agent/skills/session-to-templates/scripts/batch-session-to-templates.py \
  --min-score 35 --azure

# Custom output directory
python3 .agent/skills/session-to-templates/scripts/batch-session-to-templates.py \
  --days 30 --output ./prompts_inbox/claude_templates --azure
```

The script supports resume -- previously processed sessions are tracked in
`.manifest.json` and skipped on re-runs.

### Phase 4: Curate output

5. Review the generated templates in the output directory:

```bash
ls prompts_inbox/claude_templates/
```

Each template follows a structured schema with frontmatter (description, category,
complexity, tags) and sections (Purpose, Context, Task, Variables, Constraints,
Success Criteria, Common Pitfalls, Expected Output, Example Invocation).

6. Move good templates to your prompt library and discard low-quality ones.

## Key flags

| Flag | Purpose |
| --- | --- |
| `--index-only` | Preview mode -- list and score sessions without LLM calls |
| `--days N` | Only process sessions from the last N days |
| `--project NAME` | Filter by project path substring |
| `--top N` | Keep only the N highest-scoring sessions |
| `--min-score N` | Minimum signal score threshold |
| `--limit N` | Maximum number of sessions to process |
| `--output DIR` | Custom output directory |
| `--use-index` | Use sessions-index.json for faster discovery |
| `--azure` | Use Azure OpenAI endpoint (default LLM backend) |
| `--all` | Process all sessions regardless of date |

## Pipeline internals

The script operates in 6 phases:

1. **Discovery** -- Scans `~/.claude/projects/` for `.jsonl` session files
2. **Parsing** -- Extracts user/assistant messages, strips bootstrap/system noise
3. **Scoring** -- Rates sessions on signal strength (message depth, code blocks, tool usage, content volume)
4. **Sampling** -- For long conversations, selects head + tail + key turns (outcome signals like "created", "fixed", "implemented")
5. **Extraction** -- Sends sampled conversation to LLM with a structured extraction prompt
6. **Output** -- Saves templates with metadata, tracks processed sessions for resume

## Inputs and outputs

- Inputs: AI coding session directory (default `~/.claude/projects/`), LLM API credentials
- Outputs: Structured prompt templates in markdown with frontmatter

## Constraints

- Read-only against session files -- never modifies source sessions
- Requires an LLM API for template extraction (not zero-dependency)
- Supports resume via `.manifest.json` -- safe to re-run
- ASCII-only output filenames
- Templates follow a fixed schema (frontmatter + 9 sections)

## Examples

- $session-to-templates
