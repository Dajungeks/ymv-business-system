"""
YMV 비즈니스 시스템 - 다국어 지원 시스템
"""

import streamlit as st
from typing import Dict, Optional
from .database import get_db

# 기본 번역 데이터 (데이터베이스 연결 실패 시 사용)
DEFAULT_TRANSLATIONS = {
    "ko": {
        # 공통
        "login": "로그인",
        "logout": "로그아웃",
        "save": "저장",
        "cancel": "취소",
        "delete": "삭제",
        "edit": "편집",
        "add": "추가",
        "search": "검색",
        "export": "내보내기",
        "import": "가져오기",
        "dashboard": "대시보드",
        "settings": "설정",
        
        # 메뉴
        "system_management": "시스템 관리",
        "user_management": "사용자 관리",
        "product_management": "제품 관리",
        "customer_management": "고객 관리",
        "quotation_management": "견적서 관리",
        "purchase_management": "구매 관리",
        "cash_flow_management": "현금 흐름 관리",
        
        # 필드
        "username": "사용자명",
        "password": "비밀번호",
        "email": "이메일",
        "phone": "전화번호",
        "address": "주소",
        "company": "회사",
        "department": "부서",
        "position": "직급",
        "name": "이름",
        "description": "설명",
        "price": "가격",
        "quantity": "수량",
        "total": "합계",
        "date": "날짜",
        "status": "상태",
        
        # 메시지
        "login_success": "로그인 성공",
        "login_failed": "로그인 실패",
        "invalid_credentials": "잘못된 인증 정보",
        "access_denied": "접근 권한이 없습니다",
        "save_success": "저장되었습니다",
        "delete_success": "삭제되었습니다",
        "error_occurred": "오류가 발생했습니다",
    },
    
    "en": {
        # Common
        "login": "Login",
        "logout": "Logout",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "edit": "Edit",
        "add": "Add",
        "search": "Search",
        "export": "Export",
        "import": "Import",
        "dashboard": "Dashboard",
        "settings": "Settings",
        
        # Menus
        "system_management": "System Management",
        "user_management": "User Management",
        "product_management": "Product Management",
        "customer_management": "Customer Management",
        "quotation_management": "Quotation Management",
        "purchase_management": "Purchase Management",
        "cash_flow_management": "Cash Flow Management",
        
        # Fields
        "username": "Username",
        "password": "Password",
        "email": "Email",
        "phone": "Phone",
        "address": "Address",
        "company": "Company",
        "department": "Department",
        "position": "Position",
        "name": "Name",
        "description": "Description",
        "price": "Price",
        "quantity": "Quantity",
        "total": "Total",
        "date": "Date",
        "status": "Status",
        
        # Messages
        "login_success": "Login successful",
        "login_failed": "Login failed",
        "invalid_credentials": "Invalid credentials",
        "access_denied": "Access denied",
        "save_success": "Saved successfully",
        "delete_success": "Deleted successfully",
        "error_occurred": "An error occurred",
    },
    
    "vi": {
        # Common
        "login": "Đăng nhập",
        "logout": "Đăng xuất",
        "save": "Lưu",
        "cancel": "Hủy",
        "delete": "Xóa",
        "edit": "Chỉnh sửa",
        "add": "Thêm",
        "search": "Tìm kiếm",
        "export": "Xuất",
        "import": "Nhập",
        "dashboard": "Bảng điều khiển",
        "settings": "Cài đặt",
        
        # Menus
        "system_management": "Quản lý hệ thống",
        "user_management": "Quản lý người dùng",
        "product_management": "Quản lý sản phẩm",
        "customer_management": "Quản lý khách hàng",
        "quotation_management": "Quản lý báo giá",
        "purchase_management": "Quản lý mua hàng",
        "cash_flow_management": "Quản lý dòng tiền",
        
        # Fields
        "username": "Tên đăng nhập",
        "password": "Mật khẩu",
        "email": "Email",
        "phone": "Điện thoại",
        "address": "Địa chỉ",
        "company": "Công ty",
        "department": "Phòng ban",
        "position": "Chức vụ",
        "name": "Tên",
        "description": "Mô tả",
        "price": "Giá",
        "quantity": "Số lượng",
        "total": "Tổng cộng",
        "date": "Ngày",
        "status": "Trạng thái",
        
        # Messages
        "login_success": "Đăng nhập thành công",
        "login_failed": "Đăng nhập thất bại",
        "invalid_credentials": "Thông tin đăng nhập không đúng",
        "access_denied": "Không có quyền truy cập",
        "save_success": "Đã lưu thành công",
        "delete_success": "Đã xóa thành công",
        "error_occurred": "Đã xảy ra lỗi",
    }
}

class TranslationManager:
    """번역 관리 클래스"""
    
    def __init__(self):
        self.translations = DEFAULT_TRANSLATIONS.copy()
        self.load_from_database()
    
    def load_from_database(self):
        """데이터베이스에서 번역 데이터 로드"""
        try:
            db = get_db()
            if db and db.supabase:
                result = db.execute_query("translations")
                if result:
                    for item in result:
                        lang = item['language_code']
                        key = item['translation_key']
                        value = item['translation_value']
                        
                        if lang not in self.translations:
                            self.translations[lang] = {}
                        
                        self.translations[lang][key] = value
        except Exception as e:
            # 데이터베이스 연결 실패 시 기본값 사용
            pass
    
    def get_translation(self, key: str, language: str = "ko") -> str:
        """번역 텍스트 가져오기"""
        try:
            return self.translations.get(language, {}).get(key, key)
        except:
            return key
    
    def get_supported_languages(self) -> Dict[str, str]:
        """지원하는 언어 목록"""
        return {
            "ko": "한국어",
            "en": "English", 
            "vi": "Tiếng Việt"
        }

# 전역 번역 매니저 인스턴스
@st.cache_resource
def get_translation_manager():
    """번역 매니저 싱글톤 인스턴스"""
    return TranslationManager()

def get_current_language() -> str:
    """현재 선택된 언어 가져오기"""
    if 'language' not in st.session_state:
        st.session_state.language = 'ko'  # 기본값: 한국어
    return st.session_state.language

def set_language(language: str):
    """언어 설정"""
    st.session_state.language = language

def t(key: str, language: Optional[str] = None) -> str:
    """번역 함수 (간단한 사용을 위한 별칭)"""
    if language is None:
        language = get_current_language()
    
    manager = get_translation_manager()
    return manager.get_translation(key, language)

def create_language_selector():
    """언어 선택기 UI 생성"""
    manager = get_translation_manager()
    languages = manager.get_supported_languages()
    
    current_lang = get_current_language()
    
    selected_lang = st.selectbox(
        "🌐 Language / 언어 / Ngôn ngữ",
        options=list(languages.keys()),
        format_func=lambda x: languages[x],
        index=list(languages.keys()).index(current_lang),
        key="language_selector"
    )
    
    if selected_lang != current_lang:
        set_language(selected_lang)
        st.rerun()