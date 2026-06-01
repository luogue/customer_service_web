"""
订单对话流程管理
"""
import re
import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from sqlalchemy.orm import Session

from llm_adapter.intent_mock import intent_mock_service, IntentRecognitionResult
from knowledge_base.order_service import OrderService
from knowledge_base.models import OrderStatus
from datetime import datetime, timedelta
from security.security_service import security_service
from logs.log_collector import get_log_collector, record_log
from tracing.trace_manager import get_trace_manager

# 导入插件系统
from plugins.plugin_manager import get_plugin_result

# 导入会话管理器
from dialogue_engine.session_manager import SessionManager

logger = logging.getLogger(__name__)

# 辅助函数
def is_confirmed(content: str) -> bool:
    """判断用户是否确认"""
    confirm_keywords = ["是", "对", "是的", "对的", "确认", "好的", "ok", "okay", "yes"]
    content_lower = content.lower().strip()
    # 精确匹配，避免"不是"被误识别为"是"
    return any(keyword == content_lower or keyword in content_lower.split() for keyword in confirm_keywords)

def is_rejected(content: str) -> bool:
    """判断用户是否拒绝"""
    reject_keywords = ["不是", "不对", "错", "错误", "不行", "不要", "no", "nope"]
    content_lower = content.lower().strip()
    return any(keyword in content_lower for keyword in reject_keywords)

def is_transfer(content: str) -> bool:
    """判断用户是否要求转人工"""
    transfer_keywords = [
        "人工", "转人工", "人工客服", "客服", "人工服务",
        "找人工", "我要人工", "联系人工", "转接人工", "转客服",
        "投诉", "强烈不满", "无法解决", "解决不了", "需要人工"
    ]
    content_lower = content.lower().strip()
    return any(keyword in content_lower for keyword in transfer_keywords)

class OrderDialogueFlow:
    """订单对话流程管理"""
    
    # 常量
    WELCOME_MESSAGE = "您好，这里是AI客服，很高兴为您服务，请问有什么可以帮您？"
    GOODBYE_MESSAGE = "感谢您的咨询，祝您生活愉快！"
    
    def __init__(self, db: Session = None):
        """初始化"""
        self.db = db
        self.order_service = OrderService(db) if db else None
        self.session_states: Dict[str, Dict[str, Any]] = {}
    
    def _is_order_number_selection(self, content: str) -> bool:
        """判断是否是订单编号选择"""
        return content.strip().isdigit()
    
    def _get_exchangeable_orders(self, phone: str) -> List[Dict]:
        """
        获取可换货的订单
        规则：仅支持「已付款/已发货/已签收」状态的订单，且已签收订单需在签收后7天内
        """
        if not self.order_service:
            return []
        
        # 获取所有订单
        all_orders = self.order_service.get_orders_by_phone(phone, limit=100)
        exchangeable_orders = []
        
        for order in all_orders:
            status = order.get('status', '')
            
            # 已付款/已发货状态的订单可以直接换货
            if status in [OrderStatus.PAID.value, OrderStatus.SHIPPED.value]:
                exchangeable_orders.append(order)
            # 已签收状态的订单需要检查是否在7天内
            elif status == OrderStatus.DELIVERED.value:
                # 检查签收时间（使用updated_at作为签收时间）
                delivered_time_str = order.get('updated_at', '')
                if delivered_time_str:
                    try:
                        # 解析时间字符串
                        if isinstance(delivered_time_str, str):
                            delivered_time = datetime.fromisoformat(delivered_time_str.replace('Z', '+00:00'))
                        else:
                            delivered_time = delivered_time_str
                        
                        # 计算是否超过7天
                        days_since_delivered = (datetime.now() - delivered_time.replace(tzinfo=None)).days
                        if days_since_delivered <= 7:
                            exchangeable_orders.append(order)
                    except Exception as e:
                        logger.error(f"解析签收时间失败: {e}")
                        # 如果时间解析失败，默认允许换货
                        exchangeable_orders.append(order)
                else:
                    # 没有时间信息，默认允许换货
                    exchangeable_orders.append(order)
        
        # 只返回前5个
        return exchangeable_orders[:5]
    
    def _get_all_orders(self, phone: str) -> List[Dict]:
        """
        获取用户的所有订单
        """
        if not self.order_service:
            return []
        
        # 获取所有订单
        all_orders = self.order_service.get_orders_by_phone(phone, limit=100)
        
        return all_orders[:10]
    
    def _get_refundable_orders(self, phone: str) -> List[Dict]:
        """
        获取可退货退款的订单
        规则：仅支持「已付款/已发货/已签收」状态的订单，且已签收订单需在签收后7天内
        """
        if not self.order_service:
            return []
        
        # 获取所有订单
        all_orders = self.order_service.get_orders_by_phone(phone, limit=100)
        refundable_orders = []
        
        for order in all_orders:
            status = order.get('status', '')
            
            # 已付款/已发货状态的订单可以直接退货退款
            if status in [OrderStatus.PAID.value, OrderStatus.SHIPPED.value]:
                refundable_orders.append(order)
            # 已签收状态的订单需要检查是否在7天内
            elif status == OrderStatus.DELIVERED.value:
                # 检查签收时间（使用updated_at作为签收时间）
                delivered_time_str = order.get('updated_at', '')
                if delivered_time_str:
                    try:
                        # 解析时间字符串
                        if isinstance(delivered_time_str, str):
                            delivered_time = datetime.fromisoformat(delivered_time_str.replace('Z', '+00:00'))
                        else:
                            delivered_time = delivered_time_str
                        
                        # 计算是否超过7天
                        days_since_delivered = (datetime.now() - delivered_time.replace(tzinfo=None)).days
                        if days_since_delivered <= 7:
                            refundable_orders.append(order)
                    except Exception as e:
                        logger.error(f"解析签收时间失败: {e}")
                        # 如果时间解析失败，默认允许退货退款
                        refundable_orders.append(order)
                else:
                    # 没有时间信息，默认允许退货退款
                    refundable_orders.append(order)
        
        # 只返回前5个
        return refundable_orders[:5]
    
    def _get_order_detail(self, order: Dict) -> str:
        """获取订单详细信息"""
        return f"订单详情：\n商品：{order['product_name']}\n订单号：{order['order_number']}\n金额：¥{order['total_amount']}\n状态：{order['status_text']}\n下单时间：{order['created_at']}\n{order.get('logistics_info', '')}"
    
    def _query_orders_with_pagination(self, phone: str, session_id: str, page: int, current_step: str = None) -> List[str]:
        """分页查询订单"""
        responses = []
        
        try:
            # 如果是换货流程，使用可换货订单查询
            if current_step == "waiting_exchange_order_selection":
                all_exchangeable_orders = self._get_exchangeable_orders(phone)
                total_count = len(all_exchangeable_orders)
                # 分页
                start_idx = (page - 1) * 5
                end_idx = start_idx + 5
                orders = all_exchangeable_orders[start_idx:end_idx] if start_idx < len(all_exchangeable_orders) else []
            # 如果是退款流程，使用可退货退款订单查询
            elif current_step == "waiting_refund_order_selection":
                all_refundable_orders = self._get_refundable_orders(phone)
                total_count = len(all_refundable_orders)
                # 分页
                start_idx = (page - 1) * 5
                end_idx = start_idx + 5
                orders = all_refundable_orders[start_idx:end_idx] if start_idx < len(all_refundable_orders) else []
            elif self.order_service:
                orders = self.order_service.get_orders_by_phone(phone, limit=5, offset=(page-1)*5)
                total_count = self.order_service.get_total_orders_count(phone)
            else:
                # 模拟数据
                orders = []
                total_count = 0
            
            if not orders:
                if page > 1:
                    # 没有更多订单了，引导用户自查
                    self.session_states[session_id]["step"] = "waiting_self_check"
                    responses.append("未查询到当前登录账号绑定手机号下的更多订单。\n\n请您先自查：\n1. 确认当前登录的手机号是否正确\n2. 如需查询其他手机号的订单，请切换对应账号登录后重试\n\n请问您是否已核对？回复\"是\"确认已核对，回复\"不是\"我再帮您查询。")
                    return responses
                else:
                    # 第一页就没有订单，引导用户自查
                    self.session_states[session_id]["step"] = "waiting_self_check"
                    responses.append("未查询到当前登录账号绑定手机号下的任何订单。\n\n请您先自查：\n1. 确认当前登录的手机号是否正确\n2. 如需查询其他手机号的订单，请切换对应账号登录后重试\n\n请问您是否已核对？回复\"是\"确认已核对，回复\"不是\"我再帮您查询。")
                    return responses
            
            # 保存当前订单列表到会话状态
            self.session_states[session_id]["current_orders"] = orders
            self.session_states[session_id]["current_page"] = page
            self.session_states[session_id]["total_orders"] = total_count
            self.session_states[session_id]["phone"] = phone
            
            # 生成订单列表回复
            order_info = "\n".join([
                f"{i+1}. {order['product_name']} - {order['order_number']} - {order['status_text']}"
                for i, order in enumerate(orders)
            ])
            
            has_more = total_count > page * 5
            
            responses.append(f"找到您的订单（第{page}页，共{total_count}个）：\n{order_info}")
            
            # 根据当前步骤设置相应的提示信息和状态
            if current_step == "waiting_refund_order_selection":
                responses.append("\n请直接回复订单编号（1、2、3...）选择要退款的订单，或回复\"不是\"查看下一页。")
                self.session_states[session_id]["step"] = "waiting_refund_order_selection"
            elif current_step == "waiting_exchange_order_selection":
                responses.append("\n请直接回复订单编号（1、2、3...）选择要换货的订单，或回复\"不是\"查看下一页。")
                self.session_states[session_id]["step"] = "waiting_exchange_order_selection"
            elif current_step == "waiting_modify_order_selection":
                responses.append("\n请直接回复订单编号（1、2、3...）选择要修改的订单，或回复\"不是\"查看下一页。")
                self.session_states[session_id]["step"] = "waiting_modify_order_selection"
            elif current_step == "waiting_complaint_order_selection":
                responses.append("\n0. 不选择订单\n\n请直接回复订单编号（1、2、3...）选择订单，回复\"0\"不选择订单，或回复\"不是\"查看下一页。")
                self.session_states[session_id]["step"] = "waiting_complaint_order_selection"
            else:
                # 默认查询订单流程
                responses.append("\n请直接回复订单编号（1、2、3...）选择订单，或回复\"不是\"查看下一页。")
                self.session_states[session_id]["step"] = "waiting_order_in_list"
            
        except Exception as e:
            logger.error(f"查询订单失败: {e}")
            responses.append("查询订单时出现错误，请稍后再试。")
        
        return responses
    
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
            elif intent.intent_type == "complaint":
                return "您是想投诉或其它售后问题，对吗？请回复\"是\"或\"不是\"。"
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
        
        # 获取用户输入内容
        content = intent_result.content
        
        # 意图映射：将现有意图类型映射到插件系统的意图关键词
        intent_mapping = {
            "query_order": "order_query",
            "refund_return": "refund",
            "exchange": "after_sales",
            "modify_address": "modify_info",
            "complaint": "complaint",
            "query_promotion": "promotion",
            "cancel_order": "cancel_order",
            "urgent_delivery": "remind_delivery",
            "question_consult": "consultation"
        }
        
        for intent in intent_result.intents:
            logger.info(f"处理意图: {intent.intent_type}")
            
            # 映射到插件系统的意图关键词
            plugin_intent = intent_mapping.get(intent.intent_type, "chat")
            logger.info(f"映射到插件意图: {plugin_intent}")
            
            # 提取参数
            params = {
                "phone": phone
            }
            
            # 根据意图类型提取特定参数
            if plugin_intent == "order_query":
                # 提取订单号（如果有）
                order_id = self._extract_order_id(content)
                if order_id:
                    params["order_id"] = order_id
            elif plugin_intent == "refund":
                # 提取订单号和退款原因
                order_id = self._extract_order_id(content)
                if order_id:
                    params["order_id"] = order_id
                params["reason"] = content
            elif plugin_intent == "after_sales":
                # 提取订单号和问题描述
                order_id = self._extract_order_id(content)
                if order_id:
                    params["order_id"] = order_id
                params["issue_type"] = "换货" if intent.intent_type == "exchange" else "维修"
                params["description"] = content
            elif plugin_intent == "modify_info":
                # 提取信息类型和新值
                params["info_type"] = "address" if intent.intent_type == "modify_address" else "other"
                params["new_value"] = content
            elif plugin_intent == "complaint":
                # 提取投诉主题和内容
                params["subject"] = intent.description
                params["content"] = content
                # 提取订单号（如果有）
                order_id = self._extract_order_id(content)
                if order_id:
                    params["order_id"] = order_id
            elif plugin_intent == "promotion":
                # 提取优惠类型
                if "优惠券" in content:
                    params["promotion_type"] = "coupon"
                else:
                    params["promotion_type"] = "activity"
            elif plugin_intent == "cancel_order":
                # 提取订单号和取消原因
                order_id = self._extract_order_id(content)
                if order_id:
                    params["order_id"] = order_id
                params["reason"] = content
            elif plugin_intent == "remind_delivery":
                # 提取订单号和催单类型
                order_id = self._extract_order_id(content)
                if order_id:
                    params["order_id"] = order_id
                if "物流" in content:
                    params["type"] = "logistics"
                else:
                    params["type"] = "delivery"
            elif plugin_intent == "consultation":
                # 提取问题内容和分类
                params["question"] = content
                if "下单" in content:
                    params["category"] = "order"
                elif "发票" in content:
                    params["category"] = "invoice"
                else:
                    params["category"] = "general"
            elif plugin_intent == "chat":
                # 闲聊互动
                params["content"] = content
            
            # 退款意图特殊处理 - 不走插件，走对话流程
            if plugin_intent == "refund":
                # 询问用户是否愿意退货
                responses.append("请问您是否愿意退货？请回复\"是\"愿意退货，回复\"不是\"不愿意退货。")
                self.session_states[session_id]["step"] = "waiting_return_confirm"
                self.session_states[session_id]["phone"] = phone
                return responses
            
            # 换货意图特殊处理 - 不走插件，走对话流程
            if plugin_intent == "after_sales" and intent.intent_type == "exchange":
                # 查询可换货的订单
                all_exchangeable_orders = self._get_exchangeable_orders(phone)
                if not all_exchangeable_orders:
                    responses.append("未查询到符合换货条件的订单。\n\n请问还有其他可以帮您的吗？")
                    return responses
                
                self.session_states[session_id]["current_orders"] = all_exchangeable_orders
                self.session_states[session_id]["current_page"] = 1
                self.session_states[session_id]["total_orders"] = len(all_exchangeable_orders)
                self.session_states[session_id]["phone"] = phone
                
                order_info = "\n".join([
                    f"{i+1}. {order.get('product_name', '商品')} - {order.get('order_number', '订单号')} - {order.get('status_text', '状态')}"
                    for i, order in enumerate(all_exchangeable_orders[:5])
                ])
                responses.append(f"请选择您要换货的订单：\n{order_info}\n\n请直接回复订单编号（1、2、3...）选择要换货的订单，或回复\"不是\"查看下一页。")
                self.session_states[session_id]["step"] = "waiting_exchange_order_selection"
                return responses
            
            # 投诉意图特殊处理 - 不走插件，走对话流程
            if plugin_intent == "complaint":
                # 询问用户投诉的具体内容
                responses.append("请问您要投诉的具体内容是什么？请详细描述一下。")
                self.session_states[session_id]["step"] = "waiting_complaint_content"
                self.session_states[session_id]["phone"] = phone
                return responses
            
            # 订单查询意图特殊处理 - 不走插件，先查询订单列表
            if plugin_intent == "order_query":
                # 查询用户的订单
                all_orders = self._get_all_orders(phone)
                if not all_orders:
                    responses.append("未查询到您的订单。\n\n请问还有其他可以帮您的吗？")
                    return responses
                
                self.session_states[session_id]["current_orders"] = all_orders
                self.session_states[session_id]["current_page"] = 1
                self.session_states[session_id]["total_orders"] = len(all_orders)
                self.session_states[session_id]["phone"] = phone
                
                order_info = "\n".join([
                    f"{i+1}. {order.get('product_name', '商品')} - {order.get('order_number', '订单号')} - {order.get('status_text', '状态')}"
                    for i, order in enumerate(all_orders[:5])
                ])
                responses.append(f"请选择您要查看的订单：\n{order_info}\n\n请直接回复订单编号（1、2、3...）选择要查看的订单，或回复\"不是\"查看下一页。")
                self.session_states[session_id]["step"] = "waiting_order_in_list"
                return responses
            
            # 调用插件处理业务逻辑
            logger.info(f"调用插件: {plugin_intent}, 参数: {params}")
            plugin_result = get_plugin_result(plugin_intent, params)
            
            # 处理插件返回结果
            if plugin_result["code"] == 200:
                # 插件执行成功
                logger.info(f"插件执行成功: {plugin_result['msg']}")
                
                # 根据插件类型处理返回数据
                if plugin_intent == "order_query" and plugin_result["data"]:
                    # 订单查询特殊处理，保持原有流程
                    orders = [plugin_result["data"]] if isinstance(plugin_result["data"], dict) else plugin_result["data"].get("orders", [])
                    if orders:
                        self.session_states[session_id]["current_orders"] = orders
                        self.session_states[session_id]["current_page"] = 1
                        self.session_states[session_id]["total_orders"] = len(orders)
                        self.session_states[session_id]["phone"] = phone
                        order_info = "\n".join([
                            f"{i+1}. {order.get('product_name', '商品')} - {order.get('order_id', order.get('order_number', '订单号'))} - {order.get('status_text', '状态')}"
                            for i, order in enumerate(orders)
                        ])
                        responses.append(f"请选择您要查看的订单：\n{order_info}\n\n请直接回复订单编号（1、2、3...）选择要查看的订单，或回复\"不是\"查看下一页。")
                        self.session_states[session_id]["step"] = "waiting_order_in_list"
                    else:
                        responses.append("未查询到您的订单。")
                else:
                    # 其他插件直接返回结果
                    responses.append(plugin_result["msg"])
                    if plugin_result["data"]:
                        # 根据数据类型格式化输出
                        if isinstance(plugin_result["data"], dict):
                            if "response" in plugin_result["data"]:
                                responses.append(plugin_result["data"]["response"])
                            elif "message" in plugin_result["data"]:
                                responses.append(plugin_result["data"]["message"])
                            elif "answer" in plugin_result["data"]:
                                responses.append(plugin_result["data"]["answer"])
                            elif "promotions" in plugin_result["data"]:
                                # 格式化优惠活动信息
                                promotions = plugin_result["data"]["promotions"]
                                if promotions:
                                    promo_msg = "当前可用的优惠活动：\n"
                                    for promo in promotions:
                                        promo_msg += f"- {promo.get('promotion_name', promo.get('coupon_code', '未知活动'))}"
                                        if "discount" in promo:
                                            promo_msg += f"：{promo['discount']}"
                                        elif "value" in promo:
                                            promo_msg += f"：满{promo.get('min_spend', 0)}减{promo['value']}"
                                        promo_msg += f"（有效期至：{promo.get('expiry_date', '未知')}）\n"
                                    responses.append(promo_msg.strip())
                                else:
                                    responses.append("暂无可用的优惠活动")
            else:
                # 插件执行失败
                logger.error(f"插件执行失败: {plugin_result['msg']}")
                responses.append(f"处理失败: {plugin_result['msg']}")
            
            break
        
        return responses
    
    def _extract_order_id(self, content: str) -> Optional[str]:
        """
        从用户输入中提取订单号
        
        Args:
            content: 用户输入内容
            
        Returns:
            提取的订单号，若没有则返回None
        """
        # 匹配常见的订单号格式
        order_id_patterns = [
            r'\b\d{12,16}\b',  # 12-16位数字
            r'\b[A-Za-z0-9]{10,20}\b',  # 10-20位字母数字组合
        ]
        
        for pattern in order_id_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(0)
        
        return None
    
    def _recognize_intent(self, user_id: str, phone: str, content: str, trace_id: Optional[str] = None) -> IntentRecognitionResult:
        """意图识别（大模型交互层）"""
        # 获取trace对象
        trace_manager = get_trace_manager()
        trace = trace_manager.get_trace(trace_id) if trace_id else None
        
        # 添加意图识别span
        if trace:
            intent_span = trace.add_span("intent_recognition", "recognize_intent")
            intent_span.attributes["user_id"] = user_id
            intent_span.attributes["content"] = content
        
        logger.info(f"调用意图识别服务: {content}")
        result = intent_mock_service.recognize_intent(user_id, phone, content)
        
        # 结束意图识别span
        if trace:
            intent_span.finish("success")
            intent_span.attributes["result"] = str(result)
        
        return result
    
    def _confirm_intent(self, intent_result: IntentRecognitionResult) -> str:
        """确认意图"""
        return intent_mock_service.get_confirmation_message(intent_result.intents)
    
    def end_conversation(self) -> str:
        """结束对话"""
        return self.GOODBYE_MESSAGE
    
    def get_welcome_message(self) -> str:
        """获取首问语"""
        return self.WELCOME_MESSAGE
    
    def get_goodbye_message(self) -> str:
        """获取结束语"""
        return self.GOODBYE_MESSAGE
    
    def process_user_input(self, user_id: str, phone: str, content: str, 
                       session_id: str = None, trace_id: Optional[str] = None) -> Dict[str, Any]:
        """处理用户输入（兼容旧接口）"""
        return self.process_message(user_id, phone, content, session_id, trace_id)
    
    def process_message(self, user_id: str, phone: str, content: str, 
                       session_id: str = None, trace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            user_id: 用户ID
            phone: 手机号
            content: 用户消息内容
            session_id: 会话ID
            trace_id: 追踪ID
            
        Returns:
            处理结果，包含会话是否过期的信息
        """
        # 检查会话是否过期（只有在会话已经存在的情况下才检查）
        if session_id:
            # 检查会话是否存在
            session_file = SessionManager.get_session_file(user_id, session_id)
            if os.path.exists(session_file):
                is_valid = SessionManager.check_session_expiry(user_id, session_id)
                if not is_valid:
                    logger.info(f"会话 {session_id} 已过期")
                    return {
                        "success": False,
                        "error": "session_expired",
                        "message": "会话已过期，请重新开始"
                    }
        
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
                "failed_attempts": 0,  # 连续意图识别失败次数
                "log_id": None  # 合规日志ID
            }
        
        session_state = self.session_states[session_id]
        
        # 更新会话最后活跃时间
        if session_id:
            SessionManager.update_last_active_time(user_id, session_id)
        
        # 获取最近的对话上下文
        recent_context = SessionManager.get_recent_context(user_id, session_id)
        logger.info(f"获取到的最近上下文: {len(recent_context)}轮")
        
        # 安全与合规检查
        security_result = security_service.process_user_input(user_id, phone, content, session_id)
        if not security_result["valid"]:
            # 安全检查失败，返回错误响应
            session_state["log_id"] = security_result["log_id"]
            # 记录敏感词拦截日志
            record_log(
                user_id=user_id,
                operation="security_check",
                status="failure",
                duration=0,
                content=content,
                error=security_result["error"]
            )
            return {
                "responses": [security_result["error"]],
                "session_id": session_id,
                "status": "error"
            }
        
        # 更新会话状态中的日志ID
        session_state["log_id"] = security_result["log_id"]
        # 使用清理后的输入
        content = security_result["sanitized_input"]
        
        # 处理不同步骤
        if session_state["step"] == "initial":
            # 第一步：意图识别
            intent_result = self._recognize_intent(user_id, phone, content, trace_id)
            session_state["intent_result"] = intent_result
            logger.info(f"意图识别结果: {intent_result}")
            
            # 记录意图识别日志
            intent_types = [i.intent_type for i in intent_result.intents]
            record_log(
                user_id=user_id,
                operation="intent_recognition",
                status="success",
                duration=0,
                content=content,
                metadata={"intents": intent_types}
            )
            
            # 生成确认消息
            confirmation_msg = self._generate_confirmation_message(intent_result, phone)
            responses.append(confirmation_msg)
            session_state["step"] = "waiting_confirm"
            logger.info(f"进入等待确认状态")
        
        elif session_state["step"] == "waiting_confirm":
            # 处理用户的确认/拒绝
            logger.info(f"处理用户确认/拒绝: {content}")
            
            if is_confirmed(content):
                logger.info("用户确认，执行业务逻辑")
                # 重置失败次数
                session_state["failed_attempts"] = 0
                session_state["step"] = "confirmed"
                responses = self._process_business_logic(session_state["intent_result"], phone, session_id)
            
            elif is_rejected(content):
                logger.info("用户拒绝，重新询问")
                # 增加失败次数
                session_state["failed_attempts"] += 1
                logger.info(f"意图识别失败次数: {session_state['failed_attempts']}")
                
                # 检查是否达到3次失败
                if session_state["failed_attempts"] >= 3:
                    logger.info("连续3次意图识别失败，触发转人工流程")
                    session_state["step"] = "completed"
                    session_state["failed_attempts"] = 0  # 重置失败次数
                    responses.append("很抱歉，我无法理解您的需求。已为您转接人工客服，请稍候。")
                else:
                    session_state["step"] = "initial"
                    responses.append("抱歉，我理解错了。请问您具体需要什么帮助？")
            
            elif is_transfer(content):
                logger.info("用户要求转人工")
                session_state["step"] = "completed"
                responses.append("已为您转接人工客服，请稍候。")
            
            else:
                logger.info("用户不直接回答，重新进行意图识别")
                # 重新进行意图识别
                new_intent_result = self._recognize_intent(user_id, phone, content, trace_id)
                session_state["intent_result"] = new_intent_result
                # 生成新的确认消息
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                # 保持在等待确认状态
                logger.info("已更新意图并重新确认")
        
        elif session_state["step"] == "waiting_order_in_list":
            # 等待用户确认订单是否在列表中，或直接选择订单
            logger.info(f"等待用户确认订单是否在列表中: {content}")
            
            # 如果用户直接输入数字，默认是"是"，直接选择订单
            if self._is_order_number_selection(content):
                order_index = int(content.strip()) - 1
                current_orders = session_state.get("current_orders", [])
                
                if 0 <= order_index < len(current_orders):
                    order = current_orders[order_index]
                    # 返回订单详细信息
                    order_detail = self._get_order_detail(order)
                    responses.append(order_detail)
                    session_state["step"] = "order_selected"
                    session_state["selected_order"] = order
                else:
                    responses.append(f"请输入1-{len(current_orders)}之间的数字选择订单。")
            
            elif is_confirmed(content):
                # 用户确认在列表中，进入选择订单步骤
                logger.info("用户确认订单在列表中")
                responses.append("请回复订单数字序号（1、2、3...）选择您要查看的订单。")
                session_state["step"] = "waiting_order_selection"
            
            elif is_rejected(content):
                # 用户说不在列表中，查询下一页
                logger.info("用户说订单不在列表中，查询下一页")
                next_page = session_state.get("current_page", 1) + 1
                responses = self._query_orders_with_pagination(phone, session_id, next_page)
            
            else:
                # 用户不直接回答，重新进行意图识别
                logger.info("用户不直接回答，重新进行意图识别")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_order_selection":
            # 等待用户选择订单编号
            logger.info(f"等待用户选择订单编号: {content}")
            
            # 检查是否是数字
            if self._is_order_number_selection(content):
                order_index = int(content.strip()) - 1
                current_orders = session_state.get("current_orders", [])
                
                if 0 <= order_index < len(current_orders):
                    order = current_orders[order_index]
                    responses.append(f"您选择的订单：{order['product_name']} - {order['order_number']} - {order['status_text']}\n请问您对这个订单有什么问题？")
                    session_state["step"] = "order_selected"
                else:
                    responses.append(f"请输入1-{len(current_orders)}之间的数字选择订单。")
            else:
                # 用户不直接回答，重新进行意图识别
                logger.info("用户不直接回答，重新进行意图识别")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_phone_confirmation":
            # 等待用户确认手机号
            logger.info(f"等待用户确认手机号: {content}")
            
            if is_confirmed(content):
                logger.info("用户确认是这个手机号")
                responses.append("已为您转接人工客服，请稍候。")
                session_state["step"] = "completed"
            
            elif is_rejected(content):
                logger.info("用户否认是这个手机号")
                responses.append("为了您的账户安全，仅支持查询当前登录账号绑定的订单。\n\n如需查询其他手机号的订单，请先退出当前账号，使用其他手机号重新登录后再试。")
                session_state["step"] = "initial"
            
            elif re.search(r'1[3-9]\d{9}', content):
                logger.info("用户提供了新手机号")
                responses.append("为了您的账户安全，仅支持查询当前登录账号绑定的订单，如需查询其他手机号，请切换账号登录后重试。")
                session_state["step"] = "initial"
            
            else:
                # 用户不直接回答，重新进行意图识别
                logger.info("用户不直接回答，重新进行意图识别")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_self_check":
            # 等待用户自查后回复
            logger.info(f"等待用户自查后回复: {content}")
            
            if is_confirmed(content):
                # 用户确认已核对，但仍没找到订单，转人工
                logger.info("用户已核对但仍没找到订单，转人工")
                responses.append("已为您转接人工客服，请稍候。")
                session_state["step"] = "completed"
            
            elif is_rejected(content):
                # 用户说没核对，重新引导
                logger.info("用户说没核对，重新引导")
                responses.append("好的，请您先核对：\n1. 当前登录的手机号是否正确\n2. 如需查询其他手机号的订单，请切换对应账号登录后重试\n\n核对完成后请回复\"是\"。")
            
            else:
                # 用户不直接回答，重新进行意图识别
                logger.info("用户不直接回答，重新进行意图识别")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_refund_order_selection":
            # 等待用户选择退款订单
            logger.info(f"等待用户选择退款订单: {content}")
            
            # 如果用户直接输入数字，选择订单
            if self._is_order_number_selection(content):
                order_index = int(content.strip()) - 1
                current_orders = session_state.get("current_orders", [])
                
                if 0 <= order_index < len(current_orders):
                    order = current_orders[order_index]
                    session_state["selected_order"] = order
                    session_state["step"] = "waiting_refund_confirm"
                    responses.append(f"您选择的订单：{order['product_name']} - {order['order_number']}\n\n是否确认申请该订单退货退款？请回复\"是\"确认，回复\"不是\"取消。")
                else:
                    responses.append(f"请输入1-{len(current_orders)}之间的数字选择订单。")
            
            elif is_rejected(content):
                # 用户说不在列表中，查询下一页
                logger.info("用户说订单不在列表中，查询下一页")
                # 重新查询订单（下一页）
                phone = session_state.get("phone", "13800000000")
                next_page = session_state.get("current_page", 1) + 1
                responses = self._query_orders_with_pagination(phone, session_id, next_page, "waiting_refund_order_selection")
                # 重新设置为退款订单选择状态
                session_state["step"] = "waiting_refund_order_selection"
            
            else:
                # 用户不直接回答，重新进行意图识别
                logger.info("用户不直接回答，重新进行意图识别")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_refund_confirm":
            # 等待用户确认退款
            logger.info(f"等待用户确认退款: {content}")
            
            if is_confirmed(content):
                logger.info("用户确认退款")
                responses.append("已提交系统审核，1个工作日内处理。\n\n请问还有其他可以帮您的吗？")
                session_state["step"] = "initial"
            
            elif is_rejected(content):
                logger.info("用户取消退款")
                responses.append("已取消申请。\n\n请问还有其他可以帮您的吗？")
                session_state["step"] = "initial"
            
            else:
                # 用户不直接回答，重新进行意图识别，打断流程
                logger.info("用户不直接回答，重新进行意图识别，打断流程")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_return_confirm":
            # 等待用户确认是否愿意退货
            logger.info(f"等待用户确认是否愿意退货: {content}")
            
            if is_confirmed(content):
                # 用户愿意退货，进入退款订单选择流程
                logger.info("用户愿意退货，进入退款订单选择")
                phone = session_state.get("phone", "13800000000")
                # 查询可退货退款的订单（已付款/已发货/已签收，且签收7天内）
                orders = self._get_refundable_orders(phone)
                if orders:
                    session_state["current_orders"] = orders
                    session_state["current_page"] = 1
                    session_state["total_orders"] = len(orders)
                    session_state["phone"] = phone
                    order_info = "\n".join([
                        f"{i+1}. {order['product_name']} - {order['order_number']} - {order['status_text']}"
                        for i, order in enumerate(orders)
                    ])
                    responses.append(f"请选择您要退货退款的订单：\n{order_info}\n\n请直接回复订单编号（1、2、3...）选择要退货退款的订单，或回复\"不是\"查看下一页。")
                    session_state["step"] = "waiting_refund_order_selection"
                else:
                    responses.append("未查询到符合退货退款条件的订单。该订单状态/时效不支持退货退款。")
                    session_state["step"] = "initial"
            
            elif is_rejected(content):
                # 用户不愿意退货（仅退款），转人工
                logger.info("用户不愿意退货（仅退款），转人工")
                responses.append("仅退款申请需要人工审核，已为您转接人工客服，请稍候。")
                session_state["step"] = "completed"
            
            else:
                # 用户不直接回答，重新进行意图识别，打断流程
                logger.info("用户不直接回答，重新进行意图识别，打断流程")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_complaint_content":
            # 等待用户输入投诉内容
            logger.info(f"等待用户输入投诉内容: {content}")
            
            # 保存投诉内容
            session_state["complaint_content"] = content
            
            # 查询用户的订单供选择（可选关联订单）
            phone = session_state.get("phone", "")
            all_orders = self._get_all_orders(phone)
            
            if all_orders:
                self.session_states[session_id]["current_orders"] = all_orders
                self.session_states[session_id]["current_page"] = 1
                self.session_states[session_id]["total_orders"] = len(all_orders)
                
                order_info = "\n".join([
                    f"{i+1}. {order.get('product_name', '商品')} - {order.get('order_number', '订单号')} - {order.get('status_text', '状态')}"
                    for i, order in enumerate(all_orders[:5])
                ])
                responses.append(f"已收到您的投诉内容。\n\n请选择与投诉相关的订单（可选）：\n{order_info}\n\n0. 不关联订单\n\n请直接回复订单编号（1、2、3...）选择订单，或回复\"0\"不关联订单。")
                session_state["step"] = "waiting_complaint_order_selection"
            else:
                # 没有订单，直接提交投诉
                responses.append("已收到您的投诉内容，由于您当前没有订单，我们将直接为您处理。")
                responses.append("很抱歉给您带来不好的体验，已为您记录问题并反馈。")
                responses.append("转接人工客服为您处理，请稍候。")
                session_state["step"] = "completed"
        
        elif session_state["step"] == "waiting_complaint_order_selection":
            # 等待用户选择投诉订单（可选）
            logger.info(f"等待用户选择投诉订单: {content}")
            
            # 如果用户输入0，不选择订单
            if content.strip() == "0":
                logger.info("用户选择不关联订单")
                responses.append("很抱歉给您带来不好的体验，已为您记录问题并反馈。")
                responses.append("转接人工客服为您处理，请稍候。")
                session_state["step"] = "completed"
            
            # 如果用户直接输入数字，选择订单
            elif self._is_order_number_selection(content):
                order_index = int(content.strip()) - 1
                current_orders = session_state.get("current_orders", [])
                
                if 0 <= order_index < len(current_orders):
                    order = current_orders[order_index]
                    session_state["selected_order"] = order
                    responses.append(f"您选择的订单：{order['product_name']} - {order['order_number']}\n\n很抱歉给您带来不好的体验，已为您记录问题并反馈。")
                    responses.append("转接人工客服为您处理，请稍候。")
                    session_state["step"] = "completed"
                else:
                    responses.append(f"请输入0-{len(current_orders)}之间的数字选择订单。")
            
            elif is_rejected(content):
                # 用户说不在列表中，查询下一页
                logger.info("用户说订单不在列表中，查询下一页")
                # 重新查询订单（下一页）
                phone = session_state.get("phone", "13800000000")
                next_page = session_state.get("current_page", 1) + 1
                responses = self._query_orders_with_pagination(phone, session_id, next_page, "waiting_complaint_order_selection")
                # 重新设置为投诉订单选择状态
                session_state["step"] = "waiting_complaint_order_selection"
            
            else:
                # 用户不直接回答，重新进行意图识别
                logger.info("用户不直接回答，重新进行意图识别")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_exchange_order_selection":
            # 等待用户选择换货订单
            logger.info(f"等待用户选择换货订单: {content}")
            
            # 如果用户直接输入数字，选择订单
            if self._is_order_number_selection(content):
                order_index = int(content.strip()) - 1
                current_orders = session_state.get("current_orders", [])
                
                if 0 <= order_index < len(current_orders):
                    order = current_orders[order_index]
                    session_state["selected_order"] = order
                    session_state["step"] = "waiting_exchange_confirm"
                    responses.append(f"您选择的订单：{order['product_name']} - {order['order_number']}\n\n是否确认申请该订单换货？请回复\"是\"确认，回复\"不是\"取消。")
                else:
                    responses.append(f"请输入1-{len(current_orders)}之间的数字选择订单。")
            
            elif is_rejected(content):
                # 用户说不在列表中，查询下一页
                logger.info("用户说订单不在列表中，查询下一页")
                # 重新查询订单（下一页）
                phone = session_state.get("phone", "13800000000")
                next_page = session_state.get("current_page", 1) + 1
                responses = self._query_orders_with_pagination(phone, session_id, next_page, "waiting_exchange_order_selection")
                # 重新设置为换货订单选择状态
                session_state["step"] = "waiting_exchange_order_selection"
            
            else:
                # 用户不直接回答，重新进行意图识别
                logger.info("用户不直接回答，重新进行意图识别")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_exchange_confirm":
            # 等待用户确认换货
            logger.info(f"等待用户确认换货: {content}")
            
            if is_confirmed(content):
                logger.info("用户确认换货")
                order = session_state.get("selected_order", {})
                responses.append(f"已为您提交换货申请，系统审核后将在1个工作日内告知您换货地址及流程。\n\n请问还有其他可以帮您的吗？")
                session_state["step"] = "initial"
            
            elif is_rejected(content):
                logger.info("用户取消换货")
                responses.append("已取消您的换货申请，如有需要可再次发起。\n\n请问还有其他可以帮您的吗？")
                session_state["step"] = "initial"
            
            else:
                # 用户不直接回答，重新进行意图识别，打断换货流程
                logger.info("用户不直接回答，重新进行意图识别，打断换货流程")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_modify_order_selection":
            # 等待用户选择修改订单
            logger.info(f"等待用户选择修改订单: {content}")
            
            # 如果用户直接输入数字，选择订单
            if self._is_order_number_selection(content):
                order_index = int(content.strip()) - 1
                current_orders = session_state.get("current_orders", [])
                
                if 0 <= order_index < len(current_orders):
                    order = current_orders[order_index]
                    session_state["selected_order"] = order
                    
                    # 检查订单状态，仅未发货订单可修改
                    if order.get('status') in ['pending_payment', 'paid']:
                        session_state["step"] = "waiting_modify_content"
                        responses.append(f"您选择的订单：{order['product_name']} - {order['order_number']}\n\n请回复您要修改的内容（地址/备注/电话），或直接发送新的信息。")
                    else:
                        responses.append(f"抱歉，订单{order['order_number']}已发货，无法修改地址或备注。如需帮助请联系人工客服。")
                        session_state["step"] = "initial"
                else:
                    responses.append(f"请输入1-{len(current_orders)}之间的数字选择订单。")
            
            elif is_rejected(content):
                # 用户说不在列表中，查询下一页
                logger.info("用户说订单不在列表中，查询下一页")
                # 重新查询订单（下一页）
                phone = session_state.get("phone", "13800000000")
                next_page = session_state.get("current_page", 1) + 1
                responses = self._query_orders_with_pagination(phone, session_id, next_page, "waiting_modify_order_selection")
                # 重新设置为修改订单选择状态
                session_state["step"] = "waiting_modify_order_selection"
            
            else:
                # 用户不直接回答，重新进行意图识别
                logger.info("用户不直接回答，重新进行意图识别")
                new_intent_result = self._recognize_intent(user_id, phone, content)
                session_state["intent_result"] = new_intent_result
                new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
                responses.append(new_confirmation_msg)
                session_state["step"] = "waiting_confirm"
        
        elif session_state["step"] == "waiting_modify_content":
            # 等待用户输入修改内容
            logger.info(f"等待用户输入修改内容: {content}")
            
            order = session_state.get("selected_order", {})
            # 模拟修改成功
            responses.append(f"订单修改成功！\n订单：{order.get('product_name', '')}\n修改内容：{content}\n\n后台已更新您的订单信息。\n\n请问还有其他可以帮您的吗？")
            session_state["step"] = "initial"
        
        elif session_state["step"] == "completed":
            # 已转人工，检查是否需要重置会话
            if "重置" in content or "重新开始" in content or "重新对话" in content:
                # 用户请求重置会话，重新开始
                logger.info("用户请求重置会话")
                responses.append("已为您重置会话，请问您需要什么帮助？")
                session_state["step"] = "initial"
            else:
                # 已转人工，不再处理用户输入
                logger.info("已转人工，不再处理用户输入")
                responses.append("已为您转接人工客服，请稍候。")
        
        else:  # confirmed or order_selected
            # 已确认状态，处理新的用户输入
            logger.info(f"处理新的用户输入: {content}")
            # 用户不直接回答，重新进行意图识别
            new_intent_result = self._recognize_intent(user_id, phone, content, trace_id)
            session_state["intent_result"] = new_intent_result
            # 生成确认消息
            new_confirmation_msg = self._generate_confirmation_message(new_intent_result, phone)
            responses.append(new_confirmation_msg)
            session_state["step"] = "waiting_confirm"
        
        # 对响应进行安全检查和隐私信息打码
        processed_responses = []
        for response in responses:
            security_response = security_service.process_system_response(session_state.get("log_id"), response)
            if security_response["valid"]:
                processed_responses.append(security_response["masked_response"])
            else:
                processed_responses.append("系统响应错误")
        
        # 构建最终响应
        final_response = "\n".join(processed_responses)
        
        # 保存对话上下文
        if content and final_response:
            SessionManager.update_context(user_id, session_id, content, final_response)
            logger.info(f"已保存对话上下文，用户消息: {content[:50]}..., AI回复: {final_response[:50]}...")
        
        return {
            "success": True,
            "intent": session_state.get("intent_result"),
            "responses": processed_responses,
            "final_response": final_response,
            "session_state": session_state
        }

# 全局实例
_order_dialogue_flow_instance = None

def get_order_dialogue_flow(db: Session = None) -> OrderDialogueFlow:
    """获取订单对话流程实例（单例模式）"""
    global _order_dialogue_flow_instance
    if _order_dialogue_flow_instance is None:
        _order_dialogue_flow_instance = OrderDialogueFlow(db)
    elif db:
        _order_dialogue_flow_instance.db = db
        _order_dialogue_flow_instance.order_service = OrderService(db) if db else None
    return _order_dialogue_flow_instance
