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

def test_phone_confirmation_flow():
    url = "http://localhost:8000/api/chat/message"
    
    print("=== 测试订单查询失败后的确认流程 ===")
    print("-" * 60)
    
    # 测试场景1：用户确认是这个手机号下单
    session_id1 = "test_confirm_" + str(int(time.time()))
    print("\n场景1: 用户确认是这个手机号下单")
    print(f"会话ID: {session_id1}")
    print("-" * 60)
    
    # 第一步：用户发送订单查询请求
    data1 = {
        "message": "帮我查下订单",
        "phone": "13800000000",
        "session_id": session_id1
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
        "phone": "13800000000",
        "session_id": session_id1
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
    print("-" * 60)
    
    # 测试场景2：用户否认是这个手机号下单
    session_id2 = "test_reject_" + str(int(time.time()))
    print("\n场景2: 用户否认是这个手机号下单")
    print(f"会话ID: {session_id2}")
    print("-" * 60)
    
    # 第一步：用户发送订单查询请求
    data3 = {
        "message": "帮我查下订单",
        "phone": "13800000000",
        "session_id": session_id2
    }
    
    print("1. 用户发送：帮我查下订单")
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
    
    # 第二步：用户否认
    data4 = {
        "message": "否",
        "phone": "13800000000",
        "session_id": session_id2
    }
    
    print("2. 用户回复：否")
    response4 = requests.post(url, json=data4, stream=True, timeout=10)
    
    full_message4 = ""
    for line in response4.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_content = line_str[6:]
                if data_content == '[DONE]':
                    break
                try:
                    json_data = json.loads(data_content)
                    if json_data.get('content'):
                        full_message4 += json_data.get('content')
                except:
                    pass
    
    print(f"   AI回复: {full_message4}")
    print("-" * 60)
    
    # 测试场景3：用户提供新手机号
    session_id3 = "test_new_phone_" + str(int(time.time()))
    print("\n场景3: 用户提供新手机号")
    print(f"会话ID: {session_id3}")
    print("-" * 60)
    
    # 第一步：用户发送订单查询请求
    data5 = {
        "message": "帮我查下订单",
        "phone": "13800000000",
        "session_id": session_id3
    }
    
    print("1. 用户发送：帮我查下订单")
    response5 = requests.post(url, json=data5, stream=True, timeout=10)
    
    full_message5 = ""
    for line in response5.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_content = line_str[6:]
                if data_content == '[DONE]':
                    break
                try:
                    json_data = json.loads(data_content)
                    if json_data.get('content'):
                        full_message5 += json_data.get('content')
                except:
                    pass
    
    print(f"   AI回复: {full_message5}")
    
    # 第二步：用户提供新手机号
    data6 = {
        "message": "输错了，正确的是13811111111",
        "phone": "13800000000",
        "session_id": session_id3
    }
    
    print("2. 用户回复：输错了，正确的是13811111111")
    response6 = requests.post(url, json=data6, stream=True, timeout=10)
    
    full_message6 = ""
    for line in response6.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_content = line_str[6:]
                if data_content == '[DONE]':
                    break
                try:
                    json_data = json.loads(data_content)
                    if json_data.get('content'):
                        full_message6 += json_data.get('content')
                except:
                    pass
    
    print(f"   AI回复: {full_message6}")
    print("-" * 60)

if __name__ == "__main__":
    test_phone_confirmation_flow()
