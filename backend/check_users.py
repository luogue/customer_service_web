"""
检查数据库中的用户
"""
from knowledge_base.database import SessionLocal
from knowledge_base.models import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("数据库中的用户：")
        print("-" * 60)
        for u in users:
            print(f"ID: {u.id}")
            print(f"手机号: {u.phone}")
            print(f"姓名: {u.name}")
            print(f"角色: {u.role}")
            print(f"邮箱: {u.email}")
            print("-" * 60)
    except Exception as e:
        print(f"查询失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
