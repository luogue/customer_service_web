"""
插件注册中心
"""
from typing import Dict, Any, List, Optional


class PluginRegistry:
    """
    插件注册中心
    管理所有意图插件的注册和查询
    """
    
    def __init__(self):
        # 插件注册表：{意图关键词: {plugin_name: 插件名, params: 入参规范}}
        self.registry = {
            # 查询订单
            "order_query": {
                "plugin_name": "order_query",
                "params": [
                    {"name": "order_id", "type": "string", "required": True, "description": "订单号"},
                    {"name": "phone", "type": "string", "required": False, "description": "手机号码"}
                ]
            },
            # 查询商品
            "product_query": {
                "plugin_name": "product_query",
                "params": [
                    {"name": "product_id", "type": "string", "required": False, "description": "商品ID"},
                    {"name": "product_name", "type": "string", "required": False, "description": "商品名称"}
                ]
            },
            # 退货退款
            "refund": {
                "plugin_name": "refund",
                "params": [
                    {"name": "order_id", "type": "string", "required": True, "description": "订单号"},
                    {"name": "reason", "type": "string", "required": True, "description": "退款原因"},
                    {"name": "amount", "type": "number", "required": False, "description": "退款金额"}
                ]
            },
            # 投诉建议
            "complaint": {
                "plugin_name": "complaint",
                "params": [
                    {"name": "subject", "type": "string", "required": True, "description": "投诉主题"},
                    {"name": "content", "type": "string", "required": True, "description": "投诉内容"},
                    {"name": "order_id", "type": "string", "required": False, "description": "相关订单号"}
                ]
            },
            # 修改信息
            "modify_info": {
                "plugin_name": "modify_info",
                "params": [
                    {"name": "info_type", "type": "string", "required": True, "description": "信息类型"},
                    {"name": "new_value", "type": "string", "required": True, "description": "新值"},
                    {"name": "phone", "type": "string", "required": False, "description": "手机号码"}
                ]
            },
            # 催发货/催物流
            "remind_delivery": {
                "plugin_name": "remind_delivery",
                "params": [
                    {"name": "order_id", "type": "string", "required": True, "description": "订单号"},
                    {"name": "type", "type": "string", "required": False, "description": "类型: delivery(催发货) / logistics(催物流)"}
                ]
            },
            # 取消订单
            "cancel_order": {
                "plugin_name": "cancel_order",
                "params": [
                    {"name": "order_id", "type": "string", "required": True, "description": "订单号"},
                    {"name": "reason", "type": "string", "required": False, "description": "取消原因"}
                ]
            },
            # 开发票
            "invoice": {
                "plugin_name": "invoice",
                "params": [
                    {"name": "order_id", "type": "string", "required": True, "description": "订单号"},
                    {"name": "invoice_type", "type": "string", "required": True, "description": "发票类型"},
                    {"name": "company_name", "type": "string", "required": False, "description": "公司名称"},
                    {"name": "tax_number", "type": "string", "required": False, "description": "税号"}
                ]
            },
            # 售后维修/质保
            "after_sales": {
                "plugin_name": "after_sales",
                "params": [
                    {"name": "order_id", "type": "string", "required": True, "description": "订单号"},
                    {"name": "issue_type", "type": "string", "required": True, "description": "问题类型"},
                    {"name": "description", "type": "string", "required": True, "description": "问题描述"}
                ]
            },
            # 活动优惠/优惠券
            "promotion": {
                "plugin_name": "promotion",
                "params": [
                    {"name": "promotion_type", "type": "string", "required": False, "description": "优惠类型"},
                    {"name": "coupon_code", "type": "string", "required": False, "description": "优惠券代码"}
                ]
            },
            # 问题咨询
            "consultation": {
                "plugin_name": "consultation",
                "params": [
                    {"name": "question", "type": "string", "required": True, "description": "问题内容"},
                    {"name": "category", "type": "string", "required": False, "description": "问题分类"}
                ]
            },
            # 闲聊互动
            "chat": {
                "plugin_name": "chat",
                "params": [
                    {"name": "content", "type": "string", "required": True, "description": "聊天内容"}
                ]
            }
        }
    
    def get_plugin_info(self, intent: str) -> Optional[Dict[str, Any]]:
        """
        根据意图获取插件信息
        
        Args:
            intent: 意图关键词
            
        Returns:
            插件信息字典，包含plugin_name和params
        """
        return self.registry.get(intent)
    
    def get_all_intents(self) -> List[str]:
        """
        获取所有支持的意图
        
        Returns:
            意图关键词列表
        """
        return list(self.registry.keys())
    
    def validate_params(self, intent: str, params: Dict[str, Any]) -> tuple[bool, str]:
        """
        验证参数是否符合插件入参规范
        
        Args:
            intent: 意图关键词
            params: 参数字典
            
        Returns:
            (是否验证通过, 错误信息)
        """
        plugin_info = self.get_plugin_info(intent)
        if not plugin_info:
            return False, f"意图 {intent} 不存在"
        
        param_specs = plugin_info.get("params", [])
        for param_spec in param_specs:
            param_name = param_spec["name"]
            required = param_spec.get("required", False)
            
            if required and param_name not in params:
                return False, f"缺少必填参数: {param_name}"
            
            # 类型验证
            if param_name in params:
                param_type = param_spec.get("type", "string")
                param_value = params[param_name]
                
                if param_type == "string" and not isinstance(param_value, str):
                    return False, f"参数 {param_name} 类型错误，期望字符串"
                elif param_type == "number" and not isinstance(param_value, (int, float)):
                    return False, f"参数 {param_name} 类型错误，期望数字"
        
        return True, "验证通过"


# 创建全局插件注册中心实例
plugin_registry = PluginRegistry()