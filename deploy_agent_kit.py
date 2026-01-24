#!/usr/bin/env python3
"""Deploy the Portable Agent Collaboration Kit to a target repository.

This script copies the .agent/ folder from the kit template to a destination
repository, optionally updating .gitignore to ignore local-only files.

Uses only Python standard library for maximum portability.

Usage:
    python3 deploy_agent_kit.py --dest /path/to/repo
    python3 deploy_agent_kit.py --dest /path/to/repo --force
    python3 deploy_agent_kit.py --dest /path/to/repo --dry-run

Flags:
    --dest      Target repository path (required)
    --force     Overwrite existing files
    --dry-run   Preview changes without writing
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


# Files/patterns to add to .gitignore
GITIGNORE_ENTRIES = [
    "# Agent Collaboration Kit (local-only)",
    "conversation.compact.md",
    ".reports/",
]


@dataclass
class DeployResult:
    """Result of a deployment operation."""
    copied: List[Path] = field(default_factory=list)
    skipped: List[Path] = field(default_factory=list)
    overwritten: List[Path] = field(default_factory=list)
    gitignore_updated: bool = False
    errors: List[str] = field(default_factory=list)


def find_kit_source() -> Path:
    """Find the .agent source directory relative to this script."""
    script_dir = Path(__file__).resolve().parent
    
    # Check common locations
    candidates = [
        script_dir / ".agent",
        script_dir.parent / ".agent",
        script_dir.parent.parent / ".agent",
        script_dir.parent.parent / "templates" / "portable-agent-kit" / ".agent",
    ]
    
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    
    # If running from the kit folder itself
    if (script_dir.parent / "AGENTS.md").exists():
        return script_dir.parent
    
    raise SystemExit(
        "Could not find .agent source directory. "
        "Run this script from the kit folder or specify the source path."
    )


def iter_source_files(source_dir: Path) -> List[Path]:
    """Iterate over all files in the source directory."""
    files = []
    for path in source_dir.rglob("*"):
        if path.is_file():
            # Skip __pycache__ and .pyc files
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            files.append(path)
    return sorted(files)


def copy_file(src: Path, dest: Path, *, force: bool, dry_run: bool) -> str:
    """Copy a single file, returning the outcome."""
    if dest.exists():
        if not force:
            return "skipped"
        if dry_run:
            return "would_overwrite"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return "overwritten"
    
    if dry_run:
        return "would_copy"
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return "copied"


def update_gitignore(dest_repo: Path, *, dry_run: bool) -> bool:
    """Ensure .gitignore contains required entries."""
    gitignore_path = dest_repo / ".gitignore"
    
    if gitignore_path.exists():
        existing = gitignore_path.read_text(encoding="utf-8")
    else:
        existing = ""
    
    lines = [line.rstrip() for line in existing.splitlines()]
    
    # Check which entries are missing
    missing = []
    for entry in GITIGNORE_ENTRIES:
        # Skip comment lines when checking (they're just for context)
        if entry.startswith("#"):
            continue
        if entry not in lines:
            missing.append(entry)
    
    if not missing:
        return False
    
    if dry_run:
        return True
    
    # Append missing entries
    with gitignore_path.open("a", encoding="utf-8") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write("\n")
        for entry in GITIGNORE_ENTRIES:
            if entry.startswith("#") or entry in missing:
                f.write(f"{entry}\n")
    
    return True


def deploy(
    source_dir: Path,
    dest_repo: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> DeployResult:
    """Deploy the kit to the destination repository."""
    result = DeployResult()
    
    # Determine destination .agent folder
    dest_agent_dir = dest_repo / ".agent"
    
    # Copy all files
    for src_file in iter_source_files(source_dir):
        rel_path = src_file.relative_to(source_dir)
        dest_file = dest_agent_dir / rel_path
        
        try:
            outcome = copy_file(src_file, dest_file, force=force, dry_run=dry_run)
            
            if outcome in ("copied", "would_copy"):
                result.copied.append(rel_path)
            elif outcome in ("overwritten", "would_overwrite"):
                result.overwritten.append(rel_path)
            else:
                result.skipped.append(rel_path)
                
        except OSError as e:
            result.errors.append(f"Error copying {rel_path}: {e}")
    
    # Update .gitignore
    try:
        result.gitignore_updated = update_gitignore(dest_repo, dry_run=dry_run)
    except OSError as e:
        result.errors.append(f"Error updating .gitignore: {e}")
    
    return result


def print_result(result: DeployResult, dest: Path, dry_run: bool) -> None:
    """Print deployment results."""
    prefix = "[DRY RUN] " if dry_run else ""
    action_word = "Would copy" if dry_run else "Copied"
    overwrite_word = "Would overwrite" if dry_run else "Overwritten"
    
    print(f"\n{prefix}Agent Collaboration Kit Deployment")
    print(f"{'=' * 40}")
    print(f"Destination: {dest}")
    
    if result.copied:
        print(f"\n{action_word}: {len(result.copied)} file(s)")
        for f in result.copied[:5]:
            print(f"  + {f}")
        if len(result.copied) > 5:
            print(f"  ... and {len(result.copied) - 5} more")
    
    if result.overwritten:
        print(f"\n{overwrite_word}: {len(result.overwritten)} file(s)")
        for f in result.overwritten[:5]:
            print(f"  ~ {f}")
        if len(result.overwritten) > 5:
            print(f"  ... and {len(result.overwritten) - 5} more")
    
    if result.skipped:
        print(f"\nSkipped (already exists): {len(result.skipped)} file(s)")
        for f in result.skipped[:3]:
            print(f"  - {f}")
        if len(result.skipped) > 3:
            print(f"  ... and {len(result.skipped) - 3} more")
    
    if result.gitignore_updated:
        action = "Would update" if dry_run else "Updated"
        print(f"\n{action} .gitignore with local-only entries")
    
    if result.errors:
        print(f"\nErrors: {len(result.errors)}")
        for err in result.errors:
            print(f"  ! {err}")
    
    if not dry_run and (result.copied or result.overwritten):
        print("\n[OK] Deployment complete!")
        print("\nNext steps:")
        print("  1. Review and customize .agent/AGENTS.md")
        print("  2. Initialize Gemini Auditor: python3 .agent/tools/utilities/skills.py show gemini-cli-init")
        print("  3. Bootstrap a session: python3 .agent/tools/utilities/skills.py show session-bootstrap")
        print("  4. Set PROJECT_NAME environment variable (optional)")


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Deploy the Portable Agent Collaboration Kit to a repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic deployment
  python3 deploy_agent_kit.py --dest /path/to/my-project

  # Force overwrite existing files
  python3 deploy_agent_kit.py --dest /path/to/my-project --force

  # Preview what would be copied
  python3 deploy_agent_kit.py --dest /path/to/my-project --dry-run
        """,
    )
    
    parser.add_argument(
        "--dest",
        type=Path,
        required=True,
        help="Destination repository path.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Source .agent directory (auto-detected if not specified).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files in the destination.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be copied without making changes.",
    )
    
    return parser


def main() -> None:
    """Main entry point."""
    args = build_parser().parse_args()
    
    dest: Path = args.dest.resolve()
    
    # Validate destination
    if not dest.exists():
        print(f"Error: Destination does not exist: {dest}", file=sys.stderr)
        sys.exit(1)
    if not dest.is_dir():
        print(f"Error: Destination is not a directory: {dest}", file=sys.stderr)
        sys.exit(1)
    
    # Find or use specified source
    if args.source:
        source = args.source.resolve()
        if not source.is_dir():
            print(f"Error: Source is not a directory: {source}", file=sys.stderr)
            sys.exit(1)
    else:
        source = find_kit_source()
    
    # Deploy
    result = deploy(
        source_dir=source,
        dest_repo=dest,
        force=args.force,
        dry_run=args.dry_run,
    )
    
    # Print results
    print_result(result, dest, args.dry_run)
    
    # Exit with error if there were problems
    if result.errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
