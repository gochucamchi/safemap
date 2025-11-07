# -*- coding: utf-8 -*-
"""
안전Dream API 클라이언트 (수정 버전)
- API 응답 형식 수정
"""

import httpx
import json
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlencode


class SafeDreamAPI:
    """안전Dream API 클라이언트"""
    
    def __init__(self, api_key: str, esntl_id: str = None):
        self.api_key = api_key
        self.esntl_id = esntl_id or "10000855"
        self.base_url = "https://www.safe182.go.kr/api/lcm/findChildList.do"
    
    async def get_missing_children(
        self, 
        row_size: int = 100,
        page_num: int = 1,
        writng_trget_dscds: List[str] = None
    ) -> Dict:
        """실종아동 목록 조회"""
        if writng_trget_dscds is None:
            writng_trget_dscds = ["010", "060", "070"]
        
        params = {
            "esntlId": self.esntl_id,
            "authKey": self.api_key,
            "rowSize": str(row_size),
            "page": str(page_num),
            "sexdstnDscd": "",
            "nm": "",
            "detailDate1": "",
            "detailDate2": "",
            "age1": "",
            "age2": "",
            "etcSpfeatr": "",
            "occrAdres": "",
            "xmlUseYN": "",
        }
        
        body_parts = [urlencode(params)]
        for dscd in writng_trget_dscds:
            body_parts.append(f"writngTrgetDscds={dscd}")
        
        body = "&".join(body_parts)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"🔍 요청 URL: {self.base_url}")
                
                response = await client.post(
                    self.base_url,
                    content=body,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                    }
                )
                
                print(f"🔍 응답 상태: {response.status_code}")
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "msg": f"HTTP {response.status_code}", 
                        "totalCount": 0, 
                        "list": []
                    }
                
                data = response.json()
                
                # ✅ 안전Dream API는 totalCount와 list만 반환
                # result 필드가 없어도 정상!
                if "totalCount" in data and "list" in data:
                    data["success"] = True
                    data["msg"] = "성공"
                else:
                    data["success"] = False
                    data["msg"] = "응답 형식 오류"
                    data["totalCount"] = 0
                    data["list"] = []
                
                return data
                
        except httpx.HTTPError as e:
            print(f"❌ API 호출 실패: {e}")
            return {"success": False, "msg": str(e), "totalCount": 0, "list": []}
        except Exception as e:
            print(f"❌ 데이터 처리 실패: {e}")
            return {"success": False, "msg": str(e), "totalCount": 0, "list": []}
    
    def parse_missing_person(self, item: Dict) -> Optional[Dict]:
        """API 응답을 데이터베이스 모델로 변환"""
        try:
            # 사진 URLs (여러 필드에서 수집)
            photo_urls = []

            # 다양한 사진 필드 체크
            photo_fields = [
                "imageURL",           # 기본 이미지
                "writPhotoUrl",       # 작성 사진
                "etcPhotoUrl",        # 기타 사진
                "photoUrl",           # 사진 URL
                "imageUrl1",          # 이미지 1
                "imageUrl2",          # 이미지 2
                "imageUrl3",          # 이미지 3
            ]

            for field in photo_fields:
                url = item.get(field)
                if url and url not in photo_urls:  # 중복 제거
                    # URL이 상대 경로인 경우 전체 URL로 변환
                    if url.startswith('/'):
                        url = f"https://www.safe182.go.kr{url}"
                    elif not url.startswith('http'):
                        url = f"https://www.safe182.go.kr/{url}"
                    photo_urls.append(url)

            return {
                "external_id": str(item.get("msspsnIdntfccd", "")),
                "name": item.get("nm", ""),  # 이름
                "missing_date": self._parse_date(item.get("occrde")),  # 발생일시
                "age_at_disappearance": self._parse_age(item.get("age")),  # 실종 당시 나이
                "gender": self._parse_gender(item.get("sexdstnDscd")),  # 성별
                "nationality": item.get("ntltyDscd", "대한민국"),  # 국적

                # 위치 정보
                "location_address": item.get("occrAdres", ""),  # 발생장소
                "location_detail": item.get("occrDetailadres", ""),  # 발생장소 상세
                "latitude": None,  # 지오코딩으로 채워짐
                "longitude": None,  # 지오코딩으로 채워짐
                "geocoding_status": "pending",  # 초기 상태

                # 신체 특징
                "height": self._parse_number(item.get("tllCm")),  # 키
                "weight": self._parse_number(item.get("wghtKg")),  # 몸무게
                "body_type": item.get("bdTypeDscd", ""),  # 체격
                "face_shape": item.get("faceShpDscd", ""),  # 얼굴형
                "hair_color": item.get("hfclrDscd", ""),  # 두발색상
                "hair_style": item.get("hfstlDscd", ""),  # 두발형태

                # 착의사항
                "clothing_description": item.get("alldressingDscd", ""),  # 착의의상

                # 사진 (JSON 배열로 저장)
                "photo_urls": json.dumps(photo_urls, ensure_ascii=False) if photo_urls else None,

                # 기타 특징
                "special_features": item.get("etcSpfeatr", ""),  # 기타 특이사항
            }
        except Exception as e:
            print(f"⚠️ 데이터 파싱 실패: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """날짜 문자열 파싱"""
        if not date_str:
            return None
        try:
            if len(str(date_str)) == 8:
                return datetime.strptime(str(date_str), "%Y%m%d")
            return datetime.fromisoformat(str(date_str))
        except Exception as e:
            print(f"⚠️ 날짜 파싱 실패: {date_str}, {e}")
            return None
    
    def _parse_age(self, age_str) -> Optional[int]:
        """나이 파싱"""
        try:
            return int(age_str) if age_str else None
        except:
            return None
    
    def _parse_gender(self, gender_str: str) -> Optional[str]:
        """성별 파싱"""
        if not gender_str:
            return None
        if "남" in str(gender_str):
            return "M"
        elif "여" in str(gender_str):
            return "F"
        return None

    def _parse_number(self, number_str) -> Optional[int]:
        """숫자 파싱 (키, 몸무게 등)"""
        try:
            return int(number_str) if number_str else None
        except:
            return None


# 싱글톤 인스턴스
safe_dream_service = None


def get_safe_dream_service(api_key: str) -> SafeDreamAPI:
    """SafeDream API 서비스 인스턴스 반환"""
    global safe_dream_service
    if safe_dream_service is None:
        safe_dream_service = SafeDreamAPI(api_key)
    return safe_dream_service