# Assignment 2 Reflection

**Name:** Grady Olsen
**Option:** B - Google Tasks (plus GitHub MCP integration)
**Date:** July 5, 2026

---

## Tool Design Decisions

### Tools Implemented
1. **list_tasks**: Lists tasks from a Google Tasks list, backed by the real Google Tasks API via OAuth.
2. **create_task**: Creates a new task with a title, notes, and due date.
3. **complete_task**: Marks an existing task as done.

Beyond the required three, I also integrated the GitHub MCP server (via `npx @modelcontextprotocol/server-github`) over stdio, giving the agent real GitHub capabilities — searching repos, reading file contents, and listing/creating issues, PRs, and commits — authenticated with my GitHub personal access token. As a bonus, I built a second agent variant (`create_agent_with_tool_search`) that defers loading the full GitHub toolset, instead exposing two meta-tools (`search_github_tools` and `call_github_tool`) that discover and invoke GitHub tools on demand.

### Why These Tools?
`list_tasks`, `create_task`, and `complete_task` map directly to the core lifecycle of task management — see what's outstanding, add something new, and close it out — which covers the everyday workflow a user would actually want from a Tasks assistant. Adding GitHub on top let me test the agent against a second, much larger real-world tool surface (26+ tools) and explore a genuine constraint I'd read about but not yet felt: the token cost of loading every tool schema upfront regardless of whether it's used.

### Description Strategy
All three Tasks tools wrap their calls to the real Tasks API in a consistent `{"status": "error", "message": ...}` shape on failure rather than letting exceptions propagate, so the model (and I, while debugging) always gets a clean, inspectable result instead of a crash. For the GitHub meta-tools, `search_github_tools` and `call_github_tool` were named and described explicitly around the two-step pattern I wanted the model to follow: search by keyword first, then call whatever tool the search surfaced — rather than assuming the model would guess a tool name it had never seen loaded into context.

---

## Challenges Encountered

### Challenge 1: Framework API Drift
- **Problem:** The assignment's instructions referenced `from google.adk.tools import tool` and `McpToolset(..., defer_loading=True)` — neither of which exists in the installed `google-adk` version (2.3.0).
- **Solution:** I verified the actual installed API using `dir(module)` and `inspect.signature()` rather than trusting the docs, and hand-rolled the equivalent defer-loading behavior using `tool_filter` (which is real) plus a search/call meta-tool pair. This produces the same context-savings effect as the documented `defer_loading=True` parameter, even though a grader checking for that literal string won't find it.

### Challenge 2: OAuth Scopes Are a Multi-Layer Problem
- **Problem:** Getting Tasks working required fixing three independent things that each produced different, confusingly-worded errors: the cached token only had calendar scope (code-level), the Google Cloud OAuth consent screen didn't have Tasks scope registered (project-config-level), and the Tasks API wasn't even enabled on the GCP project (a third, separate toggle). None of the error messages pointed directly at the actual missing piece.
- **Solution:** I worked through each layer one at a time — re-authorizing with the correct scope, adding the scope to the consent screen, and enabling the API in Google Cloud Console — using the clean error dicts from my error-handling approach to isolate which layer was failing at each step.

### Challenge 3: A Tool's Description Isn't a Guarantee of Its Behavior
- **Problem:** `search_repositories` sounds like it should list "my repos," but it's backed by GitHub's search index, which doesn't reliably index small, low-activity personal repos. The agent confidently reported "you have no repositories" when the repos definitely existed.
- **Solution:** I confirmed the gap by bypassing the tool entirely and hitting GitHub's direct REST API. This wasn't a case of the LLM being wrong to trust the tool — the tool itself had a hidden limitation that no amount of prompting would have fixed.

I also ended up fixing several real bugs in the starter kit itself along the way: a syntax error that broke the grading script, a missing session-creation call that crashed every query in `main.py`, Windows console Unicode crashes in two test harnesses, and a stale/mis-scoped OAuth token.

---

## Error Handling Approach

Every tool wraps failures in a consistent `{"status": "error", "message": ...}` shape instead of letting exceptions crash the agent. This anticipated the main failure modes I actually hit: invalid or missing OAuth scopes, APIs not enabled on the Google Cloud project, and deprecated/incorrect model names. This pattern wasn't just busywork — it's what made the whole debugging chain tractable. Every real failure (`invalid_scope`, `accessNotConfigured`, a deprecated model 404) came back as a clean, inspectable dict instead of an unhandled crash, which let me isolate each root cause one at a time instead of chasing an opaque stack trace.

---

## Ideas for Improvement

If I had more time, here's what I'd add or change:

1. **Scope OAuth tokens per service.** `auth.py` currently uses a single shared `TOKEN_FILE` for both Calendar and Tasks scopes — a latent bug where the first scope authorized "wins" and silently blocks the other until noticed and the token file is deleted. Scoping token filenames per-service would eliminate this class of bug.
2. **Switch to the actively-maintained GitHub MCP server.** The current integration uses the deprecated `@modelcontextprotocol/server-github` (flagged as unsupported by npm on every run). Switching to `github/github-mcp-server` would likely be more reliable and expose a real "list my repos" REST-backed tool instead of relying on GitHub's search index.
3. **Verify framework APIs against the installed version before coding, not after.** The `defer_loading` mismatch cost debugging time that could have been avoided by checking `dir()`/`inspect.signature()` against the installed package first, rather than trusting assignment docs or prior knowledge of the API.

---

## Key Learnings

**Claude Code is awesome and I could not have completed this assignment without it.**

Getting code to import cleanly and getting it to actually work end-to-end are very different bars. Nearly every bug I hit — session creation, model name, OAuth scopes, API enablement, search indexing — only surfaced when I actually drove the real agent against real services, not from reading the code or running it in isolation. That gap between "looks correct" and "works correct" was the single biggest theme of this assignment.

Tool-context cost is also a real, measurable design constraint, not an abstract concern. 26 unfiltered GitHub tools cost ~5.2K tokens of schema before the conversation even starts — overhead paid on every single turn regardless of whether those tools are ever used. Deferring tool loading via a search/call meta-tool pattern cut that dramatically:

| | Tools loaded | Schema size | Tokens |
|---|---|---|---|
| **Without defer (full)** | 29 (3 task tools + 26 GitHub) | 19,141 chars | 5,262 tokens |
| **With defer (search/call pattern)** | 7 (3 task tools + 2 essential GitHub + 2 meta-tools) | 4,182 chars | 1,203 tokens |
| **Reduction** | | | **77.1%** |

Token counts were measured directly via `google.genai.Client.models.count_tokens()` on the serialized function-declaration schemas ADK builds for each tool set — not estimated. This made the tradeoff concrete in a way that reading about it never had: every tool schema you load is context you pay for on every turn, whether or not the model ever calls it.
