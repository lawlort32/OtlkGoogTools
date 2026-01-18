"""
Data models for OtlkGoogTools

Defines data structures for calendar events, email messages, and configuration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AuthMode(str, Enum):
    """Authentication mode options."""
    
    HYBRID = "hybrid"
    COM = "com"
    GRAPH = "graph"


@dataclass
class CalendarEvent:
    """Calendar event data model."""
    
    id: str
    subject: str
    start: datetime
    end: datetime
    location: Optional[str] = None
    body: Optional[str] = None
    attendees: List[str] = field(default_factory=list)
    is_all_day: bool = False
    reminder_minutes: int = 15
    organizer: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    
    @classmethod
    def from_graph_response(cls, data: Dict[str, Any]) -> "CalendarEvent":
        """
        Parse a Graph API response into a CalendarEvent.
        
        Args:
            data: Graph API event data
            
        Returns:
            CalendarEvent instance
        """
        # Parse start and end times
        start_str = data.get("start", {}).get("dateTime", "")
        end_str = data.get("end", {}).get("dateTime", "")
        
        # Convert to datetime
        start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        
        # Parse attendees
        attendees = [
            att.get("emailAddress", {}).get("address", "")
            for att in data.get("attendees", [])
        ]
        
        # Parse organizer
        organizer = data.get("organizer", {}).get("emailAddress", {}).get("address")
        
        # Parse created and modified times
        created_str = data.get("createdDateTime")
        modified_str = data.get("lastModifiedDateTime")
        
        created = None
        modified = None
        
        if created_str:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        if modified_str:
            modified = datetime.fromisoformat(modified_str.replace("Z", "+00:00"))
        
        # Get body content
        body = data.get("body", {}).get("content", "")
        
        # Get location
        location = data.get("location", {}).get("displayName", "")
        
        # Get reminder
        reminder_minutes = 15
        if data.get("isReminderOn"):
            reminder_minutes = data.get("reminderMinutesBeforeStart", 15)
        
        return cls(
            id=data.get("id", ""),
            subject=data.get("subject", ""),
            start=start,
            end=end,
            location=location or None,
            body=body or None,
            attendees=attendees,
            is_all_day=data.get("isAllDay", False),
            reminder_minutes=reminder_minutes,
            organizer=organizer,
            created=created,
            modified=modified,
        )
    
    def to_graph_request(self) -> Dict[str, Any]:
        """
        Convert to Graph API request format.
        
        Returns:
            Dictionary in Graph API format
        """
        event_data: Dict[str, Any] = {
            "subject": self.subject,
            "start": {
                "dateTime": self.start.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": self.end.isoformat(),
                "timeZone": "UTC"
            },
            "isAllDay": self.is_all_day,
        }
        
        # Add optional fields
        if self.body:
            event_data["body"] = {
                "contentType": "text",
                "content": self.body
            }
        
        if self.location:
            event_data["location"] = {
                "displayName": self.location
            }
        
        if self.attendees:
            event_data["attendees"] = [
                {
                    "emailAddress": {"address": email},
                    "type": "required"
                }
                for email in self.attendees
            ]
        
        if self.reminder_minutes > 0:
            event_data["isReminderOn"] = True
            event_data["reminderMinutesBeforeStart"] = self.reminder_minutes
        
        return event_data


@dataclass
class EmailMessage:
    """Email message data model."""
    
    id: str
    subject: str
    sender: str
    recipients: List[str]
    body: str
    received: datetime
    is_read: bool = False
    has_attachments: bool = False
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    importance: str = "normal"
    
    @classmethod
    def from_graph_response(cls, data: Dict[str, Any]) -> "EmailMessage":
        """
        Parse a Graph API response into an EmailMessage.
        
        Args:
            data: Graph API message data
            
        Returns:
            EmailMessage instance
        """
        # Parse sender
        sender = data.get("from", {}).get("emailAddress", {}).get("address", "")
        
        # Parse recipients
        recipients = [
            r.get("emailAddress", {}).get("address", "")
            for r in data.get("toRecipients", [])
        ]
        
        # Parse CC
        cc = [
            r.get("emailAddress", {}).get("address", "")
            for r in data.get("ccRecipients", [])
        ]
        
        # Parse BCC
        bcc = [
            r.get("emailAddress", {}).get("address", "")
            for r in data.get("bccRecipients", [])
        ]
        
        # Parse received time
        received_str = data.get("receivedDateTime", "")
        received = datetime.fromisoformat(received_str.replace("Z", "+00:00"))
        
        # Get body content
        body = data.get("body", {}).get("content", "")
        
        return cls(
            id=data.get("id", ""),
            subject=data.get("subject", ""),
            sender=sender,
            recipients=recipients,
            body=body,
            received=received,
            is_read=data.get("isRead", False),
            has_attachments=data.get("hasAttachments", False),
            cc=cc,
            bcc=bcc,
            importance=data.get("importance", "normal").lower(),
        )
    
    def to_graph_request(self) -> Dict[str, Any]:
        """
        Convert to Graph API request format.
        
        Returns:
            Dictionary in Graph API format
        """
        message_data: Dict[str, Any] = {
            "subject": self.subject,
            "body": {
                "contentType": "text",
                "content": self.body
            },
            "toRecipients": [
                {"emailAddress": {"address": email}}
                for email in self.recipients
            ],
            "importance": self.importance,
        }
        
        # Add optional fields
        if self.cc:
            message_data["ccRecipients"] = [
                {"emailAddress": {"address": email}}
                for email in self.cc
            ]
        
        if self.bcc:
            message_data["bccRecipients"] = [
                {"emailAddress": {"address": email}}
                for email in self.bcc
            ]
        
        return message_data
