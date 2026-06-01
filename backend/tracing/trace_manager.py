"""
链路追踪模块
记录用户请求的完整执行过程，包括每一步的耗时和状态
"""
import uuid
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

class TraceSpan:
    """链路追踪的一个节点"""
    
    def __init__(self, service: str, operation: str, start_time: float = None):
        """
        初始化一个追踪节点
        
        Args:
            service: 服务名称
            operation: 操作名称
            start_time: 开始时间（秒）
        """
        self.service = service
        self.operation = operation
        self.start_time = start_time or time.time()
        self.end_time = None
        self.status = "running"
        self.error = None
        self.attributes: Dict[str, Any] = {}
    
    def finish(self, status: str = "success", error: str = None):
        """
        结束一个追踪节点
        
        Args:
            status: 状态（success/failure）
            error: 错误信息
        """
        self.end_time = time.time()
        self.status = status
        self.error = error
    
    def get_duration(self) -> float:
        """
        获取节点执行时间（毫秒）
        
        Returns:
            float: 执行时间（毫秒）
        """
        if self.end_time is None:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 节点信息
        """
        return {
            "service": self.service,
            "operation": self.operation,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "duration": self.get_duration(),
            "status": self.status,
            "error": self.error,
            "attributes": self.attributes
        }

class Trace:
    """一次完整的链路追踪"""
    
    def __init__(self, trace_id: str = None):
        """
        初始化一个链路追踪
        
        Args:
            trace_id: 追踪ID
        """
        self.trace_id = trace_id or str(uuid.uuid4())
        self.start_time = time.time()
        self.end_time = None
        self.spans: List[TraceSpan] = []
        self.attributes: Dict[str, Any] = {}
    
    def add_span(self, service: str, operation: str) -> TraceSpan:
        """
        添加一个追踪节点
        
        Args:
            service: 服务名称
            operation: 操作名称
            
        Returns:
            TraceSpan: 追踪节点
        """
        span = TraceSpan(service, operation)
        self.spans.append(span)
        return span
    
    def finish(self):
        """
        结束链路追踪
        """
        self.end_time = time.time()
    
    def get_duration(self) -> float:
        """
        获取整个链路执行时间（毫秒）
        
        Returns:
            float: 执行时间（毫秒）
        """
        if self.end_time is None:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 链路信息
        """
        return {
            "trace_id": self.trace_id,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "duration": self.get_duration(),
            "spans": [span.to_dict() for span in self.spans],
            "attributes": self.attributes
        }

class TraceManager:
    """链路追踪管理器"""
    
    def __init__(self):
        """
        初始化链路追踪管理器
        """
        self.active_traces: Dict[str, Trace] = {}
    
    def create_trace(self, trace_id: str = None) -> Trace:
        """
        创建一个新的链路追踪
        
        Args:
            trace_id: 追踪ID
            
        Returns:
            Trace: 链路追踪
        """
        trace = Trace(trace_id)
        self.active_traces[trace.trace_id] = trace
        return trace
    
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """
        获取一个链路追踪
        
        Args:
            trace_id: 追踪ID
            
        Returns:
            Optional[Trace]: 链路追踪
        """
        return self.active_traces.get(trace_id)
    
    def finish_trace(self, trace_id: str):
        """
        结束一个链路追踪
        
        Args:
            trace_id: 追踪ID
        """
        if trace_id in self.active_traces:
            trace = self.active_traces[trace_id]
            trace.finish()
            # 可以在这里添加保存逻辑，比如写入数据库或日志
            del self.active_traces[trace_id]
    
    def save_trace(self, trace: Trace):
        """
        保存链路追踪
        
        Args:
            trace: 链路追踪
        """
        # 这里可以实现保存逻辑，比如写入数据库或日志
        pass

# 全局链路追踪管理器实例
_trace_manager = None

def get_trace_manager() -> TraceManager:
    """
    获取链路追踪管理器实例（单例模式）
    
    Returns:
        TraceManager: 链路追踪管理器实例
    """
    global _trace_manager
    if _trace_manager is None:
        _trace_manager = TraceManager()
    return _trace_manager
