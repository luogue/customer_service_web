"""
对话管理器（模块化版本）
使用独立的处理器模块，保持原有逻辑不变
"""
import re
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from llm_adapter.intent_mock import intent_mock_service, IntentRecognitionResult
from dialogue_engine.intent_classifier import is_confirmed, is_rejected
from dialogue_engine.handlers import (
    get_order_query_handler,
    get_refund_handler,
    get_exchange_handler,
    get_transfer_human_handler,
    get_complaint_handler,
    get_modify_order_handler,
    get_task_router
)

logger = logging.getLogger(__name__)


class DialogueManager:
    """对话管理器 - 协调各个独立处理器"""
    
    WELCOME_MESSAGE = "您好，这里是AI客服，很高兴为您服务，请问有什么可以帮您？"
    GOODBYE_MESSAGE = "感谢您的咨询，祝您生活愉快！"
    
    def __init__(self, db: Session = None):
        self.db = db
        self.session_states: Dict[str, Dict[str, Any]] = {}
        
        # 初始化各个处理器
        self.order_query_handler = get_order_query_handler(db)
        self.refund_handler = get_refund_handler(db)
        self.exchange_handler = get_exchange_handler(db)
        self.transfer_handler = get_transfer_human_handler(db)
        self.complaint_handler = get_complaint_handler(db)
        self.modify_order_handler = get_modify_order_handler(db)
        self.task_router = get_task_router(db)
    
    def _is_order_number_selection(self, content: str) -> bool:
        """判断是否是订单编号选择"""
        return content.strip().isdigit()
    
    def _recognize_intent(self, user_id: str, phone: str, content: str) -> IntentRecognitionResult:
        """意图识别"""
        logger.info(f"调用意图识别服务: {content}")
        return intent_mock_service.recognize_intent(user_id, phone, content)
    
    def _generate_confirmation_message(self, intent_result: IntentRecognitionResult, phone: str) -> str:
        """生成确认消息"""
        intents = intent_result.intents
        if not intents:
            return "请问您需要什么帮助？"
        
        if len(intents) == 1:
            intent = intents[0]
            if intent.intent_type == "query_order":
                return f"您是想查询手机号{phone}下的订单信息，对吗？请回复\"是\"或\"不是\"。"
            elif intent.intent_type == "complaint":
                return "您是想投诉或其它售后问题，对吗？请回复\"是\"或\"不是\"。"
            else:
                return f"您是想{intent.description}，对吗？请回复\"是\"或\"不是\"。"
        else:
            intent_descriptions = [intent.description for intent in intents]
            descriptions = "、".join(intent_descriptions)
            return f"您是想{descriptions}，对吗？请回复\"是\"或\"不是\"。"
    
    def get_welcome_message(self) -> str:
        """获取首问语"""
        return self.WELCOME_MESSAGE
    
    def get_goodbye_message(self) -> str:
        """获取结束语"""
        return self.GOODBYE_MESSAGE
    
    def process_user_input(self, user_id: str, phone: str, content: str, 
                          session_id: str = None) -> Dict[str, Any]:
        """处理用户输入"""
        return self.process_message(user_id, phone, content, session_id)
    
    def process_message(self, user_id: str, phone: str, content: str, 
                       session_id: str = None) -> Dict[str, Any]:
        """处理用户消息 - 主入口"""
        responses = []
        
        # 初始化会话状态
        if session_id not in self.session_states:
            self.session_states[session_id] = {
                "step": "initial",
                "intent_result": None,
                "current_orders": [],
                "current_page": 1,
                "total_orders": 0,
                "selected_order": None,
                "current_intent": None,
                "phone": phone
            }
        
        session_state = self.session_states[session_id]
        session_state["phone"] = phone
        
        # 处理重置会话状态的特殊消息
        if content == '重置会话状态':
            # 重置会话状态
            session_state["step"] = "initial"
            session_state["intent_result"] = None
            session_state["current_orders"] = []
            session_state["current_page"] = 1
            session_state["total_orders"] = 0
            session_state["selected_order"] = None
            session_state["current_intent"] = None
            return {
                "success": True,
                "intent": None,
                "responses": ["会话状态已重置，恢复AI服务"],
                "final_response": "会话状态已重置，恢复AI服务",
                "session_state": session_state
            }
        
        # 根据当前步骤分发处理
        step_handlers = {
            "initial": self._handle_initial,
            "waiting_confirm": self._handle_waiting_confirm,
            "waiting_order_in_list": self._handle_waiting_order_in_list,
            "waiting_order_selection": self._handle_waiting_order_selection,
            "waiting_phone_confirmation": self._handle_waiting_phone_confirmation,
            "waiting_self_check": self._handle_waiting_self_check,
            "waiting_refund_order_selection": self._handle_waiting_refund_order_selection,
            "waiting_refund_confirm": self._handle_waiting_refund_confirm,
            "waiting_return_confirm": self._handle_waiting_return_confirm,
            "waiting_exchange_order_selection": self._handle_waiting_exchange_order_selection,
            "waiting_exchange_confirm": self._handle_waiting_exchange_confirm,
            "waiting_complaint_order_selection": self._handle_waiting_complaint_order_selection,
            "waiting_modify_order_selection": self._handle_waiting_modify_order_selection,
            "waiting_modify_content": self._handle_waiting_modify_content,
            "completed": self._handle_completed
        }
        
        handler = step_handlers.get(session_state["step"], self._handle_default)
        responses = handler(user_id, phone, content, session_id, session_state)
        
        return {
            "success": True,
            "intent": session_state.get("intent_result"),
            "responses": responses,
            "final_response": "\n".join(responses),
            "session_state": session_state
        }
    
    def _handle_initial(self, user_id: str, phone: str, content: str, 
                       session_id: str, state: Dict) -> List[str]:
        """处理初始状态"""
        intent_result = self._recognize_intent(user_id, phone, content)
        state["intent_result"] = intent_result
        logger.info(f"意图识别结果: {intent_result}")
        
        confirmation_msg = self._generate_confirmation_message(intent_result, phone)
        state["step"] = "waiting_confirm"
        return [confirmation_msg]
    
    def _handle_waiting_confirm(self, user_id: str, phone: str, content: str,
                                session_id: str, state: Dict) -> List[str]:
        """处理等待确认状态"""
        if is_confirmed(content):
            logger.info("用户确认，执行业务逻辑")
            state["step"] = "confirmed"
            return self._process_confirmed_intent(state, phone, session_id)
        
        elif is_rejected(content):
            logger.info("用户拒绝，重新询问")
            state["step"] = "initial"
            return ["抱歉，我理解错了。请问您具体需要什么帮助？"]
        
        else:
            logger.info("用户不直接回答，重新进行意图识别")
            new_intent_result = self._recognize_intent(user_id, phone, content)
            state["intent_result"] = new_intent_result
            return [self._generate_confirmation_message(new_intent_result, phone)]
    
    def _process_confirmed_intent(self, state: Dict, phone: str, session_id: str) -> List[str]:
        """处理已确认的意图"""
        intent_result = state.get("intent_result")
        if not intent_result or not intent_result.intents:
            return ["请问您需要什么帮助？"]
        
        intent = intent_result.intents[0]
        intent_type = intent.intent_type
        
        # 使用任务路由器处理
        result = self.task_router.route_by_intent(intent_type, phone, session_id, state)
        
        # 更新状态
        if "step" in result:
            state["step"] = result["step"]
        if "data" in result and result.get("action") == "show_orders":
            state["current_orders"] = result["data"].get("orders", [])
            state["current_page"] = result["data"].get("page", 1)
            state["total_orders"] = result["data"].get("total", 0)
        
        return [result["message"]]
    
    def _handle_waiting_order_in_list(self, user_id: str, phone: str, content: str,
                                      session_id: str, state: Dict) -> List[str]:
        """处理等待订单列表确认状态"""
        if self._is_order_number_selection(content):
            order_index = int(content.strip()) - 1
            current_orders = state.get("current_orders", [])
            
            if 0 <= order_index < len(current_orders):
                order = current_orders[order_index]
                order_detail = self.order_query_handler.get_order_detail(order)
                state["step"] = "order_selected"
                state["selected_order"] = order
                return [order_detail]
            else:
                return [f"请输入1-{len(current_orders)}之间的数字选择订单。"]
        
        elif is_confirmed(content):
            return ["请回复订单数字序号（1、2、3...）选择您要查看的订单。"]
        
        elif is_rejected(content):
            next_page = state.get("current_page", 1) + 1
            result = self.order_query_handler.query_orders(phone, next_page)
            
            if result["success"] and result["orders"]:
                state["current_orders"] = result["orders"]
                state["current_page"] = result["page"]
                state["total_orders"] = result["total"]
                order_list = self.order_query_handler.format_order_list(result["orders"])
                return [f"找到您的订单（第{result['page']}页，共{result['total']}个）：\n{order_list}\n\n请直接回复订单编号（1、2、3...）选择订单，或回复\"不是\"查看下一页。"]
            else:
                state["step"] = "waiting_self_check"
                return ["未查询到当前登录账号绑定手机号下的更多订单。\n\n请您先自查：\n1. 确认当前登录的手机号是否正确\n2. 如需查询其他手机号的订单，请切换对应账号登录后重试\n\n请问您是否已核对？回复\"是\"确认已核对，回复\"不是\"我再帮您查询。"]
        
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_order_selection(self, user_id: str, phone: str, content: str,
                                        session_id: str, state: Dict) -> List[str]:
        """处理等待订单选择状态"""
        if self._is_order_number_selection(content):
            order_index = int(content.strip()) - 1
            current_orders = state.get("current_orders", [])
            
            if 0 <= order_index < len(current_orders):
                order = current_orders[order_index]
                state["step"] = "order_selected"
                state["selected_order"] = order
                return [f"您选择的订单：{order['product_name']} - {order['order_number']} - {order['status_text']}\n请问您对这个订单有什么问题？"]
            else:
                return [f"请输入1-{len(current_orders)}之间的数字选择订单。"]
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_phone_confirmation(self, user_id: str, phone: str, content: str,
                                           session_id: str, state: Dict) -> List[str]:
        """处理等待手机号确认状态"""
        if is_confirmed(content):
            state["step"] = "completed"
            return ["已为您转接人工客服，请稍候。"]
        elif is_rejected(content):
            state["step"] = "initial"
            return ["为了您的账户安全，仅支持查询当前登录账号绑定的订单。\n\n如需查询其他手机号的订单，请先退出当前账号，使用其他手机号重新登录后再试。"]
        elif re.search(r'1[3-9]\d{9}', content):
            state["step"] = "initial"
            return ["为了您的账户安全，仅支持查询当前登录账号绑定的订单，如需查询其他手机号，请切换账号登录后重试。"]
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_self_check(self, user_id: str, phone: str, content: str,
                                   session_id: str, state: Dict) -> List[str]:
        """处理等待自查确认状态"""
        if is_confirmed(content):
            state["step"] = "completed"
            return ["已为您转接人工客服，请稍候。"]
        elif is_rejected(content):
            return ["好的，请您先核对：\n1. 当前登录的手机号是否正确\n2. 如需查询其他手机号的订单，请切换对应账号登录后重试\n\n核对完成后请回复\"是\"。"]
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_refund_order_selection(self, user_id: str, phone: str, content: str,
                                               session_id: str, state: Dict) -> List[str]:
        """处理等待退款订单选择状态"""
        if self._is_order_number_selection(content):
            order_index = int(content.strip()) - 1
            current_orders = state.get("current_orders", [])
            
            if 0 <= order_index < len(current_orders):
                order = current_orders[order_index]
                state["selected_order"] = order
                state["step"] = "waiting_refund_confirm"
                return [f"您选择的订单：{order['product_name']} - {order['order_number']}\n\n是否确认申请该订单退货退款？请回复\"是\"确认，回复\"不是\"取消。"]
            else:
                return [f"请输入1-{len(current_orders)}之间的数字选择订单。"]
        
        elif is_rejected(content):
            next_page = state.get("current_page", 1) + 1
            result = self.refund_handler.get_refundable_orders(phone, next_page)
            
            if result["success"] and result["orders"]:
                state["current_orders"] = result["orders"]
                state["current_page"] = result["page"]
                state["total_orders"] = result["total"]
                order_list = self.order_query_handler.format_order_list(result["orders"])
                return [f"请选择您要退货退款的订单：\n{order_list}\n\n请直接回复订单编号（1、2、3...）选择要退货退款的订单，或回复\"不是\"查看下一页。"]
            else:
                state["step"] = "initial"
                return [result["message"]]
        
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_refund_confirm(self, user_id: str, phone: str, content: str,
                                       session_id: str, state: Dict) -> List[str]:
        """处理等待退款确认状态"""
        if is_confirmed(content):
            state["step"] = "initial"
            return ["已提交系统审核，1个工作日内处理。\n\n请问还有其他可以帮您的吗？"]
        elif is_rejected(content):
            state["step"] = "initial"
            return ["已取消申请。\n\n请问还有其他可以帮您的吗？"]
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_return_confirm(self, user_id: str, phone: str, content: str,
                                       session_id: str, state: Dict) -> List[str]:
        """处理等待是否愿意退货状态"""
        if is_confirmed(content):
            result = self.refund_handler.get_refundable_orders(phone)
            
            if result["success"] and result["orders"]:
                state["current_orders"] = result["orders"]
                state["current_page"] = 1
                state["total_orders"] = result["total"]
                state["step"] = "waiting_refund_order_selection"
                order_list = self.order_query_handler.format_order_list(result["orders"])
                return [f"请选择您要退货退款的订单：\n{order_list}\n\n请直接回复订单编号（1、2、3...）选择要退货退款的订单，或回复\"不是\"查看下一页。"]
            else:
                state["step"] = "initial"
                return [result["message"]]
        
        elif is_rejected(content):
            state["step"] = "completed"
            return ["仅退款申请需要人工审核，已为您转接人工客服，请稍候。"]
        
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_exchange_order_selection(self, user_id: str, phone: str, content: str,
                                                 session_id: str, state: Dict) -> List[str]:
        """处理等待换货订单选择状态"""
        if self._is_order_number_selection(content):
            order_index = int(content.strip()) - 1
            current_orders = state.get("current_orders", [])
            
            if 0 <= order_index < len(current_orders):
                order = current_orders[order_index]
                state["selected_order"] = order
                state["step"] = "waiting_exchange_confirm"
                return [f"您选择的订单：{order['product_name']} - {order['order_number']}\n\n是否确认申请该订单换货？请回复\"是\"确认，回复\"不是\"取消。"]
            else:
                return [f"请输入1-{len(current_orders)}之间的数字选择订单。"]
        
        elif is_rejected(content):
            next_page = state.get("current_page", 1) + 1
            result = self.exchange_handler.get_exchangeable_orders(phone, next_page)
            
            if result["success"] and result["orders"]:
                state["current_orders"] = result["orders"]
                state["current_page"] = result["page"]
                state["total_orders"] = result["total"]
                order_list = self.order_query_handler.format_order_list(result["orders"])
                return [f"请选择您要换货的订单：\n{order_list}\n\n请直接回复订单编号（1、2、3...）选择要换货的订单，或回复\"不是\"查看下一页。"]
            else:
                state["step"] = "initial"
                return [result["message"]]
        
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_exchange_confirm(self, user_id: str, phone: str, content: str,
                                         session_id: str, state: Dict) -> List[str]:
        """处理等待换货确认状态"""
        if is_confirmed(content):
            state["step"] = "initial"
            return ["已为您提交换货申请，系统审核后将在1个工作日内告知您换货地址及流程。\n\n请问还有其他可以帮您的吗？"]
        elif is_rejected(content):
            state["step"] = "initial"
            return ["已取消您的换货申请，如有需要可再次发起。\n\n请问还有其他可以帮您的吗？"]
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_complaint_order_selection(self, user_id: str, phone: str, content: str,
                                                  session_id: str, state: Dict) -> List[str]:
        """处理等待投诉订单选择状态"""
        if content.strip() == "0":
            state["step"] = "completed"
            return [
                "很抱歉给您带来不好的体验，已为您记录问题并反馈。",
                "转接人工客服为您处理，请稍候。"
            ]
        
        elif self._is_order_number_selection(content):
            order_index = int(content.strip()) - 1
            current_orders = state.get("current_orders", [])
            
            if 0 <= order_index < len(current_orders):
                order = current_orders[order_index]
                state["selected_order"] = order
                state["step"] = "completed"
                return [
                    f"您选择的订单：{order['product_name']} - {order['order_number']}\n\n很抱歉给您带来不好的体验，已为您记录问题并反馈。",
                    "转接人工客服为您处理，请稍候。"
                ]
            else:
                return [f"请输入0-{len(current_orders)}之间的数字选择订单。"]
        
        elif is_rejected(content):
            next_page = state.get("current_page", 1) + 1
            result = self.complaint_handler.get_orders_for_complaint(phone, next_page)
            
            if result["success"] and result["orders"]:
                state["current_orders"] = result["orders"]
                state["current_page"] = result["page"]
                state["total_orders"] = result["total"]
                prompt = self.complaint_handler.get_complaint_prompt(result["orders"])
                return [prompt]
            else:
                state["step"] = "completed"
                return ["未查询到您的订单。\n\n很抱歉给您带来不好的体验，已为您记录问题并反馈。\n转接人工客服为您处理，请稍候。"]
        
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_modify_order_selection(self, user_id: str, phone: str, content: str,
                                               session_id: str, state: Dict) -> List[str]:
        """处理等待修改订单选择状态"""
        if self._is_order_number_selection(content):
            order_index = int(content.strip()) - 1
            current_orders = state.get("current_orders", [])
            
            if 0 <= order_index < len(current_orders):
                order = current_orders[order_index]
                state["selected_order"] = order
                
                modifiable = self.modify_order_handler.check_modifiable(order)
                if modifiable["modifiable"]:
                    state["step"] = "waiting_modify_content"
                    return [self.modify_order_handler.get_modify_prompt(order)]
                else:
                    state["step"] = "initial"
                    return [f"抱歉，订单{order['order_number']}已发货，无法修改地址或备注。如需帮助请联系人工客服。"]
            else:
                return [f"请输入1-{len(current_orders)}之间的数字选择订单。"]
        
        elif is_rejected(content):
            next_page = state.get("current_page", 1) + 1
            result = self.modify_order_handler.get_modifiable_orders(phone, next_page)
            
            if result["success"] and result["orders"]:
                state["current_orders"] = result["orders"]
                state["current_page"] = result["page"]
                state["total_orders"] = result["total"]
                order_list = self.order_query_handler.format_order_list(result["orders"])
                return [f"请选择您要修改的订单：\n{order_list}\n\n请直接回复订单编号（1、2、3...）选择要修改的订单，或回复\"不是\"查看下一页。"]
            else:
                state["step"] = "initial"
                return ["未查询到您的订单，无法修改地址。"]
        
        else:
            return self._re_recognize_intent(user_id, phone, content, state)
    
    def _handle_waiting_modify_content(self, user_id: str, phone: str, content: str,
                                       session_id: str, state: Dict) -> List[str]:
        """处理等待修改内容状态"""
        order = state.get("selected_order", {})
        modify_type = self.modify_order_handler.parse_modify_type(content)
        result = self.modify_order_handler.modify_order(order, modify_type, content)
        
        state["step"] = "initial"
        return [result["message"] + "\n\n请问还有其他可以帮您的吗？"]
    
    def _handle_completed(self, user_id: str, phone: str, content: str,
                         session_id: str, state: Dict) -> List[str]:
        """处理已完成状态"""
        return ["已为您转接人工客服，请稍候。"]
    
    def _handle_default(self, user_id: str, phone: str, content: str,
                       session_id: str, state: Dict) -> List[str]:
        """默认处理"""
        return self._re_recognize_intent(user_id, phone, content, state)
    
    def _re_recognize_intent(self, user_id: str, phone: str, content: str, state: Dict) -> List[str]:
        """重新识别意图"""
        logger.info("用户不直接回答，重新进行意图识别")
        new_intent_result = self._recognize_intent(user_id, phone, content)
        state["intent_result"] = new_intent_result
        state["step"] = "waiting_confirm"
        return [self._generate_confirmation_message(new_intent_result, phone)]


# 全局实例
_dialogue_manager_instance: Optional[DialogueManager] = None


def get_dialogue_manager(db: Session = None) -> DialogueManager:
    """获取对话管理器实例"""
    global _dialogue_manager_instance
    if _dialogue_manager_instance is None:
        _dialogue_manager_instance = DialogueManager(db)
    elif db:
        _dialogue_manager_instance.db = db
        _dialogue_manager_instance.order_query_handler = get_order_query_handler(db)
        _dialogue_manager_instance.refund_handler = get_refund_handler(db)
        _dialogue_manager_instance.exchange_handler = get_exchange_handler(db)
        _dialogue_manager_instance.transfer_handler = get_transfer_human_handler(db)
        _dialogue_manager_instance.complaint_handler = get_complaint_handler(db)
        _dialogue_manager_instance.modify_order_handler = get_modify_order_handler(db)
        _dialogue_manager_instance.task_router = get_task_router(db)
    return _dialogue_manager_instance
