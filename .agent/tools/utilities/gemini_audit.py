#!/usr/bin/env python3
"""Invoke Gemini CLI as PACK Auditor to validate task and plan alignment.

This script is intentionally portable and uses only the Python standard library.
It can be copied into any repository to enable Gemini-based auditing.

Default paths:
  Task:     .agent/task.md
  Plan:     .agent/implementation_plan.md
  Persona:  .gemini/personas/auditor.md

Usage:
  python3 gemini_audit.py --auto
  python3 gemini_audit.py --task .agent/task.md --plan .agent/implementation_plan.md
  python3 gemini_audit.py --model gemini-2.5-flash --auto
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Default paths
DEFAULT_TASK = Path(".agent/task.md")
DEFAULT_PLAN = Path(".agent/implementation_plan.md")
DEFAULT_PERSONA = Path(".gemini/personas/auditor.md")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")


def get_node_version() -> Optional[str]:
    """Get the current Node.js version string."""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip().lstrip("v")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def check_gemini_installed() -> bool:
    """Check if Gemini CLI is available and meets requirements."""
    # Check Node.js version (v20+ required for Gemini CLI)
    node_ver = get_node_version()
    if node_ver:
        major = int(node_ver.split(".")[0])
        if major < 20:
            print(f"ERROR: Node.js {node_ver} detected. v20.0.0 or higher is required.", file=sys.stderr)
            print("Use 'nvm install 22 && nvm use 22' to update your environment.", file=sys.stderr)
            sys.exit(1)

    try:
        result = subprocess.run(
            ["gemini", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def read_file_safe(path: Path) -> str:
    """Read file contents or return placeholder if missing."""
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return f"[File not found: {path}]"


def build_audit_prompt(task_content: str, plan_content: str) -> str:
    """Build the PACK handoff audit prompt."""
    return f"""# PACK HANDOFF: AUDIT REQUEST

## 1. TASK
{task_content}

## 2. IMPLEMENTATION PLAN
{plan_content}

## 3. INSTRUCTIONS
Analyze the plan against the task requirements.

Check for:
- Alignment between stated objectives and proposed implementation
- Missing acceptance criteria or edge cases
- Security concerns or architectural anti-patterns
- Unclear or ambiguous requirements

Output your decision in this format:
```
Decision: {{APPROVE | REJECT | NEEDS_INFO}}
Rationale: <one sentence>
Next action: <what should happen next>
```
"""


def extract_decision(output: str) -> Optional[str]:
    """Extract the decision from Gemini output."""
    patterns = [
        r"Decision:\s*(APPROVE|REJECT|NEEDS_INFO)",
        r"\*\*Decision\*\*:\s*(APPROVE|REJECT|NEEDS_INFO)",
        r"Decision:\s*\*\*(APPROVE|REJECT|NEEDS_INFO)\*\*",
    ]
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None


def run_gemini_audit(
    prompt: str,
    persona_path: Path,
    model: str,
    yolo: bool = True,
) -> tuple[str, int]:
    """Run Gemini CLI with the audit prompt."""
    env = os.environ.copy()
    env["GEMINI_SYSTEM_MD"] = str(persona_path)

    cmd = ["gemini", "--model", model]
    if yolo:
        cmd.append("--yolo")

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "ERROR: Gemini CLI timed out after 120 seconds", 1
    except FileNotFoundError:
        return "ERROR: Gemini CLI not found. Install with: npm install -g @google/gemini-cli", 1


def log_audit_result(
    decision: Optional[str],
    output: str,
    task_path: Path,
    plan_path: Path,
) -> None:
    """Log the audit result using the existing handoff logging tool."""
    script_dir = Path(__file__).resolve().parent
    log_script = script_dir / "update_agent_conversation_log.py"

    if not log_script.exists():
        print(f"Warning: Could not find {log_script} for logging")
        return

    summary = f"Audit decision: {decision or 'UNKNOWN'}"

    cmd = [
        sys.executable,
        str(log_script),
        "--agent", "gemini_auditor",
        "--role", "reviewer",
        "--summary", summary,
        "--handoff", "human",
        "--context", "audit",
        "--reference", str(task_path),
        "--reference", str(plan_path),
        "--quiet",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to log audit result: {e}")


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Run Gemini CLI as PACK Auditor to validate task and plan alignment.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default paths
  python3 gemini_audit.py --auto

  # Specify files explicitly
  python3 gemini_audit.py --task .agent/task.md --plan .agent/implementation_plan.md

  # Use a different model
  python3 gemini_audit.py --model gemini-2.5-flash --auto

  # Skip logging
  python3 gemini_audit.py --auto --no-log
        """,
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="Use default paths for task, plan, and persona files.",
    )
    parser.add_argument(
        "--task",
        type=Path,
        default=DEFAULT_TASK,
        help=f"Path to task definition file (default: {DEFAULT_TASK}).",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN,
        help=f"Path to implementation plan file (default: {DEFAULT_PLAN}).",
    )
    parser.add_argument(
        "--persona",
        type=Path,
        default=DEFAULT_PERSONA,
        help=f"Path to auditor persona file (default: {DEFAULT_PERSONA}).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini model to use (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--no-yolo",
        action="store_true",
        help="Disable YOLO mode (require approval for each action).",
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Skip logging the audit result to agent_conversation_log.md.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress status messages (still outputs Gemini response).",
    )

    return parser


def main() -> None:
    """Main entry point."""
    args = build_parser().parse_args()

    # Check Gemini CLI is installed
    if not check_gemini_installed():
        print("ERROR: Gemini CLI not found.", file=sys.stderr)
        print("Install with: npm install -g @google/gemini-cli", file=sys.stderr)
        sys.exit(1)

    # Check persona file exists
    if not args.persona.exists():
        print(f"ERROR: Persona file not found: {args.persona}", file=sys.stderr)
        print("Run the gemini-cli-init skill to set up Gemini integration.", file=sys.stderr)
        sys.exit(1)

    # Read task and plan
    task_content = read_file_safe(args.task)
    plan_content = read_file_safe(args.plan)

    if not args.quiet:
        print(f"Task: {args.task}")
        print(f"Plan: {args.plan}")
        print(f"Model: {args.model}")
        print("-" * 40)

    # Build and run audit
    prompt = build_audit_prompt(task_content, plan_content)
    output, returncode = run_gemini_audit(
        prompt,
        args.persona,
        args.model,
        yolo=not args.no_yolo,
    )

    # Print output
    print(output)

    # Extract and log decision
    decision = extract_decision(output)

    if not args.no_log:
        log_audit_result(decision, output, args.task, args.plan)
        if not args.quiet:
            print("-" * 40)
            print(f"Decision: {decision or 'UNKNOWN'}")
            print("Result logged to agent_conversation_log.md")

    # Exit with appropriate code
    if decision == "APPROVE":
        sys.exit(0)
    elif decision == "REJECT":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
