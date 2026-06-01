"""
测试精排服务
"""

from sqlalchemy.orm import Session
from knowledge_base.models import SessionLocal
from knowledge_base.vector_store import VectorStore
from knowledge_base.recall_service import get_recall_service
from knowledge_base.ranking_service import get_ranking_service


def test_ranking_service():
    """测试精排服务"""
    print("=== 测试精排服务 ===")
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 创建向量存储实例
        vector_store = VectorStore(db)
        
        # 获取召回服务实例
        recall_service = get_recall_service(db, vector_store)
        
        # 获取精排服务实例
        ranking_service = get_ranking_service()
        
        # 测试查询
        test_queries = [
            "下单失败",
            "退款",
            "物流"
        ]
        
        for query in test_queries:
            print(f"\n测试查询: {query}")
            
            # 1. 召回
            recalled_results = recall_service.recall(query, top_k=15, threshold=0.3)
            print(f"召回结果数量: {len(recalled_results)}")
            
            # 2. 精排
            ranked_results = ranking_service.rank(query, recalled_results, top_k=10)
            print(f"精排后结果数量: {len(ranked_results)}")
            
            # 显示前5个结果
            print("精排结果（前5个）:")
            for i, result in enumerate(ranked_results[:5]):
                similarity = result.get('similarity', 0)
                ranking_score = result.get('ranking_score', 0)
                print(f"  {i+1}. ID: {result['id']}, 相似度: {similarity:.4f}, 排序分数: {ranking_score:.4f}")
                print(f"     内容: {result['content'][:100]}...")
        
        print("\n=== 测试完成 ===")
        
    finally:
        db.close()


if __name__ == "__main__":
    test_ranking_service()
