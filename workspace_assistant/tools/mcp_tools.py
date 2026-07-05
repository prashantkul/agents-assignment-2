"""
Part 2: GitHub MCP Integration

Configure McpToolset to connect to the GitHub MCP server.

Required: Direct configuration in Python code
Optional: File-based configuration from config/mcp_servers.json
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

# Path to MCP server configuration (for Option B)
MCP_CONFIG_PATH = Path(__file__).parent.parent / "config" / "mcp_servers.json"


# =============================================================================
# REQUIRED: Direct Configuration
# =============================================================================
# TODO: Implement get_github_mcp_toolset()
# Configure the GitHub MCP server directly in Python code.
#
# Example structure:
#
def get_github_mcp_toolset() -> McpToolset:
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not set in .env")

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": token},
    )

    return McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params)
    )


# =============================================================================
# OPTIONAL: File-based Configuration
# =============================================================================
def load_mcp_config() -> dict:
    """Load MCP server configuration from JSON file."""
    if not MCP_CONFIG_PATH.exists():
        raise FileNotFoundError(f"MCP config not found: {MCP_CONFIG_PATH}")

    with open(MCP_CONFIG_PATH) as f:
        config = json.load(f)

    # Replace environment variable placeholders
    github_config = config.get("mcpServers", {}).get("github", {})
    env = github_config.get("env", {})
    for key, value in env.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            env[key] = os.getenv(env_var, "")

    return config


# TODO: Implement get_github_mcp_toolset_from_config()
# Load configuration from config/mcp_servers.json
#
# Example structure:
#
# def get_github_mcp_toolset_from_config() -> McpToolset:
#     config = load_mcp_config()
#     github = config["mcpServers"]["github"]
#
#     token = github["env"].get("GITHUB_PERSONAL_ACCESS_TOKEN")
#     if not token:
#         raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not set in .env")
#
#     server_params = StdioServerParameters(
#         command=github["command"],
#         args=github["args"],
#         env=github["env"]
#     )
#
#     return McpToolset(
#         connection_params=StdioConnectionParams(server_params=server_params)
#     )


# =============================================================================
# BONUS (+25 points) - Tool Search Pattern
# =============================================================================
# The installed google-adk version has no `defer_loading` kwarg on McpToolset,
# so the on-demand discovery behavior is implemented by hand instead:
# - ESSENTIAL_TOOL_NAMES stays eagerly loaded (schemas always in context)
# - search_github_tools() discovers the rest by name/description only
# - call_github_tool() invokes whatever search_github_tools() found
#
# This keeps the LLM's upfront context to ~4 tool schemas (2 essential +
# 2 meta-tools) instead of all 15+ GitHub MCP tool schemas.

ESSENTIAL_TOOL_NAMES = ["search_repositories", "get_file_contents"]

_full_toolset: McpToolset | None = None
_full_tools_cache: list | None = None


async def _get_full_tools() -> list:
    """Lazily connect to the GitHub MCP server and cache its full tool list."""
    global _full_toolset, _full_tools_cache
    if _full_tools_cache is None:
        _full_toolset = get_github_mcp_toolset()
        _full_tools_cache = await _full_toolset.get_tools()
    return _full_tools_cache


async def search_github_tools(query: str) -> dict:
    """Search for available GitHub MCP tools by keyword.

    Use this to discover tools beyond the ones already loaded (e.g. issues,
    pull requests, commits) before calling call_github_tool.

    Args:
        query: Search term (e.g., "issues", "repository", "pull request").

    Returns:
        dict with 'status' and a 'tools' list of {name, description}.
    """
    try:
        tools = await _get_full_tools()
        q = query.lower()
        matches = [
            {"name": t.name, "description": t.description}
            for t in tools
            if q in t.name.lower() or q in (t.description or "").lower()
        ]
        return {"status": "success", "tools": matches}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def call_github_tool(tool_name: str, arguments: dict) -> dict:
    """Call a GitHub MCP tool discovered via search_github_tools.

    Args:
        tool_name: Exact tool name from search_github_tools results.
        arguments: Keyword arguments to pass to that tool.

    Returns:
        dict with 'status' and the tool's 'result', or an error message.
    """
    try:
        tools = await _get_full_tools()
        tool = next((t for t in tools if t.name == tool_name), None)
        if tool is None:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}
        result = await tool.run_async(args=arguments, tool_context=None)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_github_mcp_toolset_deferred() -> McpToolset:
    """Create an McpToolset restricted to only the essential, always-loaded tools."""
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not set")

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": token},
    )

    return McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params),
        tool_filter=ESSENTIAL_TOOL_NAMES,
    )


mcp_tools = [
    get_github_mcp_toolset(),
]

mcp_tools_deferred = [
    get_github_mcp_toolset_deferred(),
    search_github_tools,
    call_github_tool,
]
