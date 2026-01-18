"""
Authentication module for OtlkGoogTools

Provides OAuth2 authentication for Microsoft services with:
- Public client support (no Azure AD registration required)
- Custom app support
- Multiple authentication methods (browser, device code, silent)
- Token persistence and automatic refresh
"""

from .graph_client import GraphClient
from .oauth_manager import OAuthManager, get_oauth_manager, reset_oauth_manager
from .public_clients import (
    MicrosoftPublicClients,
    PublicClient,
    get_public_client_for_scopes,
)
from .token_store import TokenStore


# Create OutlookAuthenticator as an alias to OAuthManager for backward compatibility
OutlookAuthenticator = OAuthManager


__all__ = [
    "GraphClient",
    "OAuthManager",
    "OutlookAuthenticator",
    "PublicClient",
    "MicrosoftPublicClients",
    "TokenStore",
    "get_oauth_manager",
    "reset_oauth_manager",
    "get_public_client_for_scopes",
]
