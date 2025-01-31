"""
Platform configuration model
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Platform:
    """
    Represents a resource platform configuration
    
    Attributes:
        name: Platform identifier (e.g., 'modrinth', 'hangar')
        batch_size: Number of items to fetch per request
        api_url: Base URL for the platform's API
    """
    name: str
    batch_size: int
    api_url: Optional[str] = None
    
    def __post_init__(self):
        """Set default API URLs based on platform name"""
        if not self.api_url:
            if self.name == "modrinth":
                self.api_url = "https://api.modrinth.com/v2"
            elif self.name == "hangar":
                self.api_url = "https://hangar.papermc.io/api/v1" 