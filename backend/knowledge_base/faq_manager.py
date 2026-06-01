"""
FAQ库管理器
功能：
- FAQ增删改查
- 关键词精准匹配
- 毫秒级查询返回
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .models import FAQ


class FAQManager:
    """FAQ库管理类"""
    
    def __init__(self, db: Session):
        """初始化FAQ管理器
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def add_faq(self, question: str, answer: str, keywords: List[str]) -> Dict:
        """添加FAQ
        
        Args:
            question: 问题内容
            answer: 答案内容
            keywords: 关键词列表
            
        Returns:
            包含FAQ信息的字典
        """
        keywords_str = ' '.join(keywords)
        faq = FAQ(
            question=question,
            answer=answer,
            keywords=keywords_str
        )
        self.db.add(faq)
        self.db.commit()
        self.db.refresh(faq)
        
        return {
            "success": True,
            "faq_id": faq.id,
            "question": faq.question,
            "answer": faq.answer,
            "keywords": faq.keywords.split(),
            "created_at": faq.created_at.isoformat() if faq.created_at else None
        }
    
    def search_by_keyword(self, query: str, top_k: int = 5) -> List[Dict]:
        """根据关键词搜索FAQ（毫秒级返回）
        
        采用精准匹配策略：
        1. 提取查询中的关键词
        2. 使用LIKE进行关键词匹配
        3. 返回最相关的结果
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            FAQ列表
        """
        query_words = self._extract_keywords(query)
        
        if not query_words:
            return []
        
        # 构建关键词匹配查询
        search_conditions = []
        for word in query_words:
            search_conditions.append(FAQ.keywords.like(f"%{word}%"))
        
        # 执行查询
        faqs = self.db.query(FAQ).filter(
            or_(*search_conditions)
        ).limit(top_k).all()
        
        # 转换为字典格式
        results = []
        for faq in faqs:
            results.append({
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "keywords": faq.keywords.split(),
                "created_at": faq.created_at.isoformat() if faq.created_at else None
            })
        
        return results
    
    def get_faq_by_id(self, faq_id: int) -> Optional[Dict]:
        """根据ID获取FAQ
        
        Args:
            faq_id: FAQ ID
            
        Returns:
            FAQ信息字典
        """
        faq = self.db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            return None
        
        return {
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer,
            "keywords": faq.keywords.split(),
            "created_at": faq.created_at.isoformat() if faq.created_at else None,
            "updated_at": faq.updated_at.isoformat() if faq.updated_at else None
        }
    
    def get_all_faqs(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """获取所有FAQ
        
        Args:
            skip: 跳过数量
            limit: 返回数量
            
        Returns:
            FAQ列表
        """
        faqs = self.db.query(FAQ).offset(skip).limit(limit).all()
        
        results = []
        for faq in faqs:
            results.append({
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "keywords": faq.keywords.split(),
                "created_at": faq.created_at.isoformat() if faq.created_at else None
            })
        return results
    
    def update_faq(self, faq_id: int, question: str = None, 
                   answer: str = None, keywords: List[str] = None) -> Dict:
        """更新FAQ
        
        Args:
            faq_id: FAQ ID
            question: 新问题
            answer: 新答案
            keywords: 新关键词列表
            
        Returns:
            更新结果
        """
        faq = self.db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            return {"success": False, "message": "FAQ不存在"}
        
        if question:
            faq.question = question
        if answer:
            faq.answer = answer
        if keywords:
            faq.keywords = ' '.join(keywords)
        
        self.db.commit()
        self.db.refresh(faq)
        
        return {
            "success": True,
            "faq_id": faq.id,
            "message": "FAQ更新成功"
        }
    
    def delete_faq(self, faq_id: int) -> Dict:
        """删除FAQ
        
        Args:
            faq_id: FAQ ID
            
        Returns:
            删除结果
        """
        faq = self.db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            return {"success": False, "message": "FAQ不存在"}
        
        self.db.delete(faq)
        self.db.commit()
        
        return {"success": True, "message": "FAQ删除成功"}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取文本中的关键词
        
        Args:
            text: 文本
            
        Returns:
            关键词列表
        """
        import string
        punctuation = string.punctuation + '，。！？；：（）【】'
        text = ''.join([c if c not in punctuation else ' ' for c in text])
        words = text.strip().split()
        words = [word for word in words if word]
        return words


def get_faq_manager(db: Session) -> FAQManager:
    """获取FAQ管理器实例
    
    Args:
        db: 数据库会话
        
    Returns:
        FAQManager实例
    """
    return FAQManager(db)
