"""
取消订单插件
"""
from typing import Dict, Any


def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行取消订单
    
    Args:
        params: 参数字典，包含order_id和可选的reason
        
    Returns:
        执行结果，包含code/msg/data字段
    """
    try:
        # 入参校验
        order_id = params.get("order_id")
        reason = params.get("reason", "用户主动取消")
        
        if not order_id:
            return {
                "code": 400,
                "msg": "缺少订单号",
                "data": None
            }
        
        # 核心业务逻辑（模拟）
        # 实际项目中，这里应该调用订单服务处理真实取消
        cancel_info = {
            "order_id": order_id,
            "reason": reason,
            "status": "已取消",
            "cancel_time": "2026-03-12 10:00:00",
            "refund_status": "退款中"
        }
        
        # 返回结果
        return {
            "code": 200,
            "msg": "订单取消成功",
            "data": cancel_info
        }
    
    except Exception as e:
        return {
            "code": 500,
            "msg": f"取消订单失败: {str(e)}",
            "data": None
        }