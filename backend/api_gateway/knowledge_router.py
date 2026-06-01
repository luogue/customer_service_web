"""
淘宝电商客服AI - 知识底座层 API 接口
只提供最基础的增删改查接口
代码极简、轻量化，不包含任何模型、向量、向量化逻辑
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel

from knowledge_base.models import get_db
from knowledge_base.repositories import get_repositories
from knowledge_base.vector_store import VectorStore
from knowledge_base.search_service import get_search_service
from ops_monitor.monitor_decorator import monitor_api


router = APIRouter(
    prefix="/api/knowledge",
    tags=["knowledge"],
    responses={404: {"description": "Not found"}},
)


# ============ 数据模型 ============

class UserCreate(BaseModel):
    """用户创建请求"""
    phone: str
    username: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None


class FAQCreate(BaseModel):
    """FAQ创建请求"""
    question: str
    answer: str
    keywords: List[str]


class ConversationCreate(BaseModel):
    """对话记录创建请求"""
    user_id: int
    session_id: str
    message: str
    sender: str
    intent: Optional[str] = None


class OrderCreate(BaseModel):
    """订单创建请求"""
    user_id: int
    order_no: str
    total_amount: float
    status: Optional[str] = "pending"


class OrderItemCreate(BaseModel):
    """订单商品创建请求"""
    order_id: int
    product_id: int
    product_name: str
    quantity: int
    price: float


class LogisticsCreate(BaseModel):
    """物流信息创建请求"""
    order_id: int
    logistics_company: str
    tracking_number: str
    status: Optional[str] = "pending"


class AfterSaleCreate(BaseModel):
    """售后申请创建请求"""
    order_id: int
    user_id: int
    type: str
    reason: str


class DocumentCreate(BaseModel):
    """文档创建请求"""
    title: str


class KnowledgeCreate(BaseModel):
    """知识内容碎片创建请求"""
    content: str
    document_id: int


class KnowledgeUpdate(BaseModel):
    """知识内容碎片更新请求"""
    content: str


class CategoryCreate(BaseModel):
    """分类创建请求"""
    category_name: str


class ConfigUpdate(BaseModel):
    """配置更新请求"""
    config_key: str
    config_value: str
    description: Optional[str] = None


class DocumentCategoryUpdate(BaseModel):
    """文档分类更新请求"""
    category_id: int


# ============ 通用响应模型 ============

class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool
    message: str


# ============ 用户接口 ============

@router.post("/users", summary="创建用户")
@monitor_api(endpoint="/api/knowledge/users")
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """创建新用户"""
    repos = get_repositories(db)
    result = repos["user"].create(
        phone=user.phone,
        username=user.username,
        name=user.name,
        address=user.address,
        email=user.email
    )
    return {"success": True, "user": result}


@router.get("/users/{user_id}", summary="获取用户信息")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取用户信息"""
    repos = get_repositories(db)
    user = repos["user"].get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.get("/users/phone/{phone}", summary="根据手机号获取用户")
async def get_user_by_phone(
    phone: str,
    db: Session = Depends(get_db)
):
    """根据手机号获取用户信息"""
    repos = get_repositories(db)
    user = repos["user"].get_by_phone(phone)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


# ============ FAQ 接口 ============

@router.post("/faqs", summary="创建FAQ")
async def create_faq(
    faq: FAQCreate,
    db: Session = Depends(get_db)
):
    """创建新的FAQ"""
    repos = get_repositories(db)
    result = repos["faq"].create(
        question=faq.question,
        answer=faq.answer,
        keywords=faq.keywords
    )
    return {"success": True, "faq": result}


@router.get("/faqs/{faq_id}", summary="获取FAQ")
async def get_faq(
    faq_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取FAQ"""
    repos = get_repositories(db)
    faq = repos["faq"].get_by_id(faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ不存在")
    return faq


@router.get("/faqs/search/{query}", summary="搜索FAQ")
async def search_faq(
    query: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """搜索FAQ"""
    repos = get_repositories(db)
    results = repos["faq"].search(query, limit)
    return {"success": True, "results": results}


# ============ 对话记录接口 ============

@router.post("/conversations", summary="创建对话记录")
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """创建新的对话记录"""
    repos = get_repositories(db)
    result = repos["conversation"].create(
        user_id=conversation.user_id,
        session_id=conversation.session_id,
        message=conversation.message,
        sender=conversation.sender,
        intent=conversation.intent
    )
    return {"success": True, "conversation": result}


@router.get("/conversations/session/{session_id}", summary="获取会话记录")
async def get_session_conversations(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取会话的对话记录"""
    repos = get_repositories(db)
    conversations = repos["conversation"].get_by_session(session_id, limit)
    return {"success": True, "conversations": conversations}


# ============ 订单接口 ============

@router.post("/orders", summary="创建订单")
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    """创建新订单"""
    repos = get_repositories(db)
    result = repos["order"].create(
        user_id=order.user_id,
        order_no=order.order_no,
        total_amount=order.total_amount,
        status=order.status
    )
    return {"success": True, "order": result}


@router.get("/orders/{order_id}", summary="获取订单")
async def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取订单"""
    repos = get_repositories(db)
    order = repos["order"].get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.get("/orders/user/{user_id}", summary="获取用户订单")
async def get_user_orders(
    user_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取用户的订单"""
    repos = get_repositories(db)
    orders = repos["order"].get_by_user(user_id, limit)
    return {"success": True, "orders": orders}


@router.post("/orders/{order_id}/status", summary="更新订单状态")
async def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """更新订单状态"""
    repos = get_repositories(db)
    result = repos["order"].update_status(order_id, status)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


# ============ 订单商品接口 ============

@router.post("/order-items", summary="创建订单商品")
async def create_order_item(
    item: OrderItemCreate,
    db: Session = Depends(get_db)
):
    """创建新的订单商品"""
    repos = get_repositories(db)
    result = repos["order_item"].create(
        order_id=item.order_id,
        product_id=item.product_id,
        product_name=item.product_name,
        quantity=item.quantity,
        price=item.price
    )
    return {"success": True, "item": result}


@router.get("/order-items/order/{order_id}", summary="获取订单商品")
async def get_order_items(
    order_id: int,
    db: Session = Depends(get_db)
):
    """获取订单的商品"""
    repos = get_repositories(db)
    items = repos["order_item"].get_by_order(order_id)
    return {"success": True, "items": items}


# ============ 物流接口 ============

@router.post("/logistics", summary="创建物流信息")
async def create_logistics(
    logistics: LogisticsCreate,
    db: Session = Depends(get_db)
):
    """创建新的物流信息"""
    repos = get_repositories(db)
    result = repos["logistics"].create(
        order_id=logistics.order_id,
        logistics_company=logistics.logistics_company,
        tracking_number=logistics.tracking_number,
        status=logistics.status
    )
    return {"success": True, "logistics": result}


@router.get("/logistics/order/{order_id}", summary="获取物流信息")
async def get_logistics(
    order_id: int,
    db: Session = Depends(get_db)
):
    """根据订单ID获取物流信息"""
    repos = get_repositories(db)
    logistics = repos["logistics"].get_by_order(order_id)
    if not logistics:
        raise HTTPException(status_code=404, detail="物流信息不存在")
    return logistics


# ============ 售后接口 ============

@router.post("/after-sales", summary="创建售后申请")
async def create_after_sale(
    after_sale: AfterSaleCreate,
    db: Session = Depends(get_db)
):
    """创建新的售后申请"""
    repos = get_repositories(db)
    result = repos["after_sale"].create(
        order_id=after_sale.order_id,
        user_id=after_sale.user_id,
        type=after_sale.type,
        reason=after_sale.reason
    )
    return {"success": True, "after_sale": result}


@router.get("/after-sales/{after_sale_id}", summary="获取售后申请")
async def get_after_sale(
    after_sale_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取售后申请"""
    repos = get_repositories(db)
    after_sale = repos["after_sale"].get_by_id(after_sale_id)
    if not after_sale:
        raise HTTPException(status_code=404, detail="售后申请不存在")
    return after_sale


@router.get("/after-sales/order/{order_id}", summary="获取订单售后申请")
async def get_order_after_sales(
    order_id: int,
    db: Session = Depends(get_db)
):
    """获取订单的售后申请"""
    repos = get_repositories(db)
    after_sales = repos["after_sale"].get_by_order(order_id)
    return {"success": True, "after_sales": after_sales}


# ============ 文档接口 ============

@router.post("/documents", summary="创建文档")
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """创建新的文档"""
    repos = get_repositories(db)
    result = repos["document"].create(
        title=document.title
    )
    return {"success": True, "document": result}


@router.get("/documents/{document_id}", summary="获取文档")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取文档"""
    repos = get_repositories(db)
    document = repos["document"].get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document


@router.get("/documents", summary="获取所有文档")
async def get_all_documents(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取所有文档"""
    repos = get_repositories(db)
    documents = repos["document"].get_all(limit)
    return {"success": True, "documents": documents}


@router.delete("/documents/{document_id}", summary="删除文档")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """删除文档"""
    repos = get_repositories(db)
    result = repos["document"].delete(document_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="文档不存在")
    return result


# ============ 知识内容碎片接口 ============

@router.post("/knowledge", summary="创建内容碎片")
async def create_knowledge(
    knowledge: KnowledgeCreate,
    db: Session = Depends(get_db)
):
    """创建新的内容碎片"""
    repos = get_repositories(db)
    result = repos["knowledge"].create(
        content=knowledge.content,
        document_id=knowledge.document_id
    )
    return {"success": True, "knowledge": result}


@router.get("/knowledge/{knowledge_id}", summary="获取内容碎片")
async def get_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取内容碎片"""
    repos = get_repositories(db)
    knowledge = repos["knowledge"].get_by_id(knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="内容碎片不存在")
    return knowledge


@router.get("/knowledge/document/{document_id}", summary="获取文档的内容碎片")
async def get_document_knowledge(
    document_id: int,
    db: Session = Depends(get_db)
):
    """获取文档的所有内容碎片"""
    repos = get_repositories(db)
    knowledge_list = repos["knowledge"].get_by_document(document_id)
    return {"success": True, "knowledge_list": knowledge_list}


@router.put("/knowledge/{knowledge_id}", summary="更新内容碎片")
async def update_knowledge(
    knowledge_id: int,
    update: KnowledgeUpdate,
    db: Session = Depends(get_db)
):
    """更新内容碎片"""
    repos = get_repositories(db)
    result = repos["knowledge"].update(knowledge_id, update.content)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.delete("/knowledge/{knowledge_id}", summary="删除内容碎片")
async def delete_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db)
):
    """删除内容碎片"""
    repos = get_repositories(db)
    result = repos["knowledge"].delete(knowledge_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


# ============ 分类接口 ============

@router.post("/categories", summary="创建分类")
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    """创建新分类"""
    repos = get_repositories(db)
    result = repos["category"].create(category_name=category.category_name)
    return {"success": True, "category": result}


@router.get("/categories", summary="获取所有分类")
async def get_all_categories(
    db: Session = Depends(get_db)
):
    """获取所有分类"""
    repos = get_repositories(db)
    categories = repos["category"].get_all()
    return {"success": True, "categories": categories}


@router.get("/categories/{category_id}", summary="获取分类")
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取分类"""
    repos = get_repositories(db)
    category = repos["category"].get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.delete("/categories/{category_id}", summary="删除分类")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """删除分类"""
    repos = get_repositories(db)
    result = repos["category"].delete(category_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="分类不存在")
    return result


# ============ 配置接口 ============

@router.get("/configs", summary="获取所有配置")
async def get_all_configs(
    db: Session = Depends(get_db)
):
    """获取所有配置"""
    repos = get_repositories(db)
    configs = repos["config"].get_all()
    return {"success": True, "configs": configs}


@router.get("/configs/{config_key}", summary="获取配置")
async def get_config(
    config_key: str,
    db: Session = Depends(get_db)
):
    """根据key获取配置"""
    repos = get_repositories(db)
    config = repos["config"].get_by_key(config_key)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config


@router.put("/configs", summary="更新配置")
async def update_config(
    config: ConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新配置"""
    repos = get_repositories(db)
    result = repos["config"].set_value(
        config_key=config.config_key,
        config_value=config.config_value,
        description=config.description
    )
    return {"success": True, "config": result}


# ============ 知识库检索接口 ============

@router.get("/search", summary="知识库检索")
async def search_knowledge(
    query: str,
    top_k: int = 10,
    threshold: float = 0.3,
    search_mode: str = "hybrid",
    db: Session = Depends(get_db)
):
    """知识库检索接口
    
    Args:
        query: 检索关键词/问题
        top_k: 最大检索结果数
        threshold: 相似度阈值
        search_mode: 检索模式 (text/vector/hybrid)
        
    Returns:
        检索结果列表
    """
    try:
        # 创建向量存储实例
        vector_store = VectorStore(db)
        
        # 获取检索服务实例
        search_service = get_search_service(db, vector_store)
        
        # 执行检索
        result = search_service.search(query, top_k, threshold, search_mode)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


# ============ 健康检查 ============

@router.get("/health", summary="健康检查")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "knowledge_base",
        "timestamp": "2026-03-09"
    }
