"""
Calendar tools for Outlook

Provides high-level calendar operations using Microsoft Graph API.
"""

import logging
from datetime import datetime
from typing import List, Optional

from ..auth import get_oauth_manager
from ..auth.graph_client import GraphClient
from ..models import CalendarEvent


logger = logging.getLogger(__name__)


class CalendarTools:
    """Static methods for calendar operations."""
    
    _graph_client: Optional[GraphClient] = None
    
    @classmethod
    def _get_graph_client(cls) -> GraphClient:
        """Get or create the Graph API client."""
        if cls._graph_client is None:
            oauth_manager = get_oauth_manager()
            
            # Ensure authenticated
            if not oauth_manager.get_access_token():
                if not oauth_manager.get_authenticated():
                    raise Exception("Authentication required. Please authenticate first.")
            
            cls._graph_client = GraphClient(oauth_manager)
        
        return cls._graph_client
    
    @classmethod
    def list_calendar_events(
        cls,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_results: int = 50
    ) -> List[CalendarEvent]:
        """
        List calendar events.
        
        Args:
            start_date: Start date in ISO format (e.g., "2024-01-01T00:00:00")
            end_date: End date in ISO format
            max_results: Maximum number of events to return
            
        Returns:
            List of CalendarEvent objects
        """
        client = cls._get_graph_client()
        
        # Get events from Graph API
        events_data = client.list_calendar_events(
            start=start_date,
            end=end_date,
            max_results=max_results
        )
        
        # Convert to CalendarEvent objects
        events = [CalendarEvent.from_graph_response(data) for data in events_data]
        
        logger.info(f"Retrieved {len(events)} calendar events")
        return events
    
    @classmethod
    def create_calendar_event(
        cls,
        subject: str,
        start: datetime,
        end: datetime,
        location: Optional[str] = None,
        body: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        reminder_minutes: int = 15
    ) -> CalendarEvent:
        """
        Create a new calendar event.
        
        Args:
            subject: Event subject/title
            start: Start datetime
            end: End datetime
            location: Event location
            body: Event description
            attendees: List of attendee email addresses
            reminder_minutes: Reminder time in minutes before event
            
        Returns:
            Created CalendarEvent object
        """
        client = cls._get_graph_client()
        
        # Create event object
        event = CalendarEvent(
            id="",  # Will be assigned by server
            subject=subject,
            start=start,
            end=end,
            location=location,
            body=body,
            attendees=attendees or [],
            reminder_minutes=reminder_minutes
        )
        
        # Convert to Graph API format
        event_data = event.to_graph_request()
        
        # Create event
        result = client.create_calendar_event(event_data)
        
        # Parse response
        created_event = CalendarEvent.from_graph_response(result)
        
        logger.info(f"Created calendar event: {created_event.subject}")
        return created_event
    
    @classmethod
    def update_calendar_event(
        cls,
        event_id: str,
        subject: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        location: Optional[str] = None,
        body: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        reminder_minutes: Optional[int] = None
    ) -> CalendarEvent:
        """
        Update an existing calendar event.
        
        Args:
            event_id: ID of the event to update
            subject: Updated subject
            start: Updated start datetime
            end: Updated end datetime
            location: Updated location
            body: Updated description
            attendees: Updated attendee list
            reminder_minutes: Updated reminder time
            
        Returns:
            Updated CalendarEvent object
        """
        client = cls._get_graph_client()
        
        # Build update data
        update_data = {}
        
        if subject is not None:
            update_data["subject"] = subject
        
        if start is not None and end is not None:
            update_data["start"] = {
                "dateTime": start.isoformat(),
                "timeZone": "UTC"
            }
            update_data["end"] = {
                "dateTime": end.isoformat(),
                "timeZone": "UTC"
            }
        
        if location is not None:
            update_data["location"] = {"displayName": location}
        
        if body is not None:
            update_data["body"] = {"contentType": "text", "content": body}
        
        if attendees is not None:
            update_data["attendees"] = [
                {"emailAddress": {"address": email}, "type": "required"}
                for email in attendees
            ]
        
        if reminder_minutes is not None:
            update_data["isReminderOn"] = reminder_minutes > 0
            update_data["reminderMinutesBeforeStart"] = reminder_minutes
        
        # Update event
        result = client.update_calendar_event(event_id, update_data)
        
        # Parse response
        updated_event = CalendarEvent.from_graph_response(result)
        
        logger.info(f"Updated calendar event: {updated_event.subject}")
        return updated_event
    
    @classmethod
    def delete_calendar_event(cls, event_id: str) -> None:
        """
        Delete a calendar event.
        
        Args:
            event_id: ID of the event to delete
        """
        client = cls._get_graph_client()
        
        # Delete event
        client.delete_calendar_event(event_id)
        
        logger.info(f"Deleted calendar event: {event_id}")
