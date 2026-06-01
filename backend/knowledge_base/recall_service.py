"""
知识库检索的召回服务
实现知识库检索的召回环节：
- 接收用户输入的检索关键词 / 问题
- 从内容表（knowledge）里，用「模糊匹配 + 向量相似度」两种方式
- 粗略捞出一批符合条件的内容（数量设为最大检索结果数的 3 倍）
- 过滤掉相似度低于阈值的内容，只保留初步相关的
"""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from .repositories import KnowledgeRepository
from .vector_store import VectorStore


class RecallService:
    """召回服务"""
    
    def __init__(self, db: Session, vector_store: VectorStore):
        """初始化召回服务"""
        self.db = db
        self.knowledge_repo = KnowledgeRepository(db)
        self.vector_store = vector_store
    
    def recall(self, query: str, top_k: int = 10, threshold: float = 0.3) -> List[Dict]:
        """
        召回相关内容
        
        Args:
            query: 检索关键词/问题
            top_k: 最大检索结果数
            threshold: 相似度阈值
            
        Returns:
            召回的内容列表
        """
        # 1. 模糊匹配召回
        fuzzy_results = self._fuzzy_recall(query, limit=top_k * 3)
        
        # 2. 向量相似度召回
        vector_results = self._vector_recall(query, limit=top_k * 3)
        
        # 3. 合并结果，去重
        merged_results = self._merge_results(fuzzy_results, vector_results)
        
        # 4. 过滤掉相似度低于阈值的内容
        filtered_results = self._filter_by_threshold(merged_results, threshold)
        
        # 5. 限制返回数量
        return filtered_results[:top_k]
    
    def _fuzzy_recall(self, query: str, limit: int = 30) -> List[Dict]:
        """模糊匹配召回"""
        results = self.knowledge_repo.search(query, limit=limit)
        # 为模糊匹配结果添加相似度分数（简单设为0.5）
        for result in results:
            result['similarity'] = 0.5
        return results
    
    def _vector_recall(self, query: str, limit: int = 30) -> List[Dict]:
        """向量相似度召回"""
        try:
            # 使用向量存储搜索相似向量
            vector_results = self.vector_store.search_vectors(query, limit)
            
            # 从数据库获取对应的内容
            results = []
            for item in vector_results:
                chunk_id = item.get('chunk_id')
                if not chunk_id:
                    continue
                
                # 获取对应的知识库内容
                content = self.knowledge_repo.get_by_id(chunk_id)
                if content:
                    result = {
                        'id': content['id'],
                        'content': content['content'],
                        'document_id': content['document_id'],
                        'similarity': item.get('score', 0)
                    }
                    results.append(result)
            
            return results
        except Exception as e:
            print(f"向量召回失败: {e}")
            return []
    
    def _merge_results(self, fuzzy_results: List[Dict], vector_results: List[Dict]) -> List[Dict]:
        """合并结果，去重"""
        # 用字典去重
        result_dict = {}
        
        # 先添加模糊匹配结果
        for result in fuzzy_results:
            result_dict[result['id']] = result
        
        # 再添加向量召回结果（如果有更高的相似度）
        for result in vector_results:
            if result['id'] in result_dict:
                # 如果向量相似度更高，替换
                if result.get('similarity', 0) > result_dict[result['id']].get('similarity', 0):
                    result_dict[result['id']] = result
            else:
                result_dict[result['id']] = result
        
        # 转换回列表并按相似度排序
        merged = list(result_dict.values())
        merged.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        return merged
    
    def _filter_by_threshold(self, results: List[Dict], threshold: float) -> List[Dict]:
        """过滤掉相似度低于阈值的内容"""
        return [result for result in results if result.get('similarity', 0) >= threshold]


def get_recall_service(db: Session, vector_store: VectorStore) -> RecallService:
    """获取召回服务实例"""
    return RecallService(db, vector_store)
