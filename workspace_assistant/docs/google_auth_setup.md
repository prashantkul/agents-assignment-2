# Google API Authentication Setup

This guide walks you through setting up OAuth credentials for Google Workspace APIs.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it (e.g., "Workspace Assistant") and click "Create"
4. Select your new project

## Step 2: Enable APIs

Enable the API for your chosen option:

**Option A - Calendar:**
- Go to APIs & Services → Library
- Search "Google Calendar API"
- Click "Enable"

**Option B - Gmail:**
- Go to APIs & Services → Library
- Search "Gmail API"
- Click "Enable"

**Option C - Sheets:**
- Go to APIs & Services → Library
- Search "Google Sheets API"
- Click "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to APIs & Services → OAuth consent screen
2. Select "External" (unless you have a Workspace org)
3. Fill in required fields:
   - App name: "Workspace Assistant"
   - User support email: your email
   - Developer contact: your email
4. Click "Save and Continue"
5. Add scopes (click "Add or Remove Scopes"):
   - Calendar: `https://www.googleapis.com/auth/calendar`
   - Gmail: `https://www.googleapis.com/auth/gmail.readonly`
   - Sheets: `https://www.googleapis.com/auth/spreadsheets.readonly`
6. Click "Save and Continue"
7. Add your email as a test user
8. Click "Save and Continue"

## Step 4: Create OAuth Credentials

1. Go to APIs & Services → Credentials
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "Workspace Assistant"
5. Click "Create"
6. Click "Download JSON"
7. Save as `config/credentials/credentials.json`

## Step 5: Test Authentication

```bash
# From workspace_assistant directory
python -c "from tools.auth import get_credentials; get_credentials(['https://www.googleapis.com/auth/calendar'])"
```

This opens a browser for OAuth. After authorizing, a `token.json` is saved.

## Troubleshooting

**"Access blocked" error:**
- Ensure you added yourself as a test user in the OAuth consent screen

**"Credentials file not found":**
- Check the JSON file is at `config/credentials/credentials.json`

**"Invalid scope":**
- Make sure you enabled the correct API and added its scope

## Security Notes

- Never commit `credentials.json` or `token.json` to git
- The `.gitignore` already excludes these files
- For production, use service accounts instead of OAuth
