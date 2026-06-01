"""
测试订单查询失败后的确认流程：
1. 用户确认是这个手机号下单 → 转接人工客服
2. 用户否认是这个手机号下单 → 提示提供新手机号
3. 用户提供新手机号 → 提示仅支持查询当前登录账号绑定的订单
4. 用户输入其他内容 → 提示请回答是或不是
"""
import requests
import json
import time

def test_confirmation_scenario():
    url = "http://localhost:8000/api/chat/message"
    session_id = "test_confirmation_" + str(int(time.time()))
    
    print("=== 测试订单查询失败后的确认流程 ===")
    print(f"会话ID: {session_id}")
    print("-" * 60)
    
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
    
    # 第二步：用户确认意图
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
    
    # 第三步：用户确认是这个手机号下单
    data3 = {
        "message": "是",
        "phone": "13800000000",
        "session_id": session_id
    }
    
    print("3. 用户回复：是（确认是这个手机号）")
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
    print("-" * 60)

if __name__ == "__main__":
    test_confirmation_scenario()
