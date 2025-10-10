"""
YMV ERP 시스템 물류 관련 데이터베이스 함수
Logistics-related database functions
"""

import streamlit as st
import json
from datetime import datetime, timedelta
from utils.database import get_supabase_client  # Import


# ==========================================
# FSC 규칙 관리 함수
# ==========================================

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


def get_fsc_rule_by_id(id):
    """ID로 특정 FSC 규칙 조회"""
    try:
        client = get_supabase_client()
        response = client.table('fsc_rules').select('*').eq('rule_id', id).execute()
        
        if response.data:
            return response.data[0]
        return None
            
    except Exception as e:
        st.error(f"FSC 규칙 조회 실패: {str(e)}")
        return None

def save_fsc_rule(rule_name, min_charge, brackets_json, is_active=True):
    """FSC 규칙 저장"""
    try:
        client = get_supabase_client()
        
        data = {
            'rule_name': rule_name,
            'min_charge': min_charge,
            'brackets': brackets_json,
            'is_active': is_active,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        response = client.table('fsc_rules').insert(data).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['rule_id']
        return None
            
    except Exception as e:
        st.error(f"FSC 규칙 저장 실패: {str(e)}")
        return None


def update_fsc_rule(id, rule_name, min_charge, brackets_json, is_active):
    """FSC 규칙 수정"""
    try:
        client = get_supabase_client()
        
        data = {
            'rule_name': rule_name,
            'min_charge': min_charge,
            'brackets': brackets_json,
            'is_active': is_active,
            'updated_at': datetime.now().isoformat()
        }
        
        response = client.table('fsc_rules').update(data).eq('rule_id', id).execute()
        
        if response.data:
            return True
        return False
            
    except Exception as e:
        st.error(f"FSC 규칙 수정 실패: {str(e)}")
        return False


def delete_fsc_rule(id):
    """FSC 규칙 삭제"""
    try:
        client = get_supabase_client()
        
        response = client.table('fsc_rules').delete().eq('rule_id', id).execute()
        
        if response.data:
            return True
        return False
            
    except Exception as e:
        st.error(f"FSC 규칙 삭제 실패: {str(e)}")
        return False

def calculate_fsc(id, weight):
    """FSC 요금 계산"""
    try:
        # FSC 규칙 조회
        rule = get_fsc_rule_by_id(id)
        
        if not rule:
            return None
            
        min_charge = float(rule.get('min_charge', 0))
        brackets = rule.get('brackets', {})
        
        # 해당 무게 구간 찾기
        calculated_charge = 0
        for bracket_range, rate in brackets.items():
            min_weight, max_weight = bracket_range.split('-')
            min_weight = float(min_weight)
            max_weight = float(max_weight) if max_weight != '+' else float('inf')
            
            if min_weight <= weight <= max_weight:
                calculated_charge = weight * float(rate)
                break
        
        # 최소 요금 적용
        final_charge = max(calculated_charge, min_charge)
        
        return {
            'weight': weight,
            'calculated_charge': calculated_charge,
            'min_charge': min_charge,
            'final_charge': final_charge,
            'rule_name': rule.get('rule_name', '')
        }
        
    except Exception as e:
        st.error(f"FSC 요금 계산 실패: {str(e)}")
        return None

# ==========================================
# Trucking 규칙 관리 함수
# ==========================================

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


def get_trucking_rule_by_id(id):
    """ID로 특정 Trucking 규칙 조회"""
    try:
        client = get_supabase_client()
        response = client.table('trucking_rules').select('*').eq('rule_id', id).execute()
        
        if response.data:
            return response.data[0]
        return None
            
    except Exception as e:
        st.error(f"Trucking 규칙 조회 실패: {str(e)}")
        return None
    
def save_trucking_rule(rule_name, charge_type, calculation_method, 
                       fixed_charge=None, weight_threshold_kg=None, 
                       rate_per_kg_vnd=None, weight_brackets=None, is_active=True):
    """Trucking 규칙 저장"""
    try:
        client = get_supabase_client()
        
        data = {
            'rule_name': rule_name,
            'charge_type': charge_type,
            'calculation_method': calculation_method,
            'fixed_charge': fixed_charge,
            'weight_threshold_kg': weight_threshold_kg,
            'rate_per_kg_vnd': rate_per_kg_vnd,
            'weight_brackets': weight_brackets,
            'is_active': is_active,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        response = client.table('trucking_rules').insert(data).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['rule_id']
        return None
            
    except Exception as e:
        st.error(f"Trucking 규칙 저장 실패: {str(e)}")
        return None

def update_trucking_rule(id, rule_name, charge_type, calculation_method,
                        fixed_charge=None, weight_threshold_kg=None,
                        rate_per_kg_vnd=None, weight_brackets=None, is_active=True):
    """Trucking 규칙 수정"""
    try:
        client = get_supabase_client()
        
        data = {
            'rule_name': rule_name,
            'charge_type': charge_type,
            'calculation_method': calculation_method,
            'fixed_charge': fixed_charge,
            'weight_threshold_kg': weight_threshold_kg,
            'rate_per_kg_vnd': rate_per_kg_vnd,
            'weight_brackets': weight_brackets,
            'is_active': is_active,
            'updated_at': datetime.now().isoformat()
        }
        
        response = client.table('trucking_rules').update(data).eq('rule_id', id).execute()
        
        if response.data:
            return True
        return False
            
    except Exception as e:
        st.error(f"Trucking 규칙 수정 실패: {str(e)}")
        return False

def delete_trucking_rule(id):
    """Trucking 규칙 삭제"""
    try:
        client = get_supabase_client()
        
        response = client.table('trucking_rules').delete().eq('rule_id', id).execute()
        
        if response.data:
            return True
        return False
            
    except Exception as e:
        st.error(f"Trucking 규칙 삭제 실패: {str(e)}")
        return False

def calculate_trucking(id, weight):
    """Trucking 요금 계산"""
    try:
        # Trucking 규칙 조회
        rule = get_trucking_rule_by_id(id)
        
        if not rule:
            return None
            
        calculation_method = rule.get('calculation_method', '')
        charge_type = rule.get('charge_type', '')
        
        calculated_charge = 0
        
        if calculation_method == 'FIXED':
            # 고정 요금
            calculated_charge = float(rule.get('fixed_charge', 0))
            
        elif calculation_method == 'weight_based':
            # 무게 기반 계산
            threshold = float(rule.get('weight_threshold_kg', 0))
            rate_per_kg = float(rule.get('rate_per_kg_vnd', 0))
            
            if weight > threshold:
                calculated_charge = (weight - threshold) * rate_per_kg
            else:
                calculated_charge = 0
                
        elif calculation_method == 'bracket':
            # 구간별 계산
            brackets = rule.get('weight_brackets', {})
            for bracket_range, rate in brackets.items():
                min_weight, max_weight = bracket_range.split('-')
                min_weight = float(min_weight)
                max_weight = float(max_weight) if max_weight != '+' else float('inf')
                
                if min_weight <= weight <= max_weight:
                    calculated_charge = weight * float(rate)
                    break
        
        return {
            'weight': weight,
            'charge_type': charge_type,
            'calculation_method': calculation_method,
            'calculated_charge': calculated_charge,
            'rule_name': rule.get('rule_name', '')
        }
        
    except Exception as e:
        st.error(f"Trucking 요금 계산 실패: {str(e)}")
        return None

# ==========================================
# 물류사 요금표 관리 함수
# ==========================================

def get_transport_modes():
    """운송 수단 목록 조회 (드롭다운용)"""
    try:
        client = get_supabase_client()
        response = client.table('transport_modes').select('*').eq('is_active', True).order('id').execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"운송 수단 조회 오류: {str(e)}")
        return []


def get_rate_tables(search_query=None, transport_mode_id=None, status_filter=None):
    """물류사 요금표 목록 조회"""
    try:
        client = get_supabase_client()
        query = client.table('logistics_rate_table').select('*')
        
        if search_query:
            query = query.or_(f'provider_name.ilike.%{search_query}%,route.ilike.%{search_query}%')
        
        if transport_mode_id:
            query = query.eq('transport_mode_id', transport_mode_id)
        
        if status_filter == "활성":
            query = query.eq('is_active', True)
        elif status_filter == "비활성":
            query = query.eq('is_active', False)
        
        query = query.order('created_at', desc=True)
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"요금표 조회 오류: {str(e)}")
        return []


def get_rate_table_by_id(rate_id):
    """특정 요금표 조회"""
    try:
        client = get_supabase_client()
        response = client.table('logistics_rate_table').select('*').eq('id', rate_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"요금표 조회 오류: {str(e)}")
        return None


def save_rate_table(data):
    """새 요금표 저장"""
    try:
        client = get_supabase_client()
        response = client.table('logistics_rate_table').insert(data).execute()
        return True, response.data[0]['id'] if response.data else None
    except Exception as e:
        return False, str(e)


def update_rate_table(rate_id, data):
    """요금표 수정"""
    try:
        client = get_supabase_client()
        response = client.table('logistics_rate_table').update(data).eq('id', rate_id).execute()
        return True, "수정 완료"
    except Exception as e:
        return False, str(e)


def delete_rate_table(rate_id):
    """요금표 삭제(비활성화)"""
    try:
        client = get_supabase_client()
        response = client.table('logistics_rate_table').update({'is_active': False}).eq('id', rate_id).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"요금표 삭제 오류: {str(e)}")
        return False


# ==========================================
# Lead Time 관리 함수 (신규 추가)
# ==========================================

def get_provider_list():
    """물류사 목록 조회"""
    try:
        client = get_supabase_client()
        response = client.table('standard_lead_times').select('provider_name').execute()
        
        if response.data:
            providers = list(set([item['provider_name'] for item in response.data]))
            return sorted(providers)
        return []
    except Exception as e:
        st.error(f"물류사 목록 조회 오류: {str(e)}")
        return []


def get_lead_times(filter_provider=None, filter_mode=None, filter_active=None):
    """리드타임 목록 조회"""
    try:
        client = get_supabase_client()
        query = client.table('standard_lead_times').select('*, transport_modes(*)')
        
        if filter_provider and filter_provider != "전체":
            query = query.eq('provider_name', filter_provider)
        
        if filter_mode and filter_mode != "전체":
            mode_map = {"항공": "AIR", "육로": "TRUCK", "해상": "SEA"}
            mode_code = mode_map.get(filter_mode)
            if mode_code:
                # transport_modes 테이블과 조인하여 필터링
                all_modes = get_transport_modes()
                mode_id = next((m['id'] for m in all_modes if m['code'] == mode_code), None)
                if mode_id:
                    query = query.eq('transport_mode_id', mode_id)
        
        if filter_active == "활성만":
            query = query.eq('is_active', True)
        
        query = query.order('provider_name').order('transport_mode_id')
        
        response = query.execute()
        
        if response.data:
            result = []
            for item in response.data:
                mode_data = item.get('transport_modes', {})
                result.append({
                    'id': item['id'],
                    'provider_name': item['provider_name'],
                    'route': item['route'],
                    'standard_days': item['standard_days'],
                    'min_days': item['min_days'],
                    'max_days': item['max_days'],
                    'description': item.get('description'),
                    'is_active': item['is_active'],
                    'mode_code': mode_data.get('code', ''),
                    'mode_name': mode_data.get('name', '')
                })
            return result
        return []
    except Exception as e:
        st.error(f"리드타임 조회 오류: {str(e)}")
        return []


def get_lead_time_by_id(lead_time_id):
    """특정 리드타임 조회"""
    try:
        client = get_supabase_client()
        response = client.table('standard_lead_times').select('*, transport_modes(*)').eq('id', lead_time_id).execute()
        
        if response.data:
            item = response.data[0]
            mode_data = item.get('transport_modes', {})
            return {
                'id': item['id'],
                'provider_name': item['provider_name'],
                'route': item['route'],
                'standard_days': item['standard_days'],
                'min_days': item['min_days'],
                'max_days': item['max_days'],
                'description': item.get('description'),
                'transport_mode_id': item['transport_mode_id'],
                'mode_code': mode_data.get('code', ''),
                'mode_name': mode_data.get('name', '')
            }
        return None
    except Exception as e:
        st.error(f"리드타임 조회 오류: {str(e)}")
        return None


def save_lead_time(data):
    """리드타임 저장"""
    try:
        client = get_supabase_client()
        insert_data = {
            'provider_name': data['provider_name'],
            'transport_mode_id': data['transport_mode_id'],
            'route': data['route'],
            'standard_days': data['standard_days'],
            'min_days': data['min_days'],
            'max_days': data['max_days'],
            'description': data.get('description'),
            'is_active': True
        }
        response = client.table('standard_lead_times').insert(insert_data).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"리드타임 저장 오류: {str(e)}")
        return False


def update_lead_time(data):
    """리드타임 수정"""
    try:
        client = get_supabase_client()
        update_data = {
            'provider_name': data['provider_name'],
            'transport_mode_id': data['transport_mode_id'],
            'route': data['route'],
            'standard_days': data['standard_days'],
            'min_days': data['min_days'],
            'max_days': data['max_days'],
            'description': data.get('description')
        }
        response = client.table('standard_lead_times').update(update_data).eq('id', data['id']).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"리드타임 수정 오류: {str(e)}")
        return False


def delete_lead_time(lead_time_id):
    """리드타임 삭제(비활성화)"""
    try:
        client = get_supabase_client()
        response = client.table('standard_lead_times').update({'is_active': False}).eq('id', lead_time_id).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"리드타임 삭제 오류: {str(e)}")
        return False


# ==========================================
# Delay Reasons 관리 함수 (신규 추가)
# ==========================================

def get_delay_reasons(filter_category=None):
    """지연 사유 목록 조회"""
    try:
        client = get_supabase_client()
        query = client.table('delay_reasons_master').select('*').eq('is_active', True)
        
        if filter_category and filter_category != "전체":
            category_map = {
                "통관": "customs",
                "기상": "weather",
                "운송": "transport",
                "서류": "documentation",
                "공휴일": "holiday",
                "기타": "other"
            }
            category_code = category_map.get(filter_category)
            if category_code:
                query = query.eq('category', category_code)
        
        query = query.order('category').order('reason_name')
        
        response = query.execute()
        
        if response.data:
            return [{
                'id': item['id'],
                'category': item['category'],
                'reason_name': item['reason_name'],
                'typical_delay_days': item['typical_delay_days'],
                'responsible_party': item['responsible_party'],
                'prevention_note': item.get('prevention_note'),
                'is_active': item['is_active']
            } for item in response.data]
        return []
    except Exception as e:
        st.error(f"지연 사유 조회 오류: {str(e)}")
        return []


def get_delay_reason_by_id(reason_id):
    """특정 지연 사유 조회"""
    try:
        client = get_supabase_client()
        response = client.table('delay_reasons_master').select('*').eq('id', reason_id).execute()
        
        if response.data:
            item = response.data[0]
            return {
                'id': item['id'],
                'category': item['category'],
                'reason_name': item['reason_name'],
                'typical_delay_days': item['typical_delay_days'],
                'responsible_party': item['responsible_party'],
                'prevention_note': item.get('prevention_note')
            }
        return None
    except Exception as e:
        st.error(f"지연 사유 조회 오류: {str(e)}")
        return None


def save_delay_reason(data):
    """지연 사유 저장"""
    try:
        client = get_supabase_client()
        insert_data = {
            'category': data['category'],
            'reason_name': data['reason_name'],
            'typical_delay_days': data['typical_delay_days'],
            'responsible_party': data['responsible_party'],
            'prevention_note': data.get('prevention_note'),
            'is_active': True
        }
        response = client.table('delay_reasons_master').insert(insert_data).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"지연 사유 저장 오류: {str(e)}")
        return False


def update_delay_reason(data):
    """지연 사유 수정"""
    try:
        client = get_supabase_client()
        update_data = {
            'category': data['category'],
            'reason_name': data['reason_name'],
            'typical_delay_days': data['typical_delay_days'],
            'responsible_party': data['responsible_party'],
            'prevention_note': data.get('prevention_note')
        }
        response = client.table('delay_reasons_master').update(update_data).eq('id', data['id']).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"지연 사유 수정 오류: {str(e)}")
        return False


def delete_delay_reason(reason_id):
    """지연 사유 삭제(비활성화)"""
    try:
        client = get_supabase_client()
        response = client.table('delay_reasons_master').update({'is_active': False}).eq('id', reason_id).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"지연 사유 삭제 오류: {str(e)}")
        return False


# ==========================================
# Delivery 관리 함수 (신규 추가)
# ==========================================

def get_all_providers():
    """모든 물류사 목록 (logistics_imports 기준)"""
    try:
        client = get_supabase_client()
        response = client.table('logistics_imports').select('logistics_provider_name').execute()
        
        if response.data:
            providers = list(set([item['logistics_provider_name'] for item in response.data if item.get('logistics_provider_name')]))
            return sorted(providers)
        return []
    except Exception as e:
        st.error(f"물류사 목록 조회 오류: {str(e)}")
        return []


def get_delivery_statistics(period, provider_filter):
    """납기 통계"""
    try:
        client = get_supabase_client()
        
        # 기간 계산
        period_map = {
            "이번 달": 30,
            "최근 3개월": 90,
            "최근 6개월": 180,
            "올해": 365
        }
        days = period_map.get(period, 30)
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        query = client.table('logistics_imports').select('*').gte('shipping_date', cutoff_date)
        
        if provider_filter and provider_filter != "전체":
            query = query.eq('logistics_provider_name', provider_filter)
        
        response = query.execute()
        
        if response.data:
            total = len(response.data)
            on_time = sum(1 for item in response.data if item.get('delay_severity') == 'on_time')
            minor = sum(1 for item in response.data if item.get('delay_severity') == 'minor')
            major = sum(1 for item in response.data if item.get('delay_severity') == 'major')
            critical = sum(1 for item in response.data if item.get('delay_severity') == 'critical')
            
            delayed_items = [item for item in response.data if item.get('is_delayed')]
            avg_delay = sum(item.get('lead_time_difference_days', 0) for item in delayed_items) / len(delayed_items) if delayed_items else 0
            max_delay = max((item.get('lead_time_difference_days', 0) for item in response.data), default=0)
            
            return {
                'total': total,
                'on_time': on_time,
                'minor': minor,
                'major': major,
                'critical': critical,
                'avg_delay': avg_delay,
                'max_delay': max_delay,
                'rate_change': 0
            }
        
        return {
            'total': 0, 'on_time': 0, 'minor': 0, 'major': 0, 'critical': 0,
            'avg_delay': 0, 'max_delay': 0, 'rate_change': 0
        }
    except Exception as e:
        st.error(f"납기 통계 조회 오류: {str(e)}")
        return {
            'total': 0, 'on_time': 0, 'minor': 0, 'major': 0, 'critical': 0,
            'avg_delay': 0, 'max_delay': 0, 'rate_change': 0
        }


def get_provider_delivery_stats(period):
    """물류사별 통계"""
    try:
        client = get_supabase_client()
        
        period_map = {"이번 달": 30, "최근 3개월": 90, "최근 6개월": 180, "올해": 365}
        days = period_map.get(period, 30)
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        response = client.table('logistics_imports').select('*').gte('shipping_date', cutoff_date).execute()
        
        if not response.data:
            return []
        
        # 물류사별 그룹핑
        provider_stats = {}
        for item in response.data:
            provider = item.get('logistics_provider_name')
            if not provider:
                continue
            
            if provider not in provider_stats:
                provider_stats[provider] = {'total': 0, 'on_time': 0, 'delays': []}
            
            provider_stats[provider]['total'] += 1
            if item.get('delay_severity') == 'on_time':
                provider_stats[provider]['on_time'] += 1
            if item.get('is_delayed'):
                provider_stats[provider]['delays'].append(item.get('lead_time_difference_days', 0))
        
        # 결과 변환
        result = []
        for provider, stats in provider_stats.items():
            on_time_rate = (stats['on_time'] / stats['total'] * 100) if stats['total'] > 0 else 0
            avg_delay = sum(stats['delays']) / len(stats['delays']) if stats['delays'] else 0
            
            if on_time_rate >= 80:
                reliability = '⭐⭐⭐⭐'
            elif on_time_rate >= 60:
                reliability = '⭐⭐⭐'
            else:
                reliability = '⭐⭐'
            
            result.append({
                'provider': provider,
                'total': stats['total'],
                'on_time_rate': round(on_time_rate, 1),
                'avg_delay': round(avg_delay, 1),
                'reliability': reliability
            })
        
        return sorted(result, key=lambda x: x['on_time_rate'], reverse=True)
    except Exception as e:
        st.error(f"물류사별 통계 조회 오류: {str(e)}")
        return []


def get_top_delay_causes(period, provider_filter):
    """지연 원인 TOP 5"""
    try:
        client = get_supabase_client()
        
        period_map = {"이번 달": 30, "최근 3개월": 90, "최근 6개월": 180, "올해": 365}
        days = period_map.get(period, 30)
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        query = client.table('logistics_imports').select('*').eq('is_delayed', True).gte('shipping_date', cutoff_date)
        
        if provider_filter and provider_filter != "전체":
            query = query.eq('logistics_provider_name', provider_filter)
        
        response = query.execute()
        
        if not response.data:
            return []
        
        # 지연 사유별 그룹핑
        cause_stats = {}
        for item in response.data:
            reason = item.get('delay_reason_detail', '미분류')
            responsible = item.get('delay_responsible_party', '미정')
            
            if reason not in cause_stats:
                cause_stats[reason] = {'count': 0, 'delays': [], 'responsible': responsible}
            
            cause_stats[reason]['count'] += 1
            cause_stats[reason]['delays'].append(item.get('lead_time_difference_days', 0))
        
        # 상위 5개 추출
        result = []
        responsible_map = {
            'customs': '세관',
            'logistics_provider': '물류사',
            'supplier': '공급업체',
            'force_majeure': '불가항력'
        }
        
        for reason, stats in sorted(cause_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            avg_delay = sum(stats['delays']) / len(stats['delays']) if stats['delays'] else 0
            result.append({
                'reason_name': reason,
                'count': stats['count'],
                'avg_delay': round(avg_delay, 1),
                'responsible': responsible_map.get(stats['responsible'], stats['responsible'])
            })
        
        return result
    except Exception as e:
        st.error(f"지연 원인 조회 오류: {str(e)}")
        return []


def get_delayed_logistics(severity_filter, provider_filter, date_range):
    """지연 건 조회"""
    try:
        client = get_supabase_client()
        
        severity_map = {"경미": "minor", "중대": "major", "심각": "critical"}
        severity_list = [severity_map[s] for s in severity_filter]
        
        query = client.table('logistics_imports').select('*').eq('is_delayed', True).in_('delay_severity', severity_list)
        
        if provider_filter and provider_filter != "전체":
            query = query.eq('logistics_provider_name', provider_filter)
        
        if date_range and len(date_range) == 2:
            query = query.gte('shipping_date', date_range[0].isoformat()).lte('shipping_date', date_range[1].isoformat())
        
        query = query.order('shipping_date', desc=True)
        
        response = query.execute()
        
        if response.data:
            return [{
                'id': item['id'],
                'no': item.get('no', ''),
                'provider': item.get('logistics_provider_name', ''),
                'shipping_date': item.get('shipping_date', ''),
                'expected_arrival': item.get('expected_arrival_date', ''),
                'actual_arrival': item.get('actual_arrival_date', ''),
                'delay_days': item.get('lead_time_difference_days', 0),
                'severity': item.get('delay_severity', ''),
                'delay_reason': item.get('delay_reason_detail', '미입력'),
                'responsible': item.get('delay_responsible_party', '미정'),
                'cost_impact': float(item.get('delay_cost_impact_usd', 0)),
                'delay_detail': item.get('delay_reason_detail', '상세 내용 없음')
            } for item in response.data]
        return []
    except Exception as e:
        st.error(f"지연 건 조회 오류: {str(e)}")
        return []


def get_section_analysis(period):
    """구간별 분석"""
    try:
        client = get_supabase_client()
        
        period_map = {"최근 1개월": 30, "최근 3개월": 90, "최근 6개월": 180}
        days = period_map.get(period, 30)
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        response = client.table('logistics_imports').select('*').gte('shipping_date', cutoff_date).execute()
        
        if not response.data:
            return []
        
        # 구간별 데이터 수집
        sections = {
            '출고→항구': {'standard': 1.0, 'actuals': []},
            '항구→도착': {'standard': 2.0, 'actuals': []},
            '통관 처리': {'standard': 1.0, 'actuals': []}
        }
        
        for item in response.data:
            if item.get('shipping_to_port_days'):
                sections['출고→항구']['actuals'].append(item['shipping_to_port_days'])
            if item.get('port_to_arrival_days'):
                sections['항구→도착']['actuals'].append(item['port_to_arrival_days'])
            if item.get('customs_clearance_days'):
                sections['통관 처리']['actuals'].append(item['customs_clearance_days'])
        
        # 결과 생성
        result = []
        for section, data in sections.items():
            if data['actuals']:
                actual = sum(data['actuals']) / len(data['actuals'])
                standard = data['standard']
                diff = actual - standard
                
                if diff <= 0.2:
                    status = "✅ 정상"
                elif diff <= 1:
                    status = "⚠️ 주의"
                else:
                    status = "🔴 병목"
                
                result.append({
                    'section': section,
                    'standard': standard,
                    'actual': round(actual, 1),
                    'difference': round(diff, 1),
                    'status': status
                })
        
        return result
    except Exception as e:
        st.error(f"구간별 분석 오류: {str(e)}")
        return []