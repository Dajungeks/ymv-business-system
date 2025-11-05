"""
YMV ERP 시스템 데이터베이스 유틸리티
Database utilities for YMV ERP System
규칙 18: ConnectionWrapper 클래스 구현
"""

import streamlit as st
from datetime import datetime
import logging


class ConnectionWrapper:
    """
    데이터베이스 연결 관리 클래스 (규칙 18)
    Database connection management class
    """
    
    def __init__(self, supabase_client):
        """ConnectionWrapper 초기화"""
        self.client = supabase_client
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """로깅 설정"""
        logger = logging.getLogger('ymv_db')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def execute_query(self, operation, table, data=None, filters=None, columns="*"):
        """
        안전한 쿼리 실행
        Safe query execution with error handling
        """
        try:
            self.logger.info(f"Executing {operation} on table {table}")
            
            if operation == "SELECT":
                return self._execute_select(table, columns, filters)
            elif operation == "INSERT":
                return self._execute_insert(table, data)
            elif operation == "UPDATE":
                return self._execute_update(table, data, filters)
            elif operation == "DELETE":
                return self._execute_delete(table, filters)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            self.logger.error(f"Database operation failed: {str(e)}")
            self._handle_error(operation, table, e)
            return None
    
    def _execute_select(self, table, columns, filters):
        """SELECT 쿼리 실행"""
        query = self.client.table(table).select(columns)
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        response = query.execute()
        return response.data if response.data else []
    
    def _execute_insert(self, table, data):
        """INSERT 쿼리 실행 - ID 반환"""
        if not data:
            raise ValueError("Insert data cannot be empty")
        
        response = self.client.table(table).insert(data).execute()
        
        # ID 반환 (첫 번째 레코드의 id)
        if response.data and len(response.data) > 0:
            return response.data[0].get('id')
        return None
        
    def _execute_update(self, table, data, filters):
        """UPDATE 쿼리 실행"""
        if not data or not filters:
            raise ValueError("Update data and filters are required")
        
        # ID 필드 추출
        id_field = filters.get('id_field', 'id')
        record_id = data.get(id_field)
        
        if not record_id:
            raise ValueError(f"Record ID ({id_field}) is required for update")
        
        # 업데이트 데이터에서 ID 제거
        update_data = data.copy()
        update_data.pop(id_field, None)
        
        response = self.client.table(table).update(update_data).eq(id_field, record_id).execute()
        return response.data if response.data else []
    
    def _execute_delete(self, table, filters):
        """DELETE 쿼리 실행"""
        if not filters:
            raise ValueError("Delete filters are required")
        
        id_field = filters.get('id_field', 'id')
        record_id = filters.get('id')
        
        if not record_id:
            raise ValueError("Record ID is required for delete")
        
        response = self.client.table(table).delete().eq(id_field, record_id).execute()
        return True
    
    def _handle_error(self, operation, table, error):
        """에러 처리 및 사용자 알림"""
        error_msg = f"Database {operation} operation failed on table {table}: {str(error)}"
        self.logger.error(error_msg)
        st.error(f"데이터베이스 작업 실패: {str(error)}")
    
    def get_connection_status(self):
        """연결 상태 확인"""
        try:
            # 간단한 쿼리로 연결 테스트
            response = self.client.table("employees").select("id").limit(1).execute()
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False


class DatabaseOperations:
    """
    데이터베이스 작업 클래스
    Database operations class using ConnectionWrapper
    """
    
    def __init__(self, connection_wrapper):
        """DatabaseOperations 초기화"""
        self.db = connection_wrapper
    
    def load_data(self, table, columns="*", filters=None):
        """
        데이터 로드 (기존 load_data_from_supabase)
        Load data from database table
        """
        try:
            result = self.db.execute_query("SELECT", table, columns=columns, filters=filters)
            return result if result is not None else []
        except Exception as e:
            st.error(f"데이터 로드 실패 ({table}): {str(e)}")
            return []
    
    def save_data(self, table, data):
        """
        데이터 저장 (ID 반환)
        Save data to database table and return ID
        """
        try:
            result = self.db.execute_query("INSERT", table, data=data)
            return result  # ID 또는 None 반환
        except Exception as e:
            st.error(f"데이터 저장 실패 ({table}): {str(e)}")
            return None
    
    def update_data(self, table, data, id_field="id"):
        """
        데이터 업데이트 (기존 update_data_in_supabase)
        Update data in database table
        """
        try:
            filters = {'id_field': id_field, 'id': data.get(id_field)}
            result = self.db.execute_query("UPDATE", table, data=data, filters=filters)
            return result is not None and len(result) >= 0
        except Exception as e:
            st.error(f"데이터 업데이트 실패 ({table}): {str(e)}")
            return False
    
    def delete_data(self, table, item_id, id_field="id"):
        """
        데이터 삭제 (기존 delete_data_from_supabase)
        Delete data from database table
        """
        try:
            filters = {'id_field': id_field, 'id': item_id}
            result = self.db.execute_query("DELETE", table, filters=filters)
            return result is True
        except Exception as e:
            st.error(f"데이터 삭제 실패 ({table}): {str(e)}")
            return False
    
    def get_table_info(self, table):
        """테이블 정보 조회"""
        try:
            # 테이블의 첫 번째 레코드로 구조 파악
            result = self.load_data(table, columns="*")
            if result:
                return {
                    'columns': list(result[0].keys()),
                    'record_count': len(result),
                    'sample_record': result[0]
                }
            return {'columns': [], 'record_count': 0, 'sample_record': None}
        except Exception as e:
            st.error(f"테이블 정보 조회 실패 ({table}): {str(e)}")
            return None
    
    def bulk_insert(self, table, data_list):
        """대량 데이터 삽입"""
        try:
            result = self.db.execute_query("INSERT", table, data=data_list)
            return len(result) > 0 if result else False
        except Exception as e:
            st.error(f"대량 삽입 실패 ({table}): {str(e)}")
            return False
    
    def count_records(self, table, filters=None):
        """레코드 수 조회"""
        try:
            result = self.load_data(table, columns="id", filters=filters)
            return len(result) if result else 0
        except Exception as e:
            st.error(f"레코드 수 조회 실패 ({table}): {str(e)}")
            return 0


def create_database_operations(supabase_client):
    """
    DatabaseOperations 인스턴스 생성 헬퍼 함수
    Helper function to create DatabaseOperations instance
    """
    connection_wrapper = ConnectionWrapper(supabase_client)
    return DatabaseOperations(connection_wrapper)


# 하위 호환성을 위한 래퍼 함수들
def load_data_from_supabase(table, columns="*", filters=None, db_ops=None):
    """하위 호환성 래퍼 함수"""
    if db_ops:
        return db_ops.load_data(table, columns, filters)
    else:
        # 임시 처리 - main.py 리팩토링 완료 후 제거 예정
        st.warning("DatabaseOperations 인스턴스가 필요합니다.")
        return []

def save_data_to_supabase(table, data, db_ops=None):
    """하위 호환성 래퍼 함수"""
    if db_ops:
        return db_ops.save_data(table, data)
    else:
        st.warning("DatabaseOperations 인스턴스가 필요합니다.")
        return False

def update_data_in_supabase(table, data, id_field="id", db_ops=None):
    """하위 호환성 래퍼 함수"""
    if db_ops:
        return db_ops.update_data(table, data, id_field)
    else:
        st.warning("DatabaseOperations 인스턴스가 필요합니다.")
        return False

def delete_data_from_supabase(table, item_id, id_field="id", db_ops=None):
    """하위 호환성 래퍼 함수"""
    if db_ops:
        return db_ops.delete_data(table, item_id, id_field)
    else:
        st.warning("DatabaseOperations 인스턴스가 필요합니다.")
        return False

# ============================================
# 물류 관리 함수 (Supabase 기반)
# ============================================

def get_supabase_client():
    """Supabase 클라이언트 가져오기"""
    if 'supabase' not in st.session_state:
        st.error("Supabase 연결이 초기화되지 않았습니다.")
        return None
    return st.session_state.supabase


# ============================================
# FSC 규칙 관리 함수
# ============================================

def get_fsc_rules(search_query=None, status_filter=None):
    """FSC 규칙 목록 조회"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        query = client.table('fsc_rules').select('*')
        
        if search_query:
            query = query.ilike('rule_name', f'%{search_query}%')
        
        if status_filter == "활성":
            query = query.eq('is_active', True)
        elif status_filter == "비활성":
            query = query.eq('is_active', False)
        
        query = query.order('created_at', desc=True)
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"FSC 규칙 조회 실패: {str(e)}")
        return []


def get_fsc_rule_by_id(rule_id):
    """특정 FSC 규칙 조회"""
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.table('fsc_rules').select('*').eq('rule_id', rule_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"FSC 규칙 조회 실패: {str(e)}")
        return None


def save_fsc_rule(rule_name, min_charge, brackets_json):
    """새 FSC 규칙 저장"""
    client = get_supabase_client()
    if not client:
        return False, "Supabase 연결 실패"
    
    try:
        data = {
            'rule_name': rule_name,
            'min_charge': min_charge,
            'brackets': brackets_json,
            'is_active': True
        }
        
        response = client.table('fsc_rules').insert(data).execute()
        
        if response.data:
            return True, response.data[0]['rule_id']
        return False, "저장 실패"
    except Exception as e:
        return False, str(e)


def update_fsc_rule(rule_id, rule_name, min_charge, brackets_json):
    """FSC 규칙 수정"""
    client = get_supabase_client()
    if not client:
        return False, "Supabase 연결 실패"
    
    try:
        data = {
            'rule_name': rule_name,
            'min_charge': min_charge,
            'brackets': brackets_json
        }
        
        response = client.table('fsc_rules').update(data).eq('rule_id', rule_id).execute()
        
        if response.data:
            return True, "수정 완료"
        return False, "수정 실패"
    except Exception as e:
        return False, str(e)


def delete_fsc_rule(rule_id):
    """FSC 규칙 삭제(비활성화)"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        response = client.table('fsc_rules').update({'is_active': False}).eq('rule_id', rule_id).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"FSC 규칙 삭제 실패: {str(e)}")
        return False


def calculate_fsc(rule_id, weight):
    """FSC 금액 계산"""
    rule = get_fsc_rule_by_id(rule_id)
    
    if not rule:
        return None, "규칙을 찾을 수 없습니다"
    
    if not rule.get('is_active'):
        return None, "비활성 규칙입니다"
    
    min_charge = float(rule['min_charge'])
    brackets = rule['brackets']
    
    # JSON 파싱
    import json
    brackets_dict = json.loads(brackets) if isinstance(brackets, str) else brackets
    
    # 적용 구간 찾기
    applied_bracket = None
    unit_price = 0
    
    for bracket_range, price in brackets_dict.items():
        if '+' in bracket_range:
            min_weight = int(bracket_range.replace('+', ''))
            if weight >= min_weight:
                applied_bracket = bracket_range
                unit_price = float(price)
                break
        else:
            parts = bracket_range.split('-')
            min_weight = int(parts[0])
            max_weight = int(parts[1])
            if min_weight <= weight <= max_weight:
                applied_bracket = bracket_range
                unit_price = float(price)
                break
    
    if applied_bracket is None:
        return None, "적용 가능한 구간이 없습니다"
    
    calculated_fsc = weight * unit_price
    final_fsc = max(calculated_fsc, min_charge)
    
    return {
        'weight': weight,
        'applied_bracket': applied_bracket,
        'unit_price': unit_price,
        'calculated_fsc': calculated_fsc,
        'min_charge': min_charge,
        'final_fsc': final_fsc,
        'min_charge_applied': final_fsc == min_charge
    }, None


# ============================================
# Trucking 규칙 관리 함수
# ============================================

def get_trucking_rules(search_query=None, type_filter=None, status_filter=None):
    """Trucking 규칙 목록 조회"""
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        query = client.table('trucking_rules').select('*')
        
        if search_query:
            query = query.ilike('rule_name', f'%{search_query}%')
        
        if type_filter and type_filter != "전체":
            query = query.eq('charge_type', type_filter)
        
        if status_filter == "활성":
            query = query.eq('is_active', True)
        elif status_filter == "비활성":
            query = query.eq('is_active', False)
        
        query = query.order('charge_type').order('created_at', desc=True)
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Trucking 규칙 조회 실패: {str(e)}")
        return []


def get_trucking_rule_by_id(rule_id):
    """특정 Trucking 규칙 조회"""
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        response = client.table('trucking_rules').select('*').eq('rule_id', rule_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Trucking 규칙 조회 실패: {str(e)}")
        return None


def save_trucking_rule(rule_name, charge_type, calculation_method, fixed_charge=None, weight_brackets=None):
    """새 Trucking 규칙 저장"""
    client = get_supabase_client()
    if not client:
        return False, "Supabase 연결 실패"
    
    try:
        data = {
            'rule_name': rule_name,
            'charge_type': charge_type,
            'calculation_method': calculation_method,
            'fixed_charge': fixed_charge,
            'weight_brackets': weight_brackets,
            'is_active': True
        }
        
        response = client.table('trucking_rules').insert(data).execute()
        
        if response.data:
            return True, response.data[0]['rule_id']
        return False, "저장 실패"
    except Exception as e:
        return False, str(e)


def update_trucking_rule(rule_id, rule_name, charge_type, calculation_method, fixed_charge=None, weight_brackets=None):
    """Trucking 규칙 수정"""
    client = get_supabase_client()
    if not client:
        return False, "Supabase 연결 실패"
    
    try:
        data = {
            'rule_name': rule_name,
            'charge_type': charge_type,
            'calculation_method': calculation_method,
            'fixed_charge': fixed_charge,
            'weight_brackets': weight_brackets
        }
        
        response = client.table('trucking_rules').update(data).eq('rule_id', rule_id).execute()
        
        if response.data:
            return True, "수정 완료"
        return False, "수정 실패"
    except Exception as e:
        return False, str(e)


def delete_trucking_rule(rule_id):
    """Trucking 규칙 삭제(비활성화)"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        response = client.table('trucking_rules').update({'is_active': False}).eq('rule_id', rule_id).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"Trucking 규칙 삭제 실패: {str(e)}")
        return False


def calculate_trucking(rule_id, weight):
    """Trucking 금액 계산"""
    rule = get_trucking_rule_by_id(rule_id)
    
    if not rule:
        return None, "규칙을 찾을 수 없습니다"
    
    if not rule.get('is_active'):
        return None, "비활성 규칙입니다"
    
    rule_name = rule['rule_name']
    charge_type = rule['charge_type']
    calculation_method = rule['calculation_method']
    fixed_charge = rule.get('fixed_charge')
    weight_brackets = rule.get('weight_brackets')
    
    # 고정 요금
    if calculation_method == 'FIXED':
        return {
            'rule_name': rule_name,
            'charge_type': charge_type,
            'calculation_method': '고정요금',
            'weight': weight,
            'final_charge': fixed_charge,
            'details': f'고정요금: ${fixed_charge:,.2f}'
        }, None
    
    # 중량 기반
    import json
    brackets_dict = json.loads(weight_brackets) if isinstance(weight_brackets, str) else weight_brackets
    
    # 적용 구간 찾기
    applied_bracket = None
    unit_price = 0
    
    for bracket_range, price in brackets_dict.items():
        if '+' in bracket_range:
            min_weight = int(bracket_range.replace('+', ''))
            if weight >= min_weight:
                applied_bracket = bracket_range
                unit_price = float(price)
                break
        else:
            parts = bracket_range.split('-')
            min_weight = int(parts[0])
            max_weight = int(parts[1])
            if min_weight <= weight <= max_weight:
                applied_bracket = bracket_range
                unit_price = float(price)
                break
    
    if applied_bracket is None:
        return None, "적용 가능한 구간이 없습니다"
    
    calculated_charge = weight * unit_price
    
    return {
        'rule_name': rule_name,
        'charge_type': charge_type,
        'calculation_method': '중량기반',
        'weight': weight,
        'applied_bracket': applied_bracket,
        'unit_price': unit_price,
        'final_charge': calculated_charge,
        'details': f'{applied_bracket}kg 구간: ${unit_price}/kg × {weight}kg'
    }, None