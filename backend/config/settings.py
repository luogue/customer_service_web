import os
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    # 使用绝对路径确保数据库文件一致性
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/knowledge_base/knowledge_base.db")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-2024")
    
    # LLM配置
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "glm-4")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # 应用配置
    APP_NAME = os.getenv("APP_NAME", "客服聊天系统 API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()
