"""
파일 업로드 서비스
영수증 이미지 파일 업로드, 저장, 삭제 기능을 제공합니다.
"""
import os
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging
import aiofiles
from fastapi import UploadFile, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".webp"}

# 허용된 MIME 타입
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/heic",
    "image/heif",
    "image/webp"
}


def get_file_extension(filename: str) -> str:
    """
    파일명에서 확장자를 추출합니다.
    
    Args:
        filename: 파일명
        
    Returns:
        str: 확장자 (소문자, 점 포함)
    """
    return Path(filename).suffix.lower()


def validate_file(file: UploadFile) -> None:
    """
    업로드된 파일을 검증합니다.
    
    Args:
        file: 업로드된 파일
        
    Raises:
        HTTPException: 파일 검증 실패 시
    """
    # 파일명 확인
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일명이 없습니다.")
    
    # 확장자 검증
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않는 파일 형식입니다. 허용 형식: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # MIME 타입 검증
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않는 MIME 타입입니다: {file.content_type}"
        )


def generate_filename(original_filename: str) -> str:
    """
    파일명을 생성합니다.
    형식: receipt_YYYYMMDD_HHMMSS.ext
    
    Args:
        original_filename: 원본 파일명
        
    Returns:
        str: 생성된 파일명
    """
    ext = get_file_extension(original_filename)
    now = datetime.utcnow()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return f"receipt_{timestamp}{ext}"


def get_storage_path(filename: str) -> tuple[str, str]:
    """
    파일 저장 경로를 생성합니다.
    년/월별 디렉토리 구조로 저장합니다.
    
    Args:
        filename: 파일명
        
    Returns:
        tuple: (전체 경로, 상대 경로)
    """
    now = datetime.utcnow()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    
    # 디렉토리 경로 생성
    relative_dir = f"receipts/{year}/{month}"
    full_dir = os.path.join(settings.upload_dir, relative_dir)
    
    # 디렉토리 생성 (존재하지 않으면)
    os.makedirs(full_dir, exist_ok=True)
    
    # 파일 경로 생성
    relative_path = os.path.join(relative_dir, filename)
    full_path = os.path.join(settings.upload_dir, relative_path)
    
    return full_path, relative_path


async def save_uploaded_file(file: UploadFile) -> str:
    """
    업로드된 파일을 저장하고 상대 경로를 반환합니다.
    
    Args:
        file: 업로드된 파일
        
    Returns:
        str: 저장된 파일의 상대 경로 (DB에 저장할 경로)
        
    Raises:
        HTTPException: 파일 검증 실패 또는 저장 실패 시
    """
    try:
        # 파일 검증
        validate_file(file)
        
        # 파일 크기 확인
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"파일 크기가 너무 큽니다. 최대 크기: {settings.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="빈 파일은 업로드할 수 없습니다.")
        
        # 파일명 생성
        filename = generate_filename(file.filename)
        
        # 저장 경로 생성
        full_path, relative_path = get_storage_path(filename)
        
        # 파일 저장
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(file_content)
        
        logger.info(f"파일 저장 완료: {relative_path} (크기: {file_size} bytes)")
        
        # 상대 경로 반환 (DB에 저장할 경로)
        return relative_path
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 저장 실패: {e}")
        raise HTTPException(status_code=500, detail="파일 저장에 실패했습니다.")


def delete_file(file_path: str) -> bool:
    """
    파일을 삭제합니다.
    
    Args:
        file_path: 삭제할 파일의 상대 경로 (DB에 저장된 경로)
        
    Returns:
        bool: 삭제 성공 여부
    """
    try:
        # 상대 경로를 절대 경로로 변환
        full_path = os.path.join(settings.upload_dir, file_path)
        
        # 파일 존재 확인
        if not os.path.exists(full_path):
            logger.warning(f"삭제할 파일이 존재하지 않습니다: {file_path}")
            return False
        
        # 파일 삭제
        os.remove(full_path)
        logger.info(f"파일 삭제 완료: {file_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"파일 삭제 실패: {e}")
        return False


def get_file_url(file_path: str) -> str:
    """
    프론트엔드에서 접근 가능한 파일 URL을 생성합니다.
    
    Args:
        file_path: 파일의 상대 경로 (DB에 저장된 경로)
        
    Returns:
        str: 파일 URL
    """
    # 상대 경로의 앞뒤 공백 제거
    file_path = file_path.strip()
    
    # 경로가 비어있거나 None인 경우
    if not file_path:
        return ""
    
    # 경로 정규화 (백슬래시를 슬래시로 변환)
    file_path = file_path.replace("\\", "/")
    
    # 앞에 슬래시가 없으면 추가
    if not file_path.startswith("/"):
        file_path = "/" + file_path
    
    # API 엔드포인트 URL 생성
    # 예: http://localhost:8000/api/files/receipts/2024/01/receipt_20240115_143022.jpg
    base_url = "http://localhost:8000"  # TODO: 설정에서 가져오도록 변경 가능
    return f"{base_url}/api/files{file_path}"


def get_file_path(file_path: str) -> str:
    """
    파일의 전체 경로를 반환합니다.
    
    Args:
        file_path: 파일의 상대 경로 (DB에 저장된 경로)
        
    Returns:
        str: 파일의 전체 경로
    """
    if not file_path:
        return ""
    
    return os.path.join(settings.upload_dir, file_path)

