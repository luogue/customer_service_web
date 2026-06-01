"""
批量添加FAQ到数据库
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_base.models import SessionLocal, FAQ
from knowledge_base.repositories import FAQRepository

# FAQ数据
faq_data = [
    # 1. 订单相关
    {
        "question": "怎么下单？",
        "answer": "选择商品→立即购买→确认地址→提交订单→支付即可。",
        "keywords": ["下单", "购买", "订单"]
    },
    {
        "question": "怎么取消订单？",
        "answer": "未发货订单可在我的订单里直接点击取消申请，已发货需拒收或退货。",
        "keywords": ["取消订单", "订单取消", "退货"]
    },
    {
        "question": "订单怎么修改地址？",
        "answer": "未发货前联系客服修改，已发货无法修改。",
        "keywords": ["修改地址", "地址修改", "订单地址"]
    },
    {
        "question": "怎么查看物流？",
        "answer": "我的订单→查看物流，即可实时追踪。",
        "keywords": ["查看物流", "物流追踪", "物流信息"]
    },
    {
        "question": "为什么物流不更新？",
        "answer": "可能在运输中转，一般 1-2 天更新，超时可联系客服核实。",
        "keywords": ["物流不更新", "物流延迟", "物流信息"]
    },
    # 2. 发货与快递
    {
        "question": "什么时候发货？",
        "answer": "下单后 48 小时内发货，活动期 72 小时内。",
        "keywords": ["发货时间", "什么时候发货", "发货"]
    },
    {
        "question": "发什么快递？",
        "answer": "默认中通 / 圆通，不支持指定。",
        "keywords": ["发什么快递", "快递", "物流"]
    },
    {
        "question": "可以加急吗？",
        "answer": "不支持加急，按付款顺序发货。",
        "keywords": ["加急", "快速发货", "发货顺序"]
    },
    # 3. 售后退货退款
    {
        "question": "支持七天无理由吗？",
        "answer": "支持，不影响二次销售可退。",
        "keywords": ["七天无理由", "无理由退货", "退货"]
    },
    {
        "question": "怎么申请退货？",
        "answer": "我的订单→申请退款退货→填写原因→等待审核→寄回商品。",
        "keywords": ["申请退货", "退货流程", "退款"]
    },
    {
        "question": "运费谁承担？",
        "answer": "质量问题商家承担，个人原因买家承担。",
        "keywords": ["运费", "谁承担运费", "退货运费"]
    },
    {
        "question": "退款多久到账？",
        "answer": "审核通过后，原路退回 1-3 个工作日到账。",
        "keywords": ["退款到账", "退款时间", "到账时间"]
    },
    {
        "question": "换货怎么操作？",
        "answer": "先联系客服→确认可换→寄回商品→我们重发。",
        "keywords": ["换货", "换货流程", "更换商品"]
    },
    # 4. 商品问题
    {
        "question": "是正品吗？",
        "answer": "官方正品，支持验货。",
        "keywords": ["正品", "验货", "真假"]
    },
    {
        "question": "商品有保修吗？",
        "answer": "全国联保一年。",
        "keywords": ["保修", "保修期", "售后"]
    },
    {
        "question": "怎么选尺码？",
        "answer": "详情页有尺码表，按身高体重选择即可。",
        "keywords": ["选尺码", "尺码表", "尺寸"]
    },
    {
        "question": "有色差吗？",
        "answer": "拍摄尽量还原，轻微色差属正常。",
        "keywords": ["色差", "颜色", "拍照"]
    },
    # 5. 支付与优惠
    {
        "question": "可以优惠吗？",
        "answer": "当前已是活动价，不议价。",
        "keywords": ["优惠", "议价", "折扣"]
    },
    {
        "question": "怎么使用优惠券？",
        "answer": "下单时在支付页选择可用优惠券。",
        "keywords": ["优惠券", "使用优惠券", "折扣券"]
    },
    {
        "question": "支持分期吗？",
        "answer": "支持花呗分期。",
        "keywords": ["分期", "花呗", "支付方式"]
    },
    # 6. 拒收 / 少件 / 破损
    {
        "question": "收到破损怎么办？",
        "answer": "签收 24 小时内带快递面单 + 破损图联系客服。",
        "keywords": ["破损", "收到破损", "快递破损"]
    },
    {
        "question": "少发漏发怎么办？",
        "answer": "提供包裹面单、内物照片，客服核实补发。",
        "keywords": ["少发", "漏发", "补发"]
    },
    {
        "question": "可以拒收吗？",
        "answer": "未拆包可直接拒收，原路退款。",
        "keywords": ["拒收", "退货", "退款"]
    },
    # 7. 发票
    {
        "question": "怎么开发票？",
        "answer": "订单页申请开票，电子发票自动发送。",
        "keywords": ["开发票", "发票", "电子发票"]
    },
    {
        "question": "发票抬头能改吗？",
        "answer": "未开可改，已开无法修改。",
        "keywords": ["发票抬头", "修改发票", "发票信息"]
    },
    # 8. 常见无法回答（统一话术）
    {
        "question": "在吗？",
        "answer": "您好，在的，请问有什么可以帮您？",
        "keywords": ["在吗", "你好", "问候"]
    },
    {
        "question": "人工客服",
        "answer": "请输入问题，我帮您优先处理，复杂问题我会转接人工。",
        "keywords": ["人工客服", "转接人工", "人工"]
    }
]

def add_faqs():
    """批量添加FAQ到数据库"""
    print("开始添加FAQ到数据库...")
    
    db = SessionLocal()
    try:
        faq_repo = FAQRepository(db)
        
        for i, faq in enumerate(faq_data, 1):
            print(f"添加第 {i} 条FAQ: {faq['question']}")
            
            # 检查是否已存在
            existing_faq = db.query(FAQ).filter(
                FAQ.question == faq['question']
            ).first()
            
            if existing_faq:
                print(f"  已存在，跳过")
                continue
            
            # 添加新FAQ
            result = faq_repo.create(
                question=faq['question'],
                answer=faq['answer'],
                keywords=faq['keywords']
            )
            print(f"  添加成功: ID={result['id']}")
        
        db.commit()
        print(f"\nFAQ添加完成！共添加 {len(faq_data)} 条FAQ")
        
    except Exception as e:
        print(f"添加FAQ失败: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """主函数"""
    print("批量添加FAQ到数据库")
    print("=" * 50)
    
    add_faqs()

if __name__ == "__main__":
    main()
