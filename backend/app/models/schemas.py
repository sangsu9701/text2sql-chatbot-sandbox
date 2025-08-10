from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum

class ChartType(str, Enum):
    """차트 타입"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    TABLE = "table"

class ChatRequest(BaseModel):
    """채팅 요청 스키마"""
    question: str = Field(..., description="자연어 질문")
    wants_visualization: Optional[bool] = Field(False, description="시각화 요청 여부")
    chart_type: Optional[ChartType] = Field(None, description="차트 타입")
    session_id: Optional[str] = Field(None, description="세션 ID")

class ChatResponse(BaseModel):
    """채팅 응답 스키마"""
    answer_text: str = Field(..., description="답변 텍스트")
    sql: str = Field(..., description="실행된 SQL 쿼리")
    rows: List[Dict[str, Any]] = Field(..., description="쿼리 결과 행들")
    columns: List[str] = Field(..., description="컬럼명들")
    row_count: int = Field(..., description="행 개수")
    chart_suggestion: Optional[ChartType] = Field(None, description="제안 차트 타입")
    execution_time: float = Field(..., description="실행 시간 (초)")
    cached: bool = Field(False, description="캐시 사용 여부")

class SchemaResponse(BaseModel):
    """스키마 응답 스키마"""
    tables: Dict[str, Any] = Field(..., description="테이블 정보")
    relationships: List[Dict[str, Any]] = Field(..., description="테이블 관계")

class TableInfo(BaseModel):
    """테이블 정보"""
    name: str = Field(..., description="테이블명")
    description: str = Field(..., description="테이블 설명")
    columns: List[Dict[str, Any]] = Field(..., description="컬럼 정보")

class ColumnInfo(BaseModel):
    """컬럼 정보"""
    name: str = Field(..., description="컬럼명")
    type: str = Field(..., description="데이터 타입")
    description: str = Field(..., description="컬럼 설명")
    nullable: bool = Field(..., description="NULL 허용 여부")

class DownloadRequest(BaseModel):
    """다운로드 요청 스키마"""
    sql: str = Field(..., description="다운로드할 SQL 쿼리")
    format: str = Field("xlsx", description="다운로드 형식 (xlsx, csv)")

class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")
    error_code: Optional[str] = Field(None, description="에러 코드")
