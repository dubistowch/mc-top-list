"""HTTP client utilities."""

import aiohttp
from typing import Any, Dict, Optional

class BaseHTTPClient:
    """Base HTTP client with common functionality."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the client."""
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    @property
    def session(self) -> aiohttp.ClientSession:
        """Get the current session or create a new one."""
        if not hasattr(self, "_session") or not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    @session.setter
    def session(self, value: Optional[aiohttp.ClientSession]) -> None:
        """Set the session."""
        self._session = value
    
    async def close(self) -> None:
        """Close the session."""
        if hasattr(self, "_session") and self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    def _setup_headers(self) -> Dict[str, str]:
        """Setup default headers."""
        headers = {
            "User-Agent": "mc-top-list/1.0",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a GET request."""
        headers = self._setup_headers()
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {response_text}")
                data = await response.json()
                if not isinstance(data, (dict, list)):
                    raise Exception(f"Unexpected response format: {data}")
                return data
        except Exception as e:
            raise Exception(f"GET request failed: {str(e)}")
    
    async def post(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a POST request."""
        headers = self._setup_headers()
        
        try:
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {response_text}")
                data = await response.json()
                if not isinstance(data, (dict, list)):
                    raise Exception(f"Unexpected response format: {data}")
                return data
        except Exception as e:
            raise Exception(f"POST request failed: {str(e)}") 