from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect
from typing import Dict, List, Any
import logging
from datetime import date, datetime

logger = logging.getLogger(__name__)

def _serialize_for_json(obj):
    """JSON 직렬화를 위해 날짜/시간 객체와 Decimal 객체를 문자열로 변환"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Decimal':
        return str(obj)
    return obj

class SchemaService:
    """데이터베이스 스키마 서비스"""
    
    async def get_schema_info(self, session: AsyncSession) -> Dict[str, Any]:
        """
        데이터베이스 스키마 정보 반환
        
        Args:
            session: 데이터베이스 세션
            
        Returns:
            스키마 정보 딕셔너리
        """
        try:
            schema_info = {
                "tables": {},
                "relationships": [],
                "examples": []
            }
            
            # 테이블 정보 수집
            tables = await self._get_tables(session)
            for table_name in tables:
                table_info = await self._get_table_info(session, table_name)
                schema_info["tables"][table_name] = table_info
            
            # 관계 정보 수집
            schema_info["relationships"] = await self._get_relationships(session)
            
            # 예제 쿼리 추가
            schema_info["examples"] = self._get_example_queries()
            
            return schema_info
            
        except Exception as e:
            logger.error(f"스키마 정보 조회 실패: {e}")
            raise
    
    async def _get_tables(self, session: AsyncSession) -> List[str]:
        """테이블 목록 조회"""
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('dim_date', 'dim_product', 'dim_customer', 'fact_sales')
            ORDER BY table_name
        """)
        
        result = await session.execute(query)
        return [row[0] for row in result.fetchall()]
    
    async def _get_table_info(self, session: AsyncSession, table_name: str) -> Dict[str, Any]:
        """테이블 상세 정보 조회"""
        # 컬럼 정보 조회
        columns_query = text("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = :table_name 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        result = await session.execute(columns_query, {"table_name": table_name})
        columns = []
        
        for row in result.fetchall():
            column_info = {
                "name": row[0],
                "type": row[1],
                "nullable": row[2] == "YES",
                "default": row[3],
                "description": self._get_column_description(table_name, row[0])
            }
            columns.append(column_info)
        
        return {
            "name": table_name,
            "description": self._get_table_description(table_name),
            "columns": columns,
            "sample_data": await self._get_sample_data(session, table_name)
        }
    
    async def _get_relationships(self, session: AsyncSession) -> List[Dict[str, Any]]:
        """테이블 관계 정보 조회"""
        query = text("""
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
        """)
        
        result = await session.execute(query)
        relationships = []
        
        for row in result.fetchall():
            relationship = {
                "from_table": row[0],
                "from_column": row[1],
                "to_table": row[2],
                "to_column": row[3]
            }
            relationships.append(relationship)
        
        return relationships
    
    async def _get_sample_data(self, session: AsyncSession, table_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """샘플 데이터 조회"""
        try:
            query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
            result = await session.execute(query)
            rows = []
            for row in result.fetchall():
                row_dict = {}
                for key, value in row._mapping.items():
                    row_dict[key] = _serialize_for_json(value)
                rows.append(row_dict)
            return rows
        except Exception as e:
            logger.warning(f"샘플 데이터 조회 실패 ({table_name}): {e}")
            return []
    
    def _get_table_description(self, table_name: str) -> str:
        """테이블 설명 반환"""
        descriptions = {
            "dim_date": "날짜 차원 테이블 - 연도, 분기, 월, 주차 정보",
            "dim_product": "제품 차원 테이블 - 제품명, 카테고리, SKU 정보",
            "dim_customer": "고객 차원 테이블 - 고객명, 세그먼트, 지역 정보",
            "fact_sales": "매출 팩트 테이블 - 판매량, 단가, 매출 정보"
        }
        return descriptions.get(table_name, "테이블 설명 없음")
    
    def _get_column_description(self, table_name: str, column_name: str) -> str:
        """컬럼 설명 반환"""
        descriptions = {
            "dim_date": {
                "date_key": "날짜 키 (YYYYMMDD)",
                "date": "날짜",
                "year": "연도",
                "quarter": "분기 (1-4)",
                "month": "월 (1-12)",
                "week": "주차",
                "dow": "요일 (1-7, 1=월요일)"
            },
            "dim_product": {
                "product_id": "제품 ID",
                "product_name": "제품명",
                "category": "카테고리",
                "subcategory": "서브카테고리",
                "sku": "SKU 코드"
            },
            "dim_customer": {
                "customer_id": "고객 ID",
                "customer_name": "고객명",
                "segment": "고객 세그먼트",
                "region": "지역"
            },
            "fact_sales": {
                "sales_id": "판매 ID",
                "date_key": "날짜 키",
                "product_id": "제품 ID",
                "customer_id": "고객 ID",
                "quantity": "판매량",
                "unit_price": "단가",
                "revenue": "매출",
                "currency": "통화"
            }
        }
        
        table_desc = descriptions.get(table_name, {})
        return table_desc.get(column_name, "컬럼 설명 없음")
    
    def _get_example_queries(self) -> List[Dict[str, str]]:
        """예제 쿼리 반환"""
        return [
            {
                "question": "지난 분기 카테고리별 매출 Top 5 보여줘",
                "sql": """
                SELECT p.category, SUM(f.revenue) as total_revenue
                FROM fact_sales f
                JOIN dim_product p ON f.product_id = p.product_id
                JOIN dim_date d ON f.date_key = d.date_key
                WHERE d.quarter = EXTRACT(QUARTER FROM CURRENT_DATE - INTERVAL '3 months')
                AND d.year = EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '3 months')
                GROUP BY p.category
                ORDER BY total_revenue DESC
                LIMIT 5
                """
            },
            {
                "question": "주간 트렌드(주차별 매출, 수량) 알려줘",
                "sql": """
                SELECT d.week, SUM(f.revenue) as total_revenue, SUM(f.quantity) as total_quantity
                FROM fact_sales f
                JOIN dim_date d ON f.date_key = d.date_key
                WHERE d.year = EXTRACT(YEAR FROM CURRENT_DATE)
                GROUP BY d.week
                ORDER BY d.week
                LIMIT 1000
                """
            },
            {
                "question": "SKU A의 지역별 매출 분포",
                "sql": """
                SELECT c.region, SUM(f.revenue) as total_revenue
                FROM fact_sales f
                JOIN dim_product p ON f.product_id = p.product_id
                JOIN dim_customer c ON f.customer_id = c.customer_id
                WHERE p.sku = 'SKU_A'
                GROUP BY c.region
                ORDER BY total_revenue DESC
                LIMIT 1000
                """
            }
        ]
