"""
AI指标统计模块
"""
import uuid
import time
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from .models import Base, engine, get_db


class Metrics(Base):
    """AI指标统计表"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(String(100), unique=True, nullable=False, index=True)
    user_question = Column(Text, nullable=False)
    ai_intent = Column(String(100))
    is_correct = Column(Boolean, default=False)  # 意图识别是否正确
    is_completed = Column(Boolean, default=False)  # 业务流程是否完成
    is_context_used = Column(Boolean, default=False)  # 是否使用上下文
    is_transferred = Column(Boolean, default=False)  # 是否转人工
    is_correct_answer = Column(Boolean, default=False)  # 答案是否正确（人工标注）
    is_hallucination = Column(Boolean, default=False)  # 是否存在幻觉（人工标注）
    ai_response = Column(Text)  # AI的回答内容
    expected_answer = Column(Text)  # 期望的正确答案（用于对比）
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime)
    response_time = Column(Integer)  # 响应时间（毫秒）


def create_metrics_table():
    """创建指标统计表"""
    Metrics.__table__.create(bind=engine, checkfirst=True)
    print("指标统计表创建完成")


def generate_request_id():
    """生成唯一的请求ID"""
    return str(uuid.uuid4())


def record_metrics(request_id, user_question, ai_intent, is_correct, is_completed, 
                  is_context_used, is_transferred, start_time, end_time,
                  ai_response=None, expected_answer=None, is_correct_answer=None, is_hallucination=None):
    """记录指标数据"""
    db = next(get_db())
    try:
        # 计算响应时间（毫秒）
        response_time = int((end_time - start_time).total_seconds() * 1000)
        
        # 创建指标记录
        metrics = Metrics(
            request_id=request_id,
            user_question=user_question,
            ai_intent=ai_intent,
            is_correct=is_correct,
            is_completed=is_completed,
            is_context_used=is_context_used,
            is_transferred=is_transferred,
            ai_response=ai_response,
            expected_answer=expected_answer,
            is_correct_answer=is_correct_answer,
            is_hallucination=is_hallucination,
            start_time=start_time,
            end_time=end_time,
            response_time=response_time
        )
        
        db.add(metrics)
        db.commit()
        return True
    except Exception as e:
        print(f"记录指标失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def calculate_metrics():
    """计算指标"""
    db = next(get_db())
    try:
        # 获取所有记录
        all_metrics = db.query(Metrics).all()
        total_count = len(all_metrics)
        
        if total_count == 0:
            return {
                "total_count": 0,
                "intent_accuracy": 0,
                "completion_rate": 0,
                "context_hit_rate": 0,
                "transfer_rate": 0,
                "avg_response_time": 0,
                "correct_answer_rate": 0,
                "hallucination_rate": 0
            }
        
        # 计算各项指标
        correct_count = sum(1 for m in all_metrics if m.is_correct)
        completed_count = sum(1 for m in all_metrics if m.is_completed)
        context_used_count = sum(1 for m in all_metrics if m.is_context_used)
        transferred_count = sum(1 for m in all_metrics if m.is_transferred)
        total_response_time = sum(m.response_time for m in all_metrics if m.response_time)
        
        # 计算正确答案率和幻觉率（只统计已标注的数据）
        labeled_metrics = [m for m in all_metrics if m.is_correct_answer is not None]
        hallucination_labeled = [m for m in all_metrics if m.is_hallucination is not None]
        
        if labeled_metrics:
            correct_answer_count = sum(1 for m in labeled_metrics if m.is_correct_answer)
            correct_answer_rate = (correct_answer_count / len(labeled_metrics)) * 100
        else:
            correct_answer_rate = 0
            
        if hallucination_labeled:
            hallucination_count = sum(1 for m in hallucination_labeled if m.is_hallucination)
            hallucination_rate = (hallucination_count / len(hallucination_labeled)) * 100
        else:
            hallucination_rate = 0
        
        # 计算百分比
        intent_accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
        completion_rate = (completed_count / total_count) * 100 if total_count > 0 else 0
        context_hit_rate = (context_used_count / total_count) * 100 if total_count > 0 else 0
        transfer_rate = (transferred_count / total_count) * 100 if total_count > 0 else 0
        avg_response_time = total_response_time / total_count if total_count > 0 else 0
        
        return {
            "total_count": total_count,
            "intent_accuracy": round(intent_accuracy, 2),
            "completion_rate": round(completion_rate, 2),
            "context_hit_rate": round(context_hit_rate, 2),
            "transfer_rate": round(transfer_rate, 2),
            "avg_response_time": round(avg_response_time, 2),
            "correct_answer_rate": round(correct_answer_rate, 2),
            "hallucination_rate": round(hallucination_rate, 2),
            "labeled_count": len(labeled_metrics),
            "hallucination_labeled_count": len(hallucination_labeled)
        }
    except Exception as e:
        print(f"计算指标失败: {e}")
        return {
            "total_count": 0,
            "intent_accuracy": 0,
            "completion_rate": 0,
            "context_hit_rate": 0,
            "transfer_rate": 0,
            "avg_response_time": 0,
            "correct_answer_rate": 0,
            "hallucination_rate": 0,
            "labeled_count": 0,
            "hallucination_labeled_count": 0
        }
    finally:
        db.close()


if __name__ == "__main__":
    create_metrics_table()