"""
测试聊天接口 - 检查返回内容
"""
import requests
import json

def test_chat():
    url = "http://localhost:8000/api/chat/message"
    
    data = {
        "message": "帮我查下订单",
        "phone": "13800000000",
        "session_id": "test123"
    }
    
    print("发送请求:", json.dumps(data, ensure_ascii=False))
    print("-" * 50)
    
    full_messages = []
    
    try:
        response = requests.post(url, json=data, stream=True)
        print(f"状态码: {response.status_code}")
        print("-" * 50)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_content = line_str[6:]
                    if data_content == '[DONE]':
                        print("\n收到 [DONE]")
                        break
                    try:
                        json_data = json.loads(data_content)
                        if json_data.get('type') == 'message' and json_data.get('is_end'):
                            print(f"\n消息 {json_data.get('part')} 结束")
                            full_messages.append("")
                        elif json_data.get('content'):
                            if len(full_messages) <= json_data.get('part', 0):
                                full_messages.append("")
                            full_messages[json_data.get('part', 0)] += json_data.get('content')
                    except:
                        pass
        
        print("\n" + "=" * 50)
        print("完整消息:")
        for i, msg in enumerate(full_messages):
            print(f"消息 {i}: {msg}")
                    
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_chat()
