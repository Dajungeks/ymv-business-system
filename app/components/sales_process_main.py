import streamlit as st
from components.sales_process_dashboard import show_sales_process_dashboard
from components.purchase_order_management import show_purchase_order_management
from components.inventory_management import show_inventory_management
from components.profit_analysis import show_profit_analysis

def show_sales_process_management(load_func, save_func, update_func, delete_func, 
                                get_current_user_func, check_permission_func,
                                get_approval_status_info, calculate_statistics,
                                create_csv_download, render_print_form):
    """영업 프로세스 관리 시스템 메인 함수 - 모듈화 버전"""
    
    st.title("📄 영업 프로세스 관리")
    st.caption("Sales Process Management - Quote to Cash (모듈화)")
    
    # 현재 사용자 정보 확인
    current_user = get_current_user_func()
    if not current_user:
        st.error("로그인이 필요합니다.")
        return
    
    # 탭 구성 - 견적서 전환 제거
    tabs = st.tabs(["📊 영업 현황", "📦 발주 관리", "📋 재고 관리", "💰 수익 분석"])
    
    with tabs[0]:
        show_sales_process_dashboard(load_func)
    
    with tabs[1]:
        show_purchase_order_management(load_func, save_func, update_func, current_user)
    
    with tabs[2]:
        show_inventory_management(load_func, save_func, update_func, current_user)
    
    with tabs[3]:
        show_profit_analysis(load_func)