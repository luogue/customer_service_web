"""
API Key管理模块
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .models import Base, engine, get_db


class ApiKey(Base):
    """API Key表"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key_name = Column(String(100), unique=True, nullable=False, index=True)  # API key名称
    api_key = Column(String(255), nullable=False)  # API key值
    created_at = Column(DateTime, default=func.now())  # 创建时间
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # 更新时间


def create_api_key_table():
    """创建API Key表"""
    ApiKey.__table__.create(bind=engine, checkfirst=True)
    print("API Key表创建完成")


def set_api_key(key_name: str, api_key: str) -> bool:
    """
    设置API Key
    
    Args:
        key_name: API key名称
        api_key: API key值
        
    Returns:
        是否设置成功
    """
    db = next(get_db())
    try:
        # 检查是否已存在
        existing_key = db.query(ApiKey).filter(ApiKey.key_name == key_name).first()
        if existing_key:
            # 更新现有key
            existing_key.api_key = api_key
        else:
            # 创建新key
            new_key = ApiKey(key_name=key_name, api_key=api_key)
            db.add(new_key)
        db.commit()
        return True
    except Exception as e:
        print(f"设置API Key失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def get_api_key(key_name: str) -> str:
    """
    获取API Key
    
    Args:
        key_name: API key名称
        
    Returns:
        API key值，如果不存在返回空字符串
    """
    db = next(get_db())
    try:
        api_key = db.query(ApiKey).filter(ApiKey.key_name == key_name).first()
        return api_key.api_key if api_key else ""
    except Exception as e:
        print(f"获取API Key失败: {e}")
        return ""
    finally:
        db.close()


def delete_api_key(key_name: str) -> bool:
    """
    删除API Key
    
    Args:
        key_name: API key名称
        
    Returns:
        是否删除成功
    """
    db = next(get_db())
    try:
        api_key = db.query(ApiKey).filter(ApiKey.key_name == key_name).first()
        if api_key:
            db.delete(api_key)
            db.commit()
            return True
        return False
    except Exception as e:
        print(f"删除API Key失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def list_api_keys() -> list:
    """
    列出所有API Key
    
    Returns:
        API Key列表
    """
    db = next(get_db())
    try:
        api_keys = db.query(ApiKey).all()
        return [{
            "key_name": key.key_name,
            "created_at": key.created_at,
            "updated_at": key.updated_at
        } for key in api_keys]
    except Exception as e:
        print(f"列出API Key失败: {e}")
        return []
    finally:
        db.close()


if __name__ == "__main__":
    create_api_key_table()
    # 示例：设置API Key
    # set_api_key("openai", "your_openai_api_key")
    # set_api_key("baidu", "your_baidu_api_key")
    # 示例：获取API Key
    # print(get_api_key("openai"))
    # 示例：列出所有API Key
    # print(list_api_keys())