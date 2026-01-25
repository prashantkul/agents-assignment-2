#!/usr/bin/env python3
"""
Google Workspace Assistant - Entry Point

Usage:
    python main.py --interactive
    python main.py "What meetings do I have today?"
"""

import argparse
import asyncio
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown

from agent import create_agent

console = Console()


async def run_query(agent, query: str) -> str:
    """Execute a query and return the response."""
    try:
        response = await agent.run(query)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


async def interactive_mode(agent):
    """Run in interactive mode."""
    console.print("[bold green]Google Workspace Assistant[/bold green]")
    console.print("Type 'quit' to exit.\n")

    while True:
        query = Prompt.ask("[cyan]You[/cyan]")
        if query.lower() in ('quit', 'exit', 'q'):
            break
        if not query.strip():
            continue

        with console.status("Thinking..."):
            response = await run_query(agent, query)

        console.print("\n[green]Assistant[/green]")
        console.print(Markdown(response))
        console.print()


async def main():
    parser = argparse.ArgumentParser(description="Google Workspace Assistant")
    parser.add_argument("query", nargs="?", help="Query to send")
    parser.add_argument("--interactive", "-i", action="store_true")

    args = parser.parse_args()
    agent = create_agent()

    if args.interactive:
        await interactive_mode(agent)
    elif args.query:
        response = await run_query(agent, args.query)
        console.print(Markdown(response))
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
