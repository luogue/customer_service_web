from llm_adapter.intent_mock import intent_mock_service

# 测试"发票"关键词的意图识别
input_text = "发票"
result = intent_mock_service.recognize_intent('u001', '13800000000', input_text)

print(f"输入: {input_text}")
print(f"识别到的意图: {[intent.intent_type for intent in result.intents]}")
print(f"意图详情: {result.intents}")

# 测试其他相关关键词
other_inputs = ["开发票", "怎么开发票", "发票问题"]
for text in other_inputs:
    result = intent_mock_service.recognize_intent('u001', '13800000000', text)
    print(f"\n输入: {text}")
    print(f"识别到的意图: {[intent.intent_type for intent in result.intents]}")
