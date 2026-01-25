"""
Test harness for Part 2: GitHub MCP Integration

Usage: python -m tests.test_mcp
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MCP_TEST_QUERIES = [
    {"query": "List my GitHub repositories", "tool": "search_repositories"},
    {"query": "Show open issues in octocat/Hello-World", "tool": "list_issues"},
    {"query": "Show me the README from octocat/Hello-World", "tool": "get_file_contents"},
]


def check_environment():
    """Check prerequisites."""
    print("=" * 40)
    print("Environment Check")
    print("=" * 40)

    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token or token.startswith("ghp_xxx"):
        print("❌ GITHUB_PERSONAL_ACCESS_TOKEN not configured")
        return False
    print(f"✓ GitHub token configured")

    import subprocess
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        print("✓ Node.js installed")
    except:
        print("❌ Node.js not found")
        return False

    return True


def check_agent():
    """Check agent has McpToolset."""
    print("\n" + "=" * 40)
    print("Agent Check")
    print("=" * 40)

    try:
        from agent import create_agent
        agent = create_agent()

        for tool in agent.tools:
            if "Mcp" in type(tool).__name__:
                print("✓ McpToolset found in agent")
                return True

        print("❌ No McpToolset in agent.tools")
        return False

    except NotImplementedError:
        print("❌ create_agent not implemented yet")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("GitHub MCP Test Suite\n")

    if not check_environment():
        print("\nFix environment issues first.")
        return

    if not check_agent():
        print("\nImplement McpToolset in agent.py first.")
        return

    print("\n✓ Ready for MCP testing!")
    print("Run: python main.py --interactive")
    print("Try: 'List my GitHub repositories'")


if __name__ == "__main__":
    main()
