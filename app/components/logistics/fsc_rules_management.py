import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from utils.database_logistics import (
    get_fsc_rules,
    get_fsc_rule_by_id,
    save_fsc_rule,
    update_fsc_rule,
    delete_fsc_rule,
    calculate_fsc
)


def fsc_rules_management_page():
    """FSC 규칙 관리 페이지"""
    st.title("⚡ FSC 규칙 관리")
    st.markdown("---")
    
    # 사이드바 - 테스트 계산기
    with st.sidebar:
        st.header("🧮 FSC 계산기")
        test_calculator()
    
    # 상단 필터
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        search_query = st.text_input("🔍 규칙명 검색", key="search_fsc")
    
    with col2:
        status_filter = st.selectbox(
            "상태",
            ["전체", "활성", "비활성"],
            key="status_fsc"
        )
    
    with col3:
        st.write("")
        st.write("")
        if st.button("➕ 새 FSC 규칙 추가", use_container_width=True):
            st.session_state.show_fsc_form = True
            st.session_state.edit_fsc_id = None
    
    st.markdown("---")
    
    # 규칙 등록/수정 폼
    if st.session_state.get('show_fsc_form', False):
        show_fsc_form()
    
    # 규칙 목록 조회
    rules = get_fsc_rules(
        search_query if search_query else None,
        status_filter if status_filter != "전체" else None
    )
    
    if not rules:
        st.info("📭 등록된 FSC 규칙이 없습니다.")
        return
    
    # 규칙 목록 표시
    st.subheader(f"📋 FSC 규칙 목록 ({len(rules)}개)")
    
    for rule in rules:
        show_fsc_rule_card(rule)

def show_fsc_form():
    """FSC 규칙 등록/수정 폼"""
    with st.container():
        st.subheader("📝 FSC 규칙 등록")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rule_name = st.text_input("규칙명", key="fsc_rule_name")
            min_charge = st.number_input("최소 요금 (USD)", min_value=0.0, step=1.0, key="fsc_min_charge")
        
        with col2:
            is_active = st.checkbox("활성화", value=True, key="fsc_is_active")
        
        # 구간별 단가 설정
        st.write("### 📊 무게 구간별 단가")
        
        if 'fsc_brackets' not in st.session_state:
            st.session_state.fsc_brackets = []
        
        # 구간 추가 UI
        with st.expander("➕ 구간 추가", expanded=True):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                start_weight = st.number_input("시작 무게 (kg)", min_value=0.0, step=0.1, key="fsc_start_weight")
            with col2:
                end_weight = st.number_input("종료 무게 (kg)", min_value=0.0, step=0.1, key="fsc_end_weight")
            with col3:
                rate_per_kg = st.number_input("kg당 단가 (USD)", min_value=0.0, step=0.01, key="fsc_rate_per_kg")
            with col4:
                st.write("")  # 여백
                if st.button("➕ 추가", key="add_fsc_bracket"):
                    if end_weight > start_weight and rate_per_kg > 0:
                        bracket = {
                            'range': f"{start_weight}-{end_weight}",
                            'rate': rate_per_kg
                        }
                        st.session_state.fsc_brackets.append(bracket)
                        st.success("구간이 추가되었습니다")
                        st.rerun()
                    else:
                        st.error("올바른 구간 정보를 입력하세요")
        
        # 등록된 구간 표시
        if st.session_state.fsc_brackets:
            st.write("#### 등록된 구간")
            df = pd.DataFrame(st.session_state.fsc_brackets)
            
            # 삭제 버튼 추가
            for idx, row in df.iterrows():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"🔹 {row['range']} kg")
                with col2:
                    st.write(f"${row['rate']:.2f}/kg")
                with col3:
                    if st.button("삭제", key=f"del_bracket_{idx}"):
                        st.session_state.fsc_brackets.pop(idx)
                        st.rerun()
        
        # 저장 버튼
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("💾 저장", type="primary", key="save_fsc_rule"):
                if rule_name and st.session_state.fsc_brackets:
                    # brackets를 JSON 형식으로 변환
                    brackets_json = {}
                    for bracket in st.session_state.fsc_brackets:
                        brackets_json[bracket['range']] = bracket['rate']
                    
                    # 🔧 수정된 부분: 단일 반환값 처리
                    rule_id = save_fsc_rule(
                        rule_name=rule_name,
                        min_charge=min_charge,
                        brackets_json=brackets_json,
                        is_active=is_active
                    )
                    
                    if rule_id:
                        st.success(f"✅ FSC 규칙이 저장되었습니다 (ID: {rule_id})")
                        # 입력 초기화
                        st.session_state.fsc_brackets = []
                        st.rerun()
                    else:
                        st.error("❌ FSC 규칙 저장 실패")
                else:
                    st.error("규칙명과 최소 1개의 구간을 입력하세요")
        
        with col2:
            if st.button("🔄 초기화", key="reset_fsc_form"):
                st.session_state.fsc_brackets = []
                st.rerun()

def show_fsc_rule_card(rule):
    """FSC 규칙 카드 표시"""
    id = rule['rule_id']
    rule_name = rule['rule_name']
    min_charge = rule['min_charge']
    brackets = rule['brackets']
    is_active = rule['is_active']
    created_at = rule['created_at']
    
    # JSON 파싱
    brackets_dict = json.loads(brackets) if isinstance(brackets, str) else brackets
    
    with st.container():
        # 상태 배지
        status_badge = "🟢 활성" if is_active else "🔴 비활성"
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### {rule_name} {status_badge}")
            st.markdown(f"**최소 요금:** ${min_charge:,.2f}")
            
            # 구간 미리보기 (최대 3개)
            preview_brackets = list(brackets_dict.items())[:3]
            preview_text = " | ".join([f"{k}kg: ${v}/kg" for k, v in preview_brackets])
            if len(brackets_dict) > 3:
                preview_text += f" ... (총 {len(brackets_dict)}개 구간)"
            st.caption(preview_text)
            
            # created_at 처리
            display_date = str(created_at)[:16].replace('T', ' ') if created_at else ''
            st.caption(f"생성일: {display_date}")
        
        with col2:
            if st.button("✏️ 수정", key=f"edit_fsc_{id}"):
                st.session_state.show_fsc_form = True
                st.session_state.edit_fsc_id = id
                st.rerun()
            
            if is_active:
                if st.button("🗑️ 삭제", key=f"del_fsc_{id}"):
                    if delete_fsc_rule(id):
                        st.success("✅ 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 삭제 실패")
        
        st.markdown("---")


def test_calculator():
    """FSC 테스트 계산기"""
    st.markdown("중량을 입력하여 FSC를 계산합니다.")
    
    # 활성 규칙 목록
    rules = get_fsc_rules(status_filter="활성")
    
    if not rules:
        st.info("활성 규칙이 없습니다.")
        return
    
    # 규칙 선택
    rule_options = {f"{r['rule_name']} (ID: {r['rule_id']})": r['rule_id'] for r in rules}
    selected_rule = st.selectbox(
        "FSC 규칙 선택",
        options=list(rule_options.keys()),
        key="calc_fsc_rule"
    )
    
    # 중량 입력
    weight = st.number_input(
        "중량 (kg)",
        min_value=0.0,
        value=100.0,
        step=10.0,
        key="calc_fsc_weight"
    )
    
    # 계산 버튼
    if st.button("🧮 계산하기", use_container_width=True):
        id = rule_options[selected_rule]
        result, error = calculate_fsc(id, weight)
        
        if error:
            st.error(f"❌ {error}")
        else:
            st.success("✅ 계산 완료!")
            st.markdown(f"**중량:** {result['weight']} kg")
            st.markdown(f"**적용 구간:** {result['applied_bracket']}")
            st.markdown(f"**단가:** ${result['unit_price']}/kg")
            st.markdown(f"**계산 금액:** ${result['calculated_fsc']:,.2f}")
            st.markdown(f"**최소 요금:** ${result['min_charge']:,.2f}")
            st.markdown("---")
            st.markdown(f"### 💰 최종 FSC: ${result['final_fsc']:,.2f}")
            
            if result['min_charge_applied']:
                st.warning("⚠️ 최소 요금이 적용되었습니다.")