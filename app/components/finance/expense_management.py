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
    
    # 탭 구성 - Admin/CEO/Master는 화던 (Hóa đơn) 발행 확인 탭 추가
    if user_role in ['Admin', 'CEO', 'Master']:
        approval_tab_name = f"👨‍💼 승인 관리 ({pending_approval_count})" if pending_approval_count > 0 else "👨‍💼 승인 관리"
        invoice_tab_name = f"🧾 화던 (Hóa đơn) 확인 대기 항목 ({pending_invoice_count})" if pending_invoice_count > 0 else "🧾 화던 (Hóa đơn) 발행 확인"
        
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
        render_expense_form(load_data_func, save_data_func, current_user)
    
    with tab2:
        render_expense_list(load_data_func, update_data_func, delete_data_func, 
                          get_current_user_func, get_approval_status_info_func, 
                          create_csv_download_func, render_print_form_func)
    
    with tab3:
        render_expense_statistics(load_data_func, calculate_expense_statistics_func)
    
    with tab4:
        render_approval_management(load_data_func, update_data_func, get_current_user_func, 
                                  get_approval_status_info_func)
    
    # 화던 (Hóa đơn) 발행 확인 탭 (권한 있는 사용자만)
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

def render_expense_form(load_data_func, save_data_func, current_user):
    """지출 요청 폼 렌더링"""
    
    st.subheader("💰 새 지출 요청")
    
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # 요청자 선택 (직원 목록에서)
            employees = load_data_func("employees") if load_data_func else []
            if not employees:
                st.warning("직원 정보가 없습니다. 먼저 직원을 등록해주세요.")
                st.form_submit_button("제출", disabled=True)
                return
            
            # 활성 직원만 필터링
            active_employees = [emp for emp in employees if emp.get('employment_status') == 'active']
            
            if not active_employees:
                st.warning("활성화된 직원이 없습니다.")
                st.form_submit_button("제출", disabled=True)
                return
            
            # 직원 선택 (이름 + 사번)
            employee_options = {
                f"{emp.get('name', 'N/A')} ({emp.get('employee_id', 'N/A')})": emp.get('id')
                for emp in active_employees
            }
            
            selected_employee_display = st.selectbox(
                "요청자",
                options=list(employee_options.keys())
            )
            selected_employee_id = employee_options[selected_employee_display]
        
        with col2:
            currency = st.selectbox("통화", ["VND", "USD", "KRW"])
        
        with col1:
            # 직원 관리에서 부서 목록 가져오기
            departments = sorted(list(set([emp.get('department', '') for emp in employees if emp.get('department')])))
            
            if not departments:
                departments = ["대표이사실"]  # 기본값
            
            department = st.selectbox("부서", options=departments, index=0 if "대표이사실" in departments else 0)
        
        with col2:
            # 통화별 step 설정
            currency_steps = {
                "USD": 10,
                "VND": 10000,
                "KRW": 1000
            }
            step = currency_steps.get(currency, 1000)
            
            amount = st.number_input(
                f"금액 ({currency})",
                min_value=0.0,
                value=0.0,
                step=float(step)
            )
        
        # 지출일
        expense_date = st.date_input("지출일", value=datetime.now().date())
        
        # 결제 방법
        payment_method = st.selectbox(
            "결제 방법",
            ["현금", "개인신용카드", "법인카드","법인계좌", "개인 계좌 이체", "기타"]
        )
        
        # 지출 유형
        expense_type = st.selectbox(
            "지출 유형",
            ["교통비", "식비", "숙박비", "사무용품", "통신비", "접대비", "기타"]
        )
        
        # 긴급도
        urgency = st.selectbox("긴급도", ["낮음", "보통", "높음", "긴급"], index=1)
        
        # 공급업체 (선택사항)
        vendor = st.text_input("공급업체 (선택사항)")
        
        # 지출 내역
        description = st.text_area("지출 내역", height=100, placeholder="상세한 지출 내역을 입력하세요")
        
        # 사업 목적 (선택사항)
        business_purpose = st.text_area("사업 목적 (선택사항)", height=80)
        
        # 영수증 번호 (선택사항)
        receipt_number = st.text_input("영수증 번호 (선택사항)")
        
        # 비고
        notes = st.text_area("비고 (선택)")
        
        # 제출 버튼
        submitted = st.form_submit_button("📝 지출 요청 제출", type="primary", use_container_width=True)
        
        if submitted:
            # 유효성 검사
            if amount <= 0:
                st.error("❌ 금액을 입력해주세요.")
                return
            
            if not expense_type:
                st.error("❌ 지출 유형을 선택해주세요.")
                return
            
            # 지출 데이터 생성
            expense_data = {
                "requester": selected_employee_id,
                "department": department,
                "expense_date": expense_date.isoformat(),
                "expense_type": expense_type,
                "amount": amount,
                "currency": currency,
                "payment_method": payment_method,
                "vendor": vendor if vendor.strip() else None,
                "description": description if description.strip() else None,
                "business_purpose": business_purpose if business_purpose.strip() else None,
                "receipt_number": receipt_number if receipt_number.strip() else None,
                "notes": notes if notes.strip() else None,
                "urgency": urgency,
                "status": "pending",
                "document_number": generate_document_number(load_data_func),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # DB 저장
            if save_data_func("expenses", expense_data):
                st.success("✅ 지출 요청이 제출되었습니다!")
                st.balloons()
                
                # 성공 메시지 표시 후 리로드
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ 지출 요청 제출에 실패했습니다.")

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
            ["전체", "대기", "승인", "반려", "화던 (Hóa đơn)확인완료"],
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
            ["전체", "법인카드", "현금", "개인 신용카드", "계좌이체"],
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
    
    # 권한별 필터링
    if user_role == 'Staff':
        # 일반 직원은 본인 요청서만
        filtered = [exp for exp in filtered if (exp.get('requester') or exp.get('employee_id')) == current_user_id]
    
    # 상태 필터
    status_filter = st.session_state.get('expense_status_filter', '전체')
    if status_filter != '전체':
        if status_filter == '대기':
            filtered = [exp for exp in filtered if exp.get('status') == 'pending']
        elif status_filter == '승인':
            filtered = [exp for exp in filtered if exp.get('status') == 'approved']
        elif status_filter == '반려':
            filtered = [exp for exp in filtered if exp.get('status') == 'rejected']
        elif status_filter == '화던 (Hóa đơn)확인완료':
            filtered = [exp for exp in filtered if exp.get('accounting_confirmed', False)]
    
    # 지출 유형 필터
    type_filter = st.session_state.get('expense_type_filter', '전체')
    if type_filter != '전체':
        filtered = [exp for exp in filtered if exp.get('expense_type') == type_filter]
    
    # 결제 방법 필터
    payment_filter = st.session_state.get('expense_payment_filter', '전체')
    if payment_filter != '전체':
        filtered = [exp for exp in filtered if exp.get('payment_method') == payment_filter]
    
    # 직원 필터 (권한자만)
    if user_role in ['Master', 'CEO', 'Admin']:
        employee_filter = st.session_state.get('expense_employee_filter', '전체')
        if employee_filter and employee_filter != '전체':
            employee_name = employee_filter.split(" (")[0]
            filtered = [
                exp for exp in filtered
                if employee_dict.get(exp.get('requester') or exp.get('employee_id'), {}).get('name') == employee_name
            ]
    
    # 기간 필터
    date_from = st.session_state.get('expense_date_from')
    date_to = st.session_state.get('expense_date_to')
    
    if date_from:
        filtered = [exp for exp in filtered if exp.get('expense_date', '') >= str(date_from)]
    if date_to:
        filtered = [exp for exp in filtered if exp.get('expense_date', '') <= str(date_to)]
    
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
    
    table_data = []
    for exp in filtered_expenses:
        requester_id = exp.get('requester') or exp.get('employee_id')
        requester_info = employee_dict.get(requester_id, {})
        requester_name = requester_info.get('name', '알 수 없음')
        
        # 상태 아이콘
        expense_status = exp.get('status', 'pending')
        status_info = get_approval_status_info_func(expense_status)
        status_display = f"{status_info.get('emoji', '❓')} {status_info.get('description', '알 수 없음')}"
        
        # 화던 (Hóa đơn) 상태
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
            '화던 (Hóa đơn)': invoice_display,
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
                
                requester_id = expense.get('requester') or expense.get('employee_id')
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
                st.write(f"• 상태: {status_info.get('emoji', '')} {status_info.get('description', '알 수 없음')}")
                
                accounting_confirmed = expense.get('accounting_confirmed', False)
                if accounting_confirmed:
                    st.write("• 화던 (Hóa đơn): ✅ 확인완료")
                elif expense_status == 'approved':
                    st.write("• 화던 (Hóa đơn): ⏳ 대기중")
                else:
                    st.write("• 화던 (Hóa đơn): —")
                
                urgency = expense.get('urgency', '보통')
                st.write(f"• 긴급도: {urgency}")
            
            st.markdown("**지출 내역**")
            st.write(expense.get('description', '내역 없음'))
            
            if expense.get('business_purpose'):
                st.markdown("**사업 목적**")
                st.write(expense.get('business_purpose'))
            
            if expense.get('notes'):
                st.markdown("**비고**")
                st.write(expense.get('notes'))
            
            if expense.get('approval_comment'):
                st.markdown("**처리 의견**")
                st.info(expense.get('approval_comment'))
            
            user_role = current_user.get('role', 'Staff')
            
            st.markdown("---")
            
            # 액션 버튼
            action_cols = st.columns(4)
            
            with action_cols[0]:
                if st.button(f"🖨️ 프린트 #{expense.get('id')}", key=f"print_{expense.get('id')}"):
                    st.session_state['print_expense'] = expense
                    st.rerun()
            
            with action_cols[1]:
                # 수정 권한: 본인 요청 + 대기/반려 상태
                if expense_status in ['pending', 'rejected'] and (expense.get('requester') or expense.get('employee_id')) == current_user.get('id'):
                    if st.button(f"✏️ 수정 #{expense.get('id')}", key=f"edit_{expense.get('id')}"):
                        st.info("수정 기능은 개발 중입니다.")
            
            with action_cols[2]:
                # 삭제 권한: Admin 본인 요청 대기 상태 / CEO-Master 무조건
                can_delete = False
                if user_role in ['Master', 'CEO']:
                    can_delete = True
                elif user_role == 'Admin' and (expense.get('requester') or expense.get('employee_id')) == current_user.get('id') and expense_status == 'pending':
                    can_delete = True
                
                if can_delete:
                    if st.button(f"🗑️ 삭제 #{expense.get('id')}", key=f"delete_{expense.get('id')}"):
                        st.session_state[f'confirm_delete_{expense.get("id")}'] = True
            
            with action_cols[3]:
                # 화던 (Hóa đơn) 확인 (권한자 전용)
                if user_role in ['Master', 'CEO', 'Admin']:
                    if expense_status == 'approved' and not accounting_confirmed:
                        if st.button(f"✅ 화던 (Hóa đơn) 확인 #{expense.get('id')}", 
                                   key=f"confirm_invoice_{expense.get('id')}"):
                            update_data = {
                                'id': expense.get('id'),
                                'accounting_confirmed': True,
                                'accounting_confirmed_at': datetime.now().isoformat(),
                                'accounting_confirmed_by': current_user.get('id')
                            }
                            
                            if update_data_func("expenses", update_data, "id"):
                                st.success(f"✅ 화던 (Hóa đơn) 확인 완료: {document_number}")
                                st.rerun()
                            else:
                                st.error("화던 (Hóa đơn) 확인 처리 실패")
            
            # 삭제 확인
            if st.session_state.get(f'confirm_delete_{expense.get("id")}'):
                st.warning(f"⚠️ 정말 삭제하시겠습니까? (문서번호: {document_number})")
                confirm_cols = st.columns(2)
                
                with confirm_cols[0]:
                    if st.button(f"예, 삭제합니다 #{expense.get('id')}", 
                               key=f"confirm_yes_{expense.get('id')}"):
                        # 삭제 로직
                        st.success(f"✅ {document_number} 삭제됨")
                        if f'confirm_delete_{expense.get("id")}' in st.session_state:
                            del st.session_state[f'confirm_delete_{expense.get("id")}']
                        st.rerun()
                
                with confirm_cols[1]:
                    if st.button(f"아니오 #{expense.get('id')}", 
                               key=f"confirm_no_{expense.get('id')}"):
                        if f'confirm_delete_{expense.get("id")}' in st.session_state:
                            del st.session_state[f'confirm_delete_{expense.get("id")}']
                        st.rerun()

def render_delete_confirmation(filtered_expenses, current_user, user_role, delete_data_func, load_data_func, update_data_func):
    """삭제 확인 모달 - 구매요청 상태 되돌리기 추가"""
    
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
                    # 1. 연결된 구매요청 상태 되돌리기
                    revert_purchase_approval(exp_id, load_data_func, update_data_func)
                    
                    # 2. 지출요청서 삭제
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


def revert_purchase_approval(expense_id, load_data_func, update_data_func):
    """지출요청서 삭제 시 연결된 구매요청 상태 되돌리기"""
    try:
        # 연결된 구매요청 찾기
        purchases = load_data_func("purchases") or []
        related_purchase = next((p for p in purchases if p.get('expense_id') == expense_id), None)
        
        if related_purchase:
            # 승인대기 상태로 되돌리기
            update_data = {
                'id': related_purchase.get('id'),
                'approval_status': '승인대기',
                'approver_id': None,
                'approved_at': None,
                'status': '대기중',
                'expense_id': None,
                'updated_at': datetime.now().isoformat()
            }
            
            update_data_func("purchases", update_data, "id")
    except Exception as e:
        # 오류 발생 시 로그만 남기고 삭제는 계속 진행
        print(f"구매요청 상태 되돌리기 오류: {str(e)}")

def confirm_invoice_expense(expense_id, user_id, update_data_func, load_data_func):
    """화던 (Hóa đơn) 발행 확인 처리 (환급 상태 자동 설정)"""
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
        st.error(f"화던 (Hóa đơn) 발행 확인 처리 중 오류: {str(e)}")
        return False

def render_invoice_check_tab(load_data_func, update_data_func, get_current_user_func):
    """화던 (Hóa đơn) 발행 확인 탭 (테이블 형식 + 일괄 확인)"""
    
    st.subheader("🧾 화던 (Hóa đơn) 발행 확인 대기 목록")
    
    expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    current_user = get_current_user_func()
    
    if not expenses or not employees:
        st.info("데이터를 불러올 수 없습니다.")
        return
    
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
    # 화던 (Hóa đơn) 확인 대기 중인 항목 필터링
    pending_expenses = [exp for exp in expenses 
                       if exp.get('status') == 'approved' and not exp.get('accounting_confirmed', False)]
    
    if not pending_expenses:
        st.info("화던 (Hóa đơn) 발행 확인 대기 중인 지출요청서가 없습니다.")
        return
    
    st.write(f"⏳ 화던 (Hóa đơn) 발행 확인 대기 중: **{len(pending_expenses)}건**")
    
    # 필터 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("🔍 검색", placeholder="문서번호, 직원명...", key="invoice_search")
    
    with col2:
        sort_option = st.selectbox(
            "정렬",
            ["최신순", "오래된순", "금액높은순", "금액낮은순"],
            key="invoice_sort"
        )
    
    with col3:
        currency_filter = st.selectbox("통화", ["전체", "VND", "USD", "KRW"], key="invoice_currency")
    
    # 필터링
    filtered_expenses = pending_expenses
    
    if search_query:
        filtered_expenses = [
            exp for exp in filtered_expenses
            if search_query.lower() in str(exp.get('document_number', '')).lower()
            or search_query.lower() in str(employee_dict.get(exp.get('requester'), {}).get('name', '')).lower()
        ]
    
    if currency_filter != "전체":
        filtered_expenses = [exp for exp in filtered_expenses if exp.get('currency') == currency_filter]
    
    # 정렬
    if sort_option == "최신순":
        filtered_expenses.sort(key=lambda x: x.get('approved_at', ''), reverse=True)
    elif sort_option == "오래된순":
        filtered_expenses.sort(key=lambda x: x.get('approved_at', ''))
    elif sort_option == "금액높은순":
        filtered_expenses.sort(key=lambda x: x.get('amount', 0), reverse=True)
    elif sort_option == "금액낮은순":
        filtered_expenses.sort(key=lambda x: x.get('amount', 0))
    
    # 통계 정보
    if filtered_expenses:
        currency_totals = defaultdict(float)
        for exp in filtered_expenses:
            currency = exp.get('currency', 'VND')
            amount = exp.get('amount', 0)
            currency_totals[currency] += amount
        
        st.info(f"📊 총 금액: " + ", ".join([f"{amount:,.0f} {curr}" for curr, amount in currency_totals.items()]))
    
    st.markdown("---")
    
    # 테이블 데이터 생성
    table_data = []
    for exp in filtered_expenses:
        emp_info = employee_dict.get(exp.get('requester'), {})
        emp_name = emp_info.get('name', '알 수 없음')
        emp_id = emp_info.get('employee_id', 'N/A')
        
        approved_at = exp.get('approved_at', 'N/A')
        if approved_at != 'N/A':
            try:
                dt = datetime.fromisoformat(str(approved_at).replace('Z', '+00:00'))
                approved_at = dt.strftime('%Y-%m-%d')
            except:
                pass
        
        table_data.append({
            'ID': exp.get('id'),
            '문서번호': exp.get('document_number', 'N/A'),
            '요청자': f"{emp_name} ({emp_id})",
            '부서': exp.get('department', 'N/A'),
            '지출일': exp.get('expense_date', 'N/A'),
            '지출유형': exp.get('expense_type', 'N/A'),
            '금액': f"{exp.get('amount', 0):,.0f}",
            '통화': exp.get('currency', 'VND'),
            '공급업체': exp.get('vendor', 'N/A'),
            '승인일': approved_at
        })
    
    # 테이블 표시
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ID 선택 영역
        st.markdown("### 📋 ID 선택 (다중 선택 가능)")
        
        # 세션 상태 초기화
        if 'selected_invoice_ids' not in st.session_state:
            st.session_state.selected_invoice_ids = []
        
        # 전체 선택/해제
        col_all, _ = st.columns([1, 5])
        with col_all:
            all_ids = [exp.get('id') for exp in filtered_expenses]
            is_all_selected = len(st.session_state.selected_invoice_ids) == len(all_ids) and \
                             all(exp_id in st.session_state.selected_invoice_ids for exp_id in all_ids)
            
            select_all = st.checkbox("전체 선택", value=is_all_selected, key="select_all_invoices")
        
        # 전체 선택/해제 토글
        if select_all and not is_all_selected:
            st.session_state.selected_invoice_ids = [exp.get('id') for exp in filtered_expenses]
            st.rerun()
        elif not select_all and is_all_selected:
            st.session_state.selected_invoice_ids = []
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
                            value=exp_id in st.session_state.selected_invoice_ids,
                            key=f"check_invoice_{exp_id}"
                        )
                        
                        if is_checked and exp_id not in st.session_state.selected_invoice_ids:
                            st.session_state.selected_invoice_ids.append(exp_id)
                        elif not is_checked and exp_id in st.session_state.selected_invoice_ids:
                            st.session_state.selected_invoice_ids.remove(exp_id)
        
        st.markdown("---")
        
        # 선택된 항목 액션
        selected_count = len(st.session_state.selected_invoice_ids)
        
        if selected_count > 0:
            selected_ids_text = ", ".join([str(id) for id in sorted(st.session_state.selected_invoice_ids)])
            st.success(f"✅ {selected_count}건 선택됨 (ID: {selected_ids_text})")
            
            # 일괄 확인 버튼
            if st.button("✅ 선택 항목 일괄 화던 (Hóa đơn) 확인", type="primary", use_container_width=True):
                success_count = 0
                fail_count = 0
                
                for exp_id in st.session_state.selected_invoice_ids:
                    update_data = {
                        'id': exp_id,
                        'accounting_confirmed': True,
                        'accounting_confirmed_at': datetime.now().isoformat(),
                        'accounting_confirmed_by': current_user.get('id')
                    }
                    
                    if update_data_func("expenses", update_data, "id"):
                        success_count += 1
                    else:
                        fail_count += 1
                
                if success_count > 0:
                    st.success(f"✅ {success_count}건 화던 (Hóa đơn) 확인 완료!")
                if fail_count > 0:
                    st.error(f"❌ {fail_count}건 처리 실패")
                
                # 선택 초기화
                st.session_state.selected_invoice_ids = []
                st.rerun()
        else:
            st.info("화던 (Hóa đơn) 확인할 항목을 선택해주세요.")
    else:
        st.info("조건에 맞는 항목이 없습니다.")

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
    """승인 관리 (CEO/Master 전용) - 테이블 + ID 입력 방식"""
    
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
    
    st.subheader(f"✅ 지출요청서 승인 관리")
    
    st.write(f"📋 총 {len(pending_expenses)}건의 승인 대기")
    
    # 테이블 데이터 생성
    table_data = []
    for exp in pending_expenses:
        requester_id = exp.get('requester') or exp.get('employee_id')
        employee_info = employee_dict.get(requester_id, {})
        employee_name = employee_info.get('name', '알 수 없음')
        
        request_date = 'N/A'
        if exp.get('created_at'):
            try:
                dt = datetime.fromisoformat(str(exp['created_at']).replace('Z', '+00:00'))
                request_date = dt.strftime('%Y-%m-%d')
            except:
                request_date = str(exp['created_at'])[:10]
        
        table_data.append({
            'ID': exp.get('id'),
            '문서번호': exp.get('document_number', 'N/A'),
            '요청자': employee_name,
            '요청일': request_date,
            '지출일': exp.get('expense_date', 'N/A'),
            '지출유형': exp.get('expense_type', '기타'),
            '금액': f"{exp.get('amount', 0):,.0f}",
            '통화': exp.get('currency', 'VND'),
            '결제방법': exp.get('payment_method', 'N/A'),
            '긴급도': exp.get('urgency', '보통')
        })
    
    # 테이블 표시
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, height=400, hide_index=True)
        
        st.markdown("---")
        
        # 승인/반려 처리
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ 승인")
            approve_ids_input = st.text_input(
                "승인할 ID (쉼표로 구분)",
                placeholder="예: 15, 14, 7",
                key="approve_expense_ids"
            )
            
            if approve_ids_input:
                try:
                    approve_ids = [int(id.strip()) for id in approve_ids_input.split(',')]
                    selected_expenses = [exp for exp in pending_expenses if exp.get('id') in approve_ids]
                    
                    if selected_expenses:
                        # 통화별 합계
                        currency_totals = {}
                        for exp in selected_expenses:
                            currency = exp.get('currency', 'VND')
                            amount = exp.get('amount', 0)
                            currency_totals[currency] = currency_totals.get(currency, 0) + amount
                        
                        total_str = ", ".join([f"{amount:,.0f} {curr}" for curr, amount in currency_totals.items()])
                        
                        st.info(f"선택된 항목: {len(selected_expenses)}건 - {total_str}")
                        
                        if st.button(f"✅ 승인 처리 ({len(selected_expenses)}건)", type="primary", use_container_width=True):
                            success_count = 0
                            
                            for exp in selected_expenses:
                                update_data = {
                                    'id': exp.get('id'),
                                    'status': 'approved',
                                    'approved_by': current_user.get('id'),
                                    'approved_at': datetime.now().isoformat(),
                                    'updated_at': datetime.now().isoformat()
                                }
                                
                                if update_data_func("expenses", update_data, "id"):
                                    success_count += 1
                            
                            if success_count == len(selected_expenses):
                                st.success(f"✅ {len(selected_expenses)}건 승인 완료!")
                                import time
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.warning(f"⚠️ {success_count}/{len(selected_expenses)}건만 승인되었습니다.")
                                import time
                                time.sleep(2)
                                st.rerun()
                    else:
                        st.warning("⚠️ 선택한 ID가 승인 대기 목록에 없습니다.")
                except ValueError:
                    st.error("⚠️ ID는 숫자로 입력해주세요.")
        
        with col2:
            st.markdown("### ❌ 반려")
            reject_ids_input = st.text_input(
                "반려할 ID (쉼표로 구분)",
                placeholder="예: 15, 14, 7",
                key="reject_expense_ids"
            )
            
            reject_reason = st.text_input("반려 사유 *", key="reject_expense_reason")
            
            if reject_ids_input:
                try:
                    reject_ids = [int(id.strip()) for id in reject_ids_input.split(',')]
                    selected_expenses = [exp for exp in pending_expenses if exp.get('id') in reject_ids]
                    
                    if selected_expenses:
                        st.info(f"선택된 항목: {len(selected_expenses)}건")
                        
                        if st.button(f"❌ 반려 처리 ({len(selected_expenses)}건)", type="secondary", use_container_width=True):
                            if not reject_reason.strip():
                                st.error("반려 사유를 입력해주세요.")
                            else:
                                success_count = 0
                                
                                for exp in selected_expenses:
                                    update_data = {
                                        'id': exp.get('id'),
                                        'status': 'rejected',
                                        'approved_by': current_user.get('id'),
                                        'approved_at': datetime.now().isoformat(),
                                        'approval_comment': reject_reason,
                                        'updated_at': datetime.now().isoformat()
                                    }
                                    
                                    if update_data_func("expenses", update_data, "id"):
                                        success_count += 1
                                
                                if success_count == len(selected_expenses):
                                    st.success(f"✅ {len(selected_expenses)}건 반려 완료!")
                                    import time
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.warning(f"⚠️ {success_count}/{len(selected_expenses)}건만 반려되었습니다.")
                                    import time
                                    time.sleep(2)
                                    st.rerun()
                    else:
                        st.warning("⚠️ 선택한 ID가 승인 대기 목록에 없습니다.")
                except ValueError:
                    st.error("⚠️ ID는 숫자로 입력해주세요.")


