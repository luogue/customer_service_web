"""
订单查询 Mock 数据服务
五层架构：大模型交互层

提供订单查询相关的 Mock 数据，包括：
- 意图识别结果
- 订单查询结果
- 自然语言回复生成

设计原则：
1. 数据格式与真实接口保持一致
2. 支持一键切换到真实接口
3. 提供丰富的 Mock 场景
"""
import random
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel


# ==================== 数据模型 ====================

class Intent(BaseModel):
    """意图模型"""
    intent_type: str
    priority: int
    description: str
    confidence: float = 0.95


class IntentRecognitionResult(BaseModel):
    """意图识别结果"""
    user_id: str
    phone: str
    content: str
    intents: List[Intent]
    process_time: float = 0.5


class OrderItem(BaseModel):
    """订单商品项"""
    product_id: str
    product_name: str
    sku: str
    quantity: int
    unit_price: float
    total_price: float
    image_url: str


class LogisticsInfo(BaseModel):
    """物流信息"""
    carrier: str
    tracking_number: str
    status: str
    status_text: str
    latest_update: str
    estimated_delivery: str
    tracking_history: List[Dict[str, str]]


class OrderInfo(BaseModel):
    """订单信息"""
    order_id: str
    order_number: str
    user_id: str
    phone: str
    total_amount: float
    discount_amount: float
    pay_amount: float
    status: str
    status_text: str
    created_at: str
    pay_time: Optional[str]
    ship_time: Optional[str]
    receive_time: Optional[str]
    items: List[OrderItem]
    logistics: Optional[LogisticsInfo]
    address: Dict[str, str]


class OrderQueryResult(BaseModel):
    """订单查询结果"""
    success: bool
    phone: str
    total_count: int
    orders: List[OrderInfo]
    query_time: float = 0.3
    message: str = ""


class OrderReply(BaseModel):
    """订单查询回复"""
    reply_type: str  # "direct", "confirm_phone", "no_order", "multi_orders"
    content: str
    data: Optional[Dict[str, Any]] = None


# ==================== Mock 数据服务 ====================

class OrderMockService:
    """订单查询 Mock 服务"""
    
    def __init__(self):
        self._init_intent_data()
        self._init_order_data()
        self._init_reply_templates()
    
    def _init_intent_data(self):
        """初始化意图识别数据"""
        # 单意图场景
        self.single_intents = {
            "query_order": {
                "intent_type": "query_order",
                "priority": 1,
                "description": "查询订单信息",
                "confidence": 0.98
            },
            "query_logistics": {
                "intent_type": "query_logistics",
                "priority": 1,
                "description": "查询物流信息",
                "confidence": 0.96
            },
            "urgent_delivery": {
                "intent_type": "urgent_delivery",
                "priority": 1,
                "description": "催发货/催物流",
                "confidence": 0.94
            },
            "cancel_order": {
                "intent_type": "cancel_order",
                "priority": 1,
                "description": "取消订单",
                "confidence": 0.95
            },
            "refund_return": {
                "intent_type": "refund_return",
                "priority": 1,
                "description": "申请退货退款",
                "confidence": 0.93
            },
            "modify_address": {
                "intent_type": "modify_address",
                "priority": 1,
                "description": "修改收货地址",
                "confidence": 0.92
            },
            "question_consult": {
                "intent_type": "question_consult",
                "priority": 1,
                "description": "问题咨询",
                "confidence": 0.90
            }
        }
        
        # 多意图场景
        self.multi_intent_combinations = [
            ["query_order", "query_logistics"],
            ["query_order", "urgent_delivery"],
            ["query_order", "refund_return"],
            ["query_logistics", "urgent_delivery"]
        ]
    
    def _init_order_data(self):
        """初始化订单数据"""
        # 订单状态
        self.order_statuses = {
            "pending": {"text": "待付款", "desc": "订单已创建，等待付款"},
            "paid": {"text": "已付款", "desc": "订单已付款，等待发货"},
            "shipped": {"text": "已发货", "desc": "商品已发出，运输中"},
            "delivered": {"text": "已送达", "desc": "商品已送达，等待签收"},
            "completed": {"text": "已完成", "desc": "订单已完成"},
            "cancelled": {"text": "已取消", "desc": "订单已取消"},
            "refunding": {"text": "退款中", "desc": "退款申请处理中"},
            "refunded": {"text": "已退款", "desc": "退款已完成"}
        }
        
        # 物流公司
        self.carriers = [
            {"code": "SF", "name": "顺丰速运"},
            {"code": "JD", "name": "京东物流"},
            {"code": "YT", "name": "圆通速递"},
            {"code": "ZT", "name": "中通快递"},
            {"code": "EMS", "name": "EMS"}
        ]
        
        # 商品数据
        self.products = [
            {"id": "P001", "name": "纯棉T恤", "sku": "T001-BL-M", "price": 99.0},
            {"id": "P002", "name": "运动卫衣", "sku": "W001-GY-L", "price": 299.0},
            {"id": "P003", "name": "休闲裤", "sku": "K001-BK-32", "price": 199.0},
            {"id": "P004", "name": "运动鞋", "sku": "S001-WT-42", "price": 499.0},
            {"id": "P005", "name": "双肩包", "sku": "B001-BK", "price": 159.0}
        ]
    
    def _init_reply_templates(self):
        """初始化回复模板"""
        self.reply_templates = {
            "welcome": [
                "您好，这里是AI客服，很高兴为您服务，请问有什么可以帮您？"
            ],
            "order_not_found": [
                "抱歉，没有找到您手机号下的订单。请问是这个手机号下的订单吗？",
                "未查询到您的订单信息，请确认一下下单时使用的手机号是否正确。",
                "系统中暂无您的订单记录，您可以检查一下：\n1. 确认手机号是否正确\n2. 订单是否使用其他账号下单\n3. 订单是否已完成很久"
            ],
            "single_order": [
                "您的订单{order_number}目前{status_text}。{additional_info}",
                "查询到您的订单：{order_number}，状态为{status_text}。{additional_info}",
                "找到您的订单啦！订单号{order_number}，当前{status_text}。{additional_info}"
            ],
            "multiple_orders": [
                "找到您最近的{count}个订单：\n{order_list}",
                "查询到您的{count}个订单：\n{order_list}\n需要查看哪个订单的详细信息吗？"
            ],
            "logistics_info": [
                "物流状态：{logistics_status}\n快递公司：{carrier}\n运单号：{tracking_number}\n预计送达：{estimated_delivery}",
                "您的包裹由{carrier}配送，运单号{tracking_number}，目前{logistics_status}，预计{estimated_delivery}送达。"
            ],
            "confirm_phone": [
                "请问您要查询的是{phone}这个手机号下的订单吗？",
                "确认一下，您是用手机号{phone}下单的吗？"
            ],
            "question_consult": [
                "感谢您的咨询，关于{topic}，我来为您解答。",
                "您好，关于{topic}的问题，我可以为您提供相关信息。",
                "感谢您的提问，关于{topic}，以下是相关信息。"
            ]
        }
    
    # ==================== 意图识别接口 ====================
    
    def recognize_intent(self, user_id: str, phone: str, content: str,
                        intent_type: str = None) -> IntentRecognitionResult:
        """
        意图识别接口
        
        Args:
            user_id: 用户ID
            phone: 手机号
            content: 用户输入
            intent_type: 指定意图类型（可选）
            
        Returns:
            意图识别结果
        """
        if intent_type and intent_type in self.single_intents:
            # 返回指定意图
            intent_data = self.single_intents[intent_type].copy()
            intents = [Intent(**intent_data)]
        else:
            # 随机返回单意图或多意图
            if random.random() < 0.7:
                # 70% 单意图
                intent_key = random.choice(list(self.single_intents.keys()))
                intent_data = self.single_intents[intent_key].copy()
                intents = [Intent(**intent_data)]
            else:
                # 30% 多意图
                combo = random.choice(self.multi_intent_combinations)
                intents = [Intent(**self.single_intents[k]) for k in combo]
        
        return IntentRecognitionResult(
            user_id=user_id,
            phone=phone,
            content=content,
            intents=intents,
            process_time=round(random.uniform(0.2, 0.8), 2)
        )
    
    # ==================== 订单查询接口 ====================
    
    def query_orders(self, phone: str, order_number: str = None,
                    status: str = None, days: int = 30) -> OrderQueryResult:
        """
        订单查询接口
        
        Args:
            phone: 手机号
            order_number: 订单号（可选）
            status: 订单状态（可选）
            days: 查询最近多少天
            
        Returns:
            订单查询结果
        """
        # 模拟：13800000000 有订单，其他手机号无订单
        if phone != "13800000000":
            return OrderQueryResult(
                success=True,
                phone=phone,
                total_count=0,
                orders=[],
                message="未找到订单"
            )
        
        # 生成 Mock 订单
        orders = self._generate_mock_orders(phone, days)
        
        if order_number:
            orders = [o for o in orders if o.order_number == order_number]
        
        if status:
            orders = [o for o in orders if o.status == status]
        
        return OrderQueryResult(
            success=True,
            phone=phone,
            total_count=len(orders),
            orders=orders,
            message=f"查询成功，找到{len(orders)}个订单"
        )
    
    def _generate_mock_orders(self, phone: str, days: int) -> List[OrderInfo]:
        """生成 Mock 订单数据"""
        orders = []
        
        # 生成 1-3 个订单
        order_count = random.randint(1, 3)
        
        for i in range(order_count):
            order_id = f"ORD{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
            order_number = f"DD{random.randint(1000000000, 9999999999)}"
            
            # 随机状态（优先已发货和已完成）
            status_weights = ["shipped"] * 4 + ["completed"] * 3 + ["paid", "delivered", "pending"]
            status = random.choice(status_weights)
            status_info = self.order_statuses[status]
            
            # 生成时间
            created_at = datetime.now() - timedelta(days=random.randint(1, days))
            pay_time = created_at + timedelta(hours=random.randint(1, 24)) if status != "pending" else None
            ship_time = pay_time + timedelta(hours=random.randint(2, 48)) if status in ["shipped", "delivered", "completed"] else None
            receive_time = ship_time + timedelta(days=random.randint(1, 3)) if status in ["delivered", "completed"] else None
            
            # 生成商品
            items = self._generate_order_items()
            total_amount = sum(item.total_price for item in items)
            discount_amount = round(total_amount * random.uniform(0.05, 0.15), 2)
            pay_amount = total_amount - discount_amount
            
            # 生成物流信息（已发货状态）
            logistics = None
            if status in ["shipped", "delivered", "completed"]:
                logistics = self._generate_logistics_info(status)
            
            order = OrderInfo(
                order_id=order_id,
                order_number=order_number,
                user_id=f"U{phone[-4:]}",
                phone=phone,
                total_amount=total_amount,
                discount_amount=discount_amount,
                pay_amount=pay_amount,
                status=status,
                status_text=status_info["text"],
                created_at=created_at.strftime("%Y-%m-%d %H:%M:%S"),
                pay_time=pay_time.strftime("%Y-%m-%d %H:%M:%S") if pay_time else None,
                ship_time=ship_time.strftime("%Y-%m-%d %H:%M:%S") if ship_time else None,
                receive_time=receive_time.strftime("%Y-%m-%d %H:%M:%S") if receive_time else None,
                items=items,
                logistics=logistics,
                address={
                    "receiver": "张三",
                    "phone": phone,
                    "province": "广东省",
                    "city": "深圳市",
                    "district": "南山区",
                    "detail": "科技园南路88号"
                }
            )
            orders.append(order)
        
        # 按时间倒序排列
        orders.sort(key=lambda x: x.created_at, reverse=True)
        return orders
    
    def _generate_order_items(self) -> List[OrderItem]:
        """生成订单商品"""
        items = []
        item_count = random.randint(1, 3)
        
        selected_products = random.sample(self.products, item_count)
        
        for product in selected_products:
            quantity = random.randint(1, 2)
            total_price = round(product["price"] * quantity, 2)
            
            item = OrderItem(
                product_id=product["id"],
                product_name=product["name"],
                sku=product["sku"],
                quantity=quantity,
                unit_price=product["price"],
                total_price=total_price,
                image_url=f"https://example.com/images/{product['id']}.jpg"
            )
            items.append(item)
        
        return items
    
    def _generate_logistics_info(self, order_status: str) -> LogisticsInfo:
        """生成物流信息"""
        carrier = random.choice(self.carriers)
        tracking_number = f"SF{random.randint(100000000000, 999999999999)}"
        
        # 根据订单状态设置物流状态
        if order_status == "shipped":
            logistics_status = "transport"
            status_text = "运输中"
            latest_update = "快件已到达【深圳转运中心】"
        elif order_status == "delivered":
            logistics_status = "delivered"
            status_text = "已送达"
            latest_update = "快件已送达，请签收"
        else:  # completed
            logistics_status = "signed"
            status_text = "已签收"
            latest_update = "快件已签收，感谢使用"
        
        # 预计送达时间
        if order_status == "shipped":
            estimated_delivery = (datetime.now() + timedelta(days=random.randint(1, 2))).strftime("%m月%d日")
        else:
            estimated_delivery = "已送达"
        
        # 物流轨迹
        tracking_history = [
            {"time": datetime.now().strftime("%m-%d %H:%M"), "desc": latest_update},
            {"time": (datetime.now() - timedelta(hours=random.randint(2, 6))).strftime("%m-%d %H:%M"), "desc": "快件已发出，准备发往下一站"},
            {"time": (datetime.now() - timedelta(hours=random.randint(8, 12))).strftime("%m-%d %H:%M"), "desc": "商家已发货，等待揽收"}
        ]
        
        return LogisticsInfo(
            carrier=carrier["name"],
            tracking_number=tracking_number,
            status=logistics_status,
            status_text=status_text,
            latest_update=latest_update,
            estimated_delivery=estimated_delivery,
            tracking_history=tracking_history
        )
    
    # ==================== 回复生成接口 ====================
    
    def generate_reply(self, query_result: OrderQueryResult,
                      intent_result: IntentRecognitionResult) -> OrderReply:
        """
        生成自然语言回复
        
        Args:
            query_result: 订单查询结果
            intent_result: 意图识别结果
            
        Returns:
            订单查询回复
        """
        if query_result.total_count == 0:
            # 未找到订单
            return OrderReply(
                reply_type="no_order",
                content=random.choice(self.reply_templates["order_not_found"]),
                data={"phone": query_result.phone}
            )
        
        if query_result.total_count == 1:
            # 单个订单
            order = query_result.orders[0]
            additional_info = ""
            
            # 根据状态添加额外信息
            if order.status == "shipped" and order.logistics:
                additional_info = f"由{order.logistics.carrier}配送，预计{order.logistics.estimated_delivery}送达。"
            elif order.status == "completed":
                additional_info = "订单已完成，感谢您的购买！"
            elif order.status == "pending":
                additional_info = "请在30分钟内完成支付，超时订单将自动取消。"
            
            content = random.choice(self.reply_templates["single_order"]).format(
                order_number=order.order_number,
                status_text=order.status_text,
                additional_info=additional_info
            )
            
            return OrderReply(
                reply_type="direct",
                content=content,
                data={"order": order.dict()}
            )
        
        # 多个订单
        order_list = "\n".join([
            f"{i+1}. 订单号：{o.order_number}，状态：{o.status_text}，金额：¥{o.pay_amount}"
            for i, o in enumerate(query_result.orders[:3])
        ])
        
        content = random.choice(self.reply_templates["multiple_orders"]).format(
            count=query_result.total_count,
            order_list=order_list
        )
        
        return OrderReply(
            reply_type="multi_orders",
            content=content,
            data={"orders": [o.dict() for o in query_result.orders]}
        )
    
    def get_welcome_message(self) -> str:
        """获取首问语"""
        return self.reply_templates["welcome"][0]
    
    def get_goodbye_message(self) -> str:
        """获取结束语"""
        return "感谢您的咨询，祝您生活愉快。再见！"


# ==================== 全局服务实例 ====================

order_mock_service = OrderMockService()


# ==================== 便捷函数 ====================

def recognize_order_intent(user_id: str, phone: str, content: str) -> IntentRecognitionResult:
    """识别订单相关意图"""
    return order_mock_service.recognize_intent(user_id, phone, content)


def query_orders(phone: str, **kwargs) -> OrderQueryResult:
    """查询订单"""
    return order_mock_service.query_orders(phone, **kwargs)


def generate_order_reply(query_result: OrderQueryResult,
                        intent_result: IntentRecognitionResult) -> OrderReply:
    """生成订单查询回复"""
    return order_mock_service.generate_reply(query_result, intent_result)
