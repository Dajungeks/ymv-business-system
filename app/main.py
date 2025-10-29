"""
YMV 관리 프로그램 v4.4 - 폴더 구조 정리 완료
YMV Business Management System v4.4 - Folder Structure Organized
"""

# 표준 라이브러리
import streamlit as st
import time
from datetime import datetime, date

# 페이지 설정 (최우선 실행)
st.set_page_config(
    page_title="YMV 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 서드파티 라이브러리
import supabase
from supabase import create_client, Client

# 내부 컴포넌트 - Sales
from components.sales.customer_management import show_customer_management
from components.sales.quotation_management import show_quotation_management
from components.sales.sales_process_main import show_sales_process_management
from components.sales.performance_management import show_performance_management  # 👈 추가

# 내부 컴포넌트 - Finance
from components.finance.expense_management import show_expense_management
from components.finance.reimbursement_management import show_reimbursement_management

# 내부 컴포넌트 - HR
from components.hr.employee_management import show_employee_management

from components.hr.corporate_account_management import show_corporate_account_management

# 내부 컴포넌트 - Supplier
from components.supplier.supplier_management import show_supplier_management

# 내부 컴포넌트 - Product
from components.product.product_management import show_product_management
from components.product.product_code_management import show_product_code_management

# 내부 컴포넌트 - Operations
from components.operations.purchase_management import show_purchase_management

# 내부 컴포넌트 - Logistics
from components.logistics.logistics_management import show_logistics_management  # 👈 새로운 물류사 관리만

# 내부 컴포넌트 - Dashboard
from components.dashboard.dashboard import show_dashboard_main

# 내부 컴포넌트 - System
from components.system.multilingual_input import MultilingualInputComponent

# 내부 컴포넌트 - Specifications
from components.specifications.hot_runner_order_sheet import show_hot_runner_order_management

# 유틸리티 모듈
from utils.database import create_database_operations
from utils.auth import AuthManager
from utils.helpers import (
    StatusHelper, StatisticsCalculator, CSVGenerator, PrintFormGenerator,
    get_approval_status_info, calculate_expense_statistics, 
    create_csv_download, render_print_form
)

# ===========================================
# 전역 초기화 및 설정
# ===========================================

@st.cache_resource
def init_supabase():
    """Supabase 클라이언트 초기화"""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

@st.cache_resource
def init_managers():
    """매니저 클래스들 초기화"""
    supabase_client = init_supabase()
    
    # session_state에 supabase 저장 (물류 함수에서 사용)
    if 'supabase' not in st.session_state:
        st.session_state.supabase = supabase_client
    
    db_ops = create_database_operations(supabase_client)
    auth_manager = AuthManager(db_ops)
    return db_ops, auth_manager

# 전역 매니저 인스턴스
db_operations, auth_manager = init_managers()

# ===========================================
# 로그인 페이지
# ===========================================

def show_login_page():
    """로그인 페이지"""
    st.title("🏢 YUMOLD 관리 시스템")
    st.subheader("로그인")
    
    # 로그인 타입 선택
    login_type = st.radio(
        "로그인 유형",
        ["👨‍💼 직원 로그인", "🏢 법인 로그인"],
        horizontal=True
    )
    
    with st.form("login_form"):
        if login_type == "👨‍💼 직원 로그인":
            # 직원 로그인
            user_id = st.text_input("사번 (Employee ID)")
            password = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인")
            
            if submitted:
                if user_id and password:
                    if auth_manager.login_user(user_id, password, login_type="employee"):
                        st.success("로그인되었습니다!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("사번 또는 비밀번호가 일치하지 않습니다.")
                else:
                    st.error("사번과 비밀번호를 입력해주세요.")
        
        else:
            # 법인 로그인
            try:
                companies = db_operations.load_data('companies') or []
                
                if not companies:
                    st.warning("등록된 법인이 없습니다.")
                    submitted = st.form_submit_button("로그인", disabled=True)
                    return
                
                # 법인 선택
                company_options = {f"{c.get('company_code')} - {c.get('company_name_en')}": c.get('login_id') 
                                 for c in companies if c.get('is_active')}
                
                if not company_options:
                    st.warning("활성화된 법인이 없습니다.")
                    submitted = st.form_submit_button("로그인", disabled=True)
                    return
                
                selected_company = st.selectbox(
                    "법인 선택 *",
                    options=list(company_options.keys())
                )
                
                login_id = company_options[selected_company]
                
                st.info(f"💡 로그인 ID: **{login_id}**")
                
                password = st.text_input("비밀번호", type="password")
                submitted = st.form_submit_button("로그인")
                
                if submitted:
                    if password:
                        if auth_manager.login_user(login_id, password, login_type="company"):
                            st.success("법인 로그인되었습니다!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        st.error("비밀번호를 입력해주세요.")
            
            except Exception as e:
                st.error(f"법인 정보 로드 중 오류: {str(e)}")
                submitted = st.form_submit_button("로그인", disabled=True)

# ===========================================
# 페이지 함수들 (컴포넌트 호출)
# ===========================================

def show_dashboard():
    """대시보드 페이지"""
    show_dashboard_main(db_operations.load_data, auth_manager.get_current_user)

def show_expense_management_page():
    """지출 관리 페이지"""
    show_expense_management(
        db_operations.load_data,
        db_operations.save_data,
        db_operations.update_data,
        db_operations.delete_data,
        auth_manager.get_current_user,
        get_approval_status_info,
        calculate_expense_statistics,
        create_csv_download,
        render_print_form
    )

def show_reimbursement_management_page():
    """환급 관리 페이지"""
    current_user = auth_manager.get_current_user()
    user_role = current_user.get('role', 'Staff') if current_user else 'Staff'
    
    if user_role not in ['Admin', 'CEO']:
        st.warning("⚠️ 환급 관리 권한이 없습니다.")
        return
    
    show_reimbursement_management(
        db_operations.load_data,
        db_operations.update_data,
        auth_manager.get_current_user
    )

def show_employee_management_page():
    """직원 관리 페이지"""
    db_operations, auth_manager = init_managers()
    show_employee_management(
        db_operations.load_data,
        db_operations.save_data,
        db_operations.update_data,
        db_operations.delete_data,
        auth_manager.get_current_user,
        auth_manager.check_permission,
        get_approval_status_info,
        calculate_expense_statistics,
        create_csv_download,
        render_print_form
    )

def show_corporate_account_management_page():
    """법인 관리 페이지"""
    show_corporate_account_management(
        db_operations.load_data,
        db_operations.save_data,
        db_operations.update_data,
        db_operations.delete_data,
        auth_manager.get_current_user
    )

def show_product_code_management_page():
    """제품 코드 관리 페이지"""
    try:
        show_product_code_management(
            load_func=db_operations.load_data,
            save_func=db_operations.save_data,
            update_func=db_operations.update_data,
            delete_func=db_operations.delete_data
        )
    except Exception as e:
        st.error(f"제품 코드 관리 페이지 로드 중 오류가 발생했습니다: {str(e)}")
        st.info("시스템 관리자에게 문의해주세요.")
        
def show_product_management_page():
    """제품 관리 페이지"""
    try:
        show_product_management(
            load_func=db_operations.load_data,
            save_func=db_operations.save_data,
            update_func=db_operations.update_data,
            delete_func=db_operations.delete_data
        )
    except Exception as e:
        st.error(f"제품 관리 페이지 로드 중 오류가 발생했습니다: {str(e)}")
        st.info("시스템 관리자에게 문의해주세요.")

def show_supplier_management_page():
    """공급업체 관리 페이지"""
    try:
        show_supplier_management(
            load_func=db_operations.load_data,
            save_func=db_operations.save_data,
            update_func=db_operations.update_data,
            delete_func=db_operations.delete_data
        )
    except Exception as e:
        st.error(f"공급업체 관리 페이지 로드 중 오류: {str(e)}")

def show_customer_management_page():
    """고객 관리 페이지"""
    try:
        show_customer_management(
            load_func=db_operations.load_data,
            save_func=db_operations.save_data,
            update_func=db_operations.update_data,
            delete_func=db_operations.delete_data
        )
    except Exception as e:
        st.error(f"고객 관리 페이지 로드 중 오류: {str(e)}")
        st.info("시스템 관리자에게 문의해주세요.")

def show_sales_process_management_page():
    """영업 프로세스 관리 페이지"""
    show_sales_process_management(
        db_operations.load_data,
        db_operations.save_data,
        db_operations.update_data,
        db_operations.delete_data,
        auth_manager.get_current_user,
        auth_manager.check_permission,
        get_approval_status_info,
        calculate_expense_statistics,
        create_csv_download,
        render_print_form
    )

def show_purchase_management_page():
    """구매품 관리 페이지"""
    show_purchase_management(
        db_operations.load_data,
        db_operations.save_data,
        db_operations.update_data,
        db_operations.delete_data,
        auth_manager.get_current_user()
    )

def show_quotation_management_page():
    """견적서 관리 페이지"""
    
    # 로그인 체크
    if 'current_user' not in st.session_state or not st.session_state.current_user:
        st.warning("로그인이 필요합니다. 사이드바에서 로그인해주세요.")
        return
    
    show_quotation_management(
        save_func=db_operations.save_data,
        load_func=db_operations.load_data,
        update_func=db_operations.update_data,
        delete_func=db_operations.delete_data,
        current_user=st.session_state.current_user
    )


def show_multilingual_input():
    """다국어 입력 페이지"""
    st.title("🌐 다국어 입력 시스템")
    ml_input = MultilingualInputComponent(init_supabase())
    
    # 언어 우선순위 정보 표시
    ml_input.render_language_priority_info()
    
    # 언어 선택기
    language = ml_input.render_language_selector()
    
    # 다국어 입력 테스트
    st.subheader("다국어 제품명 입력 테스트")
    name_en, name_vn = ml_input.render_multilingual_input()
    
    if name_en:
        # 입력 검증
        errors = ml_input.validate_multilingual_input(name_en, name_vn)
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            # 포맷된 데이터 표시
            formatted_data = ml_input.format_multilingual_data(name_en, name_vn)
            st.success("입력이 완료되었습니다!")
            st.json(formatted_data)

def show_hot_runner_order_sheet_page():
    """Hot Runner Order Sheet 페이지"""
    show_hot_runner_order_management(
        db_operations.load_data,
        db_operations.save_data,
        db_operations.update_data,
        auth_manager.get_current_user()
    )

# ===========================================
# 메인 애플리케이션
# ===========================================

def main():
    """메인 애플리케이션"""
    
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "대시보드"
    
    # 공통 날짜/시간 설정
    st.session_state.today = date.today()
    st.session_state.now = datetime.now().isoformat()
    
    # 물류 시스템용 Supabase 연결 보장
    if 'supabase' not in st.session_state:
        st.session_state.supabase = init_supabase()

    # 로그인 확인
    if not auth_manager.is_logged_in():
        show_login_page()
        return
    
    # 사이드바 메뉴
    with st.sidebar:
        st.title("🏢 YMV 시스템")
        
        current_user = auth_manager.get_current_user()
        
        # session_state에 저장
        st.session_state.current_user = current_user
        
        if current_user:
            st.write(f"👤 {current_user.get('name', 'Unknown')}")
            st.write(f"🏛️ {current_user.get('department', 'Unknown')}")
            
            if st.button("🚪 로그아웃", type="secondary", use_container_width=True):
                auth_manager.logout_user()
        
        st.divider()
        # 메뉴 카테고리별 버튼
        st.subheader("📊 분석 및 관리")
        if st.button("📈 대시보드", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "대시보드" else "secondary"):
            st.session_state.current_page = "대시보드"
            st.rerun()
        
        st.subheader("💼 영업 관리")
        if st.button("👥 고객 관리", use_container_width=True,
                    type="primary" if st.session_state.current_page == "고객 관리" else "secondary"):
            st.session_state.current_page = "고객 관리"
            st.rerun()
            
        if st.button("📋 견적서 관리", use_container_width=True,
                    type="primary" if st.session_state.current_page == "견적서 관리" else "secondary"):
            st.session_state.current_page = "견적서 관리"
            st.rerun()
        
        # 👇 규격 결정서 - 영업 관리로 이동
        if st.button("🔥 규격 결정서", use_container_width=True,
                    type="primary" if st.session_state.current_page == "규격 결정서" else "secondary"):
            st.session_state.current_page = "규격 결정서"
            st.rerun()

        if st.button("📊 실적 관리", use_container_width=True,
                    type="primary" if st.session_state.current_page == "실적 관리" else "secondary"):
            st.session_state.current_page = "실적 관리"
            st.rerun()    

        if st.button("🎯 영업 프로세스", use_container_width=True,
                    type="primary" if st.session_state.current_page == "영업 프로세스" else "secondary"):
            st.session_state.current_page = "영업 프로세스"
            st.rerun()
        
        st.subheader("🏭 운영 관리")
        if st.button("🏷️ 제품 코드 관리", use_container_width=True,
                    type="primary" if st.session_state.current_page == "제품 코드 관리" else "secondary"):
            st.session_state.current_page = "제품 코드 관리"
            st.rerun()
            
        if st.button("📦 제품 관리", use_container_width=True,
                    type="primary" if st.session_state.current_page == "제품 관리" else "secondary"):
            st.session_state.current_page = "제품 관리"
            st.rerun()
            
        if st.button("🏢 공급업체 관리", use_container_width=True,
                    type="primary" if st.session_state.current_page == "공급업체 관리" else "secondary"):
            st.session_state.current_page = "공급업체 관리"
            st.rerun()
                        
        if st.button("🛒 구매품 관리", use_container_width=True,
                    type="primary" if st.session_state.current_page == "구매품 관리" else "secondary"):
            st.session_state.current_page = "구매품 관리"
            st.rerun()

        # 👇 규격 결정서 제거됨 (기존 위치)
        
        st.subheader("🚚 물류 관리")
        if st.button("🚚 물류사 관리", use_container_width=True,
                    type="primary" if st.session_state.current_page == "물류사 관리" else "secondary"):
            st.session_state.current_page = "물류사 관리"
            st.rerun()
        
        st.subheader("👤 인사 관리")
        if st.button("👨‍💼 직원 관리", use_container_width=True,
                    type="primary" if st.session_state.current_page == "직원 관리" else "secondary"):
            st.session_state.current_page = "직원 관리"
            st.rerun()

        if st.button("🏢 법인 관리", use_container_width=True,
            type="primary" if st.session_state.current_page == "법인 계정 관리" else "secondary"):
            st.session_state.current_page = "법인 계정 관리"
            st.rerun()

        if st.button("💳 지출 요청서", use_container_width=True,
                    type="primary" if st.session_state.current_page == "지출 요청서" else "secondary"):
            st.session_state.current_page = "지출 요청서"
            st.rerun()
        
        # 환급 관리 메뉴 (권한 있는 사용자만)
        if current_user and current_user.get('role') in ['Admin', 'CEO']:
            if st.button("💰 환급 관리", use_container_width=True,
                        type="primary" if st.session_state.current_page == "환급 관리" else "secondary"):
                st.session_state.current_page = "환급 관리"
                st.rerun()
        
        st.subheader("⚙️ 시스템 설정")
        if st.button("🌐 다국어 입력", use_container_width=True,
                    type="primary" if st.session_state.current_page == "다국어 입력" else "secondary"):
            st.session_state.current_page = "다국어 입력"
            st.rerun()
    
    # 현재 페이지 표시
    current_page = st.session_state.current_page
    
    # 페이지별 라우팅
    if current_page == "대시보드":
        show_dashboard()
    elif current_page == "고객 관리":
        show_customer_management_page()
    elif current_page == "견적서 관리":
        show_quotation_management_page()
    elif current_page == "규격 결정서":  # 👈 추가
        show_hot_runner_order_sheet_page()
    elif current_page == "실적 관리":
        show_performance_management(db_operations.load_data, db_operations.update_data)
    elif current_page == "영업 프로세스":
        show_sales_process_management_page()
    elif current_page == "제품 코드 관리":
        show_product_code_management_page()
    elif current_page == "제품 관리":
        show_product_management_page()
    elif current_page == "공급업체 관리":
        show_supplier_management_page()
    elif current_page == "구매품 관리":
        show_purchase_management_page()
    elif current_page == "물류사 관리":
        show_logistics_management(
            db_operations.load_data,
            db_operations.save_data,
            db_operations.update_data,
            db_operations.delete_data
        )
    elif current_page == "직원 관리":
        show_employee_management_page()
    elif current_page == "법인 계정 관리":
        show_corporate_account_management_page()
    elif current_page == "지출 요청서":
        show_expense_management_page()
    elif current_page == "환급 관리":
        show_reimbursement_management_page()
    elif current_page == "다국어 입력":
        show_multilingual_input()
    elif current_page == "Hot Runner Order Sheet":  # 👈 제거 예정 (호환성)
        show_hot_runner_order_sheet_page()

if __name__ == "__main__":
    main()