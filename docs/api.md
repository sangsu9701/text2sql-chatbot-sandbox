# AKeeON-T API 문서

## 개요

AKeeON-T는 자연어 질문을 SQL로 변환하여 SNoP 매출 데이터를 분석하는 API입니다.

## 기본 정보

- **Base URL**: `http://localhost:8000/api/v1`
- **Content-Type**: `application/json`
- **인코딩**: UTF-8

## 인증

현재 버전에서는 인증이 필요하지 않습니다.

## 엔드포인트

### 1. 채팅 API

#### POST /chat

자연어 질문을 SQL로 변환하고 실행하여 결과를 반환합니다.

**요청 본문:**

```json
{
  "question": "지난 분기 카테고리별 매출 Top 5 보여줘",
  "wants_visualization": false,
  "chart_type": "bar",
  "session_id": "user-session-123"
}
```

**응답:**

```json
{
  "answer_text": "2023년 4분기 카테고리별 매출 Top 5를 조회했습니다.",
  "sql": "SELECT p.category, SUM(f.revenue) as total_revenue FROM fact_sales f JOIN dim_product p ON f.product_id = p.product_id JOIN dim_date d ON f.date_key = d.date_key WHERE d.quarter = 4 AND d.year = 2023 GROUP BY p.category ORDER BY total_revenue DESC LIMIT 5",
  "rows": [
    {"category": "전자제품", "total_revenue": 150000000},
    {"category": "오피스", "total_revenue": 80000000},
    {"category": "가구", "total_revenue": 50000000}
  ],
  "columns": ["category", "total_revenue"],
  "row_count": 3,
  "chart_suggestion": "bar",
  "execution_time": 0.85,
  "cached": false
}
```

### 2. 스키마 API

#### GET /schema

데이터베이스 스키마 정보를 반환합니다.

**응답:**

```json
{
  "tables": {
    "dim_date": {
      "name": "dim_date",
      "description": "날짜 차원 테이블",
      "columns": [
        {
          "name": "date_key",
          "type": "integer",
          "description": "날짜 키 (YYYYMMDD)",
          "nullable": false
        }
      ]
    }
  },
  "relationships": [
    {
      "from_table": "fact_sales",
      "from_column": "date_key",
      "to_table": "dim_date",
      "to_column": "date_key"
    }
  ]
}
```

### 3. 다운로드 API

#### POST /download/xlsx

SQL 쿼리 결과를 XLSX 파일로 다운로드합니다.

**요청 본문:**

```json
{
  "sql": "SELECT p.category, SUM(f.revenue) as total_revenue FROM fact_sales f JOIN dim_product p ON f.product_id = p.product_id GROUP BY p.category",
  "format": "xlsx"
}
```

**응답:**

XLSX 파일 스트림

## 에러 응답

모든 API는 에러 발생 시 다음과 같은 형식으로 응답합니다:

```json
{
  "error": "에러 메시지",
  "detail": "상세 에러 정보",
  "error_code": "ERROR_CODE"
}
```

### HTTP 상태 코드

- `200`: 성공
- `400`: 잘못된 요청 (SQL 검증 실패 등)
- `404`: 리소스를 찾을 수 없음
- `500`: 서버 내부 오류

## 제한사항

- **최대 쿼리 행 수**: 10,000행
- **최대 쿼리 실행 시간**: 30초
- **허용된 테이블**: `dim_date`, `dim_product`, `dim_customer`, `fact_sales`
- **허용된 쿼리 타입**: SELECT만 허용

## 예제

### cURL 예제

```bash
# 채팅 API 호출
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "지난 분기 카테고리별 매출 Top 5 보여줘"
  }'

# 스키마 조회
curl -X GET http://localhost:8000/api/v1/schema

# XLSX 다운로드
curl -X POST http://localhost:8000/api/v1/download/xlsx \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM fact_sales LIMIT 100"
  }' \
  --output data.xlsx
```

### JavaScript 예제

```javascript
// 채팅 API 호출
const response = await fetch('http://localhost:8000/api/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: '지난 분기 카테고리별 매출 Top 5 보여줘'
  })
});

const data = await response.json();
console.log(data);
```
