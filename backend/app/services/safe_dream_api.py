import httpx
from typing import List, Dict, Optional
from datetime import datetime
from app.config import settings


class SafeDreamAPIService:
    """안전Dream OPEN API 연동 서비스"""
    
    def __init__(self):
        self.base_url = settings.safe_dream_base_url
        self.api_key = settings.safe_dream_api_key
        
    async def get_missing_alerts(self, limit: int = 100) -> List[Dict]:
        """
        실종경보 정보 조회
        
        Args:
            limit: 조회할 최대 건수
            
        Returns:
            실종경보 데이터 리스트
        """
        url = f"{self.base_url}/home/api/missingAlert.do"
        
        params = {
            "authKey": self.api_key,
            "rowSize": limit
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # API 응답 파싱
                if data.get("result") == "SUCCESS":
                    return data.get("list", [])
                else:
                    print(f"API Error: {data.get('message', 'Unknown error')}")
                    return []
                    
        except httpx.HTTPError as e:
            print(f"HTTP Error: {e}")
            return []
        except Exception as e:
            print(f"Error fetching missing alerts: {e}")
            return []
    
    async def search_missing_persons(
        self, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        gender: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[Dict]:
        """
        실종자 검색
        
        Args:
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            age_min: 최소 나이
            age_max: 최대 나이
            gender: 성별 (M/F)
            location: 실종 지역
            
        Returns:
            실종자 데이터 리스트
        """
        url = f"{self.base_url}/home/api/missingSearch.do"
        
        params = {
            "authKey": self.api_key
        }
        
        # 선택적 파라미터 추가
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if age_min:
            params["ageMin"] = age_min
        if age_max:
            params["ageMax"] = age_max
        if gender:
            params["gender"] = gender
        if location:
            params["location"] = location
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("result") == "SUCCESS":
                    return data.get("list", [])
                else:
                    print(f"API Error: {data.get('message', 'Unknown error')}")
                    return []
                    
        except httpx.HTTPError as e:
            print(f"HTTP Error: {e}")
            return []
        except Exception as e:
            print(f"Error searching missing persons: {e}")
            return []
    
    async def get_safety_facilities(
        self, 
        facility_type: Optional[str] = None,
        region: Optional[str] = None
    ) -> List[Dict]:
        """
        안전지도 시설 정보 조회
        
        Args:
            facility_type: 시설 유형
            region: 지역
            
        Returns:
            안전시설 데이터 리스트
        """
        url = f"{self.base_url}/home/api/safetyMap.do"
        
        params = {
            "authKey": self.api_key
        }
        
        if facility_type:
            params["type"] = facility_type
        if region:
            params["region"] = region
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("result") == "SUCCESS":
                    return data.get("list", [])
                else:
                    print(f"API Error: {data.get('message', 'Unknown error')}")
                    return []
                    
        except httpx.HTTPError as e:
            print(f"HTTP Error: {e}")
            return []
        except Exception as e:
            print(f"Error fetching safety facilities: {e}")
            return []
    
    def parse_missing_person_data(self, raw_data: Dict) -> Dict:
        """
        안전Dream API 응답을 표준 형식으로 변환
        
        Args:
            raw_data: API 원본 데이터
            
        Returns:
            표준화된 실종자 데이터
        """
        try:
            return {
                "name": raw_data.get("nm", "비공개"),
                "age": raw_data.get("age"),
                "gender": raw_data.get("sex"),
                "missing_date": raw_data.get("occrde"),
                "location_address": raw_data.get("occrAdres"),
                "location_detail": raw_data.get("occrDtl"),
                "height": raw_data.get("height"),
                "weight": raw_data.get("weight"),
                "clothing": raw_data.get("dressing"),
                "features": raw_data.get("chartor"),
                "case_number": raw_data.get("caseNo"),
                "status": raw_data.get("status", "missing")
            }
        except Exception as e:
            print(f"Error parsing data: {e}")
            return {}


# 싱글톤 인스턴스
safe_dream_service = SafeDreamAPIService()
