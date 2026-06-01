#!/usr/bin/env python3
"""
数据库初始化脚本
- 重置数据库表结构
- 添加测试用户
"""

from knowledge_base.models import Base, engine, SessionLocal, User, Knowledge, Document, VectorIndex


def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 重建数据库表
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("数据库表重建完成")
    
    # 添加测试用户
    db = SessionLocal()
    try:
        # 添加测试客户用户
        test_user = User(
            phone="13800000000",
            name="测试客户",
            role="user"
        )
        db.add(test_user)
        
        # 添加另一个测试用户
        test_user2 = User(
            phone="13800000001",
            name="测试用户2",
            role="user"
        )
        db.add(test_user2)
        
        db.commit()
        print("测试用户添加完成")
        print("测试账号：")
        print("- 客户：13800000000 / 123456")
        print("- 管理员：admin / 123456")
    except Exception as e:
        print(f"添加测试用户失败：{e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
