"""
Transaction 스키마
거래 내역 데이터 검증 및 직렬화를 위한 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from bson import ObjectId


def convert_objectid_to_str(doc: dict) -> dict:
    """
    MongoDB 문서의 _id를 문자열로 변환하고 id 필드로도 추가합니다.
    
    Args:
        doc: MongoDB 문서 딕셔너리
        
    Returns:
        dict: _id가 문자열로 변환되고 id 필드가 추가된 문서
    """
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
        # id 필드도 추가 (프론트엔드 호환성)
        doc["id"] = doc["_id"]
    return doc


class PyObjectId(ObjectId):
    """ObjectId를 Pydantic과 호환되도록 만드는 클래스"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class TransactionBase(BaseModel):
    """거래 내역 기본 스키마"""
    type: Literal["expense", "income"] = Field(..., description="거래 타입: expense(지출) 또는 income(수입)")
    date: datetime = Field(..., description="거래 날짜")
    amount: float = Field(..., gt=0, description="금액 (양수만 허용)")
    category: str = Field(..., min_length=1, description="카테고리 이름")
    memo: Optional[str] = Field(None, max_length=500, description="메모 (최대 500자)")
    receiptImagePath: Optional[str] = Field(None, description="영수증 이미지 파일 경로")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """금액 검증: 양수이고 소수점 2자리까지"""
        if v <= 0:
            raise ValueError('금액은 양수여야 합니다')
        # 소수점 2자리로 반올림
        return round(v, 2)

    @field_validator('memo')
    @classmethod
    def validate_memo(cls, v):
        """메모 검증: 최대 500자"""
        if v is not None and len(v) > 500:
            raise ValueError('메모는 최대 500자까지 입력 가능합니다')
        return v


class TransactionCreate(TransactionBase):
    """거래 내역 생성 스키마"""
    pass


class TransactionUpdate(BaseModel):
    """거래 내역 수정 스키마 (모든 필드 선택적)"""
    type: Optional[Literal["expense", "income"]] = Field(None, description="거래 타입")
    date: Optional[datetime] = Field(None, description="거래 날짜")
    amount: Optional[float] = Field(None, gt=0, description="금액 (양수만 허용)")
    category: Optional[str] = Field(None, min_length=1, description="카테고리 이름")
    memo: Optional[str] = Field(None, max_length=500, description="메모 (최대 500자)")
    receiptImagePath: Optional[str] = Field(None, description="영수증 이미지 파일 경로")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """금액 검증: 양수이고 소수점 2자리까지"""
        if v is not None:
            if v <= 0:
                raise ValueError('금액은 양수여야 합니다')
            return round(v, 2)
        return v

    @field_validator('memo')
    @classmethod
    def validate_memo(cls, v):
        """메모 검증: 최대 500자"""
        if v is not None and len(v) > 500:
            raise ValueError('메모는 최대 500자까지 입력 가능합니다')
        return v

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        """최소 하나의 필드는 업데이트되어야 함"""
        if all(v is None for v in self.model_dump().values()):
            raise ValueError('최소 하나의 필드는 업데이트되어야 합니다')
        return self


class TransactionResponse(TransactionBase):
    """거래 내역 응답 스키마"""
    id: str = Field(..., alias="_id", description="거래 내역 ID")
    createdAt: datetime = Field(..., description="생성 일시")
    updatedAt: datetime = Field(..., description="수정 일시")

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class TransactionListResponse(BaseModel):
    """거래 내역 목록 응답 스키마 (페이징 포함)"""
    items: list[TransactionResponse] = Field(..., description="거래 내역 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    limit: int = Field(..., description="페이지당 개수")
    total_pages: int = Field(..., description="전체 페이지 수")

