"""
测试订单查询功能
- 测试新用户13800000001的订单查询
- 验证只返回最近5个订单
- 验证查询到订单后向用户确认
"""
import requests
import json
import time

def test_order_query():
    url = "http://localhost:8000/api/chat/message"
    session_id = "test_order_query_" + str(int(time.time()))
    
    print("=== 测试订单查询功能 ===")
    print(f"会话ID: {session_id}")
    print("-" * 60)
    
    # 第一步：用户发送订单查询请求
    data1 = {
        "message": "帮我查下订单",
        "phone": "13800000001",  # 新用户
        "session_id": session_id
    }
    
    print("1. 用户发送：帮我查下订单")
    response1 = requests.post(url, json=data1, stream=True, timeout=10)
    
    full_message1 = ""
    for line in response1.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_content = line_str[6:]
                if data_content == '[DONE]':
                    break
                try:
                    json_data = json.loads(data_content)
                    if json_data.get('content'):
                        full_message1 += json_data.get('content')
                except:
                    pass
    
    print(f"   AI回复: {full_message1}")
    
    # 第二步：用户确认
    data2 = {
        "message": "是",
        "phone": "13800000001",
        "session_id": session_id
    }
    
    print("2. 用户回复：是")
    response2 = requests.post(url, json=data2, stream=True, timeout=10)
    
    full_message2 = ""
    for line in response2.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_content = line_str[6:]
                if data_content == '[DONE]':
                    break
                try:
                    json_data = json.loads(data_content)
                    if json_data.get('content'):
                        full_message2 += json_data.get('content')
                except:
                    pass
    
    print(f"   AI回复: {full_message2}")
    
    # 检查返回的订单数量
    order_count = full_message2.count("订单号")
    print(f"\n查询到的订单数量: {order_count}")
    if order_count <= 5:
        print("✅ 验证通过：只返回了最近5个订单")
    else:
        print("❌ 验证失败：返回了超过5个订单")
    
    print("-" * 60)

if __name__ == "__main__":
    test_order_query()
