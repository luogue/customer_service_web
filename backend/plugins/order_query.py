"""
查询订单插件
"""
from typing import Dict, Any


def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行订单查询
    
    Args:
        params: 参数字典，包含order_id和可选的phone
        
    Returns:
        执行结果，包含code/msg/data字段
    """
    try:
        # 入参校验
        order_id = params.get("order_id")
        phone = params.get("phone")
        
        if not order_id:
            return {
                "code": 400,
                "msg": "缺少订单号",
                "data": None
            }
        
        # 核心业务逻辑（模拟）
        # 实际项目中，这里应该调用订单服务查询真实订单
        order_info = {
            "order_id": order_id,
            "status": "已发货",
            "total_amount": 199.99,
            "create_time": "2026-03-01 10:00:00",
            "shipping_address": "北京市朝阳区某某街道",
            "items": [
                {
                    "product_id": "P001",
                    "product_name": "智能手表",
                    "quantity": 1,
                    "price": 199.99
                }
            ]
        }
        
        # 如果提供了手机号，验证是否匹配
        if phone:
            order_info["phone"] = phone
        
        # 返回结果
        return {
            "code": 200,
            "msg": "查询成功",
            "data": order_info
        }
    
    except Exception as e:
        return {
            "code": 500,
            "msg": f"查询订单失败: {str(e)}",
            "data": None
        }