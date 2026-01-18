"""
Windows COM Client for Outlook

Provides access to local Outlook application via Windows COM automation.
Only available on Windows with Outlook installed.
"""

import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class OutlookCOMClient:
    """Windows COM client for local Outlook automation."""
    
    def __init__(self):
        """Initialize the COM client."""
        self.outlook = None
        self.namespace = None
        
        # Check if win32com is available
        try:
            import win32com.client
            self.win32com = win32com.client
        except ImportError:
            raise ImportError(
                "win32com not available. "
                "Install pywin32 on Windows to use COM features."
            )
    
    @classmethod
    def is_available(cls) -> bool:
        """
        Check if COM automation is available.
        
        Returns:
            True if win32com is available and we're on Windows
        """
        try:
            import win32com.client
            return True
        except ImportError:
            return False
    
    def connect(self) -> None:
        """Connect to the Outlook application."""
        if not self.outlook:
            try:
                self.outlook = self.win32com.Dispatch("Outlook.Application")
                self.namespace = self.outlook.GetNamespace("MAPI")
                logger.info("Connected to Outlook via COM")
            except Exception as e:
                logger.error(f"Failed to connect to Outlook: {e}")
                raise
    
    def get_calendar_events(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_results: int = 50
    ) -> List[Any]:
        """
        Get calendar events from Outlook.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            max_results: Maximum number of events
            
        Returns:
            List of calendar events
        """
        if not self.outlook:
            self.connect()
        
        calendar = self.namespace.GetDefaultFolder(9)  # 9 = olFolderCalendar
        items = calendar.Items
        items.Sort("[Start]")
        
        # Apply filters if provided
        if start_date and end_date:
            filter_str = f"[Start] >= '{start_date}' AND [End] <= '{end_date}'"
            items = items.Restrict(filter_str)
        
        # Limit results
        events = []
        for i, item in enumerate(items):
            if i >= max_results:
                break
            events.append(item)
        
        return events
    
    def create_event(
        self,
        subject: str,
        start: str,
        end: str,
        location: Optional[str] = None,
        body: Optional[str] = None
    ) -> Any:
        """
        Create a calendar event.
        
        Args:
            subject: Event subject
            start: Start time
            end: End time
            location: Event location
            body: Event body
            
        Returns:
            Created event object
        """
        if not self.outlook:
            self.connect()
        
        appointment = self.outlook.CreateItem(1)  # 1 = olAppointmentItem
        appointment.Subject = subject
        appointment.Start = start
        appointment.End = end
        
        if location:
            appointment.Location = location
        if body:
            appointment.Body = body
        
        appointment.Save()
        return appointment
    
    def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> None:
        """
        Send an email via Outlook.
        
        Args:
            to: Recipient email addresses
            subject: Email subject
            body: Email body
            cc: CC recipients
            bcc: BCC recipients
        """
        if not self.outlook:
            self.connect()
        
        mail = self.outlook.CreateItem(0)  # 0 = olMailItem
        mail.Subject = subject
        mail.Body = body
        mail.To = "; ".join(to)
        
        if cc:
            mail.CC = "; ".join(cc)
        if bcc:
            mail.BCC = "; ".join(bcc)
        
        mail.Send()
