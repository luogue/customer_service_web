"""
催发货/催物流插件
"""
from typing import Dict, Any


def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行催发货/催物流
    
    Args:
        params: 参数字典，包含order_id和可选的type
        
    Returns:
        执行结果，包含code/msg/data字段
    """
    try:
        # 入参校验
        order_id = params.get("order_id")
        remind_type = params.get("type", "delivery")  # 默认催发货
        
        if not order_id:
            return {
                "code": 400,
                "msg": "缺少订单号",
                "data": None
            }
        
        # 核心业务逻辑（模拟）
        # 实际项目中，这里应该调用物流服务处理真实催单
        remind_info = {
            "order_id": order_id,
            "type": remind_type,
            "status": "已通知",
            "create_time": "2026-03-12 10:00:00",
            "message": "您的催单请求已收到，我们会尽快处理"
        }
        
        # 根据类型设置不同的消息
        if remind_type == "delivery":
            remind_info["message"] = "您的催发货请求已收到，我们会尽快安排发货"
        elif remind_type == "logistics":
            remind_info["message"] = "您的催物流请求已收到，我们会联系快递公司尽快处理"
        
        # 返回结果
        return {
            "code": 200,
            "msg": "催单成功",
            "data": remind_info
        }
    
    except Exception as e:
        return {
            "code": 500,
            "msg": f"催单失败: {str(e)}",
            "data": None
        }