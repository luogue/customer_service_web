"""
意图识别 Mock 数据服务
基于关键词匹配的意图识别
"""
import re
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel

class Intent(BaseModel):
    """意图模型"""
    intent_type: str
    priority: int
    description: str

class IntentRecognitionResult(BaseModel):
    """意图识别结果"""
    user_id: str
    phone: str
    content: str
    intents: List[Intent]

class IntentMockService:
    """意图识别 Mock 服务 - 基于关键词匹配"""
    
    def __init__(self):
        # 意图关键词配置
        self.intent_keywords = {
            # 1. 查订单/查物流
            "query_order": {
                "keywords": [
                    "订单", "查订单", "查询订单", "我的订单", "订单状态",
                    "物流", "查物流", "快递", "快递到哪", "发货了吗",
                    "到哪了", "什么时候到", "预计送达", "配送"
                ],
                "priority": 1,
                "description": "查询订单信息"
            },
            
            # 2. 退货/退款（包含仅退款，都需要先询问是否退货）
            "refund_return": {
                "keywords": [
                    "仅退款", "不退货退款", "直接退款", "只退款", "退款不退货", "没收到货退款",
                    "退货退款", "退货", "申请退货", "我要退货", "退商品",
                    "退款", "申请退款", "我要退款", "退钱",
                    "质量问题", "商品有问题", "损坏", "破损", "不想要了"
                ],
                "priority": 1,
                "description": "申请退款"
            },
            
            # 3. 换货
            "exchange": {
                "keywords": [
                    "换货", "换一件", "换尺码", "换颜色", "换大小",
                    "换型号", "换规格", "尺码不对", "大小不合适",
                    "颜色不对", "发错货", "换一个新的"
                ],
                "priority": 1,
                "description": "申请换货"
            },
            
            # 4. 改地址/改备注
            "modify_address": {
                "keywords": [
                    "改地址", "修改地址", "换地址", "地址错了",
                    "改收货地址", "改备注", "修改备注", "加备注",
                    "改电话", "改手机号", "改联系人"
                ],
                "priority": 1,
                "description": "修改地址或备注"
            },
            
            # 5. 投诉/售后/转人工
            "complaint": {
                "keywords": [
                    "投诉", "举报", "售后", "客服",
                    "人工", "转人工", "找客服", "投诉商家",
                    "服务态度", "欺诈", "虚假宣传", "假货"
                ],
                "priority": 1,
                "description": "投诉或售后问题"
            },
            
            # 其他辅助意图
            "query_promotion": {
                "keywords": [
                    "优惠", "优惠券", "活动", "促销", "折扣",
                    "满减", "红包", "代金券", "省钱", "便宜"
                ],
                "priority": 2,
                "description": "查询优惠活动"
            },
            
            "cancel_order": {
                "keywords": [
                    "取消订单", "取消", "不要了", "撤销订单",
                    "关闭订单", "终止订单"
                ],
                "priority": 1,
                "description": "取消订单"
            },
            
            "urgent_delivery": {
                "keywords": [
                    "催发货", "快点发货", "加急", "催单",
                    "催快递", "快点送", "急用", "赶时间"
                ],
                "priority": 1,
                "description": "催发货/催物流"
            },
            
            # 9. 问题咨询
            "question_consult": {
                "keywords": [
                    "下单失败", "下单卡顿", "限购", "限购规则",
                    "发票", "开发票", "怎么开发票", "发票问题",
                    "咨询", "问题", "疑问", "怎么", "如何",
                    "为什么", "什么", "怎么样", "如何操作"
                ],
                "priority": 1,
                "description": "问题咨询"
            }
        }
    
    def recognize_intent(self, user_id: str, phone: str, content: str) -> IntentRecognitionResult:
        """
        识别用户意图
        
        Args:
            user_id: 用户ID
            phone: 用户手机号
            content: 用户输入内容
            
        Returns:
            意图识别结果
        """
        content_lower = content.lower().strip()
        matched_intents = []
        
        # 收集所有匹配的关键词和对应的意图
        all_matches = []
        for intent_type, config in self.intent_keywords.items():
            for keyword in config["keywords"]:
                if keyword in content_lower:
                    all_matches.append({
                        "intent_type": intent_type,
                        "priority": config["priority"],
                        "description": config["description"],
                        "keyword": keyword,
                        "keyword_length": len(keyword)
                    })
        
        # 按关键词长度降序排序（优先匹配最长的关键词）
        all_matches.sort(key=lambda x: x["keyword_length"], reverse=True)
        
        # 去重，保留最长关键词匹配的意图
        seen_intents = set()
        for match in all_matches:
            if match["intent_type"] not in seen_intents:
                seen_intents.add(match["intent_type"])
                intent = Intent(
                    intent_type=match["intent_type"],
                    priority=match["priority"],
                    description=match["description"]
                )
                matched_intents.append(intent)
        
        # 按优先级排序
        matched_intents.sort(key=lambda x: x.priority)
        
        return IntentRecognitionResult(
            user_id=user_id,
            phone=phone,
            content=content,
            intents=matched_intents
        )

# 创建全局实例
intent_mock_service = IntentMockService()
