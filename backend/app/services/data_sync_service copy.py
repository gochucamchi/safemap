# -*- coding: utf-8 -*-
"""
안전Dream API 데이터 동기화 서비스 (수정 버전)
"""

import asyncio
from datetime import datetime
from typing import Dict, List

try:
    from sqlalchemy.orm import Session
    from app.services.safe_dream_api import SafeDreamAPI
    from app.models.missing_person import MissingPerson
    from app.database.db import SessionLocal
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("⚠️  SQLAlchemy를 찾을 수 없습니다. 먼저 패키지를 설치해주세요:")
    print("   pip install sqlalchemy fastapi uvicorn httpx python-dotenv")


class DataSyncService:
    """데이터 동기화 서비스"""
    
    def __init__(self, api_key: str, esntl_id: str = "10000855"):
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy가 설치되지 않았습니다")
        
        self.api_client = SafeDreamAPI(api_key=api_key, esntl_id=esntl_id)
        self.db = SessionLocal()
    
    async def sync_all_data(self, max_pages: int = 10) -> Dict:
        """모든 데이터 동기화"""
        print("\n" + "="*60)
        print("🚀 안전Dream API 데이터 동기화 시작")
        print("="*60 + "\n")
        
        result = {
            "success": True,
            "total_fetched": 0,
            "new_added": 0,
            "updated": 0,
            "skipped": 0,
            "errors": [],
            "start_time": datetime.now(),
        }
        
        try:
            all_persons = []
            
            for page in range(1, max_pages + 1):
                print(f"📄 페이지 {page}/{max_pages} 가져오는 중...")
                
                response = await self.api_client.get_missing_children(
                    row_size=100,
                    page_num=page
                )
                
                # ✅ 수정: success 필드로 체크
                if not response.get("success", False):
                    error_msg = f"API 호출 실패: {response.get('msg')}"
                    print(f"❌ {error_msg}")
                    result["errors"].append(error_msg)
                    continue
                
                persons_list = response.get("list", [])
                
                if not persons_list:
                    print(f"   ℹ️  페이지 {page}에 데이터 없음. 동기화 종료.")
                    break
                
                print(f"   ✅ {len(persons_list)}건 데이터 수신")
                all_persons.extend(persons_list)
                
                result["total_fetched"] += len(persons_list)
                
                await asyncio.sleep(0.5)
            
            print(f"\n📊 총 {result['total_fetched']}건의 데이터 수신 완료")
            print("\n" + "-"*60)
            print("💾 데이터베이스 저장 시작...")
            print("-"*60 + "\n")
            
            for idx, item in enumerate(all_persons, 1):
                try:
                    sync_result = self._sync_person(item)
                    
                    if sync_result == "added":
                        result["new_added"] += 1
                        print(f"✅ [{idx}/{len(all_persons)}] 새 데이터 추가: {item.get('occrAdres', 'N/A')[:30]}")
                    elif sync_result == "updated":
                        result["updated"] += 1
                        print(f"🔄 [{idx}/{len(all_persons)}] 데이터 업데이트: {item.get('occrAdres', 'N/A')[:30]}")
                    elif sync_result == "skipped":
                        result["skipped"] += 1
                    
                    if idx % 10 == 0:
                        self.db.commit()
                        print(f"   💾 {idx}건 저장 완료")
                
                except Exception as e:
                    error_msg = f"데이터 저장 실패: {str(e)}"
                    result["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
                    continue
            
            self.db.commit()
            
            result["end_time"] = datetime.now()
            result["duration"] = (result["end_time"] - result["start_time"]).total_seconds()
            
            print("\n" + "="*60)
            print("✅ 데이터 동기화 완료!")
            print("="*60)
            print(f"""
📊 동기화 결과:
   • 전체 수신: {result['total_fetched']}건
   • 새로 추가: {result['new_added']}건
   • 업데이트: {result['updated']}건
   • 건너뜀: {result['skipped']}건
   • 에러: {len(result['errors'])}건
   • 소요 시간: {result['duration']:.2f}초
            """)
            
            if result["errors"]:
                print("\n⚠️  에러 목록:")
                for error in result["errors"][:5]:
                    print(f"   - {error}")
                if len(result["errors"]) > 5:
                    print(f"   ... 외 {len(result['errors']) - 5}건")
            
            print("="*60 + "\n")
            
        except Exception as e:
            result["success"] = False
            result["errors"].append(f"동기화 중 치명적 오류: {str(e)}")
            print(f"\n❌ 치명적 오류 발생: {str(e)}\n")
            self.db.rollback()
        
        finally:
            self.db.close()
        
        return result
    
    def _sync_person(self, item: Dict) -> str:
        """개별 실종자 데이터 동기화"""
        parsed = self.api_client.parse_missing_person(item)
        
        if not parsed or not parsed.get("external_id"):
            return "skipped"
        
        existing = self.db.query(MissingPerson).filter(
            MissingPerson.external_id == parsed["external_id"]
        ).first()
        
        if existing:
            for key, value in parsed.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.now()
            return "updated"
        else:
            new_person = MissingPerson(
                **parsed,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(new_person)
            return "added"
    
    def get_statistics(self) -> Dict:
        """현재 DB 통계 조회"""
        try:
            total_count = self.db.query(MissingPerson).count()
            
            from datetime import timedelta
            recent_date = datetime.now() - timedelta(days=7)
            recent_count = self.db.query(MissingPerson).filter(
                MissingPerson.created_at >= recent_date
            ).count()
            
            geocoded_count = self.db.query(MissingPerson).filter(
                MissingPerson.latitude.isnot(None),
                MissingPerson.longitude.isnot(None)
            ).count()
            
            return {
                "total_count": total_count,
                "recent_count": recent_count,
                "geocoded_count": geocoded_count,
                "geocoded_percentage": round(geocoded_count / total_count * 100, 1) if total_count > 0 else 0
            }
        finally:
            self.db.close()


async def run_sync(api_key: str, max_pages: int = 10):
    """동기화 실행 함수"""
    service = DataSyncService(api_key=api_key)
    result = await service.sync_all_data(max_pages=max_pages)
    
    stats = service.get_statistics()
    print("\n" + "="*60)
    print("📊 현재 데이터베이스 통계")
    print("="*60)
    print(f"""
   • 전체 실종자: {stats['total_count']}명
   • 최근 7일 추가: {stats['recent_count']}명
   • 위경도 변환 완료: {stats['geocoded_count']}명 ({stats['geocoded_percentage']}%)
    """)
    print("="*60 + "\n")
    
    return result


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    API_KEY = os.getenv("SAFE_DREAM_API_KEY", "4fd2a9d68b504580")
    
    print("🚀 SafeMap 데이터 동기화 시작...\n")
    result = asyncio.run(run_sync(api_key=API_KEY, max_pages=10))
    
    if result["success"]:
        print("✅ 동기화 성공!")
    else:
        print("❌ 동기화 실패")
        for error in result["errors"]:
            print(f"   - {error}")