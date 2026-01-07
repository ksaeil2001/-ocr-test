# 가계부 서비스 개발 태스크 (TASKS)

## 문서 개요

본 문서는 가계부 서비스 개발을 위한 상세 태스크 목록입니다. 각 태스크는 자연어로 작성되어 있으며, AI 개발자가 직접 구현할 수 있도록 구체적으로 기술되어 있습니다.

**참조 문서**:
- PRD (Product Requirements Document)
- TRD (Technical Requirements Document)

---

## Phase 1: MVP (Minimum Viable Product)

### 1.1 프로젝트 초기 설정

#### [x] Task 1.1.1: 백엔드 프로젝트 구조 생성
**목표**: FastAPI 백엔드 프로젝트의 기본 디렉토리 구조와 설정 파일을 생성합니다.

**작업 내용**:
- `backend/` 디렉토리 생성
- `backend/app/` 디렉토리 및 하위 디렉토리 구조 생성 (TRD 2.2 참조)
  - `app/models/`, `app/schemas/`, `app/api/`, `app/services/`, `app/utils/`
- `backend/uploads/receipts/` 디렉토리 생성
- `backend/requirements.txt` 파일 생성 및 기본 의존성 추가
- `backend/.env.example` 파일 생성
- `backend/.gitignore` 파일 생성

**참조**: TRD 2.2, TRD 11.1

**산출물**:
- 완성된 디렉토리 구조
- `requirements.txt` (FastAPI, uvicorn, pymongo, python-dotenv, openai, pydantic 등)
- `.env.example` 파일

---

#### [x] Task 1.1.2: 프론트엔드 프로젝트 구조 생성
**목표**: React 프론트엔드 프로젝트의 기본 구조를 생성합니다.

**작업 내용**:
- `frontend/` 디렉토리에서 React 프로젝트 초기화 (CRA 또는 Vite)
- `src/` 디렉토리 하위 구조 생성 (TRD 2.2 참조)
  - `components/`, `pages/`, `services/`, `hooks/`, `context/`, `utils/`
- `package.json` 설정
- 기본 라우팅 설정 (React Router)
- `.env` 파일 생성

**참조**: TRD 2.2, PRD 4.2

**산출물**:
- 완성된 React 프로젝트 구조
- `package.json` (React, React Router, Axios 등)
- 기본 라우팅 설정

---

#### [x] Task 1.1.3: MongoDB 연결 및 데이터베이스 설정
**목표**: FastAPI에서 MongoDB에 연결하고 데이터베이스를 초기화합니다.

**작업 내용**:
- `backend/app/config.py` 파일 생성
  - 환경 변수 로드 (python-dotenv)
  - 설정 클래스 정의 (MongoDB URI, 데이터베이스명 등)
- `backend/app/database.py` 파일 생성
  - MongoDB 클라이언트 연결 함수 구현
  - 데이터베이스 인스턴스 생성
  - 연결 테스트 함수
- `backend/app/main.py`에 데이터베이스 연결 초기화 로직 추가

**참조**: TRD 3.1, TRD 7.3

**산출물**:
- `config.py` 파일
- `database.py` 파일
- MongoDB 연결 테스트 성공

---

### 1.2 데이터 모델 및 스키마 구현

#### [x] Task 1.2.1: Transaction 모델 및 스키마 구현
**목표**: 거래 내역(Transaction) 데이터 모델과 Pydantic 스키마를 구현합니다.

**작업 내용**:
- `backend/app/models/transaction.py` 파일 생성
  - MongoDB 문서 모델 정의 (TRD 3.2.1 참조)
  - 필드: type, date, amount, category, memo, receiptImagePath, createdAt, updatedAt
- `backend/app/schemas/transaction.py` 파일 생성
  - Pydantic 스키마 정의 (요청/응답)
  - TransactionCreate, TransactionUpdate, TransactionResponse 스키마
  - 데이터 검증 로직 (금액 양수, 날짜 형식 등)
- MongoDB 인덱스 생성 (date, category, type 등)

**참조**: PRD 2.2.3, PRD 5.1, TRD 3.2.1

**산출물**:
- `models/transaction.py`
- `schemas/transaction.py`
- MongoDB 인덱스 생성 완료

---

#### [x] Task 1.2.2: Category 모델 및 스키마 구현
**목표**: 카테고리 데이터 모델과 Pydantic 스키마를 구현합니다.

**작업 내용**:
- `backend/app/models/category.py` 파일 생성
  - MongoDB 문서 모델 정의 (TRD 3.2.2 참조)
  - 필드: name, type, color, icon, createdAt
- `backend/app/schemas/category.py` 파일 생성
  - CategoryCreate, CategoryUpdate, CategoryResponse 스키마
  - 이름 중복 검증 로직
- MongoDB 유니크 인덱스 생성 (name)

**참조**: PRD 2.3.3, PRD 5.2, TRD 3.2.2

**산출물**:
- `models/category.py`
- `schemas/category.py`
- 유니크 인덱스 생성 완료

---

### 1.3 기본 API 구현

#### [x] Task 1.3.1: 카테고리 CRUD API 구현
**목표**: 카테고리 생성, 조회, 수정, 삭제 API를 구현합니다.

**작업 내용**:
- `backend/app/api/categories.py` 파일 생성
- `GET /api/categories` 엔드포인트 구현
  - 쿼리 파라미터: type (선택)
  - 카테고리 목록 반환
- `POST /api/categories` 엔드포인트 구현
  - 카테고리 생성
  - 이름 중복 검증
- `PUT /api/categories/{id}` 엔드포인트 구현
  - 카테고리 수정
- `DELETE /api/categories/{id}` 엔드포인트 구현
  - 카테고리 삭제
  - 사용 중인 카테고리 삭제 방지 로직 (TRD 3.3 참조)
- `backend/app/main.py`에 라우터 등록

**참조**: PRD 2.3, PRD 6.3, TRD 4.4

**산출물**:
- `api/categories.py`
- 모든 엔드포인트 동작 확인

---

#### [x] Task 1.3.2: 거래 내역 CRUD API 구현
**목표**: 거래 내역 생성, 조회, 수정, 삭제 API를 구현합니다.

**작업 내용**:
- `backend/app/api/transactions.py` 파일 생성
- `GET /api/transactions` 엔드포인트 구현
  - 쿼리 파라미터: dateFrom, dateTo, category, type, search, page, limit, sort, order
  - 필터링, 검색, 정렬, 페이징 기능 구현
  - 응답에 pagination 정보 포함
- `POST /api/transactions` 엔드포인트 구현
  - 거래 내역 생성
  - 데이터 검증 (금액 양수, 카테고리 존재 여부 등)
- `GET /api/transactions/{id}` 엔드포인트 구현
  - 단일 거래 내역 조회
- `PUT /api/transactions/{id}` 엔드포인트 구현
  - 거래 내역 수정
- `DELETE /api/transactions/{id}` 엔드포인트 구현
  - 거래 내역 삭제
- `backend/app/main.py`에 라우터 등록

**참조**: PRD 2.2, PRD 6.2, TRD 4.3

**산출물**:
- `api/transactions.py`
- 모든 엔드포인트 동작 확인

---

### 1.4 파일 업로드 및 관리 기능

#### [x] Task 1.4.1: 파일 업로드 서비스 구현
**목표**: 영수증 이미지 파일을 업로드하고 로컬 파일 시스템에 저장하는 기능을 구현합니다.

**작업 내용**:
- `backend/app/services/file_service.py` 파일 생성
- `save_uploaded_file()` 함수 구현
  - 파일 검증 (확장자, 크기, MIME 타입) - TRD 6.2 참조
  - 파일명 생성 규칙 구현 (receipt_YYYYMMDD_HHMMSS.ext)
  - 년/월별 디렉토리 구조로 저장
  - 저장된 파일 경로 반환
- `delete_file()` 함수 구현
  - 파일 삭제 기능
- `get_file_url()` 함수 구현
  - 프론트엔드에서 접근 가능한 URL 생성
- 파일 크기 제한: 10MB (PRD 2.1.3 참조)
- 허용 확장자: .jpg, .jpeg, .png, .heic, .webp

**참조**: PRD 2.1.3, TRD 6.1, TRD 6.2, TRD 6.3

**산출물**:
- `services/file_service.py`
- 파일 업로드/삭제 기능 동작 확인

---

### 1.5 OpenAI OCR 통합

#### [x] Task 1.5.1: OpenAI Vision API 통합 서비스 구현
**목표**: OpenAI GPT-4 Vision API를 사용하여 영수증 이미지를 분석하고 구조화된 데이터를 추출하는 기능을 구현합니다.

**작업 내용**:
- `backend/app/services/ocr_service.py` 파일 생성
- OpenAI 클라이언트 초기화 (API 키 환경 변수에서 로드)
- `process_receipt_image()` 함수 구현
  - 이미지 파일 경로를 받아 OpenAI Vision API 호출
  - 프롬프트 구성 (TRD 5.2 참조)
  - JSON 형식 응답 파싱
  - 에러 처리 (재시도 로직, 타임아웃 처리)
- 응답 데이터 구조:
  - date, store, items, total, category, confidence, rawText
- 타임아웃: 30초 설정
- 재시도 로직: 최대 3회

**참조**: PRD 2.1, PRD 2.1.4, TRD 5.1, TRD 5.2, TRD 5.3

**산출물**:
- `services/ocr_service.py`
- OCR 기능 테스트 완료

---

#### [x] Task 1.5.2: 영수증 OCR API 엔드포인트 구현
**목표**: 영수증 이미지를 업로드하고 OCR 처리를 수행하는 API 엔드포인트를 구현합니다.

**작업 내용**:
- `backend/app/api/receipts.py` 파일 생성
- `POST /api/receipt/ocr` 엔드포인트 구현
  - multipart/form-data로 파일 업로드 받기
  - 파일 서비스를 통해 파일 저장
  - OCR 서비스를 통해 이미지 분석
  - 결과를 JSON 형식으로 반환
  - 에러 처리 (파일 형식 오류, OCR 실패 등)
- `POST /api/receipt/save` 엔드포인트 구현
  - OCR 결과를 거래 내역으로 저장
  - Transaction 생성 로직 호출
- `backend/app/main.py`에 라우터 등록

**참조**: PRD 2.1.2, PRD 6.1, TRD 4.2

**산출물**:
- `api/receipts.py`
- OCR API 엔드포인트 동작 확인

---

### 1.6 기본 통계 API 구현

#### [x] Task 1.6.1: 요약 통계 API 구현
**목표**: 대시보드에 표시할 기본 통계 데이터를 제공하는 API를 구현합니다.

**작업 내용**:
- `backend/app/api/statistics.py` 파일 생성
- `backend/app/services/statistics_service.py` 파일 생성
- `GET /api/statistics/summary` 엔드포인트 구현
  - 오늘 지출/수입 합계 계산
  - 이번 달 지출/수입 합계 계산
  - 이번 달 순수입 계산 (수입 - 지출)
  - 예산 대비 사용률 계산 (예산 기능 구현 후)
- MongoDB 집계 쿼리 사용
- `backend/app/main.py`에 라우터 등록

**참조**: PRD 2.5.1, PRD 6.5, TRD 4.6

**산출물**:
- `api/statistics.py`
- `services/statistics_service.py`
- 요약 통계 API 동작 확인

---

### 1.7 프론트엔드 기본 구조 및 API 연동

#### [x] Task 1.7.1: API 서비스 레이어 구현
**목표**: 프론트엔드에서 백엔드 API를 호출하는 서비스 레이어를 구현합니다.

**작업 내용**:
- `frontend/src/services/api.js` 파일 생성
- Axios 인스턴스 설정
  - Base URL 설정
  - 요청/응답 인터셉터 설정
  - 에러 처리
- API 함수 구현:
  - transactions API 호출 함수들
  - categories API 호출 함수들
  - receipts API 호출 함수들
  - statistics API 호출 함수들

**참조**: TRD 4.1, TRD 9.1

**산출물**:
- `services/api.js`
- 모든 API 호출 함수 구현 완료

---

#### [x] Task 1.7.2: 카테고리 관리 페이지 구현
**목표**: 카테고리를 생성, 조회, 수정, 삭제할 수 있는 페이지를 구현합니다.

**작업 내용**:
- `frontend/src/pages/Categories.jsx` 파일 생성
- 카테고리 목록 표시
- 카테고리 추가 폼 구현
  - 이름, 타입(지출/수입), 색상 선택, 아이콘 선택
- 카테고리 수정 기능 (모달 또는 인라인 편집)
- 카테고리 삭제 기능 (확인 다이얼로그)
- API 연동 (Task 1.7.1의 서비스 사용)

**참조**: PRD 2.3, PRD 7.1

**산출물**:
- `pages/Categories.jsx`
- 카테고리 CRUD 기능 동작 확인

---

#### [x] Task 1.7.3: 거래 내역 페이지 구현
**목표**: 거래 내역을 조회, 생성, 수정, 삭제할 수 있는 페이지를 구현합니다.

**작업 내용**:
- `frontend/src/pages/Transactions.jsx` 파일 생성
- 거래 내역 목록 표시 (테이블 또는 카드 형식)
- 필터링 UI 구현
  - 날짜 범위 선택
  - 카테고리 선택
  - 타입 선택 (지출/수입)
  - 검색 입력
- 정렬 기능 UI
- 페이징 UI
- 거래 내역 추가 폼 (모달)
  - 타입, 날짜, 금액, 카테고리, 메모 입력
- 거래 내역 수정 기능
- 거래 내역 삭제 기능
- API 연동

**참조**: PRD 2.2, PRD 2.2.4, PRD 2.2.5, PRD 7.1

**산출물**:
- `pages/Transactions.jsx`
- 거래 내역 CRUD 및 필터링 기능 동작 확인

---

#### [x] Task 1.7.4: 영수증 업로드 페이지 구현
**목표**: 영수증 이미지를 업로드하고 OCR 결과를 확인/수정한 후 저장할 수 있는 페이지를 구현합니다.

**작업 내용**:
- `frontend/src/pages/Receipt.jsx` 파일 생성
- 파일 업로드 컴포넌트 구현
  - 드래그 앤 드롭 또는 파일 선택
  - 이미지 미리보기
- OCR 처리 중 로딩 상태 표시
- OCR 결과 표시 및 수정 폼
  - 날짜, 상호명, 상품 목록, 총액, 카테고리 표시
  - 사용자가 수정 가능한 입력 필드
- 저장 버튼 클릭 시 거래 내역으로 저장
- 에러 처리 (OCR 실패, 파일 형식 오류 등)

**참조**: PRD 2.1.2, PRD 2.1.5, PRD 7.1

**산출물**:
- `pages/Receipt.jsx`
- 영수증 업로드 및 OCR 기능 동작 확인

---

#### [x] Task 1.7.5: 대시보드 페이지 구현
**목표**: 요약 통계를 표시하는 대시보드 페이지를 구현합니다.

**작업 내용**:
- `frontend/src/pages/Dashboard.jsx` 파일 생성
- 통계 카드 컴포넌트 구현
  - 오늘 지출/수입 카드
  - 이번 달 지출/수입 카드
  - 이번 달 순수입 카드
- 최근 거래 내역 목록 표시 (최근 10개)
- API 연동 (요약 통계 API 호출)
- 로딩 상태 처리

**참조**: PRD 2.5.1, PRD 7.1

**산출물**:
- `pages/Dashboard.jsx`
- 대시보드 페이지 동작 확인

---

#### Task 1.7.6: 공통 컴포넌트 및 레이아웃 구현
**목표**: 재사용 가능한 공통 컴포넌트와 레이아웃을 구현합니다.

**작업 내용**:
- `frontend/src/components/common/` 디렉토리 생성
- 네비게이션 바 컴포넌트 구현
  - 메뉴 항목: 대시보드, 거래 내역, 영수증, 통계, 카테고리, 예산, 설정
- 레이아웃 컴포넌트 구현 (헤더, 사이드바, 메인 컨텐츠 영역)
- 로딩 스피너 컴포넌트
- 에러 메시지 컴포넌트
- 모달 컴포넌트
- `frontend/src/App.jsx`에 라우팅 설정

**참조**: PRD 7.2, TRD 2.2

**산출물**:
- 공통 컴포넌트들
- 레이아웃 및 라우팅 설정 완료

---

### 1.8 CORS 및 에러 처리

#### Task 1.8.1: CORS 설정 및 공통 에러 처리 구현
**목표**: 백엔드에서 CORS를 설정하고 공통 에러 처리 로직을 구현합니다.

**작업 내용**:
- `backend/app/main.py`에 CORS 미들웨어 추가
  - allow_origins: http://localhost:3000
  - allow_methods: ["*"]
  - allow_headers: ["*"]
- 전역 예외 핸들러 구현
  - HTTPException 처리
  - 커스텀 예외 클래스 정의
  - 공통 에러 응답 형식 (TRD 4.1 참조)
- 로깅 설정
  - 로깅 레벨 설정
  - 파일 로깅 (선택)

**참조**: PRD 3.2, TRD 4.1, TRD 7.2, TRD 9.1, TRD 9.2

**산출물**:
- CORS 설정 완료
- 에러 처리 로직 구현 완료

---

## Phase 2: 고도화

### 2.1 예산 관리 기능

#### Task 2.1.1: Budget 모델 및 스키마 구현
**목표**: 예산 데이터 모델과 Pydantic 스키마를 구현합니다.

**작업 내용**:
- `backend/app/models/budget.py` 파일 생성
  - MongoDB 문서 모델 정의 (TRD 3.2.3 참조)
  - 필드: category, amount, period, createdAt, updatedAt
- `backend/app/schemas/budget.py` 파일 생성
  - BudgetCreate, BudgetUpdate, BudgetResponse 스키마
- MongoDB 유니크 인덱스 생성 (category, period)

**참조**: PRD 2.4.3, PRD 5.3, TRD 3.2.3

**산출물**:
- `models/budget.py`
- `schemas/budget.py`
- 인덱스 생성 완료

---

#### Task 2.1.2: 예산 CRUD API 구현
**목표**: 예산 생성, 조회, 수정, 삭제 API를 구현합니다.

**작업 내용**:
- `backend/app/api/budgets.py` 파일 생성
- `GET /api/budgets` 엔드포인트 구현
  - 쿼리 파라미터: period (선택)
  - 예산 목록 반환
- `POST /api/budgets` 엔드포인트 구현
  - 예산 생성
  - 동일 카테고리, 동일 주기 예산 중복 방지 (TRD 3.3 참조)
- `PUT /api/budgets/{id}` 엔드포인트 구현
  - 예산 수정
- `DELETE /api/budgets/{id}` 엔드포인트 구현
  - 예산 삭제
- `backend/app/main.py`에 라우터 등록

**참조**: PRD 2.4, PRD 6.4, TRD 4.5

**산출물**:
- `api/budgets.py`
- 모든 엔드포인트 동작 확인

---

#### Task 2.1.3: 예산 현황 계산 로직 구현
**목표**: 예산 대비 실제 지출 현황을 계산하는 로직을 구현합니다.

**작업 내용**:
- `backend/app/services/statistics_service.py`에 예산 현황 계산 함수 추가
- 현재 기간(월/년)의 카테고리별 지출 합계 계산
- 예산 대비 사용률 계산
- 예산 초과 여부 판단
- 남은 예산 금액 계산

**참조**: PRD 2.4.4, TRD 4.6

**산출물**:
- 예산 현황 계산 로직 구현 완료

---

#### Task 2.1.4: 예산 관리 페이지 구현
**목표**: 예산을 설정하고 현황을 확인할 수 있는 페이지를 구현합니다.

**작업 내용**:
- `frontend/src/pages/Budgets.jsx` 파일 생성
- 예산 목록 표시
- 예산 추가 폼 구현
  - 카테고리 선택, 금액 입력, 주기 선택 (월별/연별)
- 예산 수정 기능
- 예산 삭제 기능
- 예산 대비 사용률 프로그레스 바 표시
- 예산 초과 시 경고 표시
- 남은 예산 금액 표시
- API 연동

**참조**: PRD 2.4, PRD 2.4.5, PRD 7.1

**산출물**:
- `pages/Budgets.jsx`
- 예산 관리 기능 동작 확인

---

### 2.2 상세 통계 기능

#### Task 2.2.1: 카테고리별 통계 API 구현
**목표**: 카테고리별 지출/수입 통계를 제공하는 API를 구현합니다.

**작업 내용**:
- `GET /api/statistics/by-category` 엔드포인트 구현
  - 쿼리 파라미터: dateFrom, dateTo, type
  - 카테고리별 금액 합계 계산
  - 카테고리별 거래 건수 계산
  - 전체 대비 비율 계산
- MongoDB 집계 파이프라인 사용

**참조**: PRD 2.5.2, PRD 6.5, TRD 4.6

**산출물**:
- 카테고리별 통계 API 구현 완료

---

#### Task 2.2.2: 날짜별 통계 API 구현
**목표**: 날짜별 지출/수입 추이를 제공하는 API를 구현합니다.

**작업 내용**:
- `GET /api/statistics/by-date` 엔드포인트 구현
  - 쿼리 파라미터: period (daily/weekly/monthly/yearly), dateFrom, dateTo, type
  - 기간별로 그룹화하여 합계 계산
  - 일별/주별/월별/연별 통계 제공
- MongoDB 집계 파이프라인 사용

**참조**: PRD 2.5.3, PRD 6.5, TRD 4.6

**산출물**:
- 날짜별 통계 API 구현 완료

---

#### Task 2.2.3: 예산 현황 통계 API 구현
**목표**: 예산 대비 지출 현황을 제공하는 API를 구현합니다.

**작업 내용**:
- `GET /api/statistics/budget-status` 엔드포인트 구현
  - 쿼리 파라미터: period, date
  - 각 예산에 대한 현재 기간 지출 합계 계산
  - 예산 대비 사용률, 남은 금액, 초과 여부 반환

**참조**: PRD 2.5.4, PRD 6.5, TRD 4.6

**산출물**:
- 예산 현황 통계 API 구현 완료

---

#### Task 2.2.4: 트렌드 분석 API 구현
**목표**: 지출/수입 트렌드를 분석하는 API를 구현합니다.

**작업 내용**:
- `GET /api/statistics/trends` 엔드포인트 구현
  - 쿼리 파라미터: period (monthly/yearly), months, years
  - 월별/연별 지출/수입 추이 계산
  - 전월/전년 대비 증감률 계산
  - 평균 일일 지출 계산

**참조**: PRD 2.5.5, PRD 6.5, TRD 4.6

**산출물**:
- 트렌드 분석 API 구현 완료

---

#### Task 2.2.5: 통계 페이지 구현
**목표**: 다양한 통계와 차트를 표시하는 통계 페이지를 구현합니다.

**작업 내용**:
- `frontend/src/pages/Statistics.jsx` 파일 생성
- 차트 라이브러리 설치 및 설정 (Chart.js, Recharts, 또는 ApexCharts)
- 카테고리별 통계 차트 구현
  - 파이 차트 (카테고리별 비율)
  - 막대 차트 (카테고리별 금액)
- 날짜별 통계 차트 구현
  - 라인 차트 (일별/주별/월별 추이)
- 예산 현황 차트 구현
  - 프로그레스 바 또는 게이지 차트
- 트렌드 분석 차트 구현
  - 막대 차트 (월별 비교)
- 기간 선택 UI (날짜 범위 선택)
- API 연동

**참조**: PRD 2.5, PRD 7.1, PRD 7.2

**산출물**:
- `pages/Statistics.jsx`
- 모든 통계 차트 동작 확인

---

### 2.3 데이터 필터링 및 검색 고도화

#### Task 2.3.1: 거래 내역 고급 필터링 구현
**목표**: 거래 내역 페이지에 고급 필터링 기능을 추가합니다.

**작업 내용**:
- 금액 범위 필터 추가
  - 최소 금액, 최대 금액 입력
- 다중 카테고리 선택 필터
- 저장된 필터 프리셋 기능 (선택)
- 필터 초기화 버튼

**참조**: PRD 2.2.4, TRD 4.3

**산출물**:
- 고급 필터링 기능 구현 완료

---

#### Task 2.3.2: 검색 기능 개선
**목표**: 거래 내역 검색 기능을 개선합니다.

**작업 내용**:
- 메모 내용 검색 개선 (부분 일치)
- 상호명 검색 (영수증이 있는 경우)
- 검색어 하이라이트 표시
- 검색 결과 개수 표시

**참조**: PRD 2.2.4, TRD 4.3

**산출물**:
- 검색 기능 개선 완료

---

### 2.4 대시보드 고도화

#### Task 2.4.1: 대시보드에 예산 현황 추가
**목표**: 대시보드에 예산 대비 사용률 정보를 추가합니다.

**작업 내용**:
- 예산 대비 사용률 카드 추가
- 예산 초과 경고 표시
- 카테고리별 예산 현황 요약 표시

**참조**: PRD 2.5.1, PRD 2.5.4

**산출물**:
- 대시보드 예산 현황 추가 완료

---

#### Task 2.4.2: 대시보드에 차트 추가
**목표**: 대시보드에 간단한 차트를 추가합니다.

**작업 내용**:
- 최근 7일 지출 추이 라인 차트
- 카테고리별 지출 비율 파이 차트 (간소화)

**참조**: PRD 2.5, PRD 7.1

**산출물**:
- 대시보드 차트 추가 완료

---

## Phase 3: 최적화 및 개선

### 3.1 UI/UX 개선

#### Task 3.1.1: 반응형 디자인 구현
**목표**: 모바일 및 태블릿에서도 사용 가능하도록 반응형 디자인을 구현합니다.

**작업 내용**:
- CSS 미디어 쿼리 추가
- 모바일 네비게이션 메뉴 (햄버거 메뉴)
- 테이블 모바일 최적화 (카드 형식으로 변환)
- 터치 친화적 버튼 크기 조정
- 모바일에서 차트 크기 조정

**참조**: PRD 3.3, PRD 3.4

**산출물**:
- 반응형 디자인 구현 완료

---

#### Task 3.1.2: 로딩 상태 및 사용자 피드백 개선
**목표**: 사용자 경험을 개선하기 위한 로딩 상태와 피드백을 개선합니다.

**작업 내용**:
- 스켈레톤 로딩 UI 구현
- 작업 성공/실패 토스트 메시지
- 폼 유효성 검사 실시간 피드백
- 버튼 로딩 상태 표시

**참조**: PRD 3.4

**산출물**:
- 사용자 피드백 개선 완료

---

#### Task 3.1.3: 다크 모드 지원 (선택)
**목표**: 다크 모드 테마를 지원합니다.

**작업 내용**:
- 테마 컨텍스트 생성
- 다크 모드 CSS 변수 정의
- 테마 전환 토글 버튼
- 사용자 설정에 테마 저장

**참조**: PRD 2.6.1

**산출물**:
- 다크 모드 기능 구현 완료

---

### 3.2 성능 최적화

#### Task 3.2.1: 데이터베이스 쿼리 최적화
**목표**: 데이터베이스 쿼리 성능을 최적화합니다.

**작업 내용**:
- 인덱스 최적화 확인 및 추가
- 불필요한 필드 조회 제거 (프로젝션)
- 집계 쿼리 최적화
- 쿼리 실행 계획 분석

**참조**: TRD 3.2, TRD 8.1

**산출물**:
- 쿼리 성능 개선 완료

---

#### Task 3.2.2: 프론트엔드 성능 최적화
**목표**: 프론트엔드 로딩 및 렌더링 성능을 최적화합니다.

**작업 내용**:
- React.lazy()를 사용한 코드 스플리팅
- 메모이제이션 적용 (useMemo, useCallback)
- 이미지 최적화 (썸네일 생성)
- API 호출 최적화 (불필요한 요청 제거)
- 가상 스크롤링 (대량 데이터 목록)

**참조**: TRD 8.3

**산출물**:
- 프론트엔드 성능 개선 완료

---

#### Task 3.2.3: API 응답 캐싱 (선택)
**목표**: 통계 데이터 등 자주 조회되는 데이터를 캐싱합니다.

**작업 내용**:
- 통계 API 응답 캐싱 로직 구현
- 캐시 무효화 전략 수립
- TTL 설정

**참조**: TRD 8.2

**산출물**:
- API 캐싱 기능 구현 완료

---

### 3.3 에러 처리 강화

#### Task 3.3.1: 백엔드 에러 처리 개선
**목표**: 백엔드 에러 처리를 강화하고 사용자 친화적인 메시지를 제공합니다.

**작업 내용**:
- 커스텀 예외 클래스 확장
- 에러 코드 체계 정의
- 상세한 에러 메시지 (개발 환경)
- 일반적인 에러 메시지 (프로덕션 환경)
- 에러 로깅 강화

**참조**: TRD 7.4, TRD 9.1

**산출물**:
- 에러 처리 개선 완료

---

#### Task 3.3.2: 프론트엔드 에러 처리 개선
**목표**: 프론트엔드에서 에러를 적절히 처리하고 사용자에게 표시합니다.

**작업 내용**:
- Error Boundary 컴포넌트 구현
- API 에러 인터셉터 개선
- 네트워크 에러 처리
- 사용자 친화적 에러 메시지 표시
- 에러 복구 옵션 제공

**참조**: TRD 9.1

**산출물**:
- 프론트엔드 에러 처리 개선 완료

---

### 3.4 설정 기능 구현

#### Task 3.4.1: 설정 페이지 구현
**목표**: 앱 설정을 관리할 수 있는 페이지를 구현합니다.

**작업 내용**:
- `frontend/src/pages/Settings.jsx` 파일 생성
- 통화 단위 설정
- 날짜 형식 설정
- 언어 설정 (한국어)
- 설정 저장 기능 (로컬 스토리지 또는 백엔드)

**참조**: PRD 2.6.1, PRD 7.1

**산출물**:
- `pages/Settings.jsx`
- 설정 기능 동작 확인

---

#### Task 3.4.2: 데이터 내보내기 기능 구현
**목표**: 거래 내역을 CSV 또는 JSON 형식으로 내보낼 수 있는 기능을 구현합니다.

**작업 내용**:
- `GET /api/transactions/export` 엔드포인트 구현
  - 쿼리 파라미터: format (csv/json), dateFrom, dateTo
  - CSV 또는 JSON 형식으로 데이터 반환
- 프론트엔드에서 내보내기 버튼 및 다운로드 기능 구현

**참조**: PRD 2.6.2

**산출물**:
- 데이터 내보내기 기능 구현 완료

---

### 3.5 테스트 작성

#### Task 3.5.1: 백엔드 단위 테스트 작성
**목표**: 백엔드 주요 로직에 대한 단위 테스트를 작성합니다.

**작업 내용**:
- pytest 설정
- 서비스 레이어 테스트 작성
  - OCR 서비스 테스트
  - 통계 서비스 테스트
  - 파일 서비스 테스트
- 유틸리티 함수 테스트 작성

**참조**: TRD 10.1

**산출물**:
- 단위 테스트 코드 작성 완료
- 테스트 커버리지 70% 이상 달성

---

#### Task 3.5.2: 백엔드 통합 테스트 작성
**목표**: API 엔드포인트에 대한 통합 테스트를 작성합니다.

**작업 내용**:
- FastAPI TestClient 사용
- 각 API 엔드포인트 테스트 작성
- 테스트 데이터베이스 설정
- 테스트 픽스처 작성

**참조**: TRD 10.1

**산출물**:
- 통합 테스트 코드 작성 완료

---

#### Task 3.5.3: 프론트엔드 컴포넌트 테스트 작성
**목표**: 주요 프론트엔드 컴포넌트에 대한 테스트를 작성합니다.

**작업 내용**:
- React Testing Library 설정
- 주요 컴포넌트 테스트 작성
- 사용자 인터랙션 테스트
- API 모킹

**참조**: TRD 10.2

**산출물**:
- 컴포넌트 테스트 코드 작성 완료
- 테스트 커버리지 60% 이상 달성

---

## 완료 기준

각 Phase가 완료되기 위해서는:

**Phase 1 완료 기준**:
- 모든 기본 CRUD 기능 동작
- 영수증 OCR 기능 동작
- 기본 통계 표시
- 프론트엔드와 백엔드 연동 완료

**Phase 2 완료 기준**:
- 예산 관리 기능 완전 구현
- 모든 통계 API 및 차트 구현 완료
- 고급 필터링 및 검색 기능 동작

**Phase 3 완료 기준**:
- 성능 최적화 완료
- 에러 처리 강화 완료
- 테스트 작성 완료
- 사용자 경험 개선 완료

---

## 참고사항

- 각 태스크는 독립적으로 개발 가능하도록 설계되었습니다.
- 태스크 간 의존성이 있는 경우 명시되어 있습니다.
- 각 태스크 완료 후 해당 기능이 정상 동작하는지 확인해야 합니다.
- 코드 리뷰 및 리팩토링은 각 Phase 완료 후 진행하는 것을 권장합니다.
