import openai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from datetime import date, datetime
from app.core.config import settings
from app.services.sql_guardrails import SQLGuardrails
from app.services.schema_service import SchemaService

logger = logging.getLogger(__name__)

class TextToSQLService:
    """Text-to-SQL 변환 서비스"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.guardrails = SQLGuardrails()
        self.schema_service = SchemaService()
    
    async def generate_sql(self, question: str, session: AsyncSession) -> Tuple[str, str]:
        """
        자연어 질문을 SQL로 변환
        
        Args:
            question: 자연어 질문
            session: 데이터베이스 세션
            
        Returns:
            (sql_query, explanation): SQL 쿼리와 설명
        """
        try:
            # 스키마 정보 가져오기
            schema_info = await self.schema_service.get_schema_info(session)
            
            # 프롬프트 생성
            prompt = self._create_prompt(question, schema_info)
            
            # OpenAI API 호출
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE
            )
            
            # 응답 파싱
            content = response.choices[0].message.content
            sql_query, explanation = self._parse_response(content)
            
            # SQL 검증 및 가드레일 적용
            validated_sql = await self.guardrails.validate_and_clean_sql(sql_query)
            
            return validated_sql, explanation
            
        except Exception as e:
            logger.error(f"SQL 생성 실패: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트 반환"""
        return """당신은 PostgreSQL 데이터베이스 전문가입니다. 
        자연어 질문을 정확한 SQL 쿼리로 변환해야 합니다.
        
        규칙:
        1. SELECT 문만 생성 (INSERT, UPDATE, DELETE 금지)
        2. LIMIT 절을 항상 포함 (기본값: 1000)
        3. 명확하고 읽기 쉬운 SQL 작성
        4. 적절한 JOIN 사용
        5. 집계 함수 사용 시 GROUP BY 포함
        6. 한국어로 설명 제공
        7. PostgreSQL INTERVAL 구문은 반드시 'INTERVAL ''3'' month' 형태 사용 (소문자, 작은따옴표 2개)
        8. 날짜 계산 시 CURRENT_DATE 사용
        9. INTERVAL 구문 예시: INTERVAL '3' month, INTERVAL '1' year, INTERVAL '7' day
                
        응답 형식:
        SQL: [SQL 쿼리]
        설명: [한국어 설명]"""
    
    def _create_prompt(self, question: str, schema_info: Dict[str, Any]) -> str:
        """프롬프트 생성"""
        # 스키마 정보를 JSON 직렬화 가능한 형태로 변환
        serializable_schema = self._make_serializable(schema_info)
        
        return f"""다음 데이터베이스 스키마를 기반으로 질문에 답하는 SQL을 작성해주세요:

스키마 정보:
{json.dumps(serializable_schema, indent=2, ensure_ascii=False)}

질문: {question}

위 스키마를 사용하여 정확한 SQL 쿼리를 작성하고, 한국어로 간단히 설명해주세요."""

    def _parse_response(self, content: str) -> Tuple[str, str]:
        """OpenAI 응답 파싱"""
        lines = content.strip().split('\n')
        sql_query = ""
        explanation = ""
        
        in_sql = False
        in_explanation = False
        
        for line in lines:
            line = line.strip()
            # 마크다운 코드 블록 시작/끝 제거
            if line.startswith("```sql") or line.startswith("```"):
                continue
            if line.startswith("SQL:"):
                in_sql = True
                in_explanation = False
                sql_query = line[4:].strip()
            elif line.startswith("설명:"):
                in_sql = False
                in_explanation = True
                explanation = line[3:].strip()
            elif in_sql and line:
                sql_query += " " + line
            elif in_explanation and line:
                explanation += " " + line
        
        # SQL 쿼리에서 마크다운 코드 블록 표시 제거
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        return sql_query, explanation
    
    async def execute_sql(self, sql: str, session: AsyncSession) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        SQL 실행
        
        Args:
            sql: 실행할 SQL 쿼리
            session: 데이터베이스 세션
            
        Returns:
            (rows, columns): 결과 행들과 컬럼명들
        """
        try:
            result = await session.execute(text(sql))
            rows = []
            for row in result.fetchall():
                row_dict = {}
                for key, value in row._mapping.items():
                    row_dict[key] = self._serialize_for_json(value)
                rows.append(row_dict)
            columns = list(result.keys()) if result.keys() else []
            
            return rows, columns
            
        except Exception as e:
            logger.error(f"SQL 실행 실패: {e}")
            raise
    
    def _serialize_for_json(self, obj):
        """JSON 직렬화를 위해 날짜/시간 객체와 Decimal 객체를 문자열로 변환"""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Decimal':
            return str(obj)
        return obj
    
    def _make_serializable(self, obj):
        """객체를 JSON 직렬화 가능한 형태로 변환"""
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Decimal':
            return str(obj)
        else:
            return obj
