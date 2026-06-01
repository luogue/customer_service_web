"""
安全与合规服务
整合敏感词过滤、输入输出校验、数据隐私保护和合规日志记录
"""
from typing import Dict, Any, Tuple, Optional
from .sensitive_filter import sensitive_filter
from .input_validator import input_validator
from .privacy_protection import privacy_protection
from .compliance_logger import compliance_logger

class SecurityService:
    """安全与合规服务"""
    
    def __init__(self):
        pass
    
    def process_user_input(self, user_id: str, phone: str, input_text: str, session_id: str) -> Dict[str, Any]:
        """
        处理用户输入，进行安全检查
        
        Args:
            user_id: 用户ID
            phone: 用户手机号
            input_text: 用户输入文本
            session_id: 会话ID
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 1. 记录用户查询
        log_id = compliance_logger.log_user_query(user_id, phone, input_text, session_id)
        
        # 2. 输入验证
        is_valid, error_msg = input_validator.validate_input(input_text)
        if not is_valid:
            compliance_logger.log_error(log_id, "input_validation", error_msg)
            return {
                "valid": False,
                "error": error_msg,
                "log_id": log_id,
                "action": "reject"
            }
        
        # 3. 清理输入
        sanitized_input = input_validator.sanitize_input(input_text)
        
        # 4. 敏感词检查
        has_sensitive, sensitive_words, sensitive_categories = sensitive_filter.check_sensitive_content(sanitized_input)
        if has_sensitive:
            compliance_logger.log_error(log_id, "sensitive_content", f"检测到敏感词: {sensitive_words}")
            return {
                "valid": False,
                "error": "输入包含敏感内容",
                "log_id": log_id,
                "action": "reject",
                "sensitive_words": sensitive_words,
                "sensitive_categories": sensitive_categories
            }
        
        # 5. 隐私信息检测
        privacy_info = privacy_protection.detect_privacy_info(sanitized_input)
        
        # 6. 记录处理结果
        compliance_logger.log_processing_result(
            log_id,
            {},  # 意图识别结果稍后更新
            {
                "has_sensitive": has_sensitive,
                "sensitive_words": sensitive_words,
                "sensitive_categories": sensitive_categories
            },
            privacy_info
        )
        
        return {
            "valid": True,
            "log_id": log_id,
            "action": "allow",
            "sanitized_input": sanitized_input,
            "privacy_info": privacy_info
        }
    
    def process_system_response(self, log_id: str, response: str) -> Dict[str, Any]:
        """
        处理系统响应，进行安全检查
        
        Args:
            log_id: 日志ID
            response: 系统响应内容
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 1. 输出验证
        is_valid, error_msg = input_validator.validate_output(response)
        if not is_valid:
            compliance_logger.log_error(log_id, "output_validation", error_msg)
            return {
                "valid": False,
                "error": error_msg,
                "action": "reject"
            }
        
        # 2. 隐私信息打码
        masked_response = privacy_protection.mask_privacy_info(response)
        
        # 3. 记录系统响应
        compliance_logger.log_system_response(log_id, masked_response, "success")
        
        return {
            "valid": True,
            "action": "allow",
            "masked_response": masked_response
        }
    
    def process_knowledge_content(self, content: str) -> Dict[str, Any]:
        """
        处理知识库内容，进行安全检查
        
        Args:
            content: 知识库内容
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 1. 敏感词检查
        has_sensitive, sensitive_words, sensitive_categories = sensitive_filter.check_sensitive_content(content)
        if has_sensitive:
            return {
                "valid": False,
                "error": "内容包含敏感信息",
                "action": "reject",
                "sensitive_words": sensitive_words,
                "sensitive_categories": sensitive_categories
            }
        
        # 2. 隐私信息打码
        masked_content = privacy_protection.mask_privacy_info(content)
        
        return {
            "valid": True,
            "action": "allow",
            "masked_content": masked_content
        }

# 全局安全服务实例
security_service = SecurityService()
