import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import io
from collections import defaultdict

def show_expense_management(load_data_func, save_data_func, update_data_func, delete_data_func, 
                           get_current_user_func, get_approval_status_info_func, 
                           calculate_expense_statistics_func, create_csv_download_func, 
                           render_print_form_func):
    """지출 요청서 관리 컴포넌트 메인 함수"""
    
    st.header("💰 지출 요청서 관리")
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(["📝 지출요청서 작성", "📋 지출요청서 목록", "📊 지출 통계", "👨‍💼 CEO 승인"])
    
    with tab1:
        render_expense_form(load_data_func, save_data_func, get_current_user_func)
    
    with tab2:
        render_expense_list(load_data_func, update_data_func, delete_data_func, 
                          get_current_user_func, get_approval_status_info_func, 
                          create_csv_download_func, render_print_form_func)
    
    with tab3:
        render_expense_statistics(load_data_func, calculate_expense_statistics_func)
    
    with tab4:
        render_ceo_approval(load_data_func, update_data_func, get_current_user_func, 
                          get_approval_status_info_func)

def render_expense_form(load_data_func, save_data_func, get_current_user_func):
    """지출요청서 작성 폼 (안전한 필드 접근 적용)"""
    
    # 직원 정보 로드
    employees = load_data_func("employees")
    if not employees:
        st.error("직원 정보를 불러올 수 없습니다.")
        return
    
    # 현재 사용자 정보
    current_user = get_current_user_func()
    if not current_user:
        st.error("로그인 정보를 확인할 수 없습니다.")
        return
    
    # 폼 생성
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            request_date = st.date_input(
                "요청일",
                value=date.today(),
                key="expense_request_date"
            )
            
            # employee_id 필드 안전한 접근
            employee_options = {}
            for emp in employees:
                emp_id = emp.get('employee_id', f"ID{emp.get('id')}")
                emp_name = emp.get('name', '이름없음')
                employee_options[f"{emp_name} ({emp_id})"] = emp.get('id')
            
            # 현재 사용자 기본 선택
            current_emp_id = current_user.get('employee_id', f"ID{current_user.get('id')}")
            current_user_option = f"{current_user.get('name', '이름없음')} ({current_emp_id})"
            
            if current_user_option in employee_options:
                default_index = list(employee_options.keys()).index(current_user_option)
            else:
                default_index = 0
            
            selected_employee = st.selectbox(
                "요청자",
                options=list(employee_options.keys()),
                index=default_index,
                key="expense_employee"
            )
            employee_id = employee_options[selected_employee]
            
            department = st.text_input("부서", value=current_user.get('department', ''), key="expense_department")
            
        with col2:
            expense_date = st.date_input("지출일", key="expense_date")
            category = st.selectbox(
                "지출 카테고리",
                ["사무용품", "교통비", "식비", "회의비", "출장비", "기타"],
                key="expense_category"
            )
            amount = st.number_input(
                "금액 (원)",
                min_value=0,
                step=1000,
                key="expense_amount"
            )
        
        description = st.text_area("지출 내역", key="expense_description")
        receipt_number = st.text_input("영수증 번호 (선택사항)", key="expense_receipt")
        
        submitted = st.form_submit_button("💾 지출요청서 제출")
        
        if submitted:
            if amount <= 0:
                st.error("금액은 0보다 커야 합니다.")
            elif not description.strip():
                st.error("지출 내역을 입력해주세요.")
            else:
                # 지출요청서 데이터 준비 (안전한 필드 접근)
                expense_data = {
                    'request_date': request_date.strftime('%Y-%m-%d'),
                    'employee_id': employee_id,
                    'requester': employee_id,  # 백업 필드
                    'department': department,
                    'expense_date': expense_date.strftime('%Y-%m-%d'),
                    'category': category,
                    'amount': amount,
                    'description': description,
                    'expense_details': description,  # 백업 필드
                    'receipt_number': receipt_number if receipt_number else None,
                    'status': 'pending',
                    'approval_status': '대기중',  # 백업 필드
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # 데이터 저장
                if save_data_func("expenses", expense_data):
                    st.success("✅ 지출요청서가 성공적으로 제출되었습니다!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ 지출요청서 제출에 실패했습니다.")

def render_expense_list(load_data_func, update_data_func, delete_data_func, 
                       get_current_user_func, get_approval_status_info_func, 
                       create_csv_download_func, render_print_form_func):
    """지출요청서 목록 관리 (안전한 필드 접근 적용)"""
    
    # 데이터 로드
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not expenses:
        st.info("등록된 지출요청서가 없습니다.")
        return
    
    # 직원 정보를 딕셔너리로 변환 (안전한 접근)
    employee_dict = {}
    if employees:
        for emp in employees:
            emp_id = emp.get('id')
            if emp_id:
                employee_dict[emp_id] = emp
    
    # 현재 사용자 정보
    current_user = get_current_user_func()
    user_role = current_user.get('role', 'employee') if current_user else 'employee'
    current_user_id = current_user.get('id') if current_user else None
    
    # 필터링 옵션
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "상태 필터",
            ["전체", "대기", "승인", "거부"],
            key="expense_status_filter"
        )
    
    with col2:
        category_filter = st.selectbox(
            "카테고리 필터",
            ["전체", "사무용품", "교통비", "식비", "회의비", "출장비", "기타"],
            key="expense_category_filter"
        )
    
    with col3:
        if user_role == 'manager':
            employee_filter_options = ["전체"]
            for emp in employees:
                emp_name = emp.get('name', '이름없음')
                emp_id = emp.get('employee_id', f"ID{emp.get('id')}")
                employee_filter_options.append(f"{emp_name} ({emp_id})")
            
            employee_filter = st.selectbox(
                "직원 필터",
                employee_filter_options,
                key="expense_employee_filter"
            )
        else:
            employee_filter = "본인만"
    
    with col4:
        sort_order = st.selectbox(
            "정렬",
            ["최신순", "오래된순", "금액높은순", "금액낮은순"],
            key="expense_sort_order"
        )
    
    # 데이터 필터링 (안전한 필드 접근)
    filtered_expenses = []
    for expense in expenses:
        # 상태 필터링 (두 가지 필드 모두 확인)
        if status_filter != "전체":
            status_map = {"대기": ["pending", "대기중"], "승인": ["approved", "승인됨"], "거부": ["rejected", "거부됨"]}
            expense_status = expense.get('status') or expense.get('approval_status', '')
            if expense_status not in status_map[status_filter]:
                continue
        
        # 카테고리 필터링
        if category_filter != "전체" and expense.get('category') != category_filter:
            continue
        
        # 직원 필터링 (안전한 필드 접근)
        if user_role != 'manager':
            # 현재 사용자 본인 것만 표시 (여러 필드 확인)
            expense_requester = expense.get('employee_id') or expense.get('requester') or expense.get('user_id')
            if expense_requester != current_user_id:
                continue
        elif employee_filter != "전체":
            # 관리자가 특정 직원 선택한 경우
            employee_name = employee_filter.split(" (")[0]
            expense_emp_id = expense.get('employee_id') or expense.get('requester')
            if expense_emp_id:
                emp_info = employee_dict.get(expense_emp_id, {})
                if emp_info.get('name') != employee_name:
                    continue
        
        filtered_expenses.append(expense)
    
    # 정렬 (안전한 필드 접근)
    if sort_order == "최신순":
        filtered_expenses.sort(key=lambda x: x.get('request_date') or x.get('created_at', ''), reverse=True)
    elif sort_order == "오래된순":
        filtered_expenses.sort(key=lambda x: x.get('request_date') or x.get('created_at', ''))
    elif sort_order == "금액높은순":
        filtered_expenses.sort(key=lambda x: x.get('amount', 0), reverse=True)
    elif sort_order == "금액낮은순":
        filtered_expenses.sort(key=lambda x: x.get('amount', 0))
    
    # 검색 결과 표시
    st.write(f"📋 총 {len(filtered_expenses)}건의 지출요청서")
    
    # CSV 다운로드 버튼
    if filtered_expenses:
        csv_data = create_csv_download_func(filtered_expenses, employees)
        if csv_data:
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=f"expense_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # 지출요청서 목록 표시 (안전한 필드 접근)
    for idx, expense in enumerate(filtered_expenses):
        # 직원 정보 안전한 접근
        expense_emp_id = expense.get('employee_id') or expense.get('requester')
        employee_info = employee_dict.get(expense_emp_id, {})
        employee_name = employee_info.get('name', '알 수 없음')
        employee_id = employee_info.get('employee_id', f"ID{expense_emp_id}")
        
        # 상태 정보 (두 필드 모두 확인)
        expense_status = expense.get('status') or expense.get('approval_status', 'pending')
        # 상태 정규화
        if expense_status in ['pending', '대기중']:
            normalized_status = 'pending'
        elif expense_status in ['approved', '승인됨']:
            normalized_status = 'approved'
        elif expense_status in ['rejected', '거부됨']:
            normalized_status = 'rejected'
        else:
            normalized_status = 'pending'
        
        # 상태 이모지 직접 매핑 (안전한 방식)
        status_emoji_map = {
            'pending': '⏳',
            'approved': '✅', 
            'rejected': '❌'
        }
        status_emoji = status_emoji_map.get(normalized_status, '📄')
        
        # 지출요청서 카드
        request_date = expense.get('request_date') or expense.get('created_at', '')[:10] if expense.get('created_at') else 'N/A'
        category = expense.get('category', '기타')
        amount = expense.get('amount', 0)
        
        with st.expander(
            f"{status_emoji} [{request_date}] {employee_name} - {category} ({amount:,}원)",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**기본 정보**")
                st.write(f"• 요청자: {employee_name} ({employee_id})")
                st.write(f"• 부서: {expense.get('department', 'N/A')}")
                st.write(f"• 지출일: {expense.get('expense_date', 'N/A')}")
                st.write(f"• 카테고리: {category}")
                st.write(f"• 금액: {amount:,}원")
                st.write(f"• 영수증 번호: {expense.get('receipt_number', 'N/A')}")
                
                st.write("**지출 내역**")
                description = expense.get('description') or expense.get('expense_details', '내용없음')
                st.write(description)
                
                # 승인 정보 (승인/거부된 경우)
                if normalized_status in ['approved', 'rejected']:
                    st.write("**승인 정보**")
                    st.write(f"• 처리일: {expense.get('approved_at', 'N/A')}")
                    if expense.get('approved_by'):
                        approver = employee_dict.get(expense['approved_by'], {})
                        approver_name = approver.get('name', '알 수 없음')
                        st.write(f"• 처리자: {approver_name}")
                    approval_comment = expense.get('approval_comment') or expense.get('approval_comments')
                    if approval_comment:
                        st.write(f"• 처리 의견: {approval_comment}")
            
            with col2:
                # 상태 설명 직접 매핑
                status_desc_map = {
                    'pending': '승인 대기',
                    'approved': '승인됨',
                    'rejected': '거부됨'
                }
                status_description = status_desc_map.get(normalized_status, '알 수 없음')
                st.write(f"**상태**: {status_emoji} {status_description}")
                
                # 액션 버튼들
                button_col1, button_col2 = st.columns(2)
                
                with button_col1:
                    # 프린트 버튼
                    if st.button("🖨️ 프린트", key=f"print_{expense.get('id', idx)}"):
                        render_print_form_func(expense)
                
                with button_col2:
                    # 삭제 버튼 (본인 또는 관리자만, 대기중인 경우만)
                    expense_requester = expense.get('employee_id') or expense.get('requester')
                    can_delete = (user_role == 'manager' or expense_requester == current_user_id)
                    
                    if can_delete and normalized_status == 'pending':
                        if st.button("🗑️ 삭제", key=f"delete_{expense.get('id', idx)}"):
                            if delete_data_func("expenses", expense.get('id')):
                                st.success("지출요청서가 삭제되었습니다.")
                                st.rerun()
                            else:
                                st.error("삭제에 실패했습니다.")

def render_expense_statistics(load_data_func, calculate_expense_statistics_func):
    """지출 통계 표시"""
    
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not expenses:
        st.info("통계를 표시할 지출 데이터가 없습니다.")
        return
    
    # 통계 계산
    stats = calculate_expense_statistics_func(expenses)
    
    # 기본 통계 표시
    st.subheader("📊 지출 통계 대시보드")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 지출요청", f"{stats.get('total_count', 0)}건")
    
    with col2:
        st.metric("총 요청금액", f"{stats.get('total_amount', 0):,}원")
    
    with col3:
        st.metric("승인된 금액", f"{stats.get('approved_amount', 0):,}원")
    
    with col4:
        total_count = stats.get('total_count', 0)
        approved_count = stats.get('approved_count', 0)
        approval_rate = (approved_count / total_count * 100) if total_count > 0 else 0
        st.metric("승인율", f"{approval_rate:.1f}%")
    
    # 상태별 통계
    st.subheader("📈 상태별 분석")
    col1, col2 = st.columns(2)
    
    with col1:
        # 상태별 건수
        status_data = {
            "대기중": stats.get('pending_count', 0),
            "승인됨": stats.get('approved_count', 0),
            "거부됨": stats.get('rejected_count', 0)
        }
        
        if any(status_data.values()):
            st.write("**상태별 건수**")
            for status, count in status_data.items():
                st.write(f"• {status}: {count}건")
    
    with col2:
        # 카테고리별 통계
        category_stats = stats.get('category_stats', {})
        if category_stats:
            st.write("**카테고리별 통계**")
            for category, data in category_stats.items():
                if isinstance(data, dict):
                    count = data.get('count', 0)
                    amount = data.get('amount', 0)
                    st.write(f"• {category}: {count}건 ({amount:,}원)")
    
    # 월별 통계
    monthly_stats = stats.get('monthly_stats', {})
    if monthly_stats:
        st.subheader("📅 월별 지출 현황")
        
        # 월별 데이터를 DataFrame으로 변환
        monthly_data = []
        for month, data in monthly_stats.items():
            if isinstance(data, dict):
                monthly_data.append({
                    '월': month,
                    '건수': data.get('count', 0),
                    '금액': data.get('amount', 0)
                })
        
        if monthly_data:
            df_monthly = pd.DataFrame(monthly_data)
            st.dataframe(df_monthly, use_container_width=True)
            
            # 차트 표시
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**월별 건수**")
                st.bar_chart(df_monthly.set_index('월')['건수'])
            
            with col2:
                st.write("**월별 금액**")
                st.bar_chart(df_monthly.set_index('월')['금액'])

def render_ceo_approval(load_data_func, update_data_func, get_current_user_func, 
                       get_approval_status_info_func):
    """CEO 승인 관리 (안전한 필드 접근 적용)"""
    
    current_user = get_current_user_func()
    if not current_user or current_user.get('role') != 'manager':
        st.warning("⚠️ 관리자 권한이 필요합니다.")
        return
    
    # 승인 대기중인 지출요청서 로드
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not expenses:
        st.info("승인할 지출요청서가 없습니다.")
        return
    
    # 직원 정보를 딕셔너리로 변환 (안전한 접근)
    employee_dict = {}
    if employees:
        for emp in employees:
            emp_id = emp.get('id')
            if emp_id:
                employee_dict[emp_id] = emp
    
    # 대기중인 요청서만 필터링 (안전한 필드 접근)
    pending_expenses = []
    for exp in expenses:
        status = exp.get('status') or exp.get('approval_status', '')
        if status in ['pending', '대기중']:
            pending_expenses.append(exp)
    
    if not pending_expenses:
        st.info("승인 대기중인 지출요청서가 없습니다.")
        return
    
    st.subheader(f"👨‍💼 승인 대기중인 지출요청서 ({len(pending_expenses)}건)")
    
    # 정렬 옵션
    sort_option = st.selectbox(
        "정렬 기준",
        ["요청일순", "금액높은순", "금액낮은순"],
        key="approval_sort"
    )
    
    if sort_option == "요청일순":
        pending_expenses.sort(key=lambda x: x.get('request_date') or x.get('created_at', ''))
    elif sort_option == "금액높은순":
        pending_expenses.sort(key=lambda x: x.get('amount', 0), reverse=True)
    elif sort_option == "금액낮은순":
        pending_expenses.sort(key=lambda x: x.get('amount', 0))
    
    # 승인 대기 목록
    for expense in pending_expenses:
        # 직원 정보 안전한 접근
        expense_emp_id = expense.get('employee_id') or expense.get('requester')
        employee_info = employee_dict.get(expense_emp_id, {})
        employee_name = employee_info.get('name', '알 수 없음')
        employee_id = employee_info.get('employee_id', f"ID{expense_emp_id}")
        
        request_date = expense.get('request_date') or expense.get('created_at', '')[:10] if expense.get('created_at') else 'N/A'
        category = expense.get('category', '기타')
        amount = expense.get('amount', 0)
        
        with st.expander(
            f"💰 [{request_date}] {employee_name} - {category} ({amount:,}원)",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**요청 정보**")
                st.write(f"• 요청자: {employee_name} ({employee_id})")
                st.write(f"• 부서: {expense.get('department', 'N/A')}")
                st.write(f"• 요청일: {request_date}")
                st.write(f"• 지출일: {expense.get('expense_date', 'N/A')}")
                st.write(f"• 카테고리: {category}")
                st.write(f"• 금액: {amount:,}원")
                st.write(f"• 영수증 번호: {expense.get('receipt_number', 'N/A')}")
                
                st.write("**지출 내역**")
                description = expense.get('description') or expense.get('expense_details', '내용없음')
                st.write(description)
            
            with col2:
                st.write("**승인 처리**")
                
                # 승인 의견
                approval_comment = st.text_area(
                    "처리 의견 (선택사항)",
                    key=f"comment_{expense.get('id')}",
                    height=80
                )
                
                # 승인/거부 버튼
                button_col1, button_col2 = st.columns(2)
                
                with button_col1:
                    if st.button("✅ 승인", key=f"approve_{expense.get('id')}", type="primary"):
                        # 승인 처리
                        update_data = {
                            'id': expense.get('id'),
                            'status': 'approved',
                            'approval_status': '승인됨',  # 백업 필드
                            'approved_by': current_user.get('id'),
                            'approved_at': datetime.now().isoformat(),
                            'approval_comment': approval_comment if approval_comment else None,
                            'approval_comments': approval_comment if approval_comment else None,  # 백업 필드
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        if update_data_func("expenses", update_data):
                            st.success(f"✅ {employee_name}의 지출요청서를 승인했습니다.")
                            st.rerun()
                        else:
                            st.error("승인 처리에 실패했습니다.")
                
                with button_col2:
                    if st.button("❌ 거부", key=f"reject_{expense.get('id')}"):
                        # 거부 처리
                        update_data = {
                            'id': expense.get('id'),
                            'status': 'rejected',
                            'approval_status': '거부됨',  # 백업 필드
                            'approved_by': current_user.get('id'),
                            'approved_at': datetime.now().isoformat(),
                            'approval_comment': approval_comment if approval_comment else None,
                            'approval_comments': approval_comment if approval_comment else None,  # 백업 필드
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        if update_data_func("expenses", update_data):
                            st.success(f"❌ {employee_name}의 지출요청서를 거부했습니다.")
                            st.rerun()
                        else:
                            st.error("거부 처리에 실패했습니다.")