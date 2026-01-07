"""
Transaction 모델
거래 내역 데이터 모델 및 컬렉션 관리
"""
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
import logging

from app.database import get_database

logger = logging.getLogger(__name__)

# 컬렉션 이름
COLLECTION_NAME = "transactions"


def get_transaction_collection() -> AsyncIOMotorCollection:
    """
    transactions 컬렉션 인스턴스를 반환합니다.
    
    Returns:
        AsyncIOMotorCollection: transactions 컬렉션
    """
    db = get_database()
    return db[COLLECTION_NAME]


async def create_indexes():
    """
    transactions 컬렉션에 필요한 인덱스를 생성합니다.
    """
    collection = get_transaction_collection()
    
    try:
        # 날짜 역순 인덱스 (최신순 조회)
        await collection.create_index([("date", -1)])
        logger.info("인덱스 생성 완료: date (-1)")
        
        # 카테고리별 조회 인덱스
        await collection.create_index([("category", 1)])
        logger.info("인덱스 생성 완료: category (1)")
        
        # 타입별 날짜 조회 인덱스
        await collection.create_index([("type", 1), ("date", -1)])
        logger.info("인덱스 생성 완료: type (1), date (-1)")
        
        # 날짜+카테고리 복합 인덱스 (통계 쿼리 최적화)
        await collection.create_index([("date", 1), ("category", 1)])
        logger.info("인덱스 생성 완료: date (1), category (1)")
        
        logger.info("모든 transactions 인덱스 생성 완료")
        
    except Exception as e:
        logger.error(f"인덱스 생성 중 오류 발생: {e}")
        raise


def prepare_transaction_document(data: dict, is_update: bool = False) -> dict:
    """
    거래 내역 문서를 준비합니다.
    createdAt과 updatedAt을 자동으로 설정합니다.
    
    Args:
        data: 거래 내역 데이터
        is_update: 업데이트 여부
        
    Returns:
        dict: MongoDB 문서 형식의 데이터
    """
    now = datetime.utcnow()
    
    if is_update:
        # 업데이트 시 updatedAt만 설정
        data["updatedAt"] = now
    else:
        # 생성 시 createdAt과 updatedAt 모두 설정
        data["createdAt"] = now
        data["updatedAt"] = now
    
    return data

