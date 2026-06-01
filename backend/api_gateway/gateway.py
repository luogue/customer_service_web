"""
API网关模块
所有请求先经过一个统一入口，再转发给后面的接口
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from typing import Dict, List, Optional

from config import settings
from .router import router as main_router
from .rate_limiter import RateLimiter
from .circuit_breaker import CircuitBreaker
from config_center.router import router as config_router
from config_center.config_manager import get_config_manager
from tracing.middleware import TracingMiddleware
from security.sensitive_filter import sensitive_filter

class APIGateway:
    """API网关"""
    
    def __init__(self):
        self.app = FastAPI(
            title=settings.APP_NAME,
            version=settings.APP_VERSION,
            debug=settings.DEBUG
        )
        
        # CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 链路追踪中间件
        self.app.add_middleware(TracingMiddleware)
        
        # 初始化配置中心
        self.config_manager = get_config_manager()
        
        # 初始化限流和熔断
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()
        
        # 注册路由
        self._register_routes()
        
        # 添加中间件
        self._add_middlewares()
    
    def _register_routes(self):
        """注册路由"""
        # 注册主路由
        self.app.include_router(main_router)
        
        # 注册配置中心路由
        self.app.include_router(config_router)
        
        # 健康检查
        @self.app.get("/health")
        async def health_check():
            try:
                from monitoring.prometheus_monitor import prometheus_monitor
                @prometheus_monitor.api_monitor('health')
                async def monitored_health_check():
                    return {
                        "status": "healthy",
                        "timestamp": int(time.time())
                    }
                return await monitored_health_check()
            except ImportError:
                return {
                    "status": "healthy",
                    "timestamp": int(time.time())
                }
    
    def _add_middlewares(self):
        """添加中间件"""
        @self.app.middleware("http")
        async def gateway_middleware(request: Request, call_next):
            """网关中间件"""
            # 1. 获取trace对象
            trace = getattr(request.state, "trace", None)
            
            # 2. 添加网关span
            if trace:
                gateway_span = trace.add_span("gateway", "request_processing")
            
            # 3. 限流检查
            client_ip = request.client.host
            user_id = request.headers.get("X-User-ID", "unknown")
            
            if trace:
                gateway_span.attributes["client_ip"] = client_ip
                gateway_span.attributes["user_id"] = user_id
            
            if not self.rate_limiter.check_rate_limit(client_ip, user_id):
                if trace:
                    gateway_span.finish("failure", "请求过于频繁")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "请求过于频繁，请稍后再试"}
                )
            
            # 4. 敏感词检查（在路由处理中进行，不在中间件中读取请求体）
            
            # 5. 熔断检查（在具体路由处理中实现）
            
            # 6. 处理请求
            try:
                response = await call_next(request)
                if trace:
                    gateway_span.finish("success")
                return response
            except Exception as e:
                if trace:
                    gateway_span.finish("failure", str(e))
                return JSONResponse(
                    status_code=500,
                    content={"detail": "服务器内部错误"}
                )
    
    def get_app(self):
        """获取FastAPI应用实例"""
        return self.app

# 创建网关实例
gateway = APIGateway()
app = gateway.get_app()
