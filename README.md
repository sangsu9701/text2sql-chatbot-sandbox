# AKeeON-T: SNoP 매출 데이터 Text-to-SQL 임베더블 챗봇

자연어 질문을 SQL로 변환해 SNoP 매출 데이터를 질의/분석하는 임베더블 챗봇입니다.

## 🚀 주요 기능

- **자연어 → SQL 변환**: OpenAI LLM을 활용한 Text-to-SQL
- **임베드형 위젯**: Morphic과 동일한 UI/UX의 채널톡 유사 챗봇
- **데이터 시각화**: 요청 시 차트/그래프/표 렌더링
- **보안 가드레일**: SELECT-only, 파서 검증, LIMIT, 허용 스키마 화이트리스트
- **엑셀 다운로드**: 결과셋을 XLSX 형태로 다운로드

1. 백엔드 (FastAPI)
- ✅ Text-to-SQL 변환 서비스
- ✅ SQL 보안 가드레일
- ✅ Redis 캐싱
- ✅ PostgreSQL 연동
- ✅ XLSX 다운로드
- ✅ 스키마 정보 API
2. 프론트엔드 (Next.js)
- ✅ 챗봇 위젯 UI
- ✅ 데이터 테이블 (TanStack Table)
- ✅ 차트 시각화 (Recharts)
- ✅ API 연동
- ✅ 반응형 디자인
3. 데이터베이스
- ✅ SNoP 매출 데이터 스키마
- ✅ 샘플 데이터 (75개 레코드)
- ✅ 인덱스 및 관계 설정
4. 개발 환경
- ✅ Docker Compose 설정
- ✅ 환경 변수 관리
- ✅ 개발 스크립트

## 📁 프로젝트 구조

```
AKeeON-T/
├── �� backend/           # FastAPI 백엔드
│   ├── app/
│   │   ├── core/         # 설정, 데이터베이스
│   │   ├── models/       # 데이터 모델
│   │   ├── routers/      # API 라우터
│   │   ├── services/     # 비즈니스 로직
│   │   └── utils/        # 유틸리티
│   ├── requirements.txt  # Python 의존성
│   ├── main.py          # FastAPI 앱
│   └── Dockerfile       # 백엔드 컨테이너
├── �� frontend/          # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/         # Next.js App Router
│   │   ├── components/  # React 컴포넌트
│   │   ├── lib/         # 유틸리티
│   │   └── types/       # TypeScript 타입
│   ├── package.json     # Node.js 의존성
│   └── Dockerfile       # 프론트엔드 컨테이너
├── �� database/          # PostgreSQL 스키마
│   ├── schema.sql       # 테이블 구조
│   └── sample_data.sql  # 샘플 데이터
├── 📁 docs/             # 문서
│   ├── api.md           # API 문서
│   └── embedding.md     # 임베딩 가이드
├── 📄 README.md         # 프로젝트 개요
├── �� PRD.md           # 요구사항 문서
├── �� package.json     # 프로젝트 스크립트
└── �� docker-compose.yml # 개발 환경
```

## 🛠️ 기술 스택

### 프론트엔드
- Next.js 14 (App Router)
- Tailwind CSS
- shadcn/ui + Radix UI
- Recharts (차트)
- TanStack Table (표)
- SheetJS (엑셀)

### 백엔드
- FastAPI
- SQLAlchemy + asyncpg
- OpenAI API
- sqlglot (SQL 파싱/검증)
- Redis (캐싱)

### 데이터베이스
- PostgreSQL
- SNoP 매출 데이터 스키마

## 🚀 빠른 시작

### 1. 백엔드 설정
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. 프론트엔드 설정
```bash
cd frontend
npm install
npm run dev
```

### 3. 데이터베이스 설정
```bash
cd database
# PostgreSQL 설정 및 샘플 데이터 로드
```

## 📖 상세 문서

- [PRD.md](./PRD.md) - 프로젝트 요구사항 문서
- [API 문서](./docs/api.md) - 백엔드 API 명세
- [임베딩 가이드](./docs/embedding.md) - 위젯 임베딩 방법

## 🔒 보안

- SELECT-only 쿼리만 허용
- SQL 인젝션 방지 (파라미터 바인딩)
- 스키마 화이트리스트
- 실행 시간 및 행 수 제한
- CORS 및 iframe sandbox 설정

## 📊 성능 목표

- 질문→답변: < 3초 (캐시), < 8초 (생성+쿼리)
- SQL 오류율: < 3%
- 보안 차단: 100% 차단
- 위젯 설치: < 5분
