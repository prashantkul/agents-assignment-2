# GitHub MCP Server Setup

## Step 1: Create a GitHub Personal Access Token

1. GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with these scopes:
   - `repo` - full control of private repositories (or `public_repo` for public repos only)
   - `write:issues` - create and update issues
3. Copy the token immediately (you won't see it again)

## Step 2: Configure Environment

Add to `.env`:
```bash
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxx
```

## Step 3: MCP Server Configuration

The GitHub MCP server is configured in `config/mcp_servers.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

## Step 4: Integrate with Your Agent

Use these imports in `tools/mcp_tools.py`:
```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
```

Load the config and create your toolset:
```python
config = load_mcp_config()
github = config["mcpServers"]["github"]

server_params = StdioServerParameters(
    command=github["command"],
    args=github["args"],
    env=github["env"]
)

toolset = McpToolset(
    connection_params=StdioConnectionParams(server_params=server_params)
)
```

## Step 5: Test

```bash
python -m tests.test_mcp
```

## Troubleshooting

- **Bad credentials**: Token expired or missing scopes
- **Server won't start**: Check Node.js is installed (`node --version`)
- **Tool not found**: McpToolset auto-discovers tools on connection
