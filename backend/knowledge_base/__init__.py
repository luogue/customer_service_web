"""
知识底座层模块
包含：
- FAQ 库：MySQL 数据库存储，支持关键词精准匹配
- RAG 知识库：存储原始文档内容
- 向量库：存储文档分块向量索引
- RAG Pipeline：完整的文档处理和检索流程
"""

from .models import (
    Base,
    FAQ,
    Document,
    User,
    Conversation,
    Order,
    OrderItem,
    Logistics,
    AfterSale,
    get_db,
    init_db
)

from .repositories import (
    UserRepository,
    FAQRepository,
    ConversationRepository,
    OrderRepository,
    OrderItemRepository,
    LogisticsRepository,
    AfterSaleRepository,
    DocumentRepository,
    get_repositories
)


__all__ = [
    # 模型
    'Base',
    'User',
    'FAQ',
    'Conversation',
    'Order',
    'OrderItem',
    'Logistics',
    'AfterSale',
    'Document',
    'get_db',
    'init_db',
    
    # 仓库
    'UserRepository',
    'FAQRepository',
    'ConversationRepository',
    'OrderRepository',
    'OrderItemRepository',
    'LogisticsRepository',
    'AfterSaleRepository',
    'DocumentRepository',
    'get_repositories'
]
