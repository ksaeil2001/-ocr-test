"""
영수증 OCR API 라우터
영수증 이미지 업로드, OCR 처리, 거래 내역 저장 엔드포인트를 제공합니다.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from datetime import datetime
from typing import Optional
import logging

from app.services.file_service import save_uploaded_file, delete_file
from app.services.ocr_service import process_receipt_image
from app.models.transaction import (
    get_transaction_collection,
    prepare_transaction_document
)
from app.models.category import get_category_collection
from app.schemas.receipt import ReceiptOCRResponse, ReceiptSaveRequest
from app.schemas.transaction import TransactionResponse, convert_objectid_to_str

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/receipt", tags=["receipts"])


@router.post("/ocr", response_model=ReceiptOCRResponse)
async def process_receipt_ocr(file: UploadFile = File(...)):
    """
    영수증 이미지를 업로드하고 OCR 처리를 수행합니다.
    
    Args:
        file: 업로드된 이미지 파일
        
    Returns:
        ReceiptOCRResponse: OCR 처리 결과
    """
    saved_file_path = None
    
    try:
        # 파일 저장
        logger.info(f"파일 업로드 시작: {file.filename}")
        saved_file_path = await save_uploaded_file(file)
        logger.info(f"파일 저장 완료: {saved_file_path}")
        
        # OCR 처리
        logger.info(f"OCR 처리 시작: {saved_file_path}")
        ocr_result = await process_receipt_image(saved_file_path)
        logger.info(f"OCR 처리 완료: 신뢰도 {ocr_result.get('confidence', 0.0)}")
        
        # 응답 데이터 구성
        response_data = {
            "date": ocr_result.get("date"),
            "store": ocr_result.get("store"),
            "items": ocr_result.get("items", []),
            "total": ocr_result.get("total"),
            "category": ocr_result.get("category"),
            "confidence": ocr_result.get("confidence", 0.0),
            "rawText": ocr_result.get("rawText", ""),
            "receiptImagePath": saved_file_path
        }
        
        return ReceiptOCRResponse(**response_data)
        
    except ValueError as e:
        # OCR 처리 실패 또는 파일 검증 실패
        logger.error(f"OCR 처리 실패: {e}")
        
        # 저장된 파일이 있으면 삭제
        if saved_file_path:
            try:
                delete_file(saved_file_path)
                logger.info(f"실패한 파일 삭제: {saved_file_path}")
            except Exception as delete_error:
                logger.warning(f"파일 삭제 실패: {delete_error}")
        
        raise HTTPException(status_code=400, detail=str(e))
        
    except HTTPException:
        # 파일 서비스에서 발생한 HTTPException은 그대로 전달
        if saved_file_path:
            try:
                delete_file(saved_file_path)
            except Exception:
                pass
        raise
        
    except Exception as e:
        logger.error(f"영수증 OCR 처리 중 예상치 못한 오류 발생: {e}")
        
        # 저장된 파일이 있으면 삭제
        if saved_file_path:
            try:
                delete_file(saved_file_path)
            except Exception:
                pass
        
        raise HTTPException(status_code=500, detail="OCR 처리 중 오류가 발생했습니다.")


@router.post("/save", response_model=TransactionResponse, status_code=201)
async def save_receipt_transaction(request: ReceiptSaveRequest):
    """
    OCR 결과를 거래 내역으로 저장합니다.
    
    Args:
        request: 영수증 저장 요청 데이터
        
    Returns:
        TransactionResponse: 생성된 거래 내역
    """
    try:
        collection = get_transaction_collection()
        category_collection = get_category_collection()
        
        # 카테고리 존재 여부 확인
        category_exists = await category_collection.find_one({"name": request.category})
        if not category_exists:
            raise HTTPException(
                status_code=400,
                detail=f"'{request.category}' 카테고리가 존재하지 않습니다."
            )
        
        # 날짜 파싱
        try:
            transaction_date = datetime.fromisoformat(request.date.replace('Z', '+00:00'))
        except ValueError:
            # YYYY-MM-DD 형식인 경우
            try:
                transaction_date = datetime.strptime(request.date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용해주세요."
                )
        
        # 거래 타입 검증
        if request.type not in ["expense", "income"]:
            raise HTTPException(
                status_code=400,
                detail="type은 'expense' 또는 'income'이어야 합니다."
            )
        
        # 거래 내역 데이터 구성
        transaction_dict = {
            "type": request.type,
            "date": transaction_date,
            "amount": request.total,
            "category": request.category,
            "memo": request.memo or "",
            "receiptImagePath": request.receiptImagePath
        }
        
        # 메모에 상호명 추가 (있는 경우)
        if request.store:
            store_memo = f"상호: {request.store}"
            if transaction_dict["memo"]:
                transaction_dict["memo"] = f"{transaction_dict['memo']} | {store_memo}"
            else:
                transaction_dict["memo"] = store_memo
        
        # 문서 준비 및 생성
        document = prepare_transaction_document(transaction_dict, is_update=False)
        
        result = await collection.insert_one(document)
        
        # 생성된 문서 조회
        created = await collection.find_one({"_id": result.inserted_id})
        if not created:
            raise HTTPException(status_code=500, detail="거래 내역 생성 후 조회에 실패했습니다.")
        
        logger.info(f"거래 내역 저장 완료: {result.inserted_id}")
        
        return convert_objectid_to_str(created)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"거래 내역 저장 실패: {e}")
        raise HTTPException(status_code=500, detail="거래 내역 저장에 실패했습니다.")

