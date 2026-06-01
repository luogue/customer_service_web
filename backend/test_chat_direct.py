import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from knowledge_base.database import Base, get_db

# 创建测试数据库
DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建表
Base.metadata.create_all(bind=engine)

def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 测试对话流程
from dialogue_engine.order_dialogue import get_order_dialogue_flow

# 获取数据库会话
db = next(get_test_db())

# 创建对话流程实例
dialogue_flow = get_order_dialogue_flow(db)

# 测试处理用户输入
print("测试处理用户输入: 你好")
result = dialogue_flow.process_user_input(
    user_id="test_user",
    phone="13800000000",
    content="你好",
    session_id="test_session"
)

print(f"处理结果: {result}")
print(f"响应: {result.get('responses', [])}")
