"""
Prometheus监控模块
功能：
- 集成Prometheus客户端库
- 定义关键指标
- 暴露指标端点
- 提供埋点装饰器
"""
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import threading
from functools import wraps


# 定义关键指标
# API调用计数器
api_calls = Counter('api_calls_total', 'Total API calls', ['endpoint', 'method', 'status'])

# API响应时间直方图
api_response_time = Histogram('api_response_time_seconds', 'API response time in seconds', ['endpoint', 'method'])

# 错误计数器
error_count = Counter('error_count_total', 'Total error count', ['endpoint', 'error_type'])

# 系统资源指标
system_memory_usage = Gauge('system_memory_usage_bytes', 'System memory usage')
system_cpu_usage = Gauge('system_cpu_usage_percent', 'System CPU usage percent')

# 数据库指标
db_query_time = Histogram('db_query_time_seconds', 'Database query time in seconds', ['query_type'])
db_connection_count = Gauge('db_connection_count', 'Database connection count')

# 向量库指标
vector_store_size = Gauge('vector_store_size', 'Vector store size')
vector_query_time = Histogram('vector_query_time_seconds', 'Vector query time in seconds')


class PrometheusMonitor:
    """Prometheus监控器"""
    
    def __init__(self, port=8005):
        """初始化监控器
        
        Args:
            port: Prometheus指标暴露端口
        """
        self.port = port
    
    def start_server(self):
        """启动Prometheus指标服务器"""
        def server_thread():
            start_http_server(self.port)
            print(f"[监控] Prometheus指标服务器已启动，端口: {self.port}")
        
        # 启动指标服务器线程
        server_thread = threading.Thread(target=server_thread, daemon=True)
        server_thread.start()
    
    def api_monitor(self, endpoint):
        """API监控装饰器
        
        Args:
            endpoint: 端点名称
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                method = kwargs.get('method', 'GET')
                
                try:
                    # 执行原函数
                    result = await func(*args, **kwargs)
                    status = '200'
                except Exception as e:
                    status = '500'
                    error_count.labels(endpoint=endpoint, error_type=type(e).__name__).inc()
                    raise
                finally:
                    # 记录指标
                    api_calls.labels(endpoint=endpoint, method=method, status=status).inc()
                    api_response_time.labels(endpoint=endpoint, method=method).observe(time.time() - start_time)
                
                return result
            return wrapper
        return decorator
    
    def sync_api_monitor(self, endpoint):
        """同步API监控装饰器
        
        Args:
            endpoint: 端点名称
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                method = kwargs.get('method', 'GET')
                
                try:
                    # 执行原函数
                    result = func(*args, **kwargs)
                    status = '200'
                except Exception as e:
                    status = '500'
                    error_count.labels(endpoint=endpoint, error_type=type(e).__name__).inc()
                    raise
                finally:
                    # 记录指标
                    api_calls.labels(endpoint=endpoint, method=method, status=status).inc()
                    api_response_time.labels(endpoint=endpoint, method=method).observe(time.time() - start_time)
                
                return result
            return wrapper
        return decorator
    
    def db_query_monitor(self, query_type):
        """数据库查询监控装饰器
        
        Args:
            query_type: 查询类型
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                finally:
                    db_query_time.labels(query_type=query_type).observe(time.time() - start_time)
                
                return result
            return wrapper
        return decorator
    
    def vector_query_monitor(self):
        """向量查询监控装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                finally:
                    vector_query_time.observe(time.time() - start_time)
                
                return result
            return wrapper
        return decorator


# 全局监控器实例
prometheus_monitor = PrometheusMonitor()


def init_monitoring():
    """初始化监控系统"""
    prometheus_monitor.start_server()


if __name__ == "__main__":
    # 测试监控系统
    init_monitoring()
    
    # 模拟API调用
    @prometheus_monitor.api_monitor('test')
    async def test_api():
        time.sleep(0.1)
        return "test"
    
    import asyncio
    async def test():
        for i in range(10):
            await test_api()
            time.sleep(0.5)
    
    asyncio.run(test())
