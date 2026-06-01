"""
输入输出校验模块
用于对用户输入进行安全检查，过滤SQL注入、恶意代码，限制文本长度等
"""
import re
from typing import Dict, Any, Tuple, Optional

class InputValidator:
    """输入验证器"""
    
    def __init__(self):
        # SQL注入模式
        self.sql_injection_patterns = [
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|RENAME|GRANT|REVOKE)\b',
            r'\b(UNION|FROM|WHERE|JOIN|GROUP|ORDER|LIMIT|OFFSET)\b',
            r"'\s*OR\s*'1'='1",
            r"'\s*AND\s*'1'='1",
            r'\bEXEC\b',
            r'\bEXECUTE\b',
            r'\bSP_EXECUTESQL\b'
        ]
        
        # 恶意代码模式
        self.malicious_code_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'javascript:',
            r'vbscript:',
            r'expression\(',
            r'on\w+\s*='
        ]
        
        # 文本长度限制
        self.max_input_length = 1000
        self.min_input_length = 1
    
    def validate_input(self, input_text: str) -> Tuple[bool, Optional[str]]:
        """
        验证用户输入
        
        Args:
            input_text: 用户输入文本
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        # 检查输入长度
        if not input_text:
            return False, "输入不能为空"
        
        if len(input_text) < self.min_input_length:
            return False, f"输入长度不能少于{self.min_input_length}个字符"
        
        if len(input_text) > self.max_input_length:
            return False, f"输入长度不能超过{self.max_input_length}个字符"
        
        # 检查SQL注入
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                return False, "输入包含非法内容（SQL注入）"
        
        # 检查恶意代码
        for pattern in self.malicious_code_patterns:
            if re.search(pattern, input_text, re.IGNORECASE | re.DOTALL):
                return False, "输入包含非法内容（恶意代码）"
        
        return True, None
    
    def sanitize_input(self, input_text: str) -> str:
        """
        清理用户输入
        
        Args:
            input_text: 用户输入文本
            
        Returns:
            str: 清理后的输入
        """
        if not input_text:
            return input_text
        
        # 去除首尾空格
        sanitized = input_text.strip()
        
        # 转义特殊字符
        sanitized = sanitized.replace('<', '&lt;').replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;').replace("'", '&#39;')
        
        return sanitized
    
    def validate_output(self, output_text: str) -> Tuple[bool, Optional[str]]:
        """
        验证系统输出
        
        Args:
            output_text: 系统输出文本
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        # 检查输出长度
        if output_text and len(output_text) > 5000:
            return False, "输出长度过长"
        
        return True, None

# 全局输入验证器实例
input_validator = InputValidator()
