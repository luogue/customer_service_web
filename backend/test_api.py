"""
测试知识底座层 API 接口
"""

import requests
import json

BASE_URL = "http://localhost:8002/api/knowledge"

def test_health():
    """测试健康检查接口"""
    print("测试健康检查接口...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_faq():
    """测试FAQ接口"""
    print("测试FAQ接口...")
    
    # 创建FAQ
    faq_data = {
        "question": "如何申请退款？",
        "answer": "您可以在订单详情页面点击申请退款按钮，按照提示操作即可。",
        "keywords": ["退款", "申请", "退货"]
    }
    response = requests.post(f"{BASE_URL}/faqs", json=faq_data)
    print(f"创建FAQ - 状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 搜索FAQ
    query = "退款"
    response = requests.get(f"{BASE_URL}/faqs/search/{query}")
    print(f"搜索FAQ - 状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_user():
    """测试用户接口"""
    print("测试用户接口...")
    
    # 创建用户
    user_data = {
        "phone": "13800138000",
        "username": "test_user",
        "name": "测试用户",
        "address": "北京市朝阳区",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"创建用户 - 状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 获取用户
    user_id = response.json().get("user", {}).get("id")
    if user_id:
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print(f"获取用户 - 状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    print()

def test_document():
    """测试文档接口"""
    print("测试文档接口...")
    
    # 创建文档
    document_data = {
        "title": "用户使用指南",
        "content": "这是一份用户使用指南，包含了产品的基本操作方法。",
        "file_name": "user_guide.md",
        "file_type": "markdown"
    }
    response = requests.post(f"{BASE_URL}/documents", json=document_data)
    print(f"创建文档 - 状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 获取所有文档
    response = requests.get(f"{BASE_URL}/documents")
    print(f"获取所有文档 - 状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def main():
    """主函数"""
    print("测试知识底座层 API 接口")
    print("=" * 50)
    
    test_health()
    test_faq()
    test_user()
    test_document()
    
    print("测试完成！")

if __name__ == "__main__":
    main()
