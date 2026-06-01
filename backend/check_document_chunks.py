import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# 创建数据库引擎
engine = sa.create_engine(settings.DATABASE_URL)
inspector = sa.inspect(engine)

print('检查document_chunks表...')
if 'document_chunks' in inspector.get_table_names():
    print('document_chunks表结构:')
    for col in inspector.get_columns('document_chunks'):
        print('  ' + col['name'] + ': ' + str(col['type']))

print('\n检查documents表...')
for col in inspector.get_columns('documents'):
    print('  ' + col['name'] + ': ' + str(col['type']))
