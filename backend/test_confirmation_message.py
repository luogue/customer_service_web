"""
测试确认消息是否已改为"请回复'是'或'不是'"：
"""
import requests
import json
import time

def test_confirmation_message():
    url = "http://localhost:8000/api/chat/message"
    session_id = "test_confirmation_msg_" + str(int(time.time()))
    
    print("=== 测试确认消息修改 ===")
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
    
    # 验证回复内容
    if "请回复\"是\"或\"不是\"" in full_message1:
        print("\n✅ 验证通过：确认消息已改为'请回复是或不是'")
    else:
        print("\n❌ 验证失败：确认消息未改为'请回复是或不是'")
    
    # 第二步：用户输入无法识别的内容
    data2 = {
        "message": "随便",
        "phone": "13800000000",
        "session_id": session_id
    }
    
    print("\n2. 用户发送：随便（无法识别的内容）")
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
    
    # 验证回复内容
    if "请回复\"是\"或\"不是\"" in full_message2:
        print("\n✅ 验证通过：无法识别时的提示已改为'请回复是或不是'")
    else:
        print("\n❌ 验证失败：无法识别时的提示未改为'请回复是或不是'")
    
    print("-" * 60)

if __name__ == "__main__":
    test_confirmation_message()
