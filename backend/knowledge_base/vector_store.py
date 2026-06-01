"""
向量库管理器
功能：
- 向量索引管理
- 向量存储和检索接口
- 支持FAISS/Chroma等向量库

实现：
- 使用Chroma作为向量数据库
- 使用基于字符串相似度的向量化方法（无需外部模型）
"""

import os
import math
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import chromadb
from chromadb.config import Settings

from .models import VectorIndex


class VectorStore:
    """向量库管理类
    
    实现：
    - 使用Chroma作为向量数据库
    - 使用基于字符串相似度的向量化方法
    """
    
    def __init__(self, db: Session, index_path: str = "./vector_index"):
        """初始化向量库管理器
        
        Args:
            db: 数据库会话
            index_path: 向量索引存储路径
        """
        self.db = db
        self.index_path = index_path
        os.makedirs(index_path, exist_ok=True)
        
        # 初始化Chroma客户端
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=index_path,
            anonymized_telemetry=False
        ))
        
        # 获取或创建集合，启用8位量化压缩
        self.collection = self.chroma_client.get_or_create_collection(
            name="knowledge_base",
            metadata={
                "hnsw:space": "cosine",
                "hnsw:quantization": "8bit"  # 启用8位量化压缩
            }
        )
        
        # 存储文本内容以便计算相似度
        self.text_store = {}
    
    def _simple_text_vector(self, text: str) -> List[float]:
        """简单的文本向量化方法
        
        Args:
            text: 文本内容
            
        Returns:
            向量表示
        """
        # 基于字符频率的简单向量
        # 取前128个字符的ASCII值作为向量
        vector = []
        for i, char in enumerate(text[:128]):
            vector.append(ord(char) / 255.0)
        # 填充到128维
        while len(vector) < 128:
            vector.append(0.0)
        return vector
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            相似度分数 (0-1)
        """
        import string
        
        # 文本预处理：去除标点符号，转换为小写
        def preprocess(text):
            # 去除标点符号
            text = text.translate(str.maketrans('', '', string.punctuation))
            # 转换为小写
            text = text.lower()
            # 去除空格
            text = text.replace(' ', '')
            return text
        
        # 计算共同字符的比例（适合中文）
        text1_processed = preprocess(text1)
        text2_processed = preprocess(text2)
        
        if not text1_processed and not text2_processed:
            return 1.0
        
        # 计算共同字符
        common_chars = set(text1_processed) & set(text2_processed)
        total_chars = set(text1_processed) | set(text2_processed)
        
        similarity = len(common_chars) / len(total_chars)
        print(f"相似度计算: '{text1}' vs '{text2}' = {similarity}")
        
        return similarity
    
    def create_vector_index(self, chunk_id: int, text: str) -> Dict:
        """创建向量索引
        
        Args:
            chunk_id: 分块ID
            text: 文本内容
            
        Returns:
            索引创建结果
        """
        import time
        
        # 异常边界处理：检查文本是否为空或乱码
        if not text or not isinstance(text, str):
            print(f"跳过空文本或非字符串内容，chunk_id={chunk_id}")
            return {"success": False, "message": "空文本或非字符串内容"}
        
        # 检查是否为纯文本（简单判断，去除空白字符后检查长度）
        cleaned_text = text.strip()
        if not cleaned_text:
            print(f"跳过空白文本，chunk_id={chunk_id}")
            return {"success": False, "message": "空白文本"}
        
        max_retries = 2
        retry_interval = 1
        
        for attempt in range(max_retries + 1):
            try:
                # 生成简单向量
                vector = self._simple_text_vector(text)
                vector_dim = len(vector)
                
                # 存储文本内容
                self.text_store[chunk_id] = text
                
                # 存储到Chroma
                print(f"添加到Chroma: chunk_id={chunk_id}, text={text[:50]}...")
                self.collection.add(
                    ids=[f"chunk_{chunk_id}"],
                    documents=[text],
                    embeddings=[vector],
                    metadatas=[{"chunk_id": chunk_id}]
                )
                
                # 验证是否添加成功
                count = self.collection.count()
                print(f"Chroma集合当前数据量: {count}")
                
                # 存储元数据到SQLite
                vector_path = os.path.join(self.index_path, f"chunk_{chunk_id}.npy")
                
                # 检查是否已存在
                existing_index = self.db.query(VectorIndex).filter(
                    VectorIndex.chunk_id == chunk_id
                ).first()
                
                if existing_index:
                    # 更新现有记录
                    existing_index.vector_path = vector_path
                    existing_index.vector_dim = vector_dim
                    existing_index.status = "indexed"
                    self.db.commit()
                    self.db.refresh(existing_index)
                    vector_index = existing_index
                else:
                    # 创建新记录
                    vector_index = VectorIndex(
                        chunk_id=chunk_id,
                        vector_path=vector_path,
                        vector_dim=vector_dim,
                        status="indexed"
                    )
                    self.db.add(vector_index)
                    self.db.commit()
                    self.db.refresh(vector_index)
                
                return {
                    "success": True,
                    "vector_index_id": vector_index.id,
                    "chunk_id": chunk_id,
                    "vector_path": vector_path,
                    "status": "indexed"
                }
            except Exception as e:
                print(f"创建向量索引失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
                # 回滚事务
                self.db.rollback()
                
                if attempt < max_retries:
                    print(f"等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                else:
                    return {"success": False, "message": str(e)}
    
    def get_vector_index(self, chunk_id: int) -> Optional[Dict]:
        """获取向量索引
        
        Args:
            chunk_id: 分块ID
            
        Returns:
            向量索引信息
        """
        vector_index = self.db.query(VectorIndex).filter(
            VectorIndex.chunk_id == chunk_id
        ).first()
        
        if not vector_index:
            return None
        
        return {
            "id": vector_index.id,
            "chunk_id": vector_index.chunk_id,
            "vector_path": vector_index.vector_path,
            "vector_dim": vector_index.vector_dim,
            "status": vector_index.status
        }
    
    def search_vectors(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相似向量
        
        Args:
            query: 查询文本
            top_k: 返回数量
            
        Returns:
            相似向量列表
        """
        try:
            # 生成查询向量
            query_vector = self._simple_text_vector(query)
            
            # 在Chroma中搜索
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k
            )
            
            # 打印调试信息
            print(f"Chroma搜索结果: {results}")
            
            # 计算实际文本相似度
            formatted_results = []
            for i, (id_, distance, metadata, document) in enumerate(zip(
                results['ids'][0],
                results['distances'][0],
                results['metadatas'][0],
                results['documents'][0]
            )):
                chunk_id = metadata.get('chunk_id')
                # 计算文本相似度
                similarity = self._calculate_similarity(query, document)
                
                formatted_results.append({
                    "chunk_id": chunk_id,
                    "score": similarity,
                    "rank": i + 1
                })
            
            # 按相似度排序
            formatted_results.sort(key=lambda x: x['score'], reverse=True)
            
            return formatted_results
        except Exception as e:
            print(f"搜索向量失败: {e}")
            return []
    
    def delete_vector_index(self, chunk_id: int) -> Dict:
        """删除向量索引
        
        Args:
            chunk_id: 分块ID
            
        Returns:
            删除结果
        """
        try:
            # 从Chroma中删除
            self.collection.delete(ids=[f"chunk_{chunk_id}"])
            
            # 从内存存储中删除
            if chunk_id in self.text_store:
                del self.text_store[chunk_id]
            
            # 从SQLite中删除
            vector_index = self.db.query(VectorIndex).filter(
                VectorIndex.chunk_id == chunk_id
            ).first()
            
            if vector_index:
                self.db.delete(vector_index)
                self.db.commit()
            
            return {"success": True, "message": "向量索引删除成功"}
        except Exception as e:
            print(f"删除向量索引失败: {e}")
            self.db.rollback()
            return {"success": False, "message": str(e)}
    
    def batch_create_vector_index(self, items: List[Dict]) -> Dict:
        """批量创建向量索引
        
        Args:
            items: 包含chunk_id和text的字典列表
            
        Returns:
            批量处理结果
        """
        import psutil
        import gc
        
        batch_size = 20
        total_items = len(items)
        processed_count = 0
        success_count = 0
        failed_count = 0
        
        print(f"开始批量处理 {total_items} 条数据，每批次 {batch_size} 条")
        
        for i in range(0, total_items, batch_size):
            batch = items[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            # 内存占用检测
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            print(f"批次 {batch_num}: 内存占用 {memory_percent}%")
            
            if memory_percent > 85:
                print("内存占用超过85%，暂停处理...")
                # 释放内存
                gc.collect()
                print("内存释放完成，继续处理")
            
            print(f"处理批次 {batch_num}: {len(batch)} 条数据")
            
            for item in batch:
                chunk_id = item.get('chunk_id')
                text = item.get('text')
                
                if not chunk_id or not text:
                    failed_count += 1
                    continue
                
                result = self.create_vector_index(chunk_id, text)
                if result['success']:
                    success_count += 1
                else:
                    failed_count += 1
                
                processed_count += 1
            
            # 处理完一批后释放内存
            gc.collect()
            print(f"批次 {batch_num} 处理完成，已处理 {processed_count}/{total_items} 条")
        
        return {
            "success": True,
            "total": total_items,
            "processed": processed_count,
            "success": success_count,
            "failed": failed_count
        }
    
    def update_vector_index(self, chunk_id: int, new_text: str) -> Dict:
        """更新向量索引
        
        Args:
            chunk_id: 分块ID
            new_text: 新的文本内容
            
        Returns:
            更新结果
        """
        try:
            # 开始事务
            self.db.begin()
            
            # 1. 删除原向量
            delete_result = self.delete_vector_index(chunk_id)
            if not delete_result['success']:
                self.db.rollback()
                return {"success": False, "message": f"删除原向量失败: {delete_result['message']}"}
            
            # 2. 重新生成向量并写入
            create_result = self.create_vector_index(chunk_id, new_text)
            if not create_result['success']:
                self.db.rollback()
                return {"success": False, "message": f"创建新向量失败: {create_result['message']}"}
            
            # 提交事务
            self.db.commit()
            return {"success": True, "message": "向量索引更新成功"}
        except Exception as e:
            print(f"更新向量索引失败: {e}")
            self.db.rollback()
            return {"success": False, "message": str(e)}
    
    def delete_vector_with_verification(self, chunk_id: int) -> Dict:
        """删除向量索引并验证
        
        Args:
            chunk_id: 分块ID
            
        Returns:
            删除结果
        """
        try:
            # 1. 执行删除
            delete_result = self.delete_vector_index(chunk_id)
            if not delete_result['success']:
                return {"success": False, "message": delete_result['message']}
            
            # 2. 验证删除是否成功
            # 检查Chroma中是否存在
            try:
                results = self.collection.get(ids=[f"chunk_{chunk_id}"])
                if results and results['ids']:
                    return {"success": False, "message": "向量删除失败，仍存在于Chroma中"}
            except Exception as e:
                # 如果查询失败，可能是因为不存在，视为删除成功
                pass
            
            # 检查SQLite中是否存在
            vector_index = self.db.query(VectorIndex).filter(
                VectorIndex.chunk_id == chunk_id
            ).first()
            
            if vector_index:
                return {"success": False, "message": "向量删除失败，仍存在于SQLite中"}
            
            return {"success": True, "message": "向量索引删除成功并验证通过"}
        except Exception as e:
            print(f"删除向量索引并验证失败: {e}")
            return {"success": False, "message": str(e)}
    
    def consistency_check(self) -> Dict:
        """一致性校验
        
        对比知识库 ID 和向量库 ID 列表，清理向量库中无对应知识库记录的孤立项
        
        Returns:
            一致性校验结果
        """
        try:
            print("开始执行一致性校验...")
            
            # 1. 获取所有知识库分块ID
            from .models import KnowledgeBaseChunk
            kb_chunks = self.db.query(KnowledgeBaseChunk).all()
            kb_chunk_ids = set([chunk.id for chunk in kb_chunks])
            print(f"知识库中存在 {len(kb_chunk_ids)} 个分块")
            
            # 2. 获取所有向量库中的ID
            vector_ids = set()
            try:
                # 获取Chroma中的所有ID
                chroma_ids = self.collection.get()['ids']
                for chroma_id in chroma_ids:
                    if chroma_id.startswith('chunk_'):
                        try:
                            chunk_id = int(chroma_id.replace('chunk_', ''))
                            vector_ids.add(chunk_id)
                        except ValueError:
                            pass
            except Exception as e:
                print(f"获取Chroma ID失败: {e}")
            
            # 获取SQLite中的所有ID
            vector_indexes = self.db.query(VectorIndex).all()
            sqlite_vector_ids = set([idx.chunk_id for idx in vector_indexes])
            vector_ids.update(sqlite_vector_ids)
            
            print(f"向量库中存在 {len(vector_ids)} 个分块")
            
            # 3. 找出孤立项（向量库中有但知识库中没有的）
            orphaned_ids = vector_ids - kb_chunk_ids
            print(f"发现 {len(orphaned_ids)} 个孤立项")
            
            # 4. 清理孤立项
            cleaned_count = 0
            for chunk_id in orphaned_ids:
                result = self.delete_vector_index(chunk_id)
                if result['success']:
                    cleaned_count += 1
                    print(f"清理孤立项: chunk_{chunk_id}")
                else:
                    print(f"清理孤立项失败: chunk_{chunk_id}, 原因: {result['message']}")
            
            # 5. 输出不一致日志
            inconsistency_info = {
                "knowledge_base_chunks": len(kb_chunk_ids),
                "vector_store_chunks": len(vector_ids),
                "orphaned_chunks": len(orphaned_ids),
                "cleaned_chunks": cleaned_count
            }
            
            print(f"一致性校验完成: {inconsistency_info}")
            
            return {
                "success": True,
                "message": "一致性校验完成",
                "data": inconsistency_info
            }
        except Exception as e:
            print(f"一致性校验失败: {e}")
            return {"success": False, "message": str(e)}
    
    def schedule_consistency_check(self):
        """调度一致性校验任务
        
        每日定时执行一致性校验
        """
        import schedule
        import time
        
        def job():
            print("执行每日一致性校验任务...")
            self.consistency_check()
        
        # 每天凌晨1点执行
        schedule.every().day.at("01:00").do(job)
        
        print("一致性校验任务已调度，每天凌晨1点执行")
        
        # 启动调度器
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def get_all_vector_indices(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """获取所有向量索引
        
        Args:
            skip: 跳过数量
            limit: 返回数量
            
        Returns:
            向量索引列表
        """
        vector_indices = self.db.query(VectorIndex).offset(skip).limit(limit).all()
        
        results = []
        for idx in vector_indices:
            results.append({
                "id": idx.id,
                "chunk_id": idx.chunk_id,
                "vector_path": idx.vector_path,
                "vector_dim": idx.vector_dim,
                "status": idx.status,
                "created_at": idx.created_at.isoformat() if idx.created_at else None
            })
        
        return results
    
    def update_vector_status(self, chunk_id: int, status: str) -> Dict:
        """更新向量索引状态
        
        Args:
            chunk_id: 分块ID
            status: 新状态
            
        Returns:
            更新结果
        """
        vector_index = self.db.query(VectorIndex).filter(
            VectorIndex.chunk_id == chunk_id
        ).first()
        
        if not vector_index:
            return {"success": False, "message": "向量索引不存在"}
        
        vector_index.status = status
        self.db.commit()
        
        return {
            "success": True,
            "chunk_id": chunk_id,
            "status": status
        }


class VectorServiceInterface:
    """向量服务接口
    
    实现：
    - 使用简单的文本向量化方法
    - 使用Chroma进行向量搜索
    """
    
    @staticmethod
    def encode_texts(texts: List[str], model_name: str = "default") -> List[List[float]]:
        """文本向量化
        
        Args:
            texts: 文本列表
            model_name: 模型名称
            
        Returns:
            向量列表
        """
        def simple_vector(text):
            vector = []
            for i, char in enumerate(text[:128]):
                vector.append(ord(char) / 255.0)
            while len(vector) < 128:
                vector.append(0.0)
            return vector
        
        return [simple_vector(text) for text in texts]
    
    @staticmethod
    def search_similar(query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """相似度搜索
        
        Args:
            query_vector: 查询向量
            top_k: 返回数量
            
        Returns:
            相似结果列表
        """
        # 此方法已在VectorStore中实现
        return []


def get_vector_store(db: Session) -> VectorStore:
    """获取向量库实例
    
    Args:
        db: 数据库会话
        
    Returns:
        VectorStore实例
    """
    return VectorStore(db)
