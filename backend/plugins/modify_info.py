"""
修改信息插件
"""
from typing import Dict, Any


def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行修改信息
    
    Args:
        params: 参数字典，包含info_type、new_value和可选的phone
        
    Returns:
        执行结果，包含code/msg/data字段
    """
    try:
        # 入参校验
        info_type = params.get("info_type")
        new_value = params.get("new_value")
        phone = params.get("phone")
        
        if not info_type:
            return {
                "code": 400,
                "msg": "缺少信息类型",
                "data": None
            }
        
        if not new_value:
            return {
                "code": 400,
                "msg": "缺少新值",
                "data": None
            }
        
        # 核心业务逻辑（模拟）
        # 实际项目中，这里应该调用用户服务修改真实信息
        modify_info = {
            "info_type": info_type,
            "old_value": "旧值",  # 模拟旧值
            "new_value": new_value,
            "phone": phone,
            "status": "修改成功",
            "modify_time": "2026-03-12 10:00:00"
        }
        
        # 返回结果
        return {
            "code": 200,
            "msg": "信息修改成功",
            "data": modify_info
        }
    
    except Exception as e:
        return {
            "code": 500,
            "msg": f"修改信息失败: {str(e)}",
            "data": None
        }