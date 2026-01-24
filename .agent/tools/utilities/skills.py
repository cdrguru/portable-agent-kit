#!/usr/bin/env python3
"""List, show, and search optional .agent skills.

Usage:
  python3 .agent/tools/utilities/skills.py list
  python3 .agent/tools/utilities/skills.py show <skill-name>
  python3 .agent/tools/utilities/skills.py search <keyword>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


def _repo_root_from_this_file() -> Path:
    # This file lives at: <repo>/.agent/tools/utilities/skills.py
    # parents[0]=utilities, [1]=tools, [2]=.agent, [3]=<repo>
    return Path(__file__).resolve().parents[3]


def _skills_root(repo_root: Path) -> Path:
    return repo_root / ".agent" / "skills"


def _read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _iter_skill_dirs(skills_root: Path) -> List[Path]:
    if not skills_root.is_dir():
        return []
    skills: List[Path] = []
    for item in skills_root.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith("."):
            continue
        if (item / "SKILL.md").is_file():
            skills.append(item)
    return sorted(skills, key=lambda p: p.name)


def _parse_frontmatter(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None, None

    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break
    if end_index is None:
        return None, None, None

    name = None
    description = None
    short_desc = None
    in_metadata = False
    metadata_indent = 0

    for raw in lines[1:end_index]:
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()

        if in_metadata and indent <= metadata_indent:
            in_metadata = False

        if not in_metadata and indent == 0:
            if stripped.startswith("name:"):
                name = stripped.split(":", 1)[1].strip()
                continue
            if stripped.startswith("description:"):
                description = stripped.split(":", 1)[1].strip()
                continue
            if stripped.startswith("metadata:"):
                in_metadata = True
                metadata_indent = indent
                continue

        if in_metadata and indent > metadata_indent:
            if stripped.startswith("short-description:"):
                short_desc = stripped.split(":", 1)[1].strip()
                continue

    return name, description, short_desc


def _strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1 :])
    return text


def _first_nonempty_body_line(text: str) -> Optional[str]:
    body = _strip_frontmatter(text)
    for raw in body.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        return stripped
    return None


def _skill_metadata(skill_dir: Path) -> Tuple[str, str, str]:
    text = _read_text(skill_dir / "SKILL.md")
    if text is None:
        name = skill_dir.name
        return name, "", f"${name}"

    name, description, short_desc = _parse_frontmatter(text)
    if not name:
        name = skill_dir.name

    if not short_desc:
        if description:
            short_desc = description
        else:
            short_desc = _first_nonempty_body_line(text) or ""

    return name, short_desc, f"${name}"


def _find_skill_dir(skills_root: Path, skill_name: str) -> Optional[Path]:
    direct = skills_root / skill_name
    if direct.is_dir() and (direct / "SKILL.md").is_file():
        return direct

    for skill_dir in _iter_skill_dirs(skills_root):
        text = _read_text(skill_dir / "SKILL.md")
        if not text:
            continue
        name, _, _ = _parse_frontmatter(text)
        if name == skill_name:
            return skill_dir
    return None


def _print_table(rows: List[Tuple[str, str, str]]) -> None:
    widths = [max(len(row[i]) for row in rows) for i in range(3)]
    for row in rows:
        sys.stdout.write(
            f"{row[0]:<{widths[0]}} | {row[1]:<{widths[1]}} | {row[2]:<{widths[2]}}\n"
        )


def _cmd_list(skills_root: Path) -> int:
    skill_dirs = _iter_skill_dirs(skills_root)
    rows: List[Tuple[str, str, str]] = [("name", "short-description", "invocation")]
    for skill_dir in skill_dirs:
        rows.append(_skill_metadata(skill_dir))
    _print_table(rows)
    return 0


def _cmd_show(skills_root: Path, skill_name: str) -> int:
    skill_dir = _find_skill_dir(skills_root, skill_name)
    if not skill_dir:
        sys.stderr.write(f"ERROR: skill not found: {skill_name}\n")
        return 2

    text = _read_text(skill_dir / "SKILL.md")
    if text is None:
        sys.stderr.write(f"ERROR: unable to read SKILL.md for {skill_name}\n")
        return 2

    if not text.endswith("\n"):
        text += "\n"
    sys.stdout.write(text)
    return 0


def _cmd_search(skills_root: Path, keyword: str) -> int:
    keyword_lower = keyword.lower()
    matches: List[str] = []
    for skill_dir in _iter_skill_dirs(skills_root):
        text = _read_text(skill_dir / "SKILL.md")
        if not text:
            continue
        if keyword_lower in text.lower():
            name, _, _ = _parse_frontmatter(text)
            matches.append(name or skill_dir.name)

    for name in matches:
        sys.stdout.write(name + "\n")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="List, show, and search optional .agent skills."
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    subparsers.add_parser("list", help="List available skills")

    show_parser = subparsers.add_parser("show", help="Print a skill's SKILL.md")
    show_parser.add_argument("skill_name", help="Skill directory name")

    search_parser = subparsers.add_parser("search", help="Search SKILL.md content")
    search_parser.add_argument("keyword", help="Keyword to search for")

    args = parser.parse_args(argv)

    repo_root = _repo_root_from_this_file()
    skills_root = _skills_root(repo_root)
    if not skills_root.is_dir():
        sys.stderr.write(f"ERROR: skills directory not found: {skills_root}\n")
        return 2

    if args.command == "list":
        return _cmd_list(skills_root)
    if args.command == "show":
        return _cmd_show(skills_root, args.skill_name)
    if args.command == "search":
        return _cmd_search(skills_root, args.keyword)

    sys.stderr.write("ERROR: invalid command\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
