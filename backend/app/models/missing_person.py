from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MissingPerson(Base):
    """실종자 정보 모델"""
    __tablename__ = "missing_persons"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # 실종자식별코드
    missing_date = Column(DateTime)  # 발생일시
    location_address = Column(String)  # 발생장소
    location_detail = Column(String, nullable=True)  # 착의사항/상세정보
    age = Column(Integer, nullable=True)  # 나이
    gender = Column(String(1), nullable=True)  # 성별 (M/F)
    latitude = Column(Float, nullable=True)  # 위도
    longitude = Column(Float, nullable=True)  # 경도
    created_at = Column(DateTime)  # 생성일시
    updated_at = Column(DateTime)  # 수정일시
