"""
Option B: Tasks Manager Tools

Implement at least 3 tools for Google Tasks operations.
"""

from typing import Optional

# from google.adk.tools import tool
from tools.auth import get_tasks_service

# TODO: Implement your tasks tools
# Use the @tool decorator
# Each tool should return a dict with 'status' and relevant data


# @tool
def list_tasks(
    tasklist: str = "@default",
    max_results: int = 10,
    show_completed: bool = False,
) -> dict:
    """List tasks from a Google Tasks list.

    Args:
        tasklist: The task list ID. Use '@default' for the user's default list.
        max_results: Maximum number of tasks to return.
        show_completed: Whether to include completed tasks.

    Returns:
        dict with 'status' and 'tasks' keys.
    """
    try:
        service = get_tasks_service()
        results = (
            service.tasks()
            .list(
                tasklist=tasklist,
                maxResults=max_results,
                showCompleted=show_completed,
                showHidden=show_completed,  # completed tasks are hidden by default
            )
            .execute()
        )
        return {"status": "success", "tasks": results.get("items", [])}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# @tool
def create_task(
    title: str,
    notes: str = "",
    due: str = "",
    tasklist: str = "@default",
) -> dict:
    """Create a new task in a Google Tasks list.

    Args:
        title: The task title.
        notes: Optional details/description for the task.
        due: Optional due date in RFC 3339 format, e.g. '2026-07-10T00:00:00Z'.
        tasklist: The task list ID. Use '@default' for the default list.

    Returns:
        dict with 'status' and 'task' keys.
    """
    try:
        service = get_tasks_service()
        body = {"title": title}
        if notes:
            body["notes"] = notes
        if due:
            body["due"] = due
        task = service.tasks().insert(tasklist=tasklist, body=body).execute()
        return {"status": "success", "task": task}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# @tool
def complete_task(task_id: str, tasklist: str = "@default") -> dict:
    """Mark a task as completed.

    Args:
        task_id: The ID of the task to complete.
        tasklist: The task list ID. Use '@default' for the default list.

    Returns:
        dict with 'status' and 'task' keys.
    """
    try:
        service = get_tasks_service()
        task = (
            service.tasks()
            .patch(
                tasklist=tasklist,
                task=task_id,
                body={"status": "completed"},
            )
            .execute()
        )
        return {"status": "success", "task": task}
    except Exception as e:
        return {"status": "error", "message": str(e)}


tasks_tools = [list_tasks, create_task, complete_task]
