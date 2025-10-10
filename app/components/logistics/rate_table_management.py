"""
물류사 요금표 관리 화면
Logistics Rate Table Management Page
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database_logistics import (
    get_transport_modes,
    get_rate_tables,
    get_rate_table_by_id,
    save_rate_table,
    update_rate_table,
    delete_rate_table,
    get_fsc_rules,
    get_trucking_rules
)


def rate_table_management_page():
    """물류사 요금표 관리 메인 페이지"""
    st.title("💰 물류사 요금표 관리")
    st.markdown("---")
    
    # 상단 필터 영역
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        search_query = st.text_input(
            "🔍 검색",
            placeholder="물류사명 또는 경로 검색",
            key="rate_search"
        )
    
    with col2:
        transport_modes = get_transport_modes()
        mode_options = ["전체"] + [f"{m['id']}: {m['name']}" for m in transport_modes]
        selected_mode = st.selectbox("🚢 운송수단", mode_options, key="rate_mode_filter")
        
        mode_id = None
        if selected_mode != "전체":
            mode_id = int(selected_mode.split(":")[0])
    
    with col3:
        status_filter = st.selectbox("📊 상태", ["전체", "활성", "비활성"], key="rate_status_filter")
    
    st.markdown("---")
    
    # 새 요금표 등록 버튼
    if st.button("➕ 새 요금표 등록", use_container_width=False):
        st.session_state.rate_form_mode = "create"
        st.session_state.rate_edit_id = None
        st.rerun()
    
    # 등록/수정 폼 표시
    if st.session_state.get('rate_form_mode'):
        show_rate_form()
        st.markdown("---")
    
    # 요금표 목록 조회
    rates = get_rate_tables(
        search_query=search_query if search_query else None,
        transport_mode_id=mode_id,
        status_filter=status_filter if status_filter != "전체" else None
    )
    
    if not rates:
        st.info("📋 등록된 요금표가 없습니다.")
        return
    
    # 요금표 목록 표시
    st.subheader(f"📋 요금표 목록 ({len(rates)}개)")
    
    for rate in rates:
        show_rate_card(rate)


def show_rate_form():
    """요금표 등록/수정 폼"""
    mode = st.session_state.get('rate_form_mode', 'create')
    edit_id = st.session_state.get('rate_edit_id')
    
    # 수정 모드일 때 기존 데이터 로드
    existing_data = None
    if mode == 'edit' and edit_id:
        existing_data = get_rate_table_by_id(edit_id)
        if not existing_data:
            st.error("요금표를 찾을 수 없습니다.")
            st.session_state.rate_form_mode = None
            st.rerun()
            return
    
    # 폼 타이틀
    if mode == 'create':
        st.subheader("➕ 새 요금표 등록")
    else:
        st.subheader("✏️ 요금표 수정")
    
    with st.form(key="rate_table_form"):
        # 기본 정보
        st.markdown("#### 📌 기본 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            provider_name = st.text_input(
                "물류사명 *",
                value=existing_data['provider_name'] if existing_data else "",
                placeholder="예: DHL, FedEx"
            )
        
        with col2:
            transport_modes = get_transport_modes()
            mode_options = [f"{m['id']}: {m['name']}" for m in transport_modes]
            
            default_index = 0
            if existing_data:
                for idx, m in enumerate(transport_modes):
                    if m['id'] == existing_data['transport_mode_id']:
                        default_index = idx
                        break
            
            selected_mode = st.selectbox(
                "운송 수단 *",
                options=mode_options,
                index=default_index
            )
            transport_mode_id = int(selected_mode.split(":")[0])
        
        col3, col4 = st.columns(2)
        
        with col3:
            route = st.text_input(
                "경로 *",
                value=existing_data['route'] if existing_data else "",
                placeholder="예: 인천 → 로스앤젤레스"
            )
        
        with col4:
            effective_date = st.date_input(
                "적용일 *",
                value=datetime.strptime(existing_data['effective_date'], '%Y-%m-%d').date() if existing_data else datetime.now().date()
            )
        
        st.markdown("---")
        
        # 기본 요금
        st.markdown("#### 💵 기본 요금 (USD)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            delivery_order = st.number_input(
                "D/O (Delivery Order)",
                min_value=0.0,
                value=float(existing_data['delivery_order_usd']) if existing_data else 0.0,
                step=10.0,
                format="%.2f"
            )
            
            handling = st.number_input(
                "Handling",
                min_value=0.0,
                value=float(existing_data['handling_usd']) if existing_data else 0.0,
                step=10.0,
                format="%.2f"
            )
        
        with col2:
            customs_clearance = st.number_input(
                "통관 (Customs Clearance)",
                min_value=0.0,
                value=float(existing_data['customs_clearance_usd']) if existing_data else 0.0,
                step=10.0,
                format="%.2f"
            )
            
            customs_transited = st.number_input(
                "환적 통관 (Transited)",
                min_value=0.0,
                value=float(existing_data['customs_transited_usd']) if existing_data else 0.0,
                step=10.0,
                format="%.2f"
            )
        
        with col3:
            customs_charge = st.number_input(
                "세관 수수료 (Customs Charge)",
                min_value=0.0,
                value=float(existing_data['customs_charge_usd']) if existing_data else 0.0,
                step=10.0,
                format="%.2f"
            )
            
            freight_rate = st.number_input(
                "운임 단가 (USD/kg)",
                min_value=0.0,
                value=float(existing_data['freight_rate_per_kg']) if existing_data else 0.0,
                step=0.1,
                format="%.2f"
            )
        
        st.markdown("---")
        
        # 규칙 선택
        st.markdown("#### ⚙️ 계산 규칙 연결")
        col1, col2, col3 = st.columns(3)
        
        # FSC 규칙
        with col1:
            fsc_rules = get_fsc_rules(status_filter="활성")
            fsc_options = ["선택 안함"] + [f"ID {r['rule_id']}: {r['rule_name']}" for r in fsc_rules]
            
            fsc_default = 0
            if existing_data and existing_data.get('fsc_rule_id'):
                for idx, r in enumerate(fsc_rules):
                    if r['rule_id'] == existing_data['fsc_rule_id']:
                        fsc_default = idx + 1
                        break
            
            selected_fsc = st.selectbox("FSC 규칙", fsc_options, index=fsc_default)
            fsc_rule_id = None
            if selected_fsc != "선택 안함":
                fsc_rule_id = int(selected_fsc.split(":")[0].replace("ID ", ""))
        
        # Trucking LC 규칙
        with col2:
            lc_rules = [r for r in get_trucking_rules(status_filter="활성") if r['charge_type'] == 'LC']
            lc_options = ["선택 안함"] + [f"ID {r['rule_id']}: {r['rule_name']}" for r in lc_rules]
            
            lc_default = 0
            if existing_data and existing_data.get('trucking_lc_rule_id'):
                for idx, r in enumerate(lc_rules):
                    if r['rule_id'] == existing_data['trucking_lc_rule_id']:
                        lc_default = idx + 1
                        break
            
            selected_lc = st.selectbox("Trucking LC", lc_options, index=lc_default)
            lc_rule_id = None
            if selected_lc != "선택 안함":
                lc_rule_id = int(selected_lc.split(":")[0].replace("ID ", ""))
        
        # Trucking OC 규칙
        with col3:
            oc_rules = [r for r in get_trucking_rules(status_filter="활성") if r['charge_type'] == 'OC']
            oc_options = ["선택 안함"] + [f"ID {r['rule_id']}: {r['rule_name']}" for r in oc_rules]
            
            oc_default = 0
            if existing_data and existing_data.get('trucking_oc_rule_id'):
                for idx, r in enumerate(oc_rules):
                    if r['rule_id'] == existing_data['trucking_oc_rule_id']:
                        oc_default = idx + 1
                        break
            
            selected_oc = st.selectbox("Trucking OC", oc_options, index=oc_default)
            oc_rule_id = None
            if selected_oc != "선택 안함":
                oc_rule_id = int(selected_oc.split(":")[0].replace("ID ", ""))
        
        st.markdown("---")
        
        # 범위 정보
        st.markdown("#### 📦 범위 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            facility_range = st.text_input(
                "시설 일반 범위",
                value=existing_data['facility_typical_range'] if existing_data and existing_data.get('facility_typical_range') else "",
                placeholder="예: $50-100"
            )
            
            airport_range = st.text_input(
                "공항 일반 범위",
                value=existing_data['airport_typical_range'] if existing_data and existing_data.get('airport_typical_range') else "",
                placeholder="예: $30-80"
            )
        
        with col2:
            inspection_green = st.text_input(
                "검사 Green 범위",
                value=existing_data['inspection_green_range'] if existing_data else "$0",
                placeholder="예: $0"
            )
            
            inspection_yellow = st.text_input(
                "검사 Yellow 범위",
                value=existing_data['inspection_yellow_range'] if existing_data else "$20-40",
                placeholder="예: $20-40"
            )
            
            inspection_red = st.text_input(
                "검사 Red 범위",
                value=existing_data['inspection_red_range'] if existing_data else "$40-60",
                placeholder="예: $40-60"
            )
        
        st.markdown("---")
        
        # 버튼 영역
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submitted = st.form_submit_button(
                "💾 저장" if mode == 'create' else "✏️ 수정",
                use_container_width=True
            )
        
        with col_cancel:
            cancelled = st.form_submit_button("❌ 취소", use_container_width=True)
        
        # 취소 처리
        if cancelled:
            st.session_state.rate_form_mode = None
            st.session_state.rate_edit_id = None
            st.rerun()
        
        # 저장/수정 처리
        if submitted:
            # 유효성 검사
            if not provider_name or not route:
                st.error("물류사명과 경로는 필수 입력 항목입니다.")
                return
            
            # 데이터 구성
            data = {
                'provider_name': provider_name,
                'transport_mode_id': transport_mode_id,
                'route': route,
                'effective_date': effective_date.strftime('%Y-%m-%d'),
                'delivery_order_usd': delivery_order,
                'handling_usd': handling,
                'customs_clearance_usd': customs_clearance,
                'customs_transited_usd': customs_transited,
                'customs_charge_usd': customs_charge,
                'freight_rate_per_kg': freight_rate,
                'fsc_rule_id': fsc_rule_id,
                'trucking_lc_rule_id': lc_rule_id,
                'trucking_oc_rule_id': oc_rule_id,
                'facility_typical_range': facility_range if facility_range else None,
                'inspection_green_range': inspection_green,
                'inspection_yellow_range': inspection_yellow,
                'inspection_red_range': inspection_red,
                'airport_typical_range': airport_range if airport_range else None,
                'is_active': True
            }
            
            # 저장/수정 실행
            if mode == 'create':
                success, result = save_rate_table(data)
                
                if success:
                    st.success(f"요금표가 등록되었습니다! (ID: {result})")
                    st.session_state.rate_form_mode = None
                    st.rerun()
                else:
                    st.error(f"등록 실패: {result}")
            
            else:  # edit mode
                success, result = update_rate_table(edit_id, data)
                
                if success:
                    st.success("요금표가 수정되었습니다!")
                    st.session_state.rate_form_mode = None
                    st.session_state.rate_edit_id = None
                    st.rerun()
                else:
                    st.error(f"수정 실패: {result}")


def show_rate_card(rate):
    """요금표 카드 표시"""
    status_badge = "🟢 활성" if rate['is_active'] else "🔴 비활성"
    
    with st.container():
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown(f"### {rate['provider_name']} - {rate['route']} {status_badge}")
            
            # 기본 정보
            st.markdown(f"**운송수단 ID:** {rate['transport_mode_id']} | **적용일:** {rate['effective_date']}")
            
            # 주요 요금 표시
            rates_text = f"운임: ${rate['freight_rate_per_kg']}/kg | D/O: ${rate['delivery_order_usd']} | Handling: ${rate['handling_usd']}"
            st.caption(rates_text)
            
            # 규칙 연결 정보
            rules_info = []
            if rate.get('fsc_rule_id'):
                rules_info.append(f"FSC: ID {rate['fsc_rule_id']}")
            if rate.get('trucking_lc_rule_id'):
                rules_info.append(f"LC: ID {rate['trucking_lc_rule_id']}")
            if rate.get('trucking_oc_rule_id'):
                rules_info.append(f"OC: ID {rate['trucking_oc_rule_id']}")
            
            if rules_info:
                st.caption(f"연결된 규칙: {' | '.join(rules_info)}")
            
            st.caption(f"등록일: {rate['created_at'][:10]}")
        
        with col2:
            if st.button("✏️ 수정", key=f"edit_rate_{rate['id']}", use_container_width=True):
                st.session_state.rate_form_mode = "edit"
                st.session_state.rate_edit_id = rate['id']
                st.rerun()
            
            if rate['is_active']:
                if st.button("🗑️ 삭제", key=f"delete_rate_{rate['id']}", use_container_width=True):
                    if delete_rate_table(rate['id']):
                        st.success("요금표가 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("삭제 실패")
        
        st.markdown("---")