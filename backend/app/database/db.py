from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.missing_person import Base, MissingPerson  # MissingPerson도 import 필요
import os

# 데이터베이스 URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./safemap.db")

# 엔진 생성
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """데이터베이스 초기화"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
