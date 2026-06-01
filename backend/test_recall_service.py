"""
测试召回服务
"""

from sqlalchemy.orm import Session
from knowledge_base.models import SessionLocal
from knowledge_base.vector_store import VectorStore
from knowledge_base.recall_service import get_recall_service


def test_recall_service():
    """测试召回服务"""
    print("=== 测试召回服务 ===")
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 创建向量存储实例
        vector_store = VectorStore(db)
        
        # 获取召回服务实例
        recall_service = get_recall_service(db, vector_store)
        
        # 测试查询
        test_queries = [
            "下单失败",
            "退款",
            "物流",
            "客服"
        ]
        
        for query in test_queries:
            print(f"\n测试查询: {query}")
            results = recall_service.recall(query, top_k=10, threshold=0.3)
            
            print(f"召回结果数量: {len(results)}")
            for i, result in enumerate(results[:5]):  # 只显示前5个结果
                print(f"  {i+1}. ID: {result['id']}, 相似度: {result['similarity']}")
                print(f"     内容: {result['content'][:100]}...")
        
        print("\n=== 测试完成 ===")
        
    finally:
        db.close()


if __name__ == "__main__":
    test_recall_service()
