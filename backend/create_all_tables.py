"""
创建所有数据库表
"""

from knowledge_base.models import Base, engine

print("开始创建所有数据库表...")

# 创建所有表
Base.metadata.create_all(bind=engine)

print("✅ 所有数据库表创建完成")
