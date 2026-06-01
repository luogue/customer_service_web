"""
创建数据库表
"""
from knowledge_base.models import Base, engine

print("创建数据库表...")
Base.metadata.create_all(bind=engine)
print("数据库表创建成功！")
