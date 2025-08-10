import sqlglot
from sqlglot import parse_one, exp
from typing import List, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SQLGuardrails:
    """SQL 보안 가드레일"""
    
    def __init__(self):
        self.forbidden_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
            'TRUNCATE', 'GRANT', 'REVOKE', 'EXECUTE', 'EXEC'
        ]
        self.allowed_tables = settings.ALLOWED_TABLES
        self.max_rows = settings.MAX_QUERY_ROWS
    
    async def validate_and_clean_sql(self, sql: str) -> str:
        """
        SQL 검증 및 정리
        
        Args:
            sql: 원본 SQL 쿼리
            
        Returns:
            정리된 SQL 쿼리
        """
        try:
            # INTERVAL 구문 수정
            sql = self._fix_interval_syntax(sql)
            
            # SQL 파싱
            parsed = parse_one(sql, dialect="postgres")
            
            # 보안 검증
            self._validate_security(parsed)
            
            # 테이블 허용 목록 검증
            self._validate_tables(parsed)
            
            # LIMIT 추가/수정
            cleaned_sql = self._add_limit(parsed)
            
            return cleaned_sql
            
        except Exception as e:
            logger.error(f"SQL 검증 실패: {e}")
            raise ValueError(f"SQL 검증 실패: {str(e)}")
    
    def _fix_interval_syntax(self, sql: str) -> str:
        """INTERVAL 구문 수정"""
        import re
        
        # INTERVAL '3' MONTHS -> INTERVAL '3 months'
        sql = re.sub(r"INTERVAL\s+'(\d+)'\s+MONTHS", r"INTERVAL '\1 months'", sql, flags=re.IGNORECASE)
        sql = re.sub(r"INTERVAL\s+'(\d+)'\s+YEARS", r"INTERVAL '\1 years'", sql, flags=re.IGNORECASE)
        sql = re.sub(r"INTERVAL\s+'(\d+)'\s+DAYS", r"INTERVAL '\1 days'", sql, flags=re.IGNORECASE)
        sql = re.sub(r"INTERVAL\s+'(\d+)'\s+WEEKS", r"INTERVAL '\1 weeks'", sql, flags=re.IGNORECASE)
        
        # 디버깅을 위한 로그 추가
        logger.info(f"INTERVAL 수정 전: {sql}")
        
        # 더 구체적인 패턴으로 수정
        sql = re.sub(r"INTERVAL\s*'(\d+)'\s*MONTHS", r"INTERVAL '\1 months'", sql, flags=re.IGNORECASE)
        sql = re.sub(r"INTERVAL\s*'(\d+)'\s*YEARS", r"INTERVAL '\1 years'", sql, flags=re.IGNORECASE)
        sql = re.sub(r"INTERVAL\s*'(\d+)'\s*DAYS", r"INTERVAL '\1 days'", sql, flags=re.IGNORECASE)
        sql = re.sub(r"INTERVAL\s*'(\d+)'\s*WEEKS", r"INTERVAL '\1 weeks'", sql, flags=re.IGNORECASE)
        
        logger.info(f"INTERVAL 수정 후: {sql}")
        
        return sql
    
    def _validate_security(self, parsed_sql):
        """보안 검증"""
        sql_str = parsed_sql.sql().upper()
        
        # 금지된 키워드 검사
        for keyword in self.forbidden_keywords:
            if keyword in sql_str:
                raise ValueError(f"금지된 키워드 사용: {keyword}")
        
        # SELECT 문만 허용
        if not isinstance(parsed_sql, exp.Select):
            raise ValueError("SELECT 문만 허용됩니다")
    
    def _validate_tables(self, parsed_sql):
        """테이블 허용 목록 검증"""
        tables = set()
        
        # FROM 절의 테이블들
        for from_expr in parsed_sql.find_all(exp.Table):
            tables.add(from_expr.name.lower())
        
        # JOIN 절의 테이블들
        for join_expr in parsed_sql.find_all(exp.Join):
            if hasattr(join_expr, 'this') and hasattr(join_expr.this, 'name'):
                tables.add(join_expr.this.name.lower())
        
        # 허용되지 않은 테이블 검사
        for table in tables:
            if table not in [t.lower() for t in self.allowed_tables]:
                raise ValueError(f"허용되지 않은 테이블: {table}")
    
    def _add_limit(self, parsed_sql) -> str:
        """LIMIT 절 추가/수정"""
        # 기존 LIMIT 제거
        for limit_expr in parsed_sql.find_all(exp.Limit):
            limit_expr.pop()
        
        # 새로운 LIMIT 추가
        parsed_sql.limit(self.max_rows)
        
        return parsed_sql.sql()
    
    def estimate_query_cost(self, sql: str) -> dict:
        """쿼리 비용 추정"""
        try:
            parsed = parse_one(sql, dialect="postgres")
            
            # 간단한 복잡도 분석
            complexity = {
                'joins': len(list(parsed.find_all(exp.Join))),
                'aggregations': len(list(parsed.find_all(exp.AggFunc))),
                'subqueries': len(list(parsed.find_all(exp.Subquery))),
                'window_functions': len(list(parsed.find_all(exp.Window)))
            }
            
            # 복잡도 점수 계산
            score = (
                complexity['joins'] * 10 +
                complexity['aggregations'] * 5 +
                complexity['subqueries'] * 20 +
                complexity['window_functions'] * 15
            )
            
            return {
                'complexity_score': score,
                'details': complexity,
                'risk_level': 'high' if score > 50 else 'medium' if score > 20 else 'low'
            }
            
        except Exception as e:
            logger.error(f"쿼리 비용 추정 실패: {e}")
            return {'complexity_score': 0, 'details': {}, 'risk_level': 'unknown'}
