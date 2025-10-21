import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database_logistics import (
    get_transport_modes,
    get_provider_list,
    get_lead_times,
    get_lead_time_by_id,
    save_lead_time,
    update_lead_time,
    delete_lead_time
)

def lead_time_management_page():
    """표준 리드타임 관리 페이지"""
    st.title("📅 표준 리드타임 관리")
    
    # 탭 구성
    tab1, tab2 = st.tabs(["리드타임 목록", "새 리드타임 등록"])
    
    with tab1:
        show_lead_time_list()
    
    with tab2:
        add_lead_time_form()


def show_lead_time_list():
    """리드타임 목록 표시"""
    st.subheader("📋 등록된 리드타임")
    
    # 필터
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        filter_provider = st.selectbox("물류사 필터", ["전체"] + get_provider_list(), key="filter_provider")
    with col2:
        filter_mode = st.selectbox("운송 수단", ["전체", "항공", "육로", "해상"], key="filter_mode")
    with col3:
        filter_active = st.selectbox("상태", ["활성만", "전체"], key="filter_active")
    
    # 데이터 조회
    lead_times = get_lead_times(filter_provider, filter_mode, filter_active)
    
    if not lead_times:
        st.info("등록된 리드타임이 없습니다.")
        return
    
    # 물류사별 그룹핑
    grouped = {}
    for lt in lead_times:
        provider = lt['provider_name']
        if provider not in grouped:
            grouped[provider] = []
        grouped[provider].append(lt)
    
    # 카드 형태로 표시
    for provider, items in grouped.items():
        with st.expander(f"📦 {provider} 물류사", expanded=True):
            for item in items:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # 운송 수단 아이콘
                    mode_icon = "✈️" if item['mode_name'] == "항공" else "🚛" if item['mode_name'] == "육로" else "🚢"
                    
                    st.markdown(f"""
                    **{mode_icon} {item['mode_name']} - {item['route']}**
                    
                    표준: **{item['standard_days']}일** | 최소: {item['min_days']}일 | 최대: {item['max_days']}일
                    
                    {item['description'] if item['description'] else ''}
                    """)
                
                with col2:
                    if st.button("수정", key=f"edit_{item['id']}"):
                        st.session_state['edit_lead_time_id'] = item['id']
                        st.rerun()
                    
                    if st.button("삭제", key=f"delete_{item['id']}"):
                        if delete_lead_time(item['id']):
                            st.success("삭제되었습니다.")
                            st.rerun()
                
                st.divider()
    
    # 수정 모드
    if 'edit_lead_time_id' in st.session_state:
        edit_lead_time_form(st.session_state['edit_lead_time_id'])


def add_lead_time_form():
    """리드타임 등록 폼"""
    st.subheader("➕ 새 리드타임 등록")
    
    with st.form("add_lead_time_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            provider_name = st.text_input("물류사명 *", placeholder="예: JOIN")
            transport_modes = get_transport_modes()
            mode_options = {f"{m['name']} ({m['code']})": m['id'] for m in transport_modes}
            selected_mode = st.selectbox("운송 수단 *", list(mode_options.keys()))
            route = st.text_input("경로 *", placeholder="예: China-Vietnam")
        
        with col2:
            standard_days = st.number_input("표준 일수 *", min_value=1, value=5)
            min_days = st.number_input("최소 일수 *", min_value=1, value=3)
            max_days = st.number_input("최대 일수 *", min_value=1, value=7)
        
        description = st.text_area("설명", placeholder="예: 항공 운송 표준 리드타임")
        
        submitted = st.form_submit_button("💾 저장")
        
        if submitted:
            if not provider_name or not route:
                st.error("필수 항목을 입력해주세요.")
                return
            
            if min_days > standard_days or standard_days > max_days:
                st.error("최소 ≤ 표준 ≤ 최대 순서로 입력해주세요.")
                return
            
            data = {
                'provider_name': provider_name,
                'transport_mode_id': mode_options[selected_mode],
                'route': route,
                'standard_days': standard_days,
                'min_days': min_days,
                'max_days': max_days,
                'description': description
            }
            
            if save_lead_time(data):
                st.success("✅ 리드타임이 등록되었습니다!")
                st.rerun()


def edit_lead_time_form(lead_time_id):
    """리드타임 수정 폼"""
    st.subheader("✏️ 리드타임 수정")
    
    # 기존 데이터 로드
    lead_time = get_lead_time_by_id(lead_time_id)
    if not lead_time:
        st.error("데이터를 찾을 수 없습니다.")
        return
    
    with st.form("edit_lead_time_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            provider_name = st.text_input("물류사명 *", value=lead_time['provider_name'])
            transport_modes = get_transport_modes()
            mode_options = {f"{m['name']} ({m['code']})": m['id'] for m in transport_modes}
            current_mode = f"{lead_time['mode_name']} ({lead_time['mode_code']})"
            selected_mode = st.selectbox("운송 수단 *", list(mode_options.keys()), 
                                        index=list(mode_options.keys()).index(current_mode))
            route = st.text_input("경로 *", value=lead_time['route'])
        
        with col2:
            standard_days = st.number_input("표준 일수 *", min_value=1, value=lead_time['standard_days'])
            min_days = st.number_input("최소 일수 *", min_value=1, value=lead_time['min_days'])
            max_days = st.number_input("최대 일수 *", min_value=1, value=lead_time['max_days'])
        
        description = st.text_area("설명", value=lead_time['description'] if lead_time['description'] else "")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 수정 저장")
        with col_btn2:
            cancelled = st.form_submit_button("❌ 취소")
        
        if cancelled:
            del st.session_state['edit_lead_time_id']
            st.rerun()
        
        if submitted:
            if not provider_name or not route:
                st.error("필수 항목을 입력해주세요.")
                return
            
            if min_days > standard_days or standard_days > max_days:
                st.error("최소 ≤ 표준 ≤ 최대 순서로 입력해주세요.")
                return
            
            data = {
                'id': lead_time_id,
                'provider_name': provider_name,
                'transport_mode_id': mode_options[selected_mode],
                'route': route,
                'standard_days': standard_days,
                'min_days': min_days,
                'max_days': max_days,
                'description': description
            }
            
            if update_lead_time(data):
                st.success("✅ 수정되었습니다!")
                del st.session_state['edit_lead_time_id']
                st.rerun()


