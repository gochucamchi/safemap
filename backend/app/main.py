from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import missing_persons
from app.database.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행"""
    print("🚀 Starting SafeMap API Server...")
    print("📍 Environment: Development")
    init_db()
    print("✅ Database initialized")
    yield
    print("👋 Shutting down SafeMap API Server...")

app = FastAPI(
    title="SafeMap API",
    description="실시간 안전 지도 API - 실종자 정보 제공",
    version="1.0.0",
    lifespan=lifespan
)

# ⭐ CORS 설정 - 매우 중요!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (개발 중)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(missing_persons.router, prefix="/api/v1", tags=["Missing Persons"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to SafeMap API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/api/info")
async def api_info():
    return {
        "name": "SafeMap API",
        "version": "1.0.0",
        "endpoints": {
            "missing_persons": "/api/v1/missing-persons",
            "statistics": "/api/v1/missing-persons/stats",
            "health": "/api/v1/health",
            "sync": "/api/v1/sync/missing-persons"
        }
    }
