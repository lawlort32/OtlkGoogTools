#!/usr/bin/env python3
"""
Quick Start Example for OtlkGoogTools

Demonstrates zero-config authentication and basic operations:
1. Authentication with public client (no Azure setup needed)
2. Reading calendar events
3. Checking inbox
4. Creating and deleting a test event
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from otlk_goog_tools.auth import get_oauth_manager
from otlk_goog_tools.outlook.calendar_tools import CalendarTools
from otlk_goog_tools.outlook.email_tools import EmailTools


def main():
    """Main example function."""
    print("=" * 70)
    print("OtlkGoogTools Quick Start Example")
    print("=" * 70)
    print()
    
    # Step 1: Zero-config authentication with public client
    print("Step 1: Authenticating with Microsoft Graph API...")
    print("-" * 70)
    print("Using Microsoft Graph Explorer public client (no Azure setup needed!)")
    print()
    
    try:
        oauth_manager = get_oauth_manager(
            use_public_client=True,
            public_client_name="graph-explorer"
        )
        
        # Authenticate (will open browser if needed)
        if oauth_manager.get_authenticated(method="auto"):
            print("✓ Authentication successful!")
            print()
        else:
            print("✗ Authentication failed")
            sys.exit(1)
    
    except Exception as e:
        print(f"✗ Error during authentication: {e}")
        sys.exit(1)
    
    # Step 2: Read calendar events
    print("Step 2: Reading calendar events...")
    print("-" * 70)
    
    try:
        # Get events for the next 7 days
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        events = CalendarTools.list_calendar_events(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            max_results=10
        )
        
        print(f"Found {len(events)} upcoming events:")
        print()
        
        for i, event in enumerate(events[:5], 1):  # Show first 5
            print(f"{i}. {event.subject}")
            print(f"   Start: {event.start}")
            print(f"   End: {event.end}")
            if event.location:
                print(f"   Location: {event.location}")
            print()
        
        if len(events) > 5:
            print(f"... and {len(events) - 5} more events")
            print()
    
    except Exception as e:
        print(f"✗ Error reading calendar: {e}")
        print()
    
    # Step 3: Check inbox
    print("Step 3: Checking inbox...")
    print("-" * 70)
    
    try:
        messages = EmailTools.list_emails(
            folder="inbox",
            max_results=5,
            unread_only=False
        )
        
        print(f"Found {len(messages)} recent messages:")
        print()
        
        for i, msg in enumerate(messages, 1):
            status = "📧" if msg.is_read else "📬"
            print(f"{i}. {status} {msg.subject}")
            print(f"   From: {msg.sender}")
            print(f"   Received: {msg.received}")
            print()
    
    except Exception as e:
        print(f"✗ Error reading emails: {e}")
        print()
    
    # Step 4: Create and delete a test event
    print("Step 4: Creating and deleting a test event...")
    print("-" * 70)
    
    try:
        # Create a test event for tomorrow
        start_time = datetime.now() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        print("Creating test event...")
        event = CalendarTools.create_calendar_event(
            subject="OtlkGoogTools Test Event",
            start=start_time,
            end=end_time,
            location="Virtual",
            body="This is a test event created by OtlkGoogTools quick start example.",
            reminder_minutes=15
        )
        
        print(f"✓ Created event: {event.subject}")
        print(f"  Event ID: {event.id}")
        print(f"  Start: {event.start}")
        print()
        
        # Delete the test event
        print("Deleting test event...")
        CalendarTools.delete_calendar_event(event.id)
        print("✓ Test event deleted")
        print()
    
    except Exception as e:
        print(f"✗ Error with calendar operations: {e}")
        print()
    
    # Done!
    print("=" * 70)
    print("Quick start example completed successfully!")
    print("=" * 70)
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Zero-config authentication (no Azure AD registration needed)")
    print("  ✓ Reading calendar events")
    print("  ✓ Checking emails")
    print("  ✓ Creating and managing calendar events")
    print()
    print("Next steps:")
    print("  - Explore the full API in the documentation")
    print("  - Try the Google Calendar sync features")
    print("  - Use the MCP server for AI assistant integration")
    print()


if __name__ == "__main__":
    main()
