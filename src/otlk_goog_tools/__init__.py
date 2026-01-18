"""
OtlkGoogTools - The Ultimate Outlook & Google Toolkit MCP Server

Zero-config authentication for Microsoft Outlook and Google services.
Built for AI assistants using the Model Context Protocol (MCP).

Features:
- No Azure registration required (uses Microsoft public client applications)
- Three authentication modes: hybrid, COM, and Graph API
- Calendar and email operations
- Google Calendar integration (coming soon)
- Token persistence for seamless re-authentication

Author: lawlort32
License: MIT
Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "lawlort32"
__license__ = "MIT"

from .auth import OutlookAuthenticator, PublicClient
from .config import Config, get_config
from .models import CalendarEvent, EmailMessage, AuthMode

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "OutlookAuthenticator",
    "PublicClient",
    "Config",
    "get_config",
    "CalendarEvent",
    "EmailMessage",
    "AuthMode",
]