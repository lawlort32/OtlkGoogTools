#!/usr/bin/env python3
"""
Authentication test script

Tests authentication with Microsoft services using various backends and methods.
"""

import argparse
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from otlk_goog_tools.auth import (
    get_oauth_manager,
    reset_oauth_manager,
    MicrosoftPublicClients,
)
from otlk_goog_tools.auth.graph_client import GraphClient
from otlk_goog_tools.outlook.com_client import OutlookCOMClient


def test_public_client(client_name: str, method: str) -> bool:
    """Test authentication with a public client."""
    print(f"\n{'='*60}")
    print(f"Testing Public Client: {client_name}")
    print(f"Method: {method}")
    print(f"{'='*60}\n")
    
    try:
        # Get OAuth manager
        oauth_manager = get_oauth_manager(
            use_public_client=True,
            public_client_name=client_name
        )
        
        print(f"Using client: {oauth_manager.client_name}")
        print(f"Client ID: {oauth_manager.client_id}")
        print(f"Scopes: {', '.join(oauth_manager.scopes)}\n")
        
        # Authenticate
        print("Authenticating...")
        if oauth_manager.get_authenticated(method=method):
            print("✓ Authentication successful!\n")
            
            # Get access token
            token = oauth_manager.get_access_token()
            if token:
                print(f"✓ Access token obtained (length: {len(token)})\n")
                
                # Test Graph API
                print("Testing Graph API...")
                graph_client = GraphClient(oauth_manager)
                
                try:
                    user_profile = graph_client.get_user_profile()
                    print("✓ Successfully called Graph API!\n")
                    print("User Profile:")
                    print(f"  Name: {user_profile.get('displayName', 'N/A')}")
                    print(f"  Email: {user_profile.get('mail') or user_profile.get('userPrincipalName', 'N/A')}")
                    print(f"  Job Title: {user_profile.get('jobTitle', 'N/A')}")
                    print()
                    
                    return True
                except Exception as e:
                    print(f"✗ Graph API call failed: {e}\n")
                    return False
            else:
                print("✗ Failed to get access token\n")
                return False
        else:
            print("✗ Authentication failed\n")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False
    
    finally:
        # Reset for next test
        reset_oauth_manager()


def test_com_client() -> bool:
    """Test Windows COM client."""
    print(f"\n{'='*60}")
    print("Testing Windows COM Client")
    print(f"{'='*60}\n")
    
    if not OutlookCOMClient.is_available():
        print("✗ COM client not available (Windows + pywin32 required)\n")
        return False
    
    try:
        com_client = OutlookCOMClient()
        com_client.connect()
        print("✓ Successfully connected to Outlook via COM!\n")
        return True
    
    except Exception as e:
        print(f"✗ COM connection failed: {e}\n")
        return False


def list_public_clients() -> None:
    """List all available public clients."""
    print("\nAvailable Microsoft Public Clients:")
    print("=" * 60)
    
    clients = MicrosoftPublicClients.list_available()
    
    for key, client in clients.items():
        print(f"\n{key}:")
        print(f"  Name: {client.name}")
        print(f"  Client ID: {client.client_id}")
        print(f"  Description: {client.description}")
        print(f"  Default Scopes:")
        for scope in client.default_scopes:
            print(f"    - {scope}")
    
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test authentication for OtlkGoogTools"
    )
    
    parser.add_argument(
        "--backend",
        choices=["public", "com", "all"],
        default="public",
        help="Authentication backend to test"
    )
    
    parser.add_argument(
        "--client",
        choices=[
            "graph-explorer",
            "azure-cli",
            "office",
            "powershell",
            "visual-studio"
        ],
        default="graph-explorer",
        help="Public client to use"
    )
    
    parser.add_argument(
        "--method",
        choices=["auto", "browser", "device", "silent"],
        default="auto",
        help="Authentication method"
    )
    
    parser.add_argument(
        "--list-clients",
        action="store_true",
        help="List available public clients and exit"
    )
    
    args = parser.parse_args()
    
    # Handle list clients
    if args.list_clients:
        list_public_clients()
        return
    
    # Run tests
    results = {}
    
    if args.backend in ("public", "all"):
        results["public"] = test_public_client(args.client, args.method)
    
    if args.backend in ("com", "all"):
        results["com"] = test_com_client()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for backend, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{backend.upper()}: {status}")
    
    print()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
