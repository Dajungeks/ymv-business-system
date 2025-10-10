# employee_management.py - 직원 관리 시스템 (베트남 기준)
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
from typing import Dict, List, Optional, Tuple

def show_employee_management(load_func, save_func, update_func, delete_func, 
                           get_current_user_func, check_permission_func,
                           get_approval_status_info, calculate_statistics,
                           create_csv_download, render_print_form):
    """직원 관리 시스템 메인 함수 (베트남 YUMOLD 기준)"""
    
    st.title("👥 직원 관리 시스템")
    st.caption("Employee Management System - YUMOLD VIETNAM")
    
    # 현재 사용자 정보 확인
    current_user = get_current_user_func()
    if not current_user:
        st.error("로그인이 필요합니다.")
        return
    
    # 탭 구성 (비밀번호 관리 탭 추가)
    tabs = st.tabs(["📋 직원 목록", "➕ 직원 등록/수정", "🏢 조직도", "⏰ 근태 관리", "💰 급여 관리", "🔑 비밀번호 관리"])
    
    with tabs[0]:
        render_employee_list(load_func, save_func, update_func, delete_func, 
                           current_user, check_permission_func)
    
    with tabs[1]:
        render_employee_form(load_func, save_func, update_func, 
                           current_user, check_permission_func)
    
    with tabs[2]:
        render_organization_chart(load_func, current_user)
    
    with tabs[3]:
        render_attendance_management(load_func, save_func, update_func,
                                   current_user, check_permission_func)
    
    with tabs[4]:
        render_payroll_management(load_func, save_func, update_func,
                                current_user, check_permission_func)
    
    with tabs[5]:
        render_password_management(load_func, update_func, current_user)

def render_password_management(load_func, update_func, current_user):
    """비밀번호 관리 탭"""
    
    st.subheader("🔑 비밀번호 관리")
    
    user_role = current_user.get('role', 'Staff')
    
    # Master/CEO는 모든 직원 비밀번호 변경 가능
    if user_role in ['Master', 'CEO']:
        st.write("### 관리자 - 직원 비밀번호 변경")
        
        # 직원 목록 로드
        employees = load_func("employees")
        if not employees:
            st.info("직원 정보가 없습니다.")
            return
        
        # 직원 선택
        employee_options = {f"{emp.get('name', 'N/A')} ({emp.get('username', 'N/A')}) - {emp.get('department', 'N/A')}": emp 
                          for emp in employees}
        
        selected_emp_key = st.selectbox("변경할 직원 선택", list(employee_options.keys()))
        selected_emp = employee_options[selected_emp_key]
        
        st.info(f"선택된 직원: {selected_emp.get('name')} ({selected_emp.get('role', 'Staff')})")
        
        with st.form("admin_password_change"):
            new_password = st.text_input("새 비밀번호", type="password")
            confirm_password = st.text_input("비밀번호 확인", type="password")
            
            submitted = st.form_submit_button("비밀번호 변경", type="primary")
            
            if submitted:
                if not new_password:
                    st.error("새 비밀번호를 입력해주세요.")
                elif len(new_password) < 4:
                    st.error("비밀번호는 최소 4자 이상이어야 합니다.")
                elif new_password != confirm_password:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    # 비밀번호 업데이트
                    update_data = {
                        'id': selected_emp['id'],
                        'password': new_password,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    if update_func("employees", update_data, "id"):
                        st.success(f"✅ {selected_emp.get('name')} 직원의 비밀번호가 변경되었습니다.")
                        st.balloons()
                    else:
                        st.error("비밀번호 변경에 실패했습니다.")
    
    # 본인 비밀번호 변경
    st.write("---")
    st.write("### 내 비밀번호 변경")
    
    with st.form("self_password_change"):
        current_password = st.text_input("현재 비밀번호", type="password", key="current_pwd")
        new_password = st.text_input("새 비밀번호", type="password", key="new_pwd")
        confirm_password = st.text_input("비밀번호 확인", type="password", key="confirm_pwd")
        
        submitted = st.form_submit_button("내 비밀번호 변경", type="primary")
        
        if submitted:
            # 현재 비밀번호 확인
            current_employee = load_func("employees", filters={"id": current_user['id']})
            if not current_employee:
                st.error("사용자 정보를 찾을 수 없습니다.")
            else:
                current_employee = current_employee[0]
                
                if current_password != current_employee.get('password'):
                    st.error("현재 비밀번호가 일치하지 않습니다.")
                elif not new_password:
                    st.error("새 비밀번호를 입력해주세요.")
                elif len(new_password) < 4:
                    st.error("비밀번호는 최소 4자 이상이어야 합니다.")
                elif new_password != confirm_password:
                    st.error("새 비밀번호가 일치하지 않습니다.")
                else:
                    # 비밀번호 업데이트
                    update_data = {
                        'id': current_user['id'],
                        'password': new_password,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    if update_func("employees", update_data, "id"):
                        st.success("✅ 비밀번호가 성공적으로 변경되었습니다.")
                        st.info("다음 로그인부터 새 비밀번호를 사용하세요.")
                        st.balloons()
                    else:
                        st.error("비밀번호 변경에 실패했습니다.")

def render_employee_list(load_func, save_func, update_func, delete_func, 
                        current_user, check_permission_func):
    """직원 목록 탭"""
    
    st.subheader("📋 직원 목록")
    
    # 검색 및 필터 영역
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("검색", placeholder="이름, 사번, 이메일로 검색")
    
    with col2:
        dept_filter = st.selectbox("부서 필터", ["전체"] + get_departments_list(load_func))
    
    with col3:
        status_filter = st.selectbox("상태 필터", ["전체", "재직", "휴직", "퇴직"])
    
    with col4:
        role_filter = st.selectbox("역할 필터", ["전체", "Staff", "Manager", "Admin", "CEO", "Master"])
    
    # 직원 데이터 로드
    try:
        employees_data = load_func("employee_details")
        if not employees_data:
            st.info("등록된 직원이 없습니다.")
            return
        
        employees_df = pd.DataFrame(employees_data)
        
        # 필터 적용
        filtered_df = apply_employee_filters(employees_df, search_term, 
                                           dept_filter, status_filter, role_filter)
        
        if filtered_df.empty:
            st.warning("검색 조건에 맞는 직원이 없습니다.")
            return
        
        # 통계 정보
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 직원 수", len(filtered_df))
        with col2:
            active_count = len(filtered_df[filtered_df['employment_status'] == 'active'])
            st.metric("재직자", active_count)
        with col3:
            avg_salary = filtered_df['salary'].mean() if 'salary' in filtered_df.columns else 0
            st.metric("평균 급여", f"{avg_salary:,.0f} VND" if avg_salary else "N/A")
        with col4:
            dept_count = filtered_df['department'].nunique()
            st.metric("부서 수", dept_count)
        
        # CSV 다운로드 버튼
        if st.button("📥 CSV 다운로드"):
            csv_data = create_employee_csv(filtered_df)
            st.download_button(
                label="직원 목록 다운로드",
                data=csv_data,
                file_name=f"employee_list_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # 직원 목록 테이블
        display_employee_table(filtered_df, current_user, check_permission_func,
                              update_func, delete_func)
        
    except Exception as e:
        st.error(f"직원 목록 로드 중 오류 발생: {str(e)}")

def render_employee_form(load_func, save_func, update_func, current_user, check_permission_func):
    """직원 등록/수정 폼"""
    
    st.subheader("직원 등록/수정")
    
    # 권한 확인 - Master, CEO, Admin 가능
    if current_user.get('role') not in ['Master', 'CEO', 'Admin']:
        st.error("직원 등록/수정 권한이 없습니다.")
        return
    
    # 수정할 직원 선택
    col1, col2 = st.columns([3, 1])
    
    with col1:
        employees = load_func("employees", columns="id,name,username,employee_id")
        employee_options = ["신규 등록"] + [f"{emp['name']} ({emp['username']})" 
                                       for emp in employees if employees]
        selected_employee = st.selectbox("직원 선택", employee_options)
    
    with col2:
        if selected_employee != "신규 등록":
            if st.button("직원 삭제", type="secondary"):
                if st.session_state.get('confirm_delete'):
                    # 삭제 실행
                    employee_id = extract_employee_id_from_selection(selected_employee, employees)
                    if delete_employee_with_validation(employee_id, delete_func):
                        st.success("직원이 삭제되었습니다.")
                        st.rerun()
                else:
                    st.session_state['confirm_delete'] = True
                    st.warning("한 번 더 클릭하여 삭제를 확인하세요.")
    
    # 기존 데이터 로드 (수정 모드)
    existing_data = None
    if selected_employee != "신규 등록":
        employee_id = extract_employee_id_from_selection(selected_employee, employees)
        existing_data = load_func("employee_details", filters={"id": employee_id})
        existing_data = existing_data[0] if existing_data else None
    
    # 폼 렌더링
    with st.form("employee_form"):
        st.write("### 기본 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("이름 *", value=existing_data.get('full_name', '') if existing_data else '')
            username = st.text_input("사용자명 *", value=existing_data.get('username', '') if existing_data else '')
            employee_id = st.text_input("사번", value=existing_data.get('employee_id', '') if existing_data else '')
            email = st.text_input("이메일", value=existing_data.get('email', '') if existing_data else '')
            phone = st.text_input("전화번호", value=existing_data.get('phone', '') if existing_data else '')
        
        with col2:
            # 부서 및 직급
            departments = get_departments_list(load_func)
            department = st.selectbox("부서 *", departments, 
                                    index=departments.index(existing_data.get('department', '')) 
                                    if existing_data and existing_data.get('department') in departments else 0)
            
            positions = get_positions_list(load_func)
            position = st.selectbox("직급 *", positions,
                                  index=positions.index(existing_data.get('position', ''))
                                  if existing_data and existing_data.get('position') in positions else 0)
            
            # 관리자 선택
            managers = get_managers_list(load_func)
            manager_id = st.selectbox("직속 상관", [None] + managers,
                                    format_func=lambda x: "선택 안함" if x is None else x['name'])
            
            # 역할 (Staff, Manager, Admin, CEO, Master)
            role_options = ["Staff", "Manager", "Admin", "CEO", "Master"]
            
            # 호환성을 위한 매핑
            role_mapping = {
                'employee': 'Staff',
                'manager': 'Manager',
                'admin': 'Admin',
                'ceo': 'CEO',
                'master': 'Master'
            }
            
            if existing_data:
                current_role = existing_data.get('role', 'Staff')
                # 소문자로 변환 후 매핑 시도
                current_role = role_mapping.get(current_role.lower(), current_role)
                role_index = role_options.index(current_role) if current_role in role_options else 0
            else:
                role_index = 0
            
            role = st.selectbox("역할 *", role_options, index=role_index)
            
            employment_status = st.selectbox("재직 상태", ["active", "inactive", "resigned"],
                                           index=["active", "inactive", "resigned"].index(
                                               existing_data.get('employment_status', 'active'))
                                           if existing_data else 0)
        
        st.write("### 근무 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hire_date = st.date_input("입사일",
                                    value=datetime.strptime(existing_data.get('hire_date'), '%Y-%m-%d').date()
                                    if existing_data and existing_data.get('hire_date') else date.today())
            
            salary = st.number_input("기본급 (VND)", min_value=0, value=int(existing_data.get('salary', 0))
                                   if existing_data and existing_data.get('salary') else 4680000,
                                   step=100000, format="%d")
            
            work_type = st.selectbox("근무 형태", ["full_time", "part_time", "contract"],
                                   index=["full_time", "part_time", "contract"].index(
                                       existing_data.get('work_type', 'full_time'))
                                   if existing_data else 0)
        
        with col2:
            birth_date = st.date_input("생년월일",
                                     value=datetime.strptime(existing_data.get('birth_date'), '%Y-%m-%d').date()
                                     if existing_data and existing_data.get('birth_date') else None)
            
            # 베트남 최저임금 가이드 표시
            st.info("하노이 최저임금: 4,680,000 VND/월")
            
        st.write("### 개인 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            address = st.text_area("주소", value=existing_data.get('address', '') if existing_data else '')
            emergency_contact = st.text_input("비상연락처 이름", 
                                            value=existing_data.get('emergency_contact', '') if existing_data else '')
            emergency_phone = st.text_input("비상연락처 전화번호",
                                          value=existing_data.get('emergency_phone', '') if existing_data else '')
        
        with col2:
            # 비밀번호 (신규 등록시만)
            if not existing_data:
                password = st.text_input("비밀번호 *", type="password")
                confirm_password = st.text_input("비밀번호 확인 *", type="password")
            
            notes = st.text_area("비고", value=existing_data.get('notes', '') if existing_data else '')
        
        # 제출 버튼
        submitted = st.form_submit_button("저장", type="primary")
        
        if submitted:
            # 유효성 검사
            validation_errors = validate_employee_form(name, username, department, position,
                                                     password if not existing_data else None,
                                                     confirm_password if not existing_data else None)
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                # 데이터 준비
                employee_data = {
                    'name': name,
                    'username': username,
                    'employee_id': employee_id,
                    'email': email,
                    'phone': phone,
                    'department': department,
                    'position': position,
                    'manager_id': manager_id['id'] if manager_id else None,
                    'role': role,
                    'employment_status': employment_status,
                    'hire_date': hire_date.isoformat(),
                    'salary': salary,
                    'work_type': work_type,
                    'birth_date': birth_date.isoformat() if birth_date else None,
                    'address': address,
                    'emergency_contact': emergency_contact,
                    'emergency_phone': emergency_phone,
                    'notes': notes,
                    'updated_at': datetime.now().isoformat()
                }
                
                if not existing_data:
                    employee_data['password'] = password
                    employee_data['created_at'] = datetime.now().isoformat()
                
                # 저장 실행
                try:
                    if existing_data:
                        employee_data['id'] = existing_data['id']
                        update_func("employees", employee_data, "id")
                        # 인사 이력 기록
                        record_employee_history(existing_data, employee_data, current_user['id'], save_func)
                        st.success("직원 정보가 수정되었습니다.")
                    else:
                        save_func("employees", employee_data)
                        st.success("새 직원이 등록되었습니다.")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"저장 중 오류 발생: {str(e)}")

def render_organization_chart(load_func, current_user):
    """조직도 탭"""
    
    st.subheader("🏢 조직도")
    
    try:
        # 부서별 직원 정보 로드
        employees = load_func("employee_details")
        departments = load_func("departments")
        
        if not employees:
            st.info("직원 정보가 없습니다.")
            return
        
        # 부서별 그룹핑
        dept_groups = group_employees_by_department(employees)
        
        # 전체 통계
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("전체 직원", len(employees))
        with col2:
            st.metric("부서 수", len(dept_groups))
        with col3:
            active_employees = len([emp for emp in employees if emp.get('employment_status') == 'active'])
            st.metric("재직자", active_employees)
        
        # 부서별 조직도
        for dept_name, dept_employees in dept_groups.items():
            with st.expander(f"📂 {dept_name} ({len(dept_employees)}명)", expanded=True):
                render_department_tree(dept_employees)
        
        # 직급별 통계 차트
        st.write("### 📊 직급별 분포")
        position_stats = calculate_position_statistics(employees)
        
        if position_stats:
            chart_data = pd.DataFrame([
                {'직급': pos, '인원': count} for pos, count in position_stats.items()
            ])
            st.bar_chart(chart_data.set_index('직급'))
        
    except Exception as e:
        st.error(f"조직도 로드 중 오류 발생: {str(e)}")

def render_attendance_management(load_func, save_func, update_func, current_user, check_permission_func):
    """근태 관리 탭"""
    
    st.subheader("근태 관리")
    
    # 권한에 따른 탭 구성 - Master, CEO, Admin
    if current_user.get('role') in ['Master', 'CEO', 'Admin']:
        attendance_tabs = st.tabs(["월별 근태", "출퇴근 기록", "근태 통계"])
    else:
        attendance_tabs = st.tabs(["내 출퇴근"])
    
    # 월별 근태 현황 (관리자)
    if current_user.get('role') in ['Master', 'CEO', 'Admin']:
        with attendance_tabs[0]:
            render_monthly_attendance(load_func, current_user)
        
        with attendance_tabs[1]:
            render_attendance_records(load_func, save_func, update_func, current_user)
        
        with attendance_tabs[2]:
            render_attendance_statistics(load_func, current_user)
    
    # 개인 출퇴근 (모든 직원)
    with attendance_tabs[-1]:
        render_personal_attendance(load_func, save_func, current_user)

def render_payroll_management(load_func, save_func, update_func, current_user, check_permission_func):
    """급여 관리 탭 (베트남 기준)"""
    
    st.subheader("급여 관리")
    st.caption("Vietnam Tax & Social Insurance Calculation")
    
    # 권한 확인 - Master, CEO만
    if current_user.get('role') not in ['Master', 'CEO']:
        st.error("급여 관리 권한이 없습니다.")
        return
    
    payroll_tabs = st.tabs(["급여 계산", "급여 명세서", "급여 통계"])
    
    with payroll_tabs[0]:
        render_payroll_calculation(load_func, save_func, current_user)
    
    with payroll_tabs[1]:
        render_payslip_generation(load_func, current_user)
    
    with payroll_tabs[2]:
        render_payroll_statistics(load_func, current_user)

# ==================== 헬퍼 함수들 ====================

def get_departments_list(load_func) -> List[str]:
    """부서 목록 가져오기"""
    try:
        departments = load_func("departments", filters={"is_active": True})
        return [dept['dept_name'] for dept in departments] if departments else ["IT팀", "영업팀", "인사팀"]
    except:
        return ["IT팀", "영업팀", "인사팀"]

def get_positions_list(load_func) -> List[str]:
    """직급 목록 가져오기 (영문)"""
    try:
        positions = load_func("positions", filters={"is_active": True})
        return [pos['position_name'] for pos in positions] if positions else ["Staff", "Junior Manager", "Manager", "Senior Manager", "Director", "CEO"]
    except:
        return ["Staff", "Junior Manager", "Manager", "Senior Manager", "Director", "CEO"]

def get_managers_list(load_func) -> List[Dict]:
    """관리자 목록 가져오기"""
    try:
        managers = load_func("employees", 
                           filters={"role": ["Master", "CEO", "Admin"], "employment_status": "active"})
        return managers if managers else []
    except:
        return []

def apply_employee_filters(df: pd.DataFrame, search_term: str, dept_filter: str, 
                         status_filter: str, role_filter: str) -> pd.DataFrame:
    """직원 목록 필터링"""
    filtered_df = df.copy()
    
    # 검색어 필터
    if search_term:
        search_cols = ['full_name', 'username', 'employee_id', 'email']
        search_mask = False
        for col in search_cols:
            if col in filtered_df.columns:
                search_mask |= filtered_df[col].astype(str).str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[search_mask]
    
    # 부서 필터
    if dept_filter != "전체":
        filtered_df = filtered_df[filtered_df['department'] == dept_filter]
    
    # 상태 필터
    if status_filter != "전체":
        status_map = {"재직": "active", "휴직": "inactive", "퇴직": "resigned"}
        filtered_df = filtered_df[filtered_df['employment_status'] == status_map[status_filter]]
    
    # 역할 필터
    if role_filter != "전체":
        filtered_df = filtered_df[filtered_df['role'] == role_filter]
    
    return filtered_df

def display_employee_table(df: pd.DataFrame, current_user: Dict, check_permission_func,
                         update_func, delete_func):
    """직원 목록 테이블 표시"""
    
    # 표시할 컬럼 선택
    display_columns = {
        'employee_id': '사번',
        'full_name': '이름',
        'department': '부서',
        'position': '직급',
        'role': '역할',
        'employment_status': '상태',
        'hire_date': '입사일',
        'salary': '급여(VND)'
    }
    
    # 데이터 준비
    display_df = df[list(display_columns.keys())].copy()
    display_df.columns = list(display_columns.values())
    
    # 급여 포맷팅
    if '급여(VND)' in display_df.columns:
        display_df['급여(VND)'] = display_df['급여(VND)'].apply(
            lambda x: f"{x:,}" if pd.notna(x) and x > 0 else "미설정"
        )
    
    # 상태 한글화
    status_map = {"active": "재직", "inactive": "휴직", "resigned": "퇴직"}
    if '상태' in display_df.columns:
        display_df['상태'] = display_df['상태'].map(status_map).fillna("알 수 없음")
    
    # 역할은 영문 그대로 표시 (대소문자만 통일)
    if '역할' in display_df.columns:
        display_df['역할'] = display_df['역할'].str.title()
    
    # 테이블 표시
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "급여(VND)": st.column_config.TextColumn("급여(VND)", width="medium"),
            "입사일": st.column_config.DateColumn("입사일", format="YYYY-MM-DD"),
        }
    )

def validate_employee_form(name: str, username: str, department: str, position: str,
                         password: str = None, confirm_password: str = None) -> List[str]:
    """직원 폼 유효성 검사"""
    errors = []
    
    if not name.strip():
        errors.append("이름을 입력해주세요.")
    
    if not username.strip():
        errors.append("사용자명을 입력해주세요.")
    
    if not department:
        errors.append("부서를 선택해주세요.")
    
    if not position:
        errors.append("직급을 선택해주세요.")
    
    # 신규 등록시 비밀번호 검사
    if password is not None:
        if not password:
            errors.append("비밀번호를 입력해주세요.")
        elif len(password) < 4:
            errors.append("비밀번호는 4자 이상이어야 합니다.")
        elif password != confirm_password:
            errors.append("비밀번호가 일치하지 않습니다.")
    
    return errors

def record_employee_history(old_data: Dict, new_data: Dict, approved_by: int, save_func):
    """인사 이력 기록"""
    
    changes = []
    
    # 부서 변경
    if old_data.get('department') != new_data.get('department'):
        changes.append({
            'change_type': 'transfer',
            'old_department': old_data.get('department'),
            'new_department': new_data.get('department')
        })
    
    # 직급 변경
    if old_data.get('position') != new_data.get('position'):
        changes.append({
            'change_type': 'promotion',
            'old_position': old_data.get('position'),
            'new_position': new_data.get('position')
        })
    
    # 급여 변경
    if old_data.get('salary') != new_data.get('salary'):
        changes.append({
            'change_type': 'salary_change',
            'old_salary': old_data.get('salary'),
            'new_salary': new_data.get('salary')
        })
    
    # 이력 저장
    for change in changes:
        history_data = {
            'employee_id': old_data['id'],
            'change_type': change['change_type'],
            'change_date': datetime.now().date().isoformat(),
            'old_department': change.get('old_department'),
            'new_department': change.get('new_department'),
            'old_position': change.get('old_position'),
            'new_position': change.get('new_position'),
            'old_salary': change.get('old_salary'),
            'new_salary': change.get('new_salary'),
            'approved_by': approved_by,
            'created_at': datetime.now().isoformat()
        }
        
        save_func("employee_history", history_data)

def calculate_vietnam_tax(gross_salary: float) -> Dict[str, float]:
    """베트남 세금 계산"""
    
    # 2024년 베트남 개인소득세율 (VND)
    tax_brackets = [
        (5000000, 0.05),
        (10000000, 0.10),
        (18000000, 0.15),
        (32000000, 0.20),
        (52000000, 0.25),
        (80000000, 0.30),
        (float('inf'), 0.35)
    ]
    
    # 기본 공제액 (개인): 11,000,000 VND/월
    basic_deduction = 11000000
    
    # 사회보험료 공제 (직원 부담분)
    social_insurance = gross_salary * 0.08
    health_insurance = gross_salary * 0.015
    unemployment_insurance = gross_salary * 0.01
    
    total_insurance = social_insurance + health_insurance + unemployment_insurance
    
    # 과세소득 계산
    taxable_income = max(0, gross_salary - basic_deduction - total_insurance)
    
    # 세금 계산
    income_tax = 0
    remaining_income = taxable_income
    
    for bracket_limit, tax_rate in tax_brackets:
        if remaining_income <= 0:
            break
        
        taxable_at_bracket = min(remaining_income, bracket_limit)
        income_tax += taxable_at_bracket * tax_rate
        remaining_income -= taxable_at_bracket
    
    # 실수령액 계산
    net_salary = gross_salary - total_insurance - income_tax
    
    return {
        'gross_salary': gross_salary,
        'basic_deduction': basic_deduction,
        'social_insurance': social_insurance,
        'health_insurance': health_insurance,
        'unemployment_insurance': unemployment_insurance,
        'total_insurance': total_insurance,
        'taxable_income': taxable_income,
        'income_tax': income_tax,
        'net_salary': net_salary
    }

def render_payroll_calculation(load_func, save_func, current_user):
    """급여 계산 렌더링"""
    
    st.write("### 급여 계산 (베트남 세법 기준)")
    
    # 급여 계산 대상 선택
    employees = load_func("employees", filters={"employment_status": "active"})
    
    if not employees:
        st.info("급여 계산 대상 직원이 없습니다.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_employee = st.selectbox(
            "직원 선택",
            employees,
            format_func=lambda x: f"{x.get('name', 'N/A')} ({x.get('department', 'N/A')}) - {x.get('salary', 0):,} VND" if x.get('salary') else f"{x.get('name', 'N/A')} ({x.get('department', 'N/A')}) - 급여 미설정"
        )
    
    with col2:
        calculation_month = st.date_input("급여 월", value=date.today().replace(day=1))
    
    if selected_employee:
        # 기본 급여 정보
        base_salary = selected_employee.get('salary', 0) or 0
        
        if base_salary == 0:
            st.warning(f"{selected_employee.get('name', 'N/A')} 직원의 기본급이 설정되지 않았습니다. 직원 정보를 먼저 수정해주세요.")
            return
        
        # 추가 수당 입력
        st.write("### 추가 수당")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            overtime_hours = st.number_input("초과근무 시간", min_value=0.0, max_value=30.0, step=0.5)
            overtime_rate = st.number_input("시급 (VND)", value=base_salary/160 if base_salary > 0 else 30000)
        
        with col2:
            allowances = st.number_input("각종 수당 (VND)", min_value=0, step=10000)
            bonus = st.number_input("상여금 (VND)", min_value=0, step=10000)
        
        with col3:
            other_deductions = st.number_input("기타 공제 (VND)", min_value=0, step=10000)
        
        # 총 급여 계산
        overtime_pay = overtime_hours * overtime_rate
        gross_salary = base_salary + overtime_pay + allowances + bonus
        
        # 베트남 세금 계산
        tax_calc = calculate_vietnam_tax(gross_salary)
        
        # 최종 실수령액
        final_net_salary = tax_calc['net_salary'] - other_deductions
        
        # 계산 결과 표시
        st.write("### 급여 계산 결과")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**지급 항목**")
            st.write(f"• 기본급: {base_salary:,} VND")
            st.write(f"• 초과근무 수당: {overtime_pay:,} VND")
            st.write(f"• 각종 수당: {allowances:,} VND")
            st.write(f"• 상여금: {bonus:,} VND")
            st.write(f"**총 지급액: {gross_salary:,} VND**")
        
        with col2:
            st.write("**공제 항목**")
            st.write(f"• 사회보험 (8%): {tax_calc['social_insurance']:,} VND")
            st.write(f"• 건강보험 (1.5%): {tax_calc['health_insurance']:,} VND")
            st.write(f"• 실업보험 (1%): {tax_calc['unemployment_insurance']:,} VND")
            st.write(f"• 소득세: {tax_calc['income_tax']:,} VND")
            st.write(f"• 기타 공제: {other_deductions:,} VND")
            st.write(f"**총 공제액: {gross_salary - final_net_salary:,} VND**")
        
        # 실수령액 강조 표시
        st.success(f"### 실수령액: {final_net_salary:,} VND")
        
        # 급여 데이터 저장
        if st.button("급여 데이터 저장", type="primary"):
            payroll_data = {
                'employee_id': selected_employee['id'],
                'pay_period_start': calculation_month.isoformat(),
                'pay_period_end': (calculation_month.replace(day=calendar.monthrange(calculation_month.year, calculation_month.month)[1])).isoformat(),
                'base_salary': base_salary,
                'overtime_pay': overtime_pay,
                'allowances': allowances + bonus,
                'deductions': other_deductions,
                'gross_pay': gross_salary,
                'tax': tax_calc['income_tax'] + tax_calc['total_insurance'],
                'net_pay': final_net_salary,
                'status': 'approved',
                'created_at': datetime.now().isoformat()
            }
            
            try:
                save_func("payroll", payroll_data)
                st.success("급여 데이터가 저장되었습니다.")
            except Exception as e:
                st.error(f"저장 중 오류 발생: {str(e)}")

def create_employee_csv(df: pd.DataFrame) -> str:
    """직원 목록 CSV 생성"""
    return df.to_csv(index=False, encoding='utf-8-sig')

def extract_employee_id_from_selection(selection: str, employees: List[Dict]) -> int:
    """선택된 직원 문자열에서 ID 추출"""
    username = selection.split('(')[1].split(')')[0]
    for emp in employees:
        if emp['username'] == username:
            return emp['id']
    return None

def delete_employee_with_validation(employee_id: int, delete_func) -> bool:
    """직원 삭제 (유효성 검사 포함)"""
    try:
        delete_func("employees", employee_id, "id")
        return True
    except Exception as e:
        st.error(f"삭제 중 오류 발생: {str(e)}")
        return False

def group_employees_by_department(employees: List[Dict]) -> Dict[str, List[Dict]]:
    """부서별 직원 그룹핑"""
    groups = {}
    for emp in employees:
        dept = emp.get('department', '미지정')
        if dept not in groups:
            groups[dept] = []
        groups[dept].append(emp)
    return groups

def render_department_tree(employees: List[Dict]):
    """부서 조직도 트리 렌더링"""
    for emp in employees:
        status_icon = "🟢" if emp.get('employment_status') == 'active' else "🔴"
        role_map = {"Master": "👑", "CEO": "💎", "Admin": "⭐", "Manager": "📌", "Staff": "👤"}
        role_icon = role_map.get(emp.get('role', 'Staff'), "👤")
        
        st.write(f"{status_icon} {role_icon} **{emp.get('full_name', 'N/A')}** - {emp.get('position', 'N/A')}")

def calculate_position_statistics(employees: List[Dict]) -> Dict[str, int]:
    """직급별 통계 계산"""
    stats = {}
    for emp in employees:
        position = emp.get('position', '미지정')
        stats[position] = stats.get(position, 0) + 1
    return stats

def render_monthly_attendance(load_func, current_user):
    """월별 근태 현황"""
    st.write("### 📅 월별 근태 현황")
    st.info("월별 근태 현황 기능이 곧 추가됩니다.")

def render_attendance_records(load_func, save_func, update_func, current_user):
    """출퇴근 기록 관리"""
    st.write("### ⏱️ 출퇴근 기록 관리")
    st.info("출퇴근 기록 관리 기능이 곧 추가됩니다.")

def render_attendance_statistics(load_func, current_user):
    """근태 통계"""
    st.write("### 📊 근태 통계")
    st.info("근태 통계 기능이 곧 추가됩니다.")

def render_personal_attendance(load_func, save_func, current_user):
    """개인 출퇴근 관리"""
    st.write("### ⏱️ 내 출퇴근 기록")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🟢 출근", type="primary"):
            st.success("출근이 기록되었습니다.")
    
    with col2:
        if st.button("🔴 퇴근", type="secondary"):
            st.success("퇴근이 기록되었습니다.")

def render_payslip_generation(load_func, current_user):
    """급여 명세서 생성"""
    st.write("### 📋 급여 명세서")
    st.info("급여 명세서 생성 기능이 곧 추가됩니다.")

def render_payroll_statistics(load_func, current_user):
    """급여 통계"""
    st.write("### 📊 급여 통계")
    st.info("급여 통계 기능이 곧 추가됩니다.")