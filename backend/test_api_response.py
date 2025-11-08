#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 응답 테스트 - 사진 필드가 제대로 나오는지 확인
"""

import requests
import json

# API 베이스 URL
BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🧪 SafeMap API 테스트 - 사진 필드 확인")
print("=" * 80)

# 1. 실종자 목록 조회 (사진 필드 포함되는지 확인)
print("\n1️⃣ 실종자 목록 조회 테스트")
print("-" * 80)

try:
    response = requests.get(f"{BASE_URL}/api/v1/missing-persons?limit=3")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 응답 성공 (총 {data['total']}건)")

        if data['items']:
            print("\n📋 첫 번째 실종자 정보:")
            first_person = data['items'][0]

            # 주요 필드 출력
            print(f"  • ID: {first_person.get('id')}")
            print(f"  • External ID: {first_person.get('external_id')}")
            print(f"  • 위치: {first_person.get('location_address', 'N/A')}")
            print(f"  • 상태: {first_person.get('status')}")

            # 사진 필드 확인 (중요!)
            print(f"\n  🖼️  사진 필드:")
            print(f"  • photo_urls: {first_person.get('photo_urls', [])}")
            print(f"  • photo_count: {first_person.get('photo_count', 0)}")

            # 전체 JSON 출력
            print(f"\n  📄 전체 JSON:")
            print(json.dumps(first_person, indent=2, ensure_ascii=False))
        else:
            print("⚠️  데이터가 없습니다.")
    else:
        print(f"❌ 응답 실패: HTTP {response.status_code}")

except requests.exceptions.ConnectionError:
    print("❌ 연결 실패: 서버가 실행 중인지 확인하세요")
    print("   실행 방법: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

# 2. DB 통계 조회 (사진 통계 포함되는지 확인)
print("\n\n2️⃣ DB 통계 조회 테스트")
print("-" * 80)

try:
    response = requests.get(f"{BASE_URL}/api/v1/db/stats")

    if response.status_code == 200:
        stats = response.json()
        print("✅ 응답 성공")
        print(f"\n📊 DB 통계:")
        print(f"  • 전체 실종자: {stats.get('total_count', 0)}명")
        print(f"  • 위경도 변환: {stats.get('geocoded_count', 0)}명 ({stats.get('geocoded_percentage', 0)}%)")

        # 사진 통계 확인 (중요!)
        print(f"  • 사진 보유: {stats.get('photos_count', 0)}명 ({stats.get('photos_percentage', 0)}%)")

        # 전체 JSON 출력
        print(f"\n  📄 전체 JSON:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        print(f"❌ 응답 실패: HTTP {response.status_code}")

except requests.exceptions.ConnectionError:
    print("❌ 연결 실패: 서버가 실행 중인지 확인하세요")

# 3. Swagger UI 안내
print("\n\n3️⃣ Swagger UI에서 직접 확인하기")
print("-" * 80)
print("브라우저에서 다음 URL을 열어보세요:")
print(f"  📍 {BASE_URL}/docs")
print("\n확인할 엔드포인트:")
print("  • GET /api/v1/missing-persons - 실종자 목록 (photo_urls, photo_count 필드 확인)")
print("  • GET /api/v1/db/stats - DB 통계 (photos_count, photos_percentage 필드 확인)")
print("  • POST /api/v1/sync/missing-persons - 데이터 동기화 (scrape_photos 파라미터 확인)")

print("\n" + "=" * 80)
print("✅ 테스트 완료!")
print("=" * 80)
