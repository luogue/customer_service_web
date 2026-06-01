"""
RAG原始文档库管理器
功能：
- 文档上传和存储
- 文本分块
- 文档管理和查询
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from .models import Document, DocumentChunk


class DocumentManager:
    """RAG原始文档库管理类"""
    
    def __init__(self, db: Session):
        """初始化文档管理器
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def upload_document(self, title: str, content: str, 
                       file_name: str, file_type: str) -> Dict:
        """上传文档
        
        Args:
            title: 文档标题
            content: 文档内容
            file_name: 文件名
            file_type: 文件类型
            
        Returns:
            包含文档信息的字典
        """
        from .config.config_manager import file_size_limit_config
        
        # 文件大小校验
        max_file_size_mb = file_size_limit_config.get_max_file_size_mb()
        max_text_chunk_size = file_size_limit_config.get_max_text_chunk_size()
        
        # 计算内容大小（假设1个字符=1字节）
        content_size_mb = len(content) / (1024 * 1024)
        if content_size_mb > max_file_size_mb:
            return {
                "success": False,
                "message": f"文件大小超过限制（最大 {max_file_size_mb}MB）"
            }
        
        # 文本块大小校验
        if len(content) > max_text_chunk_size:
            # 这里可以添加自动分块处理逻辑
            pass
        
        document = Document(
            title=title,
            content=content,
            file_name=file_name,
            file_type=file_type,
            status="pending"
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return {
            "success": True,
            "document_id": document.id,
            "title": document.title,
            "file_name": document.file_name,
            "status": document.status,
            "created_at": document.created_at.isoformat() if document.created_at else None
        }
    
    def get_document_by_id(self, document_id: int) -> Optional[Dict]:
        """根据ID获取文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档信息字典
        """
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None
        
        return {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "file_name": document.file_name,
            "file_type": document.file_type,
            "chunk_count": document.chunk_count,
            "status": document.status,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }
    
    def get_all_documents(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """获取所有文档
        
        Args:
            skip: 跳过数量
            limit: 返回数量
            
        Returns:
            文档列表
        """
        documents = self.db.query(Document).offset(skip).limit(limit).all()
        
        results = []
        for doc in documents:
            results.append({
                "id": doc.id,
                "title": doc.title,
                "file_name": doc.file_name,
                "file_type": doc.file_type,
                "chunk_count": doc.chunk_count,
                "status": doc.status,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            })
        return results
    
    def update_document_status(self, document_id: int, status: str, chunk_count: int = None) -> Dict:
        """更新文档状态
        
        Args:
            document_id: 文档ID
            status: 新状态
            chunk_count: 分块数量
            
        Returns:
            更新结果
        """
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {"success": False, "message": "文档不存在"}
        
        document.status = status
        if chunk_count is not None:
            document.chunk_count = chunk_count
        
        self.db.commit()
        
        return {
            "success": True,
            "document_id": document.id,
            "status": document.status,
            "chunk_count": document.chunk_count
        }
    
    def delete_document(self, document_id: int) -> Dict:
        """删除文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            删除结果
        """
        # 删除文档分块
        self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete()
        
        # 删除文档
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {"success": False, "message": "文档不存在"}
        
        self.db.delete(document)
        self.db.commit()
        
        return {"success": True, "message": "文档删除成功"}
    
    def add_chunks(self, document_id: int, chunks: List[Dict]) -> Dict:
        """添加文档分块
        
        Args:
            document_id: 文档ID
            chunks: 分块列表
            
        Returns:
            添加结果
        """
        for chunk_data in chunks:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_content=chunk_data["content"],
                chunk_index=chunk_data["index"],
                start_pos=chunk_data["start_pos"],
                end_pos=chunk_data["end_pos"]
            )
            self.db.add(chunk)
        
        self.db.commit()
        
        return {
            "success": True,
            "document_id": document_id,
            "chunk_count": len(chunks)
        }
    
    def get_chunks_by_document_id(self, document_id: int) -> List[Dict]:
        """根据文档ID获取分块
        
        Args:
            document_id: 文档ID
            
        Returns:
            分块列表
        """
        chunks = self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).all()
        
        results = []
        for chunk in chunks:
            results.append({
                "id": chunk.id,
                "document_id": chunk.document_id,
                "content": chunk.chunk_content,
                "index": chunk.chunk_index,
                "start_pos": chunk.start_pos,
                "end_pos": chunk.end_pos
            })
        return results


class TextSplitter:
    """文本分块器"""
    
    @staticmethod
    def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
        """文本分块
        
        Args:
            text: 文本内容
            chunk_size: 分块大小
            chunk_overlap: 分块重叠大小
            
        Returns:
            分块列表
        """
        from .config.config_manager import file_size_limit_config
        
        # 获取最大文本块大小配置
        max_text_chunk_size = file_size_limit_config.get_max_text_chunk_size()
        
        # 确保分块大小不超过最大限制
        chunk_size = min(chunk_size, max_text_chunk_size)
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            
            if end < text_length:
                punctuation = ".？！。?!"
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in punctuation:
                        end = i + 1
                        break
            
            chunk_content = text[start:end].strip()
            if chunk_content:
                # 确保分块不超过最大限制
                if len(chunk_content) > max_text_chunk_size:
                    # 进一步拆分过大的分块
                    sub_chunks = TextSplitter._split_large_chunk(chunk_content, max_text_chunk_size)
                    for i, sub_chunk in enumerate(sub_chunks):
                        chunks.append({
                            "content": sub_chunk,
                            "index": len(chunks),
                            "start_pos": start,
                            "end_pos": start + len(sub_chunk)
                        })
                else:
                    chunks.append({
                        "content": chunk_content,
                        "index": len(chunks),
                        "start_pos": start,
                        "end_pos": end
                    })
            
            start = end - chunk_overlap
        
        return chunks
    
    @staticmethod
    def _split_large_chunk(text: str, max_size: int) -> List[str]:
        """拆分过大的文本块
        
        Args:
            text: 文本内容
            max_size: 最大块大小
            
        Returns:
            拆分后的文本块列表
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + max_size, text_length)
            
            if end < text_length:
                punctuation = ".？！。?!"
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in punctuation:
                        end = i + 1
                        break
            
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append(chunk_content)
            
            start = end
        
        return chunks


def get_document_manager(db: Session) -> DocumentManager:
    """获取文档管理器实例
    
    Args:
        db: 数据库会话
        
    Returns:
        DocumentManager实例
    """
    return DocumentManager(db)
