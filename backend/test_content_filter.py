"""
内容过滤测试脚本
测试推理生成层的敏感词过滤功能
"""
import asyncio
from llm_adapter.stream_generator import stream_generator
from security.sensitive_filter import sensitive_filter
import json


async def test_content_filter():
    """测试内容过滤功能"""
    print("=" * 60)
    print("内容过滤测试")
    print("=" * 60)
    print()
    
    # 测试用例
    test_cases = [
        {
            "name": "正常内容",
            "text": "您好，请问有什么可以帮助您的？",
            "expected": "通过"
        },
        {
            "name": "包含敏感词",
            "text": "如何参与赌博活动？",
            "expected": "过滤"
        },
        {
            "name": "包含业务违禁词",
            "text": "我这里有刷单兼职，您需要吗？",
            "expected": "过滤"
        },
        {
            "name": "包含敏感词和业务违禁词（低占比）",
            "text": "您好，我想了解一下关于赌博的相关信息，还有刷单的事情",
            "expected": "过滤"
        },
        {
            "name": "全量违规",
            "text": "赌博、色情、暴力、诈骗",
            "expected": "兜底回答"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试 {i}/{len(test_cases)}: {test_case['name']}")
        print(f"  文本: {test_case['text']}")
        print(f"  预期结果: {test_case['expected']}")
        
        # 测试过滤函数
        filter_result = sensitive_filter.filter_content(
            text=test_case['text'],
            filter_dimensions=["敏感词", "业务违禁词", "格式校验"]
        )
        
        print(f"  原始文本: {filter_result['original_text']}")
        print(f"  过滤后文本: {filter_result['filtered_text']}")
        print(f"  是否违规: {filter_result['has_violation']}")
        if filter_result['violation_words']:
            print(f"  违规词: {filter_result['violation_words']}")
        if filter_result['violation_categories']:
            print(f"  违规类别: {filter_result['violation_categories']}")
        if filter_result['fallback_response']:
            print(f"  兜底回答: {filter_result['fallback_response']}")
        print(f"  处理时间: {filter_result['processing_time']:.4f}秒")
        print(f"  过滤启用: {filter_result['filter_enabled']}")
        
        # 判断结果
        if not filter_result['has_violation']:
            actual = "通过"
        elif filter_result['fallback_response']:
            actual = "兜底回答"
        else:
            actual = "过滤"
        
        if actual == test_case['expected']:
            print(f"  ✅ 测试通过")
            results.append(True)
        else:
            print(f"  ❌ 测试失败")
            results.append(False)
        
        print()
    
    # 测试流式生成中的过滤
    print("测试流式生成中的过滤...")
    print()
    
    try:
        async for chunk in stream_generator.generate_stream("测试消息"):
            if chunk != "[DONE]":
                print(f"  流式输出: {chunk}")
            else:
                print(f"  流式输出: [DONE]")
    except Exception as e:
        print(f"  ❌ 流式生成失败: {e}")
    
    print()
    
    # 测试过滤开关
    print("测试过滤开关...")
    print(f"  过滤当前状态: {sensitive_filter.filter_enabled}")
    
    # 关闭过滤
    sensitive_filter.set_filter_enabled(False)
    print(f"  关闭过滤后: {sensitive_filter.filter_enabled}")
    
    # 测试关闭过滤后的效果
    filter_result = sensitive_filter.filter_content(
        text="赌博、色情、暴力",
        filter_dimensions=["敏感词"]
    )
    print(f"  关闭过滤后结果: {filter_result['filtered_text']}")
    print(f"  是否违规: {filter_result['has_violation']}")
    
    # 重新开启过滤
    sensitive_filter.set_filter_enabled(True)
    print(f"  重新开启过滤: {sensitive_filter.filter_enabled}")
    
    # 总结
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有测试通过！内容过滤功能正常。")
    else:
        print(f"❌ {total - passed} 个测试失败，请检查过滤配置。")
    print("=" * 60)


async def main():
    """主函数"""
    await test_content_filter()


if __name__ == "__main__":
    asyncio.run(main())
