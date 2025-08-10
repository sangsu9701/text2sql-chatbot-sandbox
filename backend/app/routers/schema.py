from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.models.schemas import SchemaResponse
from app.services.schema_service import SchemaService

logger = logging.getLogger(__name__)

router = APIRouter()
schema_service = SchemaService()

@router.get("/schema", response_model=SchemaResponse)
async def get_schema(session: AsyncSession = Depends(get_db)):
    """
    데이터베이스 스키마 정보 반환
    """
    try:
        schema_info = await schema_service.get_schema_info(session)
        
        return SchemaResponse(
            tables=schema_info["tables"],
            relationships=schema_info["relationships"]
        )
        
    except Exception as e:
        logger.error(f"스키마 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"스키마 조회 실패: {str(e)}"
        )

@router.get("/schema/tables")
async def get_tables(session: AsyncSession = Depends(get_db)):
    """
    테이블 목록 반환
    """
    try:
        tables = await schema_service._get_tables(session)
        return {"tables": tables}
        
    except Exception as e:
        logger.error(f"테이블 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"테이블 목록 조회 실패: {str(e)}"
        )

@router.get("/schema/tables/{table_name}")
async def get_table_info(
    table_name: str,
    session: AsyncSession = Depends(get_db)
):
    """
    특정 테이블 정보 반환
    """
    try:
        table_info = await schema_service._get_table_info(session, table_name)
        return table_info
        
    except Exception as e:
        logger.error(f"테이블 정보 조회 실패 ({table_name}): {e}")
        raise HTTPException(
            status_code=500,
            detail=f"테이블 정보 조회 실패: {str(e)}"
        )

@router.get("/schema/examples")
async def get_example_queries():
    """
    예제 쿼리 목록 반환
    """
    try:
        examples = schema_service._get_example_queries()
        return {"examples": examples}
        
    except Exception as e:
        logger.error(f"예제 쿼리 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"예제 쿼리 조회 실패: {str(e)}"
        )
