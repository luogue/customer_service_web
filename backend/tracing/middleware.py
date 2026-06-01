"""
链路追踪中间件
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from tracing.trace_manager import get_trace_manager, Trace
import time

class TracingMiddleware(BaseHTTPMiddleware):
    """
    链路追踪中间件
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求
        
        Args:
            request: 请求对象
            call_next: 下一个处理器
            
        Returns:
            Response: 响应对象
        """
        # 从请求头中获取trace_id，如果没有则创建一个新的
        trace_id = request.headers.get("X-Trace-ID")
        trace_manager = get_trace_manager()
        trace = trace_manager.create_trace(trace_id)
        
        # 将trace_id添加到请求头中
        request.state.trace_id = trace.trace_id
        request.state.trace = trace
        
        # 添加请求信息到trace属性
        trace.attributes["request"] = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client": {
                "host": request.client.host,
                "port": request.client.port
            }
        }
        
        # 添加接入层span
        access_span = trace.add_span("access_layer", "request_received")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 结束接入层span
            access_span.finish("success")
            
            # 添加响应信息到trace属性
            trace.attributes["response"] = {
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
            
            # 将trace_id添加到响应头中
            response.headers["X-Trace-ID"] = trace.trace_id
            
        except Exception as e:
            # 结束接入层span，标记为失败
            access_span.finish("failure", str(e))
            
            # 记录详细的错误信息
            import traceback
            error_traceback = traceback.format_exc()
            print(f"Error occurred: {e}")
            print(f"Traceback: {error_traceback}")
            
            # 创建一个错误响应
            from fastapi.responses import JSONResponse
            response = JSONResponse(
                status_code=500,
                content={"detail": "服务器内部错误"}
            )
            
            # 将trace_id添加到响应头中
            response.headers["X-Trace-ID"] = trace.trace_id
            
            # 添加响应信息到trace属性
            trace.attributes["response"] = {
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
            
            # 添加错误信息到trace属性
            trace.attributes["error"] = {
                "message": str(e),
                "traceback": error_traceback
            }
            
            return response
        finally:
            # 结束trace
            trace.finish()
            
            # 保存trace
            trace_manager.save_trace(trace)
            
            # 从活跃traces中移除
            trace_manager.finish_trace(trace.trace_id)
        
        return response
