"""
RAG 知识库实现
功能：
- 文档上传
- 文本分块
- 向量化
- 存入向量库
- 用户问题检索
- 召回最相关的文档块
- 返回原文给大模型
"""

import os
import time
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from .models import Document, DocumentChunk
from .vector_store import VectorStore, text_splitter


class RAGManager:
    """RAG 管理类"""
    
    def __init__(self, db: Session, vector_store: VectorStore):
        self.db = db
        self.vector_store = vector_store
    
    def upload_document(self, title: str, content: str, 
                       file_name: str, file_type: str) -> Document:
        """
        上传文档
        
        Args:
            title: 文档标题
            content: 文档内容
            file_name: 文件名
            file_type: 文件类型
            
        Returns:
            文档对象
        """
        # 创建文档记录
        document = Document(
            title=title,
            content=content,
            file_name=file_name,
            file_type=file_type,
            created_at=str(int(time.time()))
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        # 文本分块
        chunks = text_splitter(content)
        
        # 保存分块
        document_chunks = []
        start_pos = 0
        for i, chunk_content in enumerate(chunks):
            end_pos = start_pos + len(chunk_content)
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_content=chunk_content,
                chunk_index=i,
                start_pos=start_pos,
                end_pos=end_pos
            )
            self.db.add(chunk)
            document_chunks.append(chunk)
            start_pos = end_pos
        
        self.db.commit()
        
        # 更新文档的分块数量
        document.chunk_count = len(document_chunks)
        self.db.commit()
        
        # 向向量库添加向量
        self.vector_store.add_document(document, document_chunks)
        
        return document
    
    def search_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        搜索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回数量
            
        Returns:
            搜索结果列表
        """
        # 向量搜索
        vector_results = self.vector_store.search(query, top_k)
        
        # 丰富结果，添加原文信息
        results = []
        for result in vector_results:
            # 获取文档信息
            document = self.db.query(Document).filter(
                Document.id == result["document_id"]
            ).first()
            
            if document:
                results.append({
                    "document_id": document.id,
                    "title": document.title,
                    "content": result["content"],
                    "score": result["score"],
                    "file_name": document.file_name
                })
        
        return results
    
    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """
        根据ID获取文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档对象
        """
        return self.db.query(Document).filter(
            Document.id == document_id
        ).first()
    
    def get_all_documents(self) -> List[Dict]:
        """
        获取所有文档
        
        Returns:
            文档列表
        """
        documents = self.db.query(Document).all()
        results = []
        for doc in documents:
            results.append({
                "id": doc.id,
                "title": doc.title,
                "file_name": doc.file_name,
                "file_type": doc.file_type,
                "chunk_count": doc.chunk_count,
                "created_at": doc.created_at
            })
        return results
    
    def delete_document(self, document_id: int) -> bool:
        """
        删除文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            是否删除成功
        """
        # 删除文档分块
        self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete()
        
        # 删除文档
        document = self.db.query(Document).filter(
            Document.id == document_id
        ).first()
        if not document:
            return False
        
        self.db.delete(document)
        self.db.commit()
        
        # 注意：这里没有从向量库中删除向量
        # 实际生产环境中需要实现向量库的删除功能
        
        return True


def get_rag_manager(db: Session, vector_store: VectorStore) -> RAGManager:
    """
    获取RAG管理器实例
    
    Args:
        db: 数据库会话
        vector_store: 向量库实例
        
    Returns:
        RAGManager实例
    """
    return RAGManager(db, vector_store)
