# WORKFLOW: Brain Dump Processing

## Objective

Intake raw chaos, convert to structured orders. **Capture -> Validate -> Execute**.

## Steps

### 1. Capture (The Dump)

* **Input**: User transcript, voice note, or messy text.
* **Action**: Append raw text to `.agent/state/inbox.md`.

### 2. Validation (The gatekeeper)

Invoke **@ruthless_prioritizer**:

* *Input*: The new raw items.
* *Filter*: Eliminate "Shiny Objects" immediately.
* *Decay Rule*: If an item is "Someday/Maybe", date stamp it. If not touched in 30 days -> Auto-Delete.

### 3. Resource Check

Invoke **@librarian**:

* "Do we already have code/docs for [Validated Item]?"
* *If Yes*: Link to existing asset.
* *If No*: Flag as "New Build".

### 4. Structuring

Convert valid items into a **Project Brief**:

* **Goal**: [Linked to Manifest]
* **First Step**: [Immediate Action]
* **Definition of Done**: [Clear Outcome]

### 5. File Update

* Add structured items to `.agent/state/active_tasks.md`.
* Clear `.agent/state/inbox.md`.
