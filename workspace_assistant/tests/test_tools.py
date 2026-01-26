"""
Test harness for Part 1: Google Workspace Tools

Usage: python -m tests.test_tools

This helps you verify your tools work before submission.
"""

import inspect


def check_tool_requirements(tools: list, option: str) -> dict:
    """Check if tools meet basic requirements."""
    results = {
        "option": option,
        "checks": [],
        "passed": 0,
        "total": 0
    }

    # Check 1: At least 3 tools
    results["total"] += 1
    if len(tools) >= 3:
        results["passed"] += 1
        results["checks"].append(f"✓ {len(tools)} tools implemented (need 3+)")
    else:
        results["checks"].append(f"✗ Only {len(tools)} tools (need 3+)")

    # Check 2: Tools have docstrings
    results["total"] += 1
    with_docs = sum(1 for t in tools if t.__doc__ and len(t.__doc__) > 20)
    if with_docs == len(tools) and len(tools) > 0:
        results["passed"] += 1
        results["checks"].append(f"✓ All tools have docstrings")
    else:
        results["checks"].append(f"✗ {with_docs}/{len(tools)} tools have docstrings")

    # Check 3: Tools have type hints
    results["total"] += 1
    with_hints = sum(1 for t in tools if t.__annotations__)
    if with_hints == len(tools) and len(tools) > 0:
        results["passed"] += 1
        results["checks"].append(f"✓ All tools have type hints")
    else:
        results["checks"].append(f"✗ {with_hints}/{len(tools)} tools have type hints")

    # Check 4: Tools use action verbs
    results["total"] += 1
    verbs = ["list", "get", "find", "create", "check", "update", "delete", "complete", "reschedule"]
    with_verbs = sum(1 for t in tools if any(t.__name__.startswith(v) for v in verbs))
    if with_verbs == len(tools) and len(tools) > 0:
        results["passed"] += 1
        results["checks"].append(f"✓ All tools use action verb names")
    else:
        results["checks"].append(f"✗ {with_verbs}/{len(tools)} tools use action verbs")

    # Check 5: Tools have error handling
    results["total"] += 1
    with_try = 0
    for t in tools:
        try:
            src = inspect.getsource(t)
            if "try:" in src and "except" in src:
                with_try += 1
        except:
            pass
    if with_try == len(tools) and len(tools) > 0:
        results["passed"] += 1
        results["checks"].append(f"✓ All tools have error handling")
    else:
        results["checks"].append(f"✗ {with_try}/{len(tools)} tools have try/except")

    return results


def check_agent():
    """Check if agent is properly configured."""
    results = {
        "checks": [],
        "passed": 0,
        "total": 0
    }

    # Check 1: Agent can be created
    results["total"] += 1
    try:
        from agent import create_agent
        agent = create_agent()
        results["passed"] += 1
        results["checks"].append("✓ create_agent() works")
    except NotImplementedError:
        results["checks"].append("✗ create_agent() not implemented")
        return results
    except Exception as e:
        results["checks"].append(f"✗ create_agent() error: {str(e)[:40]}")
        return results

    # Check 2: Agent has system instruction
    results["total"] += 1
    instr = getattr(agent, 'instruction', '') or ''
    if len(instr) > 100:
        results["passed"] += 1
        results["checks"].append(f"✓ System instruction defined ({len(instr)} chars)")
    else:
        results["checks"].append(f"✗ System instruction too short ({len(instr)} chars)")

    # Check 3: Agent has tools
    results["total"] += 1
    tools = getattr(agent, 'tools', []) or []
    if len(tools) >= 3:
        results["passed"] += 1
        results["checks"].append(f"✓ Agent has {len(tools)} tools")
    else:
        results["checks"].append(f"✗ Agent has {len(tools)} tools (need 3+)")

    return results


def main():
    print("=" * 50)
    print("Part 1: Tool Requirements Check")
    print("=" * 50)

    # Try to detect which option student implemented
    option = None
    tools = []

    try:
        from tools.calendar_tools import calendar_tools
        if len(calendar_tools) > 0:
            option = "calendar"
            tools = calendar_tools
            print(f"\nDetected: Option A (Calendar)")
    except ImportError:
        pass

    if not option:
        try:
            from tools.tasks_tools import tasks_tools
            if len(tasks_tools) > 0:
                option = "tasks"
                tools = tasks_tools
                print(f"\nDetected: Option B (Tasks)")
        except ImportError:
            pass

    if not option:
        print("\n✗ No tools found in calendar_tools or tasks_tools")
        print("  Implement at least 3 tools in one of these files.")
        return

    # Check tools
    tool_results = check_tool_requirements(tools, option)
    print(f"\nTool Checks:")
    for check in tool_results["checks"]:
        print(f"  {check}")
    print(f"\nTools: {tool_results['passed']}/{tool_results['total']} checks passed")

    # Check agent
    print("\n" + "=" * 50)
    print("Agent Configuration Check")
    print("=" * 50)

    agent_results = check_agent()
    print(f"\nAgent Checks:")
    for check in agent_results["checks"]:
        print(f"  {check}")
    print(f"\nAgent: {agent_results['passed']}/{agent_results['total']} checks passed")

    # Summary
    total_passed = tool_results["passed"] + agent_results["passed"]
    total_checks = tool_results["total"] + agent_results["total"]

    print("\n" + "=" * 50)
    print(f"TOTAL: {total_passed}/{total_checks} checks passed")
    print("=" * 50)

    if total_passed == total_checks:
        print("\n✓ All checks passed! Ready for MCP integration (Part 2).")
    else:
        print("\n⚠ Some checks failed. Review the items above.")


if __name__ == "__main__":
    main()
