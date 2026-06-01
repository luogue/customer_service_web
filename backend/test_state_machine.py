"""
测试对话状态机
验证流程控制逻辑
"""
import requests
import json
import time

def test_state_machine():
    url = "http://localhost:8001/api/chat/message"
    
    print("=== 测试对话状态机 ===")
    print("-" * 60)
    
    # 测试1: 正常流程 - 用户按流程回复
    print("\n【测试1】正常流程 - 用户按流程回复")
    session_id = "test_normal_" + str(int(time.time()))
    
    # 1.1 用户查询订单
    print("1. 用户: 帮我查下订单")
    r1 = send_message(url, session_id, "帮我查下订单")
    print(f"   AI: {r1}")
    
    # 1.2 用户确认意图
    print("2. 用户: 是")
    r2 = send_message(url, session_id, "是")
    print(f"   AI: {r2}")
    
    # 1.3 用户确认手机号（假设没查到订单）
    print("3. 用户: 是")
    r3 = send_message(url, session_id, "是")
    print(f"   AI: {r3}")
    
    # 测试2: 流程打断 - 用户不按流程回复
    print("\n【测试2】流程打断 - 在确认节点发送其他内容")
    session_id2 = "test_interrupt_" + str(int(time.time()))
    
    # 2.1 用户查询订单
    print("1. 用户: 帮我查下订单")
    r4 = send_message(url, session_id2, "帮我查下订单")
    print(f"   AI: {r4}")
    
    # 2.2 用户不按流程回复，而是发送新内容
    print("2. 用户: 我想退款（打断流程）")
    r5 = send_message(url, session_id2, "我想退款")
    print(f"   AI: {r5}")
    print(f"   是否打断: {'interrupted' in r5 or '退款' in r5}")
    
    # 测试3: 在手机号确认节点说"不是"
    print("\n【测试3】手机号确认节点说'不是'")
    session_id3 = "test_phone_no_" + str(int(time.time()))
    
    # 3.1 用户查询订单
    print("1. 用户: 帮我查下订单")
    r6 = send_message(url, session_id3, "帮我查下订单")
    print(f"   AI: {r6}")
    
    # 3.2 用户确认意图
    print("2. 用户: 是")
    r7 = send_message(url, session_id3, "是")
    print(f"   AI: {r7}")
    
    # 3.3 用户说不是这个手机号
    print("3. 用户: 不是")
    r8 = send_message(url, session_id3, "不是")
    print(f"   AI: {r8}")
    
    print("\n" + "=" * 60)
    print("测试完成!")


def send_message(url, session_id, message, phone="13800000000"):
    """发送消息并获取完整回复"""
    data = {
        "message": message,
        "phone": phone,
        "session_id": session_id
    }
    
    try:
        response = requests.post(url, json=data, stream=True, timeout=10)
        full_message = ""
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_content = line_str[6:]
                    if data_content == '[DONE]':
                        break
                    try:
                        json_data = json.loads(data_content)
                        if json_data.get('content'):
                            full_message += json_data.get('content')
                    except:
                        pass
        
        return full_message
    except Exception as e:
        return f"错误: {e}"


if __name__ == "__main__":
    test_state_machine()
