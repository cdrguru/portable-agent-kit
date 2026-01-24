#!/usr/bin/env python3
"""Print a combined session-init prompt for a given agent profile.

Stdlib-only. Designed for stable, paste-friendly output.

Usage:
  python3 .agent/tools/utilities/print_agent_init.py --agent ag
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


_SECTION_DELIM = "=" * 78


def _repo_root_from_this_file() -> Path:
    # This file lives at: <repo>/.agent/tools/utilities/print_agent_init.py
    # parents[0]=utilities, [1]=tools, [2]=.agent, [3]=<repo>
    return Path(__file__).resolve().parents[3]


def _read_text_if_exists(path: Path) -> Optional[str]:
    try:
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _iter_sections(repo_root: Path, agent: str) -> Iterable[Tuple[str, str]]:
    rel_paths: List[str] = [
        ".agent/ai/prompts/multi_agent_orchestration_system.md",
        ".agent/ai/rules/agent_handshake.md",
        ".agent/context/agent_environment.md",
        f".agent/ai/prompts/agent_profiles/{agent}.md",
    ]

    for rel in rel_paths:
        abs_path = repo_root / rel
        content = _read_text_if_exists(abs_path)
        if content is None:
            continue
        yield rel, content


def _print_sections(sections: Iterable[Tuple[str, str]]) -> int:
    any_found = False
    first = True

    for rel, content in sections:
        any_found = True
        if not first:
            sys.stdout.write("\n")
        first = False

        sys.stdout.write(_SECTION_DELIM + "\n")
        sys.stdout.write(f"Source: {rel}\n")
        sys.stdout.write(_SECTION_DELIM + "\n")

        # Preserve file content with minimal normalization.
        if content and not content.endswith("\n"):
            content += "\n"
        sys.stdout.write(content)

    if not any_found:
        sys.stderr.write(
            "ERROR: no init prompt sections found. "
            "Expected one or more of the standard .agent prompt files to exist.\n"
        )
        return 2

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print the combined session-init prompt for an agent profile."
    )
    parser.add_argument(
        "--agent",
        required=True,
        choices=("ag", "hp", "codex"),
        help="Which agent profile to print (ag, hp, codex).",
    )

    args = parser.parse_args(argv)

    repo_root = _repo_root_from_this_file()
    return _print_sections(_iter_sections(repo_root, args.agent))


if __name__ == "__main__":
    raise SystemExit(main())
