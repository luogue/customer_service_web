"""
淘宝电商客服AI - 知识底座层数据库模型
基于淘宝客服知识库业务清单创建
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# 从 database.py 导入 Base、engine 和 SessionLocal，确保使用同一个实例
from .database import Base, engine, SessionLocal


class OrderStatus(enum.Enum):
    """订单状态"""
    PENDING = "pending"  # 待付款
    PAID = "paid"  # 已付款
    SHIPPED = "shipped"  # 已发货
    DELIVERED = "delivered"  # 已签收
    CANCELLED = "cancelled"  # 已取消


class AfterSaleStatus(enum.Enum):
    """售后状态"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝
    COMPLETED = "completed"  # 已完成


class AfterSaleType(enum.Enum):
    """售后类型"""
    REFUND = "refund"  # 仅退款
    RETURN_REFUND = "return_refund"  # 退货退款
    EXCHANGE = "exchange"  # 换货


class MonitorRecord(Base):
    """运维监控记录表"""
    __tablename__ = "monitor_records"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(255), nullable=False, index=True)  # 接口端点
    method = Column(String(10), nullable=False)  # 请求方法
    status = Column(String(20), nullable=False)  # 状态：success/failure
    response_time = Column(Float, nullable=False)  # 响应时间（毫秒）
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)  # 时间戳
    error_message = Column(Text, nullable=True)  # 错误信息（如果有）
    user_id = Column(String(100), nullable=True)  # 用户ID（如果有）


class Config(Base):
    """配置表"""
    __tablename__ = "configs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(255), nullable=False, unique=True, index=True)  # 配置键
    config_value = Column(Text, nullable=False)  # 配置值
    description = Column(Text, nullable=True)  # 配置描述
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间


class User(Base):
    """用户信息表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)  # 手机号
    username = Column(String(50), unique=True, index=True)  # 用户名
    name = Column(String(50))  # 真实姓名
    address = Column(Text)  # 收货地址
    email = Column(String(100))  # 邮箱
    role = Column(String(20), default="user")  # 角色
    is_member = Column(Boolean, default=False)  # 是否会员
    member_level = Column(String(20), default="normal")  # 会员等级
    points = Column(Integer, default=0)  # 积分
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class FAQ(Base):
    """FAQ表：常见问题和答案"""
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question = Column(String(500), nullable=False, index=True)  # 问题
    answer = Column(Text, nullable=False)  # 答案
    keywords = Column(String(2000), nullable=False, index=True)  # 关键词（空格分隔）
    category = Column(String(100), nullable=False, index=True)  # 分类
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Conversation(Base):
    """对话记录表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # 用户ID
    session_id = Column(String(100), index=True, nullable=False)  # 会话ID
    message = Column(Text, nullable=False)  # 消息内容
    sender = Column(String(20), nullable=False)  # 发送者（user/ai）
    intent = Column(String(100))  # 意图
    category = Column(String(100))  # 分类
    created_at = Column(DateTime, default=datetime.now, index=True)


class Product(Base):
    """商品表"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(String(50), unique=True, index=True, nullable=False)  # 商品ID
    name = Column(String(255), nullable=False, index=True)  # 商品名称
    description = Column(Text)  # 商品描述
    price = Column(Float, nullable=False)  # 价格
    stock = Column(Integer, nullable=False)  # 库存
    category = Column(String(100), index=True)  # 分类
    brand = Column(String(100))  # 品牌
    specifications = Column(Text)  # 规格参数
    material = Column(String(255))  # 材质
    warranty = Column(String(100))  # 保修信息
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Order(Base):
    """订单表"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # 用户ID
    order_no = Column(String(50), unique=True, index=True, nullable=False)  # 订单号
    total_amount = Column(Float, nullable=False)  # 总金额
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)  # 状态
    payment_method = Column(String(50))  # 支付方式
    shipping_address = Column(Text, nullable=False)  # 收货地址
    receiver_name = Column(String(50), nullable=False)  # 收货人姓名
    receiver_phone = Column(String(20), nullable=False)  # 收货人电话
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class OrderItem(Base):
    """订单商品表"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)  # 订单ID
    product_id = Column(Integer, ForeignKey("products.id"), index=True)  # 商品ID
    product_name = Column(String(255), nullable=False)  # 商品名称
    quantity = Column(Integer, nullable=False)  # 数量
    price = Column(Float, nullable=False)  # 单价
    created_at = Column(DateTime, default=datetime.now)


class Logistics(Base):
    """物流表"""
    __tablename__ = "logistics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, index=True)  # 订单ID
    logistics_company = Column(String(100))  # 物流公司
    tracking_number = Column(String(100), index=True)  # 物流单号
    status = Column(String(50), default="pending")  # 物流状态
    estimated_delivery = Column(DateTime)  # 预计送达时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AfterSale(Base):
    """售后表"""
    __tablename__ = "after_sales"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)  # 订单ID
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # 用户ID
    type = Column(Enum(AfterSaleType), nullable=False)  # 售后类型
    reason = Column(Text, nullable=False)  # 售后原因
    status = Column(Enum(AfterSaleStatus), default=AfterSaleStatus.PENDING, nullable=False)  # 状态
    refund_amount = Column(Float)  # 退款金额
    return_address = Column(Text)  # 退货地址
    tracking_number = Column(String(100))  # 退货物流单号
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Document(Base):
    """文档表：存储完整文档信息"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)  # 文档标题
    create_time = Column(DateTime, default=datetime.now)  # 创建时间
    
    # 关联到内容碎片
    chunks = relationship("Knowledge", back_populates="document")


class Knowledge(Base):
    """知识内容碎片表：存储文档的内容碎片"""
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(Text, nullable=False)  # 内容碎片
    document_id = Column(Integer, ForeignKey("documents.id"), index=True, nullable=False)  # 所属文档ID
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联到文档
    document = relationship("Document", back_populates="chunks")


class VectorIndex(Base):
    """向量索引表：存储向量索引信息"""
    __tablename__ = "vector_indices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chunk_id = Column(Integer, ForeignKey("knowledge.id"), unique=True, index=True, nullable=False)  # 关联到内容碎片
    vector_path = Column(String(255), nullable=False)  # 向量文件路径
    vector_dim = Column(Integer, nullable=False)  # 向量维度
    status = Column(String(20), default="indexed")  # 状态
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Category(Base):
    """分类表"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_name = Column(String(100), nullable=False, unique=True, index=True)  # 分类名称
    created_at = Column(DateTime, default=datetime.now)





class ConversationSession(Base):
    """会话表"""
    __tablename__ = "conversation_sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)  # 会话ID
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # 用户ID
    started_at = Column(DateTime, default=datetime.utcnow)  # 开始时间
    ended_at = Column(DateTime)  # 结束时间
    is_active = Column(Boolean, default=True)  # 是否活跃
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BusinessContext(Base):
    """业务上下文表"""
    __tablename__ = "business_contexts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)  # 会话ID
    current_intent = Column(String(100))  # 当前意图
    current_step = Column(String(100))  # 当前步骤
    current_node = Column(String(100))  # 当前节点
    user_phone = Column(String(20))  # 用户手机号
    user_id = Column(Integer)  # 用户ID
    selected_order = Column(String(50))  # 选中的订单
    order_list = Column(Text)  # 订单列表（JSON格式）
    intent_params = Column(Text)  # 意图参数（JSON格式）
    custom_params = Column(Text)  # 自定义参数（JSON格式）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Message(Base):
    """消息记录表"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), index=True, nullable=False)  # 会话ID
    role = Column(String(20), nullable=False)  # 角色（user/assistant/system）
    content = Column(Text, nullable=False)  # 消息内容
    type = Column(String(50), default="text")  # 消息类型
    created_at = Column(DateTime, default=datetime.utcnow)


class Promotion(Base):
    """营销活动表"""
    __tablename__ = "promotions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)  # 活动名称
    type = Column(String(100), nullable=False)  # 活动类型
    description = Column(Text)  # 活动描述
    start_time = Column(DateTime, nullable=False)  # 开始时间
    end_time = Column(DateTime, nullable=False)  # 结束时间
    rules = Column(Text)  # 活动规则
    status = Column(String(20), default="active")  # 状态
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Invoice(Base):
    """发票表"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)  # 订单ID
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # 用户ID
    invoice_type = Column(String(50), nullable=False)  # 发票类型
    title = Column(String(255), nullable=False)  # 发票抬头
    tax_number = Column(String(50))  # 纳税人识别号
    amount = Column(Float, nullable=False)  # 金额
    status = Column(String(20), default="pending")  # 状态
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PromptTemplate(Base):
    """Prompt模板表"""
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_name = Column(String(255), nullable=False, unique=True)  # 模板名
    template_content = Column(Text, nullable=False)  # 模板内容
    is_default = Column(Integer, default=0)  # 是否默认 0/1
    created_at = Column(DateTime, default=datetime.now)  # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("数据库表初始化完成")


def add_prompt_template_table():
    """添加Prompt模板表"""
    PromptTemplate.__table__.create(bind=engine, checkfirst=True)
    print("Prompt模板表添加完成")
