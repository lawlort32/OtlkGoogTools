"""
Token storage and persistence

Handles saving, loading, and validating OAuth tokens.
Supports optional encryption for enhanced security.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class TokenStore:
    """Manages OAuth token persistence to disk."""
    
    def __init__(self, file_path: Path, encrypt: bool = False):
        """
        Initialize the token store.
        
        Args:
            file_path: Path to the token file
            encrypt: Whether to encrypt tokens (not implemented yet)
        """
        self.file_path = file_path
        self.encrypt = encrypt
        
        # Ensure parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_token(self, token_data: Dict[str, Any]) -> None:
        """
        Save token data to disk.
        
        Args:
            token_data: Token information including access_token, refresh_token, expires_in
        """
        # Add timestamp for validation
        token_data["saved_at"] = time.time()
        
        with open(self.file_path, "w") as f:
            json.dump(token_data, f, indent=2)
    
    def load_token(self) -> Optional[Dict[str, Any]]:
        """
        Load token data from disk.
        
        Returns:
            Token data dictionary or None if file doesn't exist
        """
        if not self.file_path.exists():
            return None
        
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def delete_token(self) -> None:
        """Delete the token file."""
        if self.file_path.exists():
            self.file_path.unlink()
    
    def is_token_valid(self, token_data: Optional[Dict[str, Any]]) -> bool:
        """
        Check if a token is still valid based on expiration.
        
        Args:
            token_data: Token information
            
        Returns:
            True if token is valid and not expired
        """
        if not token_data:
            return False
        
        # Check if access_token exists
        if "access_token" not in token_data:
            return False
        
        # Check expiration with 5 minute buffer
        expires_in = token_data.get("expires_in", 0)
        saved_at = token_data.get("saved_at", 0)
        current_time = time.time()
        
        # Token is valid if it was saved recently and hasn't expired
        # Using 300 second (5 minute) buffer before expiration
        return (saved_at + expires_in - 300) > current_time
    
    def get_access_token(self) -> Optional[str]:
        """
        Get a valid access token from storage.
        
        Returns:
            Access token string or None if no valid token exists
        """
        token_data = self.load_token()
        
        if self.is_token_valid(token_data):
            return token_data.get("access_token")
        
        return None
