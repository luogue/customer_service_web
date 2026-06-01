from dialogue_engine.order_dialogue import get_order_dialogue_flow
from knowledge_base.models import get_db
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

# 获取对话流实例
db = next(get_db())
dialogue_flow = get_order_dialogue_flow(db)

# 模拟对话流程
session_id = "test_transfer_session"

print("=== 测试连续意图识别失败3次触发转人工 ===")
print()

# 第一次发送消息
print("用户: 发票")
result1 = dialogue_flow.process_message("u001", "13800000000", "发票", session_id)
print("AI:", result1.get("responses", []))
print("失败次数:", dialogue_flow.session_states[session_id].get("failed_attempts"))
print()

# 第一次拒绝
print("用户: 不是")
result2 = dialogue_flow.process_message("u001", "13800000000", "不是", session_id)
print("AI:", result2.get("responses", []))
print("失败次数:", dialogue_flow.session_states[session_id].get("failed_attempts"))
print()

# 第二次发送消息
print("用户: 下单失败")
result3 = dialogue_flow.process_message("u001", "13800000000", "下单失败", session_id)
print("AI:", result3.get("responses", []))
print("失败次数:", dialogue_flow.session_states[session_id].get("failed_attempts"))
print()

# 第二次拒绝
print("用户: 不是")
result4 = dialogue_flow.process_message("u001", "13800000000", "不是", session_id)
print("AI:", result4.get("responses", []))
print("失败次数:", dialogue_flow.session_states[session_id].get("failed_attempts"))
print()

# 第三次发送消息
print("用户: 限购规则")
result5 = dialogue_flow.process_message("u001", "13800000000", "限购规则", session_id)
print("AI:", result5.get("responses", []))
print("失败次数:", dialogue_flow.session_states[session_id].get("failed_attempts"))
print()

# 第三次拒绝 - 应该触发转人工
print("用户: 不是")
result6 = dialogue_flow.process_message("u001", "13800000000", "不是", session_id)
print("AI:", result6.get("responses", []))
print("失败次数:", dialogue_flow.session_states[session_id].get("failed_attempts"))
print("会话状态:", dialogue_flow.session_states[session_id].get("step"))
print()

print("=== 测试成功识别时重置失败次数 ===")
print()

# 新会话
session_id2 = "test_success_session"

# 发送消息
print("用户: 发票")
result7 = dialogue_flow.process_message("u001", "13800000000", "发票", session_id2)
print("AI:", result7.get("responses", []))
print()

# 确认意图
print("用户: 是")
result8 = dialogue_flow.process_message("u001", "13800000000", "是", session_id2)
print("AI:", result8.get("responses", []))
print("失败次数:", dialogue_flow.session_states[session_id2].get("failed_attempts"))
