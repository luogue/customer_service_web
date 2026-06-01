"""
测试配置中心功能
"""
import asyncio
import aiohttp
from config_center.config_manager import get_config_manager
from api_gateway.rate_limiter import RateLimiter
from api_gateway.circuit_breaker import CircuitBreaker

print("=== 测试配置中心功能 ===")

# 测试配置管理器
print("\n1. 测试配置管理器...")
config_manager = get_config_manager()

# 获取所有配置
print("当前配置:")
config = config_manager.get_all()
print(config)

# 获取特定配置
print("\n获取限流配置:")
max_requests = config_manager.get("rate_limit.max_requests")
time_window = config_manager.get("rate_limit.time_window")
print(f"max_requests: {max_requests}, time_window: {time_window}")

# 获取熔断配置
print("\n获取熔断配置:")
failure_threshold = config_manager.get("circuit_breaker.failure_threshold")
recovery_time = config_manager.get("circuit_breaker.recovery_time")
timeout = config_manager.get("circuit_breaker.timeout")
print(f"failure_threshold: {failure_threshold}, recovery_time: {recovery_time}, timeout: {timeout}")

# 修改配置
print("\n2. 测试修改配置...")
# 修改限流配置
success = config_manager.set("rate_limit.max_requests", 50)
print(f"修改rate_limit.max_requests为50: {'成功' if success else '失败'}")

# 修改熔断配置
success = config_manager.set("circuit_breaker.failure_threshold", 3)
print(f"修改circuit_breaker.failure_threshold为3: {'成功' if success else '失败'}")

# 重新加载配置
print("\n3. 测试重新加载配置...")
config_manager.reload()

# 验证配置是否更新
print("更新后的配置:")
max_requests = config_manager.get("rate_limit.max_requests")
failure_threshold = config_manager.get("circuit_breaker.failure_threshold")
print(f"max_requests: {max_requests}, failure_threshold: {failure_threshold}")

# 测试限流模块加载配置
print("\n4. 测试限流模块加载配置...")
rate_limiter = RateLimiter()
print(f"限流模块配置 - max_requests: {rate_limiter.max_requests}, time_window: {rate_limiter.time_window}")

# 测试熔断模块加载配置
print("\n5. 测试熔断模块加载配置...")
circuit_breaker = CircuitBreaker()
print(f"熔断模块配置 - failure_threshold: {circuit_breaker.failure_threshold}, recovery_time: {circuit_breaker.recovery_time}, timeout: {circuit_breaker.timeout}")

# 测试API接口
print("\n6. 测试配置中心API接口...")
async def test_api():
    async with aiohttp.ClientSession() as session:
        # 测试获取所有配置
        async with session.get("http://localhost:8003/api/config/") as response:
            print(f"获取所有配置: {response.status}")
            data = await response.json()
            print(f"响应: {data}")
        
        # 测试获取特定配置
        async with session.get("http://localhost:8003/api/config/rate_limit") as response:
            print(f"获取rate_limit配置: {response.status}")
            data = await response.json()
            print(f"响应: {data}")
        
        # 测试更新配置
        async with session.put("http://localhost:8003/api/config/rate_limit.max_requests", json=60) as response:
            print(f"更新rate_limit.max_requests为60: {response.status}")
            data = await response.json()
            print(f"响应: {data}")
        
        # 测试重新加载配置
        async with session.post("http://localhost:8003/api/config/reload") as response:
            print(f"重新加载配置: {response.status}")
            data = await response.json()
            print(f"响应: {data}")

# 运行API测试
asyncio.run(test_api())

print("\n配置中心功能测试完成！")
