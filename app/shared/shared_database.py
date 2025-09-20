# app/shared/database.py
import streamlit as st
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class LocalDatabase:
    """로컬 파일 기반 데이터베이스 (Supabase 연결 전까지 사용)"""
    
    def __init__(self):
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        
        # 테이블별 파일 매핑
        self.tables = {
            'users': 'users.json',
            'customers': 'customers.json',
            'products': 'products.json',
            'purchases': 'purchases.json',
            'expenses': 'expenses.json',
            'quotations': 'quotations.json',
            'quotation_items': 'quotation_items.json'
        }
        
        # 초기 데이터 설정
        self._initialize_default_data()
    
    def _initialize_default_data(self):
        """기본 데이터 초기화"""
        # 기본 사용자 데이터
        if not self._file_exists('users'):
            default_users = [
                {
                    'id': 1,
                    'username': 'Master',
                    'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeVMstX6P5P3OqwJ2',
                    'full_name': 'System Administrator',
                    'email': 'admin@ymv.com',
                    'department': 'IT',
                    'position': 'Administrator',
                    'role': 'master',
                    'is_active': True,
                    'created_at': datetime.now().isoformat()
                }
            ]
            self._save_to_file('users', default_users)
        
        # 기본 고객 데이터
        if not self._file_exists('customers'):
            default_customers = [
                {
                    'id': 1,
                    'company_name': 'ABC 제조업체',
                    'contact_person': '김철수',
                    'position': '구매팀장',
                    'phone': '010-1234-5678',
                    'email': 'kim@abc.com',
                    'industry': '제조업',
                    'is_active': True,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 2,
                    'company_name': 'XYZ 무역회사',
                    'contact_person': '이영희',
                    'position': '영업과장',
                    'phone': '010-9876-5432',
                    'email': 'lee@xyz.com',
                    'industry': '무역업',
                    'is_active': True,
                    'created_at': datetime.now().isoformat()
                }
            ]
            self._save_to_file('customers', default_customers)
        
        # 기본 제품 데이터
        if not self._file_exists('products'):
            default_products = [
                {
                    'id': 1,
                    'product_code': 'HR001',
                    'product_name': '핫런너 시스템 A형',
                    'category': '핫런너',
                    'unit': '세트',
                    'unit_price': 1500.00,
                    'currency': 'USD',
                    'supplier': '핫런너코리아',
                    'stock_quantity': 10,
                    'is_active': True,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 2,
                    'product_code': 'SP001',
                    'product_name': '플라스틱 부품 A',
                    'category': '판매제품',
                    'unit': '개',
                    'unit_price': 5.50,
                    'currency': 'USD',
                    'supplier': '부품공급업체',
                    'stock_quantity': 100,
                    'is_active': True,
                    'created_at': datetime.now().isoformat()
                }
            ]
            self._save_to_file('products', default_products)
    
    def _file_exists(self, table_name: str) -> bool:
        """파일 존재 여부 확인"""
        filepath = self.data_dir / self.tables[table_name]
        return filepath.exists()
    
    def _load_from_file(self, table_name: str) -> List[Dict[str, Any]]:
        """파일에서 데이터 로드"""
        filepath = self.data_dir / self.tables[table_name]
        
        if not filepath.exists():
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_to_file(self, table_name: str, data: List[Dict[str, Any]]):
        """파일에 데이터 저장"""
        filepath = self.data_dir / self.tables[table_name]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def _get_next_id(self, table_name: str) -> int:
        """다음 ID 가져오기"""
        data = self._load_from_file(table_name)
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1
    
    def select(self, table_name: str, where: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """데이터 조회"""
        data = self._load_from_file(table_name)
        
        if where is None:
            return data
        
        # 간단한 WHERE 조건 처리
        filtered_data = []
        for item in data:
            match = True
            for key, value in where.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                filtered_data.append(item)
        
        return filtered_data
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 삽입"""
        existing_data = self._load_from_file(table_name)
        
        # ID 자동 생성
        if 'id' not in data:
            data['id'] = self._get_next_id(table_name)
        
        # 생성 시간 추가
        if 'created_at' not in data:
            data['created_at'] = datetime.now().isoformat()
        
        existing_data.append(data)
        self._save_to_file(table_name, existing_data)
        
        return data
    
    def update(self, table_name: str, data: Dict[str, Any], where: Dict[str, Any]):
        """데이터 업데이트"""
        existing_data = self._load_from_file(table_name)
        
        for item in existing_data:
            match = True
            for key, value in where.items():
                if item.get(key) != value:
                    match = False
                    break
            
            if match:
                item.update(data)
                item['updated_at'] = datetime.now().isoformat()
        
        self._save_to_file(table_name, existing_data)
        return True
    
    def delete(self, table_name: str, where: Dict[str, Any]):
        """데이터 삭제"""
        existing_data = self._load_from_file(table_name)
        
        filtered_data = []
        for item in existing_data:
            match = True
            for key, value in where.items():
                if item.get(key) != value:
                    match = False
                    break
            
            if not match:  # 조건에 맞지 않는 항목만 유지
                filtered_data.append(item)
        
        self._save_to_file(table_name, filtered_data)
        return True

# 전역 데이터베이스 인스턴스
@st.cache_resource
def get_database():
    """캐시된 데이터베이스 연결 인스턴스 반환"""
    return LocalDatabase()

# 사용자 인증 함수
def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """사용자 인증"""
    db = get_database()
    users = db.select('users', {'username': username, 'is_active': True})
    
    if not users:
        return None
    
    user = users[0]
    
    # 간단한 비밀번호 확인 (실제로는 bcrypt 사용)
    if username == 'Master' and password == '1023':
        return user
    
    return None