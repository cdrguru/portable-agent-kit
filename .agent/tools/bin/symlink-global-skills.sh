#!/usr/bin/env bash
# symlink-global-skills.sh
# Replace unversioned global Claude Code skills with symlinks to PACK.
# Makes portable-agent-kit the canonical source for shared skills.
#
# Usage:  bash .agent/tools/bin/symlink-global-skills.sh [--dry-run]
# Assumes: ~/.claude/skills/ and this script's parent PACK repo exist.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACK_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PACK_SKILLS="$PACK_ROOT/.agent/skills"
GLOBAL_SKILLS="$HOME/.claude/skills"
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "[DRY RUN] No changes will be made."
  echo ""
fi

if [[ ! -d "$GLOBAL_SKILLS" ]]; then
  echo "ERROR: Global skills directory not found: $GLOBAL_SKILLS"
  exit 1
fi

if [[ ! -d "$PACK_SKILLS" ]]; then
  echo "ERROR: PACK skills directory not found: $PACK_SKILLS"
  exit 1
fi

SKILLS=(
  agent-skills-guide
  gws-calendar
  gws-calendar-agenda
  gws-calendar-insert
  gws-docs
  gws-docs-write
  gws-drive
  gws-drive-upload
  gws-gmail
  gws-gmail-forward
  gws-gmail-reply
  gws-gmail-send
  gws-gmail-triage
  gws-shared
  gws-sheets
  gws-sheets-append
  gws-sheets-read
  gws-workflow
  gws-workflow-email-to-task
  gws-workflow-meeting-prep
  gws-workflow-standup-report
  gws-workflow-weekly-digest
  persona-exec-assistant
  persona-sales-ops
  recipe-draft-email-from-doc
  recipe-find-free-time
  recipe-find-large-files
  recipe-log-deal-update
  redact-pii
  security-audit
  session-wrapup
  tax-return-cleanup
)

linked=0
skipped=0
errors=0

for skill in "${SKILLS[@]}"; do
  global_dir="$GLOBAL_SKILLS/$skill"
  pack_dir="$PACK_SKILLS/$skill"

  if [[ -L "$global_dir" ]]; then
    target="$(readlink "$global_dir")"
    echo "ALREADY_LINKED: $skill -> $target"
    skipped=$((skipped + 1))
    continue
  fi

  if [[ ! -d "$pack_dir" ]]; then
    echo "ERROR (no PACK source): $skill"
    errors=$((errors + 1))
    continue
  fi

  if [[ ! -d "$global_dir" ]]; then
    echo "SKIP (no global dir): $skill"
    skipped=$((skipped + 1))
    continue
  fi

  if $DRY_RUN; then
    echo "WOULD LINK: $skill -> $pack_dir"
  else
    rm -rf "$global_dir"
    ln -s "$pack_dir" "$global_dir"
    echo "LINKED:     $skill -> $pack_dir"
  fi
  linked=$((linked + 1))
done

echo ""
echo "Done. Linked: $linked  Skipped: $skipped  Errors: $errors  Total: ${#SKILLS[@]}"
if $DRY_RUN; then
  echo ""
  echo "Re-run without --dry-run to apply changes."
fi
