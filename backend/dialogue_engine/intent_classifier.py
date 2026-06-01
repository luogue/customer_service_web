"""
简单意图识别模块
五层架构：对话引擎层

功能：
1. 判断用户是同意/确认，还是拒绝/取消
2. 其他情况统一按无法识别处理
3. 提示用户只回复是或否
"""
import re
from typing import Dict, List
from enum import Enum


class UserIntent(Enum):
    """用户意图枚举"""
    CONFIRM = "confirm"      # 确认/同意
    REJECT = "reject"        # 拒绝/取消
    TRANSFER = "transfer"    # 转人工
    UNKNOWN = "unknown"      # 无法识别


class IntentClassifier:
    """简单意图识别器"""
    
    def __init__(self):
        # 确认/同意的关键词
        self.confirm_keywords = [
            # 直接确认
            "是", "是的", "对", "对的", "没错", "正确",
            "好", "好的", "行", "可以", "嗯", "恩",
            "确认", "同意", "接受", "认可",
            "没问题", "没问题", "就这样", "要",
            "ok", "okay", "yes", "y", "嗯嗯", "对对",
            # 积极回应
            "好啊", "行啊", "可以啊", "没问题啊",
            "要的", "想的", "愿意"
        ]
        
        # 拒绝/取消的关键词
        self.reject_keywords = [
            # 直接拒绝
            "否", "不是", "不对", "错误", "否定的",
            "不", "不要", "不行", "不可以", "不能",
            "拒绝", "取消", "放弃", "算了", "别",
            "no", "n", "non", "否认",
            # 消极回应
            "不好", "不行啊", "不可以啊", "不能啊",
            "不要了", "算了", "别这样", "不愿意",
            "不想", "不需要", "不用了"
        ]
        
        # 转人工的关键词
        self.transfer_keywords = [
            # 直接转人工
            "人工", "转人工", "人工客服", "客服",
            "人工服务", "找人工", "我要人工", "联系人工",
            "转接人工", "转客服", "客服人员", "真人",
            # 表达不满要求人工
            "投诉", "投诉人工", "强烈不满", "无法解决",
            "解决不了", "没用", "不好用", "太差了",
            "太烂了", "垃圾", "人工处理", "需要人工"
        ]
        
        # 无法识别时的提示语
        self.unknown_prompts = [
            '抱歉，我没有理解您的意思。请回复"是"或"不是"。',
            '我不太明白，您可以直接回复"是"或"不是"吗？',
            '请简单回复"是"或"不是"，谢谢！',
            '我没有听懂，您同意的话请回复"是"，不同意请回复"不是"。',
            '请用"是"或"不是"来回答，好吗？'
        ]
    
    def classify(self, message: str) -> Dict[str, any]:
        """
        识别用户意图
        
        Args:
            message: 用户输入消息
            
        Returns:
            {
                "intent": UserIntent,  # 识别出的意图
                "is_confirmed": bool,  # 是否确认
                "is_rejected": bool,   # 是否拒绝
                "is_unknown": bool,    # 是否无法识别
                "prompt": str          # 无法识别时的提示语
            }
        """
        if not message or not message.strip():
            return {
                "intent": UserIntent.UNKNOWN,
                "is_confirmed": False,
                "is_rejected": False,
                "is_unknown": True,
                "prompt": self._get_unknown_prompt()
            }
        
        # 清理消息
        cleaned = self._clean_message(message)
        
        # 先检查拒绝意图（优先于确认意图，避免"不是"被识别为"是"）
        if self._is_reject(cleaned):
            return {
                "intent": UserIntent.REJECT,
                "is_confirmed": False,
                "is_rejected": True,
                "is_unknown": False,
                "prompt": ""
            }
        
        # 再检查确认意图
        if self._is_confirm(cleaned):
            return {
                "intent": UserIntent.CONFIRM,
                "is_confirmed": True,
                "is_rejected": False,
                "is_transfer": False,
                "is_unknown": False,
                "prompt": ""
            }
        
        # 检查转人工意图
        if self._is_transfer(cleaned):
            return {
                "intent": UserIntent.TRANSFER,
                "is_confirmed": False,
                "is_rejected": False,
                "is_transfer": True,
                "is_unknown": False,
                "prompt": ""
            }
        
        # 无法识别
        return {
            "intent": UserIntent.UNKNOWN,
            "is_confirmed": False,
            "is_rejected": False,
            "is_transfer": False,
            "is_unknown": True,
            "prompt": self._get_unknown_prompt()
        }
    
    def _clean_message(self, message: str) -> str:
        """清理消息文本"""
        # 去除首尾空格
        message = message.strip()
        # 去除标点符号
        message = re.sub(r'[，。？！,.?!~\s]+', '', message)
        # 转小写
        return message.lower()
    
    def _is_confirm(self, message: str) -> bool:
        """判断是否为确认意图"""
        # 完全匹配
        if message in self.confirm_keywords:
            return True
        
        # 正则匹配常见确认模式（严格匹配，避免"不是"被识别）
        confirm_patterns = [
            r'^是的?$',
            r'^对的?$',
            r'^好的?$',
            r'^没错$',
            r'^确认$',
            r'^同意$',
            r'^ok$',
            r'^yes$',
            r'^嗯+$',
            r'^对+$',
            r'^是$',
            r'^对$',
            r'^好$',
            r'^行$',
            r'^嗯$',
        ]
        
        for pattern in confirm_patterns:
            if re.match(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _is_reject(self, message: str) -> bool:
        """判断是否为拒绝意图"""
        # 完全匹配
        if message in self.reject_keywords:
            return True
        
        # 包含拒绝关键词（短消息）
        if len(message) <= 4:
            for keyword in self.reject_keywords:
                if keyword in message:
                    return True
        
        # 正则匹配常见拒绝模式
        reject_patterns = [
            r'^不是$',
            r'^否$',
            r'^不对$',
            r'^错误$',
            r'^拒绝$',
            r'^取消$',
            r'^no$',
            r'^non$',
            r'^不+$',
            r'^算了$',
        ]
        
        for pattern in reject_patterns:
            if re.match(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _is_transfer(self, message: str) -> bool:
        """判断是否为转人工意图"""
        # 完全匹配
        if message in self.transfer_keywords:
            return True
        
        # 包含转人工关键词
        for keyword in self.transfer_keywords:
            if keyword in message:
                return True
        
        # 正则匹配常见转人工模式
        transfer_patterns = [
            r'^人工$',
            r'^转人工$',
            r'^人工客服$',
            r'^客服$',
            r'^找人工$',
            r'^我要人工$',
            r'^联系人工$',
            r'^转接人工$',
            r'^转客服$',
        ]
        
        for pattern in transfer_patterns:
            if re.match(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _get_unknown_prompt(self) -> str:
        """获取无法识别的提示语"""
        import random
        return random.choice(self.unknown_prompts)
    
    def get_confirm_prompt(self, context: str = "") -> str:
        """
        获取确认提示语
        
        Args:
            context: 上下文信息
            
        Returns:
            确认提示语
        """
        if context:
            return f'{context}，请问对吗？请回复"是"或"不是"。'
        return '请回复"是"或"不是"。'


# ==================== 全局实例 ====================

intent_classifier = IntentClassifier()


# ==================== 便捷函数 ====================

def classify_intent(message: str) -> Dict[str, any]:
    """识别用户意图"""
    return intent_classifier.classify(message)


def is_confirmed(message: str) -> bool:
    """判断用户是否确认"""
    result = intent_classifier.classify(message)
    return result["is_confirmed"]


def is_rejected(message: str) -> bool:
    """判断用户是否拒绝"""
    result = intent_classifier.classify(message)
    return result["is_rejected"]


def is_transfer(message: str) -> bool:
    """判断用户是否要求转人工"""
    result = intent_classifier.classify(message)
    return result.get("is_transfer", False)


def get_unknown_prompt() -> str:
    """获取无法识别的提示语"""
    return intent_classifier._get_unknown_prompt()
