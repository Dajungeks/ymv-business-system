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
    tab1, tab2, tab3, tab4 = st.tabs(["📝 지출요청서 작성", "📋 지출요청서 목록", "📊 지출 통계", "👨‍💼 승인 관리"])
    
    with tab1:
        render_expense_form(load_data_func, save_data_func, update_data_func, get_current_user_func)
    
    with tab2:
        render_expense_list(load_data_func, update_data_func, delete_data_func, 
                          get_current_user_func, get_approval_status_info_func, 
                          create_csv_download_func, render_print_form_func)
    
    with tab3:
        render_expense_statistics(load_data_func, calculate_expense_statistics_func)
    
    with tab4:
        render_approval_management(load_data_func, update_data_func, get_current_user_func, 
                                  get_approval_status_info_func)

def render_expense_form(load_data_func, save_data_func, update_data_func, get_current_user_func):
    """지출요청서 작성/수정 폼 (DB 구조 맞춤)"""
    
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
    
    # 수정 모드 확인 (세션 상태에서)
    edit_expense = st.session_state.get('edit_expense', None)
    
    if edit_expense:
        st.info(f"📝 지출요청서 수정 모드 (ID: {edit_expense.get('id')})")
        if st.button("❌ 수정 취소"):
            del st.session_state['edit_expense']
            st.rerun()
    
    # 폼 생성
    with st.form("expense_form", clear_on_submit=not edit_expense):
        col1, col2 = st.columns(2)
        
        with col1:
            # 요청자 선택
            employee_options = {}
            for emp in employees:
                emp_name = emp.get('name', '이름없음')
                emp_id = emp.get('employee_id', f"ID{emp.get('id')}")
                employee_options[f"{emp_name} ({emp_id})"] = emp.get('id')
            
            # 현재 사용자 또는 수정 대상 기본 선택
            if edit_expense:
                requester_id = edit_expense.get('requester')
                requester_emp = next((emp for emp in employees if emp.get('id') == requester_id), None)
                if requester_emp:
                    default_name = f"{requester_emp.get('name', '이름없음')} ({requester_emp.get('employee_id', 'N/A')})"
                    default_index = list(employee_options.keys()).index(default_name) if default_name in employee_options else 0
                else:
                    default_index = 0
            else:
                current_user_name = current_user.get('name', '이름없음')
                current_user_emp_id = current_user.get('employee_id', f"ID{current_user.get('id')}")
                current_user_option = f"{current_user_name} ({current_user_emp_id})"
                default_index = list(employee_options.keys()).index(current_user_option) if current_user_option in employee_options else 0
            
            selected_employee = st.selectbox(
                "요청자",
                options=list(employee_options.keys()),
                index=default_index,
                key="expense_employee"
            )
            requester_id = employee_options[selected_employee]
            
            department = st.text_input(
                "부서", 
                value=edit_expense.get('department', current_user.get('department', '')) if edit_expense else current_user.get('department', ''), 
                key="expense_department"
            )
            
            expense_date = st.date_input(
                "지출일", 
                value=datetime.strptime(edit_expense.get('expense_date'), '%Y-%m-%d').date() if edit_expense and edit_expense.get('expense_date') else date.today(),
                key="expense_date"
            )
            
            # 지출 유형 (expense_type)
            expense_types = ["사무용품", "교통비", "식비", "회의비", "출장비", "접대비", "기타"]
            type_index = expense_types.index(edit_expense.get('expense_type')) if edit_expense and edit_expense.get('expense_type') in expense_types else 0
            
            expense_type = st.selectbox(
                "지출 유형",
                expense_types,
                index=type_index,
                key="expense_type"
            )
        
        with col2:
            # 금액 및 통화
            currency_options = ["VND", "USD", "KRW"]
            currency_index = currency_options.index(edit_expense.get('currency', 'VND')) if edit_expense and edit_expense.get('currency') in currency_options else 0
            
            currency = st.selectbox("통화", currency_options, index=currency_index, key="expense_currency")
            amount = st.number_input(
                f"금액 ({currency})",
                min_value=0,
                value=int(edit_expense.get('amount', 0)) if edit_expense else 0,
                step=1000,
                key="expense_amount"
            )
            
            # 결제 방법
            payment_methods = ["현금", "신용카드", "계좌이체", "법인카드"]
            payment_index = payment_methods.index(edit_expense.get('payment_method')) if edit_expense and edit_expense.get('payment_method') in payment_methods else 0
            
            payment_method = st.selectbox(
                "결제 방법",
                payment_methods,
                index=payment_index,
                key="payment_method"
            )
            
            # 긴급도
            urgency_options = ["보통", "긴급", "매우긴급"]
            urgency_index = urgency_options.index(edit_expense.get('urgency', '보통')) if edit_expense and edit_expense.get('urgency') in urgency_options else 0
            
            urgency = st.selectbox(
                "긴급도",
                urgency_options,
                index=urgency_index,
                key="expense_urgency"
            )
            
            # 공급업체
            vendor = st.text_input(
                "공급업체 (선택사항)", 
                value=edit_expense.get('vendor', '') if edit_expense else '',
                key="expense_vendor"
            )
        
        # 지출 내역
        description = st.text_area(
            "지출 내역", 
            value=edit_expense.get('description', '') if edit_expense else '',
            key="expense_description"
        )
        
        # 사업 목적
        business_purpose = st.text_area(
            "사업 목적 (선택사항)", 
            value=edit_expense.get('business_purpose', '') if edit_expense else '',
            key="expense_business_purpose"
        )
        
        # 영수증 번호
        receipt_number = st.text_input(
            "영수증 번호 (선택사항)", 
            value=edit_expense.get('receipt_number', '') if edit_expense else '',
            key="expense_receipt"
        )
        
        submitted = st.form_submit_button("💾 저장" if edit_expense else "💾 지출요청서 제출")
        
        if submitted:
            if amount <= 0:
                st.error("금액은 0보다 커야 합니다.")
            elif not description.strip():
                st.error("지출 내역을 입력해주세요.")
            else:
                # 지출요청서 데이터 준비
                expense_data = {
                    'requester': requester_id,
                    'department': department,
                    'expense_date': expense_date.strftime('%Y-%m-%d'),
                    'expense_type': expense_type,
                    'amount': amount,
                    'currency': currency,
                    'payment_method': payment_method,
                    'urgency': urgency,
                    'description': description,
                    'business_purpose': business_purpose if business_purpose else None,
                    'vendor': vendor if vendor else None,
                    'receipt_number': receipt_number if receipt_number else None,
                    'status': 'pending',
                    'updated_at': datetime.now().isoformat()
                }
                
                # 수정 또는 신규 등록
                if edit_expense:
                    expense_data['id'] = edit_expense.get('id')
                    if update_data_func("expenses", expense_data, "id"):
                        st.success("✅ 지출요청서가 수정되었습니다!")
                        del st.session_state['edit_expense']
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ 수정에 실패했습니다.")
                else:
                    expense_data['created_at'] = datetime.now().isoformat()
                    if save_data_func("expenses", expense_data):
                        st.success("✅ 지출요청서가 성공적으로 제출되었습니다!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ 지출요청서 제출에 실패했습니다.")

def render_expense_list(load_data_func, update_data_func, delete_data_func, 
                       get_current_user_func, get_approval_status_info_func, 
                       create_csv_download_func, render_print_form_func):
    """지출요청서 목록 관리 (개선된 버전)"""
    
    # 프린트 모드 확인 (최우선)
    if st.session_state.get('print_expense'):
        print_expense = st.session_state['print_expense']
        employees = load_data_func("employees")
        render_print_form_func(print_expense, employees)
        
        if st.button("← 목록으로 돌아가기", type="primary"):
            del st.session_state['print_expense']
            st.rerun()
        return  # 프린트 모드에서는 목록 표시 안 함
    
    # 데이터 로드
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not expenses:
        st.info("등록된 지출요청서가 없습니다.")
        return
    
    # 직원 정보를 딕셔너리로 변환
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
        type_filter = st.selectbox(
            "지출 유형 필터",
            ["전체", "사무용품", "교통비", "식비", "회의비", "출장비", "접대비", "기타"],
            key="expense_type_filter"
        )
    
    with col3:
        # master, admin은 전체 조회 가능
        if user_role in ['Master', 'CEO', 'Admin']:
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
    
    # 데이터 필터링
    filtered_expenses = []
    for expense in expenses:
        # 상태 필터링
        if status_filter != "전체":
            status_map = {"대기": "pending", "승인": "approved", "거부": "rejected"}
            expense_status = expense.get('status', 'pending')
            if expense_status != status_map[status_filter]:
                continue
        
        # 지출 유형 필터링
        if type_filter != "전체" and expense.get('expense_type') != type_filter:
            continue
        
        # 직원 필터링
        if user_role not in ['master', 'admin']:
            if expense.get('requester') != current_user_id:
                continue
        elif employee_filter != "전체":
            employee_name = employee_filter.split(" (")[0]
            expense_requester_id = expense.get('requester')
            if expense_requester_id:
                emp_info = employee_dict.get(expense_requester_id, {})
                if emp_info.get('name') != employee_name:
                    continue
        
        filtered_expenses.append(expense)
    
    # 정렬
    if sort_order == "최신순":
        filtered_expenses.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_order == "오래된순":
        filtered_expenses.sort(key=lambda x: x.get('created_at', ''))
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
    
    # 지출요청서 목록 표시
    for idx, expense in enumerate(filtered_expenses):
        # 직원 정보
        requester_id = expense.get('requester')
        employee_info = employee_dict.get(requester_id, {})
        employee_name = employee_info.get('name', '알 수 없음')
        employee_id = employee_info.get('employee_id', f"ID{requester_id}")
        
        # 요청일
        request_date = 'N/A'
        if expense.get('created_at'):
            try:
                dt = datetime.fromisoformat(str(expense['created_at']).replace('Z', '+00:00'))
                request_date = dt.strftime('%Y-%m-%d')
            except:
                request_date = str(expense['created_at'])[:10]
        
        # 상태 정보
        expense_status = expense.get('status', 'pending')
        status_info = get_approval_status_info_func(expense_status)
        status_emoji = status_info.get('emoji', '❓')
        
        # 지출요청서 카드
        expense_type = expense.get('expense_type', '기타')
        amount = expense.get('amount', 0)
        currency = expense.get('currency', 'VND')
        
        with st.expander(
            f"{status_emoji} [{request_date}] {employee_name} - {expense_type} ({amount:,} {currency})",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**기본 정보**")
                st.write(f"• 요청자: {employee_name} ({employee_id})")
                st.write(f"• 부서: {expense.get('department', 'N/A')}")
                st.write(f"• 지출일: {expense.get('expense_date', 'N/A')}")
                st.write(f"• 지출 유형: {expense_type}")
                st.write(f"• 금액: {amount:,} {currency}")
                st.write(f"• 결제 방법: {expense.get('payment_method', 'N/A')}")
                st.write(f"• 긴급도: {expense.get('urgency', '보통')}")
                st.write(f"• 공급업체: {expense.get('vendor', 'N/A')}")
                st.write(f"• 영수증 번호: {expense.get('receipt_number', 'N/A')}")
                
                st.write("**지출 내역**")
                st.write(expense.get('description', '내용없음'))
                
                if expense.get('business_purpose'):
                    st.write("**사업 목적**")
                    st.write(expense.get('business_purpose'))
                
                # 승인 정보
                if expense_status in ['approved', 'rejected']:
                    st.write("**승인 정보**")
                    st.write(f"• 처리일: {expense.get('approved_at', 'N/A')}")
                    if expense.get('approved_by'):
                        approver = employee_dict.get(expense['approved_by'], {})
                        approver_name = approver.get('name', '알 수 없음')
                        st.write(f"• 처리자: {approver_name}")
                    if expense.get('approval_comment'):
                        if expense_status == 'rejected':
                            st.error(f"**반려 사유**: {expense.get('approval_comment')}")
                        else:
                            st.write(f"• 처리 의견: {expense.get('approval_comment')}")
            
            with col2:
                status_description = status_info.get('description', '알 수 없음')
                st.write(f"**상태**: {status_emoji} {status_description}")
                
                # 액션 버튼들
                button_col1, button_col2 = st.columns(2)
                
                with button_col1:
                    # 프린트 버튼 - 세션 상태에 저장
                    if st.button("🖨️ 프린트", key=f"print_{expense.get('id', idx)}"):
                        st.session_state['print_expense'] = expense
                        st.rerun()
                
                with button_col2:
                    # Master는 모든 항목 삭제 가능
                    if user_role == 'Master':
                        if st.button("🗑️ 삭제", key=f"delete_{expense.get('id', idx)}"):
                            if delete_data_func("expenses", expense.get('id'), "id"):
                                st.success("지출요청서가 삭제되었습니다.")
                                st.rerun()
                            else:
                                st.error("삭제에 실패했습니다.")
                    # Admin은 본인이 작성한 pending 항목만 삭제 가능
                    elif user_role == 'Admin' and expense.get('requester') == current_user_id and expense_status == 'pending':
                        if st.button("🗑️ 삭제", key=f"delete_{expense.get('id', idx)}"):
                            if delete_data_func("expenses", expense.get('id'), "id"):
                                st.success("지출요청서가 삭제되었습니다.")
                                st.rerun()
                            else:
                                st.error("삭제에 실패했습니다.")
                
                # 수정 버튼 (Master는 모든 항목, Admin은 본인의 rejected 항목만)
                can_edit = False
                if user_role == 'Master':
                    can_edit = True
                elif user_role == 'Admin' and expense.get('requester') == current_user_id and expense_status == 'rejected':
                    can_edit = True
                                
                if can_edit:
                    if st.button("✏️ 수정", key=f"edit_{expense.get('id', idx)}", type="primary"):
                        st.session_state['edit_expense'] = expense
                        st.rerun()
                
                # 재신청 버튼 (rejected 상태이고 본인이 작성한 경우)
                if expense_status == 'rejected' and expense.get('requester') == current_user_id:
                    if st.button("🔄 재신청", key=f"resubmit_{expense.get('id', idx)}"):
                        resubmit_data = {
                            'id': expense.get('id'),
                            'status': 'pending',
                            'approval_comment': None,
                            'approved_by': None,
                            'approved_at': None,
                            'updated_at': datetime.now().isoformat()
                        }
                        if update_data_func("expenses", resubmit_data, "id"):
                            st.success("재신청되었습니다!")
                            st.rerun()
                        else:
                            st.error("재신청에 실패했습니다.")

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
        # 카테고리별 통계 (expense_type)
        category_stats = stats.get('category_stats', {})
        if category_stats:
            st.write("**지출 유형별 통계**")
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

def render_approval_management(load_data_func, update_data_func, get_current_user_func, 
                              get_approval_status_info_func):
    """승인 관리 (CEO/Master 전용)"""
    
    current_user = get_current_user_func()
    # Master와 CEO만 승인 가능
    if not current_user or current_user.get('role') not in ['Master', 'CEO']:
        st.warning("⚠️ 승인 권한이 없습니다.")
        return
    
    # 승인 대기중인 지출요청서 로드
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not expenses:
        st.info("승인할 지출요청서가 없습니다.")
        return
    
    # 직원 정보를 딕셔너리로 변환
    employee_dict = {}
    if employees:
        for emp in employees:
            emp_id = emp.get('id')
            if emp_id:
                employee_dict[emp_id] = emp
    
    # 대기중인 요청서만 필터링
    pending_expenses = [exp for exp in expenses if exp.get('status') == 'pending']
    
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
        pending_expenses.sort(key=lambda x: x.get('created_at', ''))
    elif sort_option == "금액높은순":
        pending_expenses.sort(key=lambda x: x.get('amount', 0), reverse=True)
    elif sort_option == "금액낮은순":
        pending_expenses.sort(key=lambda x: x.get('amount', 0))
    
    # 승인 대기 목록
    for expense in pending_expenses:
        # 직원 정보
        requester_id = expense.get('requester')
        employee_info = employee_dict.get(requester_id, {})
        employee_name = employee_info.get('name', '알 수 없음')
        employee_id = employee_info.get('employee_id', f"ID{requester_id}")
        
        # 요청일 추출
        request_date = 'N/A'
        if expense.get('created_at'):
            try:
                dt = datetime.fromisoformat(str(expense['created_at']).replace('Z', '+00:00'))
                request_date = dt.strftime('%Y-%m-%d')
            except:
                request_date = str(expense['created_at'])[:10]
        
        expense_type = expense.get('expense_type', '기타')
        amount = expense.get('amount', 0)
        currency = expense.get('currency', 'VND')
        
        with st.expander(
            f"💰 [{request_date}] {employee_name} - {expense_type} ({amount:,} {currency})",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**요청 정보**")
                st.write(f"• 요청자: {employee_name} ({employee_id})")
                st.write(f"• 부서: {expense.get('department', 'N/A')}")
                st.write(f"• 요청일: {request_date}")
                st.write(f"• 지출일: {expense.get('expense_date', 'N/A')}")
                st.write(f"• 지출 유형: {expense_type}")
                st.write(f"• 금액: {amount:,} {currency}")
                st.write(f"• 결제 방법: {expense.get('payment_method', 'N/A')}")
                st.write(f"• 긴급도: {expense.get('urgency', '보통')}")
                st.write(f"• 공급업체: {expense.get('vendor', 'N/A')}")
                st.write(f"• 영수증 번호: {expense.get('receipt_number', 'N/A')}")
                
                st.write("**지출 내역**")
                st.write(expense.get('description', '내용없음'))
                
                if expense.get('business_purpose'):
                    st.write("**사업 목적**")
                    st.write(expense.get('business_purpose'))
            
            with col2:
                st.write("**승인 처리**")
                
                # 승인 의견
                approval_comment = st.text_area(
                    "처리 의견 (선택사항)",
                    key=f"comment_{expense.get('id')}",
                    height=80,
                    help="승인 시: 선택사항, 반려 시: 필수 입력"
                )
                
                # 승인/거부 버튼
                button_col1, button_col2 = st.columns(2)
                
                with button_col1:
                    if st.button("✅ 승인", key=f"approve_{expense.get('id')}", type="primary"):
                        # 승인 처리
                        update_data = {
                            'id': expense.get('id'),
                            'status': 'approved',
                            'approved_by': current_user.get('id'),
                            'approved_at': datetime.now().isoformat(),
                            'approval_comment': approval_comment if approval_comment else None,
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        if update_data_func("expenses", update_data, "id"):
                            st.success(f"✅ {employee_name}의 지출요청서를 승인했습니다.")
                            st.rerun()
                        else:
                            st.error("승인 처리에 실패했습니다.")
                
                with button_col2:
                    if st.button("❌ 반려", key=f"reject_{expense.get('id')}"):
                        # 반려 시 사유 필수 체크
                        if not approval_comment or not approval_comment.strip():
                            st.error("⚠️ 반려 사유를 반드시 입력해주세요!")
                        else:
                            # 거부 처리
                            update_data = {
                                'id': expense.get('id'),
                                'status': 'rejected',
                                'approved_by': current_user.get('id'),
                                'approved_at': datetime.now().isoformat(),
                                'approval_comment': approval_comment,
                                'updated_at': datetime.now().isoformat()
                            }
                            
                            if update_data_func("expenses", update_data, "id"):
                                st.success(f"❌ {employee_name}의 지출요청서를 반려했습니다.")
                                st.rerun()
                            else:
                                st.error("반려 처리에 실패했습니다.")