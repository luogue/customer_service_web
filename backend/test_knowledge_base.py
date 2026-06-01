"""
测试知识底座层 - 数据库表结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 80)
print("测试1: 初始化数据库")
print("=" * 80)

try:
    from knowledge_base import init_db
    init_db()
    print("✅ 数据库初始化成功")
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("测试2: 导入所有模块")
print("=" * 80)

try:
    from knowledge_base import (
        FAQ,
        Document,
        DocumentChunk,
        VectorIndex,
        FAQManager,
        DocumentManager,
        TextSplitter,
        VectorStore,
        VectorServiceInterface,
        RAGPipeline,
        get_faq_manager,
        get_document_manager,
        get_vector_store,
        get_rag_pipeline
    )
    print("✅ 所有模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("测试3: 测试FAQ功能")
print("=" * 80)

from knowledge_base.models import SessionLocal
db = SessionLocal()

faq_manager = FAQManager(db)

# 添加测试FAQ
faq_result = faq_manager.add_faq(
    question="如何申请退款？",
    answer="您可以在订单详情页面点击申请退款按钮，按照提示填写退款原因即可。",
    keywords=["退款", "申请", "订单"]
)
print(f"添加FAQ: {faq_result}")

# 查询FAQ
faqs = faq_manager.get_all_faqs()
print(f"FAQ总数: {len(faqs)}")

# 搜索FAQ
search_result = faq_manager.search_by_keyword("我想退款")
print(f"搜索结果: {len(search_result)} 条")

db.close()

print("\n" + "=" * 80)
print("测试4: 测试文档管理功能")
print("=" * 80)

db = SessionLocal()
doc_manager = DocumentManager(db)

# 测试文本分块
chunks = TextSplitter.split_text("这是一个测试文档内容。包含多个句子。用于测试文本分块功能。", chunk_size=10, chunk_overlap=5)
print(f"文本分块结果: {len(chunks)} 个分块")
for i, chunk in enumerate(chunks):
    print(f"  分块{i}: {chunk['content']} (位置: {chunk['start_pos']}-{chunk['end_pos']})")

db.close()

print("\n" + "=" * 80)
print("测试5: 测试向量库接口")
print("=" * 80)

db = SessionLocal()
vector_store = VectorStore(db)

print(f"向量库初始化成功")
print(f"向量索引存储路径: {vector_store.index_path}")

db.close()

print("\n" + "=" * 80)
print("✅ 所有测试完成！")
print("=" * 80)
print("\n知识底座层实现完成：")
print("\n【数据库表结构】")
print("- FAQ表 (faqs): id, question, answer, keywords, created_at, updated_at")
print("- 文档表 (documents): id, title, content, file_name, file_type, chunk_count, status")
print("- 文档分块表 (document_chunks): id, document_id, chunk_content, chunk_index, start_pos, end_pos")
print("- 向量索引表 (vector_indices): id, document_id, chunk_id, vector_path, vector_dim, status")
print("\n【代码模块】")
print("- FAQ库: FAQManager - FAQ增删改查，关键词精准匹配")
print("- 文档库: DocumentManager - 文档上传、存储、分块")
print("- 向量库: VectorStore - 向量索引管理接口")
print("- RAG Pipeline: RAGPipeline - 完整RAG流程管理")
print("\n【API接口】")
print("- POST /api/knowledge/faqs - 添加FAQ")
print("- GET /api/knowledge/faqs - 获取FAQ列表")
print("- POST /api/knowledge/documents/upload - 上传文档")
print("- GET /api/knowledge/documents - 获取文档列表")
print("- POST /api/knowledge/query - 综合查询")
print("\n【注意事项】")
print("- 向量化和相似度计算需接入外部向量服务")
print("- 当前仅提供接口框架，不加载任何模型")
