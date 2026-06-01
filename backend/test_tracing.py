"""
测试链路追踪功能
"""
import asyncio
import aiohttp
import json

print("=== 测试链路追踪功能 ===")

async def test_tracing():
    async with aiohttp.ClientSession() as session:
        # 测试智能客服接口
        print("\n1. 测试智能客服接口...")
        payload = {
            "message": "帮我查下订单",
            "session_id": "test_session_001",
            "user_id": "u001",
            "phone": "13800000000"
        }
        
        async with session.post("http://localhost:8003/api/chat/message", json=payload) as response:
            print(f"响应状态码: {response.status}")
            print(f"响应头: {dict(response.headers)}")
            
            # 检查是否包含X-Trace-ID头
            trace_id = response.headers.get("X-Trace-ID")
            if trace_id:
                print(f"X-Trace-ID: {trace_id}")
            else:
                print("警告: 响应中没有X-Trace-ID头")
            
            # 读取响应内容
            content = await response.content.read()
            print(f"响应内容: {content[:1000]}...")  # 只打印前1000个字符

        # 测试健康检查接口
        print("\n2. 测试健康检查接口...")
        async with session.get("http://localhost:8003/health") as response:
            print(f"响应状态码: {response.status}")
            print(f"响应头: {dict(response.headers)}")
            
            # 检查是否包含X-Trace-ID头
            trace_id = response.headers.get("X-Trace-ID")
            if trace_id:
                print(f"X-Trace-ID: {trace_id}")
            else:
                print("警告: 响应中没有X-Trace-ID头")
            
            # 读取响应内容
            data = await response.json()
            print(f"响应内容: {data}")

# 运行测试
asyncio.run(test_tracing())

print("\n链路追踪功能测试完成！")
