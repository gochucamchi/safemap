# -*- coding: utf-8 -*-
"""
실종자 API 엔드포인트 (버그 수정 버전)
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func  # ✅ 추가!
from typing import List, Optional
from datetime import datetime, timedelta
import os

from app.database.db import get_db
from app.models.missing_person import MissingPerson
from app.services.data_sync_service import DataSyncService

router = APIRouter()


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SafeMap API"
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
    # ✅ 수정: db.func → func
    top_locations = db.query(
        MissingPerson.location_address,
        func.count(MissingPerson.id).label("count")
    ).filter(
        MissingPerson.missing_date >= since_date
    ).group_by(
        MissingPerson.location_address
    ).order_by(
        func.count(MissingPerson.id).desc()
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
    background_tasks: BackgroundTasks,
    max_pages: int = 10,
    db: Session = Depends(get_db)
):
    """
    안전Dream API에서 데이터 동기화
    
    Args:
        max_pages: 동기화할 최대 페이지 수 (기본: 10)
    """
    api_key = os.getenv("SAFE_DREAM_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="API 키가 설정되지 않았습니다. 환경변수를 확인해주세요."
        )
    
    try:
        # 동기화 서비스 실행
        service = DataSyncService(api_key=api_key)
        result = await service.sync_all_data(max_pages=max_pages)
        
        if not result["success"]:
            return {
                "status": "error",
                "message": "동기화 중 오류가 발생했습니다",
                "errors": result["errors"]
            }
        
        # 통계 조회
        stats = service.get_statistics()
        
        return {
            "status": "success",
            "message": "데이터 동기화 완료",
            "sync_result": {
                "total_fetched": result["total_fetched"],
                "new_added": result["new_added"],
                "updated": result["updated"],
                "skipped": result["skipped"],
                "duration_seconds": result["duration"],
            },
            "database_stats": stats,
            "errors": result["errors"] if result["errors"] else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"동기화 실패: {str(e)}"
        )


@router.get("/db/stats")
async def get_db_statistics(db: Session = Depends(get_db)):
    """데이터베이스 통계"""
    total_count = db.query(MissingPerson).count()
    
    # 위경도가 있는 데이터
    geocoded_count = db.query(MissingPerson).filter(
        MissingPerson.latitude.isnot(None),
        MissingPerson.longitude.isnot(None)
    ).count()
    
    # 최근 7일 추가된 데이터
    recent_date = datetime.now() - timedelta(days=7)
    recent_count = db.query(MissingPerson).filter(
        MissingPerson.created_at >= recent_date
    ).count()
    
    # 가장 최근 업데이트 시간
    latest = db.query(MissingPerson)\
        .order_by(MissingPerson.updated_at.desc())\
        .first()
    
    return {
        "total_count": total_count,
        "geocoded_count": geocoded_count,
        "geocoded_percentage": round(geocoded_count / total_count * 100, 1) if total_count > 0 else 0,
        "recent_count": recent_count,
        "last_updated": latest.updated_at.isoformat() if latest else None
    }


@router.delete("/missing-persons/clear")
async def clear_all_data(
    confirm: str = None,
    db: Session = Depends(get_db)
):
    """
    모든 데이터 삭제 (개발용)
    
    Args:
        confirm: "DELETE_ALL"을 입력해야 실행됨
    """
    if confirm != "DELETE_ALL":
        raise HTTPException(
            status_code=400,
            detail="데이터 삭제를 확인하려면 confirm=DELETE_ALL 파라미터를 추가하세요"
        )
    
    try:
        count = db.query(MissingPerson).count()
        db.query(MissingPerson).delete()
        db.commit()
        
        return {
            "status": "success",
            "message": f"{count}건의 데이터가 삭제되었습니다"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"삭제 실패: {str(e)}")