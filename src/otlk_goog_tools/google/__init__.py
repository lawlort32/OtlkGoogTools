"""
Google integration module

Provides tools for interacting with Google services:
- Google Calendar
- Gmail (future)
- OAuth2 authentication
"""

from .auth import GoogleAuthenticator
from .calendar import GoogleCalendar
from .sync import sync_outlook_to_google


__all__ = [
    "GoogleAuthenticator",
    "GoogleCalendar",
    "sync_outlook_to_google",
]
