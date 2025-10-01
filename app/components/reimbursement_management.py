import streamlit as st
import pandas as pd
from datetime import datetime
from collections import defaultdict

def show_reimbursement_management(load_data_func, update_data_func, get_current_user_func):
    """환급 관리 메인 함수"""
    
    st.header("💰 환급 관리")
    
    current_user = get_current_user_func()
    user_role = current_user.get('role', 'Staff') if current_user else 'Staff'
    
    # 권한 체크: Admin, CEO, Master만 접근 가능
    if user_role not in ['Admin', 'CEO', 'Master']:
        st.warning("⚠️ 환급 관리 권한이 없습니다.")
        return
    
    # 프린트 모드 확인
    # 프린트 모드 확인
    if st.session_state.get('print_reimbursement'):
        from utils.helpers import PrintFormGenerator
        PrintFormGenerator.render_reimbursement_print(
            st.session_state['print_reimbursement'],
            load_data_func,
            get_current_user_func
        )
        if st.button("← 목록으로 돌아가기", type="primary"):
            del st.session_state['print_reimbursement']
            st.rerun()
        return

    # 탭 구성 (3개로 변경)
    tab1, tab2, tab3 = st.tabs(["📋 환급 대기 목록", "🖨️ 프린트 완료 목록", "✅ 최종 완료 내역"])

    with tab1:
        render_reimbursement_pending(load_data_func, update_data_func, get_current_user_func)

    with tab2:
        render_reimbursement_printed(load_data_func, update_data_func, get_current_user_func)

    with tab3:
        render_reimbursement_completed(load_data_func, get_current_user_func)


def render_reimbursement_pending(load_data_func, update_data_func, get_current_user_func):
    """환급 대기 목록 - 프린트만"""
    
    st.subheader("📋 환급 대기 목록")
    
    # 데이터 로드
    all_expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not all_expenses or not employees:
        st.info("데이터를 불러올 수 없습니다.")
        return
    
    # 직원 딕셔너리
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
    # 환급 대기 중인 항목 필터링
    pending_expenses = [exp for exp in all_expenses 
                       if exp.get('reimbursement_status') == 'pending']
    
    if not pending_expenses:
        st.info("환급 대기 중인 지출요청서가 없습니다.")
        return
    
    # 직원별 필터
    employee_filter_options = ["전체"]
    requester_ids = list(set([exp.get('requester') for exp in pending_expenses]))
    for req_id in requester_ids:
        emp_info = employee_dict.get(req_id, {})
        emp_name = emp_info.get('name', '알 수 없음')
        emp_id = emp_info.get('employee_id', f'ID{req_id}')
        employee_filter_options.append(f"{emp_name} ({emp_id})")
    
    selected_employee = st.selectbox("직원 필터", employee_filter_options, key="reimbursement_employee_filter")
    
    # 필터링
    if selected_employee != "전체":
        employee_name = selected_employee.split(" (")[0]
        filtered_expenses = [exp for exp in pending_expenses 
                           if employee_dict.get(exp.get('requester'), {}).get('name') == employee_name]
    else:
        filtered_expenses = pending_expenses
    
    st.write(f"💳 총 {len(filtered_expenses)}건의 환급 대기")
    
    if not filtered_expenses:
        return
    
    # 직원별 그룹핑
    grouped_by_employee = defaultdict(list)
    for exp in filtered_expenses:
        requester_id = exp.get('requester')
        grouped_by_employee[requester_id].append(exp)
    
    # 선택된 항목 저장용 (세션 상태)
    if 'selected_reimbursements' not in st.session_state:
        st.session_state.selected_reimbursements = {}
    
    # 직원별로 표시
    for requester_id, expenses in grouped_by_employee.items():
        emp_info = employee_dict.get(requester_id, {})
        emp_name = emp_info.get('name', '알 수 없음')
        emp_id = emp_info.get('employee_id', f'ID{requester_id}')
        
        # 통화별 합계 계산
        currency_totals = defaultdict(float)
        for exp in expenses:
            currency = exp.get('currency', 'VND')
            amount = exp.get('amount', 0)
            currency_totals[currency] += amount
        
        total_str = ", ".join([f"{amount:,.0f} {curr}" for curr, amount in currency_totals.items()])
        
        with st.expander(f"👤 {emp_name} ({emp_id}) - {len(expenses)}건 - {total_str}", expanded=True):
            # 세션 초기화
            if requester_id not in st.session_state.selected_reimbursements:
                st.session_state.selected_reimbursements[requester_id] = []
            
            # 테이블 헤더
            cols = st.columns([0.5, 1.5, 1, 1.5, 1, 1])
            cols[0].markdown("**선택**")
            cols[1].markdown("**문서번호**")
            cols[2].markdown("**지출일**")
            cols[3].markdown("**내역**")
            cols[4].markdown("**금액**")
            cols[5].markdown("**통화**")
            
            st.markdown("---")
            
            # 항목별 표시
            selected_expense_ids = []
            for exp in expenses:
                exp_id = exp.get('id')
                cols = st.columns([0.5, 1.5, 1, 1.5, 1, 1])
                
                with cols[0]:
                    if st.checkbox("", key=f"select_{exp_id}", label_visibility="collapsed"):
                        selected_expense_ids.append(exp_id)
                
                cols[1].write(exp.get('document_number', 'N/A'))
                cols[2].write(exp.get('expense_date', 'N/A'))
                cols[3].write(exp.get('description', '')[:20] + "...")
                cols[4].write(f"{exp.get('amount', 0):,.0f}")
                cols[5].write(exp.get('currency', 'VND'))
            
            st.markdown("---")
            
            # 선택된 항목 프린트 버튼
            if selected_expense_ids:
                selected_expenses = [exp for exp in expenses if exp.get('id') in selected_expense_ids]
                
                if st.button(f"🖨️ 선택 항목 프린트 ({len(selected_expenses)}건)", 
                           key=f"print_{requester_id}", use_container_width=True):
                    
                    # 임시 상태로 먼저 업데이트
                    success_count = 0
                    for exp in selected_expenses:
                        result = update_data_func("expenses", {
                            'id': exp.get('id'),
                            'reimbursement_status': 'printed',
                            'reimbursement_document_number': 'TEMP',
                            'updated_at': datetime.now().isoformat()
                        }, "id")
                        
                        if result:
                            success_count += 1
                    
                    # 업데이트 성공 확인
                    if success_count == len(selected_expenses):
                        # DB 반영 대기
                        import time
                        time.sleep(0.5)
                        
                        # 문서번호 생성 (업데이트 후)
                        from components.document_number import generate_document_number
                        document_number = generate_document_number('PAY', load_func=load_data_func)
                        
                        # 실제 문서번호로 업데이트
                        for exp in selected_expenses:
                            update_data_func("expenses", {
                                'id': exp.get('id'),
                                'reimbursement_document_number': document_number,
                                'updated_at': datetime.now().isoformat()
                            }, "id")
                        
                        # 통화별 그룹핑
                        grouped_by_currency = defaultdict(list)
                        for exp in selected_expenses:
                            currency = exp.get('currency', 'VND')
                            grouped_by_currency[currency].append(exp)
                        
                        # 프린트 데이터 저장
                        st.session_state['print_reimbursement'] = {
                            'employee_id': requester_id,
                            'grouped_expenses': dict(grouped_by_currency),
                            'document_number': document_number
                        }
                        st.success(f"✅ {success_count}건 프린트 준비 완료! 문서번호: {document_number}")
                        st.rerun()
                    else:
                        st.error(f"⚠️ {success_count}/{len(selected_expenses)}건만 처리되었습니다.")

def render_reimbursement_printed(load_data_func, update_data_func, get_current_user_func):
    """프린트 완료 목록 - 최종 환급 처리 대기"""
    
    st.subheader("🖨️ 프린트 완료 목록")
    
    # 데이터 로드
    all_expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not all_expenses or not employees:
        st.info("데이터를 불러올 수 없습니다.")
        return
    
    # 직원 딕셔너리
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
    # 프린트 완료 항목 필터링
    printed_expenses = [exp for exp in all_expenses 
                       if exp.get('reimbursement_status') == 'printed']
    
    if not printed_expenses:
        st.info("프린트 완료된 항목이 없습니다.")
        return
    
    # 정렬 옵션
    sort_option = st.selectbox("정렬", ["최신순", "오래된순", "금액높은순"], key="printed_sort")
    
    if sort_option == "최신순":
        printed_expenses.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
    elif sort_option == "오래된순":
        printed_expenses.sort(key=lambda x: x.get('updated_at', ''))
    elif sort_option == "금액높은순":
        printed_expenses.sort(key=lambda x: x.get('amount', 0), reverse=True)
    
    st.write(f"📄 총 {len(printed_expenses)}건의 프린트 완료")
    
    # 문서번호별 그룹핑
    grouped_by_doc = defaultdict(list)
    for exp in printed_expenses:
        doc_num = exp.get('reimbursement_document_number', 'N/A')
        grouped_by_doc[doc_num].append(exp)
    
    # 문서번호별로 표시
    for doc_num, expenses in grouped_by_doc.items():
        # 첫 번째 항목에서 직원 정보 추출
        first_exp = expenses[0]
        requester_id = first_exp.get('requester')
        emp_info = employee_dict.get(requester_id, {})
        emp_name = emp_info.get('name', '알 수 없음')
        
        # 통화별 합계
        currency_totals = defaultdict(float)
        for exp in expenses:
            currency = exp.get('currency', 'VND')
            amount = exp.get('amount', 0)
            currency_totals[currency] += amount
        
        total_str = ", ".join([f"{amount:,.0f} {curr}" for curr, amount in currency_totals.items()])
        
        with st.expander(f"📋 {doc_num} - {emp_name} - {len(expenses)}건 - {total_str}", expanded=False):
            # 상세 내역 표시
            for exp in expenses:
                cols = st.columns([2, 1, 1, 1])
                cols[0].write(f"**{exp.get('description', 'N/A')[:30]}**")
                cols[1].write(exp.get('expense_date', 'N/A'))
                cols[2].write(f"{exp.get('amount', 0):,.0f}")
                cols[3].write(exp.get('currency', 'VND'))
            
            st.markdown("---")
            
            # 최종 환급 완료 버튼
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"✅ 최종 환급 완료", key=f"complete_{doc_num}", use_container_width=True):
                    current_user = get_current_user_func()
                    success_count = 0
                    
                    for exp in expenses:
                        if complete_reimbursement(exp.get('id'), current_user.get('id'), update_data_func):
                            success_count += 1
                    
                    if success_count == len(expenses):
                        st.success(f"✅ {len(expenses)}건 최종 환급 완료!")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ {success_count}/{len(expenses)}건만 처리되었습니다.")
            
            with col2:
                if st.button(f"🖨️ 재출력", key=f"reprint_{doc_num}", use_container_width=True):
                    # 통화별 그룹핑
                    grouped_by_currency = defaultdict(list)
                    for exp in expenses:
                        currency = exp.get('currency', 'VND')
                        grouped_by_currency[currency].append(exp)
                    
                    # 프린트 데이터 저장
                    st.session_state['print_reimbursement'] = {
                        'employee_id': requester_id,
                        'grouped_expenses': dict(grouped_by_currency),
                        'document_number': doc_num
                    }
                    st.rerun()


def complete_reimbursement(expense_id, user_id, update_data_func):
    """환급 완료 처리"""
    try:
        update_data = {
            'id': expense_id,
            'reimbursement_status': 'completed',
            'reimbursed_at': datetime.now().isoformat(),
            'reimbursed_by': user_id,
            'updated_at': datetime.now().isoformat()
        }
        return update_data_func("expenses", update_data, "id")
    except Exception as e:
        st.error(f"환급 완료 처리 중 오류: {str(e)}")
        return False


def render_reimbursement_completed(load_data_func, get_current_user_func):
    """최종 완료 내역"""
    
    st.subheader("✅ 최종 완료 내역")
    
    # 데이터 로드
    all_expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not all_expenses or not employees:
        st.info("데이터를 불러올 수 없습니다.")
        return
    
    # 직원 딕셔너리
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
    # 최종 완료 항목 필터링
    completed_expenses = [exp for exp in all_expenses 
                         if exp.get('reimbursement_status') == 'completed']
    
    if not completed_expenses:
        st.info("최종 완료된 내역이 없습니다.")
        return
    
    # 정렬 옵션
    sort_option = st.selectbox("정렬", ["최신순", "오래된순", "금액높은순"], key="completed_sort")
    
    if sort_option == "최신순":
        completed_expenses.sort(key=lambda x: x.get('reimbursed_at', ''), reverse=True)
    elif sort_option == "오래된순":
        completed_expenses.sort(key=lambda x: x.get('reimbursed_at', ''))
    elif sort_option == "금액높은순":
        completed_expenses.sort(key=lambda x: x.get('amount', 0), reverse=True)
    
    st.write(f"💚 총 {len(completed_expenses)}건의 최종 완료")
    
    # DataFrame으로 표시
    table_data = []
    for exp in completed_expenses:
        requester_id = exp.get('requester')
        emp_info = employee_dict.get(requester_id, {})
        emp_name = emp_info.get('name', '알 수 없음')
        
        reimbursed_by_id = exp.get('reimbursed_by')
        reimbursed_by_info = employee_dict.get(reimbursed_by_id, {})
        reimbursed_by_name = reimbursed_by_info.get('name', '알 수 없음')
        
        reimbursed_at = exp.get('reimbursed_at', 'N/A')
        if reimbursed_at != 'N/A':
            try:
                dt = datetime.fromisoformat(str(reimbursed_at).replace('Z', '+00:00'))
                reimbursed_at = dt.strftime('%Y-%m-%d')
            except:
                pass
        
        table_data.append({
            '문서번호': exp.get('reimbursement_document_number', 'N/A'),
            '수령인': emp_name,
            '지출일': exp.get('expense_date', 'N/A'),
            '내역': exp.get('description', '')[:30],
            '금액': f"{exp.get('amount', 0):,.0f}",
            '통화': exp.get('currency', 'VND'),
            '완료일': reimbursed_at,
            '처리자': reimbursed_by_name
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, height=400)
        
        # CSV 다운로드
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv_data,
            file_name=f"reimbursement_completed_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


