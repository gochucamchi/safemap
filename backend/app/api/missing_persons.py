from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os

from app.database.db import get_db
from app.models.missing_person import MissingPerson
from app.services.safe_dream_api import get_safe_dream_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/missing-persons")
async def get_missing_persons(
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """실종자 목록 조회"""
    persons = db.query(MissingPerson)\
        .order_by(MissingPerson.missing_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [
        {
            "id": p.id,
            "external_id": p.external_id,
            "missing_date": p.missing_date.isoformat() if p.missing_date else None,
            "location_address": p.location_address,
            "location_detail": p.location_detail,
            "age": p.age,
            "gender": p.gender,
            "latitude": p.latitude,
            "longitude": p.longitude,
        }
        for p in persons
    ]

@router.get("/missing-persons/stats")
async def get_statistics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """통계 조회"""
    since_date = datetime.now() - timedelta(days=days)
    
    # 기간 내 전체 실종자
    total_query = db.query(MissingPerson)\
        .filter(MissingPerson.missing_date >= since_date)
    
    total_count = total_query.count()
    
    # 성별 통계
    gender_stats = {}
    for gender in ["M", "F"]:
        count = total_query.filter(MissingPerson.gender == gender).count()
        gender_stats[gender] = count
    
    # 지역별 통계 (상위 5개)
    top_locations = db.query(
        MissingPerson.location_address,
        db.func.count(MissingPerson.id).label("count")
    ).filter(
        MissingPerson.missing_date >= since_date
    ).group_by(
        MissingPerson.location_address
    ).order_by(
        db.func.count(MissingPerson.id).desc()
    ).limit(5).all()
    
    return {
        "period_days": days,
        "total_count": total_count,
        "gender_statistics": gender_stats,
        "top_locations": [
            {"region": loc[0], "count": loc[1]}
            for loc in top_locations
        ]
    }

@router.post("/sync/missing-persons")
async def sync_missing_persons(
    db: Session = Depends(get_db)
):
    """안전Dream API에서 데이터 동기화"""
    api_key = os.getenv("SAFE_DREAM_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API 키가 설정되지 않았습니다")
    
    try:
        service = get_safe_dream_service(api_key)
        
        # API 호출
        response = await service.get_missing_children(row_size=100, page_num=1)
        
        if response.get("result") != "성공":
            return {
                "message": f"API 호출 실패: {response.get('msg')}",
                "synced_count": 0
            }
        
        persons_list = response.get("list", [])
        synced_count = 0
        
        for item in persons_list:
            # 데이터 파싱
            parsed = service.parse_missing_person(item)
            if not parsed or not parsed.get("external_id"):
                continue
            
            # 이미 있는지 확인
            existing = db.query(MissingPerson).filter(
                MissingPerson.external_id == parsed["external_id"]
            ).first()
            
            if existing:
                # 업데이트
                for key, value in parsed.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.now()
            else:
                # 새로 추가
                new_person = MissingPerson(
                    **parsed,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(new_person)
                synced_count += 1
        
        db.commit()
        
        return {
            "message": "동기화 완료",
            "synced_count": synced_count,
            "total_in_api": len(persons_list),
            "total_count": response.get("totalCount", 0)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"동기화 실패: {str(e)}")
