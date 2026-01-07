"""
카테고리 샘플 데이터 추가 스크립트
"""
import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import connect_to_mongo, close_mongo_connection
from app.models.category import get_category_collection, prepare_category_document


# 샘플 카테고리 데이터
SAMPLE_CATEGORIES = [
    # 지출 카테고리
    {"name": "식비", "type": "expense", "color": "#FF6B6B", "icon": "restaurant"},
    {"name": "교통비", "type": "expense", "color": "#4ECDC4", "icon": "directions_transit"},
    {"name": "쇼핑", "type": "expense", "color": "#FFE66D", "icon": "shopping_bag"},
    {"name": "의료비", "type": "expense", "color": "#95E1D3", "icon": "local_hospital"},
    {"name": "교육비", "type": "expense", "color": "#AA96DA", "icon": "school"},
    {"name": "통신비", "type": "expense", "color": "#A8E6CF", "icon": "phone"},
    {"name": "주거비", "type": "expense", "color": "#FFD3A5", "icon": "home"},
    {"name": "문화생활", "type": "expense", "color": "#C7CEEA", "icon": "movie"},
    {"name": "기타", "type": "expense", "color": "#D4D4D4", "icon": "more_horiz"},
    
    # 수입 카테고리
    {"name": "급여", "type": "income", "color": "#4ECDC4", "icon": "account_balance"},
    {"name": "부수입", "type": "income", "color": "#95E1D3", "icon": "attach_money"},
    {"name": "투자수익", "type": "income", "color": "#AA96DA", "icon": "trending_up"},
    {"name": "기타수입", "type": "income", "color": "#A8E6CF", "icon": "add_circle"},
]


async def add_sample_categories():
    """샘플 카테고리 데이터를 추가합니다."""
    try:
        # MongoDB 연결
        await connect_to_mongo()
        print("MongoDB 연결 성공")
        
        collection = get_category_collection()
        
        # 기존 카테고리 확인
        existing_categories = await collection.find({}).to_list(length=None)
        existing_names = {cat["name"] for cat in existing_categories}
        print(f"기존 카테고리 개수: {len(existing_categories)}")
        
        # 샘플 데이터 추가
        added_count = 0
        skipped_count = 0
        
        for category_data in SAMPLE_CATEGORIES:
            if category_data["name"] in existing_names:
                print(f"  - '{category_data['name']}' 이미 존재하여 건너뜀")
                skipped_count += 1
                continue
            
            # 문서 준비 및 추가
            document = prepare_category_document(category_data)
            result = await collection.insert_one(document)
            
            print(f"  + '{category_data['name']}' 추가 완료 (ID: {result.inserted_id})")
            added_count += 1
        
        print(f"\n완료: {added_count}개 추가, {skipped_count}개 건너뜀")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # MongoDB 연결 종료
        await close_mongo_connection()
        print("MongoDB 연결 종료")


if __name__ == "__main__":
    asyncio.run(add_sample_categories())

