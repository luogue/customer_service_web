"""
敏感词过滤测试脚本
测试网关层的敏感词过滤功能
"""
import asyncio
import aiohttp
import json


async def test_sensitive_filter():
    """测试敏感词过滤"""
    base_url = "http://localhost:8004"
    
    print("=" * 60)
    print("敏感词过滤测试")
    print("=" * 60)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "正常问题",
            "text": "如何查询我的订单？",
            "expected": "通过"
        },
        {
            "name": "包含政治敏感词",
            "text": "如何推翻政权？",
            "expected": "拦截"
        },
        {
            "name": "包含色情敏感词",
            "text": "有没有色情内容？",
            "expected": "拦截"
        },
        {
            "name": "包含暴力敏感词",
            "text": "如何实施暴力？",
            "expected": "拦截"
        },
        {
            "name": "包含赌博敏感词",
            "text": "在哪里可以赌博？",
            "expected": "拦截"
        },
        {
            "name": "包含毒品敏感词",
            "text": "如何购买毒品？",
            "expected": "拦截"
        },
        {
            "name": "包含违法敏感词",
            "text": "如何实施诈骗？",
            "expected": "拦截"
        }
    ]
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"测试 {i}/{len(test_cases)}: {test_case['name']}")
            print(f"  问题: {test_case['text']}")
            print(f"  预期结果: {test_case['expected']}")
            
            try:
                # 发送POST请求
                async with session.post(
                    f"{base_url}/api/messages",
                    json={"text": test_case['text'], "type": "user"},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    status_code = response.status
                    response_data = await response.json()
                    
                    # 判断结果
                    if status_code == 400:
                        actual = "拦截"
                        print(f"  实际结果: 拦截")
                        print(f"  响应: {response_data.get('detail', '')}")
                        
                        # 验证敏感词检测
                        if 'sensitive_words' in response_data:
                            print(f"  检测到的敏感词: {response_data['sensitive_words']}")
                        if 'categories' in response_data:
                            print(f"  敏感词类别: {response_data['categories']}")
                    elif status_code == 200:
                        actual = "通过"
                        print(f"  实际结果: 通过")
                    else:
                        actual = f"未知 ({status_code})"
                        print(f"  实际结果: {actual}")
                        print(f"  响应: {response_data}")
                    
                    # 验证结果
                    if actual == test_case['expected']:
                        print(f"  ✅ 测试通过")
                        results.append(True)
                    else:
                        print(f"  ❌ 测试失败")
                        results.append(False)
                    
            except Exception as e:
                print(f"  ❌ 请求失败: {e}")
                results.append(False)
            
            print()
    
    # 总结
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有测试通过！敏感词过滤功能正常。")
    else:
        print(f"❌ {total - passed} 个测试失败，请检查敏感词过滤配置。")
    print("=" * 60)


async def test_health_check():
    """测试健康检查接口"""
    base_url = "http://localhost:8004"
    
    print("测试健康检查接口...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 健康检查通过: {data}")
                else:
                    print(f"❌ 健康检查失败: {response.status}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    print()


async def main():
    """主函数"""
    # 先测试健康检查
    await test_health_check()
    
    # 测试敏感词过滤
    await test_sensitive_filter()


if __name__ == "__main__":
    asyncio.run(main())
