"""
配置管理类
用于读取和管理阈值配置文件
"""

import json
import os

class ConfigManager:
    """配置管理类"""
    
    def __init__(self, config_path: str):
        """初始化配置管理
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 返回默认配置
            return {
                "similarity_threshold": 0.3,
                "recall_multiplier": 3,
                "top_k": 3
            }
    
    def get_similarity_threshold(self) -> float:
        """获取相似度阈值
        
        Returns:
            相似度阈值
        """
        return self.config.get("similarity_threshold", 0.3)
    
    def get_recall_multiplier(self) -> int:
        """获取召回倍数
        
        Returns:
            召回倍数
        """
        return self.config.get("recall_multiplier", 3)
    
    def get_top_k(self) -> int:
        """获取返回结果数
        
        Returns:
            返回结果数
        """
        return self.config.get("top_k", 3)
    
    def update_config(self, new_config: dict) -> bool:
        """更新配置
        
        Args:
            new_config: 新配置
            
        Returns:
            是否更新成功
        """
        try:
            self.config.update(new_config)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"更新配置失败: {e}")
            return False
    
    def reload_config(self) -> bool:
        """重新加载配置
        
        Returns:
            是否加载成功
        """
        try:
            self.config = self._load_config()
            return True
        except Exception as e:
            print(f"重新加载配置失败: {e}")
            return False

class FileSizeLimitConfig:
    """文件大小限制配置"""
    
    def __init__(self, config_path: str):
        """初始化文件大小限制配置
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载文件大小限制配置失败: {e}")
            # 返回默认配置
            return {
                "file_size": {
                    "max_file_size_mb": 100,
                    "max_text_chunk_size": 1000,
                    "split_threshold_percent": 80
                }
            }
    
    def get_max_file_size_mb(self) -> int:
        """获取单文件上传上限（MB）
        
        Returns:
            单文件上传上限
        """
        return self.config.get("file_size", {}).get("max_file_size_mb", 100)
    
    def get_max_text_chunk_size(self) -> int:
        """获取单文本块字符数上限
        
        Returns:
            单文本块字符数上限
        """
        return self.config.get("file_size", {}).get("max_text_chunk_size", 1000)
    
    def get_split_threshold_percent(self) -> int:
        """获取文件拆分阈值百分比
        
        Returns:
            文件拆分阈值百分比
        """
        return self.config.get("file_size", {}).get("split_threshold_percent", 80)
    
    def update_config(self, new_config: dict) -> bool:
        """更新配置
        
        Args:
            new_config: 新配置
            
        Returns:
            是否更新成功
        """
        try:
            self.config.update(new_config)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"更新文件大小限制配置失败: {e}")
            return False
    
    def reload_config(self) -> bool:
        """重新加载配置
        
        Returns:
            是否加载成功
        """
        try:
            self.config = self._load_config()
            return True
        except Exception as e:
            print(f"重新加载文件大小限制配置失败: {e}")
            return False

# 创建全局配置管理器实例
config_path = os.path.join(os.path.dirname(__file__), 'threshold_config.json')
config_manager = ConfigManager(config_path)

# 创建文件大小限制配置实例
file_size_limit_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'file_size_limit.json')
file_size_limit_config = FileSizeLimitConfig(file_size_limit_path)
