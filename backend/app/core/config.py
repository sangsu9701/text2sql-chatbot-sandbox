from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # 애플리케이션 설정
    APP_NAME: str = "AKeeON-T"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 데이터베이스 설정
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/snop_db"
    
    # OpenAI 설정
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.1
    
    # Redis 설정
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TTL: int = 3600  # 1시간
    
    # 보안 설정
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-domain.com"
    ]
    
    # SQL 가드레일 설정
    MAX_QUERY_ROWS: int = 10000
    MAX_QUERY_TIME: int = 30  # 초
    ALLOWED_TABLES: List[str] = [
        "dim_date",
        "dim_product", 
        "dim_customer",
        "fact_sales"
    ]
    
    # 파일 업로드 설정
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 전역 설정 인스턴스
settings = Settings()
