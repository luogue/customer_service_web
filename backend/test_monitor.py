"""
测试运维监控功能
"""
from knowledge_base.models import get_db, MonitorRecord
from ops_monitor.monitor_service import get_monitor_service
from datetime import datetime, timedelta
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

print("=== 测试监控功能 ===")

# 获取数据库会话
db = next(get_db())

# 获取监控服务
monitor_service = get_monitor_service(db)

# 测试记录API调用
print("测试记录API调用...")
record = monitor_service.record_api_call(
    endpoint="/api/chat/message",
    method="POST",
    status="success",
    response_time=123.45,
    user_id="u001"
)
print(f"创建监控记录: {record.id}")

# 测试记录失败的API调用
record_failure = monitor_service.record_api_call(
    endpoint="/api/chat/message",
    method="POST",
    status="failure",
    response_time=56.78,
    error_message="测试错误",
    user_id="u001"
)
print(f"创建失败监控记录: {record_failure.id}")

# 测试获取API统计信息
print("\n测试获取API统计信息...")
# 设置时间范围（最近24小时）
end_time = datetime.utcnow()
start_time = end_time - timedelta(hours=24)

stats = monitor_service.get_api_stats(
    start_time=start_time,
    end_time=end_time
)
print(f"总调用次数: {stats['total_calls']}")
print(f"成功调用次数: {stats['success_calls']}")
print(f"失败调用次数: {stats['failure_calls']}")
print(f"平均响应时间: {stats['avg_response_time']:.2f}ms")
print("按端点统计:")
for endpoint, endpoint_stat in stats['endpoint_stats'].items():
    print(f"  {endpoint}:")
    print(f"    总调用: {endpoint_stat['total']}")
    print(f"    成功: {endpoint_stat['success']}")
    print(f"    失败: {endpoint_stat['failure']}")
    print(f"    平均响应时间: {endpoint_stat['avg_response_time']:.2f}ms")

# 测试直接查询监控表
print("\n测试直接查询监控表...")
records = db.query(MonitorRecord).order_by(MonitorRecord.timestamp.desc()).limit(10).all()
print(f"最近10条监控记录:")
for record in records:
    print(f"  ID: {record.id}, 端点: {record.endpoint}, 方法: {record.method}, 状态: {record.status}, 响应时间: {record.response_time:.2f}ms, 时间: {record.timestamp}")

print("\n监控功能测试完成！")
