import random
import asyncio
from typing import AsyncGenerator
from security.sensitive_filter import sensitive_filter
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StreamGenerator:
    """流式生成器 - 负责mock数据和逐段生成"""
    
    def __init__(self):
        self.mock_responses = [
            "好的，我已收到您的消息。",
            
            "尊敬的客户，您好！感谢您联系我们的客服中心。关于您咨询的问题，我已经详细记录下来，并会尽快为您处理。我们的工作时间是周一至周五上午9点至下午6点，如果您在非工作时间提交了问题，我们会在下一个工作日第一时间联系您。同时，您也可以通过我们的官方网站或APP查看订单状态、物流信息等相关内容。如有任何紧急情况，请拨打我们的24小时服务热线：400-xxx-xxxx。再次感谢您的信任与支持，祝您生活愉快！",
            
            "收到，正在为您查询中...",
            
            "您好！非常感谢您的咨询。关于您提到的退款问题，我来为您详细说明一下我们的退款政策。首先，根据消费者权益保护法和我们的服务协议，您在购买商品后7天内可以申请无理由退款，但需要保证商品完好无损、包装完整、配件齐全。退款流程如下：第一步，登录您的账户，进入我的订单页面；第二步，找到需要退款的订单，点击申请退款按钮；第三步，选择退款原因，并上传相关凭证照片；第四步，提交申请后，我们会在1-3个工作日内审核；第五步，审核通过后，退款金额将在3-7个工作日内原路返回到您的支付账户。需要注意的是，如果是由于商品质量问题导致的退款，我们会承担运费；如果是个人原因导致的退款，运费需要您自行承担。另外，部分特殊商品如定制商品、生鲜食品等不支持无理由退款，具体以商品详情页说明为准。如果您还有其他疑问，欢迎随时咨询我们的在线客服或拨打客服热线。我们承诺为您提供最优质的服务体验！",
            
            "好的，我明白了。",
            
            "亲爱的用户，您好！感谢您选择我们的服务。关于您反馈的问题，我们非常重视，已经安排专人跟进处理。为了更好地为您解决问题，我们需要您提供以下信息：您的订单号、联系方式、具体问题描述以及相关截图或照片。您可以通过以下方式提交：1. 在线客服：登录APP或网站，点击右下角在线客服按钮；2. 客服邮箱：support@example.com；3. 客服热线：400-xxx-xxxx（工作日9:00-18:00）。我们承诺在收到您的信息后24小时内给予回复。同时，为了感谢您的反馈，我们将在问题解决后为您赠送一张优惠券，可在下次购物时使用。再次感谢您的理解与支持，我们会持续改进服务质量，为您提供更好的体验！",
            
            "请稍等，我帮您查一下。",
            
            "您好，关于您咨询的物流问题，我来为您详细解答。首先，您可以通过以下方式查询物流信息：1. 登录我们的APP或网站，进入我的订单，点击对应订单即可查看实时物流状态；2. 关注我们的微信公众号，绑定手机号后可接收物流更新推送；3. 直接联系快递公司，提供您的快递单号进行查询。关于配送时间，一般情况下：一线城市1-2天送达，二三线城市2-3天送达，偏远地区3-5天送达。如遇双十一、春节等高峰期，可能会有所延迟，请您谅解。如果您的包裹显示已签收但您未收到，请先检查是否放在了快递柜、门卫室或邻居家，也可以联系快递员核实。如确认丢失，我们会为您补发或退款。另外，我们支持修改收货地址（包裹未发出前）、预约配送时间、代收货款等增值服务。如有任何问题，欢迎随时联系我们！",
            
            "感谢您的反馈！",
            
            "尊敬的客户，您好！非常感谢您对我们产品的关注和信任。关于您询问的产品详情，我来为您做一个全面的介绍。我们这款产品采用了最新的技术工艺，具有以下核心优势：第一，高品质材料，经过严格的质量检测，确保安全环保无污染；第二，人性化设计，根据人体工程学原理设计，使用更加舒适便捷；第三，智能功能，支持手机APP远程控制，随时随地掌控使用状态；第四，节能环保，相比同类产品节能30%以上，为您节省开支的同时也为环保贡献力量；第五，超长质保，我们提供三年免费保修服务，让您购买无忧。产品规格参数如下：尺寸为xx乘xx乘xx厘米，重量约xx公斤，功率xx瓦，电压220V/50Hz。适用场景包括家庭、办公室、商铺等多种环境。目前我们正在开展促销活动，原价xxx元，现在购买可享受8折优惠，还赠送价值xxx元的大礼包包含配件、清洁用品等。支持分期付款，0利息0手续费。全国包邮，偏远地区除外。如有质量问题，7天无理由退换。如果您想了解更多详情或下单购买，可以访问我们的官方网站或前往线下门店体验。我们的客服团队随时为您服务，期待您的光临！"
        ]
    
    def _split_text(self, text: str) -> list:
        """将文本分割成小段，每段2-3个字符"""
        chunks = []
        i = 0
        while i < len(text):
            chunk_size = random.randint(2, 3)
            chunks.append(text[i:i + chunk_size])
            i += chunk_size
        return chunks
    
    async def generate_stream(self, user_message: str = "") -> AsyncGenerator[str, None]:
        """
        流式生成mock回复
        逐段输出，每段2-3个字符，延迟0.02秒
        """
        # 随机选择一条mock回复
        full_text = random.choice(self.mock_responses)
        
        # 应用内容过滤
        filter_result = sensitive_filter.filter_content(
            text=full_text,
            filter_dimensions=["敏感词", "业务违禁词", "格式校验"]
        )
        
        # 记录过滤日志
        logger.info(
            "内容过滤结果",
            extra={
                "original_text": filter_result["original_text"],
                "filtered_text": filter_result["filtered_text"],
                "has_violation": filter_result["has_violation"],
                "violation_words": filter_result["violation_words"],
                "violation_categories": filter_result["violation_categories"],
                "fallback_response": filter_result["fallback_response"],
                "processing_time": filter_result["processing_time"],
                "filter_enabled": filter_result["filter_enabled"]
            }
        )
        
        # 使用过滤后的文本
        final_text = filter_result["filtered_text"]
        
        # 将文本分割成小段（每段2-3个字符）
        chunks = self._split_text(final_text)
        
        # 逐段输出
        for i, chunk in enumerate(chunks):
            # 模拟AI思考延迟（0.02秒）
            delay = 0.02
            await asyncio.sleep(delay)
            
            # 输出当前片段
            yield chunk
        
        # 最后发送结束标记
        yield "[DONE]"

# 全局生成器实例
stream_generator = StreamGenerator()
