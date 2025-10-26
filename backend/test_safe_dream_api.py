#!/usr/bin/env python3
"""
SafeMap API 테스트 스크립트
"""
import asyncio
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

from app.services.safe_dream_api import SafeDreamAPI

async def test_api():
    """API 테스트"""
    api_key = os.getenv("SAFE_DREAM_API_KEY")
    if not api_key:
        print("❌ API 키가 설정되지 않았습니다")
        return
    
    print(f"🔑 API 키: {api_key}")
    print("📡 API 호출 중...")
    
    service = SafeDreamAPI(api_key)
    response = await service.get_missing_children(row_size=10, page_num=1)
    
    print(f"\n📊 응답 결과:")
    print(f"  - result: {response.get('result')}")
    print(f"  - msg: {response.get('msg')}")
    print(f"  - totalCount: {response.get('totalCount')}")
    print(f"  - list 개수: {len(response.get('list', []))}")
    
    if response.get('list'):
        print(f"\n첫 번째 데이터:")
        first_item = response['list'][0]
        for key, value in first_item.items():
            print(f"  - {key}: {value}")
        
        print(f"\n파싱된 데이터:")
        parsed = service.parse_missing_person(first_item)
        for key, value in parsed.items():
            print(f"  - {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_api())
