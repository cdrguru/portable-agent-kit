#!/usr/bin/env python3
"""
setup_offline_ai.py

This script automates the setup of a local LM Studio model as an MCP server for use with Antigravity/VS Code.
It performs the following:
1. Checks for necessary dependencies (mcp package).
2. Generates the `lmstudio_mcp.py` server script.
3. Generates or advises on `mcp-config.json`.
4. Verifies connection to LM Studio (localhost:1234).

Usage:
    python3 setup_offline_ai.py
"""

import sys
import os
import json
import subprocess
import urllib.request
import urllib.error

# --- Configuration ---
LMSTUDIO_HOST = "http://127.0.0.1"
LMSTUDIO_PORT = 1234
MCP_SERVER_SCRIPT_NAME = "lmstudio_mcp.py"
MCP_CONFIG_NAME = "mcp-config.json"

# Content for the MCP server script
MCP_SERVER_CONTENT = r'''# lmstudio_mcp.py
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
    description="Chat with a locally‑running LMStudio model.",
    func=chat
)

if __name__ == "__main__":
    # When VS Code starts the server it expects an MCP instance.
    mcp = MCP("lmstudio-chat")
    mcp.add_tool(chat_tool)
    mcp.run()
'''

def install_package(package):
    print(f"[*] Installing '{package}'...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_dependencies():
    print("[-] Checking dependencies...")
    try:
        import mcp
        print("[*] 'mcp' package found.")
    except ImportError:
        print("[!] 'mcp' package NOT found.")
        install_package("mcp")

def create_server_script():
    print(f"[-] Creating {MCP_SERVER_SCRIPT_NAME}...")
    with open(MCP_SERVER_SCRIPT_NAME, "w") as f:
        f.write(MCP_SERVER_CONTENT)
    print(f"[*] Created {MCP_SERVER_SCRIPT_NAME}")

def check_lmstudio_connection():
    print(f"[-] Checking connection to LM Studio at {LMSTUDIO_HOST}:{LMSTUDIO_PORT}...")
    url = f"{LMSTUDIO_HOST}:{LMSTUDIO_PORT}/v1/models"
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("[*] Connection SUCCESSFUL.")
                print(f"[*] Available models: {json.dumps(data, indent=2)}")
                return True
    except urllib.error.URLError as e:
        print(f"[!] Connection FAILED: {e}")
        print("[!] Please ensure LM Studio is running and the server is started on port 1234.")
        return False
    except Exception as e:
        print(f"[!] Unexpected error checking connection: {e}")
        return False

def setup_config():
    print("[-] Configuring mcp-config.json...")
    
    # Define absolute path to the script script we just created
    script_path = os.path.abspath(MCP_SERVER_SCRIPT_NAME)
    
    config_entry = {
        "mcpServers": {
            "lmstudio-chat": {
                "command": sys.executable,
                "args": [script_path],
                "env": {}
            }
        }
    }
    
    # Check if mcp-config.json exists in current folder
    if os.path.exists(MCP_CONFIG_NAME):
        print(f"[!] {MCP_CONFIG_NAME} already exists.")
        print(f"[*] Please MANUALLY add the following entry to your {MCP_CONFIG_NAME}:")
        print(json.dumps(config_entry["mcpServers"], indent=2))
    else:
        # We can try to create it, but usually this lives in specific VS Code folders.
        # Since we are automating "project specific" or "user specific" setup, 
        # let's create it here and tell the user where to put it.
        with open(MCP_CONFIG_NAME, "w") as f:
            json.dump(config_entry, f, indent=2)
        print(f"[*] Created {MCP_CONFIG_NAME} in current directory.")
        print("[*] You may need to move this file to your VS Code MCP config directory,")
        print("[*] OR if using the Antigravity extension, ensure it is pointed to this config.")

def main():
    print("=== Offline AI Setup ===")
    
    # 1. Check Deps
    check_dependencies()
    
    # 2. Create Script
    create_server_script()
    
    # 3. Check Connection (Non-blocking warning)
    conn = check_lmstudio_connection()
    
    # 4. Config
    setup_config()
    
    print("\n=== Setup Complete ===")
    if not conn:
        print("[!] WARNING: Could not connect to LM Studio.")
        print("    You can still use the generated scripts, but ensure LM Studio is running")
        print("    before attempting to use the tool in Antigravity.")
    else:
        print("[*] Ready to go! Restart Antigravity/VS Code to load the new MCP server.")

if __name__ == "__main__":
    main()
