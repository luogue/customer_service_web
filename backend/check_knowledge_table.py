import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# 创建数据库引擎
engine = sa.create_engine(settings.DATABASE_URL)
inspector = sa.inspect(engine)

print('检查knowledge表...')
tables = inspector.get_table_names()

if 'knowledge' in tables:
    print('knowledge表存在')
    print('knowledge表结构:')
    for col in inspector.get_columns('knowledge'):
        print('  ' + col['name'] + ': ' + str(col['type']))
else:
    print('knowledge表不存在')
    print('现有表:', tables)
