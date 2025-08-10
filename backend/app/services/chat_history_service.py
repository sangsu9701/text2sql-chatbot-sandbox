from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatHistoryService:
    """채팅 기록 서비스"""
    
    async def save_session(self, session_id: str, db_session: AsyncSession) -> None:
        """채팅 세션 저장/업데이트"""
        try:
            # 세션이 존재하는지 확인
            check_query = text("SELECT session_id FROM chat_sessions WHERE session_id = :session_id")
            result = await db_session.execute(check_query, {"session_id": session_id})
            existing = result.fetchone()
            
            if existing:
                # 세션 업데이트
                update_query = text("""
                    UPDATE chat_sessions 
                    SET updated_at = CURRENT_TIMESTAMP 
                    WHERE session_id = :session_id
                """)
                await db_session.execute(update_query, {"session_id": session_id})
            else:
                # 새 세션 생성
                insert_query = text("""
                    INSERT INTO chat_sessions (session_id, created_at, updated_at) 
                    VALUES (:session_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """)
                await db_session.execute(insert_query, {"session_id": session_id})
            
            await db_session.commit()
            
        except Exception as e:
            logger.error(f"세션 저장 실패: {e}")
            await db_session.rollback()
            raise
    
    async def save_message(self, session_id: str, message_type: str, content: str, 
                          sql_query: Optional[str] = None, execution_time: Optional[float] = None,
                          cached: bool = False, db_session: AsyncSession = None) -> None:
        """채팅 메시지 저장"""
        try:
            # 세션 저장
            await self.save_session(session_id, db_session)
            
            # 메시지 저장
            insert_query = text("""
                INSERT INTO chat_messages 
                (session_id, message_type, content, sql_query, execution_time, cached, created_at)
                VALUES (:session_id, :message_type, :content, :sql_query, :execution_time, :cached, CURRENT_TIMESTAMP)
            """)
            
            await db_session.execute(insert_query, {
                "session_id": session_id,
                "message_type": message_type,
                "content": content,
                "sql_query": sql_query,
                "execution_time": execution_time,
                "cached": cached
            })
            
            await db_session.commit()
            
        except Exception as e:
            logger.error(f"메시지 저장 실패: {e}")
            await db_session.rollback()
            raise
    
    async def get_session_messages(self, session_id: str, db_session: AsyncSession) -> List[Dict[str, Any]]:
        """세션의 모든 메시지 조회"""
        try:
            query = text("""
                SELECT 
                    message_id,
                    message_type,
                    content,
                    sql_query,
                    execution_time,
                    cached,
                    created_at
                FROM chat_messages 
                WHERE session_id = :session_id 
                ORDER BY created_at ASC
            """)
            
            result = await db_session.execute(query, {"session_id": session_id})
            messages = []
            
            for row in result.fetchall():
                message = {
                    "message_id": row[0],
                    "message_type": row[1],
                    "content": row[2],
                    "sql_query": row[3],
                    "execution_time": float(row[4]) if row[4] else None,
                    "cached": row[5],
                    "created_at": row[6].isoformat() if row[6] else None
                }
                messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"메시지 조회 실패: {e}")
            raise
    
    async def clear_session(self, session_id: str, db_session: AsyncSession) -> None:
        """세션의 모든 메시지 삭제"""
        try:
            delete_query = text("DELETE FROM chat_messages WHERE session_id = :session_id")
            await db_session.execute(delete_query, {"session_id": session_id})
            
            session_delete_query = text("DELETE FROM chat_sessions WHERE session_id = :session_id")
            await db_session.execute(session_delete_query, {"session_id": session_id})
            
            await db_session.commit()
            
        except Exception as e:
            logger.error(f"세션 삭제 실패: {e}")
            await db_session.rollback()
            raise
