# OtlkGoogTools 🚀

**The Ultimate Outlook & Google Toolkit MCP Server**

Seamlessly connect to Outlook and Google Calendar/Gmail with **ZERO configuration** required. Built as a Model Context Protocol (MCP) server for AI assistants like Claude.

## ✨ Key Feature: No Azure Registration Required!

Unlike traditional Microsoft Graph integrations, OtlkGoogTools uses Microsoft's public client applications - just like when you use Graph Explorer. Sign in with your Microsoft account and you're ready to go!

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/lawlort32/OtlkGoogTools.git
cd OtlkGoogTools

# Install the package
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Basic Usage

```python
from otlk_goog_tools.auth import get_oauth_manager
from otlk_goog_tools.outlook.calendar_tools import CalendarTools

# Authenticate (opens browser, sign in once)
oauth = get_oauth_manager(use_public_client=True)
oauth.get_authenticated()  # That's it! No Azure setup needed!

# Use calendar operations
events = CalendarTools.list_calendar_events(max_results=10)
for event in events:
    print(f"{event.start} - {event.subject}")
```

### As MCP Server (Claude Desktop)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "outlook": {
      "command": "python",
      "args": ["-m", "otlk_goog_tools.server"],
      "env": {
        "OTLK_GOOG_USE_PUBLIC_CLIENT": "true"
      }
    }
  }
}
```

Then ask Claude: "Show me my calendar for next week" or "Send an email to john@example.com"

### For Claude Web (Headless/Remote)

Use device code authentication:

```python
oauth = get_oauth_manager(use_public_client=True)
oauth.get_authenticated(method="device")
# Follow the instructions to authenticate via https://microsoft.com/devicelogin
```

## 🔐 Authentication Options

### Option 1: Public Client (Default - NO SETUP!)

```python
oauth = get_oauth_manager(use_public_client=True)
oauth.get_authenticated()
```

Available public clients:
- `graph-explorer` (default) - Full Graph API access
- `azure-cli` - Azure CLI client
- `office` - Microsoft Office client
- `powershell` - Azure PowerShell
- `visual-studio` - Visual Studio

### Option 2: Custom Azure AD App

```python
oauth = get_oauth_manager(
    use_public_client=False,
    custom_client_id="your-app-id",
    custom_tenant="your-tenant-id"
)
```

## 📅 Calendar Operations

```python
from otlk_goog_tools.outlook.calendar_tools import CalendarTools
from datetime import datetime, timedelta

# List events
events = CalendarTools.list_calendar_events(
    start_date=datetime.now().isoformat(),
    end_date=(datetime.now() + timedelta(days=7)).isoformat()
)

# Create event
event = CalendarTools.create_calendar_event(
    subject="Team Meeting",
    start=datetime(2024, 1, 20, 14, 0),
    end=datetime(2024, 1, 20, 15, 0),
    location="Conference Room A",
    attendees=["colleague@company.com"]
)

# Delete event
CalendarTools.delete_calendar_event(event.id)
```

## 📧 Email Operations

```python
from otlk_goog_tools.outlook.email_tools import EmailTools

# List emails
emails = EmailTools.list_emails(folder="inbox", unread_only=True)

# Send email
EmailTools.send_email(
    to=["recipient@example.com"],
    subject="Hello from OtlkGoogTools",
    body="This email was sent programmatically!"
)
```

## 🧪 Testing Authentication

```bash
# Test with default public client
python scripts/test_auth.py

# List available public clients
python scripts/test_auth.py --list-clients

# Test specific client with device code flow
python scripts/test_auth.py --client graph-explorer --method device
```

## 🛠️ Development

```bash
# Setup dev environment
git clone https://github.com/lawlort32/OtlkGoogTools.git
cd OtlkGoogTools
pip install -e ".[dev]"

# Run tests
pytest

# Run the MCP server directly
python -m otlk_goog_tools.server
```

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- Inspired by [OutlookGoogleCalendarSync](https://github.com/phw198/OutlookGoogleCalendarSync)
- Microsoft Graph API team
- Model Context Protocol community
