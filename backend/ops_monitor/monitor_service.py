"""
运维监控服务
用于记录接口调用次数、成功失败次数、响应时间等信息
"""
import time
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from knowledge_base.models import MonitorRecord
import logging

logger = logging.getLogger(__name__)

class MonitorService:
    """监控服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_api_call(self, endpoint: str, method: str, status: str, 
                       response_time: float, error_message: Optional[str] = None, 
                       user_id: Optional[str] = None) -> MonitorRecord:
        """
        记录API调用
        
        Args:
            endpoint: 接口端点
            method: 请求方法
            status: 状态：success/failure
            response_time: 响应时间（毫秒）
            error_message: 错误信息（如果有）
            user_id: 用户ID（如果有）
            
        Returns:
            MonitorRecord: 监控记录
        """
        try:
            # 创建监控记录
            record = MonitorRecord(
                endpoint=endpoint,
                method=method,
                status=status,
                response_time=response_time,
                error_message=error_message,
                user_id=user_id
            )
            
            # 保存到数据库
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            
            return record
        except Exception as e:
            logger.error(f"记录API调用失败: {e}")
            # 确保数据库会话正常
            self.db.rollback()
            return None
    
    def get_api_stats(self, start_time: Optional[datetime] = None, 
                     end_time: Optional[datetime] = None, 
                     endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        获取API统计信息
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            endpoint: 接口端点
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            query = self.db.query(MonitorRecord)
            
            # 时间过滤
            if start_time:
                query = query.filter(MonitorRecord.timestamp >= start_time)
            if end_time:
                query = query.filter(MonitorRecord.timestamp <= end_time)
            
            # 端点过滤
            if endpoint:
                query = query.filter(MonitorRecord.endpoint == endpoint)
            
            # 获取所有记录
            records = query.all()
            
            # 计算统计信息
            total_calls = len(records)
            success_calls = len([r for r in records if r.status == "success"])
            failure_calls = total_calls - success_calls
            
            # 计算平均响应时间
            response_times = [r.response_time for r in records if r.status == "success"]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # 按端点分组统计
            endpoint_stats = {}
            for record in records:
                if record.endpoint not in endpoint_stats:
                    endpoint_stats[record.endpoint] = {
                        "total": 0,
                        "success": 0,
                        "failure": 0,
                        "response_times": []
                    }
                
                endpoint_stats[record.endpoint]["total"] += 1
                if record.status == "success":
                    endpoint_stats[record.endpoint]["success"] += 1
                    endpoint_stats[record.endpoint]["response_times"].append(record.response_time)
                else:
                    endpoint_stats[record.endpoint]["failure"] += 1
            
            # 计算每个端点的平均响应时间
            for ep, stats in endpoint_stats.items():
                if stats["response_times"]:
                    stats["avg_response_time"] = sum(stats["response_times"]) / len(stats["response_times"])
                else:
                    stats["avg_response_time"] = 0
                del stats["response_times"]
            
            return {
                "total_calls": total_calls,
                "success_calls": success_calls,
                "failure_calls": failure_calls,
                "avg_response_time": avg_response_time,
                "endpoint_stats": endpoint_stats
            }
        except Exception as e:
            logger.error(f"获取API统计信息失败: {e}")
            return {
                "total_calls": 0,
                "success_calls": 0,
                "failure_calls": 0,
                "avg_response_time": 0,
                "endpoint_stats": {}
            }

# 全局监控服务实例
_monitor_service_instance = None

def get_monitor_service(db: Session = None) -> MonitorService:
    """获取监控服务实例（单例模式）"""
    global _monitor_service_instance
    if _monitor_service_instance is None:
        from knowledge_base.models import SessionLocal
        db = db or SessionLocal()
        _monitor_service_instance = MonitorService(db)
    elif db:
        _monitor_service_instance.db = db
    return _monitor_service_instance
