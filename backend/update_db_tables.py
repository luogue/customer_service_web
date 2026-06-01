"""
更新数据库表结构
添加上下文管理相关表
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_base.database import engine, Base
from knowledge_base.models import ConversationSession, BusinessContext

def main():
    print("创建数据库表...")
    
    # 创建所有表（包括新增的表）
    Base.metadata.create_all(bind=engine)
    
    print("数据库表创建完成！")
    print("新增表:")
    print("- conversation_sessions (会话表)")
    print("- business_contexts (业务上下文表)")

if __name__ == "__main__":
    main()
