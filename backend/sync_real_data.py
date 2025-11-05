#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeMap 데이터 동기화 실행 스크립트

사용법:
    python sync_real_data.py              # 기본 10페이지 동기화
    python sync_real_data.py --pages 20   # 20페이지 동기화
    python sync_real_data.py --recent     # 최근 데이터만 동기화
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from app.services.data_sync_service import DataSyncService, run_sync


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="안전Dream API 데이터 동기화"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=10,
        help="동기화할 페이지 수 (기본: 10)"
    )
    parser.add_argument(
        "--recent",
        action="store_true",
        help="최근 데이터만 동기화 (5페이지)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="안전Dream API 키 (환경변수 우선)"
    )
    
    args = parser.parse_args()
    
    # 환경변수 로드
    load_dotenv()
    
    # API 키 확인
    api_key = args.api_key or os.getenv("SAFE_DREAM_API_KEY")
    
    if not api_key:
        print("❌ 에러: API 키가 설정되지 않았습니다.")
        print("\n해결 방법:")
        print("1. .env 파일에 SAFE_DREAM_API_KEY=4fd2a9d68b504580 추가")
        print("2. 또는 --api-key 옵션으로 직접 전달")
        print("\n예시:")
        print('  python sync_real_data.py --api-key "4fd2a9d68b504580"')
        sys.exit(1)
    
    # 동기화 실행
    max_pages = 5 if args.recent else args.pages
    
    print(f"\n{'='*60}")
    print(f"  SafeMap 실시간 데이터 동기화")
    print(f"{'='*60}")
    print(f"API 키: {api_key[:10]}...")
    print(f"페이지 수: {max_pages} (최대 {max_pages * 100}건)")
    print(f"{'='*60}\n")
    
    try:
        result = asyncio.run(run_sync(api_key=api_key, max_pages=max_pages))
        
        if result["success"]:
            print("\n✅ 동기화 완료!")
            print(f"\n💡 이제 앱을 새로고침하면 실제 데이터를 볼 수 있습니다!")
            return 0
        else:
            print("\n❌ 동기화 실패")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.")
        return 1
    
    except Exception as e:
        print(f"\n❌ 에러 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
