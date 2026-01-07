"""
OpenAI OCR 서비스
OpenAI GPT-4 Vision API를 사용하여 영수증 이미지를 분석하고 구조화된 데이터를 추출합니다.
"""
import os
import json
import base64
import asyncio
from typing import Optional, Dict, List, Any
import logging
from pathlib import Path

from openai import AsyncOpenAI
from openai import APIError, APITimeoutError, APIConnectionError

from app.config import settings
from app.services.file_service import get_file_path

logger = logging.getLogger(__name__)

# OpenAI 클라이언트 초기화
client: Optional[AsyncOpenAI] = None


def get_openai_client() -> AsyncOpenAI:
    """
    OpenAI 클라이언트 인스턴스를 반환합니다.
    
    Returns:
        AsyncOpenAI: OpenAI 클라이언트 인스턴스
        
    Raises:
        ValueError: API 키가 설정되지 않은 경우
    """
    global client
    
    if client is None:
        if not settings.openai_api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다. OPENAI_API_KEY 환경 변수를 설정해주세요.")
        
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        logger.info("OpenAI 클라이언트 초기화 완료")
    
    return client


def encode_image(image_path: str) -> str:
    """
    이미지 파일을 base64로 인코딩합니다.
    
    Args:
        image_path: 이미지 파일 경로
        
    Returns:
        str: base64 인코딩된 이미지 문자열
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_image_mime_type(image_path: str) -> str:
    """
    이미지 파일의 MIME 타입을 반환합니다.
    
    Args:
        image_path: 이미지 파일 경로
        
    Returns:
        str: MIME 타입
    """
    ext = Path(image_path).suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".heic": "image/heic",
        ".webp": "image/webp"
    }
    return mime_types.get(ext, "image/jpeg")


def create_ocr_prompt() -> str:
    """
    OCR 분석을 위한 프롬프트를 생성합니다.
    
    Returns:
        str: 프롬프트 텍스트
    """
    return """당신은 영수증을 분석하는 전문가입니다. 
다음 영수증 이미지를 분석하여 JSON 형식으로 정보를 추출해주세요.

요구사항:
1. 날짜를 YYYY-MM-DD 형식으로 추출 (날짜를 찾을 수 없으면 null)
2. 상호명 추출 (상호명을 찾을 수 없으면 null)
3. 각 상품명과 가격을 배열로 추출 (상품 정보를 찾을 수 없으면 빈 배열)
4. 총액 추출 (총액을 찾을 수 없으면 null)
5. 카테고리를 추론 (가능한 경우, 예: 식비, 교통비, 쇼핑 등. 추론 불가능하면 null)
6. 신뢰도를 0-1 사이 값으로 제공 (전체적으로 얼마나 확신하는지)
7. 원본 텍스트를 rawText 필드에 포함 (가능한 한 많이 추출)

JSON 형식:
{
  "date": "YYYY-MM-DD 또는 null",
  "store": "상호명 또는 null",
  "items": [
    {"name": "상품명", "price": 금액}
  ],
  "total": 총액 또는 null,
  "category": "카테고리명 또는 null",
  "confidence": 0.0-1.0,
  "rawText": "추출된 원본 텍스트"
}

반드시 유효한 JSON 형식으로만 응답하세요. 다른 설명이나 텍스트는 포함하지 마세요."""


async def parse_ocr_response(response_text: str) -> Dict[str, Any]:
    """
    OpenAI API 응답 텍스트를 파싱하여 구조화된 데이터로 변환합니다.
    
    Args:
        response_text: API 응답 텍스트
        
    Returns:
        dict: 파싱된 OCR 결과
        
    Raises:
        ValueError: JSON 파싱 실패 시
    """
    try:
        # 응답 텍스트에서 JSON 부분만 추출 (마크다운 코드 블록 제거)
        text = response_text.strip()
        
        # JSON 코드 블록이 있는 경우 제거
        if text.startswith("```json"):
            text = text[7:]  # ```json 제거
        elif text.startswith("```"):
            text = text[3:]  # ``` 제거
        
        if text.endswith("```"):
            text = text[:-3]  # ``` 제거
        
        text = text.strip()
        
        # JSON 파싱
        data = json.loads(text)
        
        # 기본값 설정
        result = {
            "date": data.get("date"),
            "store": data.get("store"),
            "items": data.get("items", []),
            "total": data.get("total"),
            "category": data.get("category"),
            "confidence": data.get("confidence", 0.0),
            "rawText": data.get("rawText", "")
        }
        
        # 타입 검증 및 변환
        if result["total"] is not None:
            try:
                result["total"] = float(result["total"])
            except (ValueError, TypeError):
                result["total"] = None
        
        if result["confidence"] is not None:
            try:
                result["confidence"] = float(result["confidence"])
                # 0-1 범위로 제한
                result["confidence"] = max(0.0, min(1.0, result["confidence"]))
            except (ValueError, TypeError):
                result["confidence"] = 0.0
        
        # items 검증
        if not isinstance(result["items"], list):
            result["items"] = []
        
        # items 내부 항목 검증
        validated_items = []
        for item in result["items"]:
            if isinstance(item, dict) and "name" in item and "price" in item:
                try:
                    validated_items.append({
                        "name": str(item["name"]),
                        "price": float(item["price"])
                    })
                except (ValueError, TypeError):
                    continue
        result["items"] = validated_items
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 실패: {e}")
        logger.error(f"응답 텍스트: {response_text[:500]}")
        raise ValueError(f"OCR 응답을 파싱할 수 없습니다: {e}")
    except Exception as e:
        logger.error(f"응답 파싱 중 오류 발생: {e}")
        raise ValueError(f"응답 처리 중 오류가 발생했습니다: {e}")


async def process_receipt_image(image_path: str, max_retries: int = 3, timeout: int = 30) -> Dict[str, Any]:
    """
    영수증 이미지를 OpenAI Vision API로 처리하여 구조화된 데이터를 반환합니다.
    
    Args:
        image_path: 이미지 파일의 상대 경로 (DB에 저장된 경로) 또는 절대 경로
        max_retries: 최대 재시도 횟수 (기본값: 3)
        timeout: 타임아웃 시간 (초, 기본값: 30)
        
    Returns:
        dict: OCR 분석 결과
        {
            "date": str | None,
            "store": str | None,
            "items": List[dict],
            "total": float | None,
            "category": str | None,
            "confidence": float,
            "rawText": str
        }
        
    Raises:
        ValueError: API 키가 없거나 이미지 파일을 찾을 수 없는 경우
        HTTPException: API 호출 실패 시
    """
    # OpenAI 클라이언트 가져오기
    try:
        openai_client = get_openai_client()
    except ValueError as e:
        logger.error(str(e))
        raise
    
    # 이미지 파일 경로 확인 및 변환
    if not os.path.isabs(image_path):
        # 상대 경로인 경우 전체 경로로 변환
        full_image_path = get_file_path(image_path)
    else:
        full_image_path = image_path
    
    # 파일 존재 확인
    if not os.path.exists(full_image_path):
        raise ValueError(f"이미지 파일을 찾을 수 없습니다: {full_image_path}")
    
    # 이미지 인코딩
    try:
        base64_image = encode_image(full_image_path)
        mime_type = get_image_mime_type(full_image_path)
    except Exception as e:
        logger.error(f"이미지 인코딩 실패: {e}")
        raise ValueError(f"이미지 파일을 읽을 수 없습니다: {e}")
    
    # 프롬프트 생성
    prompt = create_ocr_prompt()
    
    # 재시도 로직
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"OCR 처리 시도 {attempt}/{max_retries}: {image_path}")
            
            # OpenAI Vision API 호출
            response = await asyncio.wait_for(
                openai_client.chat.completions.create(
                    model="gpt-4o",  # 또는 "gpt-4-vision-preview"
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.1  # 낮은 temperature로 일관성 있는 결과
                ),
                timeout=timeout
            )
            
            # 응답 텍스트 추출
            response_text = response.choices[0].message.content
            
            if not response_text:
                raise ValueError("OpenAI API가 빈 응답을 반환했습니다.")
            
            # 응답 파싱
            result = await parse_ocr_response(response_text)
            
            logger.info(f"OCR 처리 성공: {image_path}, 신뢰도: {result.get('confidence', 0.0)}")
            return result
            
        except asyncio.TimeoutError:
            last_error = f"OCR 처리 타임아웃 ({timeout}초 초과)"
            logger.warning(f"시도 {attempt}/{max_retries} 실패: {last_error}")
            
        except (APITimeoutError, APIConnectionError) as e:
            last_error = f"API 연결 오류: {str(e)}"
            logger.warning(f"시도 {attempt}/{max_retries} 실패: {last_error}")
            
        except APIError as e:
            # API 에러는 재시도하지 않음 (인증 오류 등)
            logger.error(f"OpenAI API 오류: {e}")
            raise ValueError(f"OpenAI API 호출 실패: {e}")
            
        except ValueError as e:
            # 파싱 오류는 재시도하지 않음
            logger.error(f"응답 파싱 오류: {e}")
            raise
            
        except Exception as e:
            last_error = f"예상치 못한 오류: {str(e)}"
            logger.error(f"시도 {attempt}/{max_retries} 실패: {last_error}")
        
        # 마지막 시도가 아니면 잠시 대기 후 재시도
        if attempt < max_retries:
            wait_time = attempt * 2  # 지수 백오프 (2초, 4초, 6초...)
            logger.info(f"{wait_time}초 후 재시도...")
            await asyncio.sleep(wait_time)
    
    # 모든 재시도 실패
    logger.error(f"OCR 처리 실패 (최대 재시도 횟수 초과): {last_error}")
    raise ValueError(f"OCR 처리에 실패했습니다: {last_error}")

