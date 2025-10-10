"""
Trucking 규칙 관리 화면
Trucking Rules Management Page
"""

import streamlit as st
import json
from datetime import datetime
from utils.database_logistics import (
    get_trucking_rules,
    get_trucking_rule_by_id,
    save_trucking_rule,
    update_trucking_rule,
    delete_trucking_rule,
    calculate_trucking
)


def trucking_rules_management_page():
    """Trucking 규칙 관리 메인 페이지"""
    st.title("🚛 Trucking 규칙 관리")
    st.markdown("---")
    
    # 사이드바에 테스트 계산기 추가
    show_test_calculator()
    
    # 상단 필터 영역
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 규칙명 검색", placeholder="규칙명을 입력하세요", key="trucking_search")
    
    with col2:
        type_filter = st.selectbox("📦 타입", ["전체", "LC", "OC"], key="trucking_type_filter")
    
    with col3:
        status_filter = st.selectbox("📊 상태", ["전체", "활성", "비활성"], key="trucking_status_filter")
    
    st.markdown("---")
    
    # 새 규칙 등록 버튼
    col_btn1, col_btn2 = st.columns([1, 5])
    with col_btn1:
        if st.button("➕ 새 규칙 등록", use_container_width=True):
            st.session_state.trucking_form_mode = "create"
            st.session_state.trucking_edit_id = None
            st.rerun()
    
    # 등록/수정 폼 표시
    if st.session_state.get('trucking_form_mode'):
        show_trucking_form()
        st.markdown("---")
    
    # 규칙 목록 조회
    rules = get_trucking_rules(
        search_query=search_query if search_query else None,
        type_filter=type_filter if type_filter != "전체" else None,
        status_filter=status_filter if status_filter != "전체" else None
    )
    
    if not rules:
        st.info("📋 등록된 Trucking 규칙이 없습니다.")
        return
    
    # LC/OC 그룹별 분류
    lc_rules = [r for r in rules if r['charge_type'] == 'LC']
    oc_rules = [r for r in rules if r['charge_type'] == 'OC']
    
    # LC 규칙 표시
    if lc_rules:
        st.subheader("🔵 LC (Local Charge) 규칙")
        for rule in lc_rules:
            show_trucking_rule_card(rule, border_color="#1E88E5")
        st.markdown("---")
    
    # OC 규칙 표시
    if oc_rules:
        st.subheader("🟢 OC (Origin Charge) 규칙")
        for rule in oc_rules:
            show_trucking_rule_card(rule, border_color="#43A047")


def show_trucking_rule_card(rule, border_color="#1E88E5"):
    """Trucking 규칙 카드 표시"""
    status_color = "🟢" if rule['is_active'] else "🔴"
    status_text = "활성" if rule['is_active'] else "비활성"
    
    # 계산 방식 표시
    if rule['calculation_method'] == 'FIXED':
        method_text = f"고정요금: ${rule['fixed_charge']:,.2f}"
    else:
        brackets = json.loads(rule['weight_brackets']) if isinstance(rule['weight_brackets'], str) else rule['weight_brackets']
        bracket_count = len(brackets) if brackets else 0
        method_text = f"중량기반 ({bracket_count}개 구간)"
    
    # 카드 HTML
    card_html = f"""
    <div style="border: 2px solid {border_color}; border-radius: 10px; padding: 15px; margin-bottom: 15px; background-color: #f9f9f9;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0; color: {border_color};">{rule['rule_name']}</h4>
                <p style="margin: 5px 0; color: #666;">
                    {status_color} {status_text} | {rule['charge_type']} | {method_text}
                </p>
                <p style="margin: 5px 0; font-size: 0.85em; color: #999;">
                    생성일: {rule['created_at'][:10]}
                </p>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # 버튼 영역
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("✏️ 수정", key=f"edit_trucking_{rule['rule_id']}", use_container_width=True):
            st.session_state.trucking_form_mode = "edit"
            st.session_state.trucking_edit_id = rule['rule_id']
            st.rerun()
    
    with col2:
        if rule['is_active']:
            if st.button("🗑️ 삭제", key=f"delete_trucking_{rule['rule_id']}", use_container_width=True):
                if delete_trucking_rule(rule['rule_id']):
                    st.success("✅ 규칙이 삭제(비활성화)되었습니다.")
                    st.rerun()
                else:
                    st.error("❌ 삭제 실패")


def show_trucking_form():
    """Trucking 규칙 등록/수정 폼"""
    mode = st.session_state.get('trucking_form_mode', 'create')
    edit_id = st.session_state.get('trucking_edit_id')
    
    # 수정 모드일 때 기존 데이터 로드
    existing_data = None
    if mode == 'edit' and edit_id:
        existing_data = get_trucking_rule_by_id(edit_id)
        if not existing_data:
            st.error("❌ 규칙을 찾을 수 없습니다.")
            st.session_state.trucking_form_mode = None
            st.rerun()
            return
    
    # 폼 타이틀
    if mode == 'create':
        st.subheader("➕ 새 Trucking 규칙 등록")
    else:
        st.subheader("✏️ Trucking 규칙 수정")
    
    with st.form(key="trucking_rule_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            rule_name = st.text_input(
                "규칙명 *",
                value=existing_data['rule_name'] if existing_data else "",
                placeholder="예: 부산항 LC 기본요금"
            )
        
        with col2:
            charge_type = st.selectbox(
                "타입 *",
                options=["LC", "OC"],
                index=0 if not existing_data else (0 if existing_data['charge_type'] == 'LC' else 1)
            )
        
        calculation_method = st.radio(
            "계산 방식 *",
            options=["고정요금", "중량기반"],
            index=0 if not existing_data else (0 if existing_data['calculation_method'] == 'FIXED' else 1),
            horizontal=True
        )
        
        fixed_charge = None
        weight_brackets_json = None
        
        # 고정요금 방식
        if calculation_method == "고정요금":
            fixed_charge = st.number_input(
                "고정 요금 (USD) *",
                min_value=0.0,
                value=float(existing_data['fixed_charge']) if existing_data and existing_data.get('fixed_charge') else 0.0,
                step=10.0,
                format="%.2f"
            )
        
        # 중량기반 방식
        else:
            st.markdown("**구간별 단가 설정 (USD/kg)**")
            
            # 기존 데이터가 있으면 로드
            existing_brackets = {}
            if existing_data and existing_data.get('weight_brackets'):
                existing_brackets = json.loads(existing_data['weight_brackets']) if isinstance(existing_data['weight_brackets'], str) else existing_data['weight_brackets']
            
            brackets = {}
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                brackets['0-50'] = st.number_input(
                    "0-50 kg",
                    min_value=0.0,
                    value=float(existing_brackets.get('0-50', 0.0)),
                    step=0.1,
                    format="%.2f",
                    key="bracket_0_50"
                )
                brackets['51-100'] = st.number_input(
                    "51-100 kg",
                    min_value=0.0,
                    value=float(existing_brackets.get('51-100', 0.0)),
                    step=0.1,
                    format="%.2f",
                    key="bracket_51_100"
                )
                brackets['101-500'] = st.number_input(
                    "101-500 kg",
                    min_value=0.0,
                    value=float(existing_brackets.get('101-500', 0.0)),
                    step=0.1,
                    format="%.2f",
                    key="bracket_101_500"
                )
            
            with col_b2:
                brackets['501-1000'] = st.number_input(
                    "501-1000 kg",
                    min_value=0.0,
                    value=float(existing_brackets.get('501-1000', 0.0)),
                    step=0.1,
                    format="%.2f",
                    key="bracket_501_1000"
                )
                brackets['1001+'] = st.number_input(
                    "1001+ kg",
                    min_value=0.0,
                    value=float(existing_brackets.get('1001+', 0.0)),
                    step=0.1,
                    format="%.2f",
                    key="bracket_1001_plus"
                )
            
            weight_brackets_json = json.dumps(brackets)
        
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
            st.session_state.trucking_form_mode = None
            st.session_state.trucking_edit_id = None
            st.rerun()
        
        # 저장/수정 처리
        if submitted:
            # 유효성 검사
            if not rule_name:
                st.error("❌ 규칙명을 입력하세요.")
                return
            
            if calculation_method == "고정요금" and fixed_charge <= 0:
                st.error("❌ 고정 요금은 0보다 커야 합니다.")
                return
            
            if calculation_method == "중량기반":
                if not any(v > 0 for v in brackets.values()):
                    st.error("❌ 최소 하나의 구간에 단가를 입력하세요.")
                    return
            
            # 저장/수정 실행
            if mode == 'create':
                rule_id = save_trucking_rule(
                    rule_name=rule_name,
                    charge_type=charge_type,
                    calculation_method='FIXED' if calculation_method == "고정요금" else 'WEIGHT_BASED',
                    fixed_charge=fixed_charge,
                    weight_brackets=weight_brackets_json
                )
                
                if rule_id:
                    st.success(f"✅ Trucking 규칙이 등록되었습니다! (ID: {rule_id})")
                    st.session_state.trucking_form_mode = None
                    st.rerun()
                else:
                    st.error("❌ 등록 실패")
            
            else:  # edit mode
                success = update_trucking_rule(
                    id=edit_id,
                    rule_name=rule_name,
                    charge_type=charge_type,
                    calculation_method='FIXED' if calculation_method == "고정요금" else 'WEIGHT_BASED',
                    fixed_charge=fixed_charge,
                    weight_brackets=weight_brackets_json
                )
                
                if success:
                    st.success("✅ Trucking 규칙이 수정되었습니다!")
                    st.session_state.trucking_form_mode = None
                    st.session_state.trucking_edit_id = None
                    st.rerun()
                else:
                    st.error("❌ 수정 실패")
         


def show_test_calculator():
    """사이드바 테스트 계산기"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("🧮 Trucking 계산기")
        
        # 활성 규칙 목록 조회
        rules = get_trucking_rules(status_filter="활성")
        
        if not rules:
            st.info("활성 규칙이 없습니다.")
            return
        
        # 규칙 선택
        rule_options = {f"{r['rule_name']} ({r['charge_type']})": r['rule_id'] for r in rules}
        selected_rule_name = st.selectbox(
            "규칙 선택",
            options=list(rule_options.keys()),
            key="calc_trucking_rule"
        )
        
        selected_id = rule_options[selected_rule_name]
        
        # 중량 입력
        weight = st.number_input(
            "중량 (kg)",
            min_value=0.0,
            value=100.0,
            step=10.0,
            key="calc_trucking_weight"
        )
        
        # 계산 버튼
        if st.button("💰 계산", use_container_width=True, key="calc_trucking_btn"):
            result = calculate_trucking(selected_id, weight)
            
            if not result:
                st.error("❌ 계산 실패")
            else:
                st.success("✅ 계산 완료!")
                
                st.markdown("**계산 결과:**")
                st.info(f"""
                **규칙:** {result['rule_name']}  
                **타입:** {result['charge_type']}  
                **방식:** {result['calculation_method']}  
                **중량:** {result['weight']} kg  
                
                ---
                
                **최종 요금:** ${result['calculated_charge']:,.2f}
                """)