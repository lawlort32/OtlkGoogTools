"""
Microsoft Public Client Applications

These are well-known, Microsoft-provided client IDs that don't require registration.
Users can authenticate with Microsoft services without setting up Azure AD apps.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PublicClient:
    """Microsoft public client application configuration."""
    
    name: str
    client_id: str
    description: str
    default_scopes: List[str]
    tenant: str = "common"


class MicrosoftPublicClients:
    """
    Well-known Microsoft public client applications.
    These can be used without Azure AD registration!
    """
    
    # Microsoft Graph Explorer - Full Graph API access
    GRAPH_EXPLORER = PublicClient(
        name="Microsoft Graph Explorer",
        client_id="de8bc8b5-d9f9-48b1-a8ad-b748da725064",
        description="Official Microsoft Graph Explorer public client",
        default_scopes=[
            "https://graph.microsoft.com/Calendars.ReadWrite",
            "https://graph.microsoft.com/Mail.ReadWrite",
            "https://graph.microsoft.com/Mail.Send",
            "https://graph.microsoft.com/User.Read",
            "https://graph.microsoft.com/Files.ReadWrite.All",
            "offline_access"
        ]
    )
    
    # Azure CLI
    AZURE_CLI = PublicClient(
        name="Azure CLI",
        client_id="04b07795-8ddb-461a-bbee-02f9e1bf7b46",
        description="Azure CLI public client",
        default_scopes=[
            "https://graph.microsoft.com/.default",
            "offline_access"
        ]
    )
    
    # Microsoft Office
    MICROSOFT_OFFICE = PublicClient(
        name="Microsoft Office",
        client_id="d3590ed6-52b3-4102-aeff-aad2292ab01c",
        description="Microsoft Office public client",
        default_scopes=[
            "https://graph.microsoft.com/Calendars.ReadWrite",
            "https://graph.microsoft.com/Mail.ReadWrite",
            "https://graph.microsoft.com/User.Read",
            "offline_access"
        ]
    )
    
    # PowerShell
    POWERSHELL = PublicClient(
        name="Microsoft Azure PowerShell",
        client_id="1950a258-227b-4e31-a9cf-717495945fc2",
        description="Azure PowerShell public client",
        default_scopes=[
            "https://graph.microsoft.com/.default",
            "offline_access"
        ]
    )
    
    # Visual Studio
    VISUAL_STUDIO = PublicClient(
        name="Visual Studio",
        client_id="872cd9fa-d31f-45e0-9eab-6e460a02d1f1",
        description="Visual Studio public client",
        default_scopes=[
            "https://graph.microsoft.com/User.Read",
            "https://graph.microsoft.com/Calendars.ReadWrite",
            "offline_access"
        ]
    )
    
    @classmethod
    def get_default(cls) -> PublicClient:
        """Get the default public client (Graph Explorer)."""
        return cls.GRAPH_EXPLORER
    
    @classmethod
    def get_by_name(cls, name: str) -> PublicClient:
        """Get a public client by name."""
        clients = {
            "graph-explorer": cls.GRAPH_EXPLORER,
            "azure-cli": cls.AZURE_CLI,
            "office": cls.MICROSOFT_OFFICE,
            "powershell": cls.POWERSHELL,
            "visual-studio": cls.VISUAL_STUDIO,
        }
        return clients.get(name.lower(), cls.GRAPH_EXPLORER)
    
    @classmethod
    def list_available(cls) -> Dict[str, PublicClient]:
        """List all available public clients."""
        return {
            "graph-explorer": cls.GRAPH_EXPLORER,
            "azure-cli": cls.AZURE_CLI,
            "office": cls.MICROSOFT_OFFICE,
            "powershell": cls.POWERSHELL,
            "visual-studio": cls.VISUAL_STUDIO,
        }


def get_public_client_for_scopes(required_scopes: List[str]) -> PublicClient:
    """Intelligently select the best public client for requested scopes."""
    is_graph = any("graph.microsoft.com" in scope for scope in required_scopes)
    needs_mail = any("mail" in scope.lower() for scope in required_scopes)
    needs_calendar = any("calendar" in scope.lower() for scope in required_scopes)
    
    if is_graph and (needs_mail or needs_calendar):
        return MicrosoftPublicClients.GRAPH_EXPLORER
    elif "/.default" in str(required_scopes):
        return MicrosoftPublicClients.AZURE_CLI
    else:
        return MicrosoftPublicClients.GRAPH_EXPLORER
