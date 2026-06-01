"""
添加默认Prompt模板到数据库
"""
from knowledge_base.models import get_db, PromptTemplate

if __name__ == "__main__":
    db = next(get_db())
    try:
        # 检查是否已经存在默认模板
        existing_default = db.query(PromptTemplate).filter(PromptTemplate.is_default == 1).first()
        if not existing_default:
            # 创建默认Prompt模板
            default_template = PromptTemplate(
                template_name="默认客服模板",
                template_content="你是一个专业的淘宝电商客服，需要：\n1. 保持友好、专业的语气\n2. 快速理解用户问题\n3. 提供准确的解决方案\n4. 遇到不确定的问题，及时请求用户提供更多信息\n\n用户问题：{user_question}",
                is_default=1
            )
            db.add(default_template)
            db.commit()
            print("默认Prompt模板添加成功")
        else:
            print("默认Prompt模板已存在")
    except Exception as e:
        print(f"错误: {e}")
        db.rollback()
    finally:
        db.close()
