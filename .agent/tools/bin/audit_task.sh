#!/bin/bash
# PACK Auditor - Quick audit wrapper for Gemini CLI
#
# Usage:
#   ./audit_task.sh                    # Use defaults
#   ./audit_task.sh gemini-2.5-flash   # Specify model
#
# Prerequisites:
#   - Gemini CLI installed: npm install -g @google/gemini-cli
#   - Gemini CLI initialized: run gemini-cli-init skill

set -e

MODEL="${1:-gemini-2.5-pro}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_SCRIPT="$SCRIPT_DIR/../utilities/gemini_audit.py"

if [[ ! -f "$AUDIT_SCRIPT" ]]; then
    echo "ERROR: Could not find gemini_audit.py at $AUDIT_SCRIPT" >&2
    exit 1
fi

python3 "$AUDIT_SCRIPT" --model "$MODEL" --auto
