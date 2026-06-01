"""
检查Prompt模板表是否存在
"""
import sqlite3
import os

# 获取数据库文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'knowledge_base', 'test.db')

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查表是否存在
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prompt_templates';")
    result = cursor.fetchone()
    if result:
        print("Prompt模板表已存在")
        # 查看表结构
        cursor.execute("PRAGMA table_info(prompt_templates);")
        columns = cursor.fetchall()
        print("表结构:")
        for column in columns:
            print(column)
    else:
        print("Prompt模板表不存在")
except Exception as e:
    print(f"错误: {e}")
finally:
    conn.close()
