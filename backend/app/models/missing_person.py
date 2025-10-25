from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class MissingPerson(Base):
    """실종자 정보 모델"""
    __tablename__ = "missing_persons"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 기본 정보
    name = Column(String(100), nullable=True)  # 이름 (개인정보로 비공개 가능)
    age = Column(Integer, nullable=True)  # 나이
    gender = Column(String(10), nullable=True)  # 성별
    
    # 실종 정보
    missing_date = Column(DateTime, nullable=False)  # 실종일시
    location_address = Column(String(500), nullable=False)  # 실종 장소 (주소)
    location_detail = Column(Text, nullable=True)  # 상세 위치 설명
    
    # 지리 정보 (좌표)
    latitude = Column(Float, nullable=True)  # 위도
    longitude = Column(Float, nullable=True)  # 경도
    
    # 외모 정보
    height = Column(Integer, nullable=True)  # 키 (cm)
    weight = Column(Integer, nullable=True)  # 몸무게 (kg)
    clothing = Column(Text, nullable=True)  # 착용 의류
    features = Column(Text, nullable=True)  # 특이사항
    
    # 메타 정보
    case_number = Column(String(100), unique=True, nullable=True)  # 사건번호
    status = Column(String(20), default="missing")  # 상태: missing, found, etc.
    source = Column(String(50), default="safe_dream")  # 데이터 출처
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<MissingPerson(id={self.id}, location={self.location_address}, date={self.missing_date})>"


class SafetyFacility(Base):
    """안전시설 정보 모델"""
    __tablename__ = "safety_facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 시설 정보
    name = Column(String(200), nullable=False)  # 시설명
    facility_type = Column(String(50), nullable=False)  # 시설 유형 (아동안전지킴이집, CCTV 등)
    address = Column(String(500), nullable=False)  # 주소
    
    # 지리 정보
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # 연락처
    phone = Column(String(20), nullable=True)
    
    # 메타 정보
    source = Column(String(50), default="safe_dream")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SafetyFacility(id={self.id}, name={self.name}, type={self.facility_type})>"
