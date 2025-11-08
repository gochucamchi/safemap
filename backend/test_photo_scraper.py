#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사진 스크랩 테스트 스크립트

사용법:
    python3 test_photo_scraper.py
"""

import asyncio
from app.services.photo_scraper_service import PhotoScraperService


async def main():
    """메인 실행 함수"""

    print("=" * 80)
    print("📸 실종자 사진 스크랩 테스트")
    print("=" * 80)

    # 테스트할 실종자 목록 (external_id와 이름)
    persons = [
        {"external_id": "6048080", "name": "이진현"},
        {"external_id": "6048041", "name": "송인식"},
        {"external_id": "6048018", "name": "이종남"},
        {"external_id": "6048013", "name": "송재호"},
        {"external_id": "6047806", "name": "함금자"},
    ]

    print(f"\n📋 스크랩 대상: {len(persons)}명")
    print("⏱️  딜레이: 3초 (rate limiting 방지)")
    print("🔄 최대 재시도: 3회\n")

    # PhotoScraperService 실행
    async with PhotoScraperService(delay=3.0, max_retries=3) as scraper:
        results = await scraper.scrape_multiple_persons(persons)

    # 결과 출력
    print("\n" + "=" * 80)
    print("📊 스크랩 결과")
    print("=" * 80)

    for person in persons:
        person_id = person["external_id"]
        name = person["name"]
        urls = results.get(person_id, [])

        print(f"\n👤 {name} (ID: {person_id})")
        print(f"   📸 사진: {len(urls)}개")

        if urls:
            for idx, url in enumerate(urls, 1):
                print(f"   [{idx}] {url}")
        else:
            print("   ❌ 사진 없음")

    # 전체 통계
    total_photos = sum(len(urls) for urls in results.values())
    persons_with_photos = sum(1 for urls in results.values() if urls)

    print("\n" + "=" * 80)
    print("✅ 완료!")
    print(f"   • 처리한 실종자: {len(persons)}명")
    print(f"   • 사진 있는 실종자: {persons_with_photos}명")
    print(f"   • 총 수집 사진: {total_photos}개")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # 비동기 함수 실행
    asyncio.run(main())
