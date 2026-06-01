"""
RAG Pipeline 管理器
功能：
- 文档上传完整流程
- 文本分块
- 向量化（调用外部服务）
- 存入向量库
- 用户问题检索
- 召回最相关的文档块
- 返回原文给大模型
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from .faq_manager import FAQManager, get_faq_manager
from .document_manager import DocumentManager, TextSplitter, get_document_manager
from .vector_store import VectorStore, get_vector_store
from .models import DocumentChunk


class RAGPipeline:
    """RAG Pipeline 管理类
    
    完整的RAG流程：
    1. 文档上传
    2. 文本分块
    3. 向量化（调用外部服务）
    4. 存入向量库
    5. 用户问题检索
    6. 召回最相关的文档块
    7. 返回原文给大模型
    """
    
    def __init__(self, db: Session):
        """初始化RAG Pipeline
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.faq_manager = FAQManager(db)
        self.document_manager = DocumentManager(db)
        self.vector_store = VectorStore(db)
        self.text_splitter = TextSplitter()
    
    def process_document(self, title: str, content: str, 
                       file_name: str, file_type: str,
                       chunk_size: int = 500, 
                       chunk_overlap: int = 50) -> Dict:
        """处理文档完整流程
        
        流程：
        1. 上传文档到数据库
        2. 文本分块
        3. 保存分块到数据库
        4. 向量化处理（调用外部服务）
        5. 存入向量库
        6. 更新文档状态
        
        Args:
            title: 文档标题
            content: 文档内容
            file_name: 文件名
            file_type: 文件类型
            chunk_size: 分块大小
            chunk_overlap: 分块重叠大小
            
        Returns:
            处理结果
        """
        # 1. 上传文档
        doc_result = self.document_manager.upload_document(
            title=title,
            content=content,
            file_name=file_name,
            file_type=file_type
        )
        
        if not doc_result["success"]:
            return doc_result
        
        document_id = doc_result["document_id"]
        
        # 2. 文本分块
        chunks = self.text_splitter.split_text(content, chunk_size, chunk_overlap)
        
        # 3. 保存分块到数据库
        self.document_manager.add_chunks(document_id, chunks)
        
        # 4. 向量化处理（调用外部服务）
        # 注意：这里仅调用接口，实际向量化由外部服务完成
        try:
            texts = [chunk["content"] for chunk in chunks]
            vectors = self._encode_texts_external(texts)
            
            # 5. 存入向量库
            for i, chunk in enumerate(chunks):
                # 获取分块ID
                db_chunk = self.db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == document_id,
                    DocumentChunk.chunk_index == i
                ).first()
                
                if db_chunk and i < len(vectors):
                    # 创建向量索引
                    self.vector_store.create_vector_index(
                        chunk_id=db_chunk.id,
                        vector=vectors[i],
                        vector_dim=len(vectors[i])
                    )
            
            # 6. 更新文档状态
            self.document_manager.update_document_status(
                document_id=document_id,
                status="completed",
                chunk_count=len(chunks)
            )
            
            return {
                "success": True,
                "document_id": document_id,
                "title": title,
                "chunk_count": len(chunks),
                "status": "completed",
                "message": "文档处理完成"
            }
            
        except Exception as e:
            self.document_manager.update_document_status(
                document_id=document_id,
                status="failed"
            )
            return {
                "success": False,
                "message": f"文档处理失败: {str(e)}"
            }
    
    def query(self, question: str, top_k: int = 3) -> Dict:
        """综合查询
        
        流程：
        1. 先查询FAQ库（精准匹配）
        2. 如果FAQ没有匹配结果，查询RAG知识库（相似度匹配）
        3. 返回原文给大模型
        
        Args:
            question: 用户问题
            top_k: 返回数量
            
        Returns:
            查询结果
        """
        # 1. 查询FAQ库
        faq_results = self.faq_manager.search_by_keyword(question, top_k=top_k)
        
        if faq_results:
            return {
                "type": "faq",
                "source": "faq",
                "results": faq_results,
                "message": "从FAQ库中找到相关答案"
            }
        
        # 2. 查询RAG知识库（相似度匹配）
        rag_results = self._search_rag(question, top_k)
        
        return {
            "type": "rag",
            "source": "knowledge_base",
            "results": rag_results,
            "message": "从知识库中找到相关内容"
        }
    
    def _search_rag(self, query: str, top_k: int) -> List[Dict]:
        """RAG知识库搜索
        
        流程：
        1. 向量化查询文本（调用外部服务）
        2. 向量库检索
        3. 召回最相关的文档块
        4. 返回原文
        
        Args:
            query: 查询文本
            top_k: 返回数量
            
        Returns:
            搜索结果列表
        """
        # 1. 向量化查询文本
        try:
            query_vectors = self._encode_texts_external([query])
            query_vector = query_vectors[0] if query_vectors else []
        except Exception:
            return []
        
        # 2. 向量库检索
        vector_results = self.vector_store.search_vectors(query_vector, top_k)
        
        # 3. 召回最相关的文档块，返回原文
        results = []
        for result in vector_results:
            chunk = self.db.query(DocumentChunk).filter(
                DocumentChunk.id == result["chunk_id"]
            ).first()
            
            if chunk:
                # 获取完整文档信息
                document = self.document_manager.get_document_by_id(chunk.document_id)
                
                results.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "title": document["title"] if document else "",
                    "content": chunk.chunk_content,
                    "score": result["score"],
                    "file_name": document["file_name"] if document else ""
                })
        
        return results
    
    def _encode_texts_external(self, texts: List[str]) -> List[List[float]]:
        """调用外部服务进行文本向量化
        
        注意：
        - 本方法仅定义接口，实际向量化由外部服务完成
        - 可接入OpenAI、百度千帆等向量服务
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        # TODO: 实现调用外部向量服务
        # 示例：
        # from openai import OpenAI
        # client = OpenAI()
        # response = client.embeddings.create(
        #     model="text-embedding-ada-002",
        #     input=texts
        # )
        # return [item.embedding for item in response.data]
        
        # 返回空列表，实际使用需接入外部服务
        raise NotImplementedError("请实现外部向量服务调用")


def get_rag_pipeline(db: Session) -> RAGPipeline:
    """获取RAG Pipeline实例
    
    Args:
        db: 数据库会话
        
    Returns:
        RAGPipeline实例
    """
    return RAGPipeline(db)
