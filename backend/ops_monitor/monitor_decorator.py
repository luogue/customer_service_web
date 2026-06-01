"""
监控装饰器
用于在API接口上添加监控功能
"""
import time
from functools import wraps
from typing import Optional
from knowledge_base.models import get_db
from .monitor_service import get_monitor_service

class monitor_api:
    """
    API监控装饰器
    用于记录API接口的调用信息
    """
    
    def __init__(self, endpoint: Optional[str] = None):
        """
        初始化装饰器
        
        Args:
            endpoint: 接口端点，如果不指定，会自动从函数名或路由获取
        """
        self.endpoint = endpoint
    
    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 开始时间
            start_time = time.time()
            status = "success"
            error_message = None
            
            try:
                # 执行原函数
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "failure"
                error_message = str(e)
                raise
            finally:
                # 计算响应时间（毫秒）
                response_time = (time.time() - start_time) * 1000
                
                # 获取接口端点
                endpoint = self.endpoint
                if not endpoint:
                    endpoint = func.__name__
                
                # 获取请求方法
                method = "POST"  # 默认方法
                
                # 获取用户ID（如果有）
                user_id = None
                
                # 记录API调用
                db = next(get_db())
                try:
                    monitor_service = get_monitor_service(db)
                    monitor_service.record_api_call(
                        endpoint=endpoint,
                        method=method,
                        status=status,
                        response_time=response_time,
                        error_message=error_message,
                        user_id=user_id
                    )
                finally:
                    db.close()
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 开始时间
            start_time = time.time()
            status = "success"
            error_message = None
            
            try:
                # 执行原函数
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "failure"
                error_message = str(e)
                raise
            finally:
                # 计算响应时间（毫秒）
                response_time = (time.time() - start_time) * 1000
                
                # 获取接口端点
                endpoint = self.endpoint
                if not endpoint:
                    endpoint = func.__name__
                
                # 获取请求方法
                method = "POST"  # 默认方法
                
                # 获取用户ID（如果有）
                user_id = None
                
                # 记录API调用
                db = next(get_db())
                try:
                    monitor_service = get_monitor_service(db)
                    monitor_service.record_api_call(
                        endpoint=endpoint,
                        method=method,
                        status=status,
                        response_time=response_time,
                        error_message=error_message,
                        user_id=user_id
                    )
                finally:
                    db.close()
        
        # 判断函数是异步还是同步
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
