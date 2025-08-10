from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import os
from dotenv import load_dotenv

from app.routers import chat, schema, download
from app.core.config import settings
from app.core.database import init_db

load_dotenv()

app = FastAPI(
    title="AKeeON-T API",
    description="SNoP 매출 데이터 Text-to-SQL 임베더블 챗봇 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(schema.router, prefix="/api/v1", tags=["schema"])
app.include_router(download.router, prefix="/api/v1", tags=["download"])

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    await init_db()

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "AKeeON-T API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
