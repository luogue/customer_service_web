"""
知识库检索的精排服务
实现知识库检索的精排环节：
- 对召回的这批内容，重新计算和用户问题的精准相似度
- 按照相似度从高到低排序
- 截取前 N 条（N = 最大检索结果数），得到最终要展示的内容
"""

from typing import List, Dict, Optional
import re


class RankingService:
    """精排服务"""
    
    def __init__(self):
        """初始化精排服务"""
        pass
    
    def rank(self, query: str, recalled_items: List[Dict], top_k: int = 10) -> List[Dict]:
        """
        对召回的内容进行精排
        
        Args:
            query: 用户问题
            recalled_items: 召回的内容列表
            top_k: 最终返回的结果数量
            
        Returns:
            排序后的内容列表
        """
        if not recalled_items:
            return []
        
        # 1. 计算精准相似度和融合得分
        ranked_items = self._calculate_similarity(query, recalled_items)
        
        # 2. 按照融合得分从高到低排序，业务数据结果始终排在知识库结果前
        ranked_items.sort(key=lambda x: (0 if x.get('source') == 'business' else 1, x.get('ranking_score', 0)), reverse=True)
        
        # 3. 截取前N条
        return ranked_items[:top_k]
    
    def _calculate_similarity(self, query: str, items: List[Dict]) -> List[Dict]:
        """
        计算查询与召回内容的精准相似度
        
        Args:
            query: 用户问题
            items: 召回的内容列表
            
        Returns:
            带有精准相似度的内容列表
        """
        if not items:
            return []
        
        # 计算每个内容的相似度和融合得分
        for item in items:
            # 计算文本匹配得分
            text_score = self._calculate_simple_similarity(query, item['content'])
            
            # 获取向量相似度得分（如果存在）
            vector_score = item.get('vector_similarity', 0)
            
            # 计算融合得分：文本匹配得分 ×40% + 向量相似度得分 ×60%
            fusion_score = text_score * 0.4 + vector_score * 0.6
            
            item['similarity'] = fusion_score
            item['ranking_score'] = fusion_score  # 添加排序分数字段
            item['text_score'] = text_score  # 保存文本匹配得分
            item['vector_score'] = vector_score  # 保存向量相似度得分
        
        return items
    
    def _calculate_simple_similarity(self, query: str, content: str) -> float:
        """
        简单的文本匹配相似度计算
        
        Args:
            query: 用户问题
            content: 内容
            
        Returns:
            相似度分数
        """
        # 提取关键词
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        content_words = set(re.findall(r'\b\w+\b', content.lower()))
        
        # 计算词频匹配
        if not query_words:
            return 0.0
        
        matched_words = query_words.intersection(content_words)
        similarity = len(matched_words) / len(query_words)
        
        # 考虑查询在内容中的出现位置
        if query.lower() in content.lower():
            similarity += 0.2  # 完全匹配增加分数
        
        # 考虑内容长度
        content_length = len(content)
        if 50 <= content_length <= 200:
            similarity += 0.1  # 适中长度的内容加分
        
        return min(similarity, 1.0)  # 限制最大分数为1.0


def get_ranking_service() -> RankingService:
    """获取精排服务实例"""
    return RankingService()
