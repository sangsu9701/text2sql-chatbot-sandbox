## PRD: SNoP 매출 데이터 Text-to-SQL 임베더블 챗봇 (AKeeON-T)

### 1) 프로젝트 개요
- 목적: 자연어 질문을 SQL로 변환해 SNoP 매출 데이터를 질의/분석하는 임베더블 챗봇. Morphic과 동일한 UI/UX, 채널톡 유사 ‘채널 버튼 + iframe 챗패널’ 방식.
- 핵심 원칙
  - AI 응답은 매 질문마다 실행 가능한 SQL을 반드시 포함
  - 차트/그래프/표는 “사용자가 요청할 때만” 렌더링
  - 보안/성능을 위해 Text-to-SQL 가드레일 필수 적용(SELECT-only, 파서 검증, LIMIT, 허용 스키마 화이트리스트 등)
- 참고
  - Morphic UI: `https://github.com/miurla/morphic`
  - Natural-language-postgres 패턴: `https://github.com/vercel-labs/natural-language-postgres`

### 2) 범위
- 포함
  - 임베드형 런처 버튼 + iframe 챗봇 위젯
  - Morphic과 동일한 대화형 Answer UI(메시지, 코드블록, 액션버튼)
  - Text-to-SQL(모델 연동, 스키마 컨텍스트, guardrails, SQL 실행)
  - FastAPI 백엔드, PostgreSQL, 샘플 데이터, 시각화(요청 시)
  - 표/다운로드(XLSX) 기능
- 제외(초기)
  - 인증/권한(사내 SSO 등): V2
  - RLS/다중 테넌트: V2
  - 실시간 스트리밍 응답: V2(가능하면 SSE 옵션)

### 3) 이해관계자와 성공 기준
- 이해관계자: 데이터/영업 운영(S&OP), 경영기획, IT/데이터팀
- 성공 지표
  - 질문→답변 평균 < 3s(캐시 적중)/< 8s(생성+쿼리)
  - SQL 오류율 < 3%, 보안 차단(비허용 쿼리) 100% 차단
  - 위젯 임베드 설치 < 5분, NPS>8

### 4) 사용자 스토리
- 분석가: “지난 분기 카테고리별 매출 Top 5 보여줘. SQL도 같이.” → SQL 블록 + 표 반환. “막대그래프로 그려줘.” → 차트 렌더.
- 매니저: “주간 트렌드(주차별 매출, 수량) 알려줘” → SQL + 시계열 집계, “엑셀로 내려줘” → XLSX 다운로드.
- 운영: “SKU A의 지역별 매출 분포” → 맵/바 차트(요청 시만).

### 5) 시스템 아키텍처
- 프론트엔드: Next.js + Tailwind + shadcn/ui + Radix, 차트(Recharts/ECharts), 표(TanStack Table), 엑셀(SheetJS)
- 백엔드: FastAPI + SQLAlchemy + asyncpg/psycopg, OpenAI(or 호환) LLM, 가드레일(sqlglot), 캐싱
- 데이터: PostgreSQL(샘플 SNoP 매출 스키마)
- 임베딩: 런처 버튼 → iframe 오버레이(postMessage 통신, origin allowlist)

데이터흐름: Widget → FastAPI(`/chat`) → LLM(Text→SQL) → Guardrails → DB 실행 → 결과 → Widget 렌더(차트는 요청 시)

### 6) UI/UX 요구사항(“Morphic 동일”)
- 런처 버튼: 우하단 고정, 원형, 다크/라이트, 뱃지/호버
- Iframe 챗패널: 헤더, 메시지 리스트, 입력창; SQL 코드블록 항상 포함; 액션 버튼(차트/표/엑셀)
- 접근성: 키보드 포커스, 스크린리더 라벨, 콘트라스트

### 7) 임베딩 사양
- 설치 스니펫(예)
```html
<script src="https://cdn.example.com/snopsql-widget.min.js" data-project-id="YOUR_PROJECT_ID" data-theme="auto"></script>
```
- 보안: origin allowlist, iframe sandbox, CSP 안내

### 8) 백엔드 API(초안)
- POST `/chat`: { question, wantsVisualization?, vizType? } → { answerText, sql, rows, columns, rowCount, chartSuggestion? }
- GET `/schema`: 허용 스키마/테이블/컬럼 메타
- POST `/download/xlsx`: 결과셋 파일 스트림

### 9) Text-to-SQL 설계
- 프롬프트: PostgreSQL, SELECT-only, WITH/LIMIT, 화이트리스트 컬럼, SQL 우선 출력
- 컨텍스트: `/schema` 메타, few-shot, 단위/통화/타임존
- 가드레일: sqlglot 파싱, 화이트리스트, 금지 키워드, LIMIT 상한, 시간범위 제한, EXPLAIN 비용 점검

### 10) 데이터 스키마(샘플)
- `dim_date(date_key, date, year, quarter, month, week, dow)`
- `dim_product(product_id, product_name, category, subcategory, sku)`
- `dim_customer(customer_id, customer_name, segment, region)`
- `fact_sales(sales_id, date_key, product_id, customer_id, quantity, unit_price, revenue, currency)`

### 11) 시각화/표/다운로드
- 표: TanStack Table
- 차트: Recharts 기본(또는 ECharts)
- XLSX: SheetJS, 대용량 서버 측 스트리밍

### 12) 보안/성능
- 보안: SELECT-only, 파라미터 바인딩, 화이트리스트, 실행시간/행수 제한, CORS/iframe sandbox
- 성능: 캐시, 타임아웃, 인덱스 권고, 프리셰이핑 뷰

### 13) 로깅/모니터링
- 로그: {question, normalized_sql, blocked_reason?, latency_ms}
- 메트릭: LLM/SQL 시간, 차단율, 캐시 히트율

### 14) 테스트
- 단위: 프롬프트→SQL 스냅샷, 가드레일
- 통합: `/chat` E2E
- 보안: DDL/DML, SQLi 시나리오 차단

### 15) 마일스톤/AC
- M1~M5: 스키마/백엔드/UI/가드레일/배포
- 수용 기준: SQL 항상 포함, 차트는 요청 시만, 임베드 스니펫 설치, DDL/DML 100% 차단, 대표 질의 10건 통과

### 16) 리스크/대응
- NL→SQL 부정확: few-shot 강화, 후보 다중 생성+가드레일 선택
- 성능: 캐시/제한/인덱스
- 보안: 파서+화이트리스트 이중화, 서명된 쿼리만 실행

### 17) 재검토
- 요구사항 충족 여부와 대안/가드레일/임베드 보안을 재점검. 실스키마 반영은 착수 시 업데이트.


