import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# 创建数据库引擎
engine = sa.create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# 检查documents表数据
print('Documents表数据:')
documents = session.execute(sa.text('SELECT id, title, created_at FROM documents')).fetchall()
for doc in documents:
    print(f'  ID: {doc[0]}, 标题: {doc[1]}, 创建时间: {doc[2]}')

print(f'\n总共有 {len(documents)} 个文档')

# 检查document_chunks表数据
print('\nDocument_chunks表数据:')
chunks = session.execute(sa.text('SELECT COUNT(*) FROM document_chunks')).scalar()
print(f'总共有 {chunks} 个内容碎片')

# 检查是否有document_id关联
print('\n检查内容碎片的document_id关联:')
document_ids = session.execute(sa.text('SELECT DISTINCT document_id FROM document_chunks')).fetchall()
print(f'关联的文档ID: {[id[0] for id in document_ids]}')

session.close()
