"""
基础数据访问层
提供最基础的增删改查接口
代码极简、轻量化，不包含任何模型、向量、向量化逻辑
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from .models import (
    User,
    FAQ,
    Conversation,
    Order,
    OrderItem,
    Logistics,
    AfterSale,
    Document,
    Knowledge,
    Category,
    Config,
    OrderStatus,
    AfterSaleStatus
)


class BaseRepository:
    """基础仓库类"""
    
    def __init__(self, db: Session):
        self.db = db


class UserRepository(BaseRepository):
    """用户数据访问"""
    
    def create(self, phone: str, username: str = None, 
               name: str = None, address: str = None, 
               email: str = None) -> Dict:
        """创建用户"""
        user = User(
            phone=phone,
            username=username,
            name=name,
            address=address,
            email=email
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._to_dict(user)
    
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """根据ID获取用户"""
        user = self.db.query(User).filter(User.id == user_id).first()
        return self._to_dict(user) if user else None
    
    def get_by_phone(self, phone: str) -> Optional[Dict]:
        """根据手机号获取用户"""
        user = self.db.query(User).filter(User.phone == phone).first()
        return self._to_dict(user) if user else None
    
    def update(self, user_id: int, **kwargs) -> Dict:
        """更新用户信息"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "message": "用户不存在"}
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return {"success": True, "user": self._to_dict(user)}
    
    def delete(self, user_id: int) -> Dict:
        """删除用户"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "message": "用户不存在"}
        
        self.db.delete(user)
        self.db.commit()
        return {"success": True, "message": "用户删除成功"}
    
    def _to_dict(self, user: User) -> Dict:
        """转换为字典"""
        return {
            "id": user.id,
            "phone": user.phone,
            "username": user.username,
            "name": user.name,
            "address": user.address,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }


class FAQRepository(BaseRepository):
    """FAQ数据访问"""
    
    def create(self, question: str, answer: str, keywords: List[str]) -> Dict:
        """创建FAQ"""
        faq = FAQ(
            question=question,
            answer=answer,
            keywords=' '.join(keywords)
        )
        self.db.add(faq)
        self.db.commit()
        self.db.refresh(faq)
        return self._to_dict(faq)
    
    def get_by_id(self, faq_id: int) -> Optional[Dict]:
        """根据ID获取FAQ"""
        faq = self.db.query(FAQ).filter(FAQ.id == faq_id).first()
        return self._to_dict(faq) if faq else None
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """搜索FAQ"""
        # 简单的关键词匹配
        query_words = query.split()
        conditions = []
        for word in query_words:
            conditions.append(FAQ.keywords.like(f"%{word}%"))
        
        faqs = self.db.query(FAQ).filter(or_(*conditions)).limit(limit).all()
        return [self._to_dict(faq) for faq in faqs]
    
    def update(self, faq_id: int, **kwargs) -> Dict:
        """更新FAQ"""
        faq = self.db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            return {"success": False, "message": "FAQ不存在"}
        
        if 'keywords' in kwargs and isinstance(kwargs['keywords'], list):
            kwargs['keywords'] = ' '.join(kwargs['keywords'])
        
        for key, value in kwargs.items():
            if hasattr(faq, key):
                setattr(faq, key, value)
        
        self.db.commit()
        self.db.refresh(faq)
        return {"success": True, "faq": self._to_dict(faq)}
    
    def delete(self, faq_id: int) -> Dict:
        """删除FAQ"""
        faq = self.db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            return {"success": False, "message": "FAQ不存在"}
        
        self.db.delete(faq)
        self.db.commit()
        return {"success": True, "message": "FAQ删除成功"}
    
    def _to_dict(self, faq: FAQ) -> Dict:
        """转换为字典"""
        return {
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer,
            "keywords": faq.keywords.split(),
            "created_at": faq.created_at.isoformat() if faq.created_at else None
        }


class ConversationRepository(BaseRepository):
    """对话记录数据访问"""
    
    def create(self, user_id: int, session_id: str, 
               message: str, sender: str, intent: str = None) -> Dict:
        """创建对话记录"""
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            message=message,
            sender=sender,
            intent=intent
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return self._to_dict(conversation)
    
    def get_by_session(self, session_id: str, limit: int = 50) -> List[Dict]:
        """获取会话的对话记录"""
        conversations = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.created_at.desc()).limit(limit).all()
        return [self._to_dict(conv) for conv in reversed(conversations)]
    
    def _to_dict(self, conversation: Conversation) -> Dict:
        """转换为字典"""
        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "session_id": conversation.session_id,
            "message": conversation.message,
            "sender": conversation.sender,
            "intent": conversation.intent,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None
        }


class OrderRepository(BaseRepository):
    """订单数据访问"""
    
    def create(self, user_id: int, order_no: str, 
               total_amount: float, status: str = "pending") -> Dict:
        """创建订单"""
        order = Order(
            user_id=user_id,
            order_no=order_no,
            total_amount=total_amount,
            status=OrderStatus(status)
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return self._to_dict(order)
    
    def get_by_id(self, order_id: int) -> Optional[Dict]:
        """根据ID获取订单"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        return self._to_dict(order) if order else None
    
    def get_by_order_no(self, order_no: str) -> Optional[Dict]:
        """根据订单号获取订单"""
        order = self.db.query(Order).filter(Order.order_no == order_no).first()
        return self._to_dict(order) if order else None
    
    def get_by_user(self, user_id: int, limit: int = 20) -> List[Dict]:
        """获取用户的订单"""
        orders = self.db.query(Order).filter(
            Order.user_id == user_id
        ).order_by(Order.created_at.desc()).limit(limit).all()
        return [self._to_dict(order) for order in orders]
    
    def update_status(self, order_id: int, status: str) -> Dict:
        """更新订单状态"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"success": False, "message": "订单不存在"}
        
        order.status = OrderStatus(status)
        self.db.commit()
        self.db.refresh(order)
        return {"success": True, "order": self._to_dict(order)}
    
    def _to_dict(self, order: Order) -> Dict:
        """转换为字典"""
        return {
            "id": order.id,
            "user_id": order.user_id,
            "order_no": order.order_no,
            "total_amount": order.total_amount,
            "status": order.status.value if order.status else None,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }


class OrderItemRepository(BaseRepository):
    """订单商品数据访问"""
    
    def create(self, order_id: int, product_id: int, 
               product_name: str, quantity: int, price: float) -> Dict:
        """创建订单商品"""
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            price=price
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return self._to_dict(item)
    
    def get_by_order(self, order_id: int) -> List[Dict]:
        """获取订单的商品"""
        items = self.db.query(OrderItem).filter(
            OrderItem.order_id == order_id
        ).all()
        return [self._to_dict(item) for item in items]
    
    def _to_dict(self, item: OrderItem) -> Dict:
        """转换为字典"""
        return {
            "id": item.id,
            "order_id": item.order_id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "price": item.price
        }


class LogisticsRepository(BaseRepository):
    """物流数据访问"""
    
    def create(self, order_id: int, logistics_company: str, 
               tracking_number: str, status: str = "pending") -> Dict:
        """创建物流信息"""
        logistics = Logistics(
            order_id=order_id,
            logistics_company=logistics_company,
            tracking_number=tracking_number,
            status=status
        )
        self.db.add(logistics)
        self.db.commit()
        self.db.refresh(logistics)
        return self._to_dict(logistics)
    
    def get_by_order(self, order_id: int) -> Optional[Dict]:
        """根据订单ID获取物流信息"""
        logistics = self.db.query(Logistics).filter(
            Logistics.order_id == order_id
        ).first()
        return self._to_dict(logistics) if logistics else None
    
    def update_status(self, order_id: int, status: str) -> Dict:
        """更新物流状态"""
        logistics = self.db.query(Logistics).filter(
            Logistics.order_id == order_id
        ).first()
        if not logistics:
            return {"success": False, "message": "物流信息不存在"}
        
        logistics.status = status
        self.db.commit()
        self.db.refresh(logistics)
        return {"success": True, "logistics": self._to_dict(logistics)}
    
    def _to_dict(self, logistics: Logistics) -> Dict:
        """转换为字典"""
        return {
            "id": logistics.id,
            "order_id": logistics.order_id,
            "logistics_company": logistics.logistics_company,
            "tracking_number": logistics.tracking_number,
            "status": logistics.status,
            "created_at": logistics.created_at.isoformat() if logistics.created_at else None
        }


class AfterSaleRepository(BaseRepository):
    """售后数据访问"""
    
    def create(self, order_id: int, user_id: int, 
               type: str, reason: str) -> Dict:
        """创建售后申请"""
        after_sale = AfterSale(
            order_id=order_id,
            user_id=user_id,
            type=type,
            reason=reason,
            status=AfterSaleStatus.PENDING
        )
        self.db.add(after_sale)
        self.db.commit()
        self.db.refresh(after_sale)
        return self._to_dict(after_sale)
    
    def get_by_id(self, after_sale_id: int) -> Optional[Dict]:
        """根据ID获取售后申请"""
        after_sale = self.db.query(AfterSale).filter(
            AfterSale.id == after_sale_id
        ).first()
        return self._to_dict(after_sale) if after_sale else None
    
    def get_by_order(self, order_id: int) -> List[Dict]:
        """获取订单的售后申请"""
        after_sales = self.db.query(AfterSale).filter(
            AfterSale.order_id == order_id
        ).all()
        return [self._to_dict(af) for af in after_sales]
    
    def update_status(self, after_sale_id: int, status: str) -> Dict:
        """更新售后状态"""
        after_sale = self.db.query(AfterSale).filter(
            AfterSale.id == after_sale_id
        ).first()
        if not after_sale:
            return {"success": False, "message": "售后申请不存在"}
        
        after_sale.status = AfterSaleStatus(status)
        self.db.commit()
        self.db.refresh(after_sale)
        return {"success": True, "after_sale": self._to_dict(after_sale)}
    
    def _to_dict(self, after_sale: AfterSale) -> Dict:
        """转换为字典"""
        return {
            "id": after_sale.id,
            "order_id": after_sale.order_id,
            "user_id": after_sale.user_id,
            "type": after_sale.type,
            "reason": after_sale.reason,
            "status": after_sale.status.value if after_sale.status else None,
            "created_at": after_sale.created_at.isoformat() if after_sale.created_at else None
        }


class DocumentRepository(BaseRepository):
    """文档数据访问"""
    
    def create(self, title: str) -> Dict:
        """创建文档"""
        document = Document(
            title=title
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return self._to_dict(document)
    
    def get_by_id(self, document_id: int) -> Optional[Dict]:
        """根据ID获取文档"""
        document = self.db.query(Document).filter(
            Document.id == document_id
        ).first()
        return self._to_dict(document) if document else None
    
    def get_all(self, limit: int = 50) -> List[Dict]:
        """获取所有文档"""
        documents = self.db.query(Document).order_by(Document.create_time.desc()).limit(limit).all()
        return [self._to_dict(doc) for doc in documents]
    
    def delete(self, document_id: int) -> Dict:
        """删除文档"""
        document = self.db.query(Document).filter(
            Document.id == document_id
        ).first()
        if not document:
            return {"success": False, "message": "文档不存在"}
        
        # 删除关联的内容碎片
        self.db.query(Knowledge).filter(Knowledge.document_id == document_id).delete()
        
        self.db.delete(document)
        self.db.commit()
        return {"success": True, "message": "文档删除成功"}
    
    def _to_dict(self, document: Document) -> Dict:
        """转换为字典"""
        return {
            "id": document.id,
            "title": document.title,
            "create_time": document.create_time.isoformat() if document.create_time else None
        }


class KnowledgeRepository(BaseRepository):
    """知识内容碎片数据访问"""
    
    def create(self, content: str, document_id: int) -> Dict:
        """创建内容碎片"""
        knowledge = Knowledge(
            content=content,
            document_id=document_id
        )
        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)
        return self._to_dict(knowledge)
    
    def get_by_id(self, knowledge_id: int) -> Optional[Dict]:
        """根据ID获取内容碎片"""
        knowledge = self.db.query(Knowledge).filter(
            Knowledge.id == knowledge_id
        ).first()
        return self._to_dict(knowledge) if knowledge else None
    
    def get_by_document(self, document_id: int) -> List[Dict]:
        """获取文档的内容碎片"""
        knowledge_list = self.db.query(Knowledge).filter(
            Knowledge.document_id == document_id
        ).order_by(Knowledge.id).all()
        return [self._to_dict(knowledge) for knowledge in knowledge_list]
    
    def update(self, knowledge_id: int, content: str) -> Dict:
        """更新内容碎片"""
        knowledge = self.db.query(Knowledge).filter(
            Knowledge.id == knowledge_id
        ).first()
        if not knowledge:
            return {"success": False, "message": "内容碎片不存在"}
        
        knowledge.content = content
        self.db.commit()
        self.db.refresh(knowledge)
        return {"success": True, "knowledge": self._to_dict(knowledge)}
    
    def delete(self, knowledge_id: int) -> Dict:
        """删除内容碎片"""
        knowledge = self.db.query(Knowledge).filter(
            Knowledge.id == knowledge_id
        ).first()
        if not knowledge:
            return {"success": False, "message": "内容碎片不存在"}
        
        self.db.delete(knowledge)
        self.db.commit()
        return {"success": True, "message": "内容碎片删除成功"}
    
    def _to_dict(self, knowledge: Knowledge) -> Dict:
        """转换为字典"""
        return {
            "id": knowledge.id,
            "content": knowledge.content,
            "document_id": knowledge.document_id,
            "created_at": knowledge.created_at.isoformat() if knowledge.created_at else None
        }
    
    def search(self, query: str, limit: int = 30) -> List[Dict]:
        """搜索内容碎片（模糊匹配）"""
        # 简单的模糊匹配
        query_words = query.split()
        conditions = []
        for word in query_words:
            conditions.append(Knowledge.content.like(f"%{word}%"))
        
        if conditions:
            knowledge_list = self.db.query(Knowledge).filter(
                or_(*conditions)
            ).limit(limit).all()
        else:
            # 当查询为空时，返回所有数据
            knowledge_list = self.db.query(Knowledge).limit(limit).all()
        
        return [self._to_dict(knowledge) for knowledge in knowledge_list]


class CategoryRepository(BaseRepository):
    """分类数据访问"""
    
    def create(self, category_name: str) -> Dict:
        """创建分类"""
        category = Category(category_name=category_name)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return self._to_dict(category)
    
    def get_by_id(self, category_id: int) -> Optional[Dict]:
        """根据ID获取分类"""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        return self._to_dict(category) if category else None
    
    def get_all(self) -> List[Dict]:
        """获取所有分类"""
        categories = self.db.query(Category).all()
        return [self._to_dict(cat) for cat in categories]
    
    def delete(self, category_id: int) -> Dict:
        """删除分类"""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return {"success": False, "message": "分类不存在"}
        
        self.db.delete(category)
        self.db.commit()
        return {"success": True, "message": "分类删除成功"}
    
    def _to_dict(self, category: Category) -> Dict:
        """转换为字典"""
        return {
            "id": category.id,
            "category_name": category.category_name,
            "created_at": category.created_at.isoformat() if category.created_at else None
        }


class ConfigRepository(BaseRepository):
    """配置数据访问"""
    
    def get_by_key(self, config_key: str) -> Optional[Dict]:
        """根据key获取配置"""
        config = self.db.query(Config).filter(Config.config_key == config_key).first()
        return self._to_dict(config) if config else None
    
    def get_all(self) -> List[Dict]:
        """获取所有配置"""
        configs = self.db.query(Config).all()
        return [self._to_dict(cfg) for cfg in configs]
    
    def set_value(self, config_key: str, config_value: str, description: str = None) -> Dict:
        """设置配置值"""
        config = self.db.query(Config).filter(Config.config_key == config_key).first()
        if config:
            config.config_value = config_value
            if description:
                config.description = description
        else:
            config = Config(
                config_key=config_key,
                config_value=config_value,
                description=description
            )
            self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return self._to_dict(config)
    
    def _to_dict(self, config: Config) -> Dict:
        """转换为字典"""
        return {
            "id": config.id,
            "config_key": config.config_key,
            "config_value": config.config_value,
            "description": config.description,
            "created_at": config.created_at.isoformat() if config.created_at else None,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        }


def get_repositories(db: Session) -> Dict[str, BaseRepository]:
    """获取所有仓库实例"""
    return {
        "user": UserRepository(db),
        "faq": FAQRepository(db),
        "conversation": ConversationRepository(db),
        "order": OrderRepository(db),
        "order_item": OrderItemRepository(db),
        "logistics": LogisticsRepository(db),
        "after_sale": AfterSaleRepository(db),
        "document": DocumentRepository(db),
        "knowledge": KnowledgeRepository(db),
        "category": CategoryRepository(db),
        "config": ConfigRepository(db)
    }
