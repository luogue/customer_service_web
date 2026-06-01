from dialogue_engine.order_dialogue import get_order_dialogue_flow
from knowledge_base.models import get_db

# 获取对话流实例
db = next(get_db())
dialogue_flow = get_order_dialogue_flow(db)

# 模拟对话流程
session_id = "test_session"

# 第一次发送消息："发票怎么开"
print("用户: 发票怎么开")
result1 = dialogue_flow.process_message("u001", "13800000000", "发票怎么开", session_id)
print("AI:", result1.get("responses", []))
print()

# 第二次发送消息："是"（确认意图）
print("用户: 是")
result2 = dialogue_flow.process_message("u001", "13800000000", "是", session_id)
print("AI:", result2.get("responses", []))
print()

# 测试另一个问题
print("用户: 下单失败怎么办")
result3 = dialogue_flow.process_message("u001", "13800000000", "下单失败怎么办", "test_session2")
print("AI:", result3.get("responses", []))
print()

print("用户: 是")
result4 = dialogue_flow.process_message("u001", "13800000000", "是", "test_session2")
print("AI:", result4.get("responses", []))
