"""
Google OAuth2 authentication

Handles authentication with Google services using OAuth2.
"""

import logging
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


logger = logging.getLogger(__name__)


class GoogleAuthenticator:
    """Google OAuth2 authenticator."""
    
    # Scopes for Google Calendar API
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(
        self,
        credentials_file: str = "credentials.json",
        token_file: Optional[Path] = None
    ):
        """
        Initialize the Google authenticator.
        
        Args:
            credentials_file: Path to Google OAuth2 credentials file
            token_file: Path to token storage file
        """
        self.credentials_file = credentials_file
        
        if token_file is None:
            token_file = Path.home() / ".otlk-goog-tools" / "google_token.pickle"
        
        self.token_file = token_file
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.credentials: Optional[Credentials] = None
    
    def authenticate(self) -> Credentials:
        """
        Authenticate with Google and return credentials.
        
        Returns:
            Google credentials object
        """
        # Try to load existing credentials
        if self.token_file.exists():
            try:
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
                logger.info("Loaded Google credentials from cache")
            except Exception as e:
                logger.warning(f"Failed to load cached credentials: {e}")
        
        # Refresh if expired
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                logger.info("Refreshed Google credentials")
            except Exception as e:
                logger.warning(f"Failed to refresh credentials: {e}")
                self.credentials = None
        
        # Get new credentials if needed
        if not self.credentials or not self.credentials.valid:
            if not Path(self.credentials_file).exists():
                raise FileNotFoundError(
                    f"Google credentials file not found: {self.credentials_file}\n"
                    "Please download it from Google Cloud Console"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file,
                self.SCOPES
            )
            
            self.credentials = flow.run_local_server(port=0)
            logger.info("Obtained new Google credentials")
            
            # Save credentials
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.credentials, token)
        
        return self.credentials
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Get current credentials if available.
        
        Returns:
            Credentials or None
        """
        if not self.credentials or not self.credentials.valid:
            return None
        
        return self.credentials
    
    def reset(self) -> None:
        """Clear authentication data."""
        self.credentials = None
        
        if self.token_file.exists():
            self.token_file.unlink()
