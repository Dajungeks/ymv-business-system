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
    
    # 탭 구성 - Admin/CEO/Master는 화던 발행 확인 탭 추가
    if user_role in ['Admin', 'CEO', 'Master']:
        approval_tab_name = f"👨‍💼 승인 관리 ({pending_approval_count})" if pending_approval_count > 0 else "👨‍💼 승인 관리"
        invoice_tab_name = f"🧾 화던 발행 확인 ({pending_invoice_count})" if pending_invoice_count > 0 else "🧾 화던 발행 확인"
        
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
    
    # 화던 발행 확인 탭 (권한 있는 사용자만)
    if user_role in ['Admin', 'CEO', 'Master']:
        with tab5:
            render_invoice_check_tab(load_data_func, update_data_func, get_current_user_func)

def render_status_flow(expense, employee_dict):
    """상태 흐름 시각화"""
    
    expense_status = expense.get('status', 'pending')
    accounting_confirmed = expense.get('accounting_confirmed', False)
    reimbursement_status = expense.get('reimbursement_status', 'pending')
    payment_method = expense.get('payment_method', '')
    
    # 단계별 상태
    step1 = "✅ 요청"
    
    if expense_status == 'approved':
        step2 = "✅ 승인"
    elif expense_status == 'rejected':
        step2 = "❌ 반려"
    else:
        step2 = "⏳ 승인대기"
    
    if expense_status == 'approved':
        if accounting_confirmed:
            step3 = "✅ 화던확인"
        else:
            step3 = "⏳ 화던대기"
    else:
        step3 = "⬜ 화던확인"
    
    # 환급 단계
    if payment_method == '법인카드':
        step4 = "— 환급불필요"
    elif reimbursement_status == 'completed':
        step4 = "✅ 환급완료"
    elif reimbursement_status == 'printed':
        step4 = "⏳ 환급중"
    elif reimbursement_status == 'pending' and accounting_confirmed:
        step4 = "⏳ 환급대기"
    else:
        step4 = "⬜ 환급"
    
    st.info(f"**진행 상태:** {step1} → {step2} → {step3} → {step4}")
    
    # 승인자 정보 (승인됨/반려됨인 경우)
    if expense_status in ['approved', 'rejected'] and expense.get('approved_by'):
        approver = employee_dict.get(expense['approved_by'], {})
        approver_name = approver.get('name', '알 수 없음')
        approved_at = expense.get('approved_at', 'N/A')
        if approved_at != 'N/A':
            try:
                dt = datetime.fromisoformat(str(approved_at).replace('Z', '+00:00'))
                approved_at = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        status_text = "승인" if expense_status == 'approved' else "반려"
        st.caption(f"{status_text}: {approver_name} ({approved_at})")



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
    """지출요청서 목록 관리 (직원별 그룹핑)"""
    
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
    
    # 필터링 옵션 (5개 컬럼)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        status_filter = st.selectbox(
            "상태 필터",
            ["전체", "대기", "승인", "반려", "화던확인완료"],
            key="expense_status_filter"
        )
    
    with col2:
        type_filter = st.selectbox(
            "지출 유형 필터",
            ["전체", "사무용품", "교통비", "식비", "회의비", "출장비", "접대비", "기타"],
            key="expense_type_filter"
        )
    
    with col3:
        payment_filter = st.selectbox(
            "결제 방법 필터",
            ["전체", "법인카드", "현금", "신용카드", "계좌이체"],
            key="expense_payment_filter"
        )
    
    with col4:
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
    
    with col5:
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
            if status_filter == "화던확인완료":
                if not expense.get('accounting_confirmed', False):
                    continue
            else:
                status_map = {"대기": "pending", "승인": "approved", "반려": "rejected"}
                expense_status = expense.get('status', 'pending')
                if expense_status != status_map[status_filter]:
                    continue
        
        # 지출 유형 필터링
        if type_filter != "전체" and expense.get('expense_type') != type_filter:
            continue
        
        # 결제 방법 필터링
        if payment_filter != "전체" and expense.get('payment_method') != payment_filter:
            continue
        
        # 직원 필터링
        if user_role not in ['Master', 'CEO', 'Admin']:
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
    
    # 총 건수 표시 및 CSV 다운로드
    st.write(f"📋 총 {len(filtered_expenses)}건의 지출요청서")
    
    if filtered_expenses:
        csv_data = create_csv_download_func(filtered_expenses, employees)
        if csv_data:
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=f"expense_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
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
        
        # 그룹 헤더 (expander)
        with st.expander(f"👤 {emp_name} ({emp_id}) - 총 {len(expenses_list)}건, {total_str}", expanded=True):
            
            # 각 지출요청서 표시
            for expense in expenses_list:
                document_number = expense.get('document_number', 'N/A')
                expense_date = expense.get('expense_date', 'N/A')
                expense_type = expense.get('expense_type', '기타')
                amount = expense.get('amount', 0)
                currency = expense.get('currency', 'VND')
                expense_status = expense.get('status', 'pending')
                accounting_confirmed = expense.get('accounting_confirmed', False)
                payment_method = expense.get('payment_method', 'N/A')
                
                # 상태 아이콘
                status_info = get_approval_status_info_func(expense_status)
                status_emoji = status_info.get('emoji', '❓')
                status_desc = status_info.get('description', '알 수 없음')
                
                # 화던 상태 아이콘
                if accounting_confirmed:
                    invoice_icon = "🧾"
                    invoice_text = "화던완료"
                elif expense_status == 'approved':
                    invoice_icon = "⏳"
                    invoice_text = "화던대기"
                else:
                    invoice_icon = "—"
                    invoice_text = ""
                
                # 한 줄로 표시
                cols = st.columns([1.5, 1, 1.2, 1, 1.5, 1, 1, 1.5])
                
                cols[0].write(f"**{document_number}**")
                cols[1].write(expense_date)
                cols[2].write(expense_type)
                
                # 결제 방법 표시
                if payment_method == '법인카드':
                    cols[3].write("💳 법인카드")
                else:
                    cols[3].write(payment_method)
                
                cols[4].write(f"**{amount:,} {currency}**")
                cols[5].write(f"{status_emoji} {status_desc}")
                cols[6].write(f"{invoice_icon} {invoice_text}")
                
                with cols[7]:
                    # 화던 확인 버튼 (승인되었고 화던 미확인 항목만)
                    if expense_status == 'approved' and not accounting_confirmed and user_role in ['Admin', 'CEO', 'Master']:
                        if st.button("✅ 화던확인", key=f"invoice_{expense.get('id')}", use_container_width=True):
                            if confirm_invoice_expense(expense.get('id'), current_user.get('id'), update_data_func, load_data_func):
                                st.success("화던 발행 확인 완료!")
                                st.rerun()
                    else:
                        if st.button("📄 상세", key=f"detail_{expense.get('id')}", use_container_width=True):
                            st.session_state[f'show_detail_{expense.get("id")}'] = True
                            st.rerun()
                
                # 상세 정보 (클릭 시 표시)
                if st.session_state.get(f'show_detail_{expense.get("id")}', False):
                    with st.container():
                        st.markdown("---")
                        
                        # 상태 흐름 시각화
                        reimbursement_status = expense.get('reimbursement_status', 'pending')
                        
                        # 단계별 상태
                        step1 = "✅ 요청"
                        
                        if expense_status == 'approved':
                            step2 = "✅ 승인"
                        elif expense_status == 'rejected':
                            step2 = "❌ 반려"
                        else:
                            step2 = "⏳ 승인대기"
                        
                        if expense_status == 'approved':
                            if accounting_confirmed:
                                step3 = "✅ 화던확인"
                            else:
                                step3 = "⏳ 화던대기"
                        else:
                            step3 = "⬜ 화던확인"
                        
                        # 환급 단계
                        if payment_method == '법인카드':
                            step4 = "— 환급불필요"
                        elif reimbursement_status == 'completed':
                            step4 = "✅ 환급완료"
                        elif reimbursement_status == 'printed':
                            step4 = "⏳ 환급중"
                        elif reimbursement_status == 'pending' and accounting_confirmed:
                            step4 = "⏳ 환급대기"
                        else:
                            step4 = "⬜ 환급"
                        
                        st.info(f"**진행 상태:** {step1} → {step2} → {step3} → {step4}")
                        
                        detail_cols = st.columns([2, 1])
                        
                        with detail_cols[0]:
                            st.write("**기본 정보**")
                            st.write(f"• 문서번호: {document_number}")
                            st.write(f"• 부서: {expense.get('department', 'N/A')}")
                            st.write(f"• 지출일: {expense_date}")
                            st.write(f"• 지출 유형: {expense_type}")
                            st.write(f"• 금액: {amount:,} {currency}")
                            st.write(f"• 결제 방법: {payment_method}")
                            st.write(f"• 긴급도: {expense.get('urgency', '보통')}")
                            st.write(f"• 공급업체: {expense.get('vendor', 'N/A')}")
                            st.write(f"• 영수증 번호: {expense.get('receipt_number', 'N/A')}")
                            
                            # 화던 확인 정보
                            if accounting_confirmed:
                                st.write("**화던 발행 확인 정보**")
                                accounting_confirmed_at = expense.get('accounting_confirmed_at', 'N/A')
                                if accounting_confirmed_at != 'N/A':
                                    try:
                                        dt = datetime.fromisoformat(str(accounting_confirmed_at).replace('Z', '+00:00'))
                                        accounting_confirmed_at = dt.strftime('%Y-%m-%d')
                                    except:
                                        pass
                                st.write(f"• 확인일: {accounting_confirmed_at}")
                                
                                accounting_confirmed_by_id = expense.get('accounting_confirmed_by')
                                if accounting_confirmed_by_id:
                                    confirmer_info = employee_dict.get(accounting_confirmed_by_id, {})
                                    confirmer_name = confirmer_info.get('name', '알 수 없음')
                                    st.write(f"• 확인자: {confirmer_name}")
                            
                            st.write("**지출 내역**")
                            st.write(expense.get('description', '내용없음'))
                            
                            if expense.get('business_purpose'):
                                st.write("**사업 목적**")
                                st.write(expense.get('business_purpose'))
                            
                            # 승인 정보
                            if expense_status in ['approved', 'rejected']:
                                st.write("**승인 정보**")
                                approved_at = expense.get('approved_at', 'N/A')
                                if approved_at != 'N/A':
                                    try:
                                        dt = datetime.fromisoformat(str(approved_at).replace('Z', '+00:00'))
                                        approved_at = dt.strftime('%Y-%m-%d')
                                    except:
                                        pass
                                st.write(f"• 처리일: {approved_at}")
                                
                                if expense.get('approved_by'):
                                    approver = employee_dict.get(expense['approved_by'], {})
                                    approver_name = approver.get('name', '알 수 없음')
                                    st.write(f"• 처리자: {approver_name}")
                                
                                if expense.get('approval_comment'):
                                    if expense_status == 'rejected':
                                        st.error(f"**반려 사유**: {expense.get('approval_comment')}")
                                    else:
                                        st.write(f"• 처리 의견: {expense.get('approval_comment')}")
                        
                        with detail_cols[1]:
                            st.write("**액션**")
                            
                            # 프린트 버튼
                            if st.button("🖨️ 프린트", key=f"print_{expense.get('id')}", use_container_width=True):
                                st.session_state['print_expense'] = expense
                                st.rerun()
                            
                            # 삭제 권한
                            can_delete = False
                            if user_role == 'Master':
                                can_delete = True
                            elif user_role == 'Admin' and expense.get('requester') == current_user_id and expense_status == 'pending':
                                can_delete = True
                            elif expense_status == 'rejected' and expense.get('requester') == current_user_id:
                                can_delete = True  # 반려된 요청서는 본인이 삭제 가능
                            
                            if can_delete:
                                if st.button("🗑️ 삭제", key=f"delete_{expense.get('id')}", use_container_width=True):
                                    if delete_data_func("expenses", expense.get('id'), "id"):
                                        st.success("지출요청서가 삭제되었습니다.")
                                        st.rerun()
                                    else:
                                        st.error("삭제에 실패했습니다.")
                            
                            # 수정 권한
                            can_edit = False
                            if user_role == 'Master':
                                can_edit = True
                            elif expense_status == 'rejected' and expense.get('requester') == current_user_id:
                                can_edit = True
                            elif user_role in ['Admin', 'CEO'] and expense_status == 'pending':
                                can_edit = True
                            
                            if can_edit:
                                if st.button("✏️ 수정", key=f"edit_{expense.get('id')}", use_container_width=True):
                                    st.session_state['edit_expense'] = expense
                                    st.rerun()
                            
                            # 재신청 버튼
                            if expense_status == 'rejected' and expense.get('requester') == current_user_id:
                                if st.button("🔄 재신청", key=f"resubmit_{expense.get('id')}", use_container_width=True):
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
                            
                            # 상세 닫기 버튼
                            if st.button("❌ 닫기", key=f"close_{expense.get('id')}", use_container_width=True):
                                st.session_state[f'show_detail_{expense.get("id")}'] = False
                                st.rerun()
                        
                        st.markdown("---")
                
                # 구분선
                st.markdown("<hr style='margin: 5px 0; border: none; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)

def render_invoice_check_tab(load_data_func, update_data_func, get_current_user_func):
    """화던 발행 확인 탭 (리스트만 표시)"""
    
    st.subheader("🧾 화던 발행 확인 대기 목록 (Hóa đơn)")
    st.caption("💡 실제 화던 확인 처리는 '지출요청서 목록' 탭에서 진행하세요.")
    
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not expenses or not employees:
        st.info("데이터를 불러올 수 없습니다.")
        return
    
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
    # 화던 확인 대기 중인 항목 필터링
    pending_expenses = [exp for exp in expenses 
                       if exp.get('status') == 'approved' and not exp.get('accounting_confirmed', False)]
    
    if not pending_expenses:
        st.info("화던 발행 확인 대기 중인 지출요청서가 없습니다.")
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
    
    st.write(f"⏳ 화던 발행 확인 대기 중: {len(filtered_expenses)}건")
    
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
            
            # 항목별 표시 (체크박스 제거)
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

def confirm_invoice_expense(expense_id, user_id, update_data_func, load_data_func):
    """화던 발행 확인 처리 (환급 상태 자동 설정)"""
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
        st.error(f"화던 발행 확인 처리 중 오류: {str(e)}")
        return False


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