# Agent Environment (Shared Context)

## Roles

- codex: planner + task orchestrator for this repo/session
- human: final decider; wants minimal interaction
- hp: human-proxy for longer clarifications and writing
- ag: IDE agent with workspace access; excels at coding/execution
  (Antigravity or Copilot)

## Interaction policy

- Default autonomy; proceed without waiting when safe.
- If user input is required: ask y/no questions only; use "y" and "no".
- If detailed human input is needed: stop and request hp to produce a short
  paste-back for codex/ag.
- Keep outputs concise and actionable; cite file paths when relevant.
