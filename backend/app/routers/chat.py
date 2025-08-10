from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import time
import logging
import hashlib
import json

from app.core.database import get_db
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services.text_to_sql import TextToSQLService
from app.services.cache_service import CacheService
from app.services.chat_history_service import ChatHistoryService

logger = logging.getLogger(__name__)

router = APIRouter()
text_to_sql_service = TextToSQLService()
cache_service = CacheService()
chat_history_service = ChatHistoryService()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    자연어 질문을 SQL로 변환하고 실행하여 결과 반환
    """
    start_time = time.time()
    
    try:
        # 캐시 키 생성
        cache_key = hashlib.md5(
            json.dumps(request.dict(), sort_keys=True).encode()
        ).hexdigest()
        
        # 캐시 확인
        cached_result = await cache_service.get(cache_key)
        if cached_result:
            logger.info(f"캐시 히트: {cache_key}")
            return ChatResponse(
                **cached_result,
                execution_time=time.time() - start_time,
                cached=True
            )
        
        # Text-to-SQL 변환
        sql_query, explanation = await text_to_sql_service.generate_sql(
            request.question, 
            session
        )
        
        # SQL 실행
        rows, columns = await text_to_sql_service.execute_sql(sql_query, session)
        
        # 차트 제안
        chart_suggestion = _suggest_chart_type(request.question, columns, rows)
        
        # 응답 생성
        response = ChatResponse(
            answer_text=explanation,
            sql=sql_query,
            rows=rows,
            columns=columns,
            row_count=len(rows),
            chart_suggestion=chart_suggestion,
            execution_time=time.time() - start_time,
            cached=False
        )
        
        # 캐시 저장
        await cache_service.set(cache_key, response.dict())
        
        # 채팅 기록 저장
        try:
            session_id = request.session_id or "demo-session"
            # 사용자 메시지 저장
            await chat_history_service.save_message(
                session_id=session_id,
                message_type="user",
                content=request.question,
                db_session=session
            )
            # AI 응답 저장
            await chat_history_service.save_message(
                session_id=session_id,
                message_type="ai",
                content=explanation,
                sql_query=sql_query,
                execution_time=time.time() - start_time,
                cached=False,
                db_session=session
            )
        except Exception as e:
            logger.warning(f"채팅 기록 저장 실패: {e}")
        
        logger.info(f"채팅 처리 완료: {request.question[:50]}...")
        return response
        
    except ValueError as e:
        logger.error(f"SQL 검증 실패: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"SQL 검증 실패: {str(e)}"
        )
    except Exception as e:
        logger.error(f"채팅 처리 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"서버 오류: {str(e)}"
        )

def _suggest_chart_type(question: str, columns: List[str], rows: List[Dict[str, Any]]) -> str:
    """
    질문과 데이터를 기반으로 차트 타입 제안
    """
    question_lower = question.lower()
    
    # 키워드 기반 차트 타입 제안
    if any(word in question_lower for word in ['트렌드', '추이', '변화', '시간']):
        return 'line'
    elif any(word in question_lower for word in ['분포', '비율', '구성']):
        return 'pie'
    elif any(word in question_lower for word in ['비교', '순위', 'top']):
        return 'bar'
    elif len(columns) == 2 and len(rows) > 10:
        return 'scatter'
    else:
        return 'table'

@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    session: AsyncSession = Depends(get_db)
):
    """채팅 기록 조회"""
    try:
        messages = await chat_history_service.get_session_messages(session_id, session)
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        logger.error(f"채팅 기록 조회 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"채팅 기록 조회 실패: {str(e)}"
        )

@router.delete("/chat/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    session: AsyncSession = Depends(get_db)
):
    """채팅 기록 삭제"""
    try:
        await chat_history_service.clear_session(session_id, session)
        return {"message": "채팅 기록이 삭제되었습니다."}
    except Exception as e:
        logger.error(f"채팅 기록 삭제 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"채팅 기록 삭제 실패: {str(e)}"
        )
