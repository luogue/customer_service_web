"""
订单数据模型 Schema
五层架构：知识底座层

提供贴近真实业务的订单数据结构，包含：
- 核心字段：订单基本信息
- 扩展字段：物流、售后、支付等详细信息
- 完整的订单状态流转
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# ==================== 枚举定义 ====================

class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"              # 待付款
    PAID = "paid"                    # 已付款
    SHIPPED = "shipped"              # 已发货
    DELIVERED = "delivered"          # 已送达/已签收
    COMPLETED = "completed"          # 已完成
    CANCELLED = "cancelled"          # 已取消
    REFUNDING = "refunding"          # 退款中
    REFUNDED = "refunded"            # 已退款
    RETURNING = "returning"          # 退货中
    RETURNED = "returned"            # 已退货


class PaymentStatus(str, Enum):
    """支付状态枚举"""
    UNPAID = "unpaid"                # 未支付
    PAID = "paid"                    # 已支付
    PARTIAL = "partial"              # 部分支付
    REFUNDING = "refunding"          # 退款中
    REFUNDED = "refunded"            # 已退款


class LogisticsStatus(str, Enum):
    """物流状态枚举"""
    PENDING = "pending"              # 待发货
    PICKED = "picked"                # 已揽收
    TRANSIT = "transit"              # 运输中
    DELIVERING = "delivering"        # 派送中
    DELIVERED = "delivered"          # 已送达
    SIGNED = "signed"                # 已签收
    EXCEPTION = "exception"          # 异常


class AfterSaleStatus(str, Enum):
    """售后状态枚举"""
    NONE = "none"                    # 无售后
    APPLYING = "applying"            # 申请中
    PROCESSING = "processing"        # 处理中
    APPROVED = "approved"            # 已同意
    REJECTED = "rejected"            # 已拒绝
    COMPLETED = "completed"          # 已完成


class RefundReason(str, Enum):
    """退款原因枚举"""
    WRONG_ITEM = "wrong_item"        # 商品错发/漏发
    QUALITY = "quality"              # 商品质量问题
    NOT_MATCH = "not_match"          # 商品与描述不符
    CHANGE_MIND = "change_mind"      # 不想要了
    WRONG_SIZE = "wrong_size"        # 尺码不合适
    LATE_DELIVERY = "late_delivery"  # 发货速度慢
    OTHER = "other"                  # 其他原因


# ==================== 基础模型 ====================

class Address(BaseModel):
    """收货地址"""
    receiver: str = Field(..., description="收货人姓名")
    phone: str = Field(..., description="收货人手机号")
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    district: str = Field(..., description="区县")
    detail: str = Field(..., description="详细地址")
    zip_code: Optional[str] = Field(None, description="邮编")
    
    def format_address(self) -> str:
        """格式化地址"""
        return f"{self.province}{self.city}{self.district}{self.detail}"


class ProductSpec(BaseModel):
    """商品规格"""
    name: str = Field(..., description="规格名称")
    value: str = Field(..., description="规格值")


class OrderItem(BaseModel):
    """订单商品项"""
    # 商品基本信息
    item_id: str = Field(..., description="订单项ID")
    product_id: str = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    product_code: str = Field(..., description="商品编码")
    sku: str = Field(..., description="SKU编码")
    
    # 规格信息
    specs: List[ProductSpec] = Field(default=[], description="规格列表")
    spec_text: str = Field("", description="规格文本描述")
    
    # 价格信息
    unit_price: float = Field(..., description="单价")
    quantity: int = Field(..., description="数量")
    total_price: float = Field(..., description="小计金额")
    discount_amount: float = Field(0.0, description="优惠金额")
    
    # 商品图片
    image_url: str = Field("", description="商品图片URL")
    
    # 售后信息
    after_sale_status: AfterSaleStatus = Field(AfterSaleStatus.NONE, description="售后状态")
    refund_amount: Optional[float] = Field(None, description="退款金额")


class LogisticsInfo(BaseModel):
    """物流信息"""
    # 物流公司信息
    carrier_code: str = Field(..., description="物流公司代码")
    carrier_name: str = Field(..., description="物流公司名称")
    
    # 运单信息
    tracking_number: str = Field(..., description="运单号")
    tracking_url: Optional[str] = Field(None, description="物流查询链接")
    
    # 物流状态
    status: LogisticsStatus = Field(LogisticsStatus.PENDING, description="物流状态")
    status_text: str = Field("待发货", description="物流状态文本")
    
    # 时间信息
    ship_time: Optional[datetime] = Field(None, description="发货时间")
    receive_time: Optional[datetime] = Field(None, description="签收时间")
    estimated_delivery: Optional[datetime] = Field(None, description="预计送达时间")
    
    # 最新物流信息
    latest_update: str = Field("", description="最新物流更新")
    latest_time: Optional[datetime] = Field(None, description="最新更新时间")
    
    # 物流轨迹
    tracking_history: List[Dict[str, Any]] = Field(default=[], description="物流轨迹")
    
    def add_tracking_record(self, time: str, desc: str) -> None:
        """添加物流轨迹记录"""
        self.tracking_history.append({
            "time": time,
            "description": desc
        })


class PaymentInfo(BaseModel):
    """支付信息"""
    # 支付金额
    total_amount: float = Field(..., description="订单总金额")
    discount_amount: float = Field(0.0, description="优惠金额")
    shipping_fee: float = Field(0.0, description="运费")
    tax_amount: float = Field(0.0, description="税费")
    pay_amount: float = Field(..., description="实付金额")
    
    # 支付详情
    payment_method: Optional[str] = Field(None, description="支付方式")
    payment_time: Optional[datetime] = Field(None, description="支付时间")
    payment_no: Optional[str] = Field(None, description="支付流水号")
    
    # 优惠信息
    coupons: List[Dict[str, Any]] = Field(default=[], description="使用的优惠券")
    promotion_info: str = Field("", description="促销信息")


class AfterSaleRecord(BaseModel):
    """售后记录"""
    # 售后基本信息
    record_id: str = Field(..., description="售后记录ID")
    type: str = Field(..., description="售后类型：退款/退货/换货")
    status: AfterSaleStatus = Field(AfterSaleStatus.APPLYING, description="售后状态")
    
    # 申请信息
    apply_time: datetime = Field(..., description="申请时间")
    reason: RefundReason = Field(..., description="退款原因")
    reason_text: str = Field("", description="原因描述")
    description: str = Field("", description="详细说明")
    
    # 金额信息
    refund_amount: float = Field(..., description="申请退款金额")
    actual_refund: Optional[float] = Field(None, description="实际退款金额")
    
    # 处理信息
    process_time: Optional[datetime] = Field(None, description="处理时间")
    process_result: str = Field("", description="处理结果")
    process_note: str = Field("", description="处理备注")
    
    # 物流信息（退货时使用）
    return_tracking: Optional[str] = Field(None, description="退货物流单号")
    return_carrier: Optional[str] = Field(None, description="退货物流公司")


# ==================== 核心订单模型 ====================

class Order(BaseModel):
    """
    订单完整数据模型
    
    包含订单的所有信息：基本信息、商品信息、支付信息、物流信息、售后信息
    """
    
    # ========== 核心字段 ==========
    
    # 订单标识
    order_id: str = Field(..., description="订单ID")
    order_number: str = Field(..., description="订单编号")
    order_sn: str = Field("", description="订单序列号")
    
    # 关联信息
    user_id: str = Field(..., description="用户ID")
    phone: str = Field(..., description="用户手机号")
    
    # 订单状态
    status: OrderStatus = Field(..., description="订单状态")
    status_text: str = Field("", description="状态文本")
    status_desc: str = Field("", description="状态描述")
    
    # 时间戳
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    paid_at: Optional[datetime] = Field(None, description="支付时间")
    shipped_at: Optional[datetime] = Field(None, description="发货时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    cancelled_at: Optional[datetime] = Field(None, description="取消时间")
    
    # ========== 商品信息 ==========
    
    items: List[OrderItem] = Field(default=[], description="订单商品列表")
    item_count: int = Field(0, description="商品种类数")
    total_quantity: int = Field(0, description="商品总数量")
    
    # ========== 支付信息 ==========
    
    payment: PaymentInfo = Field(..., description="支付信息")
    payment_status: PaymentStatus = Field(PaymentStatus.UNPAID, description="支付状态")
    
    # ========== 物流信息 ==========
    
    logistics: Optional[LogisticsInfo] = Field(None, description="物流信息")
    
    # ========== 收货信息 ==========
    
    address: Address = Field(..., description="收货地址")
    delivery_remark: str = Field("", description="配送备注")
    
    # ========== 售后信息 ==========
    
    after_sale: AfterSaleStatus = Field(AfterSaleStatus.NONE, description="售后状态")
    after_sale_records: List[AfterSaleRecord] = Field(default=[], description="售后记录列表")
    
    # ========== 其他信息 ==========
    
    source: str = Field("app", description="订单来源")
    remark: str = Field("", description="订单备注")
    tags: List[str] = Field(default=[], description="订单标签")
    
    # ========== 扩展字段 ==========
    
    extra_data: Dict[str, Any] = Field(default={}, description="扩展数据")
    
    class Config:
        """Pydantic 配置"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    # ========== 便捷方法 ==========
    
    def get_main_product(self) -> Optional[OrderItem]:
        """获取主商品（第一个商品）"""
        if self.items:
            return self.items[0]
        return None
    
    def get_product_names(self) -> str:
        """获取商品名称列表"""
        return "、".join([item.product_name for item in self.items])
    
    def is_paid(self) -> bool:
        """是否已支付"""
        return self.payment_status == PaymentStatus.PAID
    
    def is_shipped(self) -> bool:
        """是否已发货"""
        return self.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.COMPLETED]
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == OrderStatus.COMPLETED
    
    def can_cancel(self) -> bool:
        """是否可以取消"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PAID]
    
    def can_refund(self) -> bool:
        """是否可以退款"""
        return self.status in [OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED]
    
    def get_status_timeline(self) -> List[Dict[str, str]]:
        """获取订单状态时间线"""
        timeline = []
        
        timeline.append({
            "status": "订单创建",
            "time": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "desc": "订单已创建"
        })
        
        if self.paid_at:
            timeline.append({
                "status": "订单支付",
                "time": self.paid_at.strftime("%Y-%m-%d %H:%M:%S"),
                "desc": f"支付金额：¥{self.payment.pay_amount}"
            })
        
        if self.shipped_at:
            timeline.append({
                "status": "订单发货",
                "time": self.shipped_at.strftime("%Y-%m-%d %H:%M:%S"),
                "desc": f"物流公司：{self.logistics.carrier_name if self.logistics else '未知'}"
            })
        
        if self.completed_at:
            timeline.append({
                "status": "订单完成",
                "time": self.completed_at.strftime("%Y-%m-%d %H:%M:%S"),
                "desc": "订单已完成"
            })
        
        return timeline
    
    def to_summary(self) -> Dict[str, Any]:
        """转换为订单摘要"""
        return {
            "order_number": self.order_number,
            "status": self.status_text,
            "total_amount": self.payment.total_amount,
            "pay_amount": self.payment.pay_amount,
            "product_names": self.get_product_names(),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "can_cancel": self.can_cancel(),
            "can_refund": self.can_refund()
        }
    
    def to_ai_response(self) -> str:
        """生成 AI 客服回复文本"""
        lines = [
            f"订单号：{self.order_number}",
            f"订单状态：{self.status_text}",
            f"商品信息：{self.get_product_names()}",
            f"订单金额：¥{self.payment.pay_amount}",
            f"创建时间：{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        if self.logistics and self.is_shipped():
            lines.extend([
                f"",
                f"物流信息：",
                f"  物流公司：{self.logistics.carrier_name}",
                f"  运单号：{self.logistics.tracking_number}",
                f"  物流状态：{self.logistics.status_text}"
            ])
            
            if self.logistics.receive_time:
                lines.append(f"  签收时间：{self.logistics.receive_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.after_sale_records:
            record = self.after_sale_records[-1]
            lines.extend([
                f"",
                f"售后信息：",
                f"  售后类型：{record.type}",
                f"  售后状态：{record.status.value}",
                f"  退款原因：{record.reason_text}",
                f"  退款金额：¥{record.refund_amount}"
            ])
        
        return "\n".join(lines)


# ==================== 订单查询结果模型 ====================

class OrderQueryResult(BaseModel):
    """订单查询结果"""
    success: bool = Field(True, description="是否成功")
    phone: str = Field("", description="查询手机号")
    total_count: int = Field(0, description="订单总数")
    orders: List[Order] = Field(default=[], description="订单列表")
    message: str = Field("", description="提示信息")
    query_time: float = Field(0.0, description="查询耗时")


class OrderStatistics(BaseModel):
    """订单统计信息"""
    total_orders: int = Field(0, description="总订单数")
    pending_payment: int = Field(0, description="待付款订单数")
    pending_shipment: int = Field(0, description="待发货订单数")
    pending_receipt: int = Field(0, description="待收货订单数")
    completed: int = Field(0, description="已完成订单数")
    after_sale: int = Field(0, description="售后中订单数")
    total_amount: float = Field(0.0, description="累计消费金额")


# ==================== 状态映射工具 ====================

class OrderStatusMapper:
    """订单状态映射器"""
    
    STATUS_MAP = {
        OrderStatus.PENDING: {"text": "待付款", "desc": "订单已创建，等待付款"},
        OrderStatus.PAID: {"text": "已付款", "desc": "订单已付款，等待发货"},
        OrderStatus.SHIPPED: {"text": "已发货", "desc": "商品已发出，运输中"},
        OrderStatus.DELIVERED: {"text": "已送达", "desc": "商品已送达，等待签收"},
        OrderStatus.COMPLETED: {"text": "已完成", "desc": "订单已完成"},
        OrderStatus.CANCELLED: {"text": "已取消", "desc": "订单已取消"},
        OrderStatus.REFUNDING: {"text": "退款中", "desc": "退款申请处理中"},
        OrderStatus.REFUNDED: {"text": "已退款", "desc": "退款已完成"},
        OrderStatus.RETURNING: {"text": "退货中", "desc": "退货处理中"},
        OrderStatus.RETURNED: {"text": "已退货", "desc": "退货已完成"}
    }
    
    LOGISTICS_STATUS_MAP = {
        LogisticsStatus.PENDING: {"text": "待发货", "desc": "等待商家发货"},
        LogisticsStatus.PICKED: {"text": "已揽收", "desc": "快递公司已揽收"},
        LogisticsStatus.TRANSIT: {"text": "运输中", "desc": "商品运输中"},
        LogisticsStatus.DELIVERING: {"text": "派送中", "desc": "快递员正在派送"},
        LogisticsStatus.DELIVERED: {"text": "已送达", "desc": "商品已送达"},
        LogisticsStatus.SIGNED: {"text": "已签收", "desc": "商品已签收"},
        LogisticsStatus.EXCEPTION: {"text": "异常", "desc": "物流异常"}
    }
    
    REFUND_REASON_MAP = {
        RefundReason.WRONG_ITEM: "商品错发/漏发",
        RefundReason.QUALITY: "商品质量问题",
        RefundReason.NOT_MATCH: "商品与描述不符",
        RefundReason.CHANGE_MIND: "不想要了",
        RefundReason.WRONG_SIZE: "尺码不合适",
        RefundReason.LATE_DELIVERY: "发货速度慢",
        RefundReason.OTHER: "其他原因"
    }
    
    @classmethod
    def get_status_info(cls, status: OrderStatus) -> Dict[str, str]:
        """获取状态信息"""
        return cls.STATUS_MAP.get(status, {"text": "未知", "desc": "未知状态"})
    
    @classmethod
    def get_logistics_info(cls, status: LogisticsStatus) -> Dict[str, str]:
        """获取物流状态信息"""
        return cls.LOGISTICS_STATUS_MAP.get(status, {"text": "未知", "desc": "未知状态"})
    
    @classmethod
    def get_refund_reason(cls, reason: RefundReason) -> str:
        """获取退款原因文本"""
        return cls.REFUND_REASON_MAP.get(reason, "其他原因")


# ==================== 便捷函数 ====================

def create_order_from_dict(data: Dict[str, Any]) -> Order:
    """从字典创建订单对象"""
    return Order(**data)


def format_order_for_display(order: Order) -> str:
    """格式化订单用于显示"""
    return order.to_ai_response()
