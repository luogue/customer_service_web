"""
转人工处理器
独立模块 - 负责转人工相关逻辑
"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TransferHumanHandler:
    """转人工处理器"""
    
    def __init__(self, db: Session = None):
        self.db = db
    
    def transfer_to_human(self, reason: str = "", order_info: Dict = None) -> Dict[str, Any]:
        """
        转人工客服
        
        Args:
            reason: 转人工原因
            order_info: 相关订单信息（可选）
            
        Returns:
            转人工结果
        """
        logger.info(f"转人工客服: 原因={reason}, 订单={order_info}")
        
        # 这里应该调用实际的转人工服务
        # 目前返回成功消息
        return {
            "success": True,
            "message": "已为您转接人工客服，请稍候。",
            "action": "transfer_human",
            "reason": reason,
            "order_info": order_info
        }
    
    def check_transfer_conditions(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """
        检查是否需要转人工
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            {
                "should_transfer": bool,
                "reason": str
            }
        """
        # 检查用户是否明确要求人工
        transfer_keywords = ["人工", "客服", "真人", "转接"]
        if any(keyword in user_input for keyword in transfer_keywords):
            return {
                "should_transfer": True,
                "reason": "用户明确要求转人工"
            }
        
        # 可以添加更多转人工条件
        # 例如：连续多次无法识别意图、用户情绪检测等
        
        return {
            "should_transfer": False,
            "reason": ""
        }
    
    def get_transfer_message(self, context: str = "") -> str:
        """
        获取转人工提示消息
        
        Args:
            context: 上下文信息
            
        Returns:
            转人工提示消息
        """
        if context:
            return f"{context}\n\n已为您转接人工客服，请稍候。"
        return "已为您转接人工客服，请稍候。"
    
    def record_transfer(self, session_id: str, user_id: str, reason: str) -> bool:
        """
        记录转人工信息
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            reason: 转人工原因
            
        Returns:
            是否记录成功
        """
        try:
            logger.info(f"记录转人工: session_id={session_id}, user_id={user_id}, reason={reason}")
            # 这里应该保存到数据库
            return True
        except Exception as e:
            logger.error(f"记录转人工失败: {e}")
            return False


# 全局实例
_transfer_human_handler_instance: Optional[TransferHumanHandler] = None


def get_transfer_human_handler(db: Session = None) -> TransferHumanHandler:
    """获取转人工处理器实例"""
    global _transfer_human_handler_instance
    if _transfer_human_handler_instance is None:
        _transfer_human_handler_instance = TransferHumanHandler(db)
    elif db:
        _transfer_human_handler_instance.db = db
    return _transfer_human_handler_instance
