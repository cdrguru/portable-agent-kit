---
name: redact-pii
description: "Scan one or more files (markdown, text, JSON, CSV) for SSNs, EINs, TINs, account numbers, and other highly sensitive identifiers, then redact them in-place with masked placeholders. Confirms each redaction with the user before writing."
allowed-tools: Read, Grep, Edit, Glob, Bash(ls:*)
---

# PII Redaction Skill

Scan target files for highly sensitive financial and personal identifiers and redact them in-place. Preserve all surrounding context — only the sensitive values are masked.

## Invocation

The user may invoke as `/redact-pii` with or without arguments:
- `/redact-pii` — redact the currently open/discussed file
- `/redact-pii path/to/file.md` — redact a specific file
- `/redact-pii path/to/dir/` — redact all `.md`, `.txt`, `.csv`, `.json` files in a directory (non-recursive unless user says "recursive")

If no target is specified, ask the user which file(s) to redact before proceeding.

---

## Phase 1: Discover Target Files

Resolve the target path(s) from the invocation argument or conversation context.

- If a single file: read it directly.
- If a directory: Glob for `*.{md,txt,csv,json}` within it.
- If no argument and context is ambiguous: ask the user.

List the files you will scan and confirm before making any edits.

---

## Phase 2: Scan for Sensitive Patterns

Read each target file and search for the following patterns. For each match, record: file path, line number, matched text, pattern category.

### Pattern Catalog

| Category | Pattern (regex) | Mask |
|----------|----------------|------|
| SSN (Social Security Number) | `\b\d{3}-\d{2}-\d{4}\b` | `XXX-XX-XXXX` |
| SSN (unformatted 9 digits) | `\b\d{9}\b` (only flag if in financial/tax context) | `XXXXXXXXX` |
| EIN (Employer Identification Number) | `\b\d{2}-\d{7}\b` | `XX-XXXXXXX` |
| ITIN (Individual Taxpayer ID) | `\b9\d{2}-\d{2}-\d{4}\b` | `XXX-XX-XXXX` |
| Account numbers (bank/brokerage) | `\b(?:acct|account|acct\.?|a/c)[:\s#]*\d{6,17}\b` (case-insensitive) | `[ACCT-REDACTED]` |
| Routing numbers | `\b(?:routing|ABA|RTN)[:\s#]*\d{9}\b` (case-insensitive) | `[ROUTING-REDACTED]` |
| Credit/debit card numbers | `\b(?:\d{4}[- ]){3}\d{4}\b` | `XXXX-XXXX-XXXX-XXXX` |
| Passport numbers (US) | `\b[A-Z]{1,2}\d{6,9}\b` (flag only if labeled "passport") | `[PASSPORT-REDACTED]` |
| Driver's license (labeled) | when preceded by "DL", "license #", "driver" within 5 tokens | `[DL-REDACTED]` |
| State tax ID | `\b(?:state tax id|state id)[:\s]*[\dA-Z-]{5,15}\b` (case-insensitive) | `[STATE-TAX-ID-REDACTED]` |
| Full DOB (Date of Birth) | `\b(?:DOB|date of birth|born)[:\s]*\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b` (case-insensitive) | `[DOB-REDACTED]` |

### Context Rules

- **EIN vs phone/zip**: A `\d{2}-\d{7}` is only flagged as EIN if it appears near keywords like `EIN`, `tax id`, `employer id`, `TIN`, `FEIN`, or is in a tax/financial document (judge from filename and surrounding text).
- **9-digit SSN**: Only flag unformatted 9-digit numbers if they appear near `SSN`, `social security`, `taxpayer`, or similar. Do not flag arbitrary 9-digit numerals.
- **Account numbers**: Flag only if preceded by a label (acct, account, a/c, etc.). Do not flag all long digit strings.
- **False positive caution**: When uncertain, flag as a candidate and ask the user whether to redact.

---

## Phase 3: Report Findings

Before making any changes, present a summary table:

```
FINDINGS — [filename]
──────────────────────────────────────────────────────────
 # | Line | Category       | Original Value      | Mask
───|──────|────────────────|─────────────────────|──────────────────────
 1 |   42 | EIN            | 12-3456789          | XX-XXXXXXX
 2 |   87 | SSN            | 123-45-6789         | XXX-XX-XXXX
 3 |  103 | Account Number | acct: 000123456789  | acct: [ACCT-REDACTED]
──────────────────────────────────────────────────────────
Total: 3 finding(s) in 1 file(s)
```

If no findings: report "No sensitive identifiers detected in [file]." and stop.

Then ask:
> "Redact all [N] findings? Reply 'yes' to proceed, 'no' to cancel, or list item numbers to redact selectively (e.g. '1,3')."

---

## Phase 4: Redact In-Place

Upon user confirmation:

- Use the **Edit** tool to perform each substitution.
- Replace only the sensitive value — preserve surrounding text, punctuation, labels, and whitespace.
- Work file by file, finding by finding.
- After all edits, re-read the file and confirm the values are gone.

Example:
- Before: `EIN: 12-3456789`
- After:  `EIN: XX-XXXXXXX`

---

## Phase 5: Summary

After all redactions:

```
REDACTION COMPLETE
──────────────────────────────────────────────────────────
Files modified : 1
Values redacted: 3
  • [filename.md] — 3 redactions (EIN ×1, SSN ×1, Account ×1)

Review the file(s) before committing. Consider running /security_audit
to confirm no other sensitive data remains.
```

---

## Safety Rules

1. **Never redact without user confirmation** — always show findings first.
2. **Never guess at partial matches** — when uncertain, ask rather than silently skip or silently redact.
3. **Preserve document structure** — only the sensitive token is replaced; surrounding text is untouched.
4. **Do not redact example/placeholder values** — skip values that are already masked (e.g. `XXX-XX-XXXX`, `[REDACTED]`, `000-00-0000`).
5. **Do not modify binary files** — `.pdf`, `.xlsx`, `.jpeg`, `.png` are out of scope; note them but skip.
