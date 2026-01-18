"""
Email tools for Outlook

Provides high-level email operations using Microsoft Graph API.
"""

import logging
from typing import List, Optional

from ..auth import get_oauth_manager
from ..auth.graph_client import GraphClient
from ..models import EmailMessage


logger = logging.getLogger(__name__)


class EmailTools:
    """Static methods for email operations."""
    
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
    def list_emails(
        cls,
        folder: str = "inbox",
        max_results: int = 50,
        unread_only: bool = False
    ) -> List[EmailMessage]:
        """
        List email messages.
        
        Args:
            folder: Mail folder name (inbox, sentitems, drafts, etc.)
            max_results: Maximum number of messages to return
            unread_only: Only return unread messages
            
        Returns:
            List of EmailMessage objects
        """
        client = cls._get_graph_client()
        
        # Get messages from Graph API
        messages_data = client.list_messages(
            folder=folder,
            max_results=max_results,
            unread_only=unread_only
        )
        
        # Convert to EmailMessage objects
        messages = [EmailMessage.from_graph_response(data) for data in messages_data]
        
        logger.info(f"Retrieved {len(messages)} emails from {folder}")
        return messages
    
    @classmethod
    def send_email(
        cls,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        html: bool = False
    ) -> None:
        """
        Send an email message.
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            cc: List of CC recipients
            bcc: List of BCC recipients
            html: Whether body is HTML (default is plain text)
        """
        client = cls._get_graph_client()
        
        # Build message data
        message_data = {
            "subject": subject,
            "body": {
                "contentType": "html" if html else "text",
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": email}}
                for email in to
            ]
        }
        
        # Add optional recipients
        if cc:
            message_data["ccRecipients"] = [
                {"emailAddress": {"address": email}}
                for email in cc
            ]
        
        if bcc:
            message_data["bccRecipients"] = [
                {"emailAddress": {"address": email}}
                for email in bcc
            ]
        
        # Send message
        client.send_message(message_data)
        
        logger.info(f"Sent email to {len(to)} recipients: {subject}")
    
    @classmethod
    def mark_as_read(cls, email_id: str, read: bool = True) -> None:
        """
        Mark an email as read or unread.
        
        Args:
            email_id: ID of the email message
            read: True to mark as read, False for unread
        """
        client = cls._get_graph_client()
        
        # Update message
        client.mark_message_read(email_id, read)
        
        status = "read" if read else "unread"
        logger.info(f"Marked email {email_id} as {status}")
    
    @classmethod
    def get_email(cls, email_id: str) -> EmailMessage:
        """
        Get a specific email by ID.
        
        Args:
            email_id: ID of the email message
            
        Returns:
            EmailMessage object
        """
        client = cls._get_graph_client()
        
        # Get message data using the internal _make_request method
        message_data = client._make_request("GET", f"/me/messages/{email_id}")
        
        # Convert to EmailMessage object
        message = EmailMessage.from_graph_response(message_data)
        
        logger.info(f"Retrieved email: {message.subject}")
        return message
