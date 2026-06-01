"""
会话管理模块
"""
from datetime import datetime
from typing import List, Dict, Any
import json
import os

# 会话存储路径
SESSION_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "sessions")

# 确保存储目录存在
if not os.path.exists(SESSION_STORAGE_PATH):
    os.makedirs(SESSION_STORAGE_PATH)


class SessionManager:
    """
    会话管理器
    """
    
    @staticmethod
    def get_session_file(user_id: str, session_id: str) -> str:
        """
        获取会话文件路径
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            会话文件路径
        """
        user_dir = os.path.join(SESSION_STORAGE_PATH, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return os.path.join(user_dir, f"{session_id}.json")
    
    @staticmethod
    def save_context(user_id: str, session_id: str, context: List[Dict[str, Any]]) -> bool:
        """
        保存对话上下文
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            context: 对话上下文
            
        Returns:
            是否保存成功
        """
        try:
            session_file = SessionManager.get_session_file(user_id, session_id)
            current_time = datetime.now()
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'user_id': user_id,
                    'session_id': session_id,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': current_time.isoformat(),
                    'last_active_time': current_time.timestamp(),
                    'context': context
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存对话上下文失败: {e}")
            return False
    
    @staticmethod
    def get_context(user_id: str, session_id: str) -> List[Dict[str, Any]]:
        """
        获取对话上下文
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            对话上下文
        """
        try:
            session_file = SessionManager.get_session_file(user_id, session_id)
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('context', [])
            return []
        except Exception as e:
            print(f"获取对话上下文失败: {e}")
            return []
    
    @staticmethod
    def update_context(user_id: str, session_id: str, user_message: str, ai_message: str) -> bool:
        """
        更新对话上下文
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            user_message: 用户消息
            ai_message: AI回复
            
        Returns:
            是否更新成功
        """
        try:
            # 获取现有上下文
            context = SessionManager.get_context(user_id, session_id)
            
            # 添加新的对话轮次
            context.append({
                'user_message': user_message,
                'ai_message': ai_message,
                'timestamp': datetime.now().isoformat()
            })
            
            # 只保留最近5轮对话
            if len(context) > 5:
                context = context[-5:]
            
            # 保存更新后的上下文
            return SessionManager.save_context(user_id, session_id, context)
        except Exception as e:
            print(f"更新对话上下文失败: {e}")
            return False
    
    @staticmethod
    def get_recent_context(user_id: str, session_id: str) -> List[Dict[str, Any]]:
        """
        获取最近5轮对话上下文
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            最近5轮对话上下文
        """
        context = SessionManager.get_context(user_id, session_id)
        # 只返回最近5轮对话
        return context[-5:] if len(context) > 5 else context
    
    @staticmethod
    def check_session_expiry(user_id: str, session_id: str, expire_seconds: int = 600) -> bool:
        """
        检查会话是否过期
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            expire_seconds: 会话有效期（秒），默认10分钟
            
        Returns:
            True: 会话未过期，False: 会话已过期
        """
        try:
            session_file = SessionManager.get_session_file(user_id, session_id)
            if not os.path.exists(session_file):
                return False
            
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                last_active_time = data.get('last_active_time')
                if not last_active_time:
                    return False
                
                current_time = datetime.now().timestamp()
                return (current_time - last_active_time) <= expire_seconds
        except Exception as e:
            print(f"检查会话过期失败: {e}")
            return False
    
    @staticmethod
    def update_last_active_time(user_id: str, session_id: str) -> bool:
        """
        更新会话最后活跃时间
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            是否更新成功
        """
        try:
            session_file = SessionManager.get_session_file(user_id, session_id)
            if not os.path.exists(session_file):
                return False
            
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['last_active_time'] = datetime.now().timestamp()
            data['updated_at'] = datetime.now().isoformat()
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"更新最后活跃时间失败: {e}")
            return False
    
    @staticmethod
    def list_sessions(user_id: str) -> List[Dict[str, Any]]:
        """
        列出用户的所有会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            会话列表
        """
        try:
            user_dir = os.path.join(SESSION_STORAGE_PATH, user_id)
            if not os.path.exists(user_dir):
                return []
            
            sessions = []
            for filename in os.listdir(user_dir):
                if filename.endswith('.json'):
                    session_file = os.path.join(user_dir, filename)
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        sessions.append({
                            'session_id': data.get('session_id'),
                            'created_at': data.get('created_at'),
                            'updated_at': data.get('updated_at'),
                            'last_active_time': data.get('last_active_time'),
                            'message_count': len(data.get('context', []))
                        })
            
            # 按创建时间排序，最新的在前
            sessions.sort(key=lambda x: x['created_at'], reverse=True)
            return sessions
        except Exception as e:
            print(f"列出会话失败: {e}")
            return []