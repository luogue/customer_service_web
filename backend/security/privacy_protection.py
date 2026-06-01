"""
数据隐私保护模块
用于自动识别手机号、身份证号、订单号等隐私信息并打码
"""
import re
from typing import Dict, List, Tuple, Any

class PrivacyProtection:
    """隐私信息保护"""
    
    def __init__(self):
        # 隐私信息正则表达式
        self.privacy_patterns = {
            "phone": {
                "pattern": r'1[3-9]\d{9}',
                "mask": lambda x: x[:3] + '*' * 4 + x[-4:]
            },
            "id_card": {
                "pattern": r'[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]',
                "mask": lambda x: x[:6] + '*' * 8 + x[-4:]
            },
            "order_number": {
                "pattern": r'(?:订单号|订单编号|订单)[：:]?\s*([A-Za-z0-9-]{8,20})',
                "mask": lambda x: x[:4] + '*' * (len(x) - 8) + x[-4:]
            },
            "bank_card": {
                "pattern": r'\d{4}(?:\s*\d{4}){3,4}',
                "mask": lambda x: x[:4] + ' **** **** ' + x[-4:]
            },
            "email": {
                "pattern": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                "mask": lambda x: x.split('@')[0][:3] + '*' * 4 + '@' + x.split('@')[1]
            }
        }
    
    def detect_privacy_info(self, text: str) -> Dict[str, List[str]]:
        """
        检测文本中的隐私信息
        
        Args:
            text: 要检测的文本
            
        Returns:
            Dict[str, List[str]]: 检测到的隐私信息，键为隐私类型，值为隐私信息列表
        """
        if not text:
            return {}
        
        detected_info = {}
        
        for info_type, config in self.privacy_patterns.items():
            matches = re.findall(config["pattern"], text)
            if matches:
                # 对于订单号，只提取捕获组
                if info_type == "order_number":
                    detected_info[info_type] = matches
                else:
                    detected_info[info_type] = matches
        
        return detected_info
    
    def mask_privacy_info(self, text: str) -> str:
        """
        对文本中的隐私信息进行打码
        
        Args:
            text: 要打码的文本
            
        Returns:
            str: 打码后的文本
        """
        if not text:
            return text
        
        masked_text = text
        
        for info_type, config in self.privacy_patterns.items():
            if info_type == "order_number":
                # 对于订单号，需要保留前缀
                def replace_order_number(match):
                    order_number = match.group(1)
                    masked_number = config["mask"](order_number)
                    return f"{match.group(0).replace(order_number, masked_number)}"
                masked_text = re.sub(config["pattern"], replace_order_number, masked_text)
            else:
                # 对于其他隐私信息，直接替换
                def replace_func(match):
                    return config["mask"](match.group(0))
                masked_text = re.sub(config["pattern"], replace_func, masked_text)
        
        return masked_text
    
    def mask_privacy_in_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        对字典中的隐私信息进行打码
        
        Args:
            data: 要打码的字典
            
        Returns:
            Dict[str, Any]: 打码后的字典
        """
        if not data:
            return data
        
        masked_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                masked_data[key] = self.mask_privacy_info(value)
            elif isinstance(value, dict):
                masked_data[key] = self.mask_privacy_in_dict(value)
            elif isinstance(value, list):
                masked_data[key] = [
                    self.mask_privacy_info(item) if isinstance(item, str) else 
                    self.mask_privacy_in_dict(item) if isinstance(item, dict) else 
                    item
                    for item in value
                ]
            else:
                masked_data[key] = value
        
        return masked_data

# 全局隐私保护实例
privacy_protection = PrivacyProtection()
