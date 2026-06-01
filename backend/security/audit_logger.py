"""
审计日志记录器
用于记录管理员关键操作的审计日志
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import threading
from .privacy_protection import privacy_protection


class AuditLogRecord:
    """审计日志记录"""
    
    def __init__(self, admin_id: str, operation: str, status: str, 
                 resource: str, action: str, 
                 content: str = None, error: str = None,
                 metadata: Dict[str, Any] = None):
        self.timestamp = datetime.now()
        self.admin_id = admin_id
        self.operation = operation
        self.status = status  # success/failure
        self.resource = resource  # 操作的资源
        self.action = action  # 具体动作
        self.content = content
        self.error = error
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "admin_id": self.admin_id,
            "operation": self.operation,
            "status": self.status,
            "resource": self.resource,
            "action": self.action,
            "content": self.content,
            "error": self.error,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditLogRecord":
        record = cls(
            admin_id=data["admin_id"],
            operation=data["operation"],
            status=data["status"],
            resource=data["resource"],
            action=data["action"],
            content=data.get("content"),
            error=data.get("error"),
            metadata=data.get("metadata", {})
        )
        record.timestamp = datetime.fromisoformat(data["timestamp"])
        return record


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, log_file: str = "logs/audit.log"):
        self.log_file = log_file
        self.lock = threading.Lock()
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def record(self, admin_id: str, operation: str, status: str, 
               resource: str, action: str, 
               content: str = None, error: str = None,
               metadata: Dict[str, Any] = None) -> None:
        """
        记录审计日志
        
        Args:
            admin_id: 管理员ID
            operation: 操作名称
            status: 状态（success/failure）
            resource: 操作的资源
            action: 具体动作
            content: 操作内容
            error: 错误信息
            metadata: 额外元数据
        """
        # 对内容进行隐私信息打码
        if content:
            content = privacy_protection.mask_privacy_info(content)
        
        # 对错误信息进行隐私信息打码
        if error:
            error = privacy_protection.mask_privacy_info(error)
        
        # 创建审计日志记录
        audit_record = AuditLogRecord(
            admin_id=admin_id,
            operation=operation,
            status=status,
            resource=resource,
            action=action,
            content=content,
            error=error,
            metadata=metadata
        )
        
        # 写入日志文件
        with self.lock:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_record.to_dict(), ensure_ascii=False) + "\n")
    
    def query(self, start_time: Optional[datetime] = None,
             end_time: Optional[datetime] = None,
             admin_id: Optional[str] = None,
             status: Optional[str] = None,
             operation: Optional[str] = None,
             resource: Optional[str] = None,
             limit: int = 100) -> list:
        """
        查询审计日志
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            admin_id: 管理员ID
            status: 状态（success/failure）
            operation: 操作名称
            resource: 操作的资源
            limit: 返回记录数量限制
            
        Returns:
            list: 审计日志记录列表
        """
        results = []
        
        if not os.path.exists(self.log_file):
            return results
        
        with self.lock:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        audit_record = AuditLogRecord.from_dict(data)
                        
                        # 时间过滤
                        if start_time and audit_record.timestamp < start_time:
                            continue
                        if end_time and audit_record.timestamp > end_time:
                            continue
                        
                        # 管理员ID过滤
                        if admin_id and audit_record.admin_id != admin_id:
                            continue
                        
                        # 状态过滤
                        if status and audit_record.status != status:
                            continue
                        
                        # 操作名称过滤
                        if operation and audit_record.operation != operation:
                            continue
                        
                        # 资源过滤
                        if resource and audit_record.resource != resource:
                            continue
                        
                        results.append(audit_record)
                    except Exception:
                        continue
        
        # 按时间倒序排列
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 限制返回数量
        return results


# 全局审计日志记录器实例
_audit_logger = None

def get_audit_logger() -> AuditLogger:
    """获取审计日志记录器实例（单例模式）"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger

def record_audit(admin_id: str, operation: str, status: str, 
                 resource: str, action: str, 
                 content: str = None, error: str = None,
                 metadata: Dict[str, Any] = None) -> None:
    """
    记录审计日志（便捷函数）
    
    Args:
        admin_id: 管理员ID
        operation: 操作名称
        status: 状态（success/failure）
        resource: 操作的资源
        action: 具体动作
        content: 操作内容
        error: 错误信息
        metadata: 额外元数据
    """
    audit_logger = get_audit_logger()
    audit_logger.record(admin_id, operation, status, resource, action, content, error, metadata)
