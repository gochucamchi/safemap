from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MissingPerson(Base):
    """실종자 정보 모델"""
    __tablename__ = "missing_persons"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # 실종자식별코드

    # 기본 정보
    name = Column(String, nullable=True)  # 이름
    missing_date = Column(DateTime)  # 발생일시
    age_at_disappearance = Column(Integer, nullable=True)  # 실종 당시 나이
    gender = Column(String(1), nullable=True)  # 성별 (M/F)
    nationality = Column(String, nullable=True)  # 국적

    # 위치 정보
    location_address = Column(String)  # 발생장소 주소
    location_detail = Column(String, nullable=True)  # 발생장소 상세
    latitude = Column(Float, nullable=True)  # 위도
    longitude = Column(Float, nullable=True)  # 경도
    geocoding_status = Column(String(20), default="pending")  # pending/success/failed

    # 신체 특징
    height = Column(Integer, nullable=True)  # 키 (cm)
    weight = Column(Integer, nullable=True)  # 몸무게 (kg)
    body_type = Column(String, nullable=True)  # 체격
    face_shape = Column(String, nullable=True)  # 얼굴형
    hair_color = Column(String, nullable=True)  # 두발색상
    hair_style = Column(String, nullable=True)  # 두발형태

    # 착의사항
    clothing_description = Column(Text, nullable=True)  # 착의의상 상세

    # 사진 (JSON 배열로 저장)
    photo_urls = Column(Text, nullable=True)  # JSON 배열 문자열

    # 기타 특징
    special_features = Column(Text, nullable=True)  # 기타 특이사항

    # 상태 관리
    status = Column(String(20), default="missing", index=True)  # missing/resolved
    resolved_at = Column(DateTime, nullable=True)  # 실종 해제 일시
    created_at = Column(DateTime)  # 생성일시
    updated_at = Column(DateTime)  # 수정일시
