"""
测试检索服务
"""

from sqlalchemy.orm import Session
from knowledge_base.models import SessionLocal
from knowledge_base.vector_store import VectorStore
from knowledge_base.search_service import get_search_service


def test_search_service():
    """测试检索服务"""
    print("=== 测试检索服务 ===")
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 创建向量存储实例
        vector_store = VectorStore(db)
        
        # 获取检索服务实例
        search_service = get_search_service(db, vector_store)
        
        # 测试查询
        test_queries = [
            "下单失败",
            "退款",
            "物流"
        ]
        
        # 测试不同检索模式
        search_modes = ["text", "vector", "hybrid"]
        
        for query in test_queries:
            print(f"\n=== 测试查询: {query} ===")
            
            for mode in search_modes:
                print(f"\n检索模式: {mode}")
                results = search_service.search(query, top_k=3, threshold=0.3, search_mode=mode)
                
                print(f"消息: {results['message']}")
                print(f"检索结果数量: {len(results['results'])}")
                for i, result in enumerate(results['results']):
                    print(f"  {result['rank']}. ID: {result['id']}, 相似度: {result['similarity']:.4f}, 排序分数: {result['ranking_score']:.4f}")
                    print(f"     内容: {result['content'][:100]}...")
        
        print("\n=== 测试完成 ===")
        
    finally:
        db.close()


if __name__ == "__main__":
    test_search_service()
