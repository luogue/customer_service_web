"""
初始化用户数据
创建手机号 13800000000 的用户，密码 123456
"""
from knowledge_base.database import SessionLocal, engine, Base
from knowledge_base.models import User
from datetime import datetime

def init_users():
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.phone == "13800000000").first()
        if existing_user:
            print(f"用户 {existing_user.phone} 已存在，ID: {existing_user.id}")
            print(f"姓名: {existing_user.name}, 角色: {existing_user.role}")
        else:
            # 创建新用户
            new_user = User(
                name="测试用户",
                email="test@example.com",
                phone="13800000000",
                role="customer"
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"用户创建成功！")
            print(f"手机号: {new_user.phone}")
            print(f"密码: 123456")
            print(f"ID: {new_user.id}")
            print(f"姓名: {new_user.name}")
            print(f"角色: {new_user.role}")
        
        # 同时创建一个管理员用户
        admin_user = db.query(User).filter(User.phone == "13800000001").first()
        if admin_user:
            print(f"\n管理员用户 {admin_user.phone} 已存在")
        else:
            admin = User(
                name="管理员",
                email="admin@example.com",
                phone="13800000001",
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"\n管理员用户创建成功！")
            print(f"手机号: {admin.phone}")
            print(f"密码: 123456")
            print(f"ID: {admin.id}")
            print(f"姓名: {admin.name}")
            print(f"角色: {admin.role}")
            
    except Exception as e:
        print(f"初始化用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_users()
