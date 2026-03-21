---
name: security-audit
description: "Run a 3-part security & configuration audit on any repository: secret leakage scan, env var completeness check, and deployment readiness verification. Works with any language, framework, or project structure."
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(npm:*), Bash(ls:*), Bash(wc:*)
---

# Security & Configuration Audit (Universal)

Run a comprehensive 3-part audit of the current repository to detect leaked secrets, verify environment variable completeness, and assess deployment readiness. This skill adapts to any project regardless of language, framework, or structure.

## Phase 0: Project Discovery

Before scanning, identify what you're working with. Run these in parallel:

1. **Language/framework** — Glob for `package.json`, `requirements.txt`, `pyproject.toml`, `Gemfile`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `composer.json`, `*.csproj`, `mix.exs`. Read whichever exist to determine the stack.
2. **Source file types** — Based on the stack, determine the primary source extensions (e.g., `.ts,.tsx,.js` for Node, `.py` for Python, `.go` for Go, `.rb` for Ruby, etc.). Use these as `SOURCE_GLOB` for all subsequent scans.
3. **Config file types** — Glob for `**/*.{json,yaml,yml,toml,ini,cfg,conf,env,xml,properties}` at the root and one level deep to find config files.
4. **Env template** — Look for `.env.template`, `.env.example`, `.env.sample`, `.env.defaults`, or a documented env var list in README. This is the `ENV_TEMPLATE`.
5. **CI/CD and infra** — Glob for `Dockerfile*`, `docker-compose*`, `*.yaml` and `*.yml` in root and `.github/`, `.gitlab-ci*`, `Jenkinsfile`, `deploy*`, `k8s/`, `helm/`, `terraform/`, `pulumi/`, `.circleci/`, `Procfile`, `fly.toml`, `render.yaml`, `vercel.json`, `netlify.toml`.
6. **Gitignore** — Read `.gitignore` if it exists.

Summarize what you found (stack, source types, env template location, infra files) in 2-3 sentences before proceeding.

---

## Part 1: Secret Leakage Audit

### 1a. Prerequisite checks (run first)

- **`.gitignore` coverage** — Verify `.gitignore` includes: `.env`, `.env.local`, `.env.production`, `.env*.local`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `node_modules/` (if Node), `__pycache__/` (if Python), `venv/` (if Python). Flag missing entries as CRITICAL.
- **Committed secret files** — Run `git ls-files` (via Bash) and check for any tracked files matching: `.env`, `.env.local`, `.env.production`, `*.pem`, `*.key`, `*.p12`, `id_rsa`, `credentials.json`, `serviceAccountKey.json`, `*.keystore`. Any match (except `.env.template`/`.env.example`/`.env.sample`) is CRITICAL.

### 1b. Credential & secret scans (run in parallel)

Use `Grep` with `output_mode: "content"` on `SOURCE_GLOB` and config files. For each pattern, review hits in context — skip matches that are env var references, empty strings, placeholders, import paths, or comments explaining what a variable is for.

**Scan 1 — Named secrets:**
Pattern: `(client_secret|client_id|api_key|apikey|secret_key|hmac_secret|private_key|access_key|aws_secret|database_url|connection_string)\s*[:=]\s*['"\x60]`
Case-insensitive. Ignore where value is an env var reference or placeholder.

**Scan 2 — Password assignments:**
Pattern: `(password|passwd|pwd|db_pass)\s*[:=]\s*['"\x60][^'"\x60]{3,}`
Case-insensitive. Skip env var references.

**Scan 3 — Long opaque tokens (base64, API keys):**
Pattern: `['"\x60][A-Za-z0-9+/=_-]{40,}['"\x60]`
Review each hit — ignore hashes in lock files, CSS class strings, import hashes, test fixtures with fake data, and cryptographic constants from libraries.

**Scan 4 — Dangerous env var fallbacks:**
Pattern depends on language:
- Node/TS: `process\.env\.\w+\s*\|\|\s*['"][^'"]{15,}['"]`
- Python: `os\.environ\.get\(['"][^'"]+['"]\s*,\s*['"][^'"]{15,}['"]`
- Go: `os\.Getenv\(['"][^'"]+['"]\)` (then check if the result is compared/defaulted to a long string)
- Ruby: `ENV\[['"][^'"]+['"]\]\s*\|\|\s*['"][^'"]{15,}['"]`
- Generic: `getenv|GETENV|dotenv` — find the env access pattern and check fallbacks.

**Scan 5 — Private keys inline:**
Pattern (multiline): `-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----`
Any match is CRITICAL.

**Scan 6 — AWS/GCP/Azure patterns:**
Pattern: `AKIA[0-9A-Z]{16}` (AWS access key ID format)
Pattern: `"type"\s*:\s*"service_account"` (GCP service account JSON)
Pattern: `AccountKey=` (Azure storage connection string component)

### 1c. URL and infrastructure scans

- **All URLs** — Grep for `https?://[a-zA-Z0-9.-]+` across source and config files. Filter out known-safe domains: `localhost`, `127.0.0.1`, `example.com`, `schema.org`, `w3.org`, `json-schema.org`, `github.com`, `npmjs.com`, `pypi.org`, `rubygems.org`, `crates.io`, `pkg.go.dev`, `maven.org`, `nuget.org`, `jsdelivr.net`, `cdnjs.com`, `unpkg.com`, standard OAuth/API endpoints for major providers. Flag any remaining real domain that looks deployment-specific as MEDIUM.
- **Infrastructure files** — Read each infra file found in Phase 0. Check for hardcoded registry URLs with org-specific prefixes, real domain names, IP addresses, namespace references, or secret values.
- **Framework config** — If Next.js: read `next.config.*` and check `env:` / `publicRuntimeConfig` for secrets. If Django: check `settings.py` for `SECRET_KEY` with a real value. If Rails: check `config/secrets.yml` or `credentials.yml.enc`. Adapt to whatever framework was detected.

### 1d. Documentation & metadata

- **README and docs** — Read `README.md` and any files in `docs/`, `cline_docs/`, or similar. Look for real credentials, domain names, org IDs, or email addresses that were documented.
- **Package manifest** — Read the package manifest (`package.json`, `pyproject.toml`, etc.). Check `name`, `description`, `repository`, `homepage`, `author`, `bugs` for production-identifying info.
- **Public marketplace URLs** — Grep for `marketplace` URLs. Flag as LOW (public listing) but note they reveal publisher identity.

### 1e. [TOOL-GATE] Git history

Run `git rev-list --count HEAD` to get commit count.

- **< 200 commits:** Run targeted pickaxe searches:

  ```bash
  git log --all --oneline -S 'client_secret' -- ':(exclude)*.lock' ':(exclude)node_modules'
  git log --all --oneline -S 'password' -- ':(exclude)*.lock' ':(exclude)node_modules'
  git log --all --oneline -S 'BEGIN PRIVATE KEY' -- ':(exclude)*.lock'
  ```

  Flag any commits that introduced or removed real secrets.
- **>= 200 commits:** Output: "Git history contains [N] commits. Prior commits may contain original secrets. Recommend running `git filter-repo` or `BFG Repo-Cleaner` before sharing this repository."

### Part 1 output: LEAKAGE FINDINGS

| # | File | Line | Value (redacted) | Category | Severity |
|---|------|------|------------------|----------|----------|

- **CRITICAL** — Real credential, private key, tracked `.env`, missing `.gitignore` entry for secrets
- **MEDIUM** — Production URL, real email address, infrastructure detail
- **LOW** — Public marketplace URL, informational

If clean: single row "No leakage findings detected."

If any scan exceeds 50 hits, sample the first 20, report the total count, and flag the pattern for manual review.

---

## Part 2: Configuration Completeness

### Steps

1. **Collect code references** — Find all env var access patterns for the detected language:
   - Node/TS: `process\.env\.([A-Z][A-Z0-9_]+)`
   - Python: `os\.environ\[['"]([^'"]+)['"]\]`, `os\.environ\.get\(['"]([^'"]+)['"]`, `os\.getenv\(['"]([^'"]+)['"]`
   - Go: `os\.Getenv\(['"]([^'"]+)['"]`
   - Ruby: `ENV\[['"]([^'"]+)['"]\]`
   - .NET: `Configuration\[['"]([^'"]+)['"]\]`, `GetEnvironmentVariable\(['"]([^'"]+)['"]`
   - Generic: search for the framework's env access pattern.
   Extract unique variable names.

2. **Collect template variables** — Read the `ENV_TEMPLATE` found in Phase 0. Extract every variable name. If no template exists, flag this as a MEDIUM finding ("No env template file found — developers have no reference for required configuration").

3. **Client-side exposure check** — Identify the framework's client-side env prefix:
   - Next.js: `NEXT_PUBLIC_`
   - Vite: `VITE_`
   - Create React App: `REACT_APP_`
   - Nuxt: `NUXT_PUBLIC_` or in `runtimeConfig.public`
   - SvelteKit: `PUBLIC_`
   - None: skip this check.
   For every variable with the client prefix, verify it contains no secret (no PASSWORD, SECRET, KEY, TOKEN, PRIVATE in the name). Flag violations as CRITICAL.

4. **Required vs optional** — Search for the project's "required env var" pattern (e.g., `getRequiredEnvVar`, `required=True`, throwing on missing). Flag any security-sensitive variable that uses a silent fallback instead of a hard requirement.

5. **Cross-reference** — Compare code references vs template variables.

### Part 2 output: CONFIGURATION COMPLETENESS

| Variable | In Template? | Used In Code? | Required/Optional | Server/Client | Notes |
|----------|-------------|---------------|-------------------|---------------|-------|

Include a row for every unique variable found in either code or template. Flag:
- Missing from template but used in code
- In template but unused in code
- Inconsistent defaults across files
- Client-prefixed vars holding secrets
- No template file exists

---

## Part 3: Deployment Readiness

Scenario: deploying as a completely separate instance — new infrastructure, new credentials, new everything.

### Checks (adapt to the detected stack)

1. **Build success** — Would the standard build command succeed with only template values filled in? Look for compile-time constants, hardcoded imports, or missing type definitions that would break.

2. **Redirect URI / callback consistency** (if OAuth is present) — Find redirect/callback URI env vars. Verify each URI path corresponds to an actual route or endpoint in the source code.

3. **Cross-deployment isolation** — Are there hardcoded references (URLs, org IDs, database names, account IDs) that would cause a new instance to talk to the original deployment?

4. **Database/schema** — If SQL schema files exist (`schema.sql`, `migrations/`, `prisma/schema.prisma`, `alembic/`, etc.), verify they're sufficient to set up from scratch and match what the code expects.

5. **Container build** (if Dockerfile exists) — Would `docker build .` work? Any hardcoded paths, registry URLs, or assumed files?

6. **Infrastructure as code** (if K8s, Terraform, Helm, etc. exist) — Would the templates work after variable substitution? List every secret name or external reference that an operator needs to create manually, and check if they're documented.

7. **CI/CD** (if `.github/workflows/`, `.gitlab-ci.yml`, etc. exist) — Do pipelines reference hardcoded secrets, specific runners, or org-specific resources?

### Part 3 output: DEPLOYMENT READINESS

For each gap:

```text
N. [AREA] Description of gap
   File: path/to/file
   Fix: Exact change needed
```

If clean: "No deployment readiness gaps found."

---

## Part 4: Summary Verdict

**SUMMARY VERDICT** — One paragraph answering:

> Is this codebase safe to share with another developer or contribute to a public/shared repository without risk of leaking production secrets or accidentally affecting a live system?

Include: X critical findings, Y medium, Z low. Classify as:
- **SAFE** — No secrets found, good `.gitignore`, clean configuration.
- **SAFE WITH CAVEATS** — No critical leaks, but some gaps to address (list as bullets).
- **NOT SAFE** — Critical secrets found or missing safeguards. Must remediate before sharing.

---

## Execution notes

- Run Phase 0 first to adapt all subsequent scans to the actual project.
- Within Part 1, run the 1b scans in parallel (they are independent).
- After all 3 parts, present the consolidated 4-section report.
- If a scan produces 50+ hits, sample the first 20, note the total, and flag for manual review.
- If the project uses a language or framework not listed above, adapt the env var patterns and framework-specific checks accordingly — the categories and output format remain the same.
