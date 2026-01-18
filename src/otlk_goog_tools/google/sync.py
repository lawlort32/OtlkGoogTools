"""
Sync functionality between Outlook and Google Calendar

Provides tools to synchronize calendar events between Outlook and Google.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from ..models import CalendarEvent
from ..outlook.calendar_tools import CalendarTools
from .calendar import GoogleCalendar


logger = logging.getLogger(__name__)


def sync_outlook_to_google(
    google_calendar_id: str = 'primary',
    days_past: int = 7,
    days_future: int = 30,
    google_calendar: Optional[GoogleCalendar] = None
) -> dict:
    """
    Sync Outlook calendar events to Google Calendar.
    
    Args:
        google_calendar_id: Google Calendar ID to sync to
        days_past: Number of days in the past to sync
        days_future: Number of days in the future to sync
        google_calendar: Optional GoogleCalendar instance
        
    Returns:
        Dictionary with sync statistics
    """
    # Initialize Google Calendar client
    if google_calendar is None:
        google_calendar = GoogleCalendar()
    
    # Calculate date range
    start_date = datetime.now() - timedelta(days=days_past)
    end_date = datetime.now() + timedelta(days=days_future)
    
    # Format dates for API calls
    outlook_start = start_date.isoformat()
    outlook_end = end_date.isoformat()
    google_start = start_date.isoformat() + 'Z'  # RFC3339 format
    google_end = end_date.isoformat() + 'Z'
    
    logger.info(f"Syncing events from {outlook_start} to {outlook_end}")
    
    # Get Outlook events
    outlook_events = CalendarTools.list_calendar_events(
        start_date=outlook_start,
        end_date=outlook_end,
        max_results=250
    )
    
    # Get existing Google events
    google_events = google_calendar.list_events(
        calendar_id=google_calendar_id,
        time_min=google_start,
        time_max=google_end,
        max_results=250
    )
    
    # Build a map of Google events by subject for deduplication
    google_events_map = {
        event.get('summary', ''): event
        for event in google_events
    }
    
    # Sync statistics
    stats = {
        'outlook_events': len(outlook_events),
        'google_events': len(google_events),
        'created': 0,
        'skipped': 0,
        'errors': 0
    }
    
    # Create Google events for Outlook events that don't exist
    for outlook_event in outlook_events:
        try:
            # Check if event already exists in Google Calendar
            if outlook_event.subject in google_events_map:
                logger.debug(f"Skipping existing event: {outlook_event.subject}")
                stats['skipped'] += 1
                continue
            
            # Convert Outlook event to Google format
            google_event_data = _outlook_to_google_event(outlook_event)
            
            # Create in Google Calendar
            google_calendar.create_event(
                event_data=google_event_data,
                calendar_id=google_calendar_id
            )
            
            stats['created'] += 1
            logger.info(f"Created Google event: {outlook_event.subject}")
        
        except Exception as e:
            logger.error(f"Failed to sync event '{outlook_event.subject}': {e}")
            stats['errors'] += 1
    
    logger.info(
        f"Sync complete: {stats['created']} created, "
        f"{stats['skipped']} skipped, {stats['errors']} errors"
    )
    
    return stats


def _outlook_to_google_event(outlook_event: CalendarEvent) -> dict:
    """
    Convert an Outlook CalendarEvent to Google Calendar event format.
    
    Args:
        outlook_event: CalendarEvent from Outlook
        
    Returns:
        Dictionary in Google Calendar event format
    """
    event_data = {
        'summary': outlook_event.subject,
        'start': {
            'dateTime': outlook_event.start.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': outlook_event.end.isoformat(),
            'timeZone': 'UTC',
        },
    }
    
    # Add optional fields
    if outlook_event.location:
        event_data['location'] = outlook_event.location
    
    if outlook_event.body:
        event_data['description'] = outlook_event.body
    
    if outlook_event.attendees:
        event_data['attendees'] = [
            {'email': email}
            for email in outlook_event.attendees
        ]
    
    # Add reminders
    if outlook_event.reminder_minutes > 0:
        event_data['reminders'] = {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': outlook_event.reminder_minutes}
            ]
        }
    
    return event_data
