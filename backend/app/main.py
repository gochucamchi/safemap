from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.db import init_db
from app.api.missing_persons import router as missing_persons_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 코드"""
    # 시작 시
    print("🚀 Starting SafeMap API Server...")
    print(f"📍 Environment: {'Development' if settings.debug else 'Production'}")
    
    # 데이터베이스 초기화
    init_db()
    print("✅ Database initialized")
    
    yield
    
    # 종료 시
    print("👋 Shutting down SafeMap API Server...")


# FastAPI 앱 생성
app = FastAPI(
    title="SafeMap API",
    description="실종자 안전지도 백엔드 API - 안전Dream 데이터 기반",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(missing_persons_router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "SafeMap API Server",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/api/info")
async def api_info():
    """API 정보"""
    return {
        "name": "SafeMap API",
        "version": "0.1.0",
        "description": "실종자 안전지도 API - 안전Dream 데이터 기반",
        "endpoints": {
            "missing_persons": "/api/v1/missing-persons",
            "statistics": "/api/v1/missing-persons/stats",
            "safety_facilities": "/api/v1/safety-facilities",
            "sync": "/api/v1/sync/missing-persons",
            "health": "/api/v1/health"
        },
        "data_source": "안전Dream (safe182.go.kr)"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
