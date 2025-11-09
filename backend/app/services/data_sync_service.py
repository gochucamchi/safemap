# -*- coding: utf-8 -*-
"""
안전Dream API 데이터 동기화 서비스 (마지막 페이지 오류 수정 버전)
- totalCount 기반 페이지 수 계산
- 마지막 페이지는 남은 개수만큼만 요청 ✅
"""

import asyncio
import math
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
    print("⚠️  SQLAlchemy를 찾을 수 없습니다.")


class DataSyncService:
    """데이터 동기화 서비스"""
    
    def __init__(self, api_key: str, esntl_id: str = "10000855"):
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy가 설치되지 않았습니다")
        
        self.api_client = SafeDreamAPI(api_key=api_key, esntl_id=esntl_id)
    
    async def sync_all_data(self, max_pages: int = 50, scrape_photos: bool = False, max_photo_persons: int = 100) -> Dict:
        """
        모든 데이터 동기화 (최적화)

        Args:
            max_pages: 최대 페이지 수
            scrape_photos: 사진 스크랩 여부
            max_photo_persons: 사진 스크랩할 최대 인원 (rate limiting 방지)
        """
        print("\n" + "="*60)
        print("🚀 안전Dream API 데이터 동기화 시작")
        print("="*60 + "\n")
        
        result = {
            "success": True,
            "total_fetched": 0,
            "new_added": 0,
            "updated": 0,
            "skipped": 0,
            "resolved": 0,  # 실종 해제
            "photos_scraped": 0,  # 사진 스크랩한 인원
            "total_photos": 0,  # 총 수집 사진
            "errors": [],
            "start_time": datetime.now(),
        }
        
        db = SessionLocal()
        
        try:
            all_persons = []
            row_size = 100  # 기본 페이지 크기
            
            # ✅ 첫 페이지에서 전체 개수 확인
            print(f"📄 페이지 1: 조회 중 (전체 개수 확인)...")
            first_response = await self.api_client.get_missing_children(
                row_size=row_size,
                page_num=1
            )
            
            if not first_response.get("success", False):
                error_msg = f"API 호출 실패: {first_response.get('msg')}"
                print(f"❌ {error_msg}")
                result["errors"].append(error_msg)
                result["success"] = False
                return result
            
            # ✅ 전체 데이터 개수와 필요한 페이지 수 계산
            total_count = first_response.get("totalCount", 0)
            first_list = first_response.get("list", [])
            
            if total_count > 0:
                # 필요한 페이지 수 계산
                needed_pages = math.ceil(total_count / row_size)
                actual_pages = min(needed_pages, max_pages)
                
                print(f"📊 전체 데이터: {total_count}건")
                print(f"📄 필요한 페이지: {needed_pages}페이지")
                print(f"📄 요청할 페이지: {actual_pages}페이지 (최대 {max_pages}페이지)\n")
            else:
                print("⚠️  전체 데이터 개수를 확인할 수 없습니다. 빈 페이지까지 요청합니다.\n")
                actual_pages = max_pages
            
            # 첫 페이지 데이터 추가
            if first_list:
                print(f"   ✅ 페이지 1: {len(first_list)}건 데이터 수신")
                all_persons.extend(first_list)
                result["total_fetched"] += len(first_list)
            
            # ✅ 나머지 페이지 요청
            for page in range(2, actual_pages + 1):
                # 🎯 마지막 페이지는 남은 개수만큼만 요청!
                if total_count > 0:
                    already_fetched = (page - 1) * row_size
                    remaining = total_count - already_fetched
                    current_row_size = min(row_size, remaining)
                else:
                    current_row_size = row_size
                
                print(f"📄 페이지 {page}/{actual_pages}: 조회 중 (요청 크기: {current_row_size}건)...")
                
                response = await self.api_client.get_missing_children(
                    row_size=current_row_size,  # ← 동적으로 계산된 크기!
                    page_num=page
                )
                
                if not response.get("success", False):
                    error_msg = f"페이지 {page} 실패: {response.get('msg')}"
                    print(f"❌ {error_msg}")
                    result["errors"].append(error_msg)
                    # 에러 발생 시 중단
                    break
                
                persons_list = response.get("list", [])
                
                # ✅ 빈 페이지면 즉시 중단
                if not persons_list or len(persons_list) == 0:
                    print(f"   ℹ️  페이지 {page}에 데이터 없음. 동기화 종료.\n")
                    break
                
                print(f"   ✅ 페이지 {page}: {len(persons_list)}건 데이터 수신")
                all_persons.extend(persons_list)
                result["total_fetched"] += len(persons_list)
                
                # API 부하 방지
                await asyncio.sleep(0.5)
            
            print(f"\n📊 총 {result['total_fetched']}건의 데이터 수신 완료")

            # 예상 개수와 실제 개수 비교
            if total_count > 0 and result['total_fetched'] != total_count:
                print(f"⚠️  예상 {total_count}건 vs 실제 {result['total_fetched']}건")

            # ✅ API에서 받아온 external_id 목록 수집
            api_external_ids = set()
            for item in all_persons:
                parsed = self.api_client.parse_missing_person(item)
                if parsed and parsed.get("external_id"):
                    api_external_ids.add(parsed["external_id"])

            print(f"\n🔍 API에서 받은 실종자 ID: {len(api_external_ids)}개")

            # ✅ DB에서 현재 실종 중인 사람들의 ID 가져오기
            current_missing = db.query(MissingPerson).filter(
                MissingPerson.status == "missing"
            ).all()

            current_missing_ids = {p.external_id for p in current_missing}
            print(f"📊 DB에 실종 중인 사람: {len(current_missing_ids)}명")

            # ✅ API에 없지만 DB에는 실종 중으로 있는 사람들 = 실종 해제!
            resolved_ids = current_missing_ids - api_external_ids
            result["resolved"] = len(resolved_ids)

            if resolved_ids:
                print(f"\n🎉 실종 해제 감지: {len(resolved_ids)}명")
                for person in current_missing:
                    if person.external_id in resolved_ids:
                        person.status = "resolved"
                        person.resolved_at = datetime.now()
                        person.updated_at = datetime.now()
                        print(f"   ✅ 실종 해제: {person.location_address[:40]} (ID: {person.external_id})")
                db.commit()
            else:
                print("\n📌 실종 해제된 사람 없음")

            print("\n" + "-"*60)
            print("💾 데이터베이스 저장 시작...")
            print("-"*60 + "\n")

            for idx, item in enumerate(all_persons, 1):
                try:
                    sync_result = self._sync_person(item, db)
                    
                    if sync_result == "added":
                        result["new_added"] += 1
                        if result["new_added"] <= 10:  # 처음 10개만 출력
                            print(f"✅ [{idx}/{len(all_persons)}] 새 데이터 추가: {item.get('occrAdres', 'N/A')[:40]}")
                    elif sync_result == "updated":
                        result["updated"] += 1
                        if result["updated"] <= 10:  # 처음 10개만 출력
                            print(f"🔄 [{idx}/{len(all_persons)}] 데이터 업데이트: {item.get('occrAdres', 'N/A')[:40]}")
                    elif sync_result == "skipped":
                        result["skipped"] += 1
                    
                    # 주기적으로 커밋
                    if idx % 50 == 0:
                        db.commit()
                        print(f"   💾 {idx}건 저장 완료")
                
                except Exception as e:
                    error_msg = f"데이터 저장 실패 (항목 {idx}): {str(e)}"
                    result["errors"].append(error_msg)
                    if len(result["errors"]) <= 5:  # 처음 5개만 출력
                        print(f"❌ {error_msg}")
                    continue
            
            db.commit()

            # ✅ 사진 스크랩 (옵션)
            if scrape_photos:
                print("\n" + "="*60)
                print("📸 실종자 사진 스크랩 시작")
                print("="*60 + "\n")

                try:
                    photo_result = await self._scrape_photos_for_missing_persons(
                        db,
                        max_persons=max_photo_persons
                    )
                    result["photos_scraped"] = photo_result["persons_scraped"]
                    result["total_photos"] = photo_result["total_photos"]

                except Exception as e:
                    error_msg = f"사진 스크랩 오류: {str(e)}"
                    result["errors"].append(error_msg)
                    print(f"❌ {error_msg}")
                    import traceback
                    traceback.print_exc()

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
   • 실종 해제: {result['resolved']}건 🎉
   • 건너뜀: {result['skipped']}건
   • 사진 스크랩: {result['photos_scraped']}명 (총 {result['total_photos']}장)
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
            import traceback
            traceback.print_exc()
            db.rollback()
        
        finally:
            db.close()
        
        return result
    
    def _sync_person(self, item: Dict, db: Session) -> str:
        """개별 실종자 데이터 동기화"""
        parsed = self.api_client.parse_missing_person(item)

        if not parsed or not parsed.get("external_id"):
            return "skipped"

        existing = db.query(MissingPerson).filter(
            MissingPerson.external_id == parsed["external_id"]
        ).first()

        if existing:
            # 기존 데이터 업데이트
            for key, value in parsed.items():
                setattr(existing, key, value)
            # API에 다시 나타났으므로 실종 중으로 복원
            existing.status = "missing"
            existing.resolved_at = None
            existing.updated_at = datetime.now()
            return "updated"
        else:
            # 새로운 실종자 추가
            new_person = MissingPerson(
                **parsed,
                status="missing",  # 기본값: 실종 중
                resolved_at=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(new_person)
            return "added"
    
    async def _scrape_photos_for_missing_persons(self, db: Session, max_persons: int = 100) -> Dict:
        """
        사진이 없는 실종자들의 사진 스크랩

        Args:
            db: 데이터베이스 세션
            max_persons: 최대 스크랩 인원

        Returns:
            {"persons_scraped": int, "total_photos": int}
        """
        from app.services.photo_scraper_service import PhotoScraperService

        # 사진이 없는 실종자 조회 (status가 missing인 사람만)
        # ID 순서로 정렬하여 순차적으로 처리
        persons_without_photos = db.query(MissingPerson).filter(
            MissingPerson.status == "missing",
            (MissingPerson.photo_urls.is_(None)) | (MissingPerson.photo_urls == "")
        ).order_by(MissingPerson.id).limit(max_persons).all()

        if not persons_without_photos:
            print("  ℹ️  사진이 필요한 실종자 없음\n")
            return {"persons_scraped": 0, "total_photos": 0}

        print(f"  📋 사진 스크랩 대상: {len(persons_without_photos)}명 (최대 {max_persons}명)\n")

        # 스크랩할 정보 준비
        persons_to_scrape = [
            {
                "external_id": person.external_id,
                "name": person.location_address[:20] if person.location_address else "Unknown"
            }
            for person in persons_without_photos
        ]

        # 사진 스크랩
        async with PhotoScraperService(delay=3.0, max_retries=3) as scraper:
            photo_results = await scraper.scrape_multiple_persons(persons_to_scrape)

        # DB 업데이트
        total_photos = 0
        persons_scraped = 0

        for person in persons_without_photos:
            photo_urls = photo_results.get(person.external_id, [])
            if photo_urls:
                # 쉼표로 구분해서 저장
                person.photo_urls = ",".join(photo_urls)
                person.photo_count = len(photo_urls)
                person.photos_downloaded = datetime.now()
                person.updated_at = datetime.now()

                total_photos += len(photo_urls)
                persons_scraped += 1

        db.commit()

        print(f"\n  💾 DB 업데이트 완료: {persons_scraped}명, {total_photos}장\n")

        return {
            "persons_scraped": persons_scraped,
            "total_photos": total_photos
        }

    def get_statistics(self) -> Dict:
        """현재 DB 통계 조회"""
        db = SessionLocal()
        try:
            total_count = db.query(MissingPerson).count()

            from datetime import timedelta
            recent_date = datetime.now() - timedelta(days=7)
            recent_count = db.query(MissingPerson).filter(
                MissingPerson.created_at >= recent_date
            ).count()

            geocoded_count = db.query(MissingPerson).filter(
                MissingPerson.latitude.isnot(None),
                MissingPerson.longitude.isnot(None)
            ).count()

            # 사진 통계 추가
            photos_count = db.query(MissingPerson).filter(
                MissingPerson.photo_count > 0
            ).count()

            return {
                "total_count": total_count,
                "recent_count": recent_count,
                "geocoded_count": geocoded_count,
                "geocoded_percentage": round(geocoded_count / total_count * 100, 1) if total_count > 0 else 0,
                "photos_count": photos_count,
                "photos_percentage": round(photos_count / total_count * 100, 1) if total_count > 0 else 0
            }
        finally:
            db.close()


async def run_sync(api_key: str, esntl_id: str = "10000855", max_pages: int = 50, scrape_photos: bool = False):
    """
    동기화 실행 함수

    Args:
        api_key: 안전Dream API 키
        esntl_id: 기관 ID
        max_pages: 최대 페이지 수
        scrape_photos: 사진 스크랩 여부
    """
    service = DataSyncService(api_key=api_key, esntl_id=esntl_id)
    result = await service.sync_all_data(max_pages=max_pages, scrape_photos=scrape_photos)

    stats = service.get_statistics()
    print("\n" + "="*60)
    print("📊 현재 데이터베이스 통계")
    print("="*60)
    print(f"""
   • 전체 실종자: {stats['total_count']}명
   • 최근 7일 추가: {stats['recent_count']}명
   • 위경도 변환 완료: {stats['geocoded_count']}명 ({stats['geocoded_percentage']}%)
   • 사진 보유: {stats['photos_count']}명 ({stats['photos_percentage']}%)
    """)
    print("="*60 + "\n")

    return result


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    API_KEY = os.getenv("SAFE_DREAM_API_KEY")
    ESNTL_ID = os.getenv("SAFE_DREAM_ESNTL_ID", "10000855")
    
    if not API_KEY:
        print("❌ SAFE_DREAM_API_KEY가 설정되지 않았습니다!")
        exit(1)
    
    print("🚀 SafeMap 데이터 동기화 시작...\n")
    result = asyncio.run(run_sync(api_key=API_KEY, esntl_id=ESNTL_ID, max_pages=50))
    
    if result["success"]:
        print("✅ 동기화 성공!")
    else:
        print("❌ 동기화 실패")
        for error in result["errors"]:
            print(f"   - {error}")