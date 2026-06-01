"""
测试用户否认是这个手机号的流程：
1. 用户查询订单
2. 系统确认手机号
3. 用户否认是这个手机号
4. 系统提示切换账号登录
"""
import requests
import json
import time

def test_reject_phone():
    url = "http://localhost:8000/api/chat/message"
    session_id = "test_reject_phone_" + str(int(time.time()))
    
    print("=== 测试用户否认是这个手机号的流程 ===")
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
    
    # 第三步：用户否认是这个手机号
    data3 = {
        "message": "否",
        "phone": "13800000000",
        "session_id": session_id
    }
    
    print("3. 用户回复：否（否认是这个手机号）")
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
        print("\n✅ 验证通过：系统正确提示用户切换账号登录")
    else:
        print("\n❌ 验证失败：系统没有正确提示用户切换账号登录")
    
    print("-" * 60)

if __name__ == "__main__":
    test_reject_phone()
