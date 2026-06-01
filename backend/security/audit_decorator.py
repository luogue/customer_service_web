"""
审计装饰器
用于在管理员执行关键操作时自动记录审计日志
"""
import time
from functools import wraps
from typing import Optional, Dict, Any
from .audit_logger import get_audit_logger


class audit_admin_operation:
    """
    管理员操作审计装饰器
    用于记录管理员执行的关键操作
    """
    
    def __init__(self, operation: str, resource: str, action: str):
        """
        初始化装饰器
        
        Args:
            operation: 操作名称
            resource: 操作的资源
            action: 具体动作
        """
        self.operation = operation
        self.resource = resource
        self.action = action
    
    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            error = None
            content = None
            admin_id = "unknown"
            
            # 获取管理员ID（如果存在）
            if "admin_id" in kwargs:
                admin_id = kwargs["admin_id"]
            elif "user_id" in kwargs:
                admin_id = kwargs["user_id"]
            elif len(args) > 0:
                # 尝试从参数中获取admin_id或user_id
                for arg in args:
                    if isinstance(arg, dict) and ("admin_id" in arg or "user_id" in arg):
                        admin_id = arg.get("admin_id", arg.get("user_id", "unknown"))
                        break
            
            try:
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 获取返回内容
                if isinstance(result, dict):
                    content = str(result)
                elif isinstance(result, str):
                    content = result
                
                return result
            except Exception as e:
                status = "failure"
                error = str(e)
                raise
            finally:
                # 计算耗时（毫秒）
                duration = (time.time() - start_time) * 1000
                
                # 记录审计日志
                audit_logger = get_audit_logger()
                audit_logger.record(
                    admin_id=admin_id,
                    operation=self.operation,
                    status=status,
                    resource=self.resource,
                    action=self.action,
                    content=content,
                    error=error,
                    metadata={"duration": duration}
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            error = None
            content = None
            admin_id = "unknown"
            
            # 获取管理员ID（如果存在）
            if "admin_id" in kwargs:
                admin_id = kwargs["admin_id"]
            elif "user_id" in kwargs:
                admin_id = kwargs["user_id"]
            elif len(args) > 0:
                # 尝试从参数中获取admin_id或user_id
                for arg in args:
                    if isinstance(arg, dict) and ("admin_id" in arg or "user_id" in arg):
                        admin_id = arg.get("admin_id", arg.get("user_id", "unknown"))
                        break
            
            try:
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 获取返回内容
                if isinstance(result, dict):
                    content = str(result)
                elif isinstance(result, str):
                    content = result
                
                return result
            except Exception as e:
                status = "failure"
                error = str(e)
                raise
            finally:
                # 计算耗时（毫秒）
                duration = (time.time() - start_time) * 1000
                
                # 记录审计日志
                audit_logger = get_audit_logger()
                audit_logger.record(
                    admin_id=admin_id,
                    operation=self.operation,
                    status=status,
                    resource=self.resource,
                    action=self.action,
                    content=content,
                    error=error,
                    metadata={"duration": duration}
                )
        
        # 判断函数是异步还是同步
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
