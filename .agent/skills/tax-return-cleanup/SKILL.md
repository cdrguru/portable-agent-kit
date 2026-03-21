---
name: tax-return-cleanup
description: "Clean and restructure a PDF-converted IRS Form 1065 KB file into an agent-readable markdown document. Removes IRS form noise (footer codes, tracking lines, tilde tab stops, address headings, anchor IDs), extracts Schedule K totals and partner capital accounts into summary tables, and groups content by logical section (CPA letter, Schedule K, K-1s, state returns). Writes a new _clean.md file alongside the original."
allowed-tools: Read, Glob, Bash(python3:*), Bash(ls:*), Bash(wc:*)
---

# Tax Return KB Cleanup Skill

Produce a clean, agent-readable version of a PDF-converted IRS Form 1065 KB file.

## Invocation

- `/tax-return-cleanup` — clean the currently discussed KB file
- `/tax-return-cleanup path/to/file_kb.md` — clean a specific file
- `/tax-return-cleanup path/to/dir/` — find and clean all `*_kb.md` files in a directory that look like 1065 tax returns

If no target is clear from context, ask the user which file to process.

---

## Phase 1: Locate the Cleanup Script

The cleanup script lives at:

```
.agent/scripts/tax_return_cleanup.py
```

(relative to the MacFran repo root at `/Users/pmd/Documents/mynetworkrepos/macfran/`)

Use Glob to confirm it exists:
```
.agent/scripts/tax_return_cleanup.py
```

If it does NOT exist, inform the user and stop — the script must be present.

---

## Phase 2: Identify Target File(s)

Resolve the target from the invocation argument or conversation context.

- **Single file** — use it directly.
- **Directory** — Glob for `*_kb.md` inside it, then filter to those containing `1065` or `tax_return` in the filename.
- **No argument** — use the file most recently discussed in the conversation.

Confirm the target file(s) with the user if ambiguous.

---

## Phase 3: Run the Cleanup

For each target file, run:

```bash
python3 /Users/pmd/Documents/mynetworkrepos/macfran/.agent/scripts/tax_return_cleanup.py \
    "<absolute_path_to_input_kb.md>"
```

The script writes output to `<input_stem>_clean.md` in the same directory as the input.

Capture stdout and stderr. If the script exits with a non-zero code, report the error and stop.

---

## Phase 4: Verify and Report

After the script completes:

1. Read the first 100 lines of the output `_clean.md` file to confirm it looks correct.
2. Verify the output contains:
   - A `## Schedule K — Partnership Totals` section with a data table
   - At least one `## Federal K-1s` or `## Partner Capital Accounts` section
3. Report results in this format:

```
TAX RETURN CLEANUP COMPLETE
────────────────────────────────────────────────────────
Input:   documents_tax_macfran_llc_2024_1065_tax_returns_kb.md   (496 KB)
Output:  documents_tax_macfran_llc_2024_1065_tax_returns_kb_clean.md  (210 KB)
Reduction: 58%

Sections produced:
  ✓ Schedule K — Partnership Totals
  ✓ Partner Capital Accounts
  ✓ CPA Cover Letter
  ✓ Federal K-1s — Partner Detail  (12 partners)
  ✓ Louisiana State Return
  ✓ Supporting Schedules

The cleaned file is ready for agent queries.
```

---

## What the Script Does

The Python script (`tax_return_cleanup.py`) performs these transformations:

### Noise Removed
| Pattern | Example |
|---------|---------|
| IRS footer date codes | `411811 04-01-24` |
| Internal tracking lines | `14460404 756104 08972.001 2024.03020 MACFRAN, LLC 08972.01` |
| Form banner codes | `!330626!` |
| Tilde tab stops | `~~~~~~~~~~~~~~~~~~~~~~~~~~~` |
| Anchor IDs | `{#stephen-b-davis}` |
| Curly-brace noise | `}}}}}}}}}}` |
| Adobe Acrobat print warning | `Caution: Forms printed from within...` |
| Repeated page entity headers | `Name MACFRAN, LLC  I.D. Number XX-XXXXXXX` |
| Repeated Form 1065 page banners | `Form 1065 (2024) MACFRAN, LLC XX-XXXXXXX Page 5` |
| Address-line headings | `### 207 SUMAC TRAIL` → plain text |

### Structure Added
- **Summary header table** — source file, tax year, preparer, redaction notice
- **Schedule K table** — extracted line items (ordinary income, royalties, distributions, etc.)
- **Partner Capital Accounts table** — one row per partner
- **Logical section grouping** — pages bucketed into: CPA Letter, Two-Year Comparison, Schedule B/K/L/M, K-1s, State Returns, Supporting Schedules

### What Is Preserved
- All financial figures (untouched)
- Partner names, entity names, addresses
- All IRS form labels and line descriptions
- Page markers (`### Page N`)
- The `<!-- PAGE N -->` structure (as `### Page N` headings within sections)

---

## Notes

- The script writes a **new file** (`_clean.md`) — the original KB is never modified.
- If run on a file that has already been redacted (SSNs/EINs replaced with `XXX-XX-XXXX`), it works correctly — redaction and cleanup are independent operations.
- For best results, run `/redact-pii` on the KB **before** running this skill so the clean output is also PII-free.
- The script is at `.agent/scripts/tax_return_cleanup.py` in the MacFran repo and can be updated as new return formats are encountered.
