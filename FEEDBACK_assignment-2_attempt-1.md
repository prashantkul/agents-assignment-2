## Grade: 100 / 100

**Assignment:** Google Workspace Assistant + GitHub MCP (ADK)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-11  ·  Commit `204461f`

> **Note: provided files were modified.** These instructor-provided files (not meant to be changed) differ from the originals: `workspace_assistant/tools/auth.py`, `workspace_assistant/main.py`, `workspace_assistant/tests/test_tools.py`, `workspace_assistant/tests/test_mcp.py`. No automatic deduction was applied. If this was a necessary setup fix, no action is needed.

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| tool_design | 18 | 18 | Option B: three plain-function tools (list_tasks, create_task, complete_task) with clear names, complete Args/Returns docstrings, and typed params (str/int/bool), collected into tasks_tools list (line 110). Fully meets the 3+ tool bar. (`workspace_assistant/tools/tasks_tools.py:110`) |
| agent_instructions | 14 | 12 | Instruction is clear and scoped, enumerates the task/GitHub capabilities and includes an explicit safety rule ('Always confirm before making changes'). Slightly generic on how to choose among tools; a bit more tool-selection guidance would earn full marks. (`workspace_assistant/agent.py:23`) |
| error_handling | 14 | 13 | All three tools wrap the API call in try/except and return a consistent {status, message} dict on failure (lines 48-49, 79-80, 106-107). Handles optional fields (notes/due) cleanly. Uses a single broad Exception catch rather than differentiating specific error cases. (`workspace_assistant/tools/tasks_tools.py:48`) |
| functionality | 14 | 14 | Statically correct: each tool routes through get_tasks_service() (auth.py:53) and calls the right Google Tasks API method - tasks().list (line 39), insert (line 77), patch with status=completed (line 98). showHidden handling for completed tasks is a thoughtful correctness touch. (`workspace_assistant/tools/tasks_tools.py:36`) |
| code_quality | 10 | 9 | Readable, well-organized, consistently documented; tools wired into an LlmAgent via create_agent() (agent.py:18-33). Minor: unused Optional import (line 7) and leftover '# @tool' comment stubs (lines 19, 52, 83). (`workspace_assistant/tools/tasks_tools.py:7`) |
| mcp_configured | 10 | 10 | McpToolset configured correctly for the GitHub MCP server via StdioServerParameters + StdioConnectionParams (lines 38-46) and attached to the agent through mcp_tools (line 186-188, agent.py:32). (`workspace_assistant/tools/mcp_tools.py:44`) |
| github_queries | 15 | 14 | GitHub queries are correctly wired through the MCP toolset - the unfiltered toolset (line 186-188) exposes the full GitHub tool surface (repos, files, issues, PRs). Reflection documents real use (searching repos, reading files, listing/creating issues/PRs). Statically sound. (`workspace_assistant/tools/mcp_tools.py:186`) |
| mcp_error_handling | 5 | 4 | Missing GITHUB_PERSONAL_ACCESS_TOKEN raises a clear ValueError (lines 34-36, 170-172), and the meta-tools wrap MCP calls in try/except returning error dicts (lines 143-144, 164-165). The eager toolset raises at import rather than returning a graceful status, so not full marks. (`workspace_assistant/tools/mcp_tools.py:34`) |
| _bonus_ | +25 | +21 | |
| Integrity deduction | — | 0 | Provided files MODIFIED — flagged, no deduction (workspace_assistant/tools/auth.py, workspace_assistant/main.py, workspace_assistant/tests/test_tools.py, workspace_assistant/tests/test_mcp.py) |
| **Total** | **100** | **100** | |

### What went well
- Clean, consistent tool design: all three Tasks tools are plain typed functions with complete Args/Returns docstrings and a uniform {status, ...} return contract (tasks_tools.py:20-110).
- Statically correct Google Tasks API usage through get_tasks_service(), including the showHidden nuance for surfacing completed tasks (tasks_tools.py:39-46).
- Strong bonus work: a hand-rolled deferred-loading pattern (search_github_tools/call_github_tool + tool_filter) with a measured 77% schema-token reduction documented in the reflection (mcp_tools.py:107-194, reflection_template.md:66-74).
- Thoughtful, honest 1200-word reflection that traces real debugging (OAuth scope layers, framework API drift, search-index limitations) rather than restating the code.

### What to improve (actionable)
- Add more explicit tool-selection guidance to the system instruction (e.g. when to prefer Tasks vs GitHub tools) to strengthen agent_instructions (agent.py:23-26).
- Differentiate error handling beyond a single broad `except Exception` - surface auth/scope vs not-found cases distinctly so the agent can react appropriately (tasks_tools.py:48).
- Have the eager GitHub toolset degrade gracefully (return a status dict) instead of raising at import when the token is missing (mcp_tools.py:186-188).
- Remove the unused Optional import and leftover '# @tool' comment stubs for a cleaner tool module (tasks_tools.py:7,19,52,83).
- Consider the per-service token-file scoping noted in your own reflection to remove the latent shared-TOKEN_FILE scope-collision bug (auth.py:19).

### Automated checks
- ✅ All required files implemented
- ⚠️ Provided files MODIFIED — flagged, no deduction (workspace_assistant/tools/auth.py, workspace_assistant/main.py, workspace_assistant/tests/test_tools.py, workspace_assistant/tests/test_mcp.py)
- ✅ 0/0 output artifacts committed
- ✅ Reflection 1202 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*


---
<sub>🔎 **Autograder record** — attempt 1 of 2 · graded at commit `204461f` · delivered 2026-07-11T18:01:11Z. Commits pushed to `main` after this timestamp are treated as a resubmission.</sub>
