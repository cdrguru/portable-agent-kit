#!/bin/bash
# PACK Init - Unified initialization for the Portable Agent Kit
# 
# Usage: ./bin/pack-init.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SKILLS_TOOL="$ROOT_DIR/.agent/tools/utilities/skills.py"

echo "🤖 Initializing Portable Agent Kit (PACK)..."

# 1. Bootstrap the session
echo "[-] Bootstrapping local session..."
python3 "$SKILLS_TOOL" run session-bootstrap

# 2. Setup Gemini CLI (interactively if needed)
echo "[-] Setting up Gemini CLI integration..."
python3 "$SKILLS_TOOL" run gemini-cli-init

echo "✅ PACK Initialization complete. You are ready to collaborate!"
