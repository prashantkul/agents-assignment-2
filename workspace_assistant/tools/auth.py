"""
Google API Authentication Helper
"""

from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = {
    'calendar': ['https://www.googleapis.com/auth/calendar'],
    'tasks': ['https://www.googleapis.com/auth/tasks'],
}

CREDENTIALS_DIR = Path(__file__).parent.parent / "config" / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "token.json"


def get_credentials(scopes: list[str]) -> Credentials:
    """Get valid credentials, running OAuth flow if needed."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(f"Credentials not found at {CREDENTIALS_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), scopes)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_calendar_service():
    """Get authorized Google Calendar service."""
    creds = get_credentials(SCOPES['calendar'])
    return build('calendar', 'v3', credentials=creds)


def get_tasks_service():
    """Get authorized Google Tasks service."""
    creds = get_credentials(SCOPES['tasks'])
    return build('tasks', 'v1', credentials=creds)
