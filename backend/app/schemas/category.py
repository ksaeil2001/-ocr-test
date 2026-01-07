"""
Category 스키마
카테고리 데이터 검증 및 직렬화를 위한 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
import re


def convert_objectid_to_str(doc: dict) -> dict:
    """
    MongoDB 문서의 _id를 문자열로 변환합니다.
    
    Args:
        doc: MongoDB 문서 딕셔너리
        
    Returns:
        dict: _id가 문자열로 변환된 문서
    """
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


class CategoryBase(BaseModel):
    """카테고리 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=50, description="카테고리 이름 (고유값)")
    type: Literal["expense", "income"] = Field(..., description="카테고리 타입: expense(지출) 또는 income(수입)")
    color: str = Field(..., description="HEX 색상 코드 (#RRGGBB)")
    icon: Optional[str] = Field(None, max_length=50, description="아이콘 이름")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """이름 검증: 공백 제거 및 길이 확인"""
        if not v or not v.strip():
            raise ValueError('카테고리 이름은 필수입니다')
        return v.strip()

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """색상 코드 검증: HEX 형식 (#RRGGBB 또는 #RRGGBBAA)"""
        if not v:
            raise ValueError('색상 코드는 필수입니다')
        
        # HEX 색상 코드 패턴 (#RRGGBB 또는 #RRGGBBAA)
        hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$'
        if not re.match(hex_pattern, v):
            raise ValueError('색상 코드는 HEX 형식이어야 합니다 (#RRGGBB 또는 #RRGGBBAA)')
        
        return v.upper()  # 대문자로 정규화

    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v):
        """아이콘 이름 검증"""
        if v is not None:
            v = v.strip()
            if len(v) > 50:
                raise ValueError('아이콘 이름은 최대 50자까지 입력 가능합니다')
        return v


class CategoryCreate(CategoryBase):
    """카테고리 생성 스키마"""
    pass


class CategoryUpdate(BaseModel):
    """카테고리 수정 스키마 (모든 필드 선택적)"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="카테고리 이름")
    type: Optional[Literal["expense", "income"]] = Field(None, description="카테고리 타입")
    color: Optional[str] = Field(None, description="HEX 색상 코드")
    icon: Optional[str] = Field(None, max_length=50, description="아이콘 이름")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """이름 검증"""
        if v is not None:
            if not v.strip():
                raise ValueError('카테고리 이름은 필수입니다')
            return v.strip()
        return v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """색상 코드 검증"""
        if v is not None:
            hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$'
            if not re.match(hex_pattern, v):
                raise ValueError('색상 코드는 HEX 형식이어야 합니다 (#RRGGBB 또는 #RRGGBBAA)')
            return v.upper()
        return v

    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v):
        """아이콘 이름 검증"""
        if v is not None:
            v = v.strip()
            if len(v) > 50:
                raise ValueError('아이콘 이름은 최대 50자까지 입력 가능합니다')
        return v

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        """최소 하나의 필드는 업데이트되어야 함"""
        if all(v is None for v in self.model_dump().values()):
            raise ValueError('최소 하나의 필드는 업데이트되어야 합니다')
        return self


class CategoryResponse(CategoryBase):
    """카테고리 응답 스키마"""
    id: str = Field(..., alias="_id", description="카테고리 ID")
    createdAt: datetime = Field(..., description="생성 일시")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CategoryListResponse(BaseModel):
    """카테고리 목록 응답 스키마"""
    items: list[CategoryResponse] = Field(..., description="카테고리 목록")
    total: int = Field(..., description="전체 개수")

