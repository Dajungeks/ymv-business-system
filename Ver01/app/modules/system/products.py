"""
YMV 비즈니스 시스템 - 제품 관리 모듈
"""

import streamlit as st
from app.shared.database import get_db

def product_management_page():
    """제품 관리 메인 페이지"""
    st.markdown("# 제품 관리")
    
    tab1, tab2 = st.tabs(["제품 목록", "새 제품 추가"])
    
    with tab1:
        st.info("제품 목록 기능 구현 예정")
    
    with tab2:
        add_new_product()

def add_new_product():
    """새 제품 추가"""
    st.markdown("### 새 제품 등록")
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("제품명")
            unit = st.selectbox("단위", ["EA", "SET", "PCS", "BOX"])
        
        with col2:
            unit_price = st.number_input("단가", min_value=0.0)
            currency = st.selectbox("통화", ["USD", "VND", "KRW"])
        
        submitted = st.form_submit_button("제품 등록")
        
        if submitted:
            st.success(f"제품 '{product_name}'이 등록되었습니다.")

if __name__ == "__main__":
    product_management_page()