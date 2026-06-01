"""
对话流程状态机
实现节点管理和流程控制
"""
from enum import Enum, auto
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from ops_monitor import logger


class DialogueNode(Enum):
    """对话节点枚举"""
    INITIAL = auto()                    # 初始节点
    WAITING_INTENT_CONFIRM = auto()     # 等待意图确认
    WAITING_PHONE_CONFIRM = auto()      # 等待手机号确认
    PROCESSING_ORDER_QUERY = auto()     # 处理订单查询
    COMPLETED = auto()                  # 已完成（转人工）


@dataclass
class NodeConfig:
    """节点配置"""
    node: DialogueNode
    expected_responses: List[str]       # 预期回复类型：['confirm', 'reject'] 或 ['any']
    on_confirm: Optional[str] = None    # 确认后的下一个节点
    on_reject: Optional[str] = None     # 拒绝后的下一个节点
    on_interrupt: Optional[str] = None  # 打断后的下一个节点


class DialogueStateMachine:
    """
    对话流程状态机
    
    功能：
    1. 管理当前节点 (current_node)
    2. 检查用户回复是否符合预期
    3. 如果不符合预期，打断当前流程，重新识别意图
    4. 如果符合预期，继续原有流程
    """
    
    def __init__(self):
        self.current_node: DialogueNode = DialogueNode.INITIAL
        self.node_history: List[DialogueNode] = field(default_factory=list)
        self.context: Dict = field(default_factory=dict)
        
        # 节点配置映射
        self.node_configs = {
            DialogueNode.INITIAL: NodeConfig(
                node=DialogueNode.INITIAL,
                expected_responses=['any'],
                on_interrupt=None
            ),
            DialogueNode.WAITING_INTENT_CONFIRM: NodeConfig(
                node=DialogueNode.WAITING_INTENT_CONFIRM,
                expected_responses=['confirm', 'reject'],
                on_confirm='PROCESSING_ORDER_QUERY',
                on_reject='INITIAL',
                on_interrupt='INITIAL'
            ),
            DialogueNode.WAITING_PHONE_CONFIRM: NodeConfig(
                node=DialogueNode.WAITING_PHONE_CONFIRM,
                expected_responses=['confirm', 'reject'],
                on_confirm='COMPLETED',
                on_reject='INITIAL',
                on_interrupt='INITIAL'
            ),
            DialogueNode.PROCESSING_ORDER_QUERY: NodeConfig(
                node=DialogueNode.PROCESSING_ORDER_QUERY,
                expected_responses=['any'],
                on_interrupt='INITIAL'
            ),
            DialogueNode.COMPLETED: NodeConfig(
                node=DialogueNode.COMPLETED,
                expected_responses=['none'],
                on_interrupt=None
            ),
        }
    
    def get_current_node(self) -> DialogueNode:
        """获取当前节点"""
        return self.current_node
    
    def set_node(self, node: DialogueNode, context: Dict = None):
        """设置当前节点"""
        logger.info(f"状态机节点切换: {self.current_node.name} -> {node.name}")
        self.node_history.append(self.current_node)
        self.current_node = node
        if context:
            self.context.update(context)
    
    def is_expected_response(self, response_type: str) -> bool:
        """
        检查回复是否符合当前节点的预期
        
        Args:
            response_type: 回复类型 ('confirm', 'reject', 'unknown', 'any')
            
        Returns:
            是否符合预期
        """
        config = self.node_configs.get(self.current_node)
        if not config:
            return True
        
        expected = config.expected_responses
        
        # 如果预期是 'any'，任何回复都符合
        if 'any' in expected:
            return True
        
        # 如果预期是 'none'，任何回复都不符合（已完成状态）
        if 'none' in expected:
            return False
        
        # 检查回复是否在预期列表中
        return response_type in expected
    
    def should_interrupt(self, response_type: str) -> bool:
        """
        判断是否需要打断当前流程
        
        当用户回复不符合当前节点预期时，需要打断流程
        
        Args:
            response_type: 回复类型
            
        Returns:
            是否需要打断
        """
        should = not self.is_expected_response(response_type)
        if should:
            logger.info(f"流程需要打断: 当前节点={self.current_node.name}, 回复类型={response_type}")
        return should
    
    def get_interrupt_action(self) -> Optional[str]:
        """获取打断后的动作"""
        config = self.node_configs.get(self.current_node)
        if config:
            return config.on_interrupt
        return None
    
    def get_next_node(self, response_type: str) -> Optional[DialogueNode]:
        """
        根据回复类型获取下一个节点
        
        Args:
            response_type: 回复类型 ('confirm', 'reject')
            
        Returns:
            下一个节点，如果没有则返回 None
        """
        config = self.node_configs.get(self.current_node)
        if not config:
            return None
        
        if response_type == 'confirm' and config.on_confirm:
            return DialogueNode[config.on_confirm]
        elif response_type == 'reject' and config.on_reject:
            return DialogueNode[config.on_reject]
        
        return None
    
    def reset(self):
        """重置状态机"""
        logger.info("状态机重置")
        self.current_node = DialogueNode.INITIAL
        self.node_history.clear()
        self.context.clear()
    
    def get_context(self, key: str, default=None):
        """获取上下文数据"""
        return self.context.get(key, default)
    
    def set_context(self, key: str, value):
        """设置上下文数据"""
        self.context[key] = value


# 全局状态机实例
_state_machine_instance = None


def get_state_machine() -> DialogueStateMachine:
    """获取状态机实例（单例模式）"""
    global _state_machine_instance
    if _state_machine_instance is None:
        _state_machine_instance = DialogueStateMachine()
    return _state_machine_instance
