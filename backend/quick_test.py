#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeMap 데이터 동기화 빠른 테스트 (수정 버전)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# SQLAlchemy 체크
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


async def test_api_connection():
    """API 연결 테스트"""
    print("\n" + "="*60)
    print("🔍 안전Dream API 연결 테스트")
    print("="*60 + "\n")
    
    try:
        from app.services.safe_dream_api import SafeDreamAPI
    except ImportError:
        print("❌ app.services.safe_dream_api를 찾을 수 없습니다")
        print("\n파일 구조를 확인해주세요:")
        print("backend/app/services/safe_dream_api.py")
        return False
    
    api_key = "4fd2a9d68b504580"
    client = SafeDreamAPI(api_key=api_key)
    
    print("1️⃣  API 호출 테스트...")
    try:
        response = await client.get_missing_children(row_size=5, page_num=1)
        
        # ✅ 수정: success 필드로 체크
        if response.get("success", False):
            print("   ✅ API 연결 성공!")
            print(f"   📊 총 데이터 수: {response.get('totalCount', 0)}건")
            
            persons = response.get("list", [])
            print(f"   📄 받은 데이터: {len(persons)}건\n")
            
            if persons:
                print("2️⃣  샘플 데이터 확인...")
                sample = persons[0]
                print(f"""
   🔹 실종자 식별코드: {sample.get('msspsnIdntfccd', 'N/A')}
   🔹 발생일시: {sample.get('occrde', 'N/A')}
   🔹 발생장소: {sample.get('occrAdres', 'N/A')}
   🔹 나이: {sample.get('age', 'N/A')}세
   🔹 성별: {sample.get('sexdstnDscd', 'N/A')}
   🔹 대상구분: {sample.get('writngTrgetDscd', 'N/A')}
                """)
                
                print("3️⃣  데이터 파싱 테스트...")
                parsed = client.parse_missing_person(sample)
                if parsed:
                    print("   ✅ 파싱 성공!")
                    print(f"""
   📍 주소: {parsed.get('location_address')}
   📅 날짜: {parsed.get('missing_date')}
   👤 나이/성별: {parsed.get('age')}세 / {parsed.get('gender')}
                    """)
                else:
                    print("   ⚠️  파싱 실패")
            
            print("\n" + "="*60)
            print("✅ API 테스트 통과!")
            print("="*60)
            return True
            
        else:
            print(f"   ❌ API 호출 실패: {response.get('msg')}")
            print(f"   응답: {response}")
            return False
            
    except Exception as e:
        print(f"   ❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_database():
    """데이터베이스 연결 테스트"""
    print("\n4️⃣  데이터베이스 연결 테스트...")
    
    if not SQLALCHEMY_AVAILABLE:
        print("   ❌ SQLAlchemy가 설치되지 않았습니다")
        print("\n   설치 명령어:")
        print("   pip install sqlalchemy")
        return False
    
    try:
        from app.database.db import SessionLocal, init_db
        from app.models.missing_person import MissingPerson
        
        init_db()
        print("   ✅ 데이터베이스 초기화 완료")
        
        db = SessionLocal()
        count = db.query(MissingPerson).count()
        print(f"   📊 현재 저장된 데이터: {count}건")
        db.close()
        
        return True
        
    except ImportError as e:
        print(f"   ❌ 모듈 import 실패: {str(e)}")
        print("\n   필요한 패키지를 설치해주세요:")
        print("   pip install sqlalchemy fastapi uvicorn httpx python-dotenv")
        return False
    
    except Exception as e:
        print(f"   ❌ 데이터베이스 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_packages():
    """필요한 패키지 확인"""
    print("\n📦 패키지 설치 확인...")
    
    packages = {
        "sqlalchemy": SQLALCHEMY_AVAILABLE,
        "fastapi": False,
        "httpx": False,
        "python-dotenv": False,
    }
    
    try:
        import fastapi
        packages["fastapi"] = True
    except ImportError:
        pass
    
    try:
        import httpx
        packages["httpx"] = True
    except ImportError:
        pass
    
    try:
        import dotenv
        packages["python-dotenv"] = True
    except ImportError:
        pass
    
    all_installed = all(packages.values())
    
    for pkg, installed in packages.items():
        status = "✅" if installed else "❌"
        print(f"   {status} {pkg}")
    
    if not all_installed:
        print("\n❌ 일부 패키지가 설치되지 않았습니다.")
        print("\n설치 명령어:")
        print("   pip install sqlalchemy fastapi uvicorn httpx python-dotenv")
        return False
    
    print("\n✅ 모든 패키지가 설치되어 있습니다!")
    return True


def main():
    """메인 실행"""
    print("\n" + "🚀"*30)
    print("  SafeMap 빠른 테스트")
    print("🚀"*30)
    
    # 패키지 체크
    packages_ok = check_packages()
    
    if not packages_ok:
        print("\n⚠️  먼저 패키지를 설치해주세요!")
        return 1
    
    # API 테스트
    api_ok = asyncio.run(test_api_connection())
    
    # DB 테스트
    db_ok = test_database()
    
    print("\n" + "="*60)
    print("📋 테스트 결과 요약")
    print("="*60)
    print(f"   패키지: {'✅ 성공' if packages_ok else '❌ 실패'}")
    print(f"   API 연결: {'✅ 성공' if api_ok else '❌ 실패'}")
    print(f"   데이터베이스: {'✅ 성공' if db_ok else '❌ 실패'}")
    print("="*60 + "\n")
    
    if api_ok and db_ok:
        print("✅ 모든 시스템 정상!")
        print("\n다음 명령어로 실제 데이터를 동기화하세요:")
        print("   python sync_real_data.py\n")
        return 0
    else:
        print("⚠️  문제가 발견되었습니다. 위 오류를 확인해주세요.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())