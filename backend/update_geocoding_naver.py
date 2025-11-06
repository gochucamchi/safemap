#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Naver Geocoding API를 사용하여 기존 데이터베이스의 주소를 좌표로 변환하는 스크립트
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from app.database.db import SessionLocal
from app.models.missing_person import MissingPerson
from app.services.naver_geocoding_service import NaverGeocodingService
from datetime import datetime
import os
from dotenv import load_dotenv


async def update_all_locations(naver_client_id: str, naver_client_secret: str):
    """모든 실종자 데이터의 위치 정보 업데이트"""

    print("\n" + "="*60)
    print("🗺️  Naver Geocoding 서비스 시작")
    print("="*60 + "\n")

    db = SessionLocal()
    geocoding_service = NaverGeocodingService(naver_client_id, naver_client_secret)

    try:
        # 위치 정보가 없는 실종자 데이터 조회
        missing_persons = db.query(MissingPerson).filter(
            MissingPerson.latitude.is_(None),
            MissingPerson.location_address.isnot(None)
        ).all()

        total = len(missing_persons)
        print(f"📊 위치 정보가 없는 데이터: {total}건")

        if total == 0:
            print("✅ 모든 데이터에 위치 정보가 있습니다!")
            return

        print(f"🚀 지오코딩 시작...\n")

        success_count = 0
        failed_count = 0

        for idx, person in enumerate(missing_persons, 1):
            address = person.location_address.strip() if person.location_address else None

            if not address:
                continue

            # 진행 상황 출력 (10개마다)
            if idx % 10 == 0:
                print(f"📍 진행: {idx}/{total} ({idx/total*100:.1f}%) - "
                      f"성공: {success_count}, 실패: {failed_count}")

            # 지오코딩 시도
            result = await geocoding_service.geocode_address(address)

            if result:
                lat, lon = result
                person.latitude = lat
                person.longitude = lon
                person.updated_at = datetime.now()
                success_count += 1

                # 처음 5개만 상세 출력
                if success_count <= 5:
                    print(f"   ✅ {address[:40]} → ({lat:.6f}, {lon:.6f})")
            else:
                failed_count += 1

                # 처음 5개 실패만 출력
                if failed_count <= 5:
                    print(f"   ❌ {address[:40]} → 변환 실패")

            # 50개마다 커밋
            if idx % 50 == 0:
                db.commit()
                print(f"   💾 {idx}건 저장 완료")
                await asyncio.sleep(1.0)  # API 부하 방지

        # 최종 커밋
        db.commit()

        print("\n" + "="*60)
        print("✅ 지오코딩 완료!")
        print("="*60)
        print(f"""
📊 결과:
   • 전체 처리: {total}건
   • 성공: {success_count}건 ({success_count/total*100:.1f}%)
   • 실패: {failed_count}건 ({failed_count/total*100:.1f}%)
        """)

        # 캐시 통계
        cache_stats = geocoding_service.get_cache_stats()
        print(f"💾 캐시된 주소: {cache_stats['cached_addresses']}개")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    load_dotenv()

    # Naver Cloud Platform 인증 정보
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("❌ Naver API 인증 정보가 설정되지 않았습니다!")
        print("""
.env 파일에 다음을 추가해주세요:

NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret

발급 방법:
1. https://console.ncloud.com/ 로그인
2. Services → AI·NAVER API → Maps → Geocoding
3. 애플리케이션 등록
4. Client ID와 Client Secret 복사
        """)
        sys.exit(1)

    print("🚀 SafeMap Naver 지오코딩 업데이트 시작...\n")
    asyncio.run(update_all_locations(NAVER_CLIENT_ID, NAVER_CLIENT_SECRET))
