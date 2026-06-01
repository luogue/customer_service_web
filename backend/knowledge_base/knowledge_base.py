"""
完整的RAG Pipeline
集成：
- FAQ 库
- RAG 知识库
- 向量库
- 整体查询流程
"""

from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from .faq_manager import FAQManager
from .rag_manager import RAGManager
from .vector_store import VectorStore


class KnowledgeBase:
    """知识底座层主类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.vector_store = VectorStore(db)
        self.faq_manager = FAQManager(db)
        self.rag_manager = RAGManager(db, self.vector_store)
    
    def query(self, question: str, top_k: int = 3) -> Dict:
        """
        综合查询
        1. 先查询FAQ库（精准匹配）
        2. 如果FAQ没有匹配结果，查询RAG知识库（相似度匹配）
        
        Args:
            question: 用户问题
            top_k: 返回数量
            
        Returns:
            查询结果
        """
        # 1. 查询FAQ库
        faq_results = self.faq_manager.search_by_keyword(question, top_k=top_k)
        
        if faq_results:
            # FAQ有匹配结果，直接返回
            return {
                "type": "faq",
                "results": faq_results,
                "message": "从FAQ库中找到相关答案"
            }
        
        # 2. 查询RAG知识库
        rag_results = self.rag_manager.search_documents(question, top_k=top_k)
        
        return {
            "type": "rag",
            "results": rag_results,
            "message": "从知识库中找到相关内容"
        }
    
    def upload_document(self, title: str, content: str, 
                       file_name: str, file_type: str) -> Dict:
        """
        上传文档到RAG知识库
        
        Args:
            title: 文档标题
            content: 文档内容
            file_name: 文件名
            file_type: 文件类型
            
        Returns:
            上传结果
        """
        try:
            document = self.rag_manager.upload_document(
                title=title,
                content=content,
                file_name=file_name,
                file_type=file_type
            )
            
            return {
                "success": True,
                "document_id": document.id,
                "title": document.title,
                "message": "文档上传成功"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"文档上传失败: {str(e)}"
            }
    
    def add_faq(self, question: str, answer: str, keywords: List[str]) -> Dict:
        """
        添加FAQ
        
        Args:
            question: 问题
            answer: 答案
            keywords: 关键词列表
            
        Returns:
            添加结果
        """
        try:
            faq = self.faq_manager.add_faq(
                question=question,
                answer=answer,
                keywords=keywords
            )
            
            return {
                "success": True,
                "faq_id": faq.id,
                "question": faq.question,
                "message": "FAQ添加成功"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"FAQ添加失败: {str(e)}"
            }
    
    def get_faqs(self) -> List[Dict]:
        """
        获取所有FAQ
        
        Returns:
            FAQ列表
        """
        return self.faq_manager.get_all_faqs()
    
    def get_documents(self) -> List[Dict]:
        """
        获取所有文档
        
        Returns:
            文档列表
        """
        return self.rag_manager.get_all_documents()
    
    def delete_document(self, document_id: int) -> Dict:
        """
        删除文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            删除结果
        """
        success = self.rag_manager.delete_document(document_id)
        if success:
            return {
                "success": True,
                "message": "文档删除成功"
            }
        else:
            return {
                "success": False,
                "message": "文档删除失败"
            }
    
    def delete_faq(self, faq_id: int) -> Dict:
        """
        删除FAQ
        
        Args:
            faq_id: FAQ ID
            
        Returns:
            删除结果
        """
        success = self.faq_manager.delete_faq(faq_id)
        if success:
            return {
                "success": True,
                "message": "FAQ删除成功"
            }
        else:
            return {
                "success": False,
                "message": "FAQ删除失败"
            }


def get_knowledge_base(db: Session) -> KnowledgeBase:
    """
    获取知识底座实例
    
    Args:
        db: 数据库会话
        
    Returns:
        KnowledgeBase实例
    """
    return KnowledgeBase(db)
