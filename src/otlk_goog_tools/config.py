"""
Configuration management for OtlkGoogTools

Handles application settings from environment variables and provides
a centralized configuration object.
"""

import os
from pathlib import Path
from typing import Optional
from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings


class AuthMode(str, Enum):
    """Authentication mode options."""
    HYBRID = "hybrid"
    COM = "com"
    GRAPH = "graph"


class PublicClientType(str, Enum):
    """Microsoft public client application types."""
    GRAPH_EXPLORER = "graph-explorer"
    AZURE_CLI = "azure-cli"
    OFFICE = "office"
    POWERSHELL = "powershell"
    VISUAL_STUDIO = "visual-studio"


class Config(BaseSettings):
    """Application configuration."""
    
    # Authentication Mode
    auth_mode: AuthMode = Field(
        default=AuthMode.HYBRID,
        description="Authentication mode: hybrid, com, or graph"
    )
    
    # Public Client Configuration
    use_public_client: bool = Field(
        default=True,
        description="Use Microsoft public client applications (no Azure registration required)"
    )
    
    public_client: PublicClientType = Field(
        default=PublicClientType.GRAPH_EXPLORER,
        description="Which public client to use"
    )
    
    # Custom Azure AD Configuration
    client_id: Optional[str] = Field(
        default=None,
        description="Azure AD Application (Client) ID"
    )
    
    tenant_id: str = Field(
        default="common",
        description="Azure AD Tenant ID or 'common' for multi-tenant"
    )
    
    client_secret: Optional[str] = Field(
        default=None,
        description="Client secret (only for confidential clients)"
    )
    
    redirect_uri: str = Field(
        default="http://localhost:8400",
        description="OAuth redirect URI"
    )
    
    # Microsoft Graph API Scopes
    graph_scopes: str = Field(
        default="https://graph.microsoft.com/Calendars.ReadWrite,https://graph.microsoft.com/Mail.ReadWrite,https://graph.microsoft.com/Mail.Send,https://graph.microsoft.com/User.Read,offline_access",
        description="Comma-separated list of Graph API scopes"
    )
    
    # Google Configuration
    google_credentials_file: str = Field(
        default="credentials.json",
        description="Path to Google OAuth2 credentials file"
    )
    
    google_calendar_id: str = Field(
        default="primary",
        description="Google Calendar ID to sync with"
    )
    
    # Data Storage
    portable_mode: bool = Field(
        default=False,
        description="Store data in app directory instead of user profile"
    )
    
    user_data_dir: Optional[str] = Field(
        default=None,
        description="Custom user data directory path"
    )
    
    token_file: str = Field(
        default="microsoft_tokens.json",
        description="Token file name"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    log_file: Optional[str] = Field(
        default=None,
        description="Log file path (optional)"
    )
    
    # MCP Server Configuration
    mcp_server_name: str = Field(
        default="outlook",
        description="MCP server name"
    )
    
    mcp_server_version: str = Field(
        default="0.1.0",
        description="MCP server version"
    )
    
    # Calendar Sync Settings
    sync_days_past: int = Field(
        default=7,
        description="Days to sync in the past"
    )
    
    sync_days_future: int = Field(
        default=30,
        description="Days to sync in the future"
    )
    
    sync_interval: int = Field(
        default=15,
        description="Sync interval in minutes"
    )
    
    # Advanced Settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    request_timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds"
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum retries for failed requests"
    )
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "OTLK_GOOG_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_user_data_dir(self) -> Path:
        """Get the user data directory path."""
        if self.user_data_dir:
            return Path(self.user_data_dir)
        
        if self.portable_mode:
            # Store in application directory
            return Path(__file__).parent.parent.parent / "data"
        
        # Store in user home directory
        return Path.home() / ".otlk-goog-tools"
    
    def get_token_file_path(self) -> Path:
        """Get the full path to the token file."""
        data_dir = self.get_user_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / self.token_file
    
    def get_scopes_list(self) -> list[str]:
        """Get Graph API scopes as a list."""
        return [scope.strip() for scope in self.graph_scopes.split(",")]


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload the configuration from environment."""
    global _config
    _config = Config()
    return _config
