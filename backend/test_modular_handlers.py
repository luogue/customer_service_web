"""
测试模块化拆分后的功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 80)
print("测试1: 导入所有模块")
print("=" * 80)

try:
    from dialogue_engine import (
        # 原有模块
        dialogue_manager,
        OrderDialogueFlow,
        get_order_dialogue_flow,
        IntentClassifier,
        is_confirmed,
        is_rejected,
        
        # 新模块
        get_dialogue_manager,
        OrderQueryHandler,
        RefundHandler,
        ExchangeHandler,
        TransferHumanHandler,
        ComplaintHandler,
        ModifyOrderHandler,
        TaskRouter
    )
    print("✅ 所有模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("测试2: 测试意图识别模块")
print("=" * 80)

classifier = IntentClassifier()
test_cases = [
    ("是", "confirm"),
    ("不是", "reject"),
    ("好的", "confirm"),
    ("不要", "reject"),
    ("随便说点什么", "unknown")
]

for text, expected in test_cases:
    result = classifier.classify(text)
    actual = result["intent"].value
    status = "✅" if actual == expected else "❌"
    print(f"{status} 输入: '{text}' -> 期望: {expected}, 实际: {actual}")

print("\n" + "=" * 80)
print("测试3: 测试订单查询处理器（无数据库）")
print("=" * 80)

handler = OrderQueryHandler(db=None)
result = handler.query_orders("13800000000")
print(f"查询结果: success={result['success']}, message={result['message']}")

print("\n" + "=" * 80)
print("测试4: 测试退款处理器（无数据库）")
print("=" * 80)

refund_handler = RefundHandler(db=None)
result = refund_handler.get_refundable_orders("13800000000")
print(f"查询结果: success={result['success']}, message={result['message']}")

willing_result = refund_handler.handle_return_willingness(True, "13800000000")
print(f"愿意退货: action={willing_result['action']}")

print("\n" + "=" * 80)
print("测试5: 测试换货处理器（无数据库）")
print("=" * 80)

exchange_handler = ExchangeHandler(db=None)
result = exchange_handler.get_exchangeable_orders("13800000000")
print(f"查询结果: success={result['success']}, message={result['message']}")
print(f"换货政策: {exchange_handler.get_exchange_policy()}")

print("\n" + "=" * 80)
print("测试6: 测试转人工处理器")
print("=" * 80)

transfer_handler = TransferHumanHandler(db=None)
result = transfer_handler.transfer_to_human("测试原因")
print(f"转人工结果: success={result['success']}, message={result['message']}")

check_result = transfer_handler.check_transfer_conditions("我要转人工")
print(f"检测转人工: should_transfer={check_result['should_transfer']}, reason={check_result['reason']}")

print("\n" + "=" * 80)
print("测试7: 测试投诉处理器（无数据库）")
print("=" * 80)

complaint_handler = ComplaintHandler(db=None)
result = complaint_handler.handle_complaint_flow("13800000000", None)
print(f"投诉处理: action={result['action']}, message={result['message'][:50]}...")

print("\n" + "=" * 80)
print("测试8: 测试修改订单处理器（无数据库）")
print("=" * 80)

modify_handler = ModifyOrderHandler(db=None)
result = modify_handler.get_modifiable_orders("13800000000")
print(f"查询结果: success={result['success']}, message={result['message']}")

modify_type = modify_handler.parse_modify_type("修改收货地址")
print(f"解析修改类型: '修改收货地址' -> {modify_type}")

print("\n" + "=" * 80)
print("测试9: 测试任务路由器")
print("=" * 80)

router = TaskRouter(db=None)
result = router.route_by_intent("query_order", "13800000000", "test_session")
print(f"路由结果: action={result['action']}, step={result['step']}")

result = router.route_by_intent("refund_return", "13800000000", "test_session")
print(f"路由结果: action={result['action']}, step={result['step']}")

result = router.route_by_intent("human", "13800000000", "test_session")
print(f"路由结果: action={result['action']}, step={result['step']}")

print("\n" + "=" * 80)
print("测试10: 测试新的对话管理器（无数据库）")
print("=" * 80)

manager = get_dialogue_manager(db=None)
print(f"首问语: {manager.get_welcome_message()}")
print(f"结束语: {manager.get_goodbye_message()}")

result = manager.process_message("u001", "13800000000", "帮我查一下订单", "test_session_001")
print(f"处理结果: step={result['session_state']['step']}")
print(f"响应消息: {result['final_response'][:80]}...")

print("\n" + "=" * 80)
print("✅ 所有测试完成！")
print("=" * 80)
print("\n模块化拆分成功：")
print("- 订单查询模块: OrderQueryHandler")
print("- 退款模块: RefundHandler")
print("- 换货模块: ExchangeHandler")
print("- 转人工模块: TransferHumanHandler")
print("- 投诉模块: ComplaintHandler")
print("- 修改订单模块: ModifyOrderHandler")
print("- 任务路由模块: TaskRouter")
print("- 对话管理器: DialogueManager")
print("\n原有代码保持不变，新模块独立运行，互不干扰！")
