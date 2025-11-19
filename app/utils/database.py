import streamlit as st
from supabase import create_client, Client
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO)

class ConnectionWrapper:
    """Supabase 연결 래퍼 클래스"""
    
    def __init__(self, client: Client):
        self.client = client
    
    def table(self, table_name: str):
        """테이블 접근"""
        try:
            return self.client.table(table_name)
        except Exception as e:
            logging.error(f"테이블 접근 오류 ({table_name}): {str(e)}")
            raise

def get_connection() -> ConnectionWrapper:
    """Supabase 연결 가져오기"""
    try:
        url = st.secrets["SUPABASE_URL"]  # ✅ 맞음
        key = st.secrets["SUPABASE_ANON_KEY"]  # ✅ 맞음    
        client = create_client(url, key)
        return ConnectionWrapper(client)
    except Exception as e:
        logging.error(f"Supabase 연결 오류: {str(e)}")
        raise

# ============================================
# 범용 CRUD 함수
# ============================================

def save_data(table_name: str, data: Dict[str, Any]) -> Optional[Dict]:
    """데이터 저장"""
    try:
        conn = get_connection()
        result = conn.table(table_name).insert(data).execute()
        
        if result.data:
            logging.info(f"데이터 저장 성공: {table_name}")
            return result.data[0]
        return None
    except Exception as e:
        logging.error(f"데이터 저장 오류 ({table_name}): {str(e)}")
        return None

def load_data(table_name: str, columns: str = "*", filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
    """
    데이터 로드
    Args:
        table_name: 테이블 명
        columns: 선택할 컬럼 (호환성을 위해 존재, 항상 "*" 사용)
        filters: 필터 조건 딕셔너리
    Returns:
        데이터 리스트
    """
    try:
        conn = get_connection()
        query = conn.table(table_name).select("*")  # columns 인자는 무시하고 항상 "*" 사용
        
        if filters and isinstance(filters, dict):  # ✅ dict 타입 체크 추가
            for key, value in filters.items():
                query = query.eq(key, value)
        
        result = query.execute()
        return result.data if result.data else []
    except Exception as e:
        logging.error(f"데이터 로드 오류 ({table_name}): {str(e)}")
        return []

def update_data(table_name: str, data: Dict[str, Any]) -> bool:
    """데이터 수정"""
    try:
        record_id = data.pop('id')
        data['updated_at'] = datetime.now().isoformat()
        
        conn = get_connection()
        result = conn.table(table_name).update(data).eq('id', record_id).execute()
        
        if result.data:
            logging.info(f"데이터 수정 성공: {table_name}, id={record_id}")
            return True
        return False
    except Exception as e:
        logging.error(f"데이터 수정 오류 ({table_name}): {str(e)}")
        return False

def delete_data(table_name: str, record_id: int) -> bool:
    """데이터 삭제"""
    try:
        conn = get_connection()
        result = conn.table(table_name).delete().eq('id', record_id).execute()
        
        logging.info(f"데이터 삭제 성공: {table_name}, id={record_id}")
        return True
    except Exception as e:
        logging.error(f"데이터 삭제 오류 ({table_name}, id={record_id}): {str(e)}")
        return False

# ============================================
# 고객 관련 함수
# ============================================

def load_customers(table_name: str) -> List[Dict]:
    """고객 목록 로드"""
    return load_data(table_name)

def save_customer(table_name: str, data: Dict[str, Any]) -> Optional[Dict]:
    """고객 저장"""
    return save_data(table_name, data)

def update_customer(table_name: str, data: Dict[str, Any]) -> bool:
    """고객 수정"""
    return update_data(table_name, data)

def delete_customer(table_name: str, customer_id: int) -> bool:
    """고객 삭제"""
    return delete_data(table_name, customer_id)

# ============================================
# 견적 관련 함수
# ============================================

def load_quotations(table_name: str) -> List[Dict]:
    """견적서 목록 로드"""
    try:
        conn = get_connection()
        result = conn.table(table_name).select("*").order('created_at', desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logging.error(f"견적서 로드 오류 ({table_name}): {str(e)}")
        return []

def save_quotation(table_name: str, data: Dict[str, Any]) -> Optional[Dict]:
    """견적서 저장"""
    return save_data(table_name, data)

def update_quotation(table_name: str, data: Dict[str, Any]) -> bool:
    """견적서 수정"""
    return update_data(table_name, data)

def delete_quotation(table_name: str, quotation_id: int) -> bool:
    """견적서 삭제"""
    return delete_data(table_name, quotation_id)

def get_next_quotation_number(table_name: str, year: int) -> str:
    """다음 견적 번호 생성"""
    try:
        conn = get_connection()
        
        result = conn.table(table_name)\
            .select("quotation_number")\
            .ilike('quotation_number', f'{year}%')\
            .execute()
        
        if result.data:
            numbers = [int(q['quotation_number'].split('-')[-1]) for q in result.data if q.get('quotation_number')]
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1
        
        return f"{year}-{next_num:04d}"
    except Exception as e:
        logging.error(f"견적 번호 생성 오류 ({table_name}): {str(e)}")
        return f"{year}-0001"

# ============================================
# 영업 활동 관련 함수
# ============================================

def save_sales_activity(table_name: str, data: Dict[str, Any]) -> Optional[Dict]:
    """영업 활동 저장"""
    try:
        conn = get_connection()
        result = conn.table(table_name).insert(data).execute()
        
        if result.data:
            logging.info(f"영업 활동 저장 성공: {table_name}")
            return result.data[0]
        return None
    except Exception as e:
        logging.error(f"영업 활동 저장 오류 ({table_name}): {str(e)}")
        return None

def load_sales_activities(table_name: str, limit: Optional[int] = None) -> List[Dict]:
    """전체 영업 활동 로드"""
    try:
        conn = get_connection()
        query = conn.table(table_name).select("*").order('activity_date', desc=True)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        return result.data if result.data else []
    except Exception as e:
        logging.error(f"영업 활동 로드 오류 ({table_name}): {str(e)}")
        return []

def load_customer_activities(table_name: str, customer_id: int) -> List[Dict]:
    """고객별 영업 활동 로드"""
    try:
        conn = get_connection()
        result = conn.table(table_name)\
            .select("*")\
            .eq('customer_id', customer_id)\
            .order('activity_date', desc=True)\
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        logging.error(f"고객 영업 활동 로드 오류 ({table_name}, customer_id={customer_id}): {str(e)}")
        return []

def update_sales_activity(table_name: str, data: Dict[str, Any]) -> bool:
    """영업 활동 수정"""
    try:
        activity_id = data.pop('id')
        data['updated_at'] = datetime.now().isoformat()
        
        conn = get_connection()
        result = conn.table(table_name)\
            .update(data)\
            .eq('id', activity_id)\
            .execute()
        
        if result.data:
            logging.info(f"영업 활동 수정 성공: {table_name}, id={activity_id}")
            return True
        return False
    except Exception as e:
        logging.error(f"영업 활동 수정 오류 ({table_name}): {str(e)}")
        return False

def delete_sales_activity(table_name: str, activity_id: int) -> bool:
    """영업 활동 삭제"""
    try:
        conn = get_connection()
        result = conn.table(table_name)\
            .delete()\
            .eq('id', activity_id)\
            .execute()
        
        logging.info(f"영업 활동 삭제 성공: {table_name}, id={activity_id}")
        return True
    except Exception as e:
        logging.error(f"영업 활동 삭제 오류 ({table_name}, id={activity_id}): {str(e)}")
        return False

def get_activity_statistics(table_name: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
    """영업 활동 통계"""
    try:
        conn = get_connection()
        query = conn.table(table_name).select("*")
        
        if start_date:
            query = query.gte('activity_date', start_date)
        if end_date:
            query = query.lte('activity_date', end_date)
        
        result = query.execute()
        return result.data if result.data else []
    except Exception as e:
        logging.error(f"영업 활동 통계 오류 ({table_name}): {str(e)}")
        return []

def load_activities_by_date_range(table_name: str, start_date: str, end_date: str) -> List[Dict]:
    """날짜 범위로 영업 활동 로드"""
    try:
        conn = get_connection()
        result = conn.table(table_name)\
            .select("*")\
            .gte('activity_date', start_date)\
            .lte('activity_date', end_date)\
            .order('activity_date', desc=True)\
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        logging.error(f"날짜 범위 활동 로드 오류 ({table_name}): {str(e)}")
        return []

def get_upcoming_actions(table_name: str, days: int = 7) -> List[Dict]:
    """다가오는 후속 조치 로드"""
    try:
        today = date.today()
        future_date = today + timedelta(days=days)
        
        conn = get_connection()
        result = conn.table(table_name)\
            .select("*")\
            .gte('next_action_date', today.isoformat())\
            .lte('next_action_date', future_date.isoformat())\
            .not_.is_('next_action_date', 'null')\
            .order('next_action_date', desc=False)\
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        logging.error(f"다가오는 후속 조치 로드 오류 ({table_name}): {str(e)}")
        return []

# ============================================
# 물류 관리 함수 (기존 코드 유지)
# ============================================

def get_supabase_client():
    """Supabase 클라이언트 가져오기"""
    if 'supabase' not in st.session_state:
        st.error("Supabase 연결이 초기화되지 않았습니다.")
        return None
    return st.session_state.supabase

# FSC 규칙 관리 함수
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
    
    import json
    brackets_dict = json.loads(brackets) if isinstance(brackets, str) else brackets
    
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

# Trucking 규칙 관리 함수
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
    
    if calculation_method == 'FIXED':
        return {
            'rule_name': rule_name,
            'charge_type': charge_type,
            'calculation_method': '고정요금',
            'weight': weight,
            'final_charge': fixed_charge,
            'details': f'고정요금: ${fixed_charge:,.2f}'
        }, None
    
    import json
    brackets_dict = json.loads(weight_brackets) if isinstance(weight_brackets, str) else weight_brackets
    
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

# ============================================
# 기타 유틸리티 함수
# ============================================

def test_connection() -> bool:
    """데이터베이스 연결 테스트"""
    try:
        conn = get_connection()
        result = conn.table('customers_ymv').select("id").limit(1).execute()
        logging.info("데이터베이스 연결 성공")
        return True
    except Exception as e:
        logging.error(f"데이터베이스 연결 실패: {str(e)}")
        return False

def create_database_operations(supabase_client):
    """
    DatabaseOperations 인스턴스 생성 (main.py 호환용)
    """
    class SimpleDBOperations:
        def __init__(self, client):
            self.client = client
        
        def load_data(self, table_name, columns="*", filters=None, *args, **kwargs):
            """
            데이터 로드 (유연한 인자 처리)
            Args:
                table_name: 테이블 명
                columns: 컬럼 선택 (호환성용, 무시됨)
                filters: 필터 조건
            """
            return load_data(table_name, columns, filters)
        def save_data(self, table_name, data, *args, **kwargs):
            """데이터 저장 (유연한 인자 처리)"""
            return save_data(table_name, data)
        
        def update_data(self, table_name, *args, **kwargs):
            """
            데이터 수정 (유연한 인자 처리)
            호출 패턴:
            1. update_data(table_name, record_id, data) → data에 id 추가
            2. update_data(table_name, data) where data contains 'id'
            """
            if len(args) == 2:
                # 패턴 1: (record_id, data)
                record_id, data = args
                # data에 id 추가해서 전역 함수 호출
                data_with_id = {**data, 'id': record_id}
                return update_data(table_name, data_with_id)
            elif len(args) == 1:
                # 패턴 2: (data) where data contains 'id'
                data = args[0]
                if isinstance(data, dict) and 'id' in data:
                    return update_data(table_name, data)
                else:
                    logging.error(f"update_data: data must contain 'id' field")
                    return False
            else:
                logging.error(f"update_data: invalid arguments count: {len(args)}")
                return False 


        def delete_data(self, table_name, record_id, *args, **kwargs):
            """데이터 삭제 (유연한 인자 처리)"""
            return delete_data(table_name, record_id)
    
    return SimpleDBOperations(supabase_client)

def test_connection() -> bool:
    """데이터베이스 연결 테스트"""
    try:
        conn = get_connection()
        result = conn.table('customers_ymv').select("id").limit(1).execute()
        logging.info("데이터베이스 연결 성공")
        return True
    except Exception as e:
        logging.error(f"데이터베이스 연결 실패: {str(e)}")
        return False

def delete_quotation_items_by_quotation_id(table_name: str, quotation_id: int) -> bool:
    """견적서 ID로 모든 항목 삭제"""
    try:
        conn = get_connection()
        result = conn.table(table_name).delete().eq('quotation_id', quotation_id).execute()
        
        logging.info(f"견적 항목 삭제 성공: {table_name}, quotation_id={quotation_id}")
        return True
    except Exception as e:
        logging.error(f"견적 항목 삭제 오류 ({table_name}, quotation_id={quotation_id}): {str(e)}")
        return False