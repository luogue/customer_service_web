"""
简单测试精排服务
"""

from knowledge_base.ranking_service import get_ranking_service


def test_ranking_service():
    """测试精排服务"""
    print("=== 测试精排服务 ===")
    
    # 获取精排服务实例
    ranking_service = get_ranking_service()
    
    # 模拟召回结果
    recalled_items = [
        {
            "id": 1,
            "content": "【下单失败】常见原因包括网络不稳定、商品库存不足、账户风控限制、地址填写不完整、支付方式异常；解决方法：刷新页面重新下单、检查网络连接、核对收货地址完整性、切换支付方式、联系淘宝小二排查账户风控问题。",
            "document_id": 1,
            "similarity": 0.5
        },
        {
            "id": 2,
            "content": "退款申请一般在3-5个工作日内处理完成。",
            "document_id": 1,
            "similarity": 0.5
        },
        {
            "id": 3,
            "content": "【退款到账时效】仅退款未发货：退款申请审核通过后，1-3个工作日到账，支付宝微信支付即时到账，银行卡2-3个工作日；退货退款已发货：商家确认收到退货后，1-3个工作日到账，具体到账时间以支付方式为准。",
            "document_id": 1,
            "similarity": 0.5
        },
        {
            "id": 4,
            "content": "【合并订单】仅支持未付款的订单，用户可在我的订单中选择多个未付款订单，点击合并付款，合并后仅生成一个物流单号，运费按合并后总金额计算；已付款订单无法合并。",
            "document_id": 1,
            "similarity": 0.5
        }
    ]
    
    # 测试查询
    test_queries = [
        "下单失败",
        "退款",
        "物流"
    ]
    
    for query in test_queries:
        print(f"\n测试查询: {query}")
        
        # 精排
        ranked_results = ranking_service.rank(query, recalled_items, top_k=3)
        print(f"精排后结果数量: {len(ranked_results)}")
        
        # 显示结果
        print("精排结果:")
        for i, result in enumerate(ranked_results):
            similarity = result.get('similarity', 0)
            ranking_score = result.get('ranking_score', 0)
            print(f"  {i+1}. ID: {result['id']}, 相似度: {similarity:.4f}, 排序分数: {ranking_score:.4f}")
            print(f"     内容: {result['content'][:100]}...")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_ranking_service()
