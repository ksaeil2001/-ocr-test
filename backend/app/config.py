"""
애플리케이션 설정 관리 모듈
환경 변수를 로드하고 설정 클래스를 정의합니다.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # MongoDB 설정
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "household_book"
    
    # OpenAI 설정
    openai_api_key: Optional[str] = None
    
    # 파일 업로드 설정
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    
    # 서버 설정
    api_title: str = "가계부 API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()

