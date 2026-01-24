# lmstudio_mcp.py
import json, subprocess, os, sys
# Try to import mcp, if not found, we might need to rely on the environment
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # If mcp is not installed, we can't run.
    pass

from mcp.server.stdio import StdioServerTransport
from mcp.types import CallToolRequest, CallToolResult, TextContent, Tool

try:
    from mcp.server import Server
    from mcp.types import Resource, Tool, TextContent, EmbeddedResource
except ImportError:
    pass

# --- PASTE OF USER'S PROVIDED WRAPPER LOGIC ---
import json, subprocess, os
from mcp import MCP, Tool, errors   # <-- the MCP SDK (pip install mcp)

# -------------------------------------------------
# Configuration – adjust to match your LMStudio setup
# -------------------------------------------------
LMSTUDIO_HOST = "http://127.0.0.1"          # LMStudio runs locally
LMSTUDIO_PORT = 1234                       # default port for the local API
# We try to detect the model or use a generic alias
MODEL_ALIAS   = "local-model"   

API_URL = f"{LMSTUDIO_HOST}:{LMSTUDIO_PORT}/v1/chat/completions"

def _call_lmstudio(messages, temperature=0.7, max_tokens=-1, stream=False):
    # Prepare payload
    payload = {
        "model": MODEL_ALIAS,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    curl_cmd = [
        "curl", "-s", "-X", "POST", API_URL,
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    
    # Run curl
    result = subprocess.run(curl_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise errors.ServerError("curl failed", data=result.stderr)

    try:
        resp = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise errors.ServerError("Invalid JSON from LM Studio", data=result.stdout)

    if "error" in resp:
         raise errors.ServerError("LM Studio Error", data=str(resp["error"]))

    # The API returns: {"choices":[{"message":{"role":"assistant","content":"..."}}]}
    try:
        return resp["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        # It might be in a different format if something went wrong
        raise errors.ServerError("Unexpected LMStudio response structure", data=str(resp))

# -------------------------------------------------
# MCP tool definition
# -------------------------------------------------
def chat(messages: list[dict], temperature: float = 0.7, max_tokens: int = -1):
    """
    Chat with the locally running LMStudio model.
    messages: list of {"role": "...", "content": "..."}
    """
    try:
        return _call_lmstudio(messages, temperature, max_tokens)
    except Exception as exc:        # re‑raise as MCP‑compatible error
        raise errors.ServerError("LMStudio request failed", data=str(exc))

# Register the tool
chat_tool = Tool(
    name="lmstudio_chat",
    description="Chat with a locally-running LMStudio model. Best for general reasoning and code explanation.",
    func=chat
)

def get_pack_context():
    """Reads the current PACK context (task, plan, and last handoff) from the .agent folder."""
    context = {}
    paths = {
        "task": ".agent/task.md",
        "plan": ".agent/implementation_plan.md",
        "last_handoff": ".agent/docs/agent_handoffs/agent_conversation_log.md"
    }
    
    for key, rel_path in paths.items():
        if os.path.exists(rel_path):
            with open(rel_path, "r") as f:
                content = f.read()
                if key == "last_handoff":
                    # Just get the last 2000 chars of the log
                    context[key] = content[-2000:]
                else:
                    context[key] = content
        else:
            context[key] = "[Not found]"
            
    return json.dumps(context, indent=2)

pack_context_tool = Tool(
    name="get_pack_context",
    description="Reads the current PACK context (.agent/task.md, plan, and last handoff). Use this to ground the model in the current project state.",
    func=get_pack_context
)

if __name__ == "__main__":
    # When VS Code starts the server it expects an MCP instance.
    mcp = MCP("lmstudio-chat")
    mcp.add_tool(chat_tool)
    mcp.add_tool(pack_context_tool)
    mcp.run()
