"""
退货退款插件
"""
from typing import Dict, Any


def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行退货退款
    
    Args:
        params: 参数字典，包含order_id、reason和可选的amount
        
    Returns:
        执行结果，包含code/msg/data字段
    """
    try:
        # 入参校验
        order_id = params.get("order_id")
        reason = params.get("reason")
        amount = params.get("amount")
        
        if not order_id:
            return {
                "code": 400,
                "msg": "缺少订单号",
                "data": None
            }
        
        if not reason:
            return {
                "code": 400,
                "msg": "缺少退款原因",
                "data": None
            }
        
        # 核心业务逻辑（模拟）
        # 实际项目中，这里应该调用退款服务处理真实退款
        refund_info = {
            "order_id": order_id,
            "refund_id": f"REF{order_id}",
            "reason": reason,
            "amount": amount or 199.99,
            "status": "处理中",
            "create_time": "2026-03-12 10:00:00",
            "estimated_time": "3-5个工作日"
        }
        
        # 返回结果
        return {
            "code": 200,
            "msg": "退款申请提交成功",
            "data": refund_info
        }
    
    except Exception as e:
        return {
            "code": 500,
            "msg": f"提交退款申请失败: {str(e)}",
            "data": None
        }