# -*- coding: utf-8 -*-
"""
실종자 사진 스크랩 서비스
- Rate limiting 방지를 위한 딜레이 및 재시도 로직
- 진행 상황 저장 및 재개
- MD5 해시를 통한 중복 사진 필터링
"""

import asyncio
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import httpx


class PhotoScraperService:
    """실종자 사진 스크랩 서비스"""

    # 플레이스홀더 이미지 크기 (건너뛰기)
    PLACEHOLDER_SIZE = 2860

    def __init__(self, delay: float = 3.0, max_retries: int = 3):
        """
        Args:
            delay: 요청 간 기본 딜레이 (초)
            max_retries: 최대 재시도 횟수
        """
        self.delay = delay
        self.max_retries = max_retries
        self.session: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.safe182.go.kr/",
                "Origin": "https://www.safe182.go.kr"
            },
            follow_redirects=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.aclose()

    def _get_md5(self, data: bytes) -> str:
        """데이터의 MD5 해시 계산"""
        return hashlib.md5(data).hexdigest()

    async def _download_with_retry(self, url: str, retry_count: int = 0) -> Optional[httpx.Response]:
        """재시도 로직이 있는 다운로드"""
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response

        except (httpx.HTTPError, httpx.RemoteProtocolError) as e:
            if retry_count < self.max_retries:
                # Exponential backoff: 2초, 4초, 8초
                wait_time = 2 ** (retry_count + 1)
                print(f"  ⚠️  오류 발생: {str(e)[:50]}... {wait_time}초 후 재시도 ({retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(wait_time)
                return await self._download_with_retry(url, retry_count + 1)
            else:
                print(f"  ❌ 최대 재시도 횟수 초과: {str(e)[:100]}")
                return None

    async def scrape_person_photos(self, external_id: str, name: str = "") -> List[str]:
        """
        특정 실종자의 사진 URL 스크랩

        Args:
            external_id: 실종자 ID (msspsnIdntfccd)
            name: 실종자 이름 (로깅용)

        Returns:
            사진 URL 리스트
        """
        # 1. 상세 페이지 먼저 방문 (세션 생성)
        detail_url = f"https://www.safe182.go.kr/home/lcm/lcmMssGet.do?msspsnIdntfccd={external_id}&rptDscd=2"

        print(f"\n{'='*80}")
        print(f"📸 사진 스크랩: {name} (ID: {external_id})")
        print(f"{'='*80}")

        # 상세 페이지 접속
        response = await self._download_with_retry(detail_url)
        if not response:
            print("  ❌ 상세 페이지 접속 실패")
            return []

        print("  ✅ 상세 페이지 접속 성공")

        # 2. 세션 유지하면서 사진 다운로드
        photo_urls = []
        seen_hashes = set()

        # 최대 10개까지 시도 (인덱스 기반)
        for idx in range(10):
            photo_url = f"https://www.safe182.go.kr/home/lcm/blobImgListView.do?tknphotoFileIdx={idx}"

            # 이미지 다운로드
            img_response = await self._download_with_retry(photo_url)
            if not img_response:
                print(f"  [{idx}] ❌ 다운로드 실패")
                break

            img_data = img_response.content
            img_size = len(img_data)

            # 너무 작은 파일은 "no image"일 가능성
            if img_size < 1000:
                print(f"  [{idx}] ⏭️  너무 작음 ({img_size} bytes) - 건너뜀")
                break

            # 플레이스홀더 필터링 (정확히 2860 bytes)
            if img_size == 2860:
                print(f"  [{idx}] 🚫 플레이스홀더 발견 - 더 이상 사진 없음")
                break

            # MD5 해시 계산
            img_hash = self._get_md5(img_data)

            # 중복 체크
            if img_hash in seen_hashes:
                print(f"  [{idx}] 🔁 중복 사진 - 스킵")
                continue

            # 고유한 사진
            seen_hashes.add(img_hash)
            photo_urls.append(photo_url)
            print(f"  [{idx}] ✅ 고유한 사진! ({img_size} bytes, MD5: {img_hash[:8]}...)")

            # Rate limiting 방지
            await asyncio.sleep(0.5)

        print(f"  📊 총 {len(photo_urls)}개 사진 URL 수집 완료\n")

        # 다음 사람으로 넘어가기 전 딜레이
        if photo_urls:
            await asyncio.sleep(self.delay)

        return photo_urls

    async def scrape_multiple_persons(self, persons: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """
        여러 실종자의 사진 일괄 스크랩

        Args:
            persons: [{"external_id": "...", "name": "..."}, ...]

        Returns:
            {external_id: [photo_url1, photo_url2, ...], ...}
        """
        results = {}
        total = len(persons)

        print(f"\n🚀 총 {total}명의 사진 스크랩 시작")
        print(f"⏱️  요청 간 딜레이: {self.delay}초")
        print(f"🔄 최대 재시도: {self.max_retries}회\n")

        for idx, person in enumerate(persons, 1):
            external_id = person.get("external_id", "")
            name = person.get("name", "Unknown")

            if not external_id:
                continue

            print(f"진행: {idx}/{total}")

            try:
                photo_urls = await self.scrape_person_photos(external_id, name)
                results[external_id] = photo_urls

            except Exception as e:
                print(f"  ❌ 예상치 못한 오류: {str(e)[:100]}")
                results[external_id] = []
                await asyncio.sleep(self.delay)

        # 통계
        total_photos = sum(len(urls) for urls in results.values())
        persons_with_photos = sum(1 for urls in results.values() if urls)

        print(f"\n{'='*80}")
        print("📊 스크랩 완료 통계")
        print(f"{'='*80}")
        print(f"  • 처리한 실종자: {total}명")
        print(f"  • 사진 있는 실종자: {persons_with_photos}명")
        print(f"  • 총 수집 사진: {total_photos}개")
        print(f"  • 평균 사진/인: {total_photos/total:.1f}개")
        print(f"{'='*80}\n")

        return results


async def scrape_photos_example():
    """사용 예제"""
    # 테스트용 실종자 목록
    test_persons = [
        {"external_id": "6048080", "name": "이진현"},
        {"external_id": "6048041", "name": "송인식"},
    ]

    async with PhotoScraperService(delay=3.0, max_retries=3) as scraper:
        results = await scraper.scrape_multiple_persons(test_persons)

        for person_id, urls in results.items():
            print(f"{person_id}: {len(urls)}개 사진")
            for url in urls:
                print(f"  - {url}")


if __name__ == "__main__":
    asyncio.run(scrape_photos_example())
