import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from utils.database_logistics import (
    get_delay_reasons,
    get_delay_reason_by_id,
    save_delay_reason,
    update_delay_reason,
    delete_delay_reason
)

# 수정 (따옴표 오류 수정)
def delay_reasons_management_page():
    """지연 사유 마스터 관리 페이지"""
    st.title("⚠️ 지연 사유 마스터 관리")
    
    tab1, tab2 = st.tabs(["사유 목록", "새 사유 등록"])
    
    with tab1:
        show_delay_reasons_list()
    
    with tab2:
        add_delay_reason_form()


def show_delay_reasons_list():
    """지연 사유 목록 표시"""
    st.subheader("📋 등록된 지연 사유")
    
    # 필터
    categories = ["전체", "통관", "기상", "운송", "서류", "공휴일", "기타"]
    filter_category = st.selectbox("카테고리 필터", categories, key="filter_category")
    
    # 데이터 조회
    reasons = get_delay_reasons(filter_category)
    
    if not reasons:
        st.info("등록된 지연 사유가 없습니다.")
        return
    
    # 카테고리별 그룹핑
    category_map = {
        'customs': '🔴 통관',
        'weather': '🌧️ 기상',
        'transport': '🚛 운송',
        'documentation': '📄 서류',
        'holiday': '🎉 공휴일',
        'other': '📌 기타'
    }
    
    grouped = {}
    for reason in reasons:
        cat = reason['category']
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(reason)
    
    # 카드 형태로 표시
    for cat_code, items in grouped.items():
        cat_name = category_map.get(cat_code, cat_code)
        
        with st.expander(f"{cat_name}", expanded=True):
            for item in items:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    responsible_map = {
                        'customs': '세관',
                        'logistics_provider': '물류사',
                        'supplier': '공급업체',
                        'force_majeure': '불가항력',
                        'internal': '자체',
                        'calendar': '달력'
                    }
                    responsible = responsible_map.get(item['responsible_party'], item['responsible_party'])
                    
                    st.markdown(f"""
                    **{item['reason_name']}**
                    
                    평균 지연: **{item['typical_delay_days']}일** | 책임: {responsible}
                    
                    💡 예방법: {item['prevention_note'] if item['prevention_note'] else '없음'}
                    """)
                
                with col2:
                    if st.button("수정", key=f"edit_reason_{item['id']}"):
                        st.session_state['edit_reason_id'] = item['id']
                        st.rerun()
                    
                    if st.button("삭제", key=f"delete_reason_{item['id']}"):
                        if delete_delay_reason(item['id']):
                            st.success("삭제되었습니다.")
                            st.rerun()
                
                st.divider()
    
    # 수정 모드
    if 'edit_reason_id' in st.session_state:
        edit_delay_reason_form(st.session_state['edit_reason_id'])


def add_delay_reason_form():
    """지연 사유 등록 폼"""
    st.subheader("➕ 새 지연 사유 등록")
    
    with st.form("add_delay_reason_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            category_options = {
                "통관": "customs",
                "기상": "weather",
                "운송": "transport",
                "서류": "documentation",
                "공휴일": "holiday",
                "기타": "other"
            }
            selected_category = st.selectbox("카테고리 *", list(category_options.keys()))
            
            reason_name = st.text_input("사유명 *", placeholder="예: Red 검사")
            
            typical_delay_days = st.number_input("평균 지연 일수", min_value=0, value=2)
        
        with col2:
            responsible_options = {
                "세관": "customs",
                "물류사": "logistics_provider",
                "공급업체": "supplier",
                "불가항력": "force_majeure",
                "자체": "internal",
                "달력": "calendar"
            }
            selected_responsible = st.selectbox("책임 주체", list(responsible_options.keys()))
        
        prevention_note = st.text_area("예방 방법", placeholder="예: 과거 검사 이력 첨부")
        
        submitted = st.form_submit_button("💾 저장")
        
        if submitted:
            if not reason_name:
                st.error("사유명을 입력해주세요.")
                return
            
            data = {
                'category': category_options[selected_category],
                'reason_name': reason_name,
                'typical_delay_days': typical_delay_days,
                'responsible_party': responsible_options[selected_responsible],
                'prevention_note': prevention_note
            }
            
            if save_delay_reason(data):
                st.success("✅ 지연 사유가 등록되었습니다!")
                st.rerun()


def edit_delay_reason_form(reason_id):
    """지연 사유 수정 폼"""
    st.subheader("✏️ 지연 사유 수정")
    
    reason = get_delay_reason_by_id(reason_id)
    if not reason:
        st.error("데이터를 찾을 수 없습니다.")
        return
    
    with st.form("edit_delay_reason_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            category_options = {
                "통관": "customs",
                "기상": "weather",
                "운송": "transport",
                "서류": "documentation",
                "공휴일": "holiday",
                "기타": "other"
            }
            reverse_cat = {v: k for k, v in category_options.items()}
            selected_category = st.selectbox("카테고리 *", list(category_options.keys()),
                                            index=list(category_options.keys()).index(reverse_cat[reason['category']]))
            
            reason_name = st.text_input("사유명 *", value=reason['reason_name'])
            
            typical_delay_days = st.number_input("평균 지연 일수", min_value=0, value=reason['typical_delay_days'])
        
        with col2:
            responsible_options = {
                "세관": "customs",
                "물류사": "logistics_provider",
                "공급업체": "supplier",
                "불가항력": "force_majeure",
                "자체": "internal",
                "달력": "calendar"
            }
            reverse_resp = {v: k for k, v in responsible_options.items()}
            selected_responsible = st.selectbox("책임 주체", list(responsible_options.keys()),
                                               index=list(responsible_options.keys()).index(reverse_resp[reason['responsible_party']]))
        
        prevention_note = st.text_area("예방 방법", value=reason['prevention_note'] if reason['prevention_note'] else "")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 수정 저장")
        with col_btn2:
            cancelled = st.form_submit_button("❌ 취소")
        
        if cancelled:
            del st.session_state['edit_reason_id']
            st.rerun()
        
        if submitted:
            if not reason_name:
                st.error("사유명을 입력해주세요.")
                return
            
            data = {
                'id': reason_id,
                'category': category_options[selected_category],
                'reason_name': reason_name,
                'typical_delay_days': typical_delay_days,
                'responsible_party': responsible_options[selected_responsible],
                'prevention_note': prevention_note
            }
            
            if update_delay_reason(data):
                st.success("✅ 수정되었습니다!")
                del st.session_state['edit_reason_id']
                st.rerun()

