"""
MCP Server for OtlkGoogTools

This module implements the Model Context Protocol (MCP) server for Outlook and Google integration.
Provides tools for calendar and email operations that can be used by AI assistants.
"""

import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .auth import OutlookAuthenticator
from .config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OtlkGoogToolsServer:
    """MCP Server for Outlook and Google tools."""

    def __init__(self):
        """Initialize the server."""
        self.config = get_config()

        # Initialize authenticator using config settings
        self.authenticator = OutlookAuthenticator(
            use_public_client=self.config.use_public_client,
            public_client_name=(
                self.config.public_client.value if self.config.use_public_client else None
            ),
            custom_client_id=self.config.client_id,
            custom_tenant=self.config.tenant_id,
            custom_scopes=self.config.get_scopes_list(),
            token_file_path=self.config.get_token_file_path(),
            redirect_uri=self.config.redirect_uri,
        )

        self.server = Server("otlk-goog-tools")

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register all available MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools."""
            return [
                Tool(
                    name="list_calendar_events",
                    description="List calendar events from Outlook",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "Start date (ISO format)",
                            },
                            "end_date": {"type": "string", "description": "End date (ISO format)"},
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum results",
                                "default": 50,
                            },
                        },
                    },
                ),
                Tool(
                    name="create_calendar_event",
                    description="Create a new calendar event in Outlook",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "subject": {"type": "string", "description": "Event subject"},
                            "start": {"type": "string", "description": "Start time (ISO format)"},
                            "end": {"type": "string", "description": "End time (ISO format)"},
                            "body": {"type": "string", "description": "Event description"},
                            "location": {"type": "string", "description": "Event location"},
                            "attendees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Email addresses",
                            },
                        },
                        "required": ["subject", "start", "end"],
                    },
                ),
                Tool(
                    name="list_emails",
                    description="List emails from Outlook",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "folder": {
                                "type": "string",
                                "description": "Folder name",
                                "default": "inbox",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum results",
                                "default": 50,
                            },
                            "unread_only": {
                                "type": "boolean",
                                "description": "Only unread emails",
                                "default": False,
                            },
                        },
                    },
                ),
                Tool(
                    name="send_email",
                    description="Send an email via Outlook",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Recipients",
                            },
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body"},
                            "cc": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "CC recipients",
                            },
                            "bcc": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "BCC recipients",
                            },
                        },
                        "required": ["to", "subject", "body"],
                    },
                ),
                Tool(
                    name="authenticate",
                    description="Authenticate with Microsoft services. Returns device code instructions for remote/web scenarios, or initiates browser auth for desktop.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "description": "Authentication method: 'auto', 'browser', 'device', or 'silent'",
                                "default": "auto",
                                "enum": ["auto", "browser", "device", "silent"],
                            }
                        },
                    },
                ),
                Tool(
                    name="get_auth_status",
                    description="Check current authentication status and get user info if authenticated.",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "list_calendar_events":
                    result = await self._list_calendar_events(arguments)
                elif name == "create_calendar_event":
                    result = await self._create_calendar_event(arguments)
                elif name == "list_emails":
                    result = await self._list_emails(arguments)
                elif name == "send_email":
                    result = await self._send_email(arguments)
                elif name == "authenticate":
                    result = await self._authenticate(arguments)
                elif name == "get_auth_status":
                    result = await self._get_auth_status(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [TextContent(type="text", text=str(result))]

            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _list_calendar_events(self, args: dict[str, Any]) -> str:
        """List calendar events."""
        from .outlook.calendar_tools import CalendarTools

        start_date = args.get("start_date")
        end_date = args.get("end_date")
        max_results = args.get("max_results", 50)

        events = CalendarTools.list_calendar_events(
            start_date=start_date, end_date=end_date, max_results=max_results
        )

        # Format events for display
        if not events:
            return "No calendar events found."

        result = f"Found {len(events)} calendar events:\n\n"
        for event in events:
            result += f"• {event.subject}\n"
            result += f"  Start: {event.start}\n"
            result += f"  End: {event.end}\n"
            if event.location:
                result += f"  Location: {event.location}\n"
            result += "\n"

        return result

    async def _create_calendar_event(self, args: dict[str, Any]) -> str:
        """Create a calendar event."""
        from datetime import datetime

        from .outlook.calendar_tools import CalendarTools

        subject = args.get("subject")
        start = datetime.fromisoformat(args.get("start"))
        end = datetime.fromisoformat(args.get("end"))
        body = args.get("body")
        location = args.get("location")
        attendees = args.get("attendees", [])

        event = CalendarTools.create_calendar_event(
            subject=subject, start=start, end=end, body=body, location=location, attendees=attendees
        )

        return f"Successfully created event: {event.subject} (ID: {event.id})"

    async def _list_emails(self, args: dict[str, Any]) -> str:
        """List emails."""
        from .outlook.email_tools import EmailTools

        folder = args.get("folder", "inbox")
        max_results = args.get("max_results", 50)
        unread_only = args.get("unread_only", False)

        emails = EmailTools.list_emails(
            folder=folder, max_results=max_results, unread_only=unread_only
        )

        if not emails:
            return "No emails found."

        result = f"Found {len(emails)} emails:\n\n"
        for email in emails:
            status = "📬" if not email.is_read else "📭"
            result += f"{status} From: {email.sender}\n"
            result += f"   Subject: {email.subject}\n"
            result += f"   Received: {email.received}\n\n"

        return result

    async def _send_email(self, args: dict[str, Any]) -> str:
        """Send an email."""
        from .outlook.email_tools import EmailTools

        to = args.get("to", [])
        subject = args.get("subject")
        body = args.get("body")
        cc = args.get("cc", [])
        bcc = args.get("bcc", [])

        EmailTools.send_email(
            to=to, subject=subject, body=body, cc=cc if cc else None, bcc=bcc if bcc else None
        )

        return f"Successfully sent email to {', '.join(to)}: {subject}"

    async def _authenticate(self, args: dict[str, Any]) -> str:
        """Handle authentication request."""
        method = args.get("method", "auto")

        # Check if already authenticated
        if self.authenticator.get_access_token():
            return "Already authenticated! Use 'get_auth_status' to see current user info."

        # For device code, we need to capture the message
        if method == "device":
            try:
                flow = self.authenticator.app.initiate_device_flow(scopes=self.authenticator.scopes)
                if "user_code" not in flow:
                    return "Failed to initiate device code flow."

                message = flow.get("message", "")
                user_code = flow.get("user_code", "")
                verification_uri = flow.get("verification_uri", "https://microsoft.com/devicelogin")

                # Start polling in background (simplified - in production use async)
                import threading

                def poll_for_token():
                    result = self.authenticator.app.acquire_token_by_device_flow(flow)
                    if "access_token" in result:
                        self.authenticator._save_token_result(result)

                thread = threading.Thread(target=poll_for_token, daemon=True)
                thread.start()

                return f"""🔐 **Device Code Authentication**

To sign in, please:
1. Open a web browser and go to: **{verification_uri}**
2. Enter this code: **{user_code}**
3. Sign in with your Microsoft account

I'm waiting for you to complete authentication. Once done, try your request again!"""

            except Exception as e:
                return f"Authentication error: {str(e)}"

        # For browser/auto, try to authenticate
        try:
            if self.authenticator.get_authenticated(method=method):
                return "✅ Authentication successful! You can now use calendar and email tools."
            else:
                return (
                    "❌ Authentication failed. Try using method='device' for manual authentication."
                )
        except Exception as e:
            return f"Authentication error: {str(e)}. Try using method='device' for manual authentication."

    async def _get_auth_status(self, args: dict[str, Any]) -> str:
        """Get current authentication status."""
        token = self.authenticator.get_access_token()

        if not token:
            return "❌ Not authenticated. Use the 'authenticate' tool to sign in."

        # Try to get user info
        try:
            from .auth.graph_client import GraphClient

            graph_client = GraphClient(self.authenticator)
            user_profile = graph_client.get_user_profile()

            name = user_profile.get("displayName", "Unknown")
            email = user_profile.get("mail") or user_profile.get("userPrincipalName", "Unknown")

            return f"""✅ **Authenticated**

**User:** {name}
**Email:** {email}
**Client:** {self.authenticator.client_name}

You can now use calendar and email tools!"""
        except Exception as e:
            return f"✅ Authenticated (token valid), but couldn't fetch user info: {str(e)}"

    async def run(self):
        """Run the MCP server."""
        logger.info("Starting OtlkGoogTools MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)


def main():
    """Main entry point for the server."""
    server = OtlkGoogToolsServer()
    import asyncio

    asyncio.run(server.run())


if __name__ == "__main__":
    main()
