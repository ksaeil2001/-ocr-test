"""
거래 내역 API 라우터
거래 내역 CRUD 엔드포인트를 제공합니다.
"""
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from datetime import datetime
from typing import Optional
import logging
import math

from app.models.transaction import (
    get_transaction_collection,
    prepare_transaction_document
)
from app.models.category import get_category_collection
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    convert_objectid_to_str
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=TransactionListResponse)
async def get_transactions(
    dateFrom: Optional[str] = Query(None, description="시작 날짜 (ISO 형식)"),
    dateTo: Optional[str] = Query(None, description="종료 날짜 (ISO 형식)"),
    category: Optional[str] = Query(None, description="카테고리 이름"),
    type: Optional[str] = Query(None, description="거래 타입 (expense/income)"),
    search: Optional[str] = Query(None, description="검색어 (메모/상호명)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(50, ge=1, le=100, description="페이지당 항목 수"),
    sort: str = Query("date", description="정렬 필드"),
    order: str = Query("desc", description="정렬 순서 (asc/desc)")
):
    """
    거래 내역 목록을 조회합니다.
    필터링, 검색, 정렬, 페이징 기능을 지원합니다.
    
    Args:
        dateFrom: 시작 날짜
        dateTo: 종료 날짜
        category: 카테고리 이름
        type: 거래 타입
        search: 검색어
        page: 페이지 번호
        limit: 페이지당 항목 수
        sort: 정렬 필드
        order: 정렬 순서
        
    Returns:
        TransactionListResponse: 거래 내역 목록 및 페이징 정보
    """
    try:
        collection = get_transaction_collection()
        
        # 쿼리 필터 구성
        query = {}
        
        # 날짜 범위 필터
        if dateFrom or dateTo:
            date_filter = {}
            if dateFrom:
                try:
                    date_from = datetime.fromisoformat(dateFrom.replace('Z', '+00:00'))
                    date_filter["$gte"] = date_from
                except ValueError:
                    raise HTTPException(status_code=400, detail="dateFrom 형식이 올바르지 않습니다.")
            if dateTo:
                try:
                    date_to = datetime.fromisoformat(dateTo.replace('Z', '+00:00'))
                    date_filter["$lte"] = date_to
                except ValueError:
                    raise HTTPException(status_code=400, detail="dateTo 형식이 올바르지 않습니다.")
            query["date"] = date_filter
        
        # 카테고리 필터
        if category:
            query["category"] = category
        
        # 타입 필터
        if type:
            if type not in ["expense", "income"]:
                raise HTTPException(
                    status_code=400,
                    detail="type은 'expense' 또는 'income'이어야 합니다."
                )
            query["type"] = type
        
        # 검색 필터 (메모에서 검색)
        if search:
            query["$or"] = [
                {"memo": {"$regex": search, "$options": "i"}},
                # 영수증이 있는 경우 상호명도 검색 가능하도록 확장 가능
            ]
        
        # 정렬 필드 및 순서 설정
        sort_order = -1 if order == "desc" else 1
        sort_fields = {
            "date": ("date", sort_order),
            "amount": ("amount", sort_order),
            "category": ("category", sort_order),
            "createdAt": ("createdAt", sort_order),
        }
        
        sort_field, sort_direction = sort_fields.get(sort, ("date", -1))
        
        # 전체 개수 조회
        total = await collection.count_documents(query)
        
        # 페이징 계산
        skip = (page - 1) * limit
        total_pages = math.ceil(total / limit) if total > 0 else 0
        
        # 거래 내역 조회
        cursor = collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
        transactions = await cursor.to_list(length=limit)
        
        # ObjectId를 문자열로 변환
        items = [convert_objectid_to_str(txn) for txn in transactions]
        
        return TransactionListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"거래 내역 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="거래 내역 목록 조회에 실패했습니다.")


@router.post("", response_model=TransactionResponse, status_code=201)
async def create_transaction(transaction: TransactionCreate):
    """
    새 거래 내역을 생성합니다.
    
    Args:
        transaction: 거래 내역 생성 데이터
        
    Returns:
        TransactionResponse: 생성된 거래 내역
    """
    try:
        collection = get_transaction_collection()
        category_collection = get_category_collection()
        
        # 카테고리 존재 여부 확인
        category_exists = await category_collection.find_one({"name": transaction.category})
        if not category_exists:
            raise HTTPException(
                status_code=400,
                detail=f"'{transaction.category}' 카테고리가 존재하지 않습니다."
            )
        
        # 문서 준비 및 생성
        transaction_dict = transaction.model_dump()
        document = prepare_transaction_document(transaction_dict, is_update=False)
        
        result = await collection.insert_one(document)
        
        # 생성된 문서 조회
        created = await collection.find_one({"_id": result.inserted_id})
        if not created:
            raise HTTPException(status_code=500, detail="거래 내역 생성 후 조회에 실패했습니다.")
        
        return convert_objectid_to_str(created)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"거래 내역 생성 실패: {e}")
        raise HTTPException(status_code=500, detail="거래 내역 생성에 실패했습니다.")


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    """
    특정 거래 내역을 조회합니다.
    
    Args:
        transaction_id: 거래 내역 ID
        
    Returns:
        TransactionResponse: 거래 내역 정보
    """
    try:
        # ObjectId 유효성 검사
        if not ObjectId.is_valid(transaction_id):
            raise HTTPException(status_code=400, detail="유효하지 않은 거래 내역 ID입니다.")
        
        collection = get_transaction_collection()
        transaction = await collection.find_one({"_id": ObjectId(transaction_id)})
        
        if not transaction:
            raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다.")
        
        return convert_objectid_to_str(transaction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"거래 내역 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="거래 내역 조회에 실패했습니다.")


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: str, transaction: TransactionUpdate):
    """
    거래 내역을 수정합니다.
    
    Args:
        transaction_id: 거래 내역 ID
        transaction: 수정할 데이터
        
    Returns:
        TransactionResponse: 수정된 거래 내역
    """
    try:
        # ObjectId 유효성 검사
        if not ObjectId.is_valid(transaction_id):
            raise HTTPException(status_code=400, detail="유효하지 않은 거래 내역 ID입니다.")
        
        collection = get_transaction_collection()
        category_collection = get_category_collection()
        object_id = ObjectId(transaction_id)
        
        # 거래 내역 존재 확인
        existing = await collection.find_one({"_id": object_id})
        if not existing:
            raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다.")
        
        # 업데이트할 데이터 추출 (None이 아닌 값만)
        update_data = {k: v for k, v in transaction.model_dump().items() if v is not None}
        
        # 카테고리 변경 시 존재 여부 확인
        if "category" in update_data:
            category_exists = await category_collection.find_one({"name": update_data["category"]})
            if not category_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"'{update_data['category']}' 카테고리가 존재하지 않습니다."
                )
        
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")
        
        # 문서 준비 (updatedAt 자동 설정)
        update_data = prepare_transaction_document(update_data, is_update=True)
        
        # 업데이트 수행
        await collection.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )
        
        # 수정된 문서 조회
        updated = await collection.find_one({"_id": object_id})
        return convert_objectid_to_str(updated)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"거래 내역 수정 실패: {e}")
        raise HTTPException(status_code=500, detail="거래 내역 수정에 실패했습니다.")


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """
    거래 내역을 삭제합니다.
    
    Args:
        transaction_id: 거래 내역 ID
        
    Returns:
        dict: 삭제 결과 메시지
    """
    try:
        # ObjectId 유효성 검사
        if not ObjectId.is_valid(transaction_id):
            raise HTTPException(status_code=400, detail="유효하지 않은 거래 내역 ID입니다.")
        
        collection = get_transaction_collection()
        object_id = ObjectId(transaction_id)
        
        # 거래 내역 존재 확인
        existing = await collection.find_one({"_id": object_id})
        if not existing:
            raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다.")
        
        # 삭제 수행
        await collection.delete_one({"_id": object_id})
        
        return {
            "success": True,
            "message": "거래 내역이 삭제되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"거래 내역 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail="거래 내역 삭제에 실패했습니다.")

