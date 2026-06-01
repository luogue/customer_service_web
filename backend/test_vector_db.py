"""
测试向量数据库功能
"""

import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from knowledge_base.database import get_db
from knowledge_base.vector_store import get_vector_store
from knowledge_base.search_service import get_search_service
from knowledge_base.repositories import KnowledgeRepository, DocumentRepository


async def test_vector_db():
    """测试向量数据库功能"""
    print("开始测试向量数据库...")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 初始化向量存储
        vector_store = get_vector_store(db)
        print("✅ 向量存储初始化成功")
        
        # 初始化搜索服务
        search_service = get_search_service(db, vector_store)
        print("✅ 搜索服务初始化成功")
        
        # 初始化知识库仓库
        knowledge_repo = KnowledgeRepository(db)
        document_repo = DocumentRepository(db)
        
        # 检查是否有知识库数据
        knowledge_items = knowledge_repo.search("", limit=5)
        print(f"✅ 知识库中有 {len(knowledge_items)} 条数据")
        
        if not knowledge_items:
            # 添加测试数据
            print("\n开始添加测试数据...")
            
            # 创建测试文档
            doc_result = document_repo.create("测试文档")
            document_id = doc_result['id']
            print(f"✅ 创建测试文档成功，ID: {document_id}")
            
            # 添加测试知识库内容
            test_contents = [
                "如何申请退款？您可以在订单详情页点击申请退款按钮，按照提示操作即可。",
                "订单查询功能在个人中心页面，您可以查看所有订单的状态和详情。",
                "物流信息可以在订单详情页查看，我们会实时更新物流状态。",
                "如何修改收货地址？在订单未发货前，您可以在订单详情页修改收货地址。",
                "如何联系客服？您可以通过在线客服、电话或邮件联系我们的客服团队。"
            ]
            
            for i, content in enumerate(test_contents):
                knowledge_result = knowledge_repo.create(content, document_id)
                print(f"✅ 添加测试内容 {i+1} 成功，ID: {knowledge_result['id']}")
            
            # 重新获取知识库数据
            knowledge_items = knowledge_repo.search("", limit=5)
            print(f"✅ 知识库中有 {len(knowledge_items)} 条数据")
        
        # 为现有知识库内容创建向量索引
        print("\n开始创建向量索引...")
        for i, item in enumerate(knowledge_items):
            # 强制重新创建向量索引
            print(f"🔄 为内容 {item['id']} 创建向量索引...")
            result = vector_store.create_vector_index(item['id'], item['content'])
            if result['success']:
                print(f"✅ 为内容 {item['id']} 创建向量索引成功")
            else:
                print(f"❌ 为内容 {item['id']} 创建向量索引失败: {result['message']}")
            
            # 测试3条数据即可
            if i >= 2:
                break
        
        # 测试向量搜索
        print("\n开始测试向量搜索...")
        test_queries = [
            "如何退款",
            "订单查询",
            "物流信息"
        ]
        
        for query in test_queries:
            print(f"\n测试查询: {query}")
            
            # 测试向量检索（降低阈值）
            vector_result = search_service.search(query, search_mode="vector", threshold=0.1)
            print(f"向量检索结果: {len(vector_result['results'])} 条")
            for i, item in enumerate(vector_result['results']):
                print(f"  {i+1}. 相似度: {item['similarity']:.4f} - {item['content'][:50]}...")
            
            # 测试混合检索（降低阈值）
            hybrid_result = search_service.search(query, search_mode="hybrid", threshold=0.1)
            print(f"混合检索结果: {len(hybrid_result['results'])} 条")
            for i, item in enumerate(hybrid_result['results']):
                print(f"  {i+1}. 相似度: {item['similarity']:.4f} - {item['content'][:50]}...")
        
        print("\n✅ 向量数据库测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_vector_db())
