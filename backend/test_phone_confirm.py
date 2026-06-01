"""
测试手机号确认流程：
1. 用户查询订单
2. 系统确认手机号
3. 用户说"不是这个手机号" → 应该提示切换账号登录，不转人工
4. 用户说"是这个手机号" → 应该转人工
"""
import requests
import json
import time

def test_not_this_phone():
    url = "http://localhost:8001/api/chat/message"
    session_id = "test_not_phone_" + str(int(time.time()))
    
    print("=== 测试：用户说'不是这个手机号' ===")
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
    
    # 第三步：用户说不是这个手机号
    data3 = {
        "message": "不是",
        "phone": "13800000000",
        "session_id": session_id
    }
    
    print("3. 用户回复：不是（不是这个手机号）")
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
    
    # 验证回复内容
    if "为了您的账户安全，仅支持查询当前登录账号绑定的订单，如需查询其他手机号，请切换账号登录后重试。" in full_message3:
        print("\n✅ 验证通过：用户说'不是这个手机号'时，提示切换账号登录，不转人工")
    elif "已为您转接人工客服" in full_message3:
        print("\n❌ 验证失败：错误地转人工了")
    else:
        print("\n❌ 验证失败：回复内容不符合预期")
    
    print("-" * 60)

def test_yes_this_phone():
    url = "http://localhost:8001/api/chat/message"
    session_id = "test_yes_phone_" + str(int(time.time()))
    
    print("\n=== 测试：用户说'是这个手机号' ===")
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
    
    # 第三步：用户说是这个手机号
    data3 = {
        "message": "是",
        "phone": "13800000000",
        "session_id": session_id
    }
    
    print("3. 用户回复：是（是这个手机号）")
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
    
    # 验证回复内容
    if "已为您转接人工客服" in full_message3:
        print("\n✅ 验证通过：用户说'是这个手机号'时，转人工")
    else:
        print("\n❌ 验证失败：没有转人工")
    
    print("-" * 60)

if __name__ == "__main__":
    test_not_this_phone()
    test_yes_this_phone()
