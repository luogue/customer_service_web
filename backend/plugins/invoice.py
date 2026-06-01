"""
开发票插件
"""
from typing import Dict, Any


def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行开发票
    
    Args:
        params: 参数字典，包含order_id、invoice_type和可选的company_name、tax_number
        
    Returns:
        执行结果，包含code/msg/data字段
    """
    try:
        # 入参校验
        order_id = params.get("order_id")
        invoice_type = params.get("invoice_type")
        company_name = params.get("company_name")
        tax_number = params.get("tax_number")
        
        if not order_id:
            return {
                "code": 400,
                "msg": "缺少订单号",
                "data": None
            }
        
        if not invoice_type:
            return {
                "code": 400,
                "msg": "缺少发票类型",
                "data": None
            }
        
        # 核心业务逻辑（模拟）
        # 实际项目中，这里应该调用发票服务处理真实开票
        invoice_info = {
            "order_id": order_id,
            "invoice_id": f"INV{order_id}",
            "invoice_type": invoice_type,
            "company_name": company_name,
            "tax_number": tax_number,
            "amount": 199.99,
            "status": "已开具",
            "create_time": "2026-03-12 10:00:00",
            "delivery_method": "电子发票"
        }
        
        # 返回结果
        return {
            "code": 200,
            "msg": "发票开具成功",
            "data": invoice_info
        }
    
    except Exception as e:
        return {
            "code": 500,
            "msg": f"开具发票失败: {str(e)}",
            "data": None
        }