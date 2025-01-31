"""
Base transformer interface
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from ...models.resource import Resource

class BaseTransformer(ABC):
    """Base interface for resource transformers"""
    
    @abstractmethod
    def transform(self, raw_data: Dict) -> List[Resource]:
        """
        Transform raw platform data into normalized resources
        
        Args:
            raw_data: Raw data from platform API
            
        Returns:
            List of normalized Resource objects
        """
        pass 