#!/usr/bin/env python3
"""
Batch Claude Code Session to Prompt Template Processor

Indexes Claude Code CLI sessions and generates a reusable prompt template for each session.
Each template captures the problem-solving pattern in a one-shot format that can
replicate the outcome without trial-and-error.

Adapted from batch_codex_to_templates.py for Claude Code's session format.

Usage:
    # Index only (preview mode)
    python batch_claude_to_templates.py --index-only

    # Generate templates for last 7 days
    python batch_claude_to_templates.py --days 7 --output ./templates --azure

    # Generate all templates
    python batch_claude_to_templates.py --all --output ./templates --azure

    # Limit to N sessions
    python batch_claude_to_templates.py --days 30 --limit 10 --output ./templates --azure

    # Pick only the highest-signal sessions
    python batch_claude_to_templates.py --top 25 --azure

    # Filter by score threshold
    python batch_claude_to_templates.py --min-score 35 --azure

    # Filter by project path substring
    python batch_claude_to_templates.py --project pd-prompt-lib-mgr --azure

    # Use session index for faster scanning
    python batch_claude_to_templates.py --use-index --index-only
"""

import argparse
import hashlib
import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv(override=True)

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5-mini")

# Generation defaults (optimized for deterministic, low-latency extraction)
AZURE_TEMPERATURE = float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0"))
AZURE_TOP_P = float(os.getenv("AZURE_OPENAI_TOP_P", "1"))
AZURE_PRESENCE_PENALTY = float(os.getenv("AZURE_OPENAI_PRESENCE_PENALTY", "0"))
AZURE_FREQUENCY_PENALTY = float(os.getenv("AZURE_OPENAI_FREQUENCY_PENALTY", "0"))
AZURE_REASONING_EFFORT = os.getenv("AZURE_OPENAI_REASONING_EFFORT", "minimal")
AZURE_MAX_COMPLETION_TOKENS = int(os.getenv("AZURE_OPENAI_MAX_COMPLETION_TOKENS", "6000"))

# Default paths
DEFAULT_CLAUDE_PATH = "~/.claude/projects"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "prompts_inbox" / "claude_templates"


def find_claude_sessions(
    base_path: str, days: Optional[int] = None, project_filter: Optional[str] = None
) -> List[Path]:
    """Find all Claude Code session JSONL files."""
    base_path = os.path.expanduser(base_path)
    if not os.path.exists(base_path):
        print(f"Error: Path not found: {base_path}")
        return []

    base_dir = Path(base_path)
    all_files: List[Path] = []

    for project_dir in base_dir.iterdir():
        if not project_dir.is_dir():
            continue

        # Filter by project name if specified
        if project_filter and project_filter not in project_dir.name:
            continue

        for f in project_dir.glob("*.jsonl"):
            all_files.append(f)

    print(f"Found {len(all_files)} session files")

    if days is not None:
        cutoff = datetime.now() - timedelta(days=days)
        filtered = [f for f in all_files if datetime.fromtimestamp(f.stat().st_mtime) > cutoff]
        print(f"Filtering by date (last {days} days): {len(filtered)} sessions match")
        return filtered

    return all_files


def find_sessions_from_index(
    base_path: str, days: Optional[int] = None, project_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Use sessions-index.json files for fast session discovery."""
    base_path = os.path.expanduser(base_path)
    if not os.path.exists(base_path):
        print(f"Error: Path not found: {base_path}")
        return []

    base_dir = Path(base_path)
    index_entries: List[Dict[str, Any]] = []

    for project_dir in base_dir.iterdir():
        if not project_dir.is_dir():
            continue

        if project_filter and project_filter not in project_dir.name:
            continue

        index_file = project_dir / "sessions-index.json"
        if not index_file.exists():
            continue

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                index_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        original_path = index_data.get("originalPath", "")

        for entry in index_data.get("entries", []):
            entry["_originalPath"] = original_path
            entry["_projectDir"] = str(project_dir)
            index_entries.append(entry)

    print(f"Found {len(index_entries)} sessions via index")

    if days is not None:
        cutoff = datetime.now() - timedelta(days=days)
        filtered = []
        for entry in index_entries:
            created = entry.get("created")
            if created:
                try:
                    ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if ts.timestamp() > cutoff.timestamp():
                        filtered.append(entry)
                except Exception:
                    pass
        print(f"Filtering by date (last {days} days): {len(filtered)} sessions match")
        return filtered

    return index_entries


def parse_iso_timestamp(value: Optional[str]) -> Optional[float]:
    """Parse an ISO timestamp to epoch seconds."""
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).timestamp()
    except Exception:
        return None


def extract_message_text(content: Any) -> str:
    """Extract displayable text from a Claude Code message content block.

    Claude Code stores content as an array of typed blocks:
      - {"type": "text", "text": "..."}
      - {"type": "thinking", "thinking": "..."}
      - {"type": "tool_use", "name": "...", "input": {...}}
      - {"type": "tool_result", "content": "..."}
      - {"type": "ide_opened_file", ...}
      - {"type": "ide_selection", ...}

    We extract only text blocks for template purposes.
    """
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, dict):
        if content.get("type") == "text":
            return (content.get("text") or "").strip()
        return ""

    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
        return "\n".join(parts).strip()

    return ""


def extract_tool_summary(content: Any) -> List[str]:
    """Extract a summary of tool calls from message content."""
    tools: List[str] = []
    if not isinstance(content, list):
        return tools

    for item in content:
        if isinstance(item, dict) and item.get("type") == "tool_use":
            name = item.get("name", "unknown")
            inp = item.get("input", {})
            # Summarize tool call briefly
            if name in ("Bash", "ShellTool"):
                cmd = inp.get("command", "")[:60]
                tools.append(f"[{name}: {cmd}]")
            elif name in ("Read", "ReadFileTool"):
                path = inp.get("file_path", "")
                tools.append(f"[{name}: {path}]")
            elif name in ("Write", "WriteFileTool"):
                path = inp.get("file_path", "")
                tools.append(f"[{name}: {path}]")
            elif name in ("Edit", "EditTool"):
                path = inp.get("file_path", "")
                tools.append(f"[{name}: {path}]")
            elif name in ("Grep", "Glob"):
                pattern = inp.get("pattern", "")[:40]
                tools.append(f"[{name}: {pattern}]")
            elif name == "WebSearch":
                query = inp.get("query", "")[:40]
                tools.append(f"[{name}: {query}]")
            elif name == "Task":
                desc = inp.get("description", "")[:40]
                tools.append(f"[{name}: {desc}]")
            else:
                tools.append(f"[{name}]")

    return tools


def strip_ide_context(text: str) -> str:
    """Remove IDE context tags from message text, returning the user's actual input."""
    # Strip <ide_opened_file>...</ide_opened_file> tags
    cleaned = re.sub(r"<ide_opened_file>.*?</ide_opened_file>\s*", "", text, flags=re.DOTALL)
    # Strip <ide_selection>...</ide_selection> tags
    cleaned = re.sub(r"<ide_selection>.*?</ide_selection>\s*", "", cleaned, flags=re.DOTALL)
    # Strip <system-reminder>...</system-reminder> tags
    cleaned = re.sub(r"<system-reminder>.*?</system-reminder>\s*", "", cleaned, flags=re.DOTALL)
    # Strip <command-message>...</command-message> tags
    cleaned = re.sub(r"<command-message>.*?</command-message>\s*", "", cleaned, flags=re.DOTALL)
    return cleaned.strip()


def is_bootstrap_message(text: str) -> bool:
    """Detect standard Claude Code bootstrap/system messages to skip."""
    stripped = text.lstrip()
    # System reminder tags injected by Claude Code
    if "<system-reminder>" in stripped:
        return True
    # Empty content markers
    if stripped == "(no content)":
        return True
    # After stripping IDE context, if nothing remains, it's bootstrap
    cleaned = strip_ide_context(stripped)
    if not cleaned:
        return True
    return False


def parse_claude_session(session_file: Path, skip_bootstrap: bool = True) -> Optional[Dict]:
    """Parse a Claude Code session JSONL file."""
    try:
        messages: List[Dict[str, str]] = []
        tool_summaries: List[str] = []
        session_id = session_file.stem
        session_timestamp = None
        cwd = None
        model = None

        with open(session_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                entry_type = entry.get("type")

                # Skip non-message entries
                if entry_type in ("queue-operation", "file-history-snapshot", "summary"):
                    continue

                if entry_type not in ("user", "assistant"):
                    continue

                # Extract metadata
                if session_timestamp is None:
                    session_timestamp = parse_iso_timestamp(entry.get("timestamp"))

                if cwd is None:
                    cwd = entry.get("cwd")

                if entry.get("sessionId"):
                    session_id = entry["sessionId"]

                # Extract message content
                message = entry.get("message", {})
                role = message.get("role") or entry_type
                content = message.get("content")

                if role not in ("user", "assistant"):
                    continue

                # Track model used
                if role == "assistant" and message.get("model"):
                    model = message["model"]

                # Extract tool call summaries from assistant messages
                if role == "assistant" and isinstance(content, list):
                    tools = extract_tool_summary(content)
                    tool_summaries.extend(tools)

                text = extract_message_text(content)
                if not text:
                    continue

                if skip_bootstrap and role == "user" and is_bootstrap_message(text):
                    continue

                # Strip IDE context from user messages for cleaner templates
                if role == "user":
                    text = strip_ide_context(text)
                    if not text:
                        continue

                messages.append({"role": role, "content": text})

        if not messages:
            return None

        if session_timestamp is None:
            session_timestamp = session_file.stat().st_mtime

        return {
            "session_id": session_id,
            "timestamp": session_timestamp,
            "file_path": str(session_file),
            "cwd": cwd,
            "model": model,
            "message_count": len(messages),
            "tool_count": len(tool_summaries),
            "tool_summaries": tool_summaries[:20],  # Cap for display
            "messages": messages,
        }
    except Exception as e:
        print(f"Warning: Error parsing {session_file.name}: {e}")
        return None


def score_session(messages: List[Dict[str, str]], tool_count: int = 0) -> float:
    """Score a session for uniqueness/impact based on heuristic signals."""
    message_count = len(messages)
    user_messages = [m["content"] for m in messages if m["role"] == "user"]
    assistant_messages = [m["content"] for m in messages if m["role"] == "assistant"]

    total_chars = sum(len(m["content"]) for m in messages)
    user_chars = sum(len(m) for m in user_messages)
    assistant_chars = sum(len(m) for m in assistant_messages)

    text_all = "\n".join(m["content"] for m in messages)
    text_lower = text_all.lower()

    file_path_re = re.compile(r"([A-Za-z]:\\\\[^\s]+|/[^\s]+)")
    code_block_re = re.compile(r"```")
    list_re = re.compile(r"(?m)^(\s*(?:[-*]|\d+\.)\s+)")

    outcome_keywords = (
        "created", "saved", "wrote", "implemented", "refactor",
        "fixed", "audit", "report", "analysis", "strategy",
        "plan", "pipeline", "workflow", "template", "prompt",
        "checklist", "framework", "design", "architecture",
    )
    pde_keywords = ("prompt", "template", "agent", "system", "policy", "evaluation", "rubric")
    boilerplate_markers = (
        "you are a helpful assistant",
        "context from my ide setup",
        "environment_context",
        "(no content)",
    )

    score = 0.0

    # Message depth signal
    score += min(message_count, 20) * 1.5
    # Content volume signal
    score += min(total_chars / 300.0, 25)
    # Assistant did real work
    if assistant_chars > user_chars:
        score += 4.0
    if assistant_chars > 1500:
        score += 4.0
    # Tool usage is a strong signal for Claude Code sessions
    score += min(tool_count, 15) * 1.0

    # Content quality signals
    if file_path_re.search(text_all):
        score += 6.0
    if code_block_re.search(text_all):
        score += 8.0
    if list_re.search(text_all):
        score += 6.0
    if any(k in text_lower for k in outcome_keywords):
        score += 6.0
    if any(k in text_lower for k in pde_keywords):
        score += 4.0

    # Penalty signals
    if message_count <= 2:
        score -= 10.0
    if total_chars < 300:
        score -= 8.0
    if assistant_chars < 200:
        score -= 6.0
    if any(marker in text_lower for marker in boilerplate_markers):
        score -= 10.0

    return round(score, 1)


TEMPLATE_EXTRACTION_PROMPT = """You are an expert AI Prompt Engineer specializing in the Prompt Distillation and Reconstruction (PDR) method. Your task is to analyze this Claude Code CLI conversation and transform it into an optimized, reusable prompt template.

NOTE: The conversation may use head+tail+key-turn sampling. Sections marked "KEY TURNS" contain resolution/outcome signals. Sections marked "FINAL EXCHANGES" contain the session conclusion. Use ALL sections to understand the full arc from problem to solution.

## Method Overview

1. Analytical Decomposition: Dissect the conversation to identify the core problem, successful strategy, dead ends, and essential variables.
2. Systematic Reconstruction: Build an optimized one-shot prompt template that captures the winning strategy and includes a concrete worked example.

## Phase 1: Analytical Decomposition

Analyze the conversation to identify:
- Core Goal: What was the user actually trying to achieve?
- Successful Strategy: What steps/patterns actually worked? (Ignore dead ends)
- Dead Ends / Pitfalls: What approaches failed or caused problems? What should future users avoid?
- Essential Variables: What values are specific to this session and must be placeholders?
- Constraints: What rules or context were determining factors?
- Tools Used: What Claude Code tools were leveraged (Bash, Read, Write, Edit, Grep, Task, etc.)?
- Outcome: What was the concrete result? Files created, bugs fixed, deployments made?
- Complexity: How many steps, tools, and files were involved? Was multi-turn reasoning required?

## Phase 2: Systematic Reconstruction

Create an optimized prompt template following the strict schema below.

OUTPUT FORMAT:

### 1. Analysis
- Goal: [1 sentence summary]
- Strategy: [Brief bullet points of the winning approach]
- Dead Ends: [What didn't work and why — or "None" if straightforward]
- Variables: [List of identified variables]
- Tools: [Which Claude Code tools were central to the solution]
- Outcome: [What was concretely produced]

### 2. Optimized Prompt
```markdown
---
description: [Verb phrase, max 80 chars - what this template accomplishes]
source_type: claude_code_conversation
category: [bugfix | feature | refactor | config | documentation | research | debugging | deployment | workflow | other]
complexity: [low | medium | high]
recommended_model: [any | sonnet | opus]
estimated_turns: [single | multi]
tags: [comma-separated lowercase tags, 3-6 tags, e.g. git, merge, workflow, multi-branch]
---

# [Template Title - Verb Object format]

## Purpose
[1-2 sentences explaining when to use this template]

## Context
[Distilled context needed - what the AI needs to know before solving]

## Task
[Clear imperative instruction - the core ask, with numbered steps]

## Variables
- [VARIABLE_NAME]: [description of what to substitute]
[List 3-7 key variables]

## Constraints
- [Extracted constraint or requirement]
[List 2-5 constraints]

## Success Criteria
- [ ] [Concrete, verifiable condition that confirms the task is done]
- [ ] [Another condition]
[List 3-5 checkable criteria. These must be specific and testable, not vague.]

## Common Pitfalls
- [Pitfall extracted from dead ends in the conversation, or common mistake to avoid]
[List 1-3 pitfalls. If none, write "None identified — straightforward execution."]

## Expected Output
[What format/structure the response should have]

## Example Invocation
[Show this template filled in with ACTUAL values from the original session. Replace every [PLACEHOLDER] with the real value that was used. This serves as a one-shot reference for how to use the template. Keep it concise — just the Variables section filled in plus a 1-2 sentence description of the specific scenario.]
```

RULES:
1. Replace ALL specific values with [UPPERCASE_PLACEHOLDER] notation in the template body.
2. The Example Invocation section MUST use the real values from this session to demonstrate usage.
3. The template must be self-contained and executable.
4. Success Criteria must be concrete and verifiable (e.g., "file X exists", "tests pass", "command returns 0"), not vague (e.g., "code is clean").
5. Common Pitfalls should capture real lessons from the conversation's dead ends or error recovery.
6. Tags should be specific enough to enable search/filtering (e.g., "youtube, transcript, api" not just "script").
7. Complexity: low = single file/command, medium = multi-file or multi-step, high = architectural or multi-system.
8. Recommended model: "any" for simple tasks, "sonnet" for multi-file code tasks, "opus" for architectural/research.
9. Eliminate ambiguity and redundancy.
10. If the conversation is too short, trivial, or has no reusable pattern, return "No Template Extracted" inside the markdown block.
"""


OUTCOME_SIGNALS = re.compile(
    r"\b(created|saved|wrote|implemented|fixed|resolved|completed|committed|"
    r"works now|done|merged|deployed|verified|passing|success)\b",
    re.IGNORECASE,
)


def _select_key_turns(messages: List[Dict[str, str]], max_chars: int = 12000) -> List[Dict[str, str]]:
    """Select the most informative turns using head + tail + key-turn sampling.

    Strategy:
    - Head: first 3 exchanges (problem statement + initial approach)
    - Tail: last 4 exchanges (resolution + outcome)
    - Key turns: messages containing outcome signals (created, fixed, etc.)
    - Dedup and respect char budget.
    """
    if not messages:
        return []

    total_msg_chars = sum(len(m["content"]) for m in messages)

    # Short conversations: return everything (trimmed per-message)
    if total_msg_chars <= max_chars or len(messages) <= 14:
        return messages

    # --- Head: first 6 messages (≈3 exchanges) ---
    head = messages[:6]

    # --- Tail: last 8 messages (≈4 exchanges) ---
    tail = messages[-8:]

    # --- Key turns: messages with outcome signals (not already in head/tail) ---
    head_tail_indices = set(range(6)) | set(range(len(messages) - 8, len(messages)))
    key_turns = []
    for i, msg in enumerate(messages):
        if i in head_tail_indices:
            continue
        if OUTCOME_SIGNALS.search(msg["content"][:500]):
            key_turns.append(msg)

    # Budget: allocate ~4K head, ~5K tail, ~3K key turns
    head_budget = max_chars * 35 // 100
    tail_budget = max_chars * 40 // 100
    key_budget = max_chars * 25 // 100

    def trim_section(section: List[Dict[str, str]], budget: int) -> List[str]:
        lines = []
        used = 0
        for msg in section:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            content = msg["content"][:1500]
            line = f"{role}: {content}"
            if used + len(line) > budget:
                break
            lines.append(line)
            used += len(line)
        return lines

    head_lines = trim_section(head, head_budget)
    tail_lines = trim_section(tail, tail_budget)
    key_lines = trim_section(key_turns[:6], key_budget)  # cap at 6 key turns

    # Assemble with section markers
    parts = []
    parts.extend(head_lines)
    if key_lines:
        parts.append("\n--- [KEY TURNS: resolution & outcome signals] ---\n")
        parts.extend(key_lines)
    if tail_lines and len(messages) > 14:
        parts.append("\n--- [FINAL EXCHANGES: session conclusion] ---\n")
        parts.extend(tail_lines)

    return parts  # returns List[str] — handled by caller


def create_template_prompt(messages: List[Dict[str, str]], tool_summaries: List[str] = None) -> str:
    """Create a prompt for the AI to extract a template from the conversation.

    Uses head+tail+key-turn sampling to ensure the extraction model sees both
    the problem statement AND the resolution/outcome.
    """
    max_chars = 12000

    total_msg_chars = sum(len(m["content"]) for m in messages)

    if total_msg_chars <= max_chars or len(messages) <= 14:
        # Short conversation: linear assembly
        conversation_lines: List[str] = []
        total_chars = 0
        for msg in messages:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            content = msg["content"][:1500]
            line = f"{role}: {content}"
            if total_chars + len(line) > max_chars:
                conversation_lines.append("... [conversation truncated]")
                break
            conversation_lines.append(line)
            total_chars += len(line)
        conversation_text = "\n\n".join(conversation_lines)
    else:
        # Long conversation: smart sampling
        sampled = _select_key_turns(messages, max_chars=max_chars)
        conversation_text = "\n\n".join(sampled)

    # Add tool context if available
    tool_context = ""
    if tool_summaries:
        tool_context = "\n\nTOOLS USED IN SESSION:\n" + "\n".join(tool_summaries[:20])

    session_stats = (
        f"\n\nSESSION STATS: {len(messages)} messages total, "
        f"{sum(1 for m in messages if m['role'] == 'user')} user turns, "
        f"{sum(1 for m in messages if m['role'] == 'assistant')} assistant turns"
    )

    return f"""Analyze this Claude Code conversation and extract a reusable prompt template:

CONVERSATION:
{conversation_text}
{tool_context}
{session_stats}

Extract the reusable template following the format specified."""


def extract_template_azure(
    messages: List[Dict[str, str]],
    tool_summaries: List[str] = None,
    deployment: str = None,
    verbose: bool = False,
) -> Optional[str]:
    """Use Azure OpenAI to extract a template from the conversation.

    Supports two endpoint formats:
    - OpenAI-compatible: {base}/openai/v1/chat/completions (model in body)
    - Standard Azure: {base}/openai/deployments/{name}/chat/completions?api-version=...
    """
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        print("Error: Azure OpenAI credentials not configured in .env file")
        return None

    deploy_name = deployment or AZURE_OPENAI_DEPLOYMENT
    endpoint = AZURE_OPENAI_ENDPOINT.rstrip("/")

    # Detect OpenAI-compatible endpoint (ends with /openai/v1)
    if endpoint.endswith("/openai/v1") or endpoint.endswith("/openai/v1/"):
        url = f"{endpoint.rstrip('/')}/chat/completions"
        use_openai_compat = True
    else:
        # Standard Azure deployment URL
        for suffix in ["/openai/v1", "/openai"]:
            if endpoint.endswith(suffix):
                endpoint = endpoint[: -len(suffix)]
                break
        url = f"{endpoint}/openai/deployments/{deploy_name}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
        use_openai_compat = False

    if verbose:
        print(f"Azure endpoint: {url[:80]}...")
        print(f"Mode: {'OpenAI-compatible' if use_openai_compat else 'Standard Azure'}")

    if use_openai_compat:
        headers = {
            "Authorization": f"Bearer {AZURE_OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
    else:
        headers = {
            "api-key": AZURE_OPENAI_API_KEY,
            "Content-Type": "application/json",
        }

    base_payload = {
        "messages": [
            {"role": "system", "content": TEMPLATE_EXTRACTION_PROMPT},
            {"role": "user", "content": create_template_prompt(messages, tool_summaries)},
        ],
        "max_completion_tokens": AZURE_MAX_COMPLETION_TOKENS,
        "temperature": AZURE_TEMPERATURE,
        "top_p": AZURE_TOP_P,
        "presence_penalty": AZURE_PRESENCE_PENALTY,
        "frequency_penalty": AZURE_FREQUENCY_PENALTY,
        "n": 1,
    }

    # OpenAI-compat format passes model in body
    if use_openai_compat:
        base_payload["model"] = deploy_name

    payload = dict(base_payload)
    if AZURE_REASONING_EFFORT:
        payload["reasoning_effort"] = AZURE_REASONING_EFFORT

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 400:
                if verbose:
                    print("API rejected parameters; retrying with minimal payload")
                payload2 = {
                    "messages": base_payload["messages"],
                    "max_completion_tokens": base_payload["max_completion_tokens"],
                }
                # Preserve model for OpenAI-compat format
                if use_openai_compat:
                    payload2["model"] = deploy_name
                response = requests.post(url, headers=headers, json=payload2, timeout=90)
                response.raise_for_status()
            else:
                raise

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        if not content or content.strip() == "":
            if verbose:
                print("Azure returned empty content")
            return None

        match = re.search(r"```markdown(.*?)```", content, re.DOTALL)
        if match:
            content = match.group(1).strip()
        else:
            match = re.search(r"```(.*?)```", content, re.DOTALL)
            if match:
                content = match.group(1).strip()
            else:
                content = content.strip()

        return content.strip()

    except requests.exceptions.RequestException as e:
        print(f"Azure API error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def generate_filename(topic: str, session_id: str) -> str:
    """Generate a safe filename from the topic."""
    clean = re.sub(r"[^\w\s-]", "", topic.lower())
    clean = re.sub(r"[\s_]+", "-", clean)
    clean = clean[:50].strip("-")

    if not clean:
        clean = session_id[:12]

    return f"{clean}-prompt.md"


def extract_topic_from_template(template: str) -> str:
    """Extract the title/topic from a generated template."""
    match = re.search(r"^#\s+(.+)$", template, re.MULTILINE)
    if match:
        return match.group(1).strip()

    match = re.search(r"^description:\s*(.+)$", template, re.MULTILINE)
    if match:
        return match.group(1).strip()

    return "untitled"


def compute_content_hash(messages: List[Dict[str, str]]) -> str:
    """Compute a hash of the conversation content for caching."""
    content = json.dumps(messages, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def load_existing_hashes(output_dir: Path) -> set:
    """Load content hashes from existing template files to support resume."""
    hashes = set()
    manifest_file = output_dir / ".manifest.json"

    if manifest_file.exists():
        try:
            with open(manifest_file, "r") as f:
                manifest = json.load(f)
                hashes = set(manifest.get("processed_hashes", []))
        except Exception:
            pass

    return hashes


def save_manifest(output_dir: Path, hashes: set, stats: Dict[str, int]) -> None:
    """Save manifest with processed hashes and stats."""
    manifest_file = output_dir / ".manifest.json"
    manifest = {
        "last_run": datetime.now().isoformat(),
        "processed_hashes": list(hashes),
        "stats": stats,
    }

    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)


def index_sessions(
    base_path: str,
    days: Optional[int] = None,
    limit: Optional[int] = None,
    skip_bootstrap: bool = True,
    top_n: Optional[int] = None,
    min_score: Optional[float] = None,
    project_filter: Optional[str] = None,
    use_index: bool = False,
) -> List[Dict[str, Any]]:
    """Index all sessions and return parsed session data."""
    print("\nScanning for Claude Code sessions...")

    if use_index:
        index_entries = find_sessions_from_index(base_path, days=days, project_filter=project_filter)
        if not index_entries:
            print("No sessions found via index.")
            return []

        sessions = []
        for entry in index_entries:
            full_path = entry.get("fullPath")
            if not full_path or not Path(full_path).exists():
                continue
            parsed = parse_claude_session(Path(full_path), skip_bootstrap=skip_bootstrap)
            if parsed and parsed.get("messages"):
                # Enrich with index metadata
                parsed["first_prompt"] = entry.get("firstPrompt", "")
                parsed["project_path"] = entry.get("_originalPath", "")
                parsed["git_branch"] = entry.get("gitBranch", "")
                parsed["score"] = score_session(parsed["messages"], parsed.get("tool_count", 0))
                sessions.append(parsed)
    else:
        session_files = find_claude_sessions(base_path, days=days, project_filter=project_filter)
        if not session_files:
            print("No sessions found.")
            return []

        sessions = []
        for sf in session_files:
            parsed = parse_claude_session(sf, skip_bootstrap=skip_bootstrap)
            if parsed and parsed.get("messages"):
                parsed["score"] = score_session(parsed["messages"], parsed.get("tool_count", 0))
                sessions.append(parsed)

    if min_score is not None:
        sessions = [s for s in sessions if s.get("score", 0) >= min_score]

    if top_n:
        sessions.sort(key=lambda s: (s.get("score", 0), s.get("timestamp", 0)), reverse=True)
        sessions = sessions[:top_n]
    else:
        sessions.sort(key=lambda s: s.get("timestamp", 0), reverse=True)
        if limit:
            sessions = sessions[:limit]

    return sessions


def display_index(sessions: List[Dict[str, Any]]) -> None:
    """Display a summary of indexed sessions."""
    print("\nClaude Code Session Index")
    print(f"Total sessions with content: {len(sessions)}")
    print()

    if not sessions:
        return

    print(f"{'#':<4} {'Score':<7} {'Msgs':<6} {'Tools':<7} {'Date':<12} {'Model':<20} {'First User Message':<45}")
    print(f"{'-'*4} {'-'*7} {'-'*6} {'-'*7} {'-'*12} {'-'*20} {'-'*45}")

    for i, session in enumerate(sessions[:30], 1):
        msg_count = session.get("message_count", 0)
        tool_count = session.get("tool_count", 0)
        score = session.get("score", 0)
        ts = session.get("timestamp", 0)
        model = session.get("model", "unknown") or "unknown"

        # Shorten model name for display
        model_short = model.replace("claude-", "").replace("-20251101", "")[:18]

        if isinstance(ts, (int, float)) and ts > 0:
            date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        else:
            date_str = "unknown"

        first_user = next(
            (
                m["content"][:42] + "..." if len(m["content"]) > 45 else m["content"]
                for m in session.get("messages", [])
                if m["role"] == "user"
            ),
            "[no user message]",
        )
        first_user = first_user.replace("\n", " ").strip()

        print(f"{i:<4} {score:<7} {msg_count:<6} {tool_count:<7} {date_str:<12} {model_short:<20} {first_user:<45}")

    if len(sessions) > 30:
        print(f"\n... and {len(sessions) - 30} more sessions")


def process_sessions(
    sessions: List[Dict[str, Any]],
    output_dir: Path,
    use_azure: bool = True,
    deployment: str = None,
    verbose: bool = False,
    dry_run: bool = False,
) -> Dict[str, int]:
    """Process all sessions and generate templates."""
    stats = {
        "total": len(sessions),
        "processed": 0,
        "skipped": 0,
        "failed": 0,
        "exploratory": 0,
    }

    if not sessions:
        print("\nNo sessions to process.")
        return stats

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    existing_hashes = load_existing_hashes(output_dir) if not dry_run else set()

    print(f"\nProcessing {len(sessions)} sessions...")
    print(f"Output directory: {output_dir}")
    if existing_hashes:
        print(f"Resume mode: {len(existing_hashes)} previously processed")
    print()

    for i, session in enumerate(sessions, 1):
        session_id = session.get("session_id", "unknown")
        messages = session.get("messages", [])
        tool_summaries = session.get("tool_summaries", [])
        content_hash = compute_content_hash(messages)

        if content_hash in existing_hashes:
            if verbose:
                print(f"[{i}/{len(sessions)}] Skipped (cached): {session_id[:20]}")
            stats["skipped"] += 1
            continue

        first_user = next(
            (m["content"][:40] for m in messages if m["role"] == "user"),
            "unknown",
        ).replace("\n", " ")

        print(f"[{i}/{len(sessions)}] Processing: {first_user}...")

        if dry_run:
            print("  [DRY RUN] Would generate template")
            stats["processed"] += 1
            continue

        start_time = time.time()
        if use_azure:
            template = extract_template_azure(
                messages, tool_summaries=tool_summaries, deployment=deployment, verbose=verbose
            )
        else:
            print("Only Azure is supported for template extraction")
            template = None

        elapsed = time.time() - start_time

        if not template:
            print(f"  Failed to extract template ({elapsed:.1f}s)")
            stats["failed"] += 1
            continue

        if "No Template Extracted" in template or "no reusable pattern" in template.lower():
            if verbose:
                print(f"  Exploratory conversation ({elapsed:.1f}s)")
            stats["exploratory"] += 1
            existing_hashes.add(content_hash)
            continue

        topic = extract_topic_from_template(template)
        filename = generate_filename(topic, session_id)
        output_path = output_dir / filename

        counter = 1
        while output_path.exists():
            base = filename.rsplit("-prompt.md", 1)[0]
            output_path = output_dir / f"{base}-{counter}-prompt.md"
            counter += 1

        template_with_meta = (
            f"<!-- source_type: claude_code -->\n"
            f"<!-- source_session: {session_id} -->\n"
            f"<!-- content_hash: {content_hash} -->\n"
            f"<!-- source_path: {session.get('file_path', '')} -->\n"
            f"<!-- model: {session.get('model', 'unknown')} -->\n\n"
            f"{template}"
        )

        output_path.write_text(template_with_meta, encoding="utf-8")
        existing_hashes.add(content_hash)
        stats["processed"] += 1

        print(f"  Created: {output_path.name} ({elapsed:.1f}s)")

    if not dry_run:
        save_manifest(output_dir, existing_hashes, stats)

    return stats


def print_summary(stats: Dict[str, int]) -> None:
    """Print processing summary."""
    print("\n" + "=" * 60)
    print("Processing Complete")
    print("=" * 60)
    print(f"Total sessions:     {stats['total']}")
    print(f"Templates created:  {stats['processed']}")
    print(f"Skipped (cached):   {stats['skipped']}")
    print(f"Exploratory:        {stats['exploratory']}")
    print(f"Failed:             {stats['failed']}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch convert Claude Code sessions to prompt templates"
    )
    parser.add_argument(
        "--path",
        "-p",
        default=DEFAULT_CLAUDE_PATH,
        help="Path to Claude Code projects directory",
    )
    parser.add_argument(
        "--project",
        type=str,
        help="Filter by project path substring (e.g., 'pd-prompt-lib-mgr')",
    )
    parser.add_argument(
        "--days",
        "-d",
        type=int,
        help="Only process sessions from the last N days",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Process all sessions regardless of date",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        help="Limit to N sessions (after date filtering)",
    )
    parser.add_argument(
        "--top",
        type=int,
        help="Select top N sessions by score (overrides --limit sorting)",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        help="Only keep sessions with score >= this threshold",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for generated templates",
    )
    parser.add_argument(
        "--index-only",
        "-i",
        action="store_true",
        help="Only index and display sessions, do not generate templates",
    )
    parser.add_argument(
        "--use-index",
        action="store_true",
        help="Use sessions-index.json for faster scanning",
    )
    parser.add_argument(
        "--azure",
        action="store_true",
        help="Use Azure OpenAI (recommended)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be generated without writing files",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--deployment",
        type=str,
        help=f"Azure deployment name (default: {AZURE_OPENAI_DEPLOYMENT})",
    )
    parser.add_argument(
        "--keep-bootstrap",
        action="store_true",
        help="Include Claude Code bootstrap messages (system reminders, IDE context)",
    )

    args = parser.parse_args()

    days = None if args.all else (args.days or 30)

    sessions = index_sessions(
        args.path,
        days=days,
        limit=args.limit,
        skip_bootstrap=not args.keep_bootstrap,
        top_n=args.top,
        min_score=args.min_score,
        project_filter=args.project,
        use_index=args.use_index,
    )
    display_index(sessions)

    if args.index_only:
        print("\nIndex complete. Use without --index-only to generate templates.")
        return

    if not sessions:
        print("\nNo sessions to process. Exiting.")
        return

    if not args.dry_run and not args.azure:
        print("\nAzure mode required. Use --azure flag.")
        return

    output_dir = Path(args.output)
    deployment = args.deployment or AZURE_OPENAI_DEPLOYMENT
    if args.azure:
        print(f"\nUsing Azure deployment: {deployment}")
    stats = process_sessions(
        sessions,
        output_dir,
        use_azure=args.azure,
        deployment=deployment,
        verbose=args.verbose,
        dry_run=args.dry_run,
    )

    print_summary(stats)


if __name__ == "__main__":
    main()
