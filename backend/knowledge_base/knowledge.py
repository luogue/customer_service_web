import json
import os
from typing import List, Dict, Generator
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from .models import Message, User, Order, Refund, Logistics, Complaint, Transfer, Escalation

load_dotenv()

class DatabaseManager:
    """数据库管理类"""
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./knowledge_base/test.db")
        self.engine = create_engine(
            self.DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in self.DATABASE_URL else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()
    
    def get_db(self) -> Generator:
        """获取数据库会话"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def create_all(self):
        """创建所有表"""
        self.Base.metadata.create_all(bind=self.engine)

class KnowledgeBase:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.faq_data = []
        self.documents = []
        self.db_manager = DatabaseManager()
        self._load_data()
    
    def _load_data(self):
        """加载知识库数据"""
        faq_path = os.path.join(self.data_dir, "faq.json")
        if os.path.exists(faq_path):
            with open(faq_path, 'r', encoding='utf-8') as f:
                self.faq_data = json.load(f)
    
    def search_faq(self, query: str, top_k: int = 3) -> List[Dict]:
        """搜索FAQ"""
        results = []
        query_lower = query.lower()
        
        for item in self.faq_data:
            score = 0
            if query_lower in item.get('question', '').lower():
                score += 2
            if query_lower in item.get('answer', '').lower():
                score += 1
            if any(query_lower in kw.lower() for kw in item.get('keywords', [])):
                score += 3
            
            if score > 0:
                results.append({**item, 'score': score})
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def add_faq(self, question: str, answer: str, keywords: List[str] = None):
        """添加FAQ"""
        self.faq_data.append({
            'id': len(self.faq_data) + 1,
            'question': question,
            'answer': answer,
            'keywords': keywords or [],
            'created_at': datetime.now().isoformat()
        })
        self._save_data()
    
    def _save_data(self):
        """保存知识库数据"""
        os.makedirs(self.data_dir, exist_ok=True)
        faq_path = os.path.join(self.data_dir, "faq.json")
        with open(faq_path, 'w', encoding='utf-8') as f:
            json.dump(self.faq_data, f, ensure_ascii=False, indent=2)
    
    def save_message(self, session_id: str, role: str, content: str, db):
        """保存消息到数据库"""
        try:
            from .models import Message as DBMessage
            db_message = DBMessage(
                session_id=session_id,
                role=role,
                content=content,
                type='text'
            )
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
        except Exception as e:
            db.rollback()
            print(f"Error saving message to database: {e}")

knowledge_base = KnowledgeBase()
