"""
数据备份管理模块
功能：
- SQLite数据库每日凌晨自动备份，保留近7天备份文件
- Chroma向量库每周备份持久化目录，避免数据丢失
"""
import os
import shutil
import time
import schedule
import threading
from datetime import datetime, timedelta
from pathlib import Path


class BackupManager:
    """备份管理器"""
    
    def __init__(self):
        """初始化备份管理器"""
        # 配置路径
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.backup_dir = os.path.join(self.base_dir, "backups")
        self.db_path = os.path.join(self.base_dir, "knowledge_base", "knowledge_base.db")
        self.vector_index_path = os.path.join(self.base_dir, "vector_index")
        
        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, "db"), exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, "vector"), exist_ok=True)
        
        # 配置保留天数
        self.db_backup_days = 7
        self.vector_backup_days = 7
    
    def backup_sqlite_db(self):
        """备份SQLite数据库"""
        try:
            if not os.path.exists(self.db_path):
                print(f"[备份警告] SQLite数据库文件不存在: {self.db_path}")
                return
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, "db", f"knowledge_base_{timestamp}.db")
            
            # 执行备份
            shutil.copy2(self.db_path, backup_file)
            print(f"[备份成功] SQLite数据库备份到: {backup_file}")
            
            # 清理过期备份
            self.clean_old_backups("db", self.db_backup_days)
            
        except Exception as e:
            print(f"[备份错误] SQLite数据库备份失败: {e}")
    
    def backup_chroma_vector(self):
        """备份Chroma向量库"""
        try:
            if not os.path.exists(self.vector_index_path):
                print(f"[备份警告] Chroma向量库目录不存在: {self.vector_index_path}")
                return
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.backup_dir, "vector", f"vector_index_{timestamp}")
            
            # 执行备份
            shutil.copytree(self.vector_index_path, backup_dir)
            print(f"[备份成功] Chroma向量库备份到: {backup_dir}")
            
            # 清理过期备份
            self.clean_old_backups("vector", self.vector_backup_days)
            
        except Exception as e:
            print(f"[备份错误] Chroma向量库备份失败: {e}")
    
    def clean_old_backups(self, backup_type, days):
        """清理过期备份
        
        Args:
            backup_type: 备份类型 ("db" 或 "vector")
            days: 保留天数
        """
        try:
            backup_dir = os.path.join(self.backup_dir, backup_type)
            cutoff_time = time.time() - (days * 24 * 3600)
            
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                if os.path.isfile(item_path):
                    if os.path.getmtime(item_path) < cutoff_time:
                        os.remove(item_path)
                        print(f"[清理备份] 删除过期的{backup_type}备份: {item}")
                elif os.path.isdir(item_path):
                    if os.path.getmtime(item_path) < cutoff_time:
                        shutil.rmtree(item_path)
                        print(f"[清理备份] 删除过期的{backup_type}备份目录: {item}")
                        
        except Exception as e:
            print(f"[清理错误] 清理过期备份失败: {e}")
    
    def schedule_backups(self):
        """设置定时备份任务"""
        # 每日凌晨1点备份SQLite数据库
        schedule.every().day.at("01:00").do(self.backup_sqlite_db)
        
        # 每周日凌晨2点备份Chroma向量库
        schedule.every().sunday.at("02:00").do(self.backup_chroma_vector)
        
        print("[备份调度] 已设置定时备份任务")
        print("- 每日凌晨1:00备份SQLite数据库")
        print("- 每周日凌晨2:00备份Chroma向量库")
    
    def run_scheduler(self):
        """运行调度器"""
        def scheduler_loop():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        # 启动调度器线程
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
        print("[备份调度] 备份调度器已启动")
    
    def run_initial_backup(self):
        """运行初始备份"""
        print("[备份初始化] 执行初始备份")
        self.backup_sqlite_db()
        self.backup_chroma_vector()


# 全局备份管理器实例
backup_manager = BackupManager()


def init_backup_system():
    """初始化备份系统"""
    backup_manager.run_initial_backup()
    backup_manager.schedule_backups()
    backup_manager.run_scheduler()


if __name__ == "__main__":
    # 测试备份功能
    backup_manager.run_initial_backup()
    
    # 测试定时任务（运行5分钟）
    backup_manager.schedule_backups()
    backup_manager.run_scheduler()
    
    print("测试备份系统运行中，将在5分钟后退出...")
    time.sleep(300)
