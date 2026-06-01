"""
会话清理器
定期清理过期的会话数据
"""
import os
import json
from datetime import datetime
from dialogue_engine.session_manager import SESSION_STORAGE_PATH


def clean_expired_sessions(expire_seconds: int = 600) -> int:
    """
    清理过期的会话数据
    
    Args:
        expire_seconds: 会话有效期（秒），默认10分钟
        
    Returns:
        清理的会话数量
    """
    cleaned_count = 0
    
    try:
        # 遍历所有用户目录
        if not os.path.exists(SESSION_STORAGE_PATH):
            return 0
        
        for user_id in os.listdir(SESSION_STORAGE_PATH):
            user_dir = os.path.join(SESSION_STORAGE_PATH, user_id)
            if not os.path.isdir(user_dir):
                continue
            
            # 遍历用户的所有会话文件
            for filename in os.listdir(user_dir):
                if not filename.endswith('.json'):
                    continue
                
                session_file = os.path.join(user_dir, filename)
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    last_active_time = data.get('last_active_time')
                    if not last_active_time:
                        # 没有最后活跃时间，视为过期
                        os.remove(session_file)
                        cleaned_count += 1
                        continue
                    
                    # 检查是否过期
                    current_time = datetime.now().timestamp()
                    if (current_time - last_active_time) > expire_seconds:
                        os.remove(session_file)
                        cleaned_count += 1
                        
                except Exception as e:
                    print(f"清理会话文件 {session_file} 失败: {e}")
                    # 清理失败的文件也删除，避免损坏的数据
                    try:
                        os.remove(session_file)
                        cleaned_count += 1
                    except:
                        pass
    except Exception as e:
        print(f"清理过期会话失败: {e}")
    
    return cleaned_count


if __name__ == "__main__":
    # 清理过期10分钟的会话
    cleaned = clean_expired_sessions()
    print(f"清理了 {cleaned} 个过期会话")