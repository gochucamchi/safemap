from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database.db import get_db
from app.models.missing_person import MissingPerson, SafetyFacility
from app.services.safe_dream_api import safe_dream_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["Missing Persons"])


# Pydantic 모델 (응답 스키마)
class MissingPersonResponse(BaseModel):
    id: int
    name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    missing_date: datetime
    location_address: str
    latitude: Optional[float]
    longitude: Optional[float]
    status: str
    
    class Config:
        from_attributes = True


class SafetyFacilityResponse(BaseModel):
    id: int
    name: str
    facility_type: str
    address: str
    latitude: float
    longitude: float
    
    class Config:
        from_attributes = True


@router.get("/missing-persons", response_model=List[MissingPersonResponse])
async def get_missing_persons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    start_date: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
    gender: Optional[str] = Query(None, description="성별 (M/F)"),
    db: Session = Depends(get_db)
):
    """
    실종자 목록 조회
    
    - **skip**: 건너뛸 레코드 수
    - **limit**: 조회할 최대 레코드 수
    - **start_date**: 실종일 시작 (YYYY-MM-DD)
    - **end_date**: 실종일 종료 (YYYY-MM-DD)
    - **gender**: 성별 필터 (M 또는 F)
    """
    query = db.query(MissingPerson)
    
    # 날짜 필터
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(MissingPerson.missing_date >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(MissingPerson.missing_date <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    # 성별 필터
    if gender:
        query = query.filter(MissingPerson.gender == gender.upper())
    
    # 결과 조회
    missing_persons = query.offset(skip).limit(limit).all()
    
    return missing_persons


@router.get("/missing-persons/stats")
async def get_missing_statistics(
    days: int = Query(30, ge=1, le=365, description="통계 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    실종 사건 통계
    
    - **days**: 최근 N일간의 통계
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 총 실종자 수
    total_count = db.query(MissingPerson).filter(
        MissingPerson.missing_date >= start_date
    ).count()
    
    # 성별 통계
    gender_stats = {}
    for gender in ["M", "F"]:
        count = db.query(MissingPerson).filter(
            MissingPerson.missing_date >= start_date,
            MissingPerson.gender == gender
        ).count()
        gender_stats[gender] = count
    
    # 지역별 통계 (상위 10개)
    # SQLAlchemy를 사용한 그룹핑
    from sqlalchemy import func
    location_stats = db.query(
        func.substr(MissingPerson.location_address, 1, 10).label("region"),
        func.count(MissingPerson.id).label("count")
    ).filter(
        MissingPerson.missing_date >= start_date
    ).group_by("region").order_by(func.count(MissingPerson.id).desc()).limit(10).all()
    
    return {
        "period_days": days,
        "total_count": total_count,
        "gender_statistics": gender_stats,
        "top_locations": [
            {"region": loc[0], "count": loc[1]} 
            for loc in location_stats
        ]
    }


@router.get("/safety-facilities", response_model=List[SafetyFacilityResponse])
async def get_safety_facilities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    facility_type: Optional[str] = Query(None, description="시설 유형"),
    db: Session = Depends(get_db)
):
    """
    안전시설 목록 조회
    
    - **skip**: 건너뛸 레코드 수
    - **limit**: 조회할 최대 레코드 수
    - **facility_type**: 시설 유형 필터
    """
    query = db.query(SafetyFacility)
    
    if facility_type:
        query = query.filter(SafetyFacility.facility_type == facility_type)
    
    facilities = query.offset(skip).limit(limit).all()
    
    return facilities


@router.post("/sync/missing-persons")
async def sync_missing_persons_from_api(db: Session = Depends(get_db)):
    """
    안전Dream API에서 최신 실종자 데이터를 가져와 DB에 저장
    """
    try:
        # API에서 데이터 가져오기
        raw_data = await safe_dream_service.get_missing_alerts(limit=100)
        
        if not raw_data:
            return {"message": "No new data from API", "synced_count": 0}
        
        synced_count = 0
        
        for item in raw_data:
            # 데이터 파싱
            parsed = safe_dream_service.parse_missing_person_data(item)
            
            if not parsed:
                continue
            
            # 중복 체크 (case_number 기준)
            existing = None
            if parsed.get("case_number"):
                existing = db.query(MissingPerson).filter(
                    MissingPerson.case_number == parsed["case_number"]
                ).first()
            
            if existing:
                # 업데이트
                for key, value in parsed.items():
                    setattr(existing, key, value)
            else:
                # 새로 추가
                new_person = MissingPerson(**parsed)
                db.add(new_person)
                synced_count += 1
        
        db.commit()
        
        return {
            "message": "Sync completed successfully",
            "synced_count": synced_count,
            "total_processed": len(raw_data)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
