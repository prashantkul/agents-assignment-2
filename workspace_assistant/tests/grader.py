#!/usr/bin/env python3
"""
Automated Grader for Assignment 2

Usage:
    python -m tests.grader --option calendar
    python -m tests.grader --option tasks
    python -m tests.grader --all
"""

import argparse
import inspect
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from tests.mocks import setup_mocks
from tests.test_cases import CALENDAR_TESTS, TASKS_TESTS


@dataclass
class Scores:
    # Part 1: Google Workspace (70 pts)
    tool_design: float = 0.0        # 18 pts
    agent_instructions: float = 0.0  # 14 pts
    error_handling: float = 0.0      # 14 pts
    functionality: float = 0.0       # 14 pts
    code_quality: float = 0.0        # 10 pts

    # Part 2: GitHub MCP (30 pts)
    mcp_connected: float = 0.0       # 10 pts
    github_queries: float = 0.0      # 15 pts
    mcp_error_handling: float = 0.0  # 5 pts

    bonus: float = 0.0               # 25 pts

    @property
    def part1_total(self) -> float:
        return self.tool_design + self.agent_instructions + self.error_handling + self.functionality + self.code_quality

    @property
    def part2_total(self) -> float:
        return self.mcp_connected + self.github_queries + self.mcp_error_handling

    @property
    def total(self) -> float:
        return self.part1_total + self.part2_total + self.bonus


class Grader:
    def __init__(self, option: str):
        self.option = option
        self.scores = Scores()
        self.details = {}
        self.passed = 0
        self.total = 0

    def grade(self) -> dict:
        setup_mocks(self.option)

        # Part 1
        self._grade_tool_design()
        self._grade_agent_instructions()
        self._grade_error_handling()
        self._grade_functionality()
        self._grade_code_quality()

        # Part 2
        self._grade_mcp()

        # Bonus
        self._grade_bonus()

        return {
            "option": self.option,
            "timestamp": datetime.now().isoformat(),
            "scores": asdict(self.scores),
            "part1_total": self.scores.part1_total,
            "part2_total": self.scores.part2_total,
            "total": self.scores.total,
            "details": self.details,
            "tests_passed": self.passed,
            "tests_total": self.total,
        }

    def _get_tools(self):
        try:
            if self.option == "calendar":
                from tools.calendar_tools import calendar_tools
                return calendar_tools
            elif self.option == "tasks":
                from tools.tasks_tools import tasks_tools
                return tasks_tools
        except ImportError:
            pass
        return []

    def _is_implemented(self, func) -> bool:
        try:
            source = inspect.getsource(func)
            return "NotImplementedError" not in source
        except:
            return False

    def _grade_tool_design(self):
        """Grade tool design (18 points)."""
        tools = self._get_tools()
        implemented = [t for t in tools if self._is_implemented(t)]
        points = 0.0
        details = []

        # 3+ tools (6 pts)
        if len(implemented) >= 3:
            points += 6
            details.append(f"✓ {len(implemented)} tools implemented (6/6)")
        else:
            details.append(f"✗ Only {len(implemented)} tools, need 3 (0/6)")

        # Names (4 pts)
        verbs = ["list", "get", "find", "create", "check", "update", "delete", "complete", "reschedule"]
        good_names = sum(1 for t in implemented if any(t.__name__.startswith(v) for v in verbs))
        name_pts = min(4, (good_names / max(len(implemented), 1)) * 4)
        points += name_pts
        details.append(f"{'✓' if name_pts >= 3 else '✗'} Action-oriented names ({name_pts:.0f}/4)")

        # Descriptions (4 pts)
        desc_score = sum(1 for t in implemented if t.__doc__ and len(t.__doc__) > 30)
        desc_pts = min(4, (desc_score / max(len(implemented), 1)) * 4)
        points += desc_pts
        details.append(f"{'✓' if desc_pts >= 3 else '✗'} Descriptions ({desc_pts:.0f}/4)")

        # Type hints (4 pts)
        typed = sum(1 for t in implemented if t.__annotations__)
        type_pts = min(4, (typed / max(len(implemented), 1)) * 4)
        points += type_pts
        details.append(f"{'✓' if type_pts >= 3 else '✗'} Type hints ({type_pts:.0f}/4)")

        self.scores.tool_design = min(18, points)
        self.details["tool_design"] = details

    def _grade_agent_instructions(self):
        """Grade agent instructions (14 points)."""
        points = 0.0
        details = []

        try:
            from agent import create_agent
            agent = create_agent()
            instr = getattr(agent, 'instruction', '') or ''

            if len(instr) > 100:
                points += 6
                details.append("✓ System instruction defined (6/6)")
            else:
                details.append("✗ System instruction too short (0/6)")

            if any(w in instr.lower() for w in ["can", "help", "assist", "capabilities"]):
                points += 4
                details.append("✓ Defines capabilities (4/4)")
            else:
                details.append("✗ Missing capabilities (0/4)")

            if any(w in instr.lower() for w in ["error", "fail", "issue", "wrong"]):
                points += 4
                details.append("✓ Error guidance (4/4)")
            else:
                details.append("✗ Missing error guidance (0/4)")

        except Exception as e:
            details.append(f"✗ Could not load agent: {e}")

        self.scores.agent_instructions = min(14, points)
        self.details["agent_instructions"] = details

    def _grade_error_handling(self):
        """Grade error handling (14 points)."""
        tools = self._get_tools()
        implemented = [t for t in tools if self._is_implemented(t)]
        points = 0.0
        details = []

        # try/except patterns (7 pts)
        has_try = 0
        for t in implemented:
            try:
                src = inspect.getsource(t)
                if "try:" in src and "except" in src:
                    has_try += 1
            except:
                pass
        try_pts = min(7, (has_try / max(len(implemented), 1)) * 7)
        points += try_pts
        details.append(f"{'✓' if try_pts >= 5 else '✗'} Error handling patterns ({try_pts:.0f}/7)")

        # Validation (7 pts)
        tests = CALENDAR_TESTS if self.option == "calendar" else TASKS_TESTS
        val_tests = [t for t in tests if t.get("type") == "validation"]
        passed = 0
        for test in val_tests:
            if test["func"] is None:
                continue
            try:
                result = test["func"](**test.get("invalid_input", {}))
                if isinstance(result, dict) and result.get("status") == "error":
                    passed += 1
            except (ValueError, TypeError):
                passed += 1
            except:
                pass
        val_pts = min(7, (passed / max(len(val_tests), 1)) * 7) if val_tests else 3
        points += val_pts
        details.append(f"{'✓' if val_pts >= 5 else '✗'} Input validation ({val_pts:.0f}/7)")

        self.scores.error_handling = min(14, points)
        self.details["error_handling"] = details

    def _grade_functionality(self):
        """Grade functionality (14 points)."""
        tests = CALENDAR_TESTS if self.option == "calendar" else TASKS_TESTS
        func_tests = [t for t in tests if t.get("type") == "functional"]

        self.total = len(func_tests)
        details = []

        for test in func_tests:
            if test["func"] is None:
                continue
            try:
                result = test["func"](**test.get("input", {}))
                if isinstance(result, dict):
                    expected = test.get("expected_keys", [])
                    if all(k in result for k in expected):
                        self.passed += 1
            except NotImplementedError:
                pass
            except Exception as e:
                details.append(f"Test {test['name']}: {str(e)[:30]}")

        pts = (self.passed / max(self.total, 1)) * 14
        details.insert(0, f"Passed {self.passed}/{self.total} tests ({pts:.0f}/14)")

        self.scores.functionality = pts
        self.details["functionality"] = details

    def _grade_code_quality(self):
        """Grade code quality (10 points)."""
        tools = self._get_tools()
        implemented = [t for t in tools if self._is_implemented(t)]
        points = 0.0
        details = []

        # Docstrings (5 pts)
        has_doc = sum(1 for t in implemented if t.__doc__ and len(t.__doc__) > 20)
        doc_pts = min(5, (has_doc / max(len(implemented), 1)) * 5)
        points += doc_pts
        details.append(f"{'✓' if doc_pts >= 4 else '✗'} Documentation ({doc_pts:.0f}/5)")

        # Organization (5 pts)
        org_pts = 5
        for t in implemented:
            try:
                if inspect.getsource(t).count('\n') > 80:
                    org_pts -= 1
            except:
                pass
        points += max(0, org_pts)
        details.append(f"{'✓' if org_pts >= 4 else '✗'} Code organization ({org_pts:.0f}/5)")

        self.scores.code_quality = min(10, points)
        self.details["code_quality"] = details

    def _grade_mcp(self):
        """Grade MCP integration (30 points)."""
        details = []

        try:
            from agent import create_agent
            agent = create_agent()

            # Check for McpToolset in tools (10 pts)
            has_mcp = False
            for tool in agent.tools:
                tool_type = type(tool).__name__
                if "Mcp" in tool_type or "MCP" in tool_type:
                    has_mcp = True
                    break

            if has_mcp:
                self.scores.mcp_connected = 10
                details.append("✓ McpToolset configured (10/10)")

                # Check instruction mentions GitHub (15 pts)
                instr = getattr(agent, 'instruction', '') or ''
                github_keywords = ['github', 'repo', 'issue', 'pull request', 'repository']
                if any(kw in instr.lower() for kw in github_keywords):
                    self.scores.github_queries = 15
                    details.append("✓ GitHub in system instruction (15/15)")
                else:
                    self.scores.github_queries = 5  # Partial credit for having MCP
                    details.append("⚠ MCP configured but GitHub not in instruction (5/15)")

                # MCP error handling guidance (5 pts)
                if 'error' in instr.lower() or 'fail' in instr.lower():
                    self.scores.mcp_error_handling = 5
                    details.append("✓ Error handling guidance (5/5)")
                else:
                    details.append("✗ No error handling guidance (0/5)")
            else:
                details.append("✗ No McpToolset found in agent.tools (0/30)")
                details.append("  Hint: Uncomment github_toolset in agent.py")

        except Exception as e:
            details.append(f"✗ MCP grading error: {str(e)[:40]}")

        self.details["mcp"] = details

    def _grade_bonus(self):
        """Grade bonus - Tool Search Pattern (25 points)."""
        details = []
        points = 0.0

        # Check for search tool (10 pts)
        try:
            from tools.mcp_tools import mcp_tools
            has_search_tool = False
            for tool in mcp_tools:
                tool_name = getattr(tool, '__name__', '') or type(tool).__name__
                if 'search' in tool_name.lower():
                    has_search_tool = True
                    break

            if has_search_tool:
                points += 10
                details.append("✓ Tool search function implemented (10/10)")
            else:
                details.append("✗ No search tool found in mcp_tools (0/10)")
        except Exception as e:
            details.append(f"✗ Could not check mcp_tools: {str(e)[:30]}")

        # Check for defer_loading in McpToolset (10 pts)
        try:
            import inspect
            from tools.mcp_tools import mcp_tools
            source = inspect.getsource(sys.modules['tools.mcp_tools'])
            if 'defer_loading' in source and 'True' in source:
                points += 10
                details.append("✓ defer_loading=True configured (10/10)")
            else:
                details.append("✗ defer_loading not configured (0/10)")
        except Exception as e:
            details.append(f"✗ Could not check defer_loading: {str(e)[:30]}")

        # Check for create_agent_with_tool_search (5 pts)
        try:
            from agent import create_agent_with_tool_search
            agent = create_agent_with_tool_search()
            points += 5
            details.append("✓ create_agent_with_tool_search works (5/5)")
        except NotImplementedError:
            details.append("✗ create_agent_with_tool_search not implemented (0/5)")
        except Exception as e:
            details.append(f"✗ Error in create_agent_with_tool_search: {str(e)[:30]}")

        self.scores.bonus = min(25, points)
        self.details["bonus"] = details


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--option", "-o", choices=["calendar", "tasks"])
    parser.add_argument("--output", "-f", default="grade_report.json")
    parser.add_argument("--all", "-a", action="store_true")
    args = parser.parse_args()

    if args.all:
        for opt in ["calendar", "tasks"]:
            grader = Grader(opt)
            tools = grader._get_tools()
            if sum(1 for t in tools if grader._is_implemented(t)) >= 3:
                args.option = opt
                break
        if not args.option:
            print("Error: No option has 3+ implemented tools")
            sys.exit(1)

    if not args.option:
        parser.print_help()
        sys.exit(1)

    grader = Grader(args.option)
    report = grader.grade()

    Path(args.output).write_text(json.dumps(report, indent=2))

    print(f"\n{'='*45}")
    print(f"GRADE REPORT - {args.option.upper()}")
    print(f"{'='*45}")
    print(f"\nPART 1: Google Workspace (70 pts)")
    print(f"  Tool Design:        {report['scores']['tool_design']:.0f}/18")
    print(f"  Agent Instructions: {report['scores']['agent_instructions']:.0f}/14")
    print(f"  Error Handling:     {report['scores']['error_handling']:.0f}/14")
    print(f"  Functionality:      {report['scores']['functionality']:.0f}/14")
    print(f"  Code Quality:       {report['scores']['code_quality']:.0f}/10")
    print(f"  Subtotal:           {report['part1_total']:.0f}/70")
    print(f"\nPART 2: GitHub MCP (30 pts)")
    print(f"  McpToolset:         {report['scores']['mcp_connected']:.0f}/10")
    print(f"  GitHub Integration: {report['scores']['github_queries']:.0f}/15")
    print(f"  Error Handling:     {report['scores']['mcp_error_handling']:.0f}/5")
    print(f"  Subtotal:           {report['part2_total']:.0f}/30")
    print(f"\nBONUS: Tool Search Pattern (25 pts)")
    print(f"  Search Tool:        {min(10, report['scores']['bonus']):.0f}/10")
    print(f"  defer_loading:      {max(0, min(10, report['scores']['bonus'] - 10)):.0f}/10")
    print(f"  Agent Function:     {max(0, report['scores']['bonus'] - 20):.0f}/5")
    print(f"  Subtotal:           {report['scores']['bonus']:.0f}/25")
    print(f"{'='*45}")
    print(f"TOTAL:                {report['total']:.0f}/125")


if __name__ == "__main__":
    main()
