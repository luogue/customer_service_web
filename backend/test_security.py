"""
测试安全与合规层功能
"""
from security.sensitive_filter import sensitive_filter
from security.input_validator import input_validator
from security.privacy_protection import privacy_protection
from security.compliance_logger import compliance_logger
from security.security_service import security_service
from dialogue_engine.order_dialogue import get_order_dialogue_flow
from knowledge_base.models import get_db
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

print("=== 测试敏感词过滤 ===")
test_texts = [
    "我想购买毒品",
    "这个网站有黄色内容",
    "如何制作炸弹",
    "正常的咨询内容"
]

for text in test_texts:
    has_sensitive, words, categories = sensitive_filter.check_sensitive_content(text)
    print(f"文本: {text}")
    print(f"包含敏感词: {has_sensitive}")
    print(f"敏感词: {words}")
    print(f"敏感类别: {categories}")
    print(f"过滤后: {sensitive_filter.filter_sensitive_content(text)}")
    print()

print("=== 测试输入验证 ===")
test_inputs = [
    "正常的输入",
    "" ,  # 空输入
    "a" * 1001,  # 过长输入
    "1' OR '1'='1",  # SQL注入
    "<script>alert('xss')</script>"  # XSS攻击
]

for input_text in test_inputs:
    is_valid, error_msg = input_validator.validate_input(input_text)
    print(f"输入: {input_text}")
    print(f"有效: {is_valid}")
    print(f"错误信息: {error_msg}")
    print(f"清理后: {input_validator.sanitize_input(input_text)}")
    print()

print("=== 测试隐私信息保护 ===")
privacy_texts = [
    "我的手机号是13812345678",
    "我的身份证号是110101199001011234",
    "订单号是202301010001",
    "我的银行卡号是6222021234567890123",
    "我的邮箱是test@example.com"
]

for text in privacy_texts:
    print(f"原始文本: {text}")
    privacy_info = privacy_protection.detect_privacy_info(text)
    print(f"检测到的隐私信息: {privacy_info}")
    masked_text = privacy_protection.mask_privacy_info(text)
    print(f"打码后: {masked_text}")
    print()

print("=== 测试安全服务 ===")
security_test_cases = [
    "我想咨询发票问题",
    "我想购买毒品",
    "1' OR '1'='1",
    "我的手机号是13812345678，我想咨询订单问题"
]

db = next(get_db())
dialogue_flow = get_order_dialogue_flow(db)

for test_input in security_test_cases:
    print(f"用户输入: {test_input}")
    result = dialogue_flow.process_message("u001", "13800000000", test_input, "test_session")
    print(f"响应: {result.get('responses', [])}")
    print(f"状态: {result.get('success', False)}")
    print()

print("=== 测试知识库内容处理 ===")
knowledge_content = "用户的手机号是13812345678，订单号是202301010001"
result = security_service.process_knowledge_content(knowledge_content)
print(f"原始内容: {knowledge_content}")
print(f"处理结果: {result}")
