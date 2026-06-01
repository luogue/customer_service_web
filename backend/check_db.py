"""
检查数据库连接和表结构
"""

import sqlite3
import os
from config.settings import settings

print(f"数据库路径: {settings.DATABASE_URL}")

# 从SQLite URL中提取文件路径
db_path = settings.DATABASE_URL.replace('sqlite:///', '')
print(f"数据库文件: {db_path}")
print(f"文件存在: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查看所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\n数据库中的表:")
    for table in tables:
        print(f"- {table[0]}")
    
    # 查看knowledge表的结构
    try:
        cursor.execute("PRAGMA table_info(knowledge);")
        columns = cursor.fetchall()
        print("\nknowledge表结构:")
        for column in columns:
            print(f"- {column[1]}: {column[2]}")
    except Exception as e:
        print(f"\n查看knowledge表结构失败: {e}")
    
    conn.close()
else:
    print("数据库文件不存在")
