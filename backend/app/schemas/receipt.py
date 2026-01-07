"""
Receipt 스키마
영수증 OCR 결과 및 저장을 위한 Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ReceiptItem(BaseModel):
    """영수증 상품 항목"""
    name: str = Field(..., description="상품명")
    price: float = Field(..., ge=0, description="가격")


class ReceiptOCRResponse(BaseModel):
    """OCR 처리 결과 응답 스키마"""
    date: Optional[str] = Field(None, description="날짜 (YYYY-MM-DD)")
    store: Optional[str] = Field(None, description="상호명")
    items: List[ReceiptItem] = Field(default_factory=list, description="상품 목록")
    total: Optional[float] = Field(None, ge=0, description="총액")
    category: Optional[str] = Field(None, description="카테고리")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="신뢰도 (0-1)")
    rawText: str = Field("", description="원본 텍스트")
    receiptImagePath: Optional[str] = Field(None, description="영수증 이미지 경로")


class ReceiptSaveRequest(BaseModel):
    """영수증 저장 요청 스키마"""
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    store: Optional[str] = Field(None, description="상호명")
    items: List[ReceiptItem] = Field(default_factory=list, description="상품 목록")
    total: float = Field(..., gt=0, description="총액")
    category: str = Field(..., description="카테고리")
    memo: Optional[str] = Field(None, max_length=500, description="메모")
    receiptImagePath: Optional[str] = Field(None, description="영수증 이미지 경로")
    type: str = Field("expense", description="거래 타입 (expense/income)")

