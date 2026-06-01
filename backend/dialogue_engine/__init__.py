"""
对话引擎模块
包含：
- 原有对话管理器（保持兼容）
- 新的模块化对话管理器
- 独立的处理器模块
"""

# 原有模块（保持兼容）
from .dialogue import dialogue_manager, DialogueManager as OldDialogueManager
from .order_dialogue import OrderDialogueFlow, get_order_dialogue_flow
from .intent_classifier import (
    IntentClassifier,
    intent_classifier,
    UserIntent,
    classify_intent,
    is_confirmed,
    is_rejected,
    get_unknown_prompt
)

# 新的模块化组件
from .dialogue_manager import DialogueManager, get_dialogue_manager
from .handlers import (
    OrderQueryHandler,
    get_order_query_handler,
    RefundHandler,
    get_refund_handler,
    ExchangeHandler,
    get_exchange_handler,
    TransferHumanHandler,
    get_transfer_human_handler,
    ComplaintHandler,
    get_complaint_handler,
    ModifyOrderHandler,
    get_modify_order_handler,
    TaskRouter,
    get_task_router
)

__all__ = [
    # 原有模块（保持兼容）
    'dialogue_manager',
    'DialogueManager',
    'OrderDialogueFlow',
    'get_order_dialogue_flow',
    'IntentClassifier',
    'intent_classifier',
    'UserIntent',
    'classify_intent',
    'is_confirmed',
    'is_rejected',
    'get_unknown_prompt',
    
    # 新的模块化组件
    'get_dialogue_manager',
    'OrderQueryHandler',
    'get_order_query_handler',
    'RefundHandler',
    'get_refund_handler',
    'ExchangeHandler',
    'get_exchange_handler',
    'TransferHumanHandler',
    'get_transfer_human_handler',
    'ComplaintHandler',
    'get_complaint_handler',
    'ModifyOrderHandler',
    'get_modify_order_handler',
    'TaskRouter',
    'get_task_router'
]
