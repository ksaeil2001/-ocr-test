"""
MongoDB 데이터베이스 연결 모듈
MongoDB 클라이언트 연결 및 데이터베이스 인스턴스를 관리합니다.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# MongoDB 클라이언트 인스턴스
client: Optional[AsyncIOMotorClient] = None
database = None


async def connect_to_mongo():
    """
    MongoDB에 연결합니다.
    """
    global client, database
    
    try:
        client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000  # 5초 타임아웃
        )
        
        # 연결 테스트
        await client.admin.command('ping')
        
        # 데이터베이스 인스턴스 생성
        database = client[settings.database_name]
        
        logger.info(f"MongoDB 연결 성공: {settings.mongodb_uri}")
        logger.info(f"데이터베이스: {settings.database_name}")
        
        return True
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB 연결 실패: {e}")
        raise
    except Exception as e:
        logger.error(f"MongoDB 연결 중 오류 발생: {e}")
        raise


async def close_mongo_connection():
    """
    MongoDB 연결을 종료합니다.
    """
    global client
    
    if client:
        client.close()
        logger.info("MongoDB 연결 종료")


async def test_connection() -> bool:
    """
    MongoDB 연결을 테스트합니다.
    
    Returns:
        bool: 연결 성공 여부
    """
    try:
        if client is None:
            return False
        
        await client.admin.command('ping')
        return True
        
    except Exception as e:
        logger.error(f"연결 테스트 실패: {e}")
        return False


def get_database():
    """
    데이터베이스 인스턴스를 반환합니다.
    
    Returns:
        Database: MongoDB 데이터베이스 인스턴스
    """
    if database is None:
        raise RuntimeError("데이터베이스가 초기화되지 않았습니다. connect_to_mongo()를 먼저 호출하세요.")
    return database

