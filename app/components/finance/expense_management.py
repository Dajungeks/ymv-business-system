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
    
    # 현재 사용자 권한 확인
    current_user = get_current_user_func()
    user_role = current_user.get('role', 'Staff') if current_user else 'Staff'
    
    # 대기 건수 계산
    expenses = load_data_func("expenses")
    pending_approval_count = 0
    pending_invoice_count = 0
    
    if expenses:
        pending_approval_count = len([exp for exp in expenses if exp.get('status') == 'pending'])
        pending_invoice_count = len([exp for exp in expenses 
                                     if exp.get('status') == 'approved' and not exp.get('accounting_confirmed', False)])
    
    # 탭 구성 - Admin/CEO/Master는 화폐 발행 확인 탭 추가
    if user_role in ['Admin', 'CEO', 'Master']:
        approval_tab_name = f"👨‍💼 승인 관리 ({pending_approval_count})" if pending_approval_count > 0 else "👨‍💼 승인 관리"
        invoice_tab_name = f"🧾 화폐 확인 대기 항목 ({pending_invoice_count})" if pending_invoice_count > 0 else "🧾 화폐 발행 확인"
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📝 지출요청서 작성", 
            "📋 지출요청서 목록", 
            "📊 지출 통계", 
            approval_tab_name,
            invoice_tab_name
        ])
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 지출요청서 작성", 
            "📋 지출요청서 목록", 
            "📊 지출 통계", 
            "👨‍💼 승인 관리"
        ])
    
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
    
    # 화폐 발행 확인 탭 (권한 있는 사용자만)
    if user_role in ['Admin', 'CEO', 'Master']:
        with tab5:
            render_invoice_check_tab(load_data_func, update_data_func, get_current_user_func)


def generate_document_number(load_data_func):
    """문서번호 자동 생성: EXP-YYMMDD-Count"""
    today = date.today()
    date_str = today.strftime('%y%m%d')
    
    all_expenses = load_data_func("expenses")
    if all_expenses:
        today_expenses = [exp for exp in all_expenses 
                         if exp.get('document_number', '').startswith(f"EXP-{date_str}")]
        count = len(today_expenses) + 1
    else:
        count = 1
    
    return f"EXP-{date_str}-{count:03d}"


def render_expense_form(load_data_func, save_data_func, update_data_func, get_current_user_func):
    """지출요청서 작성/수정 폼"""
    
    employees = load_data_func("employees")
    if not employees:
        st.error("직원 정보를 불러올 수 없습니다.")
        return
    
    current_user = get_current_user_func()
    if not current_user:
        st.error("로그인 정보를 확인할 수 없습니다.")
        return
    
    edit_expense = st.session_state.get('edit_expense', None)
    
    if edit_expense:
        st.info(f"📝 지출요청서 수정 모드 (문서번호: {edit_expense.get('document_number', 'N/A')})")
        if st.button("❌ 수정 취소"):
            del st.session_state['edit_expense']
            st.rerun()
    
    with st.form("expense_form", clear_on_submit=not edit_expense):
        col1, col2 = st.columns(2)
        
        with col1:
            employee_options = {}
            for emp in employees:
                emp_name = emp.get('name', '이름없음')
                emp_id = emp.get('employee_id', f"ID{emp.get('id')}")
                employee_options[f"{emp_name} ({emp_id})"] = emp.get('id')
            
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
            
            expense_types = ["사무용품", "교통비", "식비", "회의비", "출장비", "접대비", "기타"]
            type_index = expense_types.index(edit_expense.get('expense_type')) if edit_expense and edit_expense.get('expense_type') in expense_types else 0
            
            expense_type = st.selectbox(
                "지출 유형",
                expense_types,
                index=type_index,
                key="expense_type"
            )
        
        with col2:
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
            
            payment_methods = ["현금", "신용카드", "계좌이체", "법인카드"]
            payment_index = payment_methods.index(edit_expense.get('payment_method')) if edit_expense and edit_expense.get('payment_method') in payment_methods else 0
            
            payment_method = st.selectbox(
                "결제 방법",
                payment_methods,
                index=payment_index,
                key="payment_method"
            )
            
            urgency_options = ["보통", "긴급", "매우긴급"]
            urgency_index = urgency_options.index(edit_expense.get('urgency', '보통')) if edit_expense and edit_expense.get('urgency') in urgency_options else 0
            
            urgency = st.selectbox(
                "긴급도",
                urgency_options,
                index=urgency_index,
                key="expense_urgency"
            )
            
            vendor = st.text_input(
                "공급업체 (선택사항)", 
                value=edit_expense.get('vendor', '') if edit_expense else '',
                key="expense_vendor"
            )
        
        description = st.text_area(
            "지출 내역", 
            value=edit_expense.get('description', '') if edit_expense else '',
            key="expense_description"
        )
        
        business_purpose = st.text_area(
            "사업 목적 (선택사항)", 
            value=edit_expense.get('business_purpose', '') if edit_expense else '',
            key="expense_business_purpose"
        )
        
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
                
                if edit_expense:
                    expense_data['id'] = edit_expense.get('id')
                    if update_data_func("expenses", expense_data, "id"):
                        st.success("✅ 지출요청서가 수정되었습니다!")
                        del st.session_state['edit_expense']
                        st.rerun()
                    else:
                        st.error("❌ 수정에 실패했습니다.")
                else:
                    expense_data['document_number'] = generate_document_number(load_data_func)
                    expense_data['created_at'] = datetime.now().isoformat()
                    
                    if save_data_func("expenses", expense_data):
                        st.success(f"✅ 지출요청서가 성공적으로 제출되었습니다! (문서번호: {expense_data['document_number']})")
                        st.rerun()
                    else:
                        st.error("❌ 지출요청서 제출에 실패했습니다.")


def render_expense_list(load_data_func, update_data_func, delete_data_func, 
                       get_current_user_func, get_approval_status_info_func, 
                       create_csv_download_func, render_print_form_func):
    """지출요청서 목록 관리 - 제품 목록과 동일한 스타일"""
    
    # 프린트 모드
    if st.session_state.get('print_expense'):
        print_expense = st.session_state['print_expense']
        employees = load_data_func("employees")
        render_print_form_func(print_expense, employees)
        
        if st.button("← 목록으로 돌아가기", type="primary"):
            del st.session_state['print_expense']
            st.rerun()
        return
    
    # 데이터 로드
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not expenses:
        st.info("등록된 지출요청서가 없습니다.")
        return
    
    # 직원 딕셔너리 생성
    employee_dict = {}
    if employees:
        for emp in employees:
            emp_id = emp.get('id')
            if emp_id:
                employee_dict[emp_id] = emp
    
    # 현재 사용자 정보
    current_user = get_current_user_func()
    user_role = current_user.get('role', 'Staff') if current_user else 'Staff'
    current_user_id = current_user.get('id') if current_user else None
    
    # 검색 필터 렌더링
    render_search_filters_expense(expenses, employees, user_role)
    
    # 필터링된 지출요청서 가져오기
    filtered_expenses = get_filtered_expenses(expenses, user_role, current_user_id, employee_dict)
    
    # 테이블 렌더링
    render_expense_table_view(filtered_expenses, employee_dict, get_approval_status_info_func)
    
    st.markdown("---")
    
    # ID 선택 영역
    render_id_selection_expense(filtered_expenses, employee_dict, current_user, user_role,
                                update_data_func, delete_data_func, 
                                get_approval_status_info_func, render_print_form_func,
                                load_data_func)


def render_search_filters_expense(expenses, employees, user_role):
    """검색 필터 영역"""
    
    st.markdown("### 🔍 지출요청서 검색")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.text_input(
            "🔍 검색",
            placeholder="문서번호/내역",
            key="expense_search_term"
        )
    
    with col2:
        st.selectbox(
            "상태",
            ["전체", "대기", "승인", "반려", "화폐확인완료"],
            key="expense_status_filter"
        )
    
    with col3:
        st.selectbox(
            "지출 유형",
            ["전체", "사무용품", "교통비", "식비", "회의비", "출장비", "접대비", "기타"],
            key="expense_type_filter"
        )
    
    with col4:
        st.selectbox(
            "결제 방법",
            ["전체", "법인카드", "현금", "신용카드", "계좌이체"],
            key="expense_payment_filter"
        )
    
    with col5:
        if user_role in ['Master', 'CEO', 'Admin']:
            employee_options = ["전체"]
            for emp in employees:
                emp_name = emp.get('name', '이름없음')
                emp_id = emp.get('employee_id', f"ID{emp.get('id')}")
                employee_options.append(f"{emp_name} ({emp_id})")
            
            st.selectbox(
                "직원",
                employee_options,
                key="expense_employee_filter"
            )
        else:
            st.selectbox("직원", ["본인만"], disabled=True, key="expense_employee_filter_disabled")
    
    # 기간 필터 및 정렬
    col_date1, col_date2, col_sort = st.columns(3)
    
    with col_date1:
        st.date_input("시작일", value=None, key="expense_date_from")
    
    with col_date2:
        st.date_input("종료일", value=None, key="expense_date_to")
    
    with col_sort:
        st.selectbox(
            "정렬",
            ["최신순", "오래된순", "금액높은순", "금액낮은순"],
            key="expense_sort_order"
        )
    
    st.markdown("---")


def get_filtered_expenses(expenses, user_role, current_user_id, employee_dict):
    """필터 적용"""
    
    filtered = expenses.copy()
    
    # 텍스트 검색
    search_term = st.session_state.get('expense_search_term', '')
    if search_term:
        filtered = [
            exp for exp in filtered
            if search_term.lower() in str(exp.get('document_number', '')).lower()
            or search_term.lower() in str(exp.get('description', '')).lower()
        ]
    
    # 상태 필터
    status_filter = st.session_state.get('expense_status_filter', '전체')
    if status_filter != '전체':
        if status_filter == '화폐확인완료':
            filtered = [exp for exp in filtered if exp.get('accounting_confirmed', False)]
        else:
            status_map = {"대기": "pending", "승인": "approved", "반려": "rejected"}
            filtered = [exp for exp in filtered if exp.get('status') == status_map.get(status_filter)]
    
    # 지출 유형 필터
    type_filter = st.session_state.get('expense_type_filter', '전체')
    if type_filter != '전체':
        filtered = [exp for exp in filtered if exp.get('expense_type') == type_filter]
    
    # 결제 방법 필터
    payment_filter = st.session_state.get('expense_payment_filter', '전체')
    if payment_filter != '전체':
        filtered = [exp for exp in filtered if exp.get('payment_method') == payment_filter]
    
    # 직원 필터
    if user_role not in ['Master', 'CEO', 'Admin']:
        filtered = [exp for exp in filtered if exp.get('requester') == current_user_id]
    else:
        employee_filter = st.session_state.get('expense_employee_filter', '전체')
        if employee_filter != '전체':
            employee_name = employee_filter.split(" (")[0]
            filtered = [
                exp for exp in filtered
                if employee_dict.get(exp.get('requester'), {}).get('name') == employee_name
            ]
    
    # 기간 필터
    date_from = st.session_state.get('expense_date_from')
    date_to = st.session_state.get('expense_date_to')
    
    if date_from:
        filtered = [exp for exp in filtered if exp.get('expense_date', '') >= date_from.strftime('%Y-%m-%d')]
    
    if date_to:
        filtered = [exp for exp in filtered if exp.get('expense_date', '') <= date_to.strftime('%Y-%m-%d')]
    
    # 정렬
    sort_order = st.session_state.get('expense_sort_order', '최신순')
    if sort_order == '최신순':
        filtered.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_order == '오래된순':
        filtered.sort(key=lambda x: x.get('created_at', ''))
    elif sort_order == '금액높은순':
        filtered.sort(key=lambda x: x.get('amount', 0), reverse=True)
    elif sort_order == '금액낮은순':
        filtered.sort(key=lambda x: x.get('amount', 0))
    
    return filtered


def render_expense_table_view(filtered_expenses, employee_dict, get_approval_status_info_func):
    """지출요청서 테이블 뷰"""
    
    if not filtered_expenses:
        st.info("조건에 맞는 지출요청서가 없습니다.")
        return
    
    # 테이블 데이터 생성
    table_data = []
    for exp in filtered_expenses:
        # 요청자 이름
        requester_id = exp.get('requester')
        requester_info = employee_dict.get(requester_id, {})
        requester_name = requester_info.get('name', '알 수 없음')
        
        # 상태 아이콘
        expense_status = exp.get('status', 'pending')
        status_info = get_approval_status_info_func(expense_status)
        status_display = f"{status_info.get('emoji', '❓')} {status_info.get('description', '알 수 없음')}"
        
        # 화폐 상태
        accounting_confirmed = exp.get('accounting_confirmed', False)
        if accounting_confirmed:
            invoice_display = "✅"
        elif expense_status == 'approved':
            invoice_display = "⏳"
        else:
            invoice_display = "—"
        
        table_data.append({
            'ID': exp.get('id', ''),
            '문서번호': exp.get('document_number', 'N/A'),
            '요청자': requester_name,
            '지출일': exp.get('expense_date', 'N/A'),
            '유형': exp.get('expense_type', 'N/A'),
            '금액': f"{exp.get('amount', 0):,}",
            '통화': exp.get('currency', 'VND'),
            '상태': status_display,
            '화폐': invoice_display,
            'Active': '✅'
        })
    
    df = pd.DataFrame(table_data)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"📊 총 **{len(filtered_expenses)}건** 지출요청서")


def render_id_selection_expense(filtered_expenses, employee_dict, current_user, user_role,
                               update_data_func, delete_data_func, 
                               get_approval_status_info_func, render_print_form_func,
                               load_data_func):
    """ID 선택 영역"""
    
    st.markdown("### 📋 ID 선택 (다중 선택 가능)")
    
    # 세션 상태 초기화
    if 'selected_expense_ids' not in st.session_state:
        st.session_state.selected_expense_ids = []
    
    if not filtered_expenses:
        return
    
    # 전체 선택/해제
    col_all, _ = st.columns([1, 5])
    with col_all:
        # 현재 전체 선택 상태 확인
        all_ids = [exp.get('id') for exp in filtered_expenses]
        is_all_selected = len(st.session_state.selected_expense_ids) == len(all_ids) and \
                         all(exp_id in st.session_state.selected_expense_ids for exp_id in all_ids)
        
        select_all = st.checkbox("전체 선택", value=is_all_selected, key="select_all_expenses")
    
    # 전체 선택/해제 토글
    if select_all and not is_all_selected:
        # 전체 선택
        st.session_state.selected_expense_ids = [exp.get('id') for exp in filtered_expenses]
        st.rerun()
    elif not select_all and is_all_selected:
        # 전체 해제
        st.session_state.selected_expense_ids = []
        st.rerun()
    
    # ID 체크박스 (한 줄에 10개씩)
    ids_per_row = 10
    
    for i in range(0, len(filtered_expenses), ids_per_row):
        cols = st.columns(ids_per_row)
        for j in range(ids_per_row):
            idx = i + j
            if idx < len(filtered_expenses):
                exp = filtered_expenses[idx]
                exp_id = exp.get('id')
                with cols[j]:
                    is_checked = st.checkbox(
                        str(exp_id),
                        value=exp_id in st.session_state.selected_expense_ids,
                        key=f"check_expense_{exp_id}"
                    )
                    
                    if is_checked and exp_id not in st.session_state.selected_expense_ids:
                        st.session_state.selected_expense_ids.append(exp_id)
                    elif not is_checked and exp_id in st.session_state.selected_expense_ids:
                        st.session_state.selected_expense_ids.remove(exp_id)
    
    st.markdown("---")
    
    # 선택된 항목 액션
    selected_count = len(st.session_state.selected_expense_ids)
    
    if selected_count > 0:
        selected_ids_text = ", ".join([str(id) for id in sorted(st.session_state.selected_expense_ids)])
        st.success(f"✅ {selected_count}건 선택됨 (ID: {selected_ids_text})")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📄 상세보기", type="primary", use_container_width=True):
                st.session_state.show_expense_details = True
                st.rerun()
        
        with col2:
            if st.button("🖨️ 프린트", use_container_width=True):
                if selected_count == 1:
                    expenses = [exp for exp in filtered_expenses if exp.get('id') in st.session_state.selected_expense_ids]
                    if expenses:
                        st.session_state['print_expense'] = expenses[0]
                        st.rerun()
                else:
                    st.error("프린트는 1건만 선택해주세요.")
        
        with col3:
            if st.button("✏️ 수정", use_container_width=True):
                if selected_count == 1:
                    expense_id = st.session_state.selected_expense_ids[0]
                    expense = next((exp for exp in filtered_expenses if exp.get('id') == expense_id), None)
                    
                    if expense:
                        # 수정 권한 확인
                        can_edit = False
                        expense_status = expense.get('status')
                        
                        if user_role == 'Master':
                            can_edit = True
                        elif expense_status == 'rejected' and expense.get('requester') == current_user.get('id'):
                            can_edit = True
                        elif user_role in ['Admin', 'CEO'] and expense_status == 'pending':
                            can_edit = True
                        
                        if can_edit:
                            st.session_state['edit_expense'] = expense
                            st.rerun()
                        else:
                            st.error("이 지출요청서는 수정할 권한이 없습니다.")
                else:
                    st.error("수정은 1건만 선택해주세요.")
        
        with col4:
            if st.button("🗑️ 삭제", use_container_width=True):
                st.session_state.show_delete_confirm = True
                st.rerun()
    
    # 상세보기 표시
    if st.session_state.get('show_expense_details'):
        render_expense_details_modal(filtered_expenses, employee_dict, 
                                     get_approval_status_info_func, update_data_func, 
                                     current_user, load_data_func)
    
    # 삭제 확인 모달
    if st.session_state.get('show_delete_confirm'):
        render_delete_confirmation(filtered_expenses, current_user, user_role, delete_data_func)


def render_expense_details_modal(filtered_expenses, employee_dict, get_approval_status_info_func,
                                 update_data_func, current_user, load_data_func):
    """선택된 지출요청서 상세 정보"""
    
    st.markdown("---")
    st.markdown("## 📄 선택된 지출요청서 상세")
    
    selected_expenses = [exp for exp in filtered_expenses 
                        if exp.get('id') in st.session_state.selected_expense_ids]
    
    for expense in selected_expenses:
        document_number = expense.get('document_number', 'N/A')
        description = expense.get('description', '')
        
        with st.expander(f"📄 {document_number} - {description[:30]}...", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**기본 정보**")
                st.write(f"• 문서번호: {expense.get('document_number', 'N/A')}")
                
                requester_id = expense.get('requester')
                requester_info = employee_dict.get(requester_id, {})
                requester_name = requester_info.get('name', '알 수 없음')
                st.write(f"• 요청자: {requester_name}")
                
                st.write(f"• 부서: {expense.get('department', 'N/A')}")
                st.write(f"• 지출일: {expense.get('expense_date', 'N/A')}")
            
            with col2:
                st.markdown("**금액 정보**")
                amount = expense.get('amount', 0)
                currency = expense.get('currency', 'VND')
                st.write(f"• 금액: {amount:,} {currency}")
                st.write(f"• 유형: {expense.get('expense_type', 'N/A')}")
                st.write(f"• 결제방법: {expense.get('payment_method', 'N/A')}")
                st.write(f"• 공급업체: {expense.get('vendor', 'N/A')}")
            
            with col3:
                st.markdown("**상태 정보**")
                expense_status = expense.get('status', 'pending')
                status_info = get_approval_status_info_func(expense_status)
                st.write(f"• 상태: {status_info.get('emoji')} {status_info.get('description')}")
                
                accounting_confirmed = expense.get('accounting_confirmed', False)
                invoice_text = "✅ 완료" if accounting_confirmed else ("⏳ 대기" if expense_status == 'approved' else "— 해당없음")
                st.write(f"• 화폐확인: {invoice_text}")
                
                if expense.get('approved_by'):
                    approver_info = employee_dict.get(expense['approved_by'], {})
                    approver_name = approver_info.get('name', '알 수 없음')
                    st.write(f"• 승인자: {approver_name}")
            
            st.markdown("---")
            st.markdown("**지출 내역**")
            st.write(expense.get('description', '내용없음'))
            
            if expense.get('business_purpose'):
                st.markdown("**사업 목적**")
                st.write(expense.get('business_purpose'))
            
            if expense.get('approval_comment'):
                st.markdown("**처리 의견**")
                if expense_status == 'rejected':
                    st.error(f"**반려 사유:** {expense.get('approval_comment')}")
                else:
                    st.info(expense.get('approval_comment'))
            
            # 화폐 확인 버튼 (권한 확인)
            if (expense_status == 'approved' and 
                not accounting_confirmed and 
                current_user.get('role') in ['Admin', 'CEO', 'Master']):
                
                st.markdown("---")
                if st.button("🧾 화폐 확인 처리", key=f"invoice_btn_{expense.get('id')}", use_container_width=True):
                    if confirm_invoice_expense(expense.get('id'), current_user.get('id'), 
                                              update_data_func, load_data_func):
                        st.success("✅ 화폐 발행 확인 완료!")
                        st.rerun()
                    else:
                        st.error("❌ 화폐 확인 처리 실패")
    
    if st.button("❌ 닫기", use_container_width=True):
        st.session_state.show_expense_details = False
        st.rerun()


def render_delete_confirmation(filtered_expenses, current_user, user_role, delete_data_func):
    """삭제 확인 모달"""
    
    st.markdown("---")
    st.warning(f"⚠️ {len(st.session_state.selected_expense_ids)}건의 지출요청서를 삭제하시겠습니까?")
    
    # 삭제 권한 확인
    can_delete_all = True
    cannot_delete_ids = []
    
    for exp_id in st.session_state.selected_expense_ids:
        expense = next((exp for exp in filtered_expenses if exp.get('id') == exp_id), None)
        if expense:
            can_delete = False
            expense_status = expense.get('status')
            
            if user_role == 'Master':
                can_delete = True
            elif user_role == 'Admin' and expense.get('requester') == current_user.get('id') and expense_status == 'pending':
                can_delete = True
            elif expense_status == 'rejected' and expense.get('requester') == current_user.get('id'):
                can_delete = True
            
            if not can_delete:
                can_delete_all = False
                cannot_delete_ids.append(exp_id)
    
    if not can_delete_all:
        st.error(f"❌ 삭제 권한이 없는 항목: {', '.join(map(str, cannot_delete_ids))}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ 예", key="confirm_delete_expenses", use_container_width=True):
            if can_delete_all:
                success_count = 0
                for exp_id in st.session_state.selected_expense_ids:
                    if delete_data_func('expenses', exp_id, 'id'):
                        success_count += 1
                
                if success_count > 0:
                    st.success(f"✅ {success_count}건 삭제 완료!")
                    st.session_state.selected_expense_ids = []
                    st.session_state.show_delete_confirm = False
                    st.rerun()
                else:
                    st.error("❌ 삭제 실패")
    
    with col2:
        if st.button("❌ 아니오", key="cancel_delete_expenses", use_container_width=True):
            st.session_state.show_delete_confirm = False
            st.rerun()


def confirm_invoice_expense(expense_id, user_id, update_data_func, load_data_func):
    """화폐 발행 확인 처리 (환급 상태 자동 설정)"""
    try:
        all_expenses = load_data_func("expenses")
        expense = next((exp for exp in all_expenses if exp.get('id') == expense_id), None)
        
        if not expense:
            st.error("지출요청서를 찾을 수 없습니다.")
            return False
        
        payment_method = expense.get('payment_method', '')
        if payment_method == '법인카드':
            reimbursement_status = 'not_required'
        else:
            reimbursement_status = 'pending'
        
        update_data = {
            'id': expense_id,
            'accounting_confirmed': True,
            'accounting_confirmed_by': user_id,
            'accounting_confirmed_at': datetime.now().isoformat(),
            'reimbursement_status': reimbursement_status,
            'reimbursement_amount': expense.get('amount') if reimbursement_status == 'pending' else None,
            'updated_at': datetime.now().isoformat()
        }
        
        return update_data_func("expenses", update_data, "id")
    except Exception as e:
        st.error(f"화폐 발행 확인 처리 중 오류: {str(e)}")
        return False


def render_invoice_check_tab(load_data_func, update_data_func, get_current_user_func):
    """화폐 발행 확인 탭 (리스트만 표시)"""
    
    st.subheader("🧾 화폐 발행 확인 대기 목록 (Hóa đơn)")
    st.caption("💡 실제 화폐 확인 처리는 '지출요청서 목록' 탭에서 진행하세요.")
    
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not expenses or not employees:
        st.info("데이터를 불러올 수 없습니다.")
        return
    
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
    # 화폐 확인 대기 중인 항목 필터링
    pending_expenses = [exp for exp in expenses 
                       if exp.get('status') == 'approved' and not exp.get('accounting_confirmed', False)]
    
    if not pending_expenses:
        st.info("화폐 발행 확인 대기 중인 지출요청서가 없습니다.")
        return
    
    # 필터 및 정렬 옵션
    col1, col2 = st.columns(2)
    
    with col1:
        sort_option = st.selectbox(
            "정렬",
            ["최신순", "오래된순", "금액높은순", "금액낮은순"],
            key="invoice_sort"
        )
    
    with col2:
        employee_filter_options = ["전체"]
        requester_ids = list(set([exp.get('requester') for exp in pending_expenses]))
        for req_id in requester_ids:
            emp_info = employee_dict.get(req_id, {})
            emp_name = emp_info.get('name', '알 수 없음')
            emp_id = emp_info.get('employee_id', f'ID{req_id}')
            employee_filter_options.append(f"{emp_name} ({emp_id})")
        
        employee_filter = st.selectbox("직원 필터", employee_filter_options, key="invoice_employee_filter")
    
    # 직원 필터링
    if employee_filter != "전체":
        employee_name = employee_filter.split(" (")[0]
        filtered_expenses = [exp for exp in pending_expenses 
                           if employee_dict.get(exp.get('requester'), {}).get('name') == employee_name]
    else:
        filtered_expenses = pending_expenses
    
    # 정렬
    if sort_option == "최신순":
        filtered_expenses.sort(key=lambda x: x.get('approved_at', ''), reverse=True)
    elif sort_option == "오래된순":
        filtered_expenses.sort(key=lambda x: x.get('approved_at', ''))
    elif sort_option == "금액높은순":
        filtered_expenses.sort(key=lambda x: x.get('amount', 0), reverse=True)
    elif sort_option == "금액낮은순":
        filtered_expenses.sort(key=lambda x: x.get('amount', 0))
    
    st.write(f"⏳ 화폐 발행 확인 대기 중: {len(filtered_expenses)}건")
    
    # 통계 정보
    if filtered_expenses:
        currency_totals = defaultdict(float)
        for exp in filtered_expenses:
            currency = exp.get('currency', 'VND')
            amount = exp.get('amount', 0)
            currency_totals[currency] += amount
        
        st.info(f"📊 총 금액: " + ", ".join([f"{amount:,.0f} {curr}" for curr, amount in currency_totals.items()]))
    
    st.markdown("---")
    
    # 직원별 그룹핑
    grouped_by_employee = defaultdict(list)
    for exp in filtered_expenses:
        requester_id = exp.get('requester')
        grouped_by_employee[requester_id].append(exp)
    
    # 직원별로 표시
    for requester_id, expenses_list in grouped_by_employee.items():
        emp_info = employee_dict.get(requester_id, {})
        emp_name = emp_info.get('name', '알 수 없음')
        emp_id = emp_info.get('employee_id', f'ID{requester_id}')
        
        # 통화별 총 금액 계산
        currency_totals = defaultdict(float)
        for exp in expenses_list:
            currency = exp.get('currency', 'VND')
            amount = exp.get('amount', 0)
            currency_totals[currency] += amount
        
        total_str = ", ".join([f"{amount:,.0f} {curr}" for curr, amount in currency_totals.items()])
        
        with st.expander(f"👤 {emp_name} ({emp_id}) - {len(expenses_list)}건 - {total_str}", expanded=False):
            
            # 테이블 헤더
            cols = st.columns([1.5, 1, 1.5, 1.5, 1])
            cols[0].markdown("**문서번호**")
            cols[1].markdown("**지출일**")
            cols[2].markdown("**지출 내역**")
            cols[3].markdown("**금액**")
            cols[4].markdown("**승인일**")
            
            st.markdown("---")
            
            # 항목별 표시
            for exp in expenses_list:
                cols = st.columns([1.5, 1, 1.5, 1.5, 1])
                
                cols[0].write(exp.get('document_number', 'N/A'))
                cols[1].write(exp.get('expense_date', 'N/A'))
                cols[2].write(exp.get('description', '')[:30] + "...")
                
                amount = exp.get('amount', 0)
                currency = exp.get('currency', 'VND')
                cols[3].write(f"{amount:,.0f} {currency}")
                
                approved_at = exp.get('approved_at', 'N/A')
                if approved_at != 'N/A':
                    try:
                        dt = datetime.fromisoformat(str(approved_at).replace('Z', '+00:00'))
                        approved_at = dt.strftime('%Y-%m-%d')
                    except:
                        pass
                cols[4].write(approved_at)


def render_expense_statistics(load_data_func, calculate_expense_statistics_func):
    """지출 통계 표시"""
    
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not expenses:
        st.info("통계를 표시할 지출 데이터가 없습니다.")
        return
    
    stats = calculate_expense_statistics_func(expenses)
    
    st.subheader("📊 지출 통계 대시보드")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 지출요청", f"{stats.get('total_count', 0)}건")
    
    with col2:
        st.metric("총 요청금액", f"{stats.get('total_amount', 0):,}VND")
    
    with col3:
        st.metric("승인된 금액", f"{stats.get('approved_amount', 0):,}VND")
    
    with col4:
        total_count = stats.get('total_count', 0)
        approved_count = stats.get('approved_count', 0)
        approval_rate = (approved_count / total_count * 100) if total_count > 0 else 0
        st.metric("승인율", f"{approval_rate:.1f}%")
    
    st.subheader("📈 상태별 분석")
    col1, col2 = st.columns(2)
    
    with col1:
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
        category_stats = stats.get('category_stats', {})
        if category_stats:
            st.write("**지출 유형별 통계**")
            for category, data in category_stats.items():
                if isinstance(data, dict):
                    count = data.get('count', 0)
                    amount = data.get('amount', 0)
                    st.write(f"• {category}: {count}건 ({amount:,}VND)")
    
    monthly_stats = stats.get('monthly_stats', {})
    if monthly_stats:
        st.subheader("📅 월별 지출 현황")
        
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
    if not current_user or current_user.get('role') not in ['Master', 'CEO']:
        st.warning("⚠️ 승인 권한이 없습니다.")
        return
    
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not expenses:
        st.info("승인할 지출요청서가 없습니다.")
        return
    
    employee_dict = {}
    if employees:
        for emp in employees:
            emp_id = emp.get('id')
            if emp_id:
                employee_dict[emp_id] = emp
    
    pending_expenses = [exp for exp in expenses if exp.get('status') == 'pending']
    
    if not pending_expenses:
        st.info("승인 대기중인 지출요청서가 없습니다.")
        return
    
    st.subheader(f"👨‍💼 승인 대기중인 지출요청서 ({len(pending_expenses)}건)")
    
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
    
    for expense in pending_expenses:
        requester_id = expense.get('requester')
        employee_info = employee_dict.get(requester_id, {})
        employee_name = employee_info.get('name', '알 수 없음')
        employee_id = employee_info.get('employee_id', f"ID{requester_id}")
        
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
                
                approval_comment = st.text_area(
                    "처리 의견 (선택사항)",
                    key=f"comment_{expense.get('id')}",
                    height=80,
                    help="승인 시: 선택사항, 반려 시: 필수 입력"
                )
                
                button_col1, button_col2 = st.columns(2)
                
                with button_col1:
                    if st.button("✅ 승인", key=f"approve_{expense.get('id')}", type="primary"):
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
                        if not approval_comment or not approval_comment.strip():
                            st.error("⚠️ 반려 사유를 반드시 입력해주세요!")
                        else:
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