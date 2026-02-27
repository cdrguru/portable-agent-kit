# Claude Desktop (Cowork) Local Storage on macOS

**Primary Location:** `~/Library/Application Support/Claude/`
**Total Size:** ~13 GB (varies by usage)

## Directory Breakdown (sorted by size)

| Directory | Size | Purpose |
|-----------|------|---------|
| `vm_bundles/` | 11 GB | Cowork sandbox VM images |
| `local-agent-mode-sessions/` | 666 MB | **Cowork conversation history** (JSON files) |
| `Cache/` | 567 MB | Browser cache |
| `Claude Extensions/` | 369 MB | Installed extensions |
| `Code Cache/` | 328 MB | V8 code cache |
| `claude-code-vm/` | 213 MB | VM runtime files |
| `claude-code/` | 178 MB | Claude Code CLI data |
| `IndexedDB/` | 900 KB | Browser IndexedDB (cloud sync) |
| `Local Storage/` | 564 KB | LevelDB local storage |
| `Session Storage/` | 136 KB | Ephemeral session data |

## Key Conversation History Locations

### 1. Cowork (Agent Mode) Conversations

```
~/Library/Application Support/Claude/local-agent-mode-sessions/
└── {account-uuid}/
    └── {workspace-uuid}/
        ├── local_*.json        # Individual session files (19-104KB each)
        ├── local_*/            # Session subdirectories with attachments
        ├── cowork_settings.json
        ├── cowork_plugins/
        └── debug/
```

Each `local_*.json` file contains the full conversation history for one Cowork session.

### 2. Cloud Sync (Regular Chat) Conversations

```
~/Library/Application Support/Claude/IndexedDB/https_claude.ai_0.indexeddb.leveldb/
```

LevelDB format, synced with claude.ai. Contains cached conversation data for the web UI.

### 3. Local Storage (LevelDB)

```
~/Library/Application Support/Claude/Local Storage/leveldb/
```

Contains app state, preferences, and cached data in LevelDB format.

## Config Files

| File | Purpose |
|------|---------|
| `claude_desktop_config.json` | MCP servers, trusted folders, Chrome extension pairing |
| `config.json` | UI preferences, window state, OAuth tokens (encrypted) |
| `window-state.json` | Window position and size |

### claude_desktop_config.json Structure

```json
{
  "mcpServers": { ... },
  "preferences": {
    "chromeExtension": { "pairedDeviceId": "...", "pairedDeviceName": "..." },
    "localAgentModeTrustedFolders": [ "/path/to/folder", ... ],
    "coworkScheduledTasksEnabled": true,
    "coworkWebSearchEnabled": true
  }
}
```

## To Manage/Delete Conversations

### Delete Cowork sessions only

```bash
rm -rf ~/Library/Application\ Support/Claude/local-agent-mode-sessions/
```

### Clear caches (free up space)

```bash
rm -rf ~/Library/Application\ Support/Claude/Cache/
rm -rf ~/Library/Application\ Support/Claude/Code\ Cache/
rm -rf ~/Library/Application\ Support/Claude/GPUCache/
```

### Full reset (all local data)

```bash
rm -rf ~/Library/Application\ Support/Claude/
```

**Warning:** This removes all local settings, MCP configs, and cached conversations. Cloud conversations remain on claude.ai.

## Paths That DO NOT Exist

These locations are sometimes suggested but are not used by Claude Desktop:

- `~/Library/Application Support/com.anthropic.claude/`
- `~/Library/Containers/com.anthropic.claude/`
- `~/Library/Caches/Claude/`
- `~/Library/Caches/com.anthropic.claude/`

## Notes

- Conversation history in Cowork mode is stored locally as JSON files
- Regular Claude chat conversations sync to claude.ai and are cached in IndexedDB
- The `vm_bundles/` directory is the largest; contains sandboxed execution environments
- MCP server configurations are in `claude_desktop_config.json`
- OAuth tokens in `config.json` are encrypted

---

*Last verified: 2026-02-26*
