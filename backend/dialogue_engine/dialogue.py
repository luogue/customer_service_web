from typing import List, Dict, Optional
from datetime import datetime
import re
from sqlalchemy.orm import Session

from knowledge_base.models import Conversation as DBMessage

class DialogueManager:
    def __init__(self):
        self.sessions = {}
        self.intent_patterns = {
            'order_query': r'查订单|订单状态|物流|发货时间|订单查询|物流查询|查物流|我的订单物流到哪了|我买的东西什么时候发货|帮我查一下订单状态',
            'product_query': r'规格|价格|库存|材质|尺寸|重量|颜色|型号|参数|这个商品有几个颜色|这件衣服是什么材质的|这款现在还有货吗',
            'refund_return': r'退货|退款|换货|退运费|申请退货|申请退款|我要申请退货|商品有问题，我想退款|不合适可以换货吗',
            'complaint': r'投诉|差评|服务差|商品差|物流慢|态度不好|质量差|你们服务太差了|商品质量有问题，我要投诉|物流太慢，我要差评',
            'info_modification': r'改地址|改手机号|改备注|修改地址|修改手机号|修改备注|帮我改一下收货地址|我要换个手机号|订单帮我加个备注',
            'urgent_delivery': r'催发货|催物流|什么时候发货|快点发货|赶紧给我发货|我的快递怎么还不动|都几天了怎么不发货',
            'cancel_order': r'取消订单|退单|不要了|我不想要了，取消订单|帮我把这个订单退掉|下单错了，能取消吗',
            'invoice': r'开发票|发票|税票|我要开电子发票|这个订单能开发票吗|发票抬头怎么改',
            'after_sales': r'售后|维修|质保|保修|质量问题|商品坏了能修吗|这个保修多久|质量问题怎么售后',
            'promotion': r'活动|优惠|优惠券|折扣|促销|现在有什么优惠|优惠券怎么用|满减活动是多少',
            'chitchat': r'你好|您好|谢谢|再见|早上好|晚上好|夸奖|赞美|闲聊|无关|你好呀|谢谢客服|今天天气怎么样',
            'human': r'人工|客服|转接|真人',
            'help': r'帮助|怎么|如何|教程|指导'
        }
        
        # 意图例句
        self.intent_examples = {
            'order_query': [
                '我的订单物流到哪了',
                '我买的东西什么时候发货',
                '帮我查一下订单状态'
            ],
            'product_query': [
                '这个商品有几个颜色',
                '这件衣服是什么材质的',
                '这款现在还有货吗'
            ],
            'refund_return': [
                '我要申请退货',
                '商品有问题，我想退款',
                '不合适可以换货吗'
            ],
            'complaint': [
                '你们服务太差了',
                '商品质量有问题，我要投诉',
                '物流太慢，我要差评'
            ],
            'info_modification': [
                '帮我改一下收货地址',
                '我要换个手机号',
                '订单帮我加个备注'
            ],
            'urgent_delivery': [
                '赶紧给我发货',
                '我的快递怎么还不动',
                '都几天了怎么不发货'
            ],
            'cancel_order': [
                '我不想要了，取消订单',
                '帮我把这个订单退掉',
                '下单错了，能取消吗'
            ],
            'invoice': [
                '我要开电子发票',
                '这个订单能开发票吗',
                '发票抬头怎么改'
            ],
            'after_sales': [
                '商品坏了能修吗',
                '这个保修多久',
                '质量问题怎么售后'
            ],
            'promotion': [
                '现在有什么优惠',
                '优惠券怎么用',
                '满减活动是多少'
            ],
            'chitchat': [
                '你好呀',
                '谢谢客服',
                '今天天气怎么样'
            ],
            'human': [
                '转人工',
                '我要找客服',
                '转接真人'
            ],
            'help': [
                '怎么使用优惠券',
                '如何申请退款',
                '帮助我一下'
            ]
        }
    
    def get_or_create_session(self, session_id: str) -> Dict:
        """获取或创建对话会话"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'id': session_id,
                'messages': [],
                'context': {},
                'created_at': datetime.now(),
                'last_active': datetime.now()
            }
        return self.sessions[session_id]
    
    def detect_intent(self, message: str) -> str:
        """检测用户意图"""
        message_lower = message.lower()
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, message_lower):
                return intent
        return 'general'
    
    def add_message(self, session_id: str, role: str, content: str, db: Session = None):
        """添加消息到会话"""
        session = self.get_or_create_session(session_id)
        message_data = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        session['messages'].append(message_data)
        session['last_active'] = datetime.now()
        
        # 更新上下文
        if role == 'user':
            intent = self.detect_intent(content)
            session['context']['last_intent'] = intent
        
        # 保存到数据库
        if db:
            try:
                db_message = DBMessage(
                    session_id=session_id,
                    role=role,
                    content=content,
                    type='text'
                )
                db.add(db_message)
                db.commit()
                db.refresh(db_message)
            except Exception as e:
                db.rollback()
                print(f"Error saving message to database: {e}")
    
    def get_conversation_history(self, session_id: str, limit: int = 10, db: Session = None) -> List[Dict]:
        """获取对话历史"""
        session = self.sessions.get(session_id)
        if session and session['messages']:
            return session['messages'][-limit:]
        
        # 如果内存中没有，从数据库获取
        if db:
            try:
                db_messages = db.query(DBMessage).filter(
                    DBMessage.session_id == session_id
                ).order_by(DBMessage.created_at.desc()).limit(limit).all()
                
                messages = []
                for msg in reversed(db_messages):
                    messages.append({
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.created_at.isoformat()
                    })
                return messages
            except Exception as e:
                print(f"Error retrieving messages from database: {e}")
        
        return []
    
    def should_transfer_to_human(self, session_id: str) -> bool:
        """判断是否需要转人工"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        messages = session['messages']
        if len(messages) < 3:
            return False
        
        # 检查连续未识别的问题
        recent_messages = messages[-6:]
        user_messages = [m for m in recent_messages if m['role'] == 'user']
        
        if len(user_messages) >= 3:
            unclear_count = sum(1 for m in user_messages 
                              if self.detect_intent(m['content']) == 'general')
            if unclear_count >= 3:
                return True
        
        # 检查是否明确要求人工
        last_message = messages[-1] if messages else None
        if last_message and last_message['role'] == 'user':
            if self.detect_intent(last_message['content']) == 'human':
                return True
        
        return False
    
    def clear_session(self, session_id: str):
        """清除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_intent_examples(self, intent: str = None) -> Dict[str, List[str]]:
        """获取意图例句
        
        Args:
            intent: 意图名称，如果为None则返回所有意图的例句
            
        Returns:
            意图例句字典
        """
        if intent:
            return {intent: self.intent_examples.get(intent, [])}
        return self.intent_examples
    
    def get_intent_by_example(self, message: str) -> str:
        """通过例句匹配意图
        
        Args:
            message: 用户消息
            
        Returns:
            匹配的意图
        """
        message_lower = message.lower()
        # 先尝试正则匹配
        intent = self.detect_intent(message)
        if intent != 'general':
            return intent
        
        # 如果正则匹配失败，尝试例句匹配
        for intent_name, examples in self.intent_examples.items():
            for example in examples:
                if any(keyword in message_lower for keyword in example.lower().split()):
                    return intent_name
        
        return 'general'

dialogue_manager = DialogueManager()
