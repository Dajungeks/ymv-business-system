"""
YMV 비즈니스 시스템 - 사용자 관리 모듈
"""

import streamlit as st
import bcrypt
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

from app.shared.database import get_db
from app.shared.utils import (
    show_success_message, show_error_message, show_warning_message,
    validate_email, export_to_csv, format_date
)
from app.shared.translations import t
from app.modules.auth.login import get_auth_manager

def user_management_page():
    """사용자 관리 메인 페이지"""
    st.markdown(f"# 👥 {t('user_management')}")
    
    # 권한 확인
    auth = get_auth_manager()
    current_user = auth.get_current_user()
    
    if not current_user or not current_user.get('is_master', False):
        st.error("❌ 관리자 권한이 필요합니다.")
        return
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["👤 사용자 목록", "➕ 새 사용자", "🔑 권한 관리"])
    
    with tab1:
        show_users_list()
    
    with tab2:
        add_new_user()
    
    with tab3:
        manage_permissions()

def show_users_list():
    """사용자 목록 표시"""
    st.markdown("### 👤 등록된 사용자")
    
    db = get_db()
    if not db:
        st.error("데이터베이스 연결 실패")
        return
    
    # 사용자 목록 조회
    users = db.execute_query(
        "users", 
        columns="user_id, username, email, full_name, department, position, is_active, is_master, created_at"
    )
    
    if not users:
        st.info("등록된 사용자가 없습니다.")
        return
    
    # 검색 및 필터
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 사용자 검색", placeholder="이름, 사용자명, 이메일")
    
    with col2:
        dept_filter = st.selectbox("부서 필터", ["전체"] + list(set([u['department'] for u in users if u['department']])))
    
    with col3:
        status_filter = st.selectbox("상태 필터", ["전체", "활성", "비활성"])
    
    # 필터링
    filtered_users = users
    
    if search_term:
        filtered_users = [
            u for u in filtered_users 
            if search_term.lower() in (u['username'] or '').lower() 
            or search_term.lower() in (u['full_name'] or '').lower()
            or search_term.lower() in (u['email'] or '').lower()
        ]
    
    if dept_filter != "전체":
        filtered_users = [u for u in filtered_users if u['department'] == dept_filter]
    
    if status_filter == "활성":
        filtered_users = [u for u in filtered_users if u['is_active']]
    elif status_filter == "비활성":
        filtered_users = [u for u in filtered_users if not u['is_active']]
    
    # 사용자 테이블 표시
    if filtered_users:
        df = pd.DataFrame(filtered_users)
        
        # 열 이름 변경
        df.columns = ['ID', '사용자명', '이메일', '성명', '부서', '직급', '활성', '관리자', '생성일']
        
        # 표시 형식 변경
        df['활성'] = df['활성'].map({True: '✅', False: '❌'})
        df['관리자'] = df['관리자'].map({True: '👑', False: ''})
        df['생성일'] = pd.to_datetime(df['생성일']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 내보내기 버튼
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📥 CSV 내보내기"):
                csv_data = export_to_csv(filtered_users, "users.csv")
                st.download_button(
                    label="다운로드",
                    data=csv_data,
                    file_name=f"users_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # 사용자 편집
        st.markdown("---")
        st.markdown("### ✏️ 사용자 편집")
        
        if len(filtered_users) > 0:
            selected_user_id = st.selectbox(
                "편집할 사용자 선택",
                options=[u['user_id'] for u in filtered_users],
                format_func=lambda x: next((u['full_name'] + f" ({u['username']})") for u in filtered_users if u['user_id'] == x)
            )
            
            if selected_user_id:
                edit_user(selected_user_id)
        else:
            st.info("편집할 사용자가 없습니다.")

def add_new_user():
    """새 사용자 추가"""
    st.markdown("### ➕ 새 사용자 등록")
    
    # 베트남 기업 기준 드롭다운 옵션
    departments = [
        "선택하세요",
        "경영진 (Management)",
        "인사부 (HR)",
        "회계부 (Accounting)", 
        "영업부 (Sales)",
        "구매부 (Purchasing)",
        "생산부 (Production)",
        "품질관리 (QC)",
        "IT부 (IT)",
        "총무부 (General Affairs)"
    ]
    
    positions = [
        "선택하세요",
        "사장 (President)",
        "부사장 (Vice President)", 
        "이사 (Director)",
        "부장 (General Manager)",
        "과장 (Manager)",
        "대리 (Assistant Manager)",
        "주임 (Supervisor)",
        "사원 (Staff)"
    ]
    
    # 자동 생성된 직원 ID 미리보기
    auto_employee_id = generate_employee_id()
    st.info(f"🆔 자동 생성될 직원 ID: **{auto_employee_id}**")
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("성명 *")
            email = st.text_input("이메일 *")
            password = st.text_input("임시 비밀번호 *", type="password", value="1234")
        
        with col2:
            department = st.selectbox("부서", departments)
            position = st.selectbox("직급", positions)
            is_master = st.checkbox("관리자 권한 부여")
        
        submitted = st.form_submit_button("👤 사용자 등록", use_container_width=True)
        
        if submitted:
            # 입력 검증
            if not email or not full_name:
                show_error_message("필수 항목을 모두 입력해주세요.")
                return
            
            if department == "선택하세요":
                show_error_message("부서를 선택해주세요.")
                return
                
            if position == "선택하세요":
                show_error_message("직급을 선택해주세요.")
                return
            
            if not validate_email(email):
                show_error_message("올바른 이메일 형식이 아닙니다.")
                return
            
            # 실제 직원 ID 생성 (최신)
            employee_id = generate_employee_id()
            
            # 사용자 생성
            if create_user({
                'username': employee_id,  # 직원 ID를 사용자명으로 사용
                'email': email,
                'password': password,
                'full_name': full_name,
                'department': department,
                'position': position,
                'phone': '',
                'is_master': is_master
            }):
                show_success_message(f"사용자 '{full_name}' (ID: {employee_id})가 성공적으로 등록되었습니다.")
                st.rerun()

def generate_employee_id() -> str:
    """직원 ID 자동 생성 (YYMMDD-Count)"""
    from datetime import date
    
    db = get_db()
    if not db:
        return "250101-01"  # 기본값
    
    today = date.today()
    date_prefix = today.strftime("%y%m%d")
    
    try:
        # 오늘 날짜로 생성된 마지막 직원 ID 조회
        existing_users = db.execute_query(
            "users", 
            columns="username",
            conditions={}
        )
        
        # 오늘 날짜 패턴과 일치하는 ID 찾기
        today_pattern = f"{date_prefix}-"
        max_count = 0
        
        for user in existing_users:
            username = user['username']
            if username.startswith(today_pattern) and len(username) == 9:  # YYMMDD-NN
                try:
                    count = int(username.split('-')[1])
                    max_count = max(max_count, count)
                except:
                    continue
        
        # 다음 번호 생성
        next_count = max_count + 1
        return f"{date_prefix}-{next_count:02d}"
        
    except Exception as e:
        # 오류 시 기본값 반환
        return f"{date_prefix}-01"



def create_user(user_data: Dict) -> bool:
    """사용자 생성"""
    db = get_db()
    if not db:
        show_error_message("데이터베이스 연결 실패")
        return False
    
    try:
        # 중복 확인
        existing_user = db.execute_query("users", conditions={"username": user_data['username']})
        if existing_user:
            show_error_message("이미 존재하는 사용자명입니다.")
            return False
        
        existing_email = db.execute_query("users", conditions={"email": user_data['email']})
        if existing_email:
            show_error_message("이미 등록된 이메일입니다.")
            return False
        
        # 비밀번호 해시화
        password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 사용자 데이터 준비
        insert_data = {
            'username': user_data['username'],
            'email': user_data['email'],
            'password_hash': password_hash,
            'full_name': user_data['full_name'],
            'department': user_data.get('department'),
            'position': user_data.get('position'),
            'is_master': user_data.get('is_master', False),
            'is_active': True
        }

        # phone이 있고 비어있지 않으면 추가
        if user_data.get('phone') and user_data.get('phone').strip():
            insert_data['phone'] = user_data['phone']
        
        # 사용자 삽입
        result = db.execute_query("users", "insert", data=insert_data)
        
        if result:
            return True
        else:
            show_error_message("사용자 생성 중 오류가 발생했습니다.")
            return False
            
    except Exception as e:
        show_error_message(f"사용자 생성 오류: {str(e)}")
        return False

def edit_user(user_id: int):
    """사용자 편집"""
    db = get_db()
    if not db:
        return
    
    # 현재 사용자 정보 조회
    user = db.execute_query("users", conditions={"user_id": user_id})
    if not user:
        st.error("사용자를 찾을 수 없습니다.")
        return
    
    user = user[0]
    
    # 베트남 기업 기준 드롭다운 옵션
    departments = [
        "경영진 (Management)",
        "인사부 (HR)",
        "회계부 (Accounting)", 
        "영업부 (Sales)",
        "구매부 (Purchasing)",
        "생산부 (Production)",
        "품질관리 (QC)",
        "IT부 (IT)",
        "총무부 (General Affairs)"
    ]
    
    positions = [
        "사장 (President)",
        "부사장 (Vice President)", 
        "이사 (Director)",
        "부장 (General Manager)",
        "과장 (Manager)",
        "대리 (Assistant Manager)",
        "주임 (Supervisor)",
        "사원 (Staff)"
    ]
    
    with st.form(f"edit_user_{user_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("성명", value=user['full_name'])
            email = st.text_input("이메일", value=user['email'])
            
            # 현재 부서가 목록에 있는지 확인
            dept_index = 0
            if user['department'] in departments:
                dept_index = departments.index(user['department'])
            department = st.selectbox("부서", departments, index=dept_index)
        
        with col2:
            # 현재 직급이 목록에 있는지 확인  
            pos_index = 0
            if user['position'] in positions:
                pos_index = positions.index(user['position'])
            position = st.selectbox("직급", positions, index=pos_index)
            
            is_active = st.checkbox("활성 상태", value=user['is_active'])
        
        # Master 계정은 비활성화 불가
        if user['username'] == 'Master':
            st.info("Master 계정은 수정할 수 없습니다.")
            is_active = True
        
        col1, col2 = st.columns(2)
        
        with col1:
            update_submitted = st.form_submit_button("💾 정보 수정")
        
        with col2:
            if user['username'] != 'Master':
                delete_submitted = st.form_submit_button("🗑️ 사용자 삭제", type="secondary")
            else:
                delete_submitted = False
        
            if update_submitted:
                from datetime import datetime, timezone
                
                update_data = {
                    'full_name': full_name,
                    'email': email,
                    'department': department,
                    'position': position,
                    'is_active': is_active,
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
                
                result = db.execute_query("users", "update", data=update_data, conditions={"user_id": user_id})
                if result:
                    show_success_message("사용자 정보가 수정되었습니다.")
                    st.rerun()
                else:
                    show_error_message("사용자 정보 수정에 실패했습니다.")
        
        if delete_submitted:
            if st.session_state.get(f'confirm_delete_{user_id}', False):
                # 실제 삭제 실행
                result = db.execute_query("users", "delete", conditions={"user_id": user_id})
                if result:
                    show_success_message(f"사용자 '{user['full_name']}'이 삭제되었습니다.")
                    st.rerun()
                else:
                    show_error_message("사용자 삭제에 실패했습니다.")
            else:
                # 삭제 확인
                st.session_state[f'confirm_delete_{user_id}'] = True
                show_warning_message("다시 삭제 버튼을 클릭하면 사용자가 영구 삭제됩니다.")
                st.rerun()
def manage_permissions():
    """권한 관리"""
    st.markdown("### 🔑 사용자 권한 관리")
    
    db = get_db()
    if not db:
        return
    
    # 사용자 선택
    users = db.execute_query("users", columns="user_id, username, full_name", conditions={"is_active": True})
    
    if not users:
        st.info("활성 사용자가 없습니다.")
        return
    
    selected_user_id = st.selectbox(
        "권한을 설정할 사용자 선택",
        options=[u['user_id'] for u in users],
        format_func=lambda x: next(u['full_name'] + f" ({u['username']})" for u in users if u['user_id'] == x)
    )
    
    if selected_user_id:
        manage_user_permissions(selected_user_id)

def manage_user_permissions(user_id: int):
    """특정 사용자의 권한 관리"""
    db = get_db()
    
    # 현재 권한 조회
    current_permissions = db.execute_query("user_permissions", conditions={"user_id": user_id})
    current_perms_dict = {perm['menu_name']: perm for perm in current_permissions} if current_permissions else {}
    
    # 메뉴별 권한 설정
    menus = [
        'system_management',
        'customer_management', 
        'quotation_management',
        'purchase_management',
        'cash_flow_management'
    ]
    
    st.markdown("#### 메뉴별 접근 권한")
    
    permissions_to_save = []
    
    for menu in menus:
        with st.container():
            st.markdown(f"**{t(menu)}**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            current_perm = current_perms_dict.get(menu, {})
            
            with col1:
                can_access = st.checkbox("접근", key=f"{menu}_access", value=current_perm.get('can_access', False))
            
            with col2:
                can_create = st.checkbox("생성", key=f"{menu}_create", value=current_perm.get('can_create', False))
            
            with col3:
                can_edit = st.checkbox("편집", key=f"{menu}_edit", value=current_perm.get('can_edit', False))
            
            with col4:
                can_delete = st.checkbox("삭제", key=f"{menu}_delete", value=current_perm.get('can_delete', False))
            
            permissions_to_save.append({
                'menu_name': menu,
                'can_access': can_access,
                'can_create': can_create,
                'can_edit': can_edit,
                'can_delete': can_delete
            })
    
    if st.button("💾 권한 저장", use_container_width=True):
        save_user_permissions(user_id, permissions_to_save)

def save_user_permissions(user_id: int, permissions: List[Dict]):
    """사용자 권한 저장"""
    db = get_db()
    
    try:
        # 기존 권한 삭제
        db.execute_query("user_permissions", "delete", conditions={"user_id": user_id})
        
        # 새 권한 저장
        for perm in permissions:
            perm_data = {
                'user_id': user_id,
                'menu_name': perm['menu_name'],
                'can_access': perm['can_access'],
                'can_create': perm['can_create'],
                'can_edit': perm['can_edit'],
                'can_delete': perm['can_delete']
            }
            
            db.execute_query("user_permissions", "insert", data=perm_data)
        
        show_success_message("권한이 성공적으로 저장되었습니다.")
        
    except Exception as e:
        show_error_message(f"권한 저장 오류: {str(e)}")

# 메인 실행
if __name__ == "__main__":
    user_management_page()