from config import settings
from knowledge_base.database import engine, Base
from api_gateway.gateway import app


# 初始化备份系统
try:
    from backup.backup_manager import init_backup_system
    init_backup_system()
except ImportError as e:
    print(f"[警告] 备份系统初始化失败: {e}")

# 初始化监控系统
try:
    from monitoring.prometheus_monitor import init_monitoring
    init_monitoring()
except ImportError as e:
    print(f"[警告] 监控系统初始化失败: {e}")

# 初始化日志系统
try:
    from logging.loki_logger import get_logger
    logger = get_logger()
    logger.info("应用启动", endpoint="main", status="starting")
except ImportError as e:
    print(f"[警告] 日志系统初始化失败: {e}")

# 创建数据库表
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
