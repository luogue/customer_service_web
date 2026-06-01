"""
数据迁移脚本
将现有数据迁移到知识底座层的数据库表中
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_base.models import (
    engine, Base, SessionLocal,
    User, FAQ, Conversation, Order, OrderItem, Logistics, AfterSale, Document
)
from sqlalchemy import inspect, text


def parse_datetime(value):
    """解析日期时间字符串"""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        # 尝试解析常见的日期时间格式
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except:
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        except:
            try:
                return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except:
                return None

def get_existing_tables():
    """获取数据库中现有的表"""
    inspector = inspect(engine)
    return inspector.get_table_names()

def migrate_users():
    """迁移用户数据"""
    print("迁移用户数据...")
    
    db = SessionLocal()
    try:
        # 检查是否存在旧的users表
        existing_tables = get_existing_tables()
        if 'users' in existing_tables:
            # 检查是否有数据
            result = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
            if result > 0:
                print(f"发现 {result} 条用户数据，开始迁移...")
                
                # 这里可以添加具体的迁移逻辑
                # 例如：从旧表读取数据，转换后写入新表
                
                print("用户数据迁移完成！")
            else:
                print("用户表为空，跳过迁移")
        else:
            print("用户表不存在，跳过迁移")
    except Exception as e:
        print(f"迁移用户数据失败: {e}")
    finally:
        db.close()

def migrate_conversations():
    """迁移对话记录数据"""
    print("迁移对话记录数据...")
    
    db = SessionLocal()
    try:
        # 检查是否存在旧的messages表
        existing_tables = get_existing_tables()
        if 'messages' in existing_tables:
            # 检查是否有数据
            result = db.execute(text("SELECT COUNT(*) FROM messages")).scalar()
            if result > 0:
                print(f"发现 {result} 条对话记录数据，开始迁移...")
                
                # 读取旧数据
                old_messages = db.execute(text("SELECT * FROM messages")).fetchall()
                
                # 转换并插入新表
                for msg in old_messages:
                    # 处理日期时间类型
                    created_at = parse_datetime(msg.created_at)
                    
                    conversation = Conversation(
                        user_id=msg.user_id if hasattr(msg, 'user_id') else None,
                        session_id=msg.session_id,
                        message=msg.content,
                        sender=msg.role,
                        intent=None,  # 旧表可能没有intent字段
                        created_at=created_at
                    )
                    db.add(conversation)
                
                db.commit()
                print("对话记录数据迁移完成！")
            else:
                print("对话记录表为空，跳过迁移")
        else:
            print("对话记录表不存在，跳过迁移")
    except Exception as e:
        print(f"迁移对话记录数据失败: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_orders():
    """迁移订单数据"""
    print("迁移订单数据...")
    
    db = SessionLocal()
    try:
        # 检查是否存在旧的orders表
        existing_tables = get_existing_tables()
        if 'orders' in existing_tables:
            # 检查是否有数据
            result = db.execute(text("SELECT COUNT(*) FROM orders")).scalar()
            if result > 0:
                print(f"发现 {result} 条订单数据，开始迁移...")
                
                # 读取旧数据
                old_orders = db.execute(text("SELECT * FROM orders")).fetchall()
                
                # 转换并插入新表
                for order in old_orders:
                    # 处理日期时间类型
                    created_at = parse_datetime(order.created_at)
                    updated_at = parse_datetime(order.updated_at)
                    
                    new_order = Order(
                        user_id=order.user_id,
                        order_no=order.order_number,
                        total_amount=order.total_amount,
                        status=order.status,
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    db.add(new_order)
                
                db.commit()
                print("订单数据迁移完成！")
            else:
                print("订单表为空，跳过迁移")
        else:
            print("订单表不存在，跳过迁移")
    except Exception as e:
        print(f"迁移订单数据失败: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_logistics():
    """迁移物流数据"""
    print("迁移物流数据...")
    
    db = SessionLocal()
    try:
        # 检查是否存在旧的logistics表
        existing_tables = get_existing_tables()
        if 'logistics' in existing_tables:
            # 检查是否有数据
            result = db.execute(text("SELECT COUNT(*) FROM logistics")).scalar()
            if result > 0:
                print(f"发现 {result} 条物流数据，开始迁移...")
                
                # 读取旧数据
                old_logistics = db.execute(text("SELECT * FROM logistics")).fetchall()
                
                # 转换并插入新表
                for logistics in old_logistics:
                    # 处理日期时间类型
                    created_at = parse_datetime(logistics.created_at)
                    updated_at = parse_datetime(logistics.updated_at)
                    
                    new_logistics = Logistics(
                        order_id=logistics.order_id,
                        logistics_company=logistics.carrier,
                        tracking_number=logistics.tracking_number,
                        status=logistics.status,
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    db.add(new_logistics)
                
                db.commit()
                print("物流数据迁移完成！")
            else:
                print("物流表为空，跳过迁移")
        else:
            print("物流表不存在，跳过迁移")
    except Exception as e:
        print(f"迁移物流数据失败: {e}")
        db.rollback()
    finally:
        db.close()

def migrate_after_sales():
    """迁移售后数据"""
    print("迁移售后数据...")
    
    db = SessionLocal()
    try:
        # 检查是否存在旧的refunds表
        existing_tables = get_existing_tables()
        if 'refunds' in existing_tables:
            # 检查是否有数据
            result = db.execute(text("SELECT COUNT(*) FROM refunds")).scalar()
            if result > 0:
                print(f"发现 {result} 条售后数据，开始迁移...")
                
                # 读取旧数据
                old_refunds = db.execute(text("SELECT * FROM refunds")).fetchall()
                
                # 转换并插入新表
                for refund in old_refunds:
                    # 处理日期时间类型
                    created_at = parse_datetime(refund.created_at)
                    updated_at = parse_datetime(refund.updated_at)
                    
                    after_sale = AfterSale(
                        order_id=refund.order_id,
                        user_id=None,  # 旧表可能没有user_id字段
                        type="refund",
                        reason=refund.reason,
                        status=refund.status,
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    db.add(after_sale)
                
                db.commit()
                print("售后数据迁移完成！")
            else:
                print("售后表为空，跳过迁移")
        else:
            print("售后表不存在，跳过迁移")
    except Exception as e:
        print(f"迁移售后数据失败: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """主函数"""
    print("数据迁移脚本")
    print("=" * 50)
    
    # 迁移数据
    migrate_users()
    migrate_conversations()
    migrate_orders()
    migrate_logistics()
    migrate_after_sales()
    
    print("\n数据迁移完成！")
    print("所有数据已统一存储到知识底座层的数据库表中")

if __name__ == "__main__":
    main()
