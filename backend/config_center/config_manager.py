"""
配置中心模块
管理系统配置项，支持从数据库或配置文件中读取配置，并且支持运行时修改配置
"""
import json
import os
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from knowledge_base.models import get_db

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config/config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.db: Optional[Session] = None
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """
        加载配置
        优先从数据库加载，数据库不存在则从文件加载
        """
        # 尝试从数据库加载
        try:
            self.db = next(get_db())
            # 从数据库加载配置
            from knowledge_base.models import Config
            configs = self.db.query(Config).all()
            for config in configs:
                try:
                    # 尝试解析JSON值
                    value = json.loads(config.config_value)
                except:
                    # 如果不是JSON，直接使用字符串
                    value = config.config_value
                self.config[config.config_key] = value
        except Exception as e:
            print(f"从数据库加载配置失败: {e}")
            # 从文件加载
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                # 使用默认配置
                self.config = self._get_default_config()
                # 保存默认配置到文件
                self._save_to_file()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置
        """
        return {
            "rate_limit": {
                "token_rate": 0.5,
                "max_tokens": 30
            },
            "circuit_breaker": {
                "failure_threshold": 5,
                "recovery_time": 30,
                "timeout": 5
            },
            "security": {
                "sensitive_filter": True,
                "privacy_protection": True
            },
            "monitoring": {
                "enabled": True,
                "log_level": "INFO"
            }
        }
    
    def _save_to_file(self):
        """
        保存配置到文件
        """
        # 确保配置目录存在
        config_dir = os.path.dirname(self.config_file)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def _save_to_db(self):
        """
        保存配置到数据库
        """
        if self.db:
            try:
                from knowledge_base.models import Config
                for key, value in self.config.items():
                    # 转换为JSON字符串
                    if isinstance(value, (dict, list)):
                        value_str = json.dumps(value)
                    else:
                        value_str = str(value)
                    
                    # 查找或创建配置
                    config = self.db.query(Config).filter(Config.config_key == key).first()
                    if config:
                        config.config_value = value_str
                    else:
                        config = Config(
                            config_key=key,
                            config_value=value_str,
                            description=""
                        )
                        self.db.add(config)
                self.db.commit()
            except Exception as e:
                print(f"保存配置到数据库失败: {e}")
                self.db.rollback()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        # 支持点号分隔的嵌套键
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置项
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            bool: 是否设置成功
        """
        try:
            # 支持点号分隔的嵌套键
            keys = key.split(".")
            config = self.config
            
            # 遍历键，创建嵌套字典
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            
            # 保存配置
            self._save_to_file()
            self._save_to_db()
            
            return True
        except Exception as e:
            print(f"设置配置失败: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Any]: 所有配置
        """
        return self.config
    
    def reload(self):
        """
        重新加载配置
        """
        self.load_config()

# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> ConfigManager:
    """
    获取配置管理器实例（单例模式）
    
    Returns:
        ConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
