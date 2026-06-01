"""
限流模块
使用令牌桶算法实现限流
"""
import time
from collections import defaultdict
from typing import Dict, Tuple

from config_center.config_manager import get_config_manager

class RateLimiter:
    """限流管理器 - 令牌桶算法"""
    
    def __init__(self):
        """
        初始化限流管理器
        """
        # 从配置中心读取配置
        self.config_manager = get_config_manager()
        self._load_config()
    
    def _load_config(self):
        """
        加载配置
        """
        # 令牌桶参数
        self.token_rate = self.config_manager.get("rate_limit.token_rate", 0.5)  # 每秒生成多少令牌
        self.max_tokens = self.config_manager.get("rate_limit.max_tokens", 30)    # 桶的最大容量
        
        # 存储每个用户/IP的令牌桶状态
        # key: user_id/ip, value: (available_tokens, last_update_time)
        self.buckets: Dict[str, Tuple[float, float]] = defaultdict(self._create_bucket)
    
    def _create_bucket(self):
        """创建新的令牌桶，初始为满"""
        return (float(self.max_tokens), time.time())
    
    def _add_tokens(self, key: str):
        """
        向令牌桶中添加令牌
        
        Args:
            key: 用户/IP的key
        """
        available_tokens, last_update_time = self.buckets[key]
        current_time = time.time()
        
        # 计算从上次更新到现在应该添加的令牌数
        time_passed = current_time - last_update_time
        tokens_to_add = time_passed * self.token_rate
        
        # 更新可用令牌数（不超过最大容量）
        available_tokens = min(float(self.max_tokens), available_tokens + tokens_to_add)
        
        # 更新令牌桶状态
        self.buckets[key] = (available_tokens, current_time)
    
    def check_rate_limit(self, ip: str, user_id: str) -> bool:
        """
        检查是否超过限流（尝试从令牌桶获取令牌）
        
        Args:
            ip: 客户端IP
            user_id: 用户ID
            
        Returns:
            bool: 是否允许请求（获取到令牌返回True，否则返回False）
        """
        # 合并IP和用户ID限流（使用更严格的限制）
        ip_key = f"ip:{ip}"
        user_key = f"user:{user_id}"
        
        # 更新两个令牌桶
        self._add_tokens(ip_key)
        self._add_tokens(user_key)
        
        # 获取当前令牌数
        ip_tokens, _ = self.buckets[ip_key]
        user_tokens, _ = self.buckets[user_key]
        
        # 如果任一令牌桶为空，拒绝请求
        if ip_tokens < 1 or user_tokens < 1:
            return False
        
        # 消耗令牌
        self.buckets[ip_key] = (ip_tokens - 1, time.time())
        self.buckets[user_key] = (user_tokens - 1, time.time())
        
        return True
    
    def get_token_count(self, ip: str, user_id: str) -> Tuple[float, float]:
        """
        获取当前令牌数
        
        Args:
            ip: 客户端IP
            user_id: 用户ID
            
        Returns:
            Tuple[float, float]: (IP令牌数, 用户令牌数)
        """
        # 更新令牌桶以获取最新令牌数
        ip_key = f"ip:{ip}"
        user_key = f"user:{user_id}"
        
        self._add_tokens(ip_key)
        self._add_tokens(user_key)
        
        ip_tokens, _ = self.buckets[ip_key]
        user_tokens, _ = self.buckets[user_key]
        
        return ip_tokens, user_tokens
    
    def reload_config(self):
        """
        重新加载配置
        """
        self._load_config()
