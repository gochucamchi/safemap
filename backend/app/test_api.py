#!/usr/bin/env python3
"""
SafeMap Backend API 테스트 스크립트
서버가 실행 중일 때 이 스크립트를 실행하여 API를 테스트할 수 있습니다.
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"


def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_root():
    """루트 엔드포인트 테스트"""
    print_section("1. 루트 엔드포인트 테스트")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_api_info():
    """API 정보 테스트"""
    print_section("2. API 정보 조회")
    
    response = requests.get(f"{BASE_URL}/api/info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_health():
    """헬스 체크 테스트"""
    print_section("3. 헬스 체크")
    
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_missing_persons():
    """실종자 목록 조회 테스트"""
    print_section("4. 실종자 목록 조회")
    
    # 기본 조회
    print("📋 전체 조회 (limit=5)")
    response = requests.get(f"{BASE_URL}/api/v1/missing-persons?limit=5")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"조회된 레코드 수: {len(data)}")
    if data:
        print(f"첫 번째 레코드: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
    else:
        print("데이터가 없습니다. 먼저 /api/v1/sync/missing-persons를 호출하여 데이터를 동기화하세요.")
    
    # 날짜 필터링
    print("\n📅 날짜 필터링 (최근 30일)")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    response = requests.get(
        f"{BASE_URL}/api/v1/missing-persons",
        params={
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "limit": 5
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"조회된 레코드 수: {len(response.json())}")


def test_statistics():
    """통계 조회 테스트"""
    print_section("5. 실종 사건 통계")
    
    response = requests.get(f"{BASE_URL}/api/v1/missing-persons/stats?days=30")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_safety_facilities():
    """안전시설 조회 테스트"""
    print_section("6. 안전시설 목록 조회")
    
    response = requests.get(f"{BASE_URL}/api/v1/safety-facilities?limit=5")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"조회된 레코드 수: {len(data)}")
    if data:
        print(f"첫 번째 시설: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
    else:
        print("안전시설 데이터가 없습니다.")


def test_sync():
    """데이터 동기화 테스트"""
    print_section("7. 안전Dream API 데이터 동기화")
    
    print("⚠️  주의: 이 작업은 실제 API를 호출하며 시간이 걸릴 수 있습니다.")
    print("API 키가 설정되어 있어야 합니다.")
    
    user_input = input("\n계속하시겠습니까? (y/N): ")
    
    if user_input.lower() == 'y':
        print("\n🔄 동기화 시작...")
        try:
            response = requests.post(f"{BASE_URL}/api/v1/sync/missing-persons", timeout=60)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except requests.exceptions.Timeout:
            print("❌ 타임아웃: 요청 시간이 너무 오래 걸립니다.")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
    else:
        print("동기화를 건너뜁니다.")


def main():
    """메인 함수"""
    print("\n" + "🚀 SafeMap Backend API 테스트 시작 " + "\n")
    print(f"Base URL: {BASE_URL}")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 서버 연결 확인
        requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ 서버 연결 성공\n")
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
        print("서버가 실행 중인지 확인하세요: uvicorn app.main:app --reload")
        return
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return
    
    # 테스트 실행
    try:
        test_root()
        test_api_info()
        test_health()
        test_missing_persons()
        test_statistics()
        test_safety_facilities()
        test_sync()
        
        print_section("✅ 모든 테스트 완료")
        print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  테스트 중단됨")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()
