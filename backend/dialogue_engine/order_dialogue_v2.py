"""
订单查询对话流程 V2
使用状态机管理对话流程
实现完整的五层调用顺序：
接入层 → 对话引擎层 → 大模型交互层 → 知识底座层 → 运维保障层
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from llm_adapter.intent_mock import intent_mock_service, IntentRecognitionResult
from knowledge_base.order_service import OrderService
from .intent_classifier import classify_intent, is_confirmed, is_rejected
from .dialogue_state_machine import DialogueStateMachine, DialogueNode, get_state_machine
from ops_monitor import logger


class OrderDialogueFlowV2:
    """订单查询对话流程 V2 - 使用状态机"""
    
    # 首问语
    WELCOME_MESSAGE = "您好，这里是AI客服，很高兴为您服务，请问有什么可以帮您？"
    
    # 结束语
    GOODBYE_MESSAGE = "感谢您的咨询，祝您生活愉快。再见！"
    
    def __init__(self, db: Session = None):
        self.db = db
        self.order_service = OrderService(db) if db else None
        self.state_machine = get_state_machine()
    
    def get_welcome_message(self) -> str:
        """获取首问语"""
        return self.WELCOME_MESSAGE
    
    def get_goodbye_message(self) -> str:
        """获取结束语"""
        return self.GOODBYE_MESSAGE
    
    def process_user_input(self, user_id: str, phone: str, content: str, 
                          session_id: str = None) -> Dict:
        """
        处理用户输入，使用状态机管理流程
        
        流程控制：
        1. 检查当前节点是否要求特定回复（是/否）
        2. 如果用户不按流程回复，打断当前流程，重新识别意图
        3. 如果用户按流程回复，继续原有流程
        
        Args:
            user_id: 用户ID
            phone: 用户手机号
            content: 用户输入内容
            session_id: 会话ID
            
        Returns:
            处理结果
        """
        logger.info(f"处理用户输入: user_id={user_id}, phone={phone}, content={content}")
        logger.info(f"当前状态机节点: {self.state_machine.get_current_node().name}")
        
        # 获取当前节点
        current_node = self.state_machine.get_current_node()
        
        # 如果已完成，不回复
        if current_node == DialogueNode.COMPLETED:
            logger.info("已转人工，不回复用户消息")
            return {
                "success": True,
                "intent": None,
                "responses": [],
                "final_response": "",
                "session_state": {"node": current_node.name}
            }
        
        # 判断用户回复类型
        response_type = self._classify_response(content)
        logger.info(f"用户回复类型: {response_type}")
        
        # 检查是否需要打断流程
        if self.state_machine.should_interrupt(response_type):
            logger.info("用户不按流程回复，打断当前流程，重新识别意图")
            return self._handle_interrupt(user_id, phone, content, session_id)
        
        # 按流程处理
        return self._handle_flow(user_id, phone, content, session_id, response_type)
    
    def _classify_response(self, content: str) -> str:
        """
        分类用户回复
        
        Returns:
            'confirm' - 确认/是
            'reject' - 拒绝/否
            'unknown' - 无法识别
        """
        if is_confirmed(content):
            return 'confirm'
        elif is_rejected(content):
            return 'reject'
        else:
            return 'unknown'
    
    def _handle_interrupt(self, user_id: str, phone: str, content: str, 
                         session_id: str) -> Dict:
        """
        处理流程打断
        
        当用户不按流程回复时，打断当前流程，重新识别意图
        """
        logger.info("处理流程打断")
        
        # 重置状态机到初始节点
        self.state_machine.reset()
        
        # 重新识别意图
        intent_result = self._recognize_intent(user_id, phone, content)
        logger.info(f"重新识别意图: {intent_result}")
        
        # 生成确认消息
        confirmation_msg = self._generate_confirmation_message(intent_result, phone)
        
        # 进入等待意图确认状态
        self.state_machine.set_node(DialogueNode.WAITING_INTENT_CONFIRM, {
            'intent_result': intent_result,
            'phone': phone,
            'user_id': user_id
        })
        
        return {
            "success": True,
            "intent": intent_result,
            "responses": [confirmation_msg],
            "final_response": confirmation_msg,
            "session_state": {"node": self.state_machine.get_current_node().name},
            "interrupted": True
        }
    
    def _handle_flow(self, user_id: str, phone: str, content: str, 
                    session_id: str, response_type: str) -> Dict:
        """
        按流程处理用户输入
        """
        current_node = self.state_machine.get_current_node()
        
        if current_node == DialogueNode.INITIAL:
            return self._handle_initial_node(user_id, phone, content, session_id)
        
        elif current_node == DialogueNode.WAITING_INTENT_CONFIRM:
            return self._handle_intent_confirm_node(user_id, phone, content, session_id, response_type)
        
        elif current_node == DialogueNode.WAITING_PHONE_CONFIRM:
            return self._handle_phone_confirm_node(user_id, phone, content, session_id, response_type)
        
        elif current_node == DialogueNode.PROCESSING_ORDER_QUERY:
            # 订单查询已处理完成，进入初始状态处理新输入
            return self._handle_initial_node(user_id, phone, content, session_id)
        
        else:
            logger.warning(f"未知节点: {current_node}")
            return self._handle_initial_node(user_id, phone, content, session_id)
    
    def _handle_initial_node(self, user_id: str, phone: str, content: str, 
                            session_id: str) -> Dict:
        """处理初始节点"""
        logger.info("处理初始节点")
        
        # 意图识别（大模型交互层 - Mock）
        intent_result = self._recognize_intent(user_id, phone, content)
        logger.info(f"意图识别结果: {intent_result}")
        
        # 生成确认消息
        confirmation_msg = self._generate_confirmation_message(intent_result, phone)
        
        # 进入等待意图确认状态
        self.state_machine.set_node(DialogueNode.WAITING_INTENT_CONFIRM, {
            'intent_result': intent_result,
            'phone': phone,
            'user_id': user_id
        })
        
        return {
            "success": True,
            "intent": intent_result,
            "responses": [confirmation_msg],
            "final_response": confirmation_msg,
            "session_state": {"node": self.state_machine.get_current_node().name}
        }
    
    def _handle_intent_confirm_node(self, user_id: str, phone: str, content: str, 
                                   session_id: str, response_type: str) -> Dict:
        """处理意图确认节点"""
        logger.info(f"处理意图确认节点，回复类型: {response_type}")
        
        intent_result = self.state_machine.get_context('intent_result')
        
        if response_type == 'confirm':
            # 用户确认，处理业务逻辑
            logger.info("用户确认意图")
            self.state_machine.set_node(DialogueNode.PROCESSING_ORDER_QUERY)
            responses = self._process_business_logic(intent_result, phone, session_id)
            
            return {
                "success": True,
                "intent": intent_result,
                "responses": responses,
                "final_response": "\n".join(responses),
                "session_state": {"node": self.state_machine.get_current_node().name}
            }
        
        elif response_type == 'reject':
            # 用户拒绝，回到初始状态
            logger.info("用户拒绝意图")
            self.state_machine.set_node(DialogueNode.INITIAL)
            response = "抱歉，我理解错了。请问您具体需要什么帮助？"
            
            return {
                "success": True,
                "intent": None,
                "responses": [response],
                "final_response": response,
                "session_state": {"node": self.state_machine.get_current_node().name}
            }
        
        else:
            # 无法识别（理论上不会到这里，因为已经检查过）
            logger.warning("在意图确认节点收到无法识别的回复")
            response = "抱歉，我没有理解您的意思。请回复\"是\"或\"不是\"。"
            
            return {
                "success": True,
                "intent": intent_result,
                "responses": [response],
                "final_response": response,
                "session_state": {"node": self.state_machine.get_current_node().name}
            }
    
    def _handle_phone_confirm_node(self, user_id: str, phone: str, content: str, 
                                  session_id: str, response_type: str) -> Dict:
        """处理手机号确认节点"""
        logger.info(f"处理手机号确认节点，回复类型: {response_type}")
        
        if response_type == 'confirm':
            # 用户确认是这个手机号，转人工
            logger.info("用户确认是这个手机号，转人工")
            self.state_machine.set_node(DialogueNode.COMPLETED)
            response = "已为您转接人工客服，请稍候。"
            
            return {
                "success": True,
                "intent": None,
                "responses": [response],
                "final_response": response,
                "session_state": {"node": self.state_machine.get_current_node().name}
            }
        
        elif response_type == 'reject':
            # 用户否认是这个手机号，提示切换账号
            logger.info("用户否认是这个手机号")
            self.state_machine.set_node(DialogueNode.INITIAL)
            response = "为了您的账户安全，仅支持查询当前登录账号绑定的订单，如需查询其他手机号，请切换账号登录后重试。"
            
            return {
                "success": True,
                "intent": None,
                "responses": [response],
                "final_response": response,
                "session_state": {"node": self.state_machine.get_current_node().name}
            }
        
        else:
            # 无法识别（理论上不会到这里）
            logger.warning("在手机确认节点收到无法识别的回复")
            response = "抱歉，我没有理解您的意思。请回答是或不是。"
            
            return {
                "success": True,
                "intent": None,
                "responses": [response],
                "final_response": response,
                "session_state": {"node": self.state_machine.get_current_node().name}
            }
    
    def _generate_confirmation_message(self, intent_result: IntentRecognitionResult, 
                                     phone: str) -> str:
        """生成确认消息"""
        intents = intent_result.intents
        if not intents:
            return "请问您需要什么帮助？"
        
        if len(intents) == 1:
            intent = intents[0]
            if intent.intent_type == "query_order":
                return f"您是想查询手机号{phone}下的订单信息，对吗？请回复\"是\"或\"不是\"。"
            else:
                return f"您是想{intent.description}，对吗？请回复\"是\"或\"不是\"。"
        else:
            intent_descriptions = [intent.description for intent in intents]
            descriptions = "、".join(intent_descriptions)
            return f"您是想{descriptions}，对吗？请回复\"是\"或\"不是\"。"
    
    def _process_business_logic(self, intent_result: IntentRecognitionResult, 
                              phone: str, session_id: str = None) -> List[str]:
        """处理业务逻辑"""
        responses = []
        
        for intent in intent_result.intents:
            logger.info(f"处理意图: {intent.intent_type}")
            
            if intent.intent_type == "query_order":
                logger.info(f"开始查询订单，手机号: {phone}")
                order_response = self._handle_order_query(phone)
                logger.info(f"订单查询结果: {order_response}")
                
                if order_response["type"] == "no_order":
                    # 未找到订单，进入手机号确认状态
                    self.state_machine.set_node(DialogueNode.WAITING_PHONE_CONFIRM, {
                        'last_phone': phone
                    })
                    responses.append(f"经核实，手机号{phone}下没有订单。请问是这个手机号下的订单吗？请回答是或不是。")
                    logger.info("未找到订单，进入手机号确认状态")
                    break
                else:
                    responses.append(order_response["message"])
                    self.state_machine.set_node(DialogueNode.INITIAL)
                    
            elif intent.intent_type == "query_promotion":
                logger.info("处理优惠查询意图")
                responses.append("目前我们有满199减20的活动，还有新人专享优惠券可以领取哦！")
                self.state_machine.set_node(DialogueNode.INITIAL)
                
            else:
                logger.info(f"处理其他意图: {intent.intent_type}")
                responses.append(f"我理解您想要{intent.description}，这个功能正在开发中，敬请期待！")
                self.state_machine.set_node(DialogueNode.INITIAL)
        
        return responses
    
    def _recognize_intent(self, user_id: str, phone: str, content: str) -> IntentRecognitionResult:
        """意图识别（大模型交互层）"""
        logger.info(f"调用意图识别服务: {content}")
        return intent_mock_service.recognize_intent(user_id, phone, content)
    
    def _handle_order_query(self, phone: str) -> Dict:
        """处理订单查询（知识底座层）"""
        logger.info(f"查询订单: phone={phone}")
        
        if not self.order_service:
            logger.info("订单服务不可用")
            return {
                "type": "error",
                "message": "抱歉，订单查询服务暂时不可用。"
            }
        
        try:
            orders = self.order_service.get_orders_by_phone(phone)
            logger.info(f"查询到订单数量: {len(orders)}")
            
            if not orders:
                logger.info(f"未找到订单: {phone}")
                return {
                    "type": "no_order",
                    "message": f"经核实，手机号{phone}下没有订单。",
                    "phone": phone
                }
            
            response = self.order_service.generate_order_response(orders)
            logger.info(f"生成订单回复: {response}")
            return {
                "type": "success",
                "message": response
            }
            
        except Exception as e:
            logger.error(f"查询订单失败: {e}")
            return {
                "type": "error",
                "message": "查询订单时出现错误，请稍后再试。"
            }


# 全局实例
_dialogue_flow_v2_instance = None


def get_order_dialogue_flow_v2(db: Session = None) -> OrderDialogueFlowV2:
    """获取订单对话流程实例 V2（单例模式）"""
    global _dialogue_flow_v2_instance
    if _dialogue_flow_v2_instance is None:
        _dialogue_flow_v2_instance = OrderDialogueFlowV2(db)
    elif db:
        _dialogue_flow_v2_instance.db = db
        _dialogue_flow_v2_instance.order_service = OrderService(db) if db else None
    return _dialogue_flow_v2_instance
