# 가계부 서비스 TRD (Technical Requirements Document)

## 1. 문서 개요

### 1.1 목적
본 문서는 가계부 서비스의 기술적 구현 요구사항을 정의합니다. 시스템 아키텍처, 데이터베이스 설계, API 명세, 보안 요구사항 등을 상세히 기술합니다.

### 1.2 참조 문서
- PRD (Product Requirements Document)
- API 명세서
- 데이터베이스 스키마 설계서

### 1.3 기술 스택 요약
- **백엔드**: Python 3.11+, FastAPI 0.104+
- **프론트엔드**: React 18+, React Router 6+
- **데이터베이스**: MongoDB 6.0+
- **OCR**: OpenAI GPT-4 Vision API
- **파일 저장**: 로컬 파일 시스템

---

## 2. 시스템 아키텍처

### 2.1 전체 아키텍처

```
┌─────────────────┐
│   React Client  │
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/REST API
         │
┌────────▼────────┐
│  FastAPI Server │
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
┌───▼───┐ ┌──▼──┐    ┌──────▼──────┐
│MongoDB│ │Local│    │ OpenAI API   │
│       │ │File │    │ (External)   │
│       │ │Sys  │    │              │
└───────┘ └─────┘    └─────────────┘
```

### 2.2 디렉토리 구조

```
가계부/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 앱 진입점
│   │   ├── config.py               # 설정 관리
│   │   ├── database.py             # MongoDB 연결
│   │   ├── models/                 # 데이터 모델
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   └── budget.py
│   │   ├── schemas/                # Pydantic 스키마
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   ├── budget.py
│   │   │   └── receipt.py
│   │   ├── api/                    # API 라우터
│   │   │   ├── __init__.py
│   │   │   ├── transactions.py
│   │   │   ├── categories.py
│   │   │   ├── budgets.py
│   │   │   ├── receipts.py
│   │   │   └── statistics.py
│   │   ├── services/               # 비즈니스 로직
│   │   │   ├── __init__.py
│   │   │   ├── ocr_service.py      # OpenAI OCR 처리
│   │   │   ├── file_service.py    # 파일 업로드/저장
│   │   │   └── statistics_service.py
│   │   └── utils/                  # 유틸리티
│   │       ├── __init__.py
│   │       └── validators.py
│   ├── uploads/                    # 업로드된 파일 저장
│   │   └── receipts/
│   │       └── YYYY/MM/
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/             # 재사용 컴포넌트
│   │   │   ├── common/
│   │   │   ├── charts/
│   │   │   └── forms/
│   │   ├── pages/                  # 페이지 컴포넌트
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Transactions.jsx
│   │   │   ├── Receipt.jsx
│   │   │   ├── Statistics.jsx
│   │   │   ├── Categories.jsx
│   │   │   ├── Budgets.jsx
│   │   │   └── Settings.jsx
│   │   ├── services/               # API 호출 서비스
│   │   │   └── api.js
│   │   ├── hooks/                  # Custom Hooks
│   │   │   ├── useTransactions.js
│   │   │   └── useStatistics.js
│   │   ├── context/                # Context API
│   │   │   └── AppContext.jsx
│   │   ├── utils/                  # 유틸리티
│   │   │   └── formatters.js
│   │   ├── App.jsx
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   └── .env
│
└── docs/
    ├── PRD.md
    └── TRD.md
```

---

## 3. 데이터베이스 설계

### 3.1 MongoDB 데이터베이스 구조

**데이터베이스명**: `household_book`

### 3.2 컬렉션 스키마

#### 3.2.1 transactions 컬렉션

```javascript
{
  _id: ObjectId("..."),
  type: "expense" | "income",        // 필수
  date: ISODate("2024-01-15T00:00:00Z"),  // 필수
  amount: Number,                    // 필수, 양수
  category: String,                  // 필수, 카테고리 이름 참조
  memo: String,                      // 선택, 최대 500자
  receiptImagePath: String,          // 선택, 로컬 파일 경로
  createdAt: ISODate,               // 자동 생성
  updatedAt: ISODate                // 자동 업데이트
}
```

**인덱스**:
- `{ date: -1 }` - 날짜 역순 (최신순 조회)
- `{ category: 1 }` - 카테고리별 조회
- `{ type: 1, date: -1 }` - 타입별 날짜 조회
- `{ date: 1, category: 1 }` - 날짜+카테고리 복합 인덱스

#### 3.2.2 categories 컬렉션

```javascript
{
  _id: ObjectId("..."),
  name: String,                      // 필수, 고유값
  type: "expense" | "income",        // 필수
  color: String,                    // 필수, HEX 색상 코드 (#FF5733)
  icon: String,                     // 선택, 아이콘 이름
  createdAt: ISODate                // 자동 생성
}
```

**인덱스**:
- `{ name: 1 }` - 유니크 인덱스 (중복 방지)
- `{ type: 1 }` - 타입별 조회

#### 3.2.3 budgets 컬렉션

```javascript
{
  _id: ObjectId("..."),
  category: String,                 // 필수, 카테고리 이름 참조
  amount: Number,                   // 필수, 양수
  period: "monthly" | "yearly",    // 필수
  createdAt: ISODate,              // 자동 생성
  updatedAt: ISODate               // 자동 업데이트
}
```

**인덱스**:
- `{ category: 1 }` - 유니크 인덱스 (카테고리당 하나의 예산)
- `{ period: 1 }` - 주기별 조회

### 3.3 데이터 무결성 규칙

1. **카테고리 삭제 제약**: 거래 내역에 사용 중인 카테고리는 삭제 불가
2. **예산 제약**: 동일 카테고리, 동일 주기당 하나의 예산만 존재
3. **거래 금액**: 항상 양수 (음수 불가)
4. **날짜 범위**: 유효한 날짜만 허용

---

## 4. API 상세 명세

### 4.1 공통 사항

**Base URL**: `http://localhost:8000/api`

**공통 응답 형식**:
```json
{
  "success": true,
  "data": {...},
  "message": "성공 메시지"
}
```

**에러 응답 형식**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지"
  }
}
```

**HTTP 상태 코드**:
- `200 OK`: 성공
- `201 Created`: 생성 성공
- `400 Bad Request`: 잘못된 요청
- `404 Not Found`: 리소스 없음
- `500 Internal Server Error`: 서버 에러

### 4.2 영수증 OCR API

#### POST /api/receipt/ocr

**요청**:
- Content-Type: `multipart/form-data`
- Body:
  - `file`: File (이미지 파일, 최대 10MB)

**응답** (성공):
```json
{
  "success": true,
  "data": {
    "date": "2024-01-15",
    "store": "편의점",
    "items": [
      {
        "name": "삼각김밥",
        "price": 2500
      }
    ],
    "total": 4000,
    "category": "식비",
    "confidence": 0.95,
    "rawText": "추출된 원본 텍스트"
  }
}
```

**에러 응답**:
- `400`: 파일 형식 오류, 파일 크기 초과
- `500`: OCR 처리 실패

#### POST /api/receipt/save

**요청**:
```json
{
  "date": "2024-01-15",
  "store": "편의점",
  "items": [...],
  "total": 4000,
  "category": "식비",
  "memo": "점심 식사",
  "receiptImagePath": "/uploads/receipts/2024/01/receipt_20240115_123456.jpg"
}
```

**응답**:
```json
{
  "success": true,
  "data": {
    "_id": "...",
    "type": "expense",
    "date": "2024-01-15T00:00:00Z",
    "amount": 4000,
    "category": "식비",
    ...
  }
}
```

### 4.3 거래 내역 API

#### GET /api/transactions

**쿼리 파라미터**:
- `dateFrom`: ISO 날짜 문자열 (선택)
- `dateTo`: ISO 날짜 문자열 (선택)
- `category`: 카테고리 이름 (선택)
- `type`: "expense" | "income" (선택)
- `search`: 검색어 (선택, 메모/상호명 검색)
- `page`: 페이지 번호 (기본값: 1)
- `limit`: 페이지당 항목 수 (기본값: 50)
- `sort`: 정렬 필드 (기본값: "date")
- `order`: 정렬 순서 "asc" | "desc" (기본값: "desc")

**응답**:
```json
{
  "success": true,
  "data": {
    "transactions": [...],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 100,
      "totalPages": 2
    }
  }
}
```

#### POST /api/transactions

**요청**:
```json
{
  "type": "expense",
  "date": "2024-01-15",
  "amount": 5000,
  "category": "식비",
  "memo": "점심 식사",
  "receiptImagePath": null
}
```

#### PUT /api/transactions/{id}

**요청**: POST와 동일한 형식

#### DELETE /api/transactions/{id}

**응답**:
```json
{
  "success": true,
  "message": "거래 내역이 삭제되었습니다."
}
```

### 4.4 카테고리 API

#### GET /api/categories

**쿼리 파라미터**:
- `type`: "expense" | "income" (선택)

#### POST /api/categories

**요청**:
```json
{
  "name": "식비",
  "type": "expense",
  "color": "#FF5733",
  "icon": "restaurant"
}
```

**검증**:
- `name`: 필수, 중복 불가
- `type`: 필수, "expense" 또는 "income"
- `color`: 필수, HEX 색상 코드 형식

#### DELETE /api/categories/{id}

**제약사항**: 사용 중인 카테고리는 삭제 불가 (400 에러)

### 4.5 예산 API

#### GET /api/budgets

**쿼리 파라미터**:
- `period`: "monthly" | "yearly" (선택)

#### POST /api/budgets

**요청**:
```json
{
  "category": "식비",
  "amount": 300000,
  "period": "monthly"
}
```

**검증**:
- 동일 카테고리, 동일 주기 예산이 이미 존재하면 400 에러

### 4.6 통계 API

#### GET /api/statistics/summary

**쿼리 파라미터**:
- `date`: ISO 날짜 문자열 (선택, 기본값: 오늘)

**응답**:
```json
{
  "success": true,
  "data": {
    "today": {
      "expense": 15000,
      "income": 0
    },
    "thisMonth": {
      "expense": 500000,
      "income": 2000000,
      "netIncome": 1500000
    },
    "budgetStatus": {
      "totalBudget": 1000000,
      "totalSpent": 500000,
      "usageRate": 0.5
    }
  }
}
```

#### GET /api/statistics/by-category

**쿼리 파라미터**:
- `dateFrom`: ISO 날짜 문자열 (필수)
- `dateTo`: ISO 날짜 문자열 (필수)
- `type`: "expense" | "income" (선택)

**응답**:
```json
{
  "success": true,
  "data": [
    {
      "category": "식비",
      "amount": 200000,
      "count": 45,
      "percentage": 40.0
    },
    ...
  ]
}
```

#### GET /api/statistics/by-date

**쿼리 파라미터**:
- `period`: "daily" | "weekly" | "monthly" | "yearly" (필수)
- `dateFrom`: ISO 날짜 문자열 (필수)
- `dateTo`: ISO 날짜 문자열 (필수)
- `type`: "expense" | "income" (선택)

**응답**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-01-15",
      "expense": 15000,
      "income": 0
    },
    ...
  ]
}
```

#### GET /api/statistics/budget-status

**쿼리 파라미터**:
- `period`: "monthly" | "yearly" (선택, 기본값: "monthly")
- `date`: ISO 날짜 문자열 (선택, 기본값: 오늘)

**응답**:
```json
{
  "success": true,
  "data": [
    {
      "category": "식비",
      "budget": 300000,
      "spent": 200000,
      "remaining": 100000,
      "usageRate": 0.67,
      "isOverBudget": false
    },
    ...
  ]
}
```

#### GET /api/statistics/trends

**쿼리 파라미터**:
- `period`: "monthly" | "yearly" (필수)
- `months`: 숫자 (선택, 기본값: 6, 월별일 때)
- `years`: 숫자 (선택, 기본값: 3, 연별일 때)

**응답**:
```json
{
  "success": true,
  "data": {
    "periods": ["2024-01", "2024-02", ...],
    "expenses": [500000, 450000, ...],
    "incomes": [2000000, 2000000, ...],
    "comparison": {
      "previousPeriod": 500000,
      "currentPeriod": 450000,
      "changeRate": -0.1
    }
  }
}
```

---

## 5. OpenAI OCR 통합

### 5.1 OCR 서비스 구현

**파일**: `backend/app/services/ocr_service.py`

**주요 함수**:
```python
async def process_receipt_image(image_path: str) -> dict:
    """
    영수증 이미지를 OpenAI Vision API로 처리하여 구조화된 데이터 반환
    
    Returns:
        {
            "date": str,
            "store": str,
            "items": List[dict],
            "total": float,
            "category": str | None,
            "confidence": float,
            "rawText": str
        }
    """
```

### 5.2 OpenAI API 호출

**모델**: `gpt-4-vision-preview` 또는 `gpt-4o`

**프롬프트 구조**:
```
당신은 영수증을 분석하는 전문가입니다. 
다음 영수증 이미지를 분석하여 JSON 형식으로 정보를 추출해주세요.

요구사항:
1. 날짜를 YYYY-MM-DD 형식으로 추출
2. 상호명 추출
3. 각 상품명과 가격을 배열로 추출
4. 총액 추출
5. 카테고리를 추론 (가능한 경우)
6. 신뢰도를 0-1 사이 값으로 제공

JSON 형식:
{
  "date": "YYYY-MM-DD",
  "store": "상호명",
  "items": [
    {"name": "상품명", "price": 금액}
  ],
  "total": 총액,
  "category": "카테고리명 또는 null",
  "confidence": 0.0-1.0
}
```

### 5.3 에러 처리

- **API 실패**: 재시도 로직 (최대 3회)
- **파싱 실패**: 기본값 반환 또는 사용자 수동 입력 유도
- **타임아웃**: 30초 타임아웃 설정

### 5.4 비용 최적화

- 이미지 크기 제한 (10MB)
- 이미지 압축 (필요시)
- 캐싱 고려 (동일 이미지 재처리 방지)

---

## 6. 파일 관리

### 6.1 파일 업로드 처리

**저장 경로 구조**:
```
backend/uploads/receipts/YYYY/MM/receipt_YYYYMMDD_HHMMSS.ext
```

**파일명 생성 규칙**:
- 형식: `receipt_{YYYY}{MM}{DD}_{HH}{MM}{SS}.{ext}`
- 예시: `receipt_20240115_143022.jpg`

### 6.2 파일 검증

- **허용 확장자**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.webp`
- **최대 크기**: 10MB
- **MIME 타입 검증**: 실제 파일 타입 확인

### 6.3 파일 서비스

**파일**: `backend/app/services/file_service.py`

**주요 함수**:
```python
async def save_uploaded_file(file: UploadFile) -> str:
    """업로드된 파일을 저장하고 경로 반환"""

def delete_file(file_path: str) -> bool:
    """파일 삭제"""

def get_file_url(file_path: str) -> str:
    """파일 URL 반환 (프론트엔드용)"""
```

---

## 7. 보안 요구사항

### 7.1 입력 검증

- **Pydantic 스키마**: 모든 입력 데이터 검증
- **파일 업로드**: 파일 타입, 크기, 확장자 검증
- **SQL Injection**: MongoDB 사용으로 자동 방지
- **XSS 방지**: 입력 데이터 이스케이프 처리

### 7.2 CORS 설정

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7.3 환경 변수 관리

**`.env` 파일** (Git에 커밋하지 않음):
```
OPENAI_API_KEY=sk-...
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=household_book
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
```

### 7.4 에러 메시지

- 민감한 정보 노출 방지
- 일반적인 에러 메시지 제공
- 상세 에러는 서버 로그에만 기록

---

## 8. 성능 최적화

### 8.1 데이터베이스 최적화

- **인덱스**: 자주 조회되는 필드에 인덱스 생성
- **쿼리 최적화**: 필요한 필드만 조회 (프로젝션)
- **페이징**: 대량 데이터 조회 시 페이징 적용

### 8.2 API 최적화

- **비동기 처리**: FastAPI의 async/await 활용
- **응답 캐싱**: 통계 데이터 캐싱 (Redis 고려 가능)
- **배치 처리**: 여러 통계 쿼리 병렬 처리

### 8.3 프론트엔드 최적화

- **코드 스플리팅**: React.lazy() 활용
- **이미지 최적화**: 썸네일 생성
- **API 호출 최적화**: 불필요한 요청 방지

---

## 9. 에러 처리 및 로깅

### 9.1 에러 처리 전략

**백엔드**:
- FastAPI의 HTTPException 사용
- 커스텀 예외 클래스 정의
- 전역 예외 핸들러

**프론트엔드**:
- API 에러 인터셉터
- 사용자 친화적 에러 메시지
- 에러 바운더리 (Error Boundary)

### 9.2 로깅

**로깅 레벨**:
- `DEBUG`: 개발 중 디버깅 정보
- `INFO`: 일반 정보
- `WARNING`: 경고
- `ERROR`: 에러
- `CRITICAL`: 치명적 에러

**로깅 내용**:
- API 요청/응답
- OCR 처리 결과
- 데이터베이스 쿼리 (개발 환경)
- 에러 스택 트레이스

---

## 10. 테스트 전략

### 10.1 백엔드 테스트

- **단위 테스트**: 서비스 로직 테스트
- **통합 테스트**: API 엔드포인트 테스트
- **테스트 프레임워크**: pytest

### 10.2 프론트엔드 테스트

- **컴포넌트 테스트**: React Testing Library
- **E2E 테스트**: (선택) Cypress

### 10.3 테스트 커버리지 목표

- 백엔드: 70% 이상
- 프론트엔드: 60% 이상

---

## 11. 배포 및 운영

### 11.1 로컬 개발 환경

**백엔드 실행**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**프론트엔드 실행**:
```bash
cd frontend
npm install
npm start
```

**MongoDB 실행**:
```bash
mongod --dbpath ./data/db
```

### 11.2 환경 변수 설정

각 환경별 `.env` 파일 생성:
- `backend/.env`
- `frontend/.env`

### 11.3 데이터 백업

- MongoDB 덤프: `mongodump`
- 업로드 파일 백업: `uploads/` 디렉토리 백업
- 정기 백업 스크립트 작성 권장

---

## 12. 개발 가이드라인

### 12.1 코드 스타일

**백엔드**:
- PEP 8 준수
- Black 포맷터 사용
- 타입 힌트 사용

**프론트엔드**:
- ESLint 설정
- Prettier 포맷터 사용
- 함수형 컴포넌트 우선

### 12.2 Git 커밋 규칙

- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정

### 12.3 API 버전 관리

- 현재 버전: v1
- URL에 버전 포함: `/api/v1/...`

---

## 13. 향후 확장성

### 13.1 확장 가능한 구조

- 모듈화된 서비스 구조
- 플러그인 방식의 통계 기능
- 확장 가능한 데이터 모델

### 13.2 성능 확장

- MongoDB 샤딩 (필요시)
- Redis 캐싱 도입
- CDN 활용 (이미지 서빙)

### 13.3 기능 확장

- 다중 사용자 지원
- 모바일 앱 개발
- 외부 서비스 연동 (은행 API 등)
```

이 내용을 `docs/TRD.md`로 저장하세요. 수정할 부분이 있으면 알려주세요.
