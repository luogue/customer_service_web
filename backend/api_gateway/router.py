from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import asyncio
import secrets
from sqlalchemy.orm import Session

from llm_adapter import ai_service
from ops_monitor import logger
from knowledge_base.models import get_db, User
from .knowledge_router import router as knowledge_router
from .chat_router import router as chat_router
from .prompt_router import router as prompt_router
from security.auth import create_access_token, get_current_user, get_current_admin
from config.env_config import get_env_config

# 尝试导入监控器
try:
    from monitoring.prometheus_monitor import prometheus_monitor
except ImportError:
    prometheus_monitor = None

# 从环境配置读取管理员信息
config = get_env_config()
ADMIN_USERNAME = config.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = config.get("ADMIN_PASSWORD", "123456")
ADMIN_ROLE = config.get("ADMIN_ROLE", "admin")
ADMIN_NAME = config.get("ADMIN_NAME", "管理员")
DEFAULT_USER_PASSWORD = config.get("DEFAULT_USER_PASSWORD", "123456")

router = APIRouter()

# 数据模型
class Message(BaseModel):
    id: Optional[int] = None
    text: str
    type: str
    time: Optional[str] = None

class ChatRequest(BaseModel):
    text: str
    type: str = "user"

class LoginRequest(BaseModel):
    phone: str = None
    username: str = None
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None
    token: Optional[str] = None

# 内存存储
messages: List[Message] = []
active_connections: List[WebSocket] = []

def get_current_time():
    return datetime.now().strftime("%H:%M")

async def broadcast_message(message: Message):
    """广播消息给所有连接"""
    for connection in active_connections:
        try:
            await connection.send_json(message.model_dump())
        except Exception:
            pass

# 内存存储管理员账号
ADMIN_DB = {
    ADMIN_USERNAME: {"password": ADMIN_PASSWORD, "role": ADMIN_ROLE, "name": ADMIN_NAME, "id": 0}
}

# 登录接口
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 使用监控装饰器
    if prometheus_monitor:
        @prometheus_monitor.api_monitor('login')
        async def monitored_login():
            logger.info(f"Login attempt: {request.phone or request.username}")
            
            # 检查是否是管理员账号登录
            if request.username and request.username in ADMIN_DB:
                admin = ADMIN_DB[request.username]
                if admin["password"] != request.password:
                    return LoginResponse(success=False, message="密码错误")
                
                # 使用JWT token
                token = create_access_token(
                    data={"user_id": admin["id"], "username": request.username, "role": admin["role"]}
                )
                return LoginResponse(
                    success=True,
                    message="登录成功",
                    user={
                        "id": 0,
                        "username": request.username,
                        "phone": "13800000001",
                        "role": admin["role"],
                        "name": admin["name"]
                    },
                    token=token
                )
            
            # 从数据库查询用户（手机号登录）
            if not request.phone:
                return LoginResponse(success=False, message="请输入手机号或用户名")
            
            user = db.query(User).filter(User.phone == request.phone).first()
            
            if not user:
                return LoginResponse(success=False, message="手机号不存在")
            
            if request.password != DEFAULT_USER_PASSWORD:
                return LoginResponse(success=False, message="密码错误")
            
            # 使用JWT token
            token = create_access_token(
                data={"user_id": user.id, "phone": user.phone, "role": user.role}
            )
            
            return LoginResponse(
                success=True,
                message="登录成功",
                user={
                    "id": user.id,
                    "phone": user.phone,
                    "role": user.role,
                    "name": user.name
                },
                token=token
            )
        return await monitored_login()
    else:
        # 无监控版本
        logger.info(f"Login attempt: {request.phone or request.username}")
        
        # 检查是否是管理员账号登录
        if request.username and request.username in ADMIN_DB:
            admin = ADMIN_DB[request.username]
            if admin["password"] != request.password:
                return LoginResponse(success=False, message="密码错误")
            
            # 使用JWT token
            token = create_access_token(
                data={"user_id": admin["id"], "username": request.username, "role": admin["role"]}
            )
            return LoginResponse(
                success=True,
                message="登录成功",
                user={
                    "id": 0,
                    "username": request.username,
                    "phone": "13800000001",
                    "role": admin["role"],
                    "name": admin["name"]
                },
                token=token
            )
        
        # 从数据库查询用户（手机号登录）
        if not request.phone:
            return LoginResponse(success=False, message="请输入手机号或用户名")
        
        user = db.query(User).filter(User.phone == request.phone).first()
        
        if not user:
            return LoginResponse(success=False, message="手机号不存在")
        
        if request.password != DEFAULT_USER_PASSWORD:
            return LoginResponse(success=False, message="密码错误")
        
        # 使用JWT token
        token = create_access_token(
            data={"user_id": user.id, "phone": user.phone, "role": user.role}
        )
        
        return LoginResponse(
            success=True,
            message="登录成功",
            user={
                "id": user.id,
                "phone": user.phone,
                "role": user.role,
                "name": user.name
            },
            token=token
        )

# 消息接口
@router.get("/messages", response_model=List[Message])
async def get_messages():
    return messages

@router.post("/messages", response_model=Message)
async def send_message(request: ChatRequest):
    # 使用监控装饰器
    if prometheus_monitor:
        @prometheus_monitor.api_monitor('send_message')
        async def monitored_send_message():
            user_message = Message(
                id=len(messages) + 1,
                text=request.text,
                type=request.type,
                time=get_current_time()
            )
            messages.append(user_message)
            await broadcast_message(user_message)
            
            # 异步处理AI回复
            asyncio.create_task(process_ai_response(request.text))
            
            return user_message
        return await monitored_send_message()
    else:
        # 无监控版本
        user_message = Message(
            id=len(messages) + 1,
            text=request.text,
            type=request.type,
            time=get_current_time()
        )
        messages.append(user_message)
        await broadcast_message(user_message)
        
        # 异步处理AI回复
        asyncio.create_task(process_ai_response(request.text))
        
        return user_message

async def process_ai_response(user_message: str):
    """处理AI回复"""
    await asyncio.sleep(1)
    
    try:
        ai_response_text = await ai_service.generate_response(user_message)
    except Exception as e:
        logger.error(f"AI response error: {e}")
        ai_response_text = "抱歉，我暂时无法回答您的问题，请稍后再试。"
    
    ai_message = Message(
        id=len(messages) + 1,
        text=ai_response_text,
        type="ai",
        time=get_current_time()
    )
    messages.append(ai_message)
    await broadcast_message(ai_message)

# WebSocket接口
@router.websocket("/ws/messages")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket connected. Total: {len(active_connections)}")
    
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "send_message":
                await send_message(ChatRequest(text=data.get("text")))
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

# 健康检查
@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# 获取当前用户信息（需要登录）
@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "phone": current_user.phone,
            "role": current_user.role,
            "name": current_user.name
        }
    }


# 管理员接口示例（需要管理员权限）
@router.get("/admin/users")
async def get_all_users_admin(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取所有用户列表（仅管理员）"""
    users = db.query(User).all()
    return {
        "success": True,
        "users": [
            {
                "id": u.id,
                "phone": u.phone,
                "role": u.role,
                "name": u.name
            }
            for u in users
        ]
    }


# 包含知识底座路由
router.include_router(knowledge_router, prefix="/api/knowledge")
# 包含聊天路由
router.include_router(chat_router, prefix="/api/chat")
# 包含Prompt模板路由
router.include_router(prompt_router, prefix="/api")
