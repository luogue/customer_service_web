"""
检查默认Prompt模板是否存在
"""
import sqlite3
import os

# 获取数据库文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'knowledge_base', 'test.db')

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查默认模板是否存在
try:
    cursor.execute("SELECT * FROM prompt_templates WHERE is_default = 1;")
    result = cursor.fetchone()
    if result:
        print("默认Prompt模板已存在")
        print(f"ID: {result[0]}")
        print(f"模板名: {result[1]}")
        print(f"模板内容: {result[2]}")
        print(f"是否默认: {result[3]}")
        print(f"创建时间: {result[4]}")
        print(f"更新时间: {result[5]}")
    else:
        print("默认Prompt模板不存在")
except Exception as e:
    print(f"错误: {e}")
finally:
    conn.close()
