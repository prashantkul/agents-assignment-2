# Assignment 2: Google Workspace Assistant + MCP Server

**UCLA Extension - Agentic AI Course**

---

## Overview

| Part | Focus | Points |
|------|-------|--------|
| **Part 1** | Build a Google Workspace agent with ADK | 70 |
| **Part 2** | Connect to GitHub via MCP Server | 30 |

---

# Part 1: Google Workspace Assistant (70 points)

Build an AI agent using **Agent Development Kit (ADK)**.

**Choose ONE option:**

| Option | Focus |
|--------|-------|
| **A** | Calendar Assistant - Schedule meetings, find free time, manage conflicts |
| **B** | Tasks Manager - Create tasks, track to-dos, manage deadlines |

## Requirements

1. **Minimum 3 tools** with clear names and descriptions
2. **Error handling** with user-friendly messages
3. **System instruction** that guides the agent's behavior

## Option A: Calendar Tools

| Tool | Purpose |
|------|---------|
| `list_upcoming_events` | Get events for a date range |
| `find_available_slots` | Find free time between participants |
| `create_event` | Schedule a new meeting |
| `check_conflicts` | Detect scheduling conflicts |
| `reschedule_event` | Move an existing event |

## Option B: Tasks Tools

| Tool | Purpose |
|------|---------|
| `list_tasks` | Get tasks from a list |
| `create_task` | Add a new task |
| `complete_task` | Mark a task as done |
| `update_task` | Modify task details |
| `delete_task` | Remove a task |

---

# Part 2: GitHub MCP Server (30 points)

Extend your agent to interact with GitHub using **McpToolset**.

## What You Need to Do

1. Create a GitHub Personal Access Token with `repo` scope
2. Configure `McpToolset` to connect to the GitHub MCP server
3. Update your system instruction to include GitHub capabilities

## Key Classes

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
```

## GitHub MCP Server

### Required: Direct Configuration
```python
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": token}
)

toolset = McpToolset(
    connection_params=StdioConnectionParams(server_params=server_params)
)
```

### Optional: File-based Configuration
Alternatively, load from `config/mcp_servers.json`:
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

Use the provided `load_mcp_config()` helper to load and parse this config.

## Required GitHub Functionality

Your agent should handle:
1. "List my GitHub repositories"
2. "Show open issues in [repo]"
3. "Create an issue in [repo] about [topic]"

---

## Evaluation Rubric

### Part 1: Google Workspace (70 pts)

| Component | Points |
|-----------|--------|
| Tool Design | 18 |
| Agent Instructions | 14 |
| Error Handling | 14 |
| Functionality | 14 |
| Code Quality | 10 |

### Part 2: GitHub MCP (30 pts)

| Component | Points |
|-----------|--------|
| McpToolset Configured | 10 |
| GitHub Queries Work | 15 |
| Error Handling | 5 |

**Bonus (+25):** Implement tool search with `defer_loading`

### Bonus: Tool Search Pattern (+25 pts)

**What:** Implement the `defer_loading` pattern so your agent doesn't load all 15+ GitHub MCP tools upfront—only searches and loads what it needs.

**Why:** Reduces token usage by ~80% (from ~8K to ~1.5K tokens for GitHub tools).

**How:**
1. Add a `search_github_tools` tool to your agent (10 pts)
2. Configure McpToolset with `defer_loading=True` (10 pts)
3. Implement `create_agent_with_tool_search()` in agent.py (5 pts)

**Required Comparison:**
In your reflection, include a comparison showing token/context bloat:
- Run your agent **without** `defer_loading` and note the context size
- Run your agent **with** `defer_loading` and note the context size
- Calculate the % reduction in tokens

Example comparison:
| Mode | Tools Loaded | Approx Tokens |
|------|--------------|---------------|
| Without defer_loading | 15+ GitHub tools | ~8,000 |
| With defer_loading | 1-2 tools + search | ~1,500 |
| **Savings** | | **~80%** |

See `tools/mcp_tools.py` for scaffolding

---

## Getting Started

```bash
conda create -n workspace-agent python=3.11 -y
conda activate workspace-agent
pip install -r requirements.txt
cp .env.example .env
# Add your tokens to .env

python main.py --interactive
python -m tests.grader --all
```

---

## Testing with ADK Web UI

ADK provides a built-in web interface for testing your agent interactively.

### Start the Web UI

```bash
cd workspace_assistant
adk web
```

This launches a local web server (typically at `http://localhost:8000`).

### Using the Web UI

1. **Select your agent** from the dropdown (should show your `workspace_assistant`)
2. **Type queries** in the chat interface to test your tools
3. **View tool calls** - the UI shows which tools are invoked and their responses
4. **Debug errors** - see full error messages and stack traces

### Test Queries to Try

**Part 1 - Calendar (Option A):**
- "What meetings do I have tomorrow?"
- "Find a free slot for a 1-hour meeting next week"
- "Schedule a team sync for Monday at 2pm"

**Part 1 - Tasks (Option B):**
- "Show my tasks"
- "Add a task: Review PR by Friday"
- "Mark the first task as complete"

**Part 2 - GitHub MCP:**
- "List my GitHub repositories"
- "Show open issues in octocat/Hello-World"
- "Create an issue in my-repo about fixing the login bug"

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not appearing | Ensure `agent.py` has a valid `create_agent()` function |
| Tools not showing | Check that tools are added to the agent's `tools` list |
| MCP connection failed | Verify `GITHUB_PERSONAL_ACCESS_TOKEN` in `.env` |
| Import errors | Run `pip install -r requirements.txt` |

---

## Submission

1. Run `python -m tests.grader --all` to verify your score
2. Record a 2-3 minute demo
3. Complete `docs/reflection.md`
4. ZIP your project (exclude `credentials/`, `__pycache__/`)

---

## Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK MCP Tools](https://google.github.io/adk-docs/tools-custom/mcp-tools/)
- [Google Calendar API](https://developers.google.com/calendar/api)
- [Google Tasks API](https://developers.google.com/tasks)
- [GitHub MCP Server](https://github.com/modelcontextprotocol/servers)
