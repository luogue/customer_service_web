"""
Loki日志管理模块
功能：
- 实现结构化日志
- 支持Loki日志收集
- 统一日志格式
- 支持多级别日志
"""
import logging
import json
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


class LokiFormatter(logging.Formatter):
    """Loki日志格式化器"""
    
    def format(self, record):
        """格式化日志记录
        
        Args:
            record: 日志记录对象
            
        Returns:
            格式化后的日志字符串
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "customer_service_ai",
            "endpoint": getattr(record, "endpoint", "unknown"),
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", "unknown"),
            "error_type": getattr(record, "error_type", "none"),
            "duration": getattr(record, "duration", 0)
        }
        
        # 添加异常信息
        if record.exc_info:
            import traceback
            log_data["exception"] = traceback.format_exc()
        
        return json.dumps(log_data)


class LokiLogger:
    """Loki日志管理器"""
    
    def __init__(self, name="customer_service", log_dir="logs"):
        """初始化日志管理器
        
        Args:
            name: 日志名称
            log_dir: 日志目录
        """
        self.name = name
        self.log_dir = log_dir
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 初始化日志器
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """设置日志器
        
        Returns:
            配置好的日志器
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 文件处理器 - 按天轮转
        file_handler = TimedRotatingFileHandler(
            os.path.join(self.log_dir, "app.log"),
            when="midnight",
            interval=1,
            backupCount=7
        )
        file_handler.setFormatter(LokiFormatter())
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(LokiFormatter())
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message, **kwargs):
        """记录INFO级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志字段
        """
        extra = kwargs
        self.logger.info(message, extra=extra)
    
    def warning(self, message, **kwargs):
        """记录WARNING级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志字段
        """
        extra = kwargs
        self.logger.warning(message, extra=extra)
    
    def error(self, message, **kwargs):
        """记录ERROR级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志字段
        """
        extra = kwargs
        self.logger.error(message, extra=extra)
    
    def critical(self, message, **kwargs):
        """记录CRITICAL级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志字段
        """
        extra = kwargs
        self.logger.critical(message, extra=extra)
    
    def debug(self, message, **kwargs):
        """记录DEBUG级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志字段
        """
        extra = kwargs
        self.logger.debug(message, extra=extra)


# 全局日志器实例
loki_logger = LokiLogger()


def get_logger(name=None):
    """获取日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    if name:
        return LokiLogger(name)
    return loki_logger


# 日志装饰器
def log_function(func):
    """函数日志装饰器
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    import time
    
    def wrapper(*args, **kwargs):
        start_time = time.time()
        function_name = func.__name__
        
        try:
            # 记录函数开始
            loki_logger.info(f"Function {function_name} started", 
                          function=function_name, 
                          endpoint=function_name)
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 记录函数结束
            duration = (time.time() - start_time) * 1000
            loki_logger.info(f"Function {function_name} completed", 
                          function=function_name, 
                          endpoint=function_name, 
                          duration=round(duration, 2))
            
            return result
        except Exception as e:
            # 记录函数错误
            duration = (time.time() - start_time) * 1000
            loki_logger.error(f"Function {function_name} failed: {str(e)}", 
                           function=function_name, 
                           endpoint=function_name, 
                           error_type=type(e).__name__, 
                           duration=round(duration, 2))
            raise
    
    return wrapper


if __name__ == "__main__":
    # 测试日志功能
    logger = get_logger()
    
    logger.info("测试信息日志", endpoint="test", user_id="123")
    logger.warning("测试警告日志", endpoint="test", user_id="123")
    
    try:
        1 / 0
    except Exception as e:
        logger.error("测试错误日志", endpoint="test", user_id="123", error=str(e))
    
    @log_function
    def test_function():
        logger.info("测试函数执行", endpoint="test_function")
        time.sleep(0.1)
        return "success"
    
    import time
    test_function()
