"""
Outlook module

Provides tools for interacting with Outlook via:
- Microsoft Graph API
- Windows COM automation (local Outlook)
"""

from .calendar_tools import CalendarTools
from .email_tools import EmailTools


# COM client is optional (Windows only)
try:
    from .com_client import OutlookCOMClient
    __all__ = ["CalendarTools", "EmailTools", "OutlookCOMClient"]
except ImportError:
    __all__ = ["CalendarTools", "EmailTools"]
