"""
测试日志收集功能
"""
import time
from datetime import datetime, timedelta
from logs.log_collector import get_log_collector
from logs.log_decorator import record_log

print("=== 测试日志收集功能 ===")

# 获取日志收集器
log_collector = get_log_collector()

# 测试记录日志
print("\n1. 测试记录日志...")
record_log(
    user_id="u001",
    operation="user_query",
    status="success",
    duration=123.45,
    content="帮我查一下订单"
)
print("日志记录成功！")

# 测试记录错误日志
record_log(
    user_id="u001",
    operation="intent_recognition",
    status="failure",
    duration=50.0,
    content="测试内容",
    error="意图识别失败"
)
print("错误日志记录成功！")

# 测试查询日志
print("\n2. 测试查询日志...")
logs = log_collector.query(limit=10)
print(f"查询到 {len(logs)} 条日志:")
for log in logs:
    print(f"  时间: {log.timestamp}, 用户: {log.user_id}, 操作: {log.operation}, 状态: {log.status}, 耗时: {log.duration:.2f}ms")

# 测试按条件查询
print("\n3. 测试按条件查询...")
# 按用户ID查询
user_logs = log_collector.query(user_id="u001", limit=5)
print(f"用户 u001 的日志: {len(user_logs)} 条")

# 按状态查询
failure_logs = log_collector.query(status="failure", limit=5)
print(f"失败的日志: {len(failure_logs)} 条")

# 按时间查询
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)
time_logs = log_collector.query(start_time=start_time, end_time=end_time, limit=5)
print(f"最近1小时的日志: {len(time_logs)} 条")

# 测试统计信息
print("\n4. 测试统计信息...")
stats = log_collector.get_stats()
print(f"总日志数: {stats['total']}")
print(f"成功: {stats['success']}, 失败: {stats['failure']}")
print("按操作统计:")
for op, op_stats in stats['operation_stats'].items():
    print(f"  {op}: 总数={op_stats['total']}, 成功={op_stats['success']}, 失败={op_stats['failure']}, 平均耗时={op_stats['avg_duration']:.2f}ms")

print("\n日志收集功能测试完成！")
