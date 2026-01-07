"""
통계 서비스
거래 내역 통계 계산 로직을 제공합니다.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from app.models.transaction import get_transaction_collection

logger = logging.getLogger(__name__)


async def get_today_summary(target_date: Optional[datetime] = None) -> Dict[str, float]:
    """
    오늘의 지출/수입 합계를 계산합니다.
    
    Args:
        target_date: 기준 날짜 (기본값: 오늘)
        
    Returns:
        dict: {"expense": 지출 합계, "income": 수입 합계}
    """
    if target_date is None:
        target_date = datetime.utcnow()
    
    # 오늘의 시작과 끝 시간
    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    collection = get_transaction_collection()
    
    # 지출 합계 계산
    expense_pipeline = [
        {
            "$match": {
                "type": "expense",
                "date": {
                    "$gte": start_of_day,
                    "$lte": end_of_day
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ]
    
    expense_result = await collection.aggregate(expense_pipeline).to_list(length=1)
    expense_total = expense_result[0]["total"] if expense_result else 0.0
    
    # 수입 합계 계산
    income_pipeline = [
        {
            "$match": {
                "type": "income",
                "date": {
                    "$gte": start_of_day,
                    "$lte": end_of_day
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ]
    
    income_result = await collection.aggregate(income_pipeline).to_list(length=1)
    income_total = income_result[0]["total"] if income_result else 0.0
    
    return {
        "expense": round(expense_total, 2),
        "income": round(income_total, 2)
    }


async def get_month_summary(target_date: Optional[datetime] = None) -> Dict[str, float]:
    """
    이번 달의 지출/수입 합계 및 순수입을 계산합니다.
    
    Args:
        target_date: 기준 날짜 (기본값: 오늘)
        
    Returns:
        dict: {"expense": 지출 합계, "income": 수입 합계, "netIncome": 순수입}
    """
    if target_date is None:
        target_date = datetime.utcnow()
    
    # 이번 달의 시작과 끝 시간
    start_of_month = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 다음 달의 첫 날 계산
    if target_date.month == 12:
        next_month = target_date.replace(year=target_date.year + 1, month=1, day=1)
    else:
        next_month = target_date.replace(month=target_date.month + 1, day=1)
    
    end_of_month = next_month - timedelta(microseconds=1)
    
    collection = get_transaction_collection()
    
    # 지출 합계 계산
    expense_pipeline = [
        {
            "$match": {
                "type": "expense",
                "date": {
                    "$gte": start_of_month,
                    "$lte": end_of_month
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ]
    
    expense_result = await collection.aggregate(expense_pipeline).to_list(length=1)
    expense_total = expense_result[0]["total"] if expense_result else 0.0
    
    # 수입 합계 계산
    income_pipeline = [
        {
            "$match": {
                "type": "income",
                "date": {
                    "$gte": start_of_month,
                    "$lte": end_of_month
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ]
    
    income_result = await collection.aggregate(income_pipeline).to_list(length=1)
    income_total = income_result[0]["total"] if income_result else 0.0
    
    # 순수입 계산 (수입 - 지출)
    net_income = income_total - expense_total
    
    return {
        "expense": round(expense_total, 2),
        "income": round(income_total, 2),
        "netIncome": round(net_income, 2)
    }


async def get_budget_status(target_date: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
    """
    예산 대비 사용률을 계산합니다.
    예산 기능이 구현되지 않은 경우 None을 반환합니다.
    
    Args:
        target_date: 기준 날짜 (기본값: 오늘)
        
    Returns:
        dict: {"totalBudget": 총 예산, "totalSpent": 총 지출, "usageRate": 사용률}
        또는 None (예산 기능 미구현 시)
    """
    # 예산 기능이 아직 구현되지 않았으므로 None 반환
    # TODO: 예산 기능 구현 후 이 함수를 완성
    return None


async def get_summary_statistics(target_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    요약 통계 데이터를 계산합니다.
    
    Args:
        target_date: 기준 날짜 (기본값: 오늘)
        
    Returns:
        dict: 요약 통계 데이터
    """
    if target_date is None:
        target_date = datetime.utcnow()
    
    # 오늘 통계
    today_stats = await get_today_summary(target_date)
    
    # 이번 달 통계
    month_stats = await get_month_summary(target_date)
    
    # 예산 현황 (예산 기능 구현 후)
    budget_status = await get_budget_status(target_date)
    
    result = {
        "today": today_stats,
        "thisMonth": month_stats
    }
    
    # 예산 현황이 있으면 추가
    if budget_status:
        result["budgetStatus"] = budget_status
    
    return result

