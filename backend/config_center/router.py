"""
配置中心API路由
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from knowledge_base.database import get_db
from config_center.config_manager import get_config_manager
from knowledge_base.models import Config

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/", response_model=Dict[str, Any])
async def get_all_configs():
    """
    获取所有配置
    """
    config_manager = get_config_manager()
    return config_manager.get_all()


@router.get("/{key}", response_model=Dict[str, Any])
async def get_config(key: str):
    """
    获取指定配置
    """
    config_manager = get_config_manager()
    value = config_manager.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"key": key, "value": value}


@router.put("/{key}")
async def update_config(key: str, value: Any):
    """
    更新配置
    """
    config_manager = get_config_manager()
    success = config_manager.set(key, value)
    if not success:
        raise HTTPException(status_code=500, detail="更新配置失败")
    
    # 重新加载配置
    config_manager.reload()
    
    # 通知其他模块重新加载配置
    # 这里可以添加事件通知机制
    
    return {"message": "配置更新成功", "key": key, "value": value}


@router.post("/")
async def create_config(key: str, value: Any, description: str = None):
    """
    创建配置
    """
    config_manager = get_config_manager()
    success = config_manager.set(key, value)
    if not success:
        raise HTTPException(status_code=500, detail="创建配置失败")
    
    # 重新加载配置
    config_manager.reload()
    
    return {"message": "配置创建成功", "key": key, "value": value}


@router.delete("/{key}")
async def delete_config(key: str, db: Session = Depends(get_db)):
    """
    删除配置
    """
    # 从数据库中删除
    config = db.query(Config).filter(Config.config_key == key).first()
    if config:
        db.delete(config)
        db.commit()
    
    # 从配置管理器中删除
    config_manager = get_config_manager()
    config = config_manager.get_all()
    
    # 支持点号分隔的嵌套键
    keys = key.split(".")
    if len(keys) == 1:
        if key in config:
            del config[key]
    else:
        # 遍历键，找到要删除的配置
        current = config
        for k in keys[:-1]:
            if k in current:
                current = current[k]
            else:
                break
        else:
            if keys[-1] in current:
                del current[keys[-1]]
    
    # 保存配置
    config_manager._save_to_file()
    config_manager._save_to_db()
    
    # 重新加载配置
    config_manager.reload()
    
    return {"message": "配置删除成功", "key": key}


@router.post("/reload")
async def reload_config():
    """
    重新加载配置
    """
    config_manager = get_config_manager()
    config_manager.reload()
    
    # 通知其他模块重新加载配置
    # 这里可以添加事件通知机制
    
    return {"message": "配置重新加载成功"}
