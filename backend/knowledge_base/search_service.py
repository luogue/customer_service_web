"""
知识库检索服务
整合召回和精排逻辑，提供完整的检索流程
支持三种检索模式：文本检索、向量检索、混合检索
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from .recall_service import get_recall_service
from .ranking_service import get_ranking_service
from .vector_store import VectorStore
from .config.config_manager import config_manager


class SearchService:
    """检索服务"""
    
    def __init__(self, db: Session, vector_store: VectorStore):
        """初始化检索服务"""
        self.db = db
        self.vector_store = vector_store
        self.recall_service = get_recall_service(db, vector_store)
        self.ranking_service = get_ranking_service()
        self.vector_enabled = True  # 向量检索是否启用
        self.downgrade_reason = None  # 降级原因
        
        # 查询缓存
        self.query_cache = {}  # 缓存字典
        self.cache_expiry = 600  # 缓存过期时间（10分钟）
        self.query_counter = {}  # 查询计数器，用于统计高频查询
        self.high_frequency_threshold = 3  # 高频查询阈值
        self.cache_time = {}  # 缓存时间戳
        
        # 用户历史查询缓存
        self.user_history = {}  # 按用户ID存储历史查询
        self.history_limit = 3  # 每个用户保留最近3条查询
    
    def search(self, query: str, top_k: int = None, threshold: float = None, 
               search_mode: str = "hybrid", user_id: str = "anonymous") -> Dict:
        """
        完整的检索流程
        
        Args:
            query: 检索关键词/问题
            top_k: 最大检索结果数，默认返回前3条
            threshold: 相似度阈值
            search_mode: 检索模式 (text/vector/hybrid)
            user_id: 用户ID，用于存储历史查询
            
        Returns:
            检索结果字典
        """
        import time
        
        # 使用配置管理器获取默认值
        if top_k is None:
            top_k = config_manager.get_top_k()
        if threshold is None:
            threshold = config_manager.get_similarity_threshold()
        
        # 更新用户历史查询
        if user_id not in self.user_history:
            self.user_history[user_id] = []
        
        # 添加当前查询到历史记录
        self.user_history[user_id].append(query)
        # 只保留最近3条
        if len(self.user_history[user_id]) > self.history_limit:
            self.user_history[user_id] = self.user_history[user_id][-self.history_limit:]
        
        # 生成缓存键
        cache_key = f"{query}_{top_k}_{threshold}_{search_mode}_{user_id}"
        
        # 检查缓存是否有效
        current_time = time.time()
        if cache_key in self.query_cache:
            cache_timestamp = self.cache_time.get(cache_key, 0)
            if current_time - cache_timestamp < self.cache_expiry:
                print(f"使用缓存结果: {query}")
                return self.query_cache[cache_key]
            else:
                # 缓存过期，删除
                del self.query_cache[cache_key]
                del self.cache_time[cache_key]
        
        # 构建增强查询（包含历史查询）
        enhanced_query = query
        if self.user_history[user_id]:
            # 拼接最近3条历史查询
            history_queries = " ".join(self.user_history[user_id][:-1])  # 排除当前查询
            if history_queries:
                enhanced_query = f"{query} {history_queries}"
                print(f"增强查询: {enhanced_query}")
        
        # 执行正常的搜索流程
        # 1. 根据检索模式执行召回
        recall_multiplier = config_manager.get_recall_multiplier()
        recalled_items = self._recall_by_mode(enhanced_query, top_k * recall_multiplier, threshold, search_mode)
        
        # 2. 精排
        ranked_items = self.ranking_service.rank(enhanced_query, recalled_items, top_k * recall_multiplier)
        
        # 3. 过滤掉相似度低于阈值的内容
        filtered_items = [item for item in ranked_items if item.get('similarity', 0) >= threshold]
        
        # 4. 截取前N条
        final_items = filtered_items[:top_k]
        
        # 5. 格式化结果
        if not final_items:
            result = {
                "success": True,
                "message": "未找到相关内容",
                "results": []
            }
        else:
            result = {
                "success": True,
                "message": f"找到 {len(final_items)} 条相关内容",
                "results": self._format_results(final_items)
            }
        
        # 统计查询次数
        self.query_counter[query] = self.query_counter.get(query, 0) + 1
        
        # 对于高频查询（≥3次），将结果存入缓存
        if self.query_counter[query] >= self.high_frequency_threshold:
            print(f"缓存高频查询结果: {query} (第{self.query_counter[query]}次)")
            self.query_cache[cache_key] = result
            self.cache_time[cache_key] = current_time
        
        return result
    
    def _recall_by_mode(self, query: str, top_k: int, threshold: float, 
                        search_mode: str) -> List[Dict]:
        """
        根据检索模式执行召回
        
        Args:
            query: 检索关键词/问题
            top_k: 最大检索结果数
            threshold: 相似度阈值
            search_mode: 检索模式 (text/vector/hybrid)
            
        Returns:
            召回的内容列表
        """
        # 优先级固化：先查 FAQ 表（精准匹配）
        try:
            faq_results = self.recall_service.faq_recall(query, top_k, threshold)
            if faq_results:
                print("FAQ 表精准匹配成功")
                return faq_results
        except Exception as e:
            print(f"FAQ 检索失败: {e}")
        
        # 未匹配则查业务数据表
        try:
            business_results = self.recall_service.business_recall(query, top_k, threshold)
            if business_results:
                print("业务数据表匹配成功")
                return business_results
        except Exception as e:
            print(f"业务数据检索失败: {e}")
        
        # 再未匹配则触发知识库混合检索
        if search_mode == "text":
            return self._text_recall(query, top_k, threshold)
        elif search_mode == "vector":
            if self.vector_enabled:
                try:
                    results = self._vector_recall(query, top_k, threshold)
                    # 如果向量检索返回空结果，不触发降级
                    return results
                except Exception as e:
                    print(f"向量检索失败，触发降级: {e}")
                    self.vector_enabled = False
                    self.downgrade_reason = f"向量检索失败: {str(e)}"
                    print("已降级到文本检索模式")
                    # 降级到文本检索
                    return self._text_recall(query, top_k, threshold)
            else:
                print(f"向量检索已禁用（原因: {self.downgrade_reason}），使用文本检索")
                return self._text_recall(query, top_k, threshold)
        else:  # hybrid
            if self.vector_enabled:
                try:
                    results = self.recall_service.recall(query, top_k, threshold)
                    return results
                except Exception as e:
                    print(f"混合检索失败，触发降级: {e}")
                    self.vector_enabled = False
                    self.downgrade_reason = f"混合检索失败: {str(e)}"
                    print("已降级到文本检索模式")
                    # 降级到文本检索
                    return self._text_recall(query, top_k, threshold)
            else:
                print(f"向量检索已禁用（原因: {self.downgrade_reason}），使用文本检索")
                return self._text_recall(query, top_k, threshold)
    
    def _text_recall(self, query: str, top_k: int, threshold: float) -> List[Dict]:
        """
        文本检索召回
        
        Args:
            query: 检索关键词/问题
            top_k: 最大检索结果数
            threshold: 相似度阈值
            
        Returns:
            召回的内容列表
        """
        # 调用召回服务的模糊匹配方法
        from .repositories import KnowledgeRepository
        knowledge_repo = KnowledgeRepository(self.db)
        
        # 模糊匹配召回
        fuzzy_results = knowledge_repo.search(query, limit=top_k * 3)
        
        # 为模糊匹配结果添加相似度分数
        for result in fuzzy_results:
            result['similarity'] = 0.5
        
        # 过滤掉相似度低于阈值的内容
        filtered_results = [result for result in fuzzy_results if result.get('similarity', 0) >= threshold]
        
        return filtered_results
    
    def _vector_recall(self, query: str, top_k: int, threshold: float) -> List[Dict]:
        """
        向量检索召回
        
        Args:
            query: 检索关键词/问题
            top_k: 最大检索结果数
            threshold: 相似度阈值
            
        Returns:
            召回的内容列表
        """
        try:
            # 使用向量存储搜索相似向量
            vector_results = self.vector_store.search_vectors(query, top_k * 3)
            
            # 从数据库获取对应的内容
            from .repositories import KnowledgeRepository
            knowledge_repo = KnowledgeRepository(self.db)
            
            results = []
            for item in vector_results:
                chunk_id = item.get('chunk_id')
                if not chunk_id:
                    continue
                
                # 获取对应的知识库内容
                content = knowledge_repo.get_by_id(chunk_id)
                if content:
                    result = {
                        'id': content['id'],
                        'content': content['content'],
                        'document_id': content['document_id'],
                        'similarity': item.get('score', 0),
                        'ranking_score': item.get('score', 0)
                    }
                    results.append(result)
            
            # 过滤掉相似度低于阈值的内容
            filtered_results = [result for result in results if result.get('similarity', 0) >= threshold]
            
            # 按相似度排序
            filtered_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            return filtered_results
        except Exception as e:
            print(f"向量检索失败: {e}")
            return []
    
    def _format_results(self, results: List[Dict]) -> List[Dict]:
        """
        格式化检索结果
        
        Args:
            results: 排序后的结果列表
            
        Returns:
            格式化后的结果列表
        """
        formatted_results = []
        
        for i, result in enumerate(results):
            formatted_result = {
                "id": result['id'],
                "content": result['content'],
                "document_id": result['document_id'],
                "similarity": result.get('similarity', 0),
                "ranking_score": result.get('ranking_score', 0),
                "rank": i + 1
            }
            formatted_results.append(formatted_result)
        
        return formatted_results


def get_search_service(db: Session, vector_store: VectorStore) -> SearchService:
    """获取检索服务实例"""
    return SearchService(db, vector_store)
