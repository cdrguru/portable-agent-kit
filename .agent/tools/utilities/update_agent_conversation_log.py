#!/usr/bin/env python3
"""Append agent handoff notes to an append-only conversation log.

This script is intentionally portable and uses only the Python standard library.
It can be copied into any repository to enable agent handoff logging.

Default log path:
  .agent/docs/agent_handoffs/agent_conversation_log.md

Default boundary:
  === MESSAGE BOUNDARY ===

Environment variables:
  AGENT_CONVERSATION_LOG  - Override default log path
  AGENT_CONVERSATION_BOUNDARY - Override boundary marker
  PROJECT_NAME - Project identifier in log entries

Usage:
  python3 update_agent_conversation_log.py \
    --agent builder \
    --summary "Implemented login feature" \
    --handoff reviewer \
    --task "Review auth flow" \
    --reference "src/auth.py"
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


# Configuration defaults (can be overridden via environment or CLI)
DEFAULT_LOG_PATH = Path(
    os.getenv("AGENT_CONVERSATION_LOG", ".agent/docs/agent_handoffs/agent_conversation_log.md")
)
DEFAULT_BOUNDARY = os.getenv("AGENT_CONVERSATION_BOUNDARY", "=== MESSAGE BOUNDARY ===")
DEFAULT_PROJECT = os.getenv("PROJECT_NAME", "[PROJECT_NAME]")


def _clean_items(items: List[str]) -> List[str]:
    """Remove duplicates and empty items, preserving order."""
    seen = set()
    cleaned: List[str] = []
    for item in items:
        text = item.strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
    return cleaned


def _collect_details(args: argparse.Namespace) -> str:
    """Collect details from multiple sources (inline, file, stdin)."""
    chunks: List[str] = []
    if args.details:
        chunks.append(args.details)
    if args.details_file:
        try:
            chunks.append(Path(args.details_file).read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise SystemExit(f"Details file not found: {exc.filename}") from exc
    if args.stdin:
        stdin_payload = sys.stdin.read()
        if stdin_payload.strip():
            chunks.append(stdin_payload)
    if not chunks:
        return ""
    joined = "\n\n".join(textwrap.dedent(chunk).strip() for chunk in chunks if chunk)
    return joined.strip()


def _parse_timestamp(raw: Optional[str]) -> datetime:
    """Parse timestamp string or return current UTC time."""
    if not raw or not raw.strip() or raw.strip().upper() == "NOW":
        return datetime.now(timezone.utc)
    candidate = raw.strip()
    try:
        if candidate.endswith("Z"):
            candidate = candidate[:-1]
            dt = datetime.fromisoformat(candidate)
            return dt.replace(tzinfo=timezone.utc)
        dt = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise SystemExit(f"Invalid timestamp format: {raw}") from exc
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _normalize_entry(text: str) -> str:
    """Normalize entry text for comparison."""
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def _extract_last_entry(raw: str, boundary: str) -> Optional[str]:
    """Extract the last entry from the log for duplicate detection."""
    if not raw.strip():
        return None
    parts = re.split(rf"^{re.escape(boundary)}\s*$", raw, flags=re.MULTILINE)
    for part in reversed(parts):
        stripped = part.strip()
        if stripped:
            return stripped
    return None


@dataclass
class ConversationEntry:
    """Represents a single handoff entry in the conversation log."""
    
    summary: str
    agent: str
    role: str
    details: str = ""
    tasks: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    handoff: Optional[str] = None
    context: Optional[str] = None
    status: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def render(self, project: str) -> str:
        """Render the entry as markdown text."""
        lines: List[str] = []
        lines.append(f"TimestampUTC: {self.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        lines.append(f"Project: {project}")
        lines.append(f"Agent: {self.agent}")
        lines.append(f"Role: {self.role}")
        if self.status:
            lines.append(f"Status: {self.status}")
        if self.context:
            lines.append(f"Context: {self.context}")
        if self.handoff:
            lines.append(f"HandoffTo: {self.handoff}")
        if self.tags:
            lines.append(f"Tags: {', '.join(self.tags)}")
        if self.references:
            lines.append("References:")
            lines.extend(f"- {ref}" for ref in self.references)
        lines.append("")
        lines.append(f"Summary: {self.summary}")
        if self.tasks:
            lines.append("")
            lines.append("Tasks:")
            lines.extend(f"- {item}" for item in self.tasks)
        if self.details:
            lines.append("")
            lines.append("Details:")
            lines.append(textwrap.indent(self.details.strip(), "  "))
        if self.notes:
            lines.append("")
            lines.append("Notes:")
            lines.extend(f"- {note}" for note in self.notes)
        return "\n".join(lines).strip() + "\n"


def append_entry(args: argparse.Namespace) -> None:
    """Append a new entry to the conversation log."""
    log_path: Path = args.logfile
    boundary: str = args.boundary
    project: str = args.project

    entry = ConversationEntry(
        summary=args.summary.strip(),
        agent=args.agent.strip(),
        role=args.role.strip(),
        details=_collect_details(args),
        tasks=_clean_items(args.task or []),
        tags=_clean_items(args.tag or []),
        references=_clean_items(args.reference or []),
        handoff=args.handoff.strip() if args.handoff else None,
        context=args.context.strip() if args.context else None,
        status=args.status.strip() if args.status else None,
        notes=_clean_items(args.note or []),
        timestamp=_parse_timestamp(args.timestamp),
    )

    entry_text = entry.render(project)
    normalized_new = _normalize_entry(entry_text)

    # Read existing log for duplicate detection
    raw_text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    last_entry = _extract_last_entry(raw_text, boundary)
    
    if last_entry and not args.force:
        if _normalize_entry(last_entry) == normalized_new:
            if not args.quiet:
                print("Skipped: entry matches the previous handoff message.")
            return

    # Ensure directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Append the entry
    with log_path.open("a", encoding="utf-8") as handle:
        if raw_text and not raw_text.endswith("\n"):
            handle.write("\n")
        if raw_text.strip():
            handle.write("\n")
        handle.write(f"{boundary}\n")
        handle.write(entry_text.rstrip() + "\n\n")

    if not args.quiet:
        print(f"Appended handoff entry: {entry.agent} -> {entry.handoff or 'unspecified'}")
        print(f"Log: {log_path}")


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Record an agent handoff in the conversation log. "
            "Use this when finishing work so the next agent has context."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          # Basic handoff
          python3 update_agent_conversation_log.py \\
            --agent builder --summary "Added login" --handoff reviewer

          # With tasks and references
          python3 update_agent_conversation_log.py \\
            --agent builder \\
            --summary "Implemented auth flow" \\
            --handoff reviewer \\
            --task "Review security" \\
            --task "Check edge cases" \\
            --reference "src/auth.py" \\
            --reference "tests/test_auth.py"

          # With context and tags
          python3 update_agent_conversation_log.py \\
            --agent docs \\
            --summary "Updated API docs" \\
            --context documentation \\
            --tag api --tag docs \\
            --handoff human
        """),
    )
    
    # Required arguments
    parser.add_argument(
        "--agent", required=True,
        help="Name of the agent emitting this handoff."
    )
    parser.add_argument(
        "--summary", required=True,
        help="Short headline summarizing what was done."
    )
    
    # Optional arguments
    parser.add_argument(
        "--role", default="assistant",
        help="Role hint: assistant, reviewer, planner, director (default: assistant)."
    )
    parser.add_argument(
        "--handoff",
        help="Who should pick up next (agent name or 'human')."
    )
    parser.add_argument(
        "--status", default="ready",
        help="Status indicator: ready, blocked, wip (default: ready)."
    )
    parser.add_argument(
        "--context",
        help="Short context label: setup, refactor, bugfix, feature."
    )
    
    # Repeatable arguments
    parser.add_argument(
        "--task", action="append",
        help="Follow-up task for the next agent (repeatable)."
    )
    parser.add_argument(
        "--reference", action="append",
        help="File path or URL reference (repeatable)."
    )
    parser.add_argument(
        "--tag", action="append",
        help="Tag to categorize this entry (repeatable)."
    )
    parser.add_argument(
        "--note", action="append",
        help="Additional note for context (repeatable)."
    )
    
    # Details (multiple sources)
    parser.add_argument(
        "--details",
        help="Inline details for the next agent."
    )
    parser.add_argument(
        "--details-file",
        help="Read additional details from a file (UTF-8)."
    )
    parser.add_argument(
        "--stdin", action="store_true",
        help="Read additional details from STDIN."
    )
    
    # Timestamp
    parser.add_argument(
        "--timestamp",
        help="Override timestamp (ISO8601). Defaults to current UTC."
    )
    
    # Configuration
    parser.add_argument(
        "--logfile", type=Path, default=DEFAULT_LOG_PATH,
        help=f"Log file path (default: {DEFAULT_LOG_PATH})."
    )
    parser.add_argument(
        "--boundary", default=DEFAULT_BOUNDARY,
        help="Boundary marker between entries."
    )
    parser.add_argument(
        "--project", default=DEFAULT_PROJECT,
        help="Project identifier for log entries."
    )
    
    # Flags
    parser.add_argument(
        "--force", action="store_true",
        help="Write even if the previous entry is identical."
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress console output."
    )
    
    return parser


def main() -> None:
    """Main entry point."""
    args = build_parser().parse_args()
    append_entry(args)


if __name__ == "__main__":
    main()
