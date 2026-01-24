# Offline AI Mode Guide

This guide explains how to use **Nematron 4 Nano** (or any model) running locally in **LM Studio** with **Antigravity**. This allows you to code with AI assistance even without an internet connection (e.g., on an airplane).

## Prerequisites

1. **LM Studio**: Download and install [LM Studio](https://lmstudio.ai/).
2. **Model**: Download a model inside LM Studio (e.g., `nvidia/nemotron-4-nano`).
3. **Python**: Ensure Python 3 is installed.

## Setup Instructions

We have provided a script `setup_offline_ai.py` to automate the configuration.

1. **Start LM Studio Server**:
    * Open LM Studio.
    * Go to the **Local Server** (double-arrow icon) tab on the left.
    * **Select a model** from the dropdown at the top.
    * Click **Start Server**.
    * Ensure the port is `1234` (default).

2. **Run the Setup Script**:
    Open your terminal in this directory and run:

    ```bash
    python3 setup_offline_ai.py
    ```

    This script will:
    * Install the `mcp` python package if missing.
    * Create `lmstudio_mcp.py` (the bridge between Antigravity and LM Studio).
    * Create `mcp-config.json` configured to run that script.
    * Check if it can see your LM Studio instance.

3. **Configure Antigravity / VS Code**:
    * You need to ensure VS Code / Antigravity sees the `mcp-config.json`.
    * **Option A (Global)**: Move the content of `mcp-config.json` into your global MCP config (found via Command Palette: *MCP: Open Settings*).
    * **Option B (Workspace)**: If you are opening this folder directly, VS Code might pick up the `mcp-config.json` in the root.
    * **Reload**: Run Command Palette -> `Developer: Reload Window` to apply changes.

## Usage

Once setup is complete and Antigravity has reloaded:

1. Open Antigravity Chat.
2. You should be able to use the **`lmstudio_chat`** tool or see the model available if configured as a custom model.
3. If configured as a tool, you can ask Antigravity to "ask the local model" or it may be available as a discrete model selection depending on your specific extension version.

### Context Awareness (Offline)

The `lmstudio_chat` server now includes a **`get_pack_context`** tool.
* Use it to feed `.agent/task.md` and recent handoff notes into the local model.
* Example prompt: "Use get_pack_context to understand the project state, then summarize the current objective."

### Hybrid Workflow

You can combine **LM Studio** for coding and **Gemini CLI** (if configured) for architectural auditing. Gemini's 1M+ token window is excellent for analyzing large plans locally.

### Quick Command

We have included a workflow so you can easily access the model:

* Type **`/lmstudio [your prompt]`** in the chat.
  * Example: `/lmstudio write me a poem about rust`
* This will automatically route your request to the local model.

## Troubleshooting

* **"Connection Refused"**:
  * Is LM Studio running?
  * Is the Server started (Green indicator in LM Studio)?
  * Is it on port 1234?

* **"mcp module not found"**:
  * The script tries to install it, but if it fails, run `pip install mcp` manually.

* **Slow Responses**:
  * Local models depend on your hardware. Ensure you are using a "Nano" or "Quantized" model for speed on laptops.
