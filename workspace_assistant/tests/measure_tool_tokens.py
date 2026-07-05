"""
Bonus: Tool Search Pattern - Token Usage Comparison

Measures actual tool-schema token overhead (via Gemini's count_tokens)
for the full GitHub MCP toolset vs. the on-demand search/call pattern.

Usage: python -m tests.measure_tool_tokens
"""

import asyncio
import json
import os
import sys

from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

from google import genai
from google.adk.tools.function_tool import FunctionTool

from tools.mcp_tools import (
    call_github_tool,
    get_github_mcp_toolset,
    get_github_mcp_toolset_deferred,
    search_github_tools,
)
from tools.tasks_tools import tasks_tools


async def declarations_for(tools: list) -> list:
    """Collect FunctionDeclarations for a mix of plain functions and toolsets."""
    decls = []
    for t in tools:
        if hasattr(t, "get_tools"):
            for sub in await t.get_tools():
                d = sub._get_declaration()
                if d:
                    decls.append(d)
        else:
            ft = t if hasattr(t, "_get_declaration") else FunctionTool(t)
            d = ft._get_declaration()
            if d:
                decls.append(d)
    return decls


async def measure(label: str, decls: list, client: genai.Client, model: str) -> int:
    schema_json = json.dumps(
        [d.model_dump(exclude_none=True, mode="json") for d in decls]
    )
    resp = client.models.count_tokens(model=model, contents=schema_json)
    print(
        f"{label}: {len(decls)} tools, {len(schema_json)} chars, "
        f"{resp.total_tokens} tokens (schema only)"
    )
    return resp.total_tokens


async def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not set in .env")
        return

    full_tools = tasks_tools + [get_github_mcp_toolset()]
    deferred_tools = tasks_tools + [
        get_github_mcp_toolset_deferred(),
        search_github_tools,
        call_github_tool,
    ]

    full_decls = await declarations_for(full_tools)
    deferred_decls = await declarations_for(deferred_tools)

    client = genai.Client(api_key=api_key)
    model = os.getenv("MODEL_NAME", "gemini-2.5-flash")

    full_tokens = await measure("Without defer (full)", full_decls, client, model)
    deferred_tokens = await measure("With defer (search/call)", deferred_decls, client, model)

    reduction = 100 * (1 - deferred_tokens / full_tokens)
    print(f"\nReduction: {reduction:.1f}%")


if __name__ == "__main__":
    asyncio.run(main())
