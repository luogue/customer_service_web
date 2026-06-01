"""重新创建数据库和测试数据"""
import os
import sys

# 删除旧数据库
db_path = os.path.join(os.path.dirname(__file__), 'knowledge_base', 'app.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"已删除旧数据库: {db_path}")

# 创建新表
from knowledge_base.database import engine, Base
Base.metadata.create_all(bind=engine)
print("数据库表创建成功")

# 创建测试数据
from create_test_user import main
main()
