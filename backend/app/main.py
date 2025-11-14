# -*- coding: utf-8 -*-
"""
SafeMap API Server
- 서버 시작 시 자동 데이터 동기화
- 30분마다 자동 갱신
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import os
import asyncio

# ✅ .env 파일 로드
from dotenv import load_dotenv
load_dotenv()

from app.database.db import engine, Base
from app.api import missing_persons


# 자동 동기화 매니저
class AutoSyncManager:
    """자동 동기화 매니저 (30분마다)"""

<<<<<<< HEAD
    def __init__(self, api_key: str, kakao_api_key: str, esntl_id: str = "10000855"):
=======
    def __init__(self, api_key: str, esntl_id: str = "10000855"):
>>>>>>> d1176d62440f338400f576518b53ff4a493b3716
        self.api_key = api_key
        self.kakao_api_key = kakao_api_key
        self.esntl_id = esntl_id
        self.task = None
        self.is_running = False
        self.is_first_run = True  # 첫 실행 플래그
    
    async def start(self):
        """자동 동기화 시작"""
        print("🚀 자동 동기화 시작 (30분 간격)")
        self.is_running = True
        self.task = asyncio.create_task(self._sync_loop())
    
    async def stop(self):
        """자동 동기화 중지"""
        print("⏹️  자동 동기화 중지")
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
    
    async def _sync_loop(self):
        """동기화 루프"""
        # 서버 시작 즉시 첫 동기화
        await self._run_sync()
        
        # 30분마다 반복
        while self.is_running:
            try:
                await asyncio.sleep(30 * 60)  # 30분
                
                if self.is_running:
                    print("\n⏰ 정기 동기화 시작 (30분 경과)")
                    await self._run_sync()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ 자동 동기화 오류: {e}")
                await asyncio.sleep(60)
    
    async def _run_sync(self):
        """동기화 실행 (데이터 + 사진 + 지오코딩)"""
        try:
            from app.services.data_sync_service import DataSyncService

            service = DataSyncService(
                api_key=self.api_key,
                kakao_api_key=self.kakao_api_key,
                esntl_id=self.esntl_id
            )

<<<<<<< HEAD
            result = await service.sync_all_data(max_pages=50)
=======
            # 첫 실행: 모든 데이터 처리
            if self.is_first_run:
                print("\n🎯 첫 실행: 모든 사진 + 모든 지오코딩 처리")
                result = await service.sync_all_data(
                    max_pages=50,
                    scrape_photos=True,
                    max_photo_persons=None,  # 전체
                    geocode_addresses=True,
                    max_geocode_persons=None,  # 전체
                    is_initial_sync=True
                )
                self.is_first_run = False
            else:
                # 정기 실행: 최근 추가된 것만 처리
                print("\n🔄 정기 동기화: 새로운 데이터만 처리")
                result = await service.sync_all_data(
                    max_pages=50,
                    scrape_photos=True,
                    max_photo_persons=None,  # 최근 1시간 이내 전체
                    geocode_addresses=True,
                    max_geocode_persons=None,  # 최근 1시간 이내 전체
                    is_initial_sync=False
                )
>>>>>>> d1176d62440f338400f576518b53ff4a493b3716

            if result["success"]:
                stats = service.get_statistics()
                print(f"\n📊 현재 DB: {stats['total_count']}건")
<<<<<<< HEAD
                print(f"   지오코딩: 성공 {stats['geocoding_success']}건 / 실패 {stats['geocoding_failed']}건")
=======

                # 사진 스크랩 결과 출력
                if "photos_scraped" in result and result["photos_scraped"] > 0:
                    print(f"📸 사진 스크랩: {result['photos_scraped']}명 성공, "
                          f"{result['total_photos']}장 다운로드")

                # 지오코딩 결과 출력
                if "geocoded" in result and result["geocoded"] > 0:
                    print(f"🗺️  지오코딩: {result['geocoded']}명 완료")
>>>>>>> d1176d62440f338400f576518b53ff4a493b3716

        except Exception as e:
            print(f"❌ 동기화 실패: {e}")
            import traceback
            traceback.print_exc()


# 전역 변수
sync_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    서버 생명주기 관리
    """
    global sync_manager
    
    print("\n" + "="*60)
    print("🚀 Starting SafeMap API Server...")
    print("="*60)
    
    # 1. 데이터베이스 초기화
    print("📍 Environment: Development")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")
    
    # 2. 자동 동기화 시작
    api_key = os.getenv("SAFE_DREAM_API_KEY")
    # 지오코딩에는 REST API 키 사용 (KAKAO_REST_API_KEY 우선, 없으면 KAKAO_JS_API_KEY)
    kakao_api_key = os.getenv("KAKAO_REST_API_KEY") or os.getenv("KAKAO_JS_API_KEY")
    esntl_id = os.getenv("SAFE_DREAM_ESNTL_ID", "10000855")

    if api_key and kakao_api_key:
        print(f"🔑 API Key found: {api_key[:10]}...")
        print(f"🗺️  Kakao API Key found: {kakao_api_key[:10]}...")
        print(f"👤 Esntl ID: {esntl_id}")
        print("🔄 Initializing auto-sync service with auto-geocoding...")
        sync_manager = AutoSyncManager(api_key, kakao_api_key, esntl_id)
        await sync_manager.start()
        print("✅ Auto-sync enabled (30-minute interval, auto-geocoding enabled)")
    elif api_key:
        print(f"🔑 API Key found: {api_key[:10]}...")
        print("⚠️  KAKAO_REST_API_KEY/KAKAO_JS_API_KEY not found - geocoding will be disabled")
        print("   Set the Kakao API key in .env file to enable auto-geocoding")
    else:
        print("⚠️  SAFE_DREAM_API_KEY not found - auto-sync disabled")
        print("   Set the API key in .env file to enable auto-sync")
    
    print("="*60)
    print("✅ Server ready!")
    print("="*60 + "\n")
    
    # 서버 실행
    yield
    
    # 서버 종료 시
    print("\n" + "="*60)
    print("👋 Shutting down SafeMap API Server...")
    print("="*60)
    
    if sync_manager:
        await sync_manager.stop()
        print("✅ Auto-sync stopped")
    
    print("="*60)
    print("✅ Server shutdown complete")
    print("="*60 + "\n")


# FastAPI 앱 생성
app = FastAPI(
    title="SafeMap API",
    description="실종자 정보 및 안전시설 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(
    missing_persons.router,
    prefix="/api/v1",
    tags=["missing-persons"]
)

# 사진 디렉토리 정적 파일 서빙
PHOTOS_DIR = Path("downloaded_photos")
PHOTOS_DIR.mkdir(exist_ok=True)

# Static files 마운트 (사진 서빙용)
app.mount("/photos", StaticFiles(directory=str(PHOTOS_DIR)), name="photos")


# 루트 엔드포인트
@app.get("/")
async def root():
    """API 루트"""
    return {
        "service": "SafeMap API",
        "version": "1.0.0",
        "status": "running",
        "features": {
            "auto_sync": sync_manager is not None,
            "sync_interval": "30 minutes" if sync_manager else None
        }
    }


# 동기화 상태 확인
@app.get("/api/v1/sync/status")
async def sync_status():
    """자동 동기화 상태 확인"""
    if not sync_manager:
        return {
            "enabled": False,
            "message": "Auto-sync is disabled. Set SAFE_DREAM_API_KEY to enable."
        }
    
    return {
        "enabled": True,
        "is_running": sync_manager.is_running,
        "interval": "30 minutes",
        "last_sync": "Check server logs"
    }


# 수동 동기화 트리거
@app.post("/api/v1/sync/trigger")
async def trigger_sync(
    scrape_photos: bool = True,
    geocode_addresses: bool = True,
    process_all: bool = False
):
    """
    수동으로 동기화 실행 (데이터 + 사진 + 지오코딩)

    Args:
        scrape_photos: 사진 스크랩 여부
        geocode_addresses: 지오코딩 여부
        process_all: True면 전체 처리, False면 최근 추가만
    """
    if not sync_manager:
        return {
            "success": False,
            "message": "Auto-sync is not configured"
        }

<<<<<<< HEAD
    print("\n🔄 수동 동기화 요청")
=======
    print(f"\n🔄 수동 동기화 요청 (사진: {scrape_photos}, 지오코딩: {geocode_addresses}, 전체: {process_all})")
>>>>>>> d1176d62440f338400f576518b53ff4a493b3716

    try:
        from app.services.data_sync_service import DataSyncService

        service = DataSyncService(
            api_key=sync_manager.api_key,
            kakao_api_key=sync_manager.kakao_api_key,
            esntl_id=sync_manager.esntl_id
        )

<<<<<<< HEAD
        result = await service.sync_all_data(max_pages=50)
=======
        result = await service.sync_all_data(
            max_pages=50,
            scrape_photos=scrape_photos,
            max_photo_persons=None,
            geocode_addresses=geocode_addresses,
            max_geocode_persons=None,
            is_initial_sync=process_all
        )
>>>>>>> d1176d62440f338400f576518b53ff4a493b3716
        return result

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )