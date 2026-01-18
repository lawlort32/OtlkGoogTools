"""
Google Calendar API wrapper

Provides access to Google Calendar operations.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from .auth import GoogleAuthenticator


logger = logging.getLogger(__name__)


class GoogleCalendar:
    """Google Calendar API client."""
    
    def __init__(self, authenticator: Optional[GoogleAuthenticator] = None):
        """
        Initialize the Google Calendar client.
        
        Args:
            authenticator: Google authenticator instance
        """
        if authenticator is None:
            authenticator = GoogleAuthenticator()
        
        self.authenticator = authenticator
        self.service = None
    
    def _get_service(self):
        """Get or create the Calendar API service."""
        if self.service is None:
            credentials = self.authenticator.get_credentials()
            
            if credentials is None:
                credentials = self.authenticator.authenticate()
            
            self.service = build('calendar', 'v3', credentials=credentials)
        
        return self.service
    
    def list_events(
        self,
        calendar_id: str = 'primary',
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List calendar events.
        
        Args:
            calendar_id: Calendar ID (default: 'primary')
            time_min: Lower bound for event start time (RFC3339 timestamp)
            time_max: Upper bound for event start time (RFC3339 timestamp)
            max_results: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        service = self._get_service()
        
        # Build request parameters
        params: Dict[str, Any] = {
            'calendarId': calendar_id,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        if time_min:
            params['timeMin'] = time_min
        if time_max:
            params['timeMax'] = time_max
        
        # Execute request
        events_result = service.events().list(**params).execute()
        events = events_result.get('items', [])
        
        logger.info(f"Retrieved {len(events)} events from Google Calendar")
        return events
    
    def create_event(
        self,
        event_data: Dict[str, Any],
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Create a calendar event.
        
        Args:
            event_data: Event data in Google Calendar format
            calendar_id: Calendar ID (default: 'primary')
            
        Returns:
            Created event data
        """
        service = self._get_service()
        
        event = service.events().insert(
            calendarId=calendar_id,
            body=event_data
        ).execute()
        
        logger.info(f"Created event: {event.get('summary', 'Untitled')}")
        return event
    
    def update_event(
        self,
        event_id: str,
        event_data: Dict[str, Any],
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        Update a calendar event.
        
        Args:
            event_id: Event ID
            event_data: Updated event data
            calendar_id: Calendar ID (default: 'primary')
            
        Returns:
            Updated event data
        """
        service = self._get_service()
        
        event = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_data
        ).execute()
        
        logger.info(f"Updated event: {event.get('summary', 'Untitled')}")
        return event
    
    def delete_event(
        self,
        event_id: str,
        calendar_id: str = 'primary'
    ) -> None:
        """
        Delete a calendar event.
        
        Args:
            event_id: Event ID
            calendar_id: Calendar ID (default: 'primary')
        """
        service = self._get_service()
        
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        logger.info(f"Deleted event: {event_id}")
