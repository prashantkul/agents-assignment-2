"""
Mock implementations for Google APIs.

These mocks allow grading without real API credentials.
"""

from unittest.mock import MagicMock, patch


# =============================================================================
# Mock Data
# =============================================================================

MOCK_CALENDAR_EVENTS = [
    {
        "id": "event1",
        "summary": "Team Standup",
        "start": {"dateTime": "2024-01-15T09:00:00-08:00"},
        "end": {"dateTime": "2024-01-15T09:30:00-08:00"},
        "attendees": [{"email": "alice@example.com"}],
    },
    {
        "id": "event2",
        "summary": "Project Review",
        "start": {"dateTime": "2024-01-15T14:00:00-08:00"},
        "end": {"dateTime": "2024-01-15T15:00:00-08:00"},
    },
]

MOCK_TASK_LISTS = [
    {"id": "list1", "title": "My Tasks"},
    {"id": "list2", "title": "Work"},
]

MOCK_TASKS = [
    {
        "id": "task1",
        "title": "Review proposal",
        "notes": "Check budget section",
        "due": "2024-01-20T00:00:00Z",
        "status": "needsAction",
    },
    {
        "id": "task2",
        "title": "Send report",
        "status": "needsAction",
    },
    {
        "id": "task3",
        "title": "Old task",
        "status": "completed",
    },
]


# =============================================================================
# Mock Services
# =============================================================================

class MockCalendarService:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def events(self):
        return MockCalendarEvents(self.should_fail)

    def freebusy(self):
        return MockFreeBusy()


class MockCalendarEvents:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def list(self, **kwargs):
        return MockRequest({"items": MOCK_CALENDAR_EVENTS}, self.should_fail)

    def insert(self, **kwargs):
        return MockRequest({"id": "new_event"}, self.should_fail)

    def patch(self, **kwargs):
        return MockRequest({"id": kwargs.get("eventId")}, self.should_fail)

    def get(self, **kwargs):
        return MockRequest(MOCK_CALENDAR_EVENTS[0], self.should_fail)


class MockFreeBusy:
    def query(self, **kwargs):
        return MockRequest({"calendars": {}})


class MockTasksService:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def tasklists(self):
        return MockTaskLists(self.should_fail)

    def tasks(self):
        return MockTasks(self.should_fail)


class MockTaskLists:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def list(self, **kwargs):
        return MockRequest({"items": MOCK_TASK_LISTS}, self.should_fail)


class MockTasks:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def list(self, **kwargs):
        show_completed = kwargs.get("showCompleted", False)
        tasks = MOCK_TASKS if show_completed else [t for t in MOCK_TASKS if t["status"] != "completed"]
        return MockRequest({"items": tasks}, self.should_fail)

    def insert(self, **kwargs):
        return MockRequest({"id": "new_task"}, self.should_fail)

    def patch(self, **kwargs):
        return MockRequest({"id": kwargs.get("task")}, self.should_fail)

    def delete(self, **kwargs):
        return MockRequest({}, self.should_fail)


class MockRequest:
    def __init__(self, data, should_fail=False):
        self.data = data
        self.should_fail = should_fail

    def execute(self):
        if self.should_fail:
            from googleapiclient.errors import HttpError
            resp = MagicMock()
            resp.status = 500
            raise HttpError(resp, b"Mock API Error")
        return self.data


# =============================================================================
# Setup
# =============================================================================

_patches = []


def setup_mocks(option: str, should_fail: bool = False):
    """Set up mocks for grading."""
    global _patches
    teardown_mocks()

    if option == "calendar":
        p = patch('tools.auth.get_calendar_service', return_value=MockCalendarService(should_fail))
    elif option == "tasks":
        p = patch('tools.auth.get_tasks_service', return_value=MockTasksService(should_fail))
    else:
        return

    _patches.append(p)
    p.start()


def teardown_mocks():
    global _patches
    for p in _patches:
        p.stop()
    _patches = []
