"""
API client factory and base client interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Type, TypeVar, ClassVar
import structlog

# Initialize structured logging
logger = structlog.get_logger(__name__)

T = TypeVar('T', bound='BaseClient')

class ClientError(Exception):
    """Base exception for client errors"""
    pass

class ClientRegistrationError(ClientError):
    """Error when registering a client fails"""
    pass

class ClientCreationError(ClientError):
    """Error when creating a client instance fails"""
    pass

class BaseClient(ABC):
    """Base interface for platform-specific API clients"""
    
    # Class variable to store platform name
    platform: ClassVar[str]
    
    @abstractmethod
    async def fetch_resources(self) -> Dict:
        """
        Fetch resources from the platform
        
        Returns:
            Dict containing fetched resources
            
        Raises:
            ClientError: If fetching resources fails
        """
        pass

class ClientFactory:
    """Factory for creating platform-specific API clients"""
    
    def __init__(self) -> None:
        """Initialize the client registry"""
        self._clients: Dict[str, Type[BaseClient]] = {}
    
    def register(self, platform: str, client_class: Type[T]) -> None:
        """
        Register a client class for a platform
        
        Args:
            platform: Platform identifier
            client_class: Client class to register
            
        Raises:
            ClientRegistrationError: If registration fails
        """
        try:
            if platform in self._clients:
                logger.warning("client_already_registered", platform=platform)
            self._clients[platform] = client_class
            logger.info("client_registered", platform=platform, client_class=client_class.__name__)
        except Exception as e:
            logger.error("client_registration_failed", platform=platform, error=str(e))
            raise ClientRegistrationError(f"Failed to register client for platform {platform}: {str(e)}")
    
    def create(self, platform: str) -> BaseClient:
        """
        Create a client instance for the specified platform
        
        Args:
            platform: Platform identifier
            
        Returns:
            Instance of the appropriate client class
            
        Raises:
            ClientCreationError: If client creation fails
        """
        try:
            if platform not in self._clients:
                logger.error("client_not_registered", platform=platform)
                raise ClientCreationError(f"No client registered for platform: {platform}")
            
            client_class = self._clients[platform]
            client = client_class()
            logger.info("client_created", platform=platform, client_class=client_class.__name__)
            return client
        except ClientCreationError:
            raise
        except Exception as e:
            logger.error("client_creation_failed", platform=platform, error=str(e))
            raise ClientCreationError(f"Failed to create client for platform {platform}: {str(e)}") 