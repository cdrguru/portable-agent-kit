# WORKFLOW: Daily Startup

## Objective

Launch the day with high intentionality. **Zero Willpower needed** - just run the script.

## Steps

### 1. Retrospective (The Feedback Loop)

*Check yesterday's roadmap in `.agent/state/daily/`*

* **Did you complete the "One Thing"?** (Yes/No)
* *Update Metrics*: Increment `completion_streak` in `.agent/state/metrics.md` if Yes.

### 2. Ingest & Prioritize

1. Read `.agent/state/active_tasks.md`.
2. Invoke **@ruthless_prioritizer** on the list.
3. **Deprioritize**: Move any Item > 5 days old to `backlog` section.

### 3. Flight Plan (The Output)

Generate the `logs/daily/YYYY-MM-DD_roadmap.md`:

* **The One Thing**: (Must be P0).
* **The Batches**: (Grouping small P1s).
* **The Hazard**: (One distraction to avoid).

### 4. Committal

* "Paul, your flight plan is ready. Your One Thing is [TASK]. ready to begin?"

## Usage

`gemini -p "$(cat .agent/workflows/daily_startup.md)"`
