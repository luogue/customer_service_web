"""初始化数据库"""
from knowledge_base.database import engine, Base

# 创建所有表
Base.metadata.create_all(bind=engine)
print('数据库表创建成功')
