"""
测试上下文管理模块
"""
import requests
import json

BASE_URL = "http://localhost:8002/api"
SESSION_ID = "test_session_001"

def print_response(response):
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print("-" * 80)

print("=" * 80)
print("测试1: 创建会话")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/context/session/create",
    json={
        "session_id": SESSION_ID,
        "user_id": 1
    }
)
print_response(response)

print("\n" * 2)
print("=" * 80)
print("测试2: 获取会话信息")
print("=" * 80)
response = requests.get(f"{BASE_URL}/context/session/{SESSION_ID}")
print_response(response)

print("\n" * 2)
print("=" * 80)
print("测试3: 更新业务上下文")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/context/business/update",
    json={
        "session_id": SESSION_ID,
        "current_intent": "order_query",
        "current_step": "phone_confirm",
        "user_phone": "13800000000",
        "custom_params": {"test": "value"}
    }
)
print_response(response)

print("\n" * 2)
print("=" * 80)
print("测试4: 获取业务上下文")
print("=" * 80)
response = requests.get(f"{BASE_URL}/context/business/{SESSION_ID}")
print_response(response)

print("\n" * 2)
print("=" * 80)
print("测试5: 保存用户消息")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/context/message/save",
    json={
        "session_id": SESSION_ID,
        "role": "user",
        "content": "你好，我想查一下订单"
    }
)
print_response(response)

print("\n" * 2)
print("=" * 80)
print("测试6: 保存AI回复")
print("=" * 80)
response = requests.post(
    f"{BASE_URL}/context/message/save",
    json={
        "session_id": SESSION_ID,
        "role": "ai",
        "content": "您好，请先告诉我您的手机号，方便我为您查询订单。"
    }
)
print_response(response)

print("\n" * 2)
print("=" * 80)
print("测试7: 获取最近对话")
print("=" * 80)
response = requests.get(f"{BASE_URL}/context/messages/{SESSION_ID}/recent?count=10")
print_response(response)

print("\n" * 2)
print("=" * 80)
print("测试8: 构建大模型Prompt")
print("=" * 80)
response = requests.get(f"{BASE_URL}/context/prompt/{SESSION_ID}?max_recent_turns=10")
print_response(response)

print("\n" * 2)
print("=" * 80)
print("测试9: 结束会话（不清理数据）")
print("=" * 80)
response = requests.post(f"{BASE_URL}/context/session/{SESSION_ID}/end")
print_response(response)

print("\n" * 2)
print("=" * 80)
print("测试10: 获取完整消息列表")
print("=" * 80)
response = requests.get(f"{BASE_URL}/context/messages/{SESSION_ID}")
print_response(response)

print("\n" * 2)
print("=" * 80)
print("✅ 所有测试完成！")
print("=" * 80)
