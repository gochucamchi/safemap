from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 안전Dream API 설정
    safe_dream_api_key: str = ""
    safe_dream_base_url: str = "https://www.safe182.go.kr"
    
    # 데이터베이스 설정
    database_url: str = "sqlite:///./safemap.db"  # 개발용 SQLite (프로덕션은 PostgreSQL)
    
    # API 설정
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # 지도 API
    kakao_api_key: Optional[str] = None
    naver_map_client_id: Optional[str] = None
    naver_map_client_secret: Optional[str] = None
    
    # CORS 설정
    allowed_origins: list = ["*"]  # 개발용, 프로덕션에서는 구체적으로 지정
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
