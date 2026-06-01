"""
插件系统初始化文件
"""
from .plugin_registry import PluginRegistry
from .plugin_manager import call_plugin

__all__ = ["PluginRegistry", "call_plugin"]