"""
Category 모델
카테고리 데이터 모델 및 컬렉션 관리
"""
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
import logging

from app.database import get_database

logger = logging.getLogger(__name__)

# 컬렉션 이름
COLLECTION_NAME = "categories"


def get_category_collection() -> AsyncIOMotorCollection:
    """
    categories 컬렉션 인스턴스를 반환합니다.
    
    Returns:
        AsyncIOMotorCollection: categories 컬렉션
    """
    db = get_database()
    return db[COLLECTION_NAME]


async def create_indexes():
    """
    categories 컬렉션에 필요한 인덱스를 생성합니다.
    """
    collection = get_category_collection()
    
    try:
        # 이름 유니크 인덱스 (중복 방지)
        await collection.create_index([("name", 1)], unique=True)
        logger.info("인덱스 생성 완료: name (1) - unique")
        
        # 타입별 조회 인덱스
        await collection.create_index([("type", 1)])
        logger.info("인덱스 생성 완료: type (1)")
        
        logger.info("모든 categories 인덱스 생성 완료")
        
    except Exception as e:
        logger.error(f"인덱스 생성 중 오류 발생: {e}")
        raise


async def check_name_exists(name: str, exclude_id: str = None) -> bool:
    """
    카테고리 이름이 이미 존재하는지 확인합니다.
    
    Args:
        name: 확인할 카테고리 이름
        exclude_id: 제외할 문서 ID (업데이트 시 사용)
        
    Returns:
        bool: 이름이 존재하면 True, 아니면 False
    """
    collection = get_category_collection()
    
    query = {"name": name}
    if exclude_id:
        query["_id"] = {"$ne": exclude_id}
    
    count = await collection.count_documents(query)
    return count > 0


def prepare_category_document(data: dict) -> dict:
    """
    카테고리 문서를 준비합니다.
    createdAt을 자동으로 설정합니다.
    
    Args:
        data: 카테고리 데이터
        
    Returns:
        dict: MongoDB 문서 형식의 데이터
    """
    now = datetime.utcnow()
    data["createdAt"] = now
    return data

