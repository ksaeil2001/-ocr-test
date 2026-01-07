"""
통계 API 라우터
통계 데이터를 제공하는 엔드포인트를 제공합니다.
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
import logging

from app.services.statistics_service import get_summary_statistics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


@router.get("/summary")
async def get_summary(
    date: Optional[str] = Query(None, description="기준 날짜 (ISO 형식, 기본값: 오늘)")
):
    """
    요약 통계 데이터를 조회합니다.
    오늘의 지출/수입 합계, 이번 달의 지출/수입 합계 및 순수입을 반환합니다.
    
    Args:
        date: 기준 날짜 (ISO 형식, 선택)
        
    Returns:
        dict: 요약 통계 데이터
        {
            "today": {"expense": 지출, "income": 수입},
            "thisMonth": {"expense": 지출, "income": 수입, "netIncome": 순수입},
            "budgetStatus": {...} (예산 기능 구현 후)
        }
    """
    try:
        # 날짜 파싱
        target_date = None
        if date:
            try:
                target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # YYYY-MM-DD 형식인 경우
                    target_date = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="날짜 형식이 올바르지 않습니다. ISO 형식 또는 YYYY-MM-DD 형식을 사용해주세요."
                    )
        
        # 통계 계산
        statistics = await get_summary_statistics(target_date)
        
        return {
            "success": True,
            "data": statistics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"요약 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="통계 데이터 조회에 실패했습니다.")

