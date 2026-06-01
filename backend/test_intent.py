from llm_adapter.intent_mock import intent_mock_service

# 测试不同的输入
test_inputs = [
    "咨询一下下单失败的问题",
    "发票怎么开",
    "限购规则是什么",
    "下单失败怎么办",
    "我要开发票"
]

for input_text in test_inputs:
    result = intent_mock_service.recognize_intent('u001', '13800000000', input_text)
    print(f"输入: {input_text}")
    print(f"识别到的意图: {[intent.intent_type for intent in result.intents]}")
    print()
