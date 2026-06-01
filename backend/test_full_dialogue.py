from dialogue_engine.order_dialogue import get_order_dialogue_flow
from knowledge_base.models import get_db
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

# 获取对话流实例
db = next(get_db())
dialogue_flow = get_order_dialogue_flow(db)

# 模拟对话流程
session_id = "test_invoice_session"

# 第一次发送消息："发票"
print("用户: 发票")
result1 = dialogue_flow.process_message("u001", "13800000000", "发票", session_id)
print("AI:", result1.get("responses", []))
print("会话状态:", dialogue_flow.session_states.get(session_id, {}))
print()

# 检查意图识别结果
if session_id in dialogue_flow.session_states:
    intent_result = dialogue_flow.session_states[session_id].get("intent_result")
    if intent_result:
        print("意图识别结果:", intent_result.intents)
        print("用户输入内容:", intent_result.content)
print()

# 第二次发送消息："是"（确认意图）
print("用户: 是")
result2 = dialogue_flow.process_message("u001", "13800000000", "是", session_id)
print("AI:", result2.get("responses", []))
print("会话状态:", dialogue_flow.session_states.get(session_id, {}))
