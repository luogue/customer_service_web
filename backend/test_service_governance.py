"""
测试服务治理功能
"""
import asyncio
import aiohttp
import time
from api_gateway.rate_limiter import RateLimiter
from api_gateway.circuit_breaker import CircuitBreaker

print("=== 测试服务治理功能 ===")

# 测试限流
print("\n1. 测试限流功能...")
rate_limiter = RateLimiter(max_requests=5, time_window=10)  # 10秒内最多5次请求

# 模拟请求
for i in range(10):
    allowed = rate_limiter.check_rate_limit("127.0.0.1", "u001")
    print(f"请求 {i+1}: {'允许' if allowed else '拒绝'}")
    time.sleep(0.5)  # 间隔0.5秒

# 测试熔断
print("\n2. 测试熔断功能...")
circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_time=5)

# 模拟连续失败
print("模拟连续失败...")
def failing_func():
    raise Exception("模拟失败")

def success_func():
    return "成功"

for i in range(5):
    try:
        result = circuit_breaker.execute("test_module", failing_func)
        print(f"执行 {i+1}: 成功")
    except Exception as e:
        state = circuit_breaker.get_module_state("test_module")
        print(f"执行 {i+1}: 失败, 状态: {state['state'].value}, 失败次数: {state['failure_count']}")

# 测试熔断后是否拒绝请求
print("\n测试熔断后是否拒绝请求...")
try:
    result = circuit_breaker.execute("test_module", success_func)
    print("执行成功")
except Exception as e:
    print(f"执行失败: {e}")

# 等待恢复
print("\n等待5秒后测试恢复...")
time.sleep(5)

try:
    result = circuit_breaker.execute("test_module", success_func)
    state = circuit_breaker.get_module_state("test_module")
    print(f"执行成功: {result}, 状态: {state['state'].value}")
except Exception as e:
    print(f"执行失败: {e}")

# 测试网关
print("\n3. 测试网关功能...")
async def test_gateway():
    async with aiohttp.ClientSession() as session:
        # 测试健康检查
        async with session.get("http://localhost:8003/health") as response:
            print(f"健康检查: {response.status}")
            data = await response.json()
            print(f"响应: {data}")

# 运行测试
asyncio.run(test_gateway())

print("\n服务治理功能测试完成！")
