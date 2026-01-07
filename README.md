# 가계부 서비스

온라인 가계부 서비스 - 영수증 OCR 자동 인식 기능 포함

## 기술 스택

- **백엔드**: Python/FastAPI
- **프론트엔드**: React
- **데이터베이스**: MongoDB
- **OCR**: OpenAI GPT-4 Vision API

## 주요 기능

- 지출/수입 관리
- 영수증 OCR 자동 인식
- 통계 및 대시보드
- 설정 관리

## 프로젝트 구조

```
가계부/
├── backend/          # FastAPI 백엔드
├── frontend/         # React 프론트엔드
└── docs/            # 문서
```

## 시작하기

### 백엔드 설정

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 프론트엔드 설정

```bash
cd frontend
npm install
npm start
```

## 환경 변수

백엔드 `.env` 파일:
```
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=household_book
```

