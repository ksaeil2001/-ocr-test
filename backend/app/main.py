"""
FastAPI 애플리케이션 진입점
데이터베이스 연결 초기화 및 라우터 등록을 수행합니다.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, test_connection
from app.models.transaction import create_indexes as create_transaction_indexes
from app.models.category import create_indexes as create_category_indexes
from app.api.categories import router as categories_router
from app.api.transactions import router as transactions_router
from app.api.receipts import router as receipts_router
from app.api.statistics import router as statistics_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177", "http://localhost:5178"],  # 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(categories_router)
app.include_router(transactions_router)
app.include_router(receipts_router)
app.include_router(statistics_router)


@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행되는 이벤트 핸들러
    MongoDB 연결을 초기화합니다.
    """
    logger.info("애플리케이션 시작 중...")
    try:
        await connect_to_mongo()
        
        # 연결 테스트
        if await test_connection():
            logger.info("MongoDB 연결 테스트 성공")
            
            # 인덱스 생성
            try:
                await create_transaction_indexes()
            except Exception as idx_error:
                logger.warning(f"Transaction 인덱스 생성 중 오류 발생 (무시됨): {idx_error}")
            
            try:
                await create_category_indexes()
            except Exception as idx_error:
                logger.warning(f"Category 인덱스 생성 중 오류 발생 (무시됨): {idx_error}")
        else:
            logger.warning("MongoDB 연결 테스트 실패")
            
    except Exception as e:
        logger.error(f"애플리케이션 시작 실패: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 실행되는 이벤트 핸들러
    MongoDB 연결을 종료합니다.
    """
    logger.info("애플리케이션 종료 중...")
    await close_mongo_connection()
    logger.info("애플리케이션 종료 완료")


@app.get("/")
async def root():
    """
    루트 엔드포인트
    """
    return {
        "message": "가계부 API",
        "version": settings.api_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    데이터베이스 연결 상태를 확인합니다.
    """
    db_status = await test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected"
    }

