"""
Prompt模板管理路由
实现Prompt模板的CRUD接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from knowledge_base.models import get_db, PromptTemplate
from security import audit_admin_operation

router = APIRouter(tags=["Prompt模板管理"])


class PromptTemplateCreate(BaseModel):
    """创建Prompt模板的请求模型"""
    template_name: str
    template_content: str
    is_default: int = 0


class PromptTemplateUpdate(BaseModel):
    """更新Prompt模板的请求模型"""
    template_name: str
    template_content: str
    is_default: int = 0


class PromptTemplateResponse(BaseModel):
    """Prompt模板的响应模型"""
    id: int
    template_name: str
    template_content: str
    is_default: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/prompt/templates", response_model=List[PromptTemplateResponse])
async def get_all_prompt_templates(db: Session = Depends(get_db)):
    """
    查询所有Prompt模板
    """
    templates = db.query(PromptTemplate).all()
    return templates


@router.post("/prompt/templates", response_model=PromptTemplateResponse)
@audit_admin_operation(operation="创建Prompt模板", resource="prompt_template", action="create")
async def create_prompt_template(
    template: PromptTemplateCreate,
    db: Session = Depends(get_db),
    admin_id: str = "admin"
):
    """
    新增Prompt模板
    """
    # 检查模板名是否已存在
    existing_template = db.query(PromptTemplate).filter(
        PromptTemplate.template_name == template.template_name
    ).first()
    if existing_template:
        raise HTTPException(status_code=400, detail="模板名已存在")
    
    # 如果设置为默认模板，将其他模板的is_default设置为0
    if template.is_default == 1:
        db.query(PromptTemplate).update({PromptTemplate.is_default: 0})
    
    # 创建新模板
    new_template = PromptTemplate(
        template_name=template.template_name,
        template_content=template.template_content,
        is_default=template.is_default
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template


@router.put("/prompt/templates/{template_id}", response_model=PromptTemplateResponse)
@audit_admin_operation(operation="修改Prompt模板", resource="prompt_template", action="update")
async def update_prompt_template(
    template_id: int,
    template: PromptTemplateUpdate,
    db: Session = Depends(get_db),
    admin_id: str = "admin"
):
    """
    修改Prompt模板
    """
    # 查找模板
    existing_template = db.query(PromptTemplate).filter(
        PromptTemplate.id == template_id
    ).first()
    if not existing_template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 检查模板名是否已存在（如果修改了模板名）
    if template.template_name != existing_template.template_name:
        existing_name = db.query(PromptTemplate).filter(
            PromptTemplate.template_name == template.template_name
        ).first()
        if existing_name:
            raise HTTPException(status_code=400, detail="模板名已存在")
    
    # 如果设置为默认模板，将其他模板的is_default设置为0
    if template.is_default == 1:
        db.query(PromptTemplate).update({PromptTemplate.is_default: 0})
    
    # 更新模板
    existing_template.template_name = template.template_name
    existing_template.template_content = template.template_content
    existing_template.is_default = template.is_default
    existing_template.updated_at = datetime.now()
    
    db.commit()
    db.refresh(existing_template)
    return existing_template


@router.delete("/prompt/templates/{template_id}")
@audit_admin_operation(operation="删除Prompt模板", resource="prompt_template", action="delete")
async def delete_prompt_template(
    template_id: int,
    db: Session = Depends(get_db),
    admin_id: str = "admin"
):
    """
    删除Prompt模板
    """
    # 查找模板
    existing_template = db.query(PromptTemplate).filter(
        PromptTemplate.id == template_id
    ).first()
    if not existing_template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 不能删除默认模板
    if existing_template.is_default == 1:
        raise HTTPException(status_code=400, detail="不能删除默认模板")
    
    # 删除模板
    db.delete(existing_template)
    db.commit()
    return {"message": "模板删除成功"}
