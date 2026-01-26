# CLAUDE.md - Project Context

## Project Overview

Assignment 2 starter kit for UCLA Extension's Agentic AI course. Students build a Google Workspace Assistant using Google's Agent Development Kit (ADK).

## Tech Stack

- **Python**: 3.11+
- **Agent Framework**: Google ADK
- **APIs**: Google Calendar or Google Tasks API
- **MCP**: GitHub MCP Server integration
- **Auth**: OAuth 2.0 for Desktop Apps

## Project Structure

```
workspace_assistant/
├── agent.py           # Main agent definition (students complete)
├── main.py            # Entry point
├── tools/
│   ├── auth.py        # Google OAuth helper
│   ├── calendar_tools.py  # Option A stubs
│   ├── tasks_tools.py     # Option B stubs
│   └── mcp_tools.py       # Part 2: GitHub MCP integration
├── config/
│   ├── settings.py        # Configuration
│   ├── mcp_servers.json   # MCP server config (optional)
│   └── credentials/       # OAuth files (gitignored)
├── tests/
│   └── test_mcp.py        # MCP integration test
└── docs/
    ├── google_auth_setup.md
    ├── github_mcp_setup.md
    └── reflection_template.md
```

## Student Tasks

**Part 1 (70 pts):** Choose ONE option and implement:
1. At least 3 tools with proper descriptions
2. System instruction in agent.py
3. Error handling for API failures

**Part 2 (30 pts):** GitHub MCP integration:
1. Configure McpToolset for GitHub
2. Update system instruction for GitHub capabilities

**Bonus (+25 pts):** Tool search with defer_loading

## Key Commands

```bash
# Setup
conda create -n workspace-agent python=3.11 -y
conda activate workspace-agent
pip install -r requirements.txt
cp .env.example .env

# Run
python main.py --interactive

# Test with ADK Web UI
adk web
```
