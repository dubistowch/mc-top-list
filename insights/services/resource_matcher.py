"""Resource matching service for identifying same resources across platforms"""

import re
from typing import List, Dict, Any
from difflib import SequenceMatcher

class ResourceMatcher:
    """Service for matching same resources across different platforms"""
    
    def __init__(self):
        self.name_cleaner = re.compile(r'[^\w\s-]')
    
    def _normalize_name(self, name: str) -> str:
        """Normalize resource name for comparison"""
        # 移除特殊字元，轉換為小寫
        name = self.name_cleaner.sub('', name.lower())
        # 移除多餘空白
        return ' '.join(name.split())
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two resource names"""
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def _is_same_resource(self, resource1: Dict[str, Any], resource2: Dict[str, Any]) -> bool:
        """Check if two resources are the same based on various criteria"""
        # 如果名稱完全相同，直接視為相同資源
        if self._normalize_name(resource1["name"]) == self._normalize_name(resource2["name"]):
            return True
            
        # 計算名稱相似度
        name_similarity = self._calculate_name_similarity(resource1["name"], resource2["name"])
        
        # 如果名稱相似度高且作者相同，視為相同資源
        if (name_similarity > 0.8 and 
            self._normalize_name(resource1["author"]) == self._normalize_name(resource2["author"])):
            return True
            
        return False
    
    def merge_resources(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge same resources from different platforms"""
        merged_resources = []
        processed_indices = set()
        
        for i, resource1 in enumerate(resources):
            if i in processed_indices:
                continue
                
            # 建立新的合併資源
            merged_resource = resource1.copy()
            merged_resource["platforms"] = [{
                "name": resource1["platform"],
                "downloads": resource1["downloads"],
                "website_url": resource1["website_url"]
            }]
            total_downloads = resource1["downloads"]
            
            # 尋找相同資源
            for j, resource2 in enumerate(resources[i + 1:], i + 1):
                if j in processed_indices:
                    continue
                    
                if self._is_same_resource(resource1, resource2):
                    # 合併平台資訊
                    merged_resource["platforms"].append({
                        "name": resource2["platform"],
                        "downloads": resource2["downloads"],
                        "website_url": resource2["website_url"]
                    })
                    # 累計下載次數
                    total_downloads += resource2["downloads"]
                    processed_indices.add(j)
            
            # 更新合併後的資源資訊
            merged_resource["downloads"] = total_downloads
            merged_resource.pop("platform", None)  # 移除單一平台欄位
            merged_resource.pop("website_url", None)  # 移除單一網址欄位
            
            merged_resources.append(merged_resource)
            processed_indices.add(i)
        
        return merged_resources 