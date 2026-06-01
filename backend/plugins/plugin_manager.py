"""
插件管理器
"""
import importlib
from typing import Dict, Any, Optional
from .plugin_registry import plugin_registry


def call_plugin(plugin_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    统一调用插件
    
    Args:
        plugin_name: 插件名称
        params: 插件参数
        
    Returns:
        插件执行结果，包含code/msg/data字段
    """
    try:
        # 动态导入插件模块
        module_path = f"plugins.{plugin_name}"
        plugin_module = importlib.import_module(module_path)
        
        # 检查插件模块是否有execute函数
        if not hasattr(plugin_module, "execute"):
            return {
                "code": 500,
                "msg": f"插件 {plugin_name} 缺少execute函数",
                "data": None
            }
        
        # 执行插件
        result = plugin_module.execute(params)
        
        # 验证返回格式
        if isinstance(result, dict) and all(key in result for key in ["code", "msg", "data"]):
            return result
        else:
            return {
                "code": 500,
                "msg": f"插件 {plugin_name} 返回格式错误",
                "data": None
            }
    
    except ImportError:
        return {
            "code": 404,
            "msg": f"插件 {plugin_name} 不存在",
            "data": None
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": f"插件执行错误: {str(e)}",
            "data": None
        }


def get_plugin_result(intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据意图获取插件执行结果
    
    Args:
        intent: 意图关键词
        params: 插件参数
        
    Returns:
        插件执行结果
    """
    # 获取插件信息
    plugin_info = plugin_registry.get_plugin_info(intent)
    if not plugin_info:
        return {
            "code": 404,
            "msg": f"意图 {intent} 不存在",
            "data": None
        }
    
    # 验证参数
    is_valid, error_msg = plugin_registry.validate_params(intent, params)
    if not is_valid:
        return {
            "code": 400,
            "msg": error_msg,
            "data": None
        }
    
    # 调用插件
    plugin_name = plugin_info["plugin_name"]
    return call_plugin(plugin_name, params)