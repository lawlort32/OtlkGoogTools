"""
OAuth2 Manager using Microsoft MSAL

Handles authentication with Microsoft services using:
- Public client mode (no Azure AD registration required)
- Custom app mode (for organizations with their own Azure AD apps)
- Browser-based authentication with local callback server
- Device code flow for headless/remote scenarios
- Automatic token refresh
"""

import logging
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import parse_qs, urlparse

import msal

from .public_clients import MicrosoftPublicClients, PublicClient
from .token_store import TokenStore


logger = logging.getLogger(__name__)


class AuthCodeReceiver(BaseHTTPRequestHandler):
    """HTTP server handler for OAuth redirect callback."""
    
    auth_code: Optional[str] = None
    error: Optional[str] = None
    
    def do_GET(self) -> None:
        """Handle GET request from OAuth redirect."""
        # Parse the query parameters
        query_components = parse_qs(urlparse(self.path).query)
        
        if "code" in query_components:
            AuthCodeReceiver.auth_code = query_components["code"][0]
            self._send_success_page()
        elif "error" in query_components:
            AuthCodeReceiver.error = query_components["error"][0]
            self._send_error_page()
        else:
            self._send_error_page()
    
    def _send_success_page(self) -> None:
        """Send success HTML page."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Successful</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .success { color: #4CAF50; font-size: 24px; margin: 20px; }
                .message { color: #666; margin: 20px; }
            </style>
        </head>
        <body>
            <div class="success">✓ Authentication Successful!</div>
            <div class="message">You can close this window and return to your application.</div>
        </body>
        </html>
        """
        self._send_response(200, html)
    
    def _send_error_page(self) -> None:
        """Send error HTML page."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Failed</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: #f44336; font-size: 24px; margin: 20px; }
                .message { color: #666; margin: 20px; }
            </style>
        </head>
        <body>
            <div class="error">✗ Authentication Failed</div>
            <div class="message">Please try again or contact support.</div>
        </body>
        </html>
        """
        self._send_response(400, html)
    
    def _send_response(self, status_code: int, html: str) -> None:
        """Send HTTP response."""
        self.send_response(status_code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format: str, *args: Any) -> None:
        """Suppress server logs."""
        pass


class OAuthManager:
    """Manages OAuth2 authentication for Microsoft services."""
    
    def __init__(
        self,
        use_public_client: bool = True,
        public_client_name: Optional[str] = None,
        custom_client_id: Optional[str] = None,
        custom_tenant: str = "common",
        custom_scopes: Optional[List[str]] = None,
        token_file_path: Optional[Path] = None,
        redirect_uri: str = "http://localhost:8400"
    ):
        """
        Initialize the OAuth manager.
        
        Args:
            use_public_client: Use Microsoft public client (no registration needed)
            public_client_name: Name of public client to use (e.g., "graph-explorer")
            custom_client_id: Custom Azure AD app client ID
            custom_tenant: Tenant ID for custom app
            custom_scopes: Custom scopes to request
            token_file_path: Path to token storage file
            redirect_uri: OAuth redirect URI
        """
        self.use_public_client = use_public_client
        self.redirect_uri = redirect_uri
        
        # Configure client and scopes
        if use_public_client:
            public_client = MicrosoftPublicClients.get_by_name(
                public_client_name or "graph-explorer"
            )
            self.client_id = public_client.client_id
            self.tenant = public_client.tenant
            self.scopes = custom_scopes or public_client.default_scopes
            self.client_name = public_client.name
        else:
            if not custom_client_id:
                raise ValueError("custom_client_id required when use_public_client=False")
            self.client_id = custom_client_id
            self.tenant = custom_tenant
            self.scopes = custom_scopes or [
                "https://graph.microsoft.com/User.Read",
                "offline_access"
            ]
            self.client_name = "Custom App"
        
        # Create MSAL app
        authority = f"https://login.microsoftonline.com/{self.tenant}"
        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=authority
        )
        
        # Setup token storage
        if token_file_path is None:
            token_file_path = Path.home() / ".otlk-goog-tools" / "microsoft_tokens.json"
        self.token_store = TokenStore(token_file_path)
        
        self._access_token: Optional[str] = None
        self._token_data: Optional[Dict[str, Any]] = None
    
    def get_authenticated(self, method: str = "auto") -> bool:
        """
        Authenticate with Microsoft services.
        
        Args:
            method: Authentication method - "auto", "browser", "device", or "silent"
            
        Returns:
            True if authentication successful
        """
        # Try silent authentication first
        if method in ("auto", "silent"):
            if self._authenticate_silent():
                logger.info("Silent authentication successful")
                return True
        
        # If silent fails and only silent requested, return False
        if method == "silent":
            return False
        
        # Try browser authentication
        if method in ("auto", "browser"):
            try:
                if self._authenticate_browser():
                    logger.info("Browser authentication successful")
                    return True
            except Exception as e:
                logger.warning(f"Browser authentication failed: {e}")
                if method == "browser":
                    raise
        
        # Try device code flow
        if method in ("auto", "device"):
            if self._authenticate_device_code():
                logger.info("Device code authentication successful")
                return True
        
        return False
    
    def _authenticate_silent(self) -> bool:
        """Attempt silent authentication using cached tokens."""
        # Try to load from token store
        token_data = self.token_store.load_token()
        
        if token_data and self.token_store.is_token_valid(token_data):
            self._token_data = token_data
            self._access_token = token_data["access_token"]
            logger.info("Using cached token")
            return True
        
        # Try to get accounts from cache
        accounts = self.app.get_accounts()
        
        if accounts:
            # Try to acquire token silently
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
            
            if result and "access_token" in result:
                self._save_token_result(result)
                return True
        
        return False
    
    def _authenticate_browser(self) -> bool:
        """Authenticate using browser with local callback server."""
        # Start local server for OAuth callback
        server = HTTPServer(("localhost", 8400), AuthCodeReceiver)
        
        # Get authorization URL
        flow = self.app.initiate_auth_code_flow(
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        if "auth_uri" not in flow:
            raise Exception("Failed to create authorization URL")
        
        auth_url = flow["auth_uri"]
        logger.info(f"Opening browser for authentication: {auth_url}")
        
        # Open browser
        webbrowser.open(auth_url)
        
        # Wait for callback (with timeout)
        server.timeout = 300  # 5 minutes
        server.handle_request()
        
        # Check if we got the auth code
        if not AuthCodeReceiver.auth_code:
            error = AuthCodeReceiver.error or "No authorization code received"
            raise Exception(f"Authentication failed: {error}")
        
        # Exchange code for token
        result = self.app.acquire_token_by_auth_code_flow(
            auth_code_flow=flow,
            auth_response={"code": AuthCodeReceiver.auth_code}
        )
        
        # Reset the auth code for next use
        AuthCodeReceiver.auth_code = None
        AuthCodeReceiver.error = None
        
        if "access_token" in result:
            self._save_token_result(result)
            return True
        
        raise Exception(f"Token acquisition failed: {result.get('error_description', 'Unknown error')}")
    
    def _authenticate_device_code(self) -> bool:
        """Authenticate using device code flow (for headless/SSH scenarios)."""
        flow = self.app.initiate_device_flow(scopes=self.scopes)
        
        if "user_code" not in flow:
            raise Exception("Failed to create device flow")
        
        # Display device code message
        print("\n" + "=" * 60)
        print(flow["message"])
        print("=" * 60 + "\n")
        
        # Poll for token
        result = self.app.acquire_token_by_device_flow(flow)
        
        if "access_token" in result:
            self._save_token_result(result)
            return True
        
        raise Exception(f"Device code authentication failed: {result.get('error_description', 'Unknown error')}")
    
    def _save_token_result(self, result: Dict[str, Any]) -> None:
        """Save token result to cache and storage."""
        self._token_data = result
        self._access_token = result["access_token"]
        self.token_store.save_token(result)
    
    def _refresh_token(self) -> bool:
        """Refresh the access token using refresh token."""
        if not self._token_data or "refresh_token" not in self._token_data:
            return False
        
        # Try silent token acquisition first
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
            if result and "access_token" in result:
                self._save_token_result(result)
                return True
        
        return False
    
    def get_access_token(self) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token or None
        """
        # Check if current token is valid
        if self._token_data and self.token_store.is_token_valid(self._token_data):
            return self._access_token
        
        # Try to refresh
        if self._refresh_token():
            return self._access_token
        
        # Need new authentication
        return None
    
    def reset(self) -> None:
        """Clear all authentication data."""
        self._access_token = None
        self._token_data = None
        self.token_store.delete_token()
        
        # Remove accounts from cache
        accounts = self.app.get_accounts()
        for account in accounts:
            self.app.remove_account(account)


# Global OAuth manager instance
_oauth_manager: Optional[OAuthManager] = None


def get_oauth_manager(
    use_public_client: bool = True,
    public_client_name: Optional[str] = None,
    **kwargs: Any
) -> OAuthManager:
    """
    Get or create the global OAuth manager instance.
    
    Args:
        use_public_client: Use Microsoft public client
        public_client_name: Name of public client to use
        **kwargs: Additional arguments for OAuthManager
        
    Returns:
        OAuthManager instance
    """
    global _oauth_manager
    
    if _oauth_manager is None:
        _oauth_manager = OAuthManager(
            use_public_client=use_public_client,
            public_client_name=public_client_name,
            **kwargs
        )
    
    return _oauth_manager


def reset_oauth_manager() -> None:
    """Reset the global OAuth manager instance."""
    global _oauth_manager
    
    if _oauth_manager:
        _oauth_manager.reset()
        _oauth_manager = None
