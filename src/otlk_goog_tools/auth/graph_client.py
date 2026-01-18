"""
Microsoft Graph API Client

Wrapper for common Microsoft Graph API operations.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

from .oauth_manager import OAuthManager


logger = logging.getLogger(__name__)


class GraphClient:
    """Microsoft Graph API client."""
    
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, oauth_manager: OAuthManager):
        """
        Initialize the Graph API client.
        
        Args:
            oauth_manager: Authenticated OAuth manager
        """
        self.oauth_manager = oauth_manager
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to Microsoft Graph API.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (relative to base URL)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data
            
        Raises:
            Exception: If request fails
        """
        # Get access token
        access_token = self.oauth_manager.get_access_token()
        
        if not access_token:
            raise Exception("No valid access token. Please authenticate first.")
        
        # Prepare headers
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {access_token}"
        headers.setdefault("Content-Type", "application/json")
        
        # Build full URL
        url = f"{self.GRAPH_API_ENDPOINT}/{endpoint.lstrip('/')}"
        
        # Make request
        response = requests.request(method, url, headers=headers, **kwargs)
        
        # Handle errors
        if not response.ok:
            error_msg = f"Graph API request failed: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
            except Exception:
                error_msg += f" - {response.text}"
            
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Return JSON response
        if response.content:
            return response.json()
        return {}
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get the current user's profile.
        
        Returns:
            User profile data
        """
        return self._make_request("GET", "/me")
    
    def list_calendar_events(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List calendar events.
        
        Args:
            start: Start datetime in ISO format
            end: End datetime in ISO format
            max_results: Maximum number of events to return
            
        Returns:
            List of calendar events
        """
        params: Dict[str, Any] = {
            "$top": max_results,
            "$orderby": "start/dateTime"
        }
        
        if start and end:
            # Use calendarView for date range queries
            params["startDateTime"] = start
            params["endDateTime"] = end
            endpoint = "/me/calendarView"
        else:
            # Use events endpoint
            endpoint = "/me/events"
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def create_calendar_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new calendar event.
        
        Args:
            event_data: Event data in Graph API format
            
        Returns:
            Created event data
        """
        return self._make_request("POST", "/me/events", json=event_data)
    
    def update_calendar_event(
        self,
        event_id: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing calendar event.
        
        Args:
            event_id: Event ID
            event_data: Updated event data
            
        Returns:
            Updated event data
        """
        return self._make_request("PATCH", f"/me/events/{event_id}", json=event_data)
    
    def delete_calendar_event(self, event_id: str) -> None:
        """
        Delete a calendar event.
        
        Args:
            event_id: Event ID
        """
        self._make_request("DELETE", f"/me/events/{event_id}")
    
    def list_messages(
        self,
        folder: str = "inbox",
        max_results: int = 50,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List email messages.
        
        Args:
            folder: Mail folder name (inbox, sentitems, drafts, etc.)
            max_results: Maximum number of messages to return
            unread_only: Only return unread messages
            
        Returns:
            List of email messages
        """
        params: Dict[str, Any] = {
            "$top": max_results,
            "$orderby": "receivedDateTime DESC"
        }
        
        if unread_only:
            params["$filter"] = "isRead eq false"
        
        response = self._make_request(
            "GET",
            f"/me/mailFolders/{folder}/messages",
            params=params
        )
        return response.get("value", [])
    
    def send_message(self, message_data: Dict[str, Any]) -> None:
        """
        Send an email message.
        
        Args:
            message_data: Message data in Graph API format
        """
        self._make_request("POST", "/me/sendMail", json={"message": message_data})
    
    def mark_message_read(self, message_id: str, read: bool = True) -> None:
        """
        Mark a message as read or unread.
        
        Args:
            message_id: Message ID
            read: True to mark as read, False for unread
        """
        self._make_request(
            "PATCH",
            f"/me/messages/{message_id}",
            json={"isRead": read}
        )
