# -*- coding: utf-8 -*-
"""
실종자 API 엔드포인트 (날짜 필터 추가 버전)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
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
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="상태 필터 (missing/resolved/all)", regex="^(missing|resolved|all)$"),
    days: Optional[int] = Query(None, ge=1, le=3650, description="최근 N일 데이터"),
    start_date: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    실종자 목록 조회

    상태 필터:
    - status=missing → 실종 중인 사람만
    - status=resolved → 실종 해제된 사람만
    - status=all 또는 생략 → 전체

    날짜 필터 옵션:
    1. days=30 → 최근 30일
    2. start_date=2024-01-01&end_date=2024-12-31 → 특정 기간
    3. 둘 다 없으면 → 전체 데이터
    """
    query = db.query(MissingPerson)

    # ✅ 상태 필터 적용
    if status and status != "all":
        query = query.filter(MissingPerson.status == status)

    # 날짜 필터 적용
    if days:
        # 최근 N일
        since_date = datetime.now() - timedelta(days=days)
        query = query.filter(MissingPerson.missing_date >= since_date)

    elif start_date and end_date:
        # 특정 기간
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            if start > end:
                raise HTTPException(
                    status_code=400,
                    detail="시작일이 종료일보다 늦을 수 없습니다"
                )

            query = query.filter(
                and_(
                    MissingPerson.missing_date >= start,
                    MissingPerson.missing_date <= end
                )
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력하세요"
            )

    # 정렬 및 페이징
    persons = query.order_by(MissingPerson.missing_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

    # 전체 개수 (필터 적용 후)
    total_count = query.count()

    return {
        "total": total_count,
        "items": [
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
                "status": p.status,  # ✅ 추가
                "resolved_at": p.resolved_at.isoformat() if p.resolved_at else None,  # ✅ 추가
            }
            for p in persons
        ]
    }


@router.get("/missing-persons/stats")
async def get_statistics(
    days: int = Query(30, ge=1, le=3650, description="최근 N일 통계"),
    db: Session = Depends(get_db)
):
    """통계 조회 (날짜 필터 적용)"""
    since_date = datetime.now() - timedelta(days=days)

    # 기간 내 전체 실종자
    total_query = db.query(MissingPerson)\
        .filter(MissingPerson.missing_date >= since_date)

    total_count = total_query.count()

    # ✅ 상태별 통계 (실종 중 / 실종 해제)
    status_stats = {}
    for status in ["missing", "resolved"]:
        count = total_query.filter(MissingPerson.status == status).count()
        status_stats[status] = count

    # 성별 통계
    gender_stats = {}
    for gender in ["M", "F"]:
        count = total_query.filter(MissingPerson.gender == gender).count()
        gender_stats[gender] = count

    # 지역별 통계 (상위 5개)
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

    # 일별 통계 (최근 30일)
    daily_stats = []
    for i in range(min(days, 30)):
        date = datetime.now() - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        count = db.query(MissingPerson).filter(
            and_(
                MissingPerson.missing_date >= date_start,
                MissingPerson.missing_date <= date_end
            )
        ).count()

        daily_stats.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": count
        })

    return {
        "period_days": days,
        "total_count": total_count,
        "status_statistics": status_stats,  # ✅ 추가
        "gender_statistics": gender_stats,
        "top_locations": [
            {"region": loc[0], "count": loc[1]}
            for loc in top_locations
        ],
        "daily_statistics": daily_stats
    }


@router.post("/sync/missing-persons")
async def sync_missing_persons(
    max_pages: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """안전Dream API에서 데이터 동기화"""
    api_key = os.getenv("SAFE_DREAM_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="API 키가 설정되지 않았습니다"
        )
    
    try:
        service = DataSyncService(api_key=api_key)
        result = await service.sync_all_data(max_pages=max_pages)
        
        if not result["success"]:
            return {
                "status": "error",
                "message": "동기화 중 오류가 발생했습니다",
                "errors": result["errors"]
            }
        
        stats = service.get_statistics()
        
        return {
            "status": "success",
            "message": "데이터 동기화 완료",
            "sync_result": {
                "total_fetched": result["total_fetched"],
                "new_added": result["new_added"],
                "updated": result["updated"],
                "resolved": result["resolved"],  # ✅ 추가
                "skipped": result["skipped"],
                "duration_seconds": result["duration"],
            },
            "database_stats": stats,
            "errors": result["errors"] if result["errors"] else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"동기화 실패: {str(e)}")


@router.get("/db/stats")
async def get_db_statistics(db: Session = Depends(get_db)):
    """데이터베이스 전체 통계"""
    total_count = db.query(MissingPerson).count()
    
    geocoded_count = db.query(MissingPerson).filter(
        MissingPerson.latitude.isnot(None),
        MissingPerson.longitude.isnot(None)
    ).count()
    
    recent_date = datetime.now() - timedelta(days=7)
    recent_count = db.query(MissingPerson).filter(
        MissingPerson.created_at >= recent_date
    ).count()
    
    latest = db.query(MissingPerson)\
        .order_by(MissingPerson.updated_at.desc())\
        .first()
    
    # 가장 오래된 데이터
    oldest = db.query(MissingPerson)\
        .filter(MissingPerson.missing_date.isnot(None))\
        .order_by(MissingPerson.missing_date.asc())\
        .first()
    
    # 가장 최근 데이터
    newest = db.query(MissingPerson)\
        .filter(MissingPerson.missing_date.isnot(None))\
        .order_by(MissingPerson.missing_date.desc())\
        .first()
    
    return {
        "total_count": total_count,
        "geocoded_count": geocoded_count,
        "geocoded_percentage": round(geocoded_count / total_count * 100, 1) if total_count > 0 else 0,
        "recent_count": recent_count,
        "last_updated": latest.updated_at.isoformat() if latest else None,
        "date_range": {
            "oldest": oldest.missing_date.isoformat() if oldest and oldest.missing_date else None,
            "newest": newest.missing_date.isoformat() if newest and newest.missing_date else None,
        }
    }


@router.delete("/missing-persons/clear")
async def clear_all_data(
    confirm: str = Query(None),
    db: Session = Depends(get_db)
):
    """모든 데이터 삭제 (개발용)"""
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
