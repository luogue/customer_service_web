import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# 创建数据库引擎
engine = sa.create_engine(settings.DATABASE_URL)
inspector = sa.inspect(engine)

print('现有表:', inspector.get_table_names())

print('\ndocuments表结构:')
for col in inspector.get_columns('documents'):
    print('  ' + col['name'] + ': ' + str(col['type']))
