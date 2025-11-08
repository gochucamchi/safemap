from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text
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

    # 사진 정보
    photo_urls = Column(Text, nullable=True)  # 쉼표로 구분된 사진 URL 리스트
    photo_count = Column(Integer, default=0)  # 사진 개수
    photos_downloaded = Column(DateTime, nullable=True)  # 사진 다운로드 일시

    status = Column(String(20), default="missing", index=True)  # 상태 (missing/resolved)
    resolved_at = Column(DateTime, nullable=True)  # 실종 해제 일시
    created_at = Column(DateTime)  # 생성일시
    updated_at = Column(DateTime)  # 수정일시
