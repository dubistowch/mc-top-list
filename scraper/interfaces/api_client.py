"""API 客戶端介面定義"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TypeVar, Generic

import aiohttp

from models.resource import Resource
from utils.logger import setup_logger

T = TypeVar('T')

class RateLimiter:
    """速率限制處理器"""
    
    def __init__(self):
        self.remaining = None
        self.reset_time = None
    
    def update(self, headers: Dict[str, str]) -> None:
        """更新速率限制信息"""
        self.remaining = headers.get('X-RateLimit-Remaining')
        self.reset_time = headers.get('X-RateLimit-Reset')

class RequestTracer:
    """請求追蹤器"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def create_config(self) -> aiohttp.TraceConfig:
        """創建請求追蹤配置"""
        config = aiohttp.TraceConfig()
        config.on_request_start.append(self._on_request_start)
        config.on_request_end.append(self._on_request_end)
        return config
    
    async def _on_request_start(self, session, trace_config_ctx, params) -> None:
        """請求開始時的追蹤處理"""
        self.logger.debug(f'開始請求: {params}')

    async def _on_request_end(self, session, trace_config_ctx, params) -> None:
        """請求結束時的追蹤處理"""
        self.logger.debug(f'請求完成: {params}')

class APIClient(ABC, Generic[T]):
    """API 客戶端基礎類"""
    
    def __init__(self):
        """初始化 API 客戶端"""
        self.logger = setup_logger()
        self.rate_limiter = RateLimiter()
        self.tracer = RequestTracer(self.logger)
        self.session = None
        self.headers = self._create_headers()
    
    def _create_headers(self) -> Dict[str, str]:
        """創建 HTTP 請求標頭"""
        return {"User-Agent": "Minecraft-Plugin-Crawler/1.0"}
    
    @abstractmethod
    def _get_base_url(self) -> str:
        """獲取 API 基礎 URL"""
        pass
    
    async def _init_session(self) -> None:
        """初始化 aiohttp session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                trace_configs=[self.tracer.create_config()]
            )
    
    async def __aenter__(self):
        """Context manager 進入點"""
        await self._init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager 退出點"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    @abstractmethod
    async def fetch_resources(self, category: str) -> List[Resource]:
        """獲取資源列表"""
        pass
    
    @abstractmethod
    async def get_project(self, project_id: str) -> Resource:
        """獲取特定專案"""
        pass
    
    @abstractmethod
    async def fetch_new_resources(self, days: int = 7) -> List[Resource]:
        """獲取最近發布的資源"""
        pass
    
    @abstractmethod
    async def fetch_popular_resources(self, days: int = 7) -> List[Resource]:
        """獲取最受歡迎的資源"""
        pass
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """執行 API 請求"""
        await self._init_session()
        url = f"{self._get_base_url()}/{endpoint.lstrip('/')}"
        
        self.logger.debug(f"API 請求: {url}")
        if params := kwargs.get('params'):
            self.logger.debug(f"請求參數: {params}")
        
        async with self.session.request(method, url, **kwargs) as response:
            self.rate_limiter.update(response.headers)
            response.raise_for_status()
            data = await response.json()
            
            self.logger.debug(f"API 響應狀態: {response.status}")
            self.logger.debug(f"API 響應數據: {data}")
            
            return data 