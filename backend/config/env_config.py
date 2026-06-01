"""
环境配置管理模块
从.env文件读取配置，避免硬编码敏感信息
"""
import os
from pathlib import Path
from typing import Optional


class EnvConfig:
    """环境配置类"""
    
    def __init__(self):
        """初始化配置"""
        self.base_dir = Path(__file__).parent.parent.parent
        
        # 加载.env文件
        self._load_env_file()
    
    def _load_env_file(self):
        """加载.env文件"""
        env_file = self.base_dir / ".env"
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return os.getenv(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            整数配置值
        """
        value = self.get(key)
        if value:
            try:
                return int(value)
            except ValueError:
                return default
        return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            布尔配置值
        """
        value = self.get(key)
        if value:
            return value.lower() in ('true', '1', 'yes', 'on')
        return default


# 全局配置实例
env_config = EnvConfig()


def get_env_config() -> EnvConfig:
    """获取环境配置实例
    
    Returns:
        环境配置实例
    """
    return env_config


if __name__ == "__main__":
    # 测试配置读取
    config = get_env_config()
    print(f"JWT_SECRET_KEY: {config.get('JWT_SECRET_KEY')}")
    print(f"ADMIN_PASSWORD: {config.get('ADMIN_PASSWORD')}")
    print(f"DEBUG: {config.get_bool('DEBUG')}")
