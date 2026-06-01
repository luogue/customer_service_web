from llm_adapter.llm_client import ai_service
import asyncio

async def test_ai_service():
    """测试AI服务"""
    print("测试AI服务...")
    response = await ai_service.generate_response('你好，我想咨询一下退款问题')
    print(f"AI响应: {response}")

if __name__ == "__main__":
    asyncio.run(test_ai_service())