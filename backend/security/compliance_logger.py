"""
合规日志记录模块
用于完整记录用户提问内容、处理结果、返回内容、操作时间等信息
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

class ComplianceLogger:
    """合规日志记录器"""
    
    def __init__(self):
        # 配置日志
        self.logger = logging.getLogger("compliance")
        if not self.logger.handlers:
            # 创建文件处理器
            file_handler = logging.FileHandler("compliance.log", encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 配置日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)
    
    def log_user_query(self, user_id: str, phone: str, query: str, session_id: str) -> str:
        """
        记录用户查询
        
        Args:
            user_id: 用户ID
            phone: 用户手机号
            query: 用户查询内容
            session_id: 会话ID
            
        Returns:
            str: 日志ID
        """
        log_id = f"LOG_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        log_data = {
            "log_id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "user_query",
            "user_id": user_id,
            "phone": phone,
            "session_id": session_id,
            "query": query
        }
        
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
        return log_id
    
    def log_processing_result(self, log_id: str, intent_result: Dict[str, Any], 
                            sensitive_check: Dict[str, Any], privacy_info: Dict[str, Any]) -> None:
        """
        记录处理结果
        
        Args:
            log_id: 日志ID
            intent_result: 意图识别结果
            sensitive_check: 敏感词检查结果
            privacy_info: 隐私信息检测结果
        """
        log_data = {
            "log_id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "processing_result",
            "intent_result": intent_result,
            "sensitive_check": sensitive_check,
            "privacy_info": privacy_info
        }
        
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_system_response(self, log_id: str, response: str, status: str) -> None:
        """
        记录系统响应
        
        Args:
            log_id: 日志ID
            response: 系统响应内容
            status: 处理状态
        """
        log_data = {
            "log_id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "system_response",
            "response": response,
            "status": status
        }
        
        self.logger.info(json.dumps(log_data, ensure_ascii=False))
    
    def log_error(self, log_id: str, error_type: str, error_message: str) -> None:
        """
        记录错误信息
        
        Args:
            log_id: 日志ID
            error_type: 错误类型
            error_message: 错误信息
        """
        log_data = {
            "log_id": log_id,
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "error_type": error_type,
            "error_message": error_message
        }
        
        self.logger.error(json.dumps(log_data, ensure_ascii=False))

# 全局合规日志记录器实例
compliance_logger = ComplianceLogger()
