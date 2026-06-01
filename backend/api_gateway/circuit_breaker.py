"""
熔断模块
某个模块（如大模型）连续失败5次，就暂时不调用它，直接返回提示
"""
import time
from typing import Dict, Optional, Callable, Any
from enum import Enum

class CircuitState(Enum):
    """熔断状态"""
    CLOSED = "closed"  # 正常状态
    OPEN = "open"      # 熔断状态
    HALF_OPEN = "half_open"  # 半开状态

from config_center.config_manager import get_config_manager

class CircuitBreaker:
    """熔断管理器"""
    
    def __init__(self):
        """
        初始化熔断管理器
        """
        # 从配置中心读取配置
        self.config_manager = get_config_manager()
        self._load_config()
    
    def _load_config(self):
        """
        加载配置
        """
        self.failure_threshold = self.config_manager.get("circuit_breaker.failure_threshold", 5)
        self.recovery_time = self.config_manager.get("circuit_breaker.recovery_time", 30)
        self.timeout = self.config_manager.get("circuit_breaker.timeout", 5)
        
        # 存储每个模块的状态
        # key: module_name, value: dict with state, failure_count, last_failure_time, last_state_change_time
        self.module_states: Dict[str, Dict] = {}
    
    def execute(self, module_name: str, func: Callable, *args, **kwargs) -> Any:
        """
        执行函数，带有熔断保护
        
        Args:
            module_name: 模块名称
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Any: 函数执行结果
            
        Raises:
            Exception: 执行失败时抛出异常
        """
        # 检查模块状态
        state = self._get_module_state(module_name)
        
        # 如果是打开状态，检查是否可以尝试恢复
        if state["state"] == CircuitState.OPEN:
            if time.time() - state["last_state_change_time"] > self.recovery_time:
                # 进入半开状态
                self._update_module_state(module_name, CircuitState.HALF_OPEN)
                state["state"] = CircuitState.HALF_OPEN
            else:
                # 熔断状态，直接抛出异常
                raise Exception(f"模块 {module_name} 已熔断，请稍后再试")
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            
            # 执行成功，重置失败计数
            self._reset_module_failure(module_name)
            
            return result
        except Exception as e:
            # 执行失败，增加失败计数
            self._increment_module_failure(module_name)
            
            # 检查是否达到熔断阈值
            state = self._get_module_state(module_name)
            if state["failure_count"] >= self.failure_threshold:
                # 进入熔断状态
                self._update_module_state(module_name, CircuitState.OPEN)
            
            raise
    
    def _get_module_state(self, module_name: str) -> Dict:
        """
        获取模块状态
        
        Args:
            module_name: 模块名称
            
        Returns:
            Dict: 模块状态
        """
        if module_name not in self.module_states:
            self.module_states[module_name] = {
                "state": CircuitState.CLOSED,
                "failure_count": 0,
                "last_failure_time": 0,
                "last_state_change_time": time.time()
            }
        
        return self.module_states[module_name]
    
    def _update_module_state(self, module_name: str, state: CircuitState):
        """
        更新模块状态
        
        Args:
            module_name: 模块名称
            state: 新状态
        """
        self.module_states[module_name]["state"] = state
        self.module_states[module_name]["last_state_change_time"] = time.time()
    
    def _increment_module_failure(self, module_name: str):
        """
        增加模块失败计数
        
        Args:
            module_name: 模块名称
        """
        state = self._get_module_state(module_name)
        state["failure_count"] += 1
        state["last_failure_time"] = time.time()
    
    def _reset_module_failure(self, module_name: str):
        """
        重置模块失败计数
        
        Args:
            module_name: 模块名称
        """
        state = self._get_module_state(module_name)
        state["failure_count"] = 0
        
        # 如果是半开状态，恢复到闭合状态
        if state["state"] == CircuitState.HALF_OPEN:
            self._update_module_state(module_name, CircuitState.CLOSED)
    
    def get_module_state(self, module_name: str) -> Dict:
        """
        获取模块状态（外部调用）
        
        Args:
            module_name: 模块名称
            
        Returns:
            Dict: 模块状态
        """
        return self._get_module_state(module_name)
    
    def reload_config(self):
        """
        重新加载配置
        """
        self._load_config()
