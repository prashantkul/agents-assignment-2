"""
Test cases for automated grading.
"""


def _get_calendar_func(name):
    try:
        from tools.calendar_tools import (
            list_upcoming_events, find_available_slots, create_event,
            check_conflicts, reschedule_event
        )
        return {
            "list_upcoming_events": list_upcoming_events,
            "find_available_slots": find_available_slots,
            "create_event": create_event,
            "check_conflicts": check_conflicts,
            "reschedule_event": reschedule_event,
        }.get(name)
    except ImportError:
        return None


def _get_tasks_func(name):
    try:
        from tools.tasks_tools import (
            list_task_lists, list_tasks, create_task,
            complete_task, update_task, delete_task
        )
        return {
            "list_task_lists": list_task_lists,
            "list_tasks": list_tasks,
            "create_task": create_task,
            "complete_task": complete_task,
            "update_task": update_task,
            "delete_task": delete_task,
        }.get(name)
    except ImportError:
        return None


# =============================================================================
# Calendar Tests
# =============================================================================

CALENDAR_TESTS = [
    {
        "name": "list_events_default",
        "type": "functional",
        "func": _get_calendar_func("list_upcoming_events"),
        "input": {},
        "expected_keys": ["status", "events"],
    },
    {
        "name": "list_events_week",
        "type": "functional",
        "func": _get_calendar_func("list_upcoming_events"),
        "input": {"days_ahead": 7},
        "expected_keys": ["status", "events"],
    },
    {
        "name": "create_event",
        "type": "functional",
        "func": _get_calendar_func("create_event"),
        "input": {"title": "Test", "start_time": "2024-01-20T10:00:00", "end_time": "2024-01-20T11:00:00"},
        "expected_keys": ["status"],
    },
    {
        "name": "check_conflicts",
        "type": "functional",
        "func": _get_calendar_func("check_conflicts"),
        "input": {"date": "2024-01-15"},
        "expected_keys": ["status"],
    },
    {
        "name": "find_slots",
        "type": "functional",
        "func": _get_calendar_func("find_available_slots"),
        "input": {"participants": ["alice@example.com"], "duration_minutes": 30},
        "expected_keys": ["status"],
    },
    # Validation tests
    {
        "name": "list_events_negative",
        "type": "validation",
        "func": _get_calendar_func("list_upcoming_events"),
        "invalid_input": {"days_ahead": -5},
    },
    # API error tests
    {
        "name": "list_events_api_error",
        "type": "api_error",
        "func": _get_calendar_func("list_upcoming_events"),
        "input": {},
    },
]


# =============================================================================
# Tasks Tests
# =============================================================================

TASKS_TESTS = [
    {
        "name": "list_tasks_default",
        "type": "functional",
        "func": _get_tasks_func("list_tasks"),
        "input": {},
        "expected_keys": ["status", "tasks"],
    },
    {
        "name": "list_task_lists",
        "type": "functional",
        "func": _get_tasks_func("list_task_lists"),
        "input": {},
        "expected_keys": ["status", "task_lists"],
    },
    {
        "name": "create_task",
        "type": "functional",
        "func": _get_tasks_func("create_task"),
        "input": {"title": "New task"},
        "expected_keys": ["status"],
    },
    {
        "name": "create_task_with_due",
        "type": "functional",
        "func": _get_tasks_func("create_task"),
        "input": {"title": "Task with deadline", "due_date": "2024-01-25"},
        "expected_keys": ["status"],
    },
    {
        "name": "complete_task",
        "type": "functional",
        "func": _get_tasks_func("complete_task"),
        "input": {"task_id": "task1"},
        "expected_keys": ["status"],
    },
    # Validation tests
    {
        "name": "create_task_empty_title",
        "type": "validation",
        "func": _get_tasks_func("create_task"),
        "invalid_input": {"title": ""},
    },
    # API error tests
    {
        "name": "list_tasks_api_error",
        "type": "api_error",
        "func": _get_tasks_func("list_tasks"),
        "input": {},
    },
]
