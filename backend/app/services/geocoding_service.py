# -*- coding: utf-8 -*-
"""
Kakao Local API를 사용한 주소 → 좌표 변환 (지오코딩) 서비스
"""

import httpx
import asyncio
from typing import Optional, Tuple, Dict
from datetime import datetime


class KakaoGeocodingService:
    """Kakao Local API를 사용한 지오코딩 서비스"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: Kakao REST API 키 (JavaScript 키 아님!)
        """
        self.api_key = api_key
        self.base_url = "https://dapi.kakao.com/v2/local/search/address.json"
        self._cache = {}  # 주소 캐시
        self._request_count = 0
        self._last_request_time = None

    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        주소를 좌표로 변환

        Args:
            address: 변환할 주소

        Returns:
            (latitude, longitude) 튜플 또는 None
        """
        if not address or not address.strip():
            return None

        address = address.strip()

        # 캐시 확인
        if address in self._cache:
            return self._cache[address]

        # API 호출 속도 제한 (초당 최대 10회)
        await self._rate_limit()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.base_url,
                    params={"query": address},
                    headers={"Authorization": f"KakaoAK {self.api_key}"}
                )

                if response.status_code != 200:
                    print(f"⚠️  지오코딩 실패 (HTTP {response.status_code}): {address[:30]}")
                    return None

                data = response.json()
                documents = data.get("documents", [])

                if not documents:
                    # 주소 검색 실패 시 키워드 검색 시도
                    return await self._geocode_by_keyword(address)

                # 첫 번째 결과 사용
                first_result = documents[0]

                # 도로명 주소 우선, 없으면 지번 주소
                if first_result.get("road_address"):
                    lon = float(first_result["road_address"]["x"])
                    lat = float(first_result["road_address"]["y"])
                elif first_result.get("address"):
                    lon = float(first_result["address"]["x"])
                    lat = float(first_result["address"]["y"])
                else:
                    return None

                result = (lat, lon)
                self._cache[address] = result
                return result

        except Exception as e:
            print(f"⚠️  지오코딩 오류: {address[:30]}, {str(e)}")
            return None

    async def _geocode_by_keyword(self, address: str) -> Optional[Tuple[float, float]]:
        """키워드 검색으로 지오코딩 시도"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://dapi.kakao.com/v2/local/search/keyword.json",
                    params={"query": address},
                    headers={"Authorization": f"KakaoAK {self.api_key}"}
                )

                if response.status_code != 200:
                    return None

                data = response.json()
                documents = data.get("documents", [])

                if not documents:
                    return None

                # 첫 번째 결과 사용
                first_result = documents[0]
                lon = float(first_result.get("x"))
                lat = float(first_result.get("y"))

                result = (lat, lon)
                self._cache[address] = result
                return result

        except Exception as e:
            return None

    async def _rate_limit(self):
        """API 호출 속도 제한 (초당 최대 10회)"""
        current_time = datetime.now()

        if self._last_request_time:
            time_diff = (current_time - self._last_request_time).total_seconds()

            # 같은 초 내에 10번 이상 요청하면 대기
            if time_diff < 1.0:
                self._request_count += 1
                if self._request_count >= 10:
                    await asyncio.sleep(1.0 - time_diff)
                    self._request_count = 0
            else:
                self._request_count = 0

        self._last_request_time = datetime.now()

    async def geocode_batch(
        self,
        addresses: list,
        show_progress: bool = True
    ) -> Dict[str, Optional[Tuple[float, float]]]:
        """
        여러 주소를 일괄 변환

        Args:
            addresses: 변환할 주소 리스트
            show_progress: 진행 상황 출력 여부

        Returns:
            {address: (lat, lon)} 딕셔너리
        """
        results = {}
        total = len(addresses)

        for idx, address in enumerate(addresses, 1):
            if show_progress and idx % 10 == 0:
                print(f"🗺️  지오코딩 진행: {idx}/{total} ({idx/total*100:.1f}%)")

            result = await self.geocode_address(address)
            results[address] = result

            # API 부하 방지
            if idx % 50 == 0:
                await asyncio.sleep(1.0)

        if show_progress:
            success_count = sum(1 for v in results.values() if v is not None)
            print(f"✅ 지오코딩 완료: {success_count}/{total} ({success_count/total*100:.1f}%)")

        return results

    def get_cache_stats(self) -> Dict:
        """캐시 통계 반환"""
        return {
            "cached_addresses": len(self._cache),
            "total_requests": self._request_count
        }


# 싱글톤 인스턴스
_geocoding_service = None


def get_geocoding_service(api_key: str) -> KakaoGeocodingService:
    """지오코딩 서비스 인스턴스 반환"""
    global _geocoding_service
    if _geocoding_service is None or _geocoding_service.api_key != api_key:
        _geocoding_service = KakaoGeocodingService(api_key)
    return _geocoding_service
