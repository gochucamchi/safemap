import httpx
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlencode

class SafeDreamAPI:
    """안전Dream API 클라이언트 - 실종검색 API"""
    
    def __init__(self, api_key: str, esntl_id: str = None):
        self.api_key = api_key
        # esntl_id가 없으면 환경변수에서 가져오기
        self.esntl_id = esntl_id or "10000855"  # 실제 발급 ID
        self.base_url = "https://www.safe182.go.kr/api/lcm/findChildList.do"
    
    async def get_missing_children(
        self, 
        row_size: int = 100,
        page_num: int = 1,
        writng_trget_dscds: List[str] = None
    ) -> Dict:
        """
        실종아동 목록 조회
        
        Args:
            row_size: 한 페이지 결과 수
            page_num: 페이지 번호
            writng_trget_dscds: 대상구분 코드 리스트
                - "010": 아동
                - "060": 지적장애
                - "070": 치매
            
        Returns:
            {
                "result": "성공/실패",
                "msg": "메시지",
                "totalCount": 총개수,
                "list": [...]
            }
        """
        # 기본 대상구분: 아동, 지적장애, 치매
        if writng_trget_dscds is None:
            writng_trget_dscds = ["010", "060", "070"]
        
        # POST body 파라미터 생성
        params = {
            "esntlId": self.esntl_id,
            "authKey": self.api_key,
            "rowSize": str(row_size),
            "page": str(page_num),
            "sexdstnDscd": "",  # 성별 (비우면 전체)
            "nm": "",  # 성명 (비우면 전체)
            "detailDate1": "",  # 시작일
            "detailDate2": "",  # 종료일
            "age1": "",  # 최소 나이
            "age2": "",  # 최대 나이
            "etcSpfeatr": "",  # 기타 특징
            "occrAdres": "",  # 발생주소
            "xmlUseYN": "",  # 비우면 JSON
        }
        
        # writngTrgetDscds 배열 처리
        body_parts = [urlencode(params)]
        for dscd in writng_trget_dscds:
            body_parts.append(f"writngTrgetDscds={dscd}")
        
        body = "&".join(body_parts)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"🔍 요청 URL: {self.base_url}")
                print(f"🔍 요청 Body: {body}")

                # 등록된 URL에서 오는 것처럼 헤더 추가
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Referer": "https://nightmarish-vampire-pqxqw7gv7v7hrq7p-8000.app.github.dev/",
                    "Origin": "https://nightmarish-vampire-pqxqw7gv7v7hrq7p-8000.app.github.dev",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                response = await client.post(
                    self.base_url,
                    content=body,
                    headers=headers
                )
                
                print(f"🔍 응답 상태: {response.status_code}")
                print(f"🔍 응답 내용: {response.text[:1000]}")
                
                if response.status_code != 200:
                    return {
                        "result": "실패", 
                        "msg": f"HTTP {response.status_code}: {response.text[:200]}", 
                        "totalCount": 0, 
                        "list": []
                    }
                
                data = response.json()
                return data
                
        except httpx.HTTPError as e:
            print(f"❌ API 호출 실패: {e}")
            return {"result": "실패", "msg": str(e), "totalCount": 0, "list": []}
        except Exception as e:
            print(f"❌ 데이터 처리 실패: {e}")
            return {"result": "실패", "msg": str(e), "totalCount": 0, "list": []}
    
    def parse_missing_person(self, item: Dict) -> Optional[Dict]:
        """
        API 응답을 데이터베이스 모델로 변환
        
        Args:
            item: API 응답의 list 항목
            {
                "occrde": "20241020",  # 발생일시
                "age": "7",  # 당시나이
                "ageNow": "8",  # 현재나이
                "sexdstnDscd": "남자",  # 성별
                "occrAdres": "서울특별시 강남구",  # 발생장소
                "nm": "홍길동",  # 성명
                "writngTrgetDscd": "아동",  # 대상구분
                "alldressingDscd": "청바지, 흰색 티셔츠",  # 착의사항
                "msspsnIdntfccd": "M202410200001"  # 실종자식별코드
            }
        
        Returns:
            변환된 딕셔너리 또는 None
        """
        try:
            return {
                "external_id": item.get("msspsnIdntfccd", ""),  # 실종자식별코드
                "missing_date": self._parse_date(item.get("occrde")),  # 발생일시
                "location_address": item.get("occrAdres", ""),  # 발생장소
                "location_detail": item.get("alldressingDscd", ""),  # 착의사항 (상세정보로 활용)
                "age": self._parse_age(item.get("age")),  # 당시나이
                "gender": self._parse_gender(item.get("sexdstnDscd")),  # 성별
                "latitude": None,  # API에서 제공 안 함
                "longitude": None,  # API에서 제공 안 함
            }
        except Exception as e:
            print(f"⚠️ 데이터 파싱 실패: {e}, item: {item}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """날짜 문자열 파싱 (YYYYMMDD 형식)"""
        if not date_str:
            return None
        try:
            if len(date_str) == 8:
                return datetime.strptime(date_str, "%Y%m%d")
            return datetime.fromisoformat(date_str)
        except Exception as e:
            print(f"⚠️ 날짜 파싱 실패: {date_str}, {e}")
            return None
    
    def _parse_age(self, age_str: str) -> Optional[int]:
        """나이 파싱"""
        try:
            return int(age_str) if age_str else None
        except:
            return None
    
    def _parse_gender(self, gender_str: str) -> Optional[str]:
        """성별 파싱 (M/F)"""
        if not gender_str:
            return None
        if "남" in gender_str:
            return "M"
        elif "여" in gender_str:
            return "F"
        return None


# 싱글톤 인스턴스
safe_dream_service = None

def get_safe_dream_service(api_key: str) -> SafeDreamAPI:
    """SafeDream API 서비스 인스턴스 반환"""
    global safe_dream_service
    if safe_dream_service is None:
        safe_dream_service = SafeDreamAPI(api_key)
    return safe_dream_service
