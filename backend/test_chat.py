"""
测试聊天接口
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
    
    try:
        response = requests.post(url, json=data, stream=True)
        print(f"状态码: {response.status_code}")
        print("-" * 50)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_content = line_str[6:]
                    print(f"收到: {data_content}")
                    
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_chat()
