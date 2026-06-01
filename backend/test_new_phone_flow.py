"""
测试新的订单查询流程：
1. 用户确认是这个手机号下单
2. 系统查询订单（无订单）
3. 系统提示用户提供新手机号
4. 用户提供新手机号
5. 系统使用新手机号查询订单
"""
import requests
import json
import time

def test_new_phone_flow():
    url = "http://localhost:8000/api/chat/message"
    session_id = "test_new_phone_" + str(int(time.time()))
    
    print("=== 测试新手机号流程 ===")
    print(f"会话ID: {session_id}")
    print("-" * 50)
    
    # 第一步：用户发送订单查询请求
    data1 = {
        "message": "帮我查下订单",
        "phone": "13800000000",
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
    print("-" * 50)
    
    # 第二步：用户确认
    data2 = {
        "message": "是",
        "phone": "13800000000",
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
    print("-" * 50)
    
    # 第三步：用户提供新手机号
    data3 = {
        "message": "13912345678",
        "phone": "13800000000",  # 保持原手机号，系统会在会话状态中更新
        "session_id": session_id
    }
    
    print("3. 用户提供新手机号：13912345678")
    response3 = requests.post(url, json=data3, stream=True, timeout=10)
    
    full_message3 = ""
    for line in response3.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_content = line_str[6:]
                if data_content == '[DONE]':
                    break
                try:
                    json_data = json.loads(data_content)
                    if json_data.get('content'):
                        full_message3 += json_data.get('content')
                except:
                    pass
    
    print(f"   AI回复: {full_message3}")
    print("-" * 50)

if __name__ == "__main__":
    test_new_phone_flow()
