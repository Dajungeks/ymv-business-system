"""
YMV 비즈니스 관리 시스템 - 메인 애플리케이션
"""

import streamlit as st
import sys
import os
from datetime import datetime

# 기존 import 문들 아래에 추가
from app.modules.system.users import user_management_page
from app.modules.admin.general_affairs import general_affairs_page
from app.modules.system.products import product_management_page
from app.modules.system.categories import category_management_page

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 공통 모듈 임포트
from app.shared.database import get_db
from app.shared.utils import show_success_message, show_error_message
from app.shared.translations import t, create_language_selector, get_current_language

def init_session_state():
    """세션 상태 초기화"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'language' not in st.session_state:
        st.session_state.language = 'ko'
    if 'current_menu' not in st.session_state:
        st.session_state.current_menu = 'dashboard'

def check_authentication():
    """인증 확인"""
    return st.session_state.get('authenticated', False)

def login_form():
    """로그인 폼"""
    st.markdown("## 🏢 YMV 비즈니스 관리 시스템")
    st.markdown("---")
    
    # 언어 선택기
    create_language_selector()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"### {t('login')}")
        
        with st.form("login_form"):
            username = st.text_input(t("username"), placeholder="Master")
            password = st.text_input(t("password"), type="password", placeholder="1023")
            login_button = st.form_submit_button(t("login"), use_container_width=True)
            
            if login_button:
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.user_info = {
                        'username': username,
                        'user_id': 1 if username == "Master" else 0,
                        'is_master': username == "Master"
                    }
                    show_success_message(t("login_success"))
                    st.rerun()
                else:
                    show_error_message(t("login_failed"))

def authenticate_user(username: str, password: str) -> bool:
    """사용자 인증"""
    # 임시 인증 (나중에 데이터베이스 연결 후 실제 인증 구현)
    if username == "Master" and password == "1023":
        return True
    
    # TODO: 데이터베이스에서 사용자 인증
    # db = get_db()
    # user = db.get_user_by_username(username)
    # if user and verify_password(password, user['password_hash']):
    #     return True
    
    return False

def create_sidebar():
    """사이드바 메뉴 생성"""
    with st.sidebar:
        st.markdown("### 🏢 YMV 시스템")
        
        # 사용자 정보
        user_info = st.session_state.get('user_info', {})
        st.markdown(f"**{t('username')}:** {user_info.get('username', 'Unknown')}")
        
        st.markdown("---")
        
        # 메인 메뉴
        # 메인 메뉴
        menu_items = {
            'dashboard': "대시보드",
            'system': "시스템 관리",
            'customers': "고객 관리",
            'quotations': "견적서 관리",
            'purchases': "구매 관리",
            'cashflow': "현금 흐름 관리",
        }
        
        selected_menu = st.radio(
            "메뉴 선택",
            options=list(menu_items.keys()),
            format_func=lambda x: menu_items[x],
            key="menu_selection"
        )
        
        st.session_state.current_menu = selected_menu
        
        st.markdown("---")
        
        # 언어 변경
        create_language_selector()
        
        # 로그아웃
        if st.button(f"🚪 {t('logout')}", use_container_width=True):
            st.session_state.clear()
            st.rerun()

def show_dashboard():
    """대시보드 화면"""
    st.markdown(f"# 📊 {t('dashboard')}")
    
    # 요약 카드들
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📋 견적서",
            value="12",
            delta="2"
        )
    
    with col2:
        st.metric(
            label="👥 고객",
            value="45",
            delta="5"
        )
    
    with col3:
        st.metric(
            label="🛒 구매",
            value="8",
            delta="-1"
        )
    
    with col4:
        st.metric(
            label="💰 현금 흐름",
            value="$25,430",
            delta="$2,100"
        )
    
    st.markdown("---")
    
    # 빠른 액션
    st.markdown("### ⚡ 빠른 액션")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.form("quotation_form"):
            submitted1 = st.form_submit_button("📝 새 견적서 작성", use_container_width=True)
            if submitted1:
                st.session_state['current_menu'] = 'quotations'
                st.rerun()
    
    with col2:
        with st.form("customer_form"):
            submitted2 = st.form_submit_button("👤 새 고객 추가", use_container_width=True)
            if submitted2:
                st.session_state['current_menu'] = 'customers'
                st.rerun()
    
    with col3:
        with st.form("purchase_form"):
            submitted3 = st.form_submit_button("🛒 새 구매 등록", use_container_width=True)
            if submitted3:
                st.session_state['current_menu'] = 'purchases'
                st.rerun()
    
    # 디버깅용
    st.write(f"현재 메뉴: {st.session_state.get('current_menu', 'dashboard')}")
            
def show_coming_soon(module_name: str):
    """개발 예정 화면"""
    st.markdown(f"# 🚧 {module_name}")
    st.info(f"""
    **{module_name}** 모듈은 현재 개발 중입니다.
    
    📅 **예정 기능:**
    - 데이터 관리 및 조회
    - 추가/편집/삭제 기능
    - CSV/Excel 내보내기
    - 다국어 지원
    
    곧 업데이트될 예정입니다! 🚀
    """)

def main():
    """메인 함수"""
    # 세션 상태 초기화
    init_session_state()
    
    # 인증 확인
    if not check_authentication():
        login_form()
        return
    
    # 인증된 사용자 화면
    create_sidebar()
    
    # 현재 메뉴에 따른 화면 표시
    current_menu = st.session_state.get('current_menu', 'dashboard')
    
    if current_menu == 'dashboard':
        show_dashboard()
    elif current_menu == 'system':
        system_management_tabs()
    elif current_menu == 'customers':
        show_coming_soon("고객 관리")
    elif current_menu == 'quotations':
        show_coming_soon("견적서 관리")
    elif current_menu == 'purchases':
        general_affairs_page()
    elif current_menu == 'cashflow':
        general_affairs_page()
    else:
        show_dashboard()
def system_management_tabs():
    """시스템 관리 탭 구성"""
    tab1, tab2, tab3 = st.tabs(["사용자 관리", "제품 관리", "카테고리 관리"])
    
    with tab1:
        user_management_page()
    
    with tab2:
        product_management_page()
    
    with tab3:
        category_management_page()
if __name__ == "__main__":
    main()