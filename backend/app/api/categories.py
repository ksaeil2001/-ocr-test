"""
카테고리 API 라우터
카테고리 CRUD 엔드포인트를 제공합니다.
"""
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from typing import Optional
import logging

from app.models.category import (
    get_category_collection,
    check_name_exists,
    prepare_category_document
)
from app.models.transaction import get_transaction_collection
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    convert_objectid_to_str
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=CategoryListResponse)
async def get_categories(
    type: Optional[str] = Query(None, description="카테고리 타입 필터 (expense/income)")
):
    """
    카테고리 목록을 조회합니다.
    
    Args:
        type: 카테고리 타입 필터 (선택)
        
    Returns:
        CategoryListResponse: 카테고리 목록 및 전체 개수
    """
    try:
        collection = get_category_collection()
        
        # 쿼리 필터 구성
        query = {}
        if type:
            if type not in ["expense", "income"]:
                raise HTTPException(
                    status_code=400,
                    detail="type은 'expense' 또는 'income'이어야 합니다."
                )
            query["type"] = type
        
        # 카테고리 조회
        cursor = collection.find(query).sort("name", 1)
        categories = await cursor.to_list(length=None)
        
        # ObjectId를 문자열로 변환
        items = [convert_objectid_to_str(cat) for cat in categories]
        
        return CategoryListResponse(
            items=items,
            total=len(items)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카테고리 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="카테고리 목록 조회에 실패했습니다.")


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(category: CategoryCreate):
    """
    새 카테고리를 생성합니다.
    
    Args:
        category: 카테고리 생성 데이터
        
    Returns:
        CategoryResponse: 생성된 카테고리
    """
    try:
        collection = get_category_collection()
        
        # 이름 중복 검증
        if await check_name_exists(category.name):
            raise HTTPException(
                status_code=400,
                detail=f"'{category.name}' 카테고리가 이미 존재합니다."
            )
        
        # 문서 준비 및 생성
        category_dict = category.model_dump()
        document = prepare_category_document(category_dict)
        
        result = await collection.insert_one(document)
        
        # 생성된 문서 조회
        created = await collection.find_one({"_id": result.inserted_id})
        if not created:
            raise HTTPException(status_code=500, detail="카테고리 생성 후 조회에 실패했습니다.")
        
        return convert_objectid_to_str(created)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카테고리 생성 실패: {e}")
        raise HTTPException(status_code=500, detail="카테고리 생성에 실패했습니다.")


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str):
    """
    특정 카테고리를 조회합니다.
    
    Args:
        category_id: 카테고리 ID
        
    Returns:
        CategoryResponse: 카테고리 정보
    """
    try:
        # ObjectId 유효성 검사
        if not ObjectId.is_valid(category_id):
            raise HTTPException(status_code=400, detail="유효하지 않은 카테고리 ID입니다.")
        
        collection = get_category_collection()
        category = await collection.find_one({"_id": ObjectId(category_id)})
        
        if not category:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")
        
        return convert_objectid_to_str(category)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카테고리 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="카테고리 조회에 실패했습니다.")


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, category: CategoryUpdate):
    """
    카테고리를 수정합니다.
    
    Args:
        category_id: 카테고리 ID
        category: 수정할 데이터
        
    Returns:
        CategoryResponse: 수정된 카테고리
    """
    try:
        # ObjectId 유효성 검사
        if not ObjectId.is_valid(category_id):
            raise HTTPException(status_code=400, detail="유효하지 않은 카테고리 ID입니다.")
        
        collection = get_category_collection()
        object_id = ObjectId(category_id)
        
        # 카테고리 존재 확인
        existing = await collection.find_one({"_id": object_id})
        if not existing:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")
        
        # 업데이트할 데이터 추출 (None이 아닌 값만)
        update_data = {k: v for k, v in category.model_dump().items() if v is not None}
        
        # 이름 변경 시 중복 검증
        if "name" in update_data:
            if await check_name_exists(update_data["name"], category_id):
                raise HTTPException(
                    status_code=400,
                    detail=f"'{update_data['name']}' 카테고리가 이미 존재합니다."
                )
        
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")
        
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
        logger.error(f"카테고리 수정 실패: {e}")
        raise HTTPException(status_code=500, detail="카테고리 수정에 실패했습니다.")


@router.delete("/{category_id}")
async def delete_category(category_id: str):
    """
    카테고리를 삭제합니다.
    사용 중인 카테고리는 삭제할 수 없습니다.
    
    Args:
        category_id: 카테고리 ID
        
    Returns:
        dict: 삭제 결과 메시지
    """
    try:
        # ObjectId 유효성 검사
        if not ObjectId.is_valid(category_id):
            raise HTTPException(status_code=400, detail="유효하지 않은 카테고리 ID입니다.")
        
        collection = get_category_collection()
        object_id = ObjectId(category_id)
        
        # 카테고리 존재 확인
        existing = await collection.find_one({"_id": object_id})
        if not existing:
            raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")
        
        # 사용 중인 카테고리 확인 (거래 내역에서 사용 중인지 확인)
        transaction_collection = get_transaction_collection()
        usage_count = await transaction_collection.count_documents({"category": existing["name"]})
        
        if usage_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"이 카테고리는 {usage_count}개의 거래 내역에서 사용 중입니다. 먼저 해당 거래 내역의 카테고리를 변경해주세요."
            )
        
        # 삭제 수행
        await collection.delete_one({"_id": object_id})
        
        return {
            "success": True,
            "message": "카테고리가 삭제되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카테고리 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail="카테고리 삭제에 실패했습니다.")

