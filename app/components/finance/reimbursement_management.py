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
    
    # 지출/환급은 법인 분리 없이 공통 테이블 사용
    expense_table = 'expenses'
    
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

    # 탭 구성 (2개로 변경)
    tab1, tab2 = st.tabs(["📝 환급 대상", "📋 환급 목록"])

    with tab1:
        render_reimbursement_pending(load_data_func, update_data_func, get_current_user_func, expense_table)

    with tab2:
        render_reimbursement_printed(load_data_func, update_data_func, get_current_user_func, expense_table)

def render_reimbursement_pending(load_data_func, update_data_func, get_current_user_func, expense_table):
    """환급 대상 목록 - 테이블 UI"""
    
    st.subheader("📋 환급 대상 목록")
    
    # 법인별 테이블에서 데이터 로드
    all_expenses = load_data_func(expense_table)
    employees = load_data_func("employees")
    
    if not all_expenses or not employees:
        st.info("데이터를 불러올 수 없습니다.")
        return
    
    # 직원 딕셔너리
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
      # 환급 대상: 화던 확인 완료 + 개인돈 사용 + 환급 대기중
    pending_expenses = [exp for exp in all_expenses 
                    if exp.get('accounting_confirmed', False) == True
                    and exp.get('payment_method') not in ['법인카드', '법인계좌']
                    and (exp.get('reimbursement_status') is None 
                            or exp.get('reimbursement_status') == 'pending')]
    
    if not pending_expenses:
        st.info("환급 대상 지출요청서가 없습니다.")
        return
    
    st.write(f"💳 총 {len(pending_expenses)}건의 환급 대상")
    
    # 테이블 데이터 생성
    table_data = []
    for exp in pending_expenses:
        requester_id = exp.get('requester')
        emp_info = employee_dict.get(requester_id, {})
        emp_name = emp_info.get('name', '알 수 없음')
        
        # 화던 상태 표시
        hoadon_status = "✅" if exp.get('accounting_confirmed') else "⏳"
        
        # 환급 상태 표시
        reimbursement_status = exp.get('reimbursement_status', 'pending')
        status_map = {
            'pending': '대기',
            'printed': '환급완료',
            'completed': '최종완료',
            'not_required': '환급불필요'
        }
        status_display = status_map.get(reimbursement_status, reimbursement_status)
        
        table_data.append({
            'ID': exp.get('id'),
            '지출요청서번호': exp.get('document_number', 'N/A'),
            '요청자': emp_name,
            '지출일': exp.get('expense_date', 'N/A'),
            '유형': exp.get('expense_type', 'N/A'),
            '금액': f"{exp.get('amount', 0):,.0f}",
            '통화': exp.get('currency', 'VND'),
            '환급상태': status_display,
            '화던(Hóa đơn)': hoadon_status,
            '결제방법': exp.get('payment_method', 'N/A')
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        
        # 선택 가능한 테이블
        st.dataframe(df, use_container_width=True, height=400, hide_index=True)
        
        # 선택 입력
        st.markdown("---")
        selected_ids_input = st.text_input(
            "환급 처리할 ID (쉼표로 구분)", 
            placeholder="예: 112, 113, 114",
            key="selected_reimbursement_ids"
        )
        
        if selected_ids_input:
            try:
                selected_ids = [int(id.strip()) for id in selected_ids_input.split(',')]
                selected_expenses = [exp for exp in pending_expenses if exp.get('id') in selected_ids]
                
                if selected_expenses:
                    # 통화별 합계
                    currency_totals = defaultdict(float)
                    for exp in selected_expenses:
                        currency = exp.get('currency', 'VND')
                        amount = exp.get('amount', 0)
                        currency_totals[currency] += amount
                    
                    total_str = ", ".join([f"{amount:,.0f} {curr}" for curr, amount in currency_totals.items()])
                    
                    st.info(f"선택된 항목: {len(selected_expenses)}건 - {total_str}")
                    
                    # 환급 대상자 선택
                    st.markdown("---")
                    st.markdown("### 👤 환급 대상자 선택")
                    
                    # 직원 목록
                    active_employees = [emp for emp in employees if emp.get('employment_status') == 'active']
                    employee_options = {
                        f"{emp.get('name', 'N/A')} ({emp.get('employee_id', 'N/A')})": emp.get('id')
                        for emp in active_employees
                    }
                    
                    # 기본값: 첫 번째 선택 항목의 요청자
                    default_requester_id = selected_expenses[0].get('requester')
                    default_requester_info = employee_dict.get(default_requester_id, {})
                    default_display = f"{default_requester_info.get('name', 'N/A')} ({default_requester_info.get('employee_id', 'N/A')})"
                    
                    # 기본값 인덱스 찾기
                    default_index = 0
                    if default_display in employee_options:
                        default_index = list(employee_options.keys()).index(default_display)
                    
                    selected_recipient_display = st.selectbox(
                        "환급 받을 사람",
                        options=list(employee_options.keys()),
                        index=default_index,
                        key="reimbursement_recipient_select"
                    )
                    selected_recipient_id = employee_options[selected_recipient_display]
                    
                    st.caption(f"💡 기본값: 요청자 ({default_display})")
                    
                    # 2개 버튼: 프린트 / 환급 완료 처리
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button(f"🖨️ 환급 프린트 ({len(selected_expenses)}건)", type="secondary", use_container_width=True):
                            # 문서번호 생성 (상태 변경 없이)
                            from components.system.document_number import generate_document_number
                            document_number = generate_document_number('PAY', load_func=load_data_func)
                            
                            # 통화별 그룹핑
                            grouped_by_currency = defaultdict(list)
                            for exp in selected_expenses:
                                currency = exp.get('currency', 'VND')
                                grouped_by_currency[currency].append(exp)
                            
                            # 프린트 데이터 저장 (상태 변경 없음)
                            st.session_state['print_reimbursement'] = {
                                'employee_id': selected_recipient_id,
                                'grouped_expenses': dict(grouped_by_currency),
                                'document_number': document_number,
                                'is_preview': True  # 미리보기 모드
                            }
                            st.success(f"✅ 프린트 준비 완료! 문서번호: {document_number}")
                            st.rerun()
                    
                    with col_btn2:
                        if st.button(f"✅ 환급 완료 처리 ({len(selected_expenses)}건)", type="primary", use_container_width=True):
                            # 문서번호 생성
                            from components.system.document_number import generate_document_number
                            document_number = generate_document_number('PAY', load_func=load_data_func)
                            
                            # 상태를 printed로 변경
                            success_count = 0
                            for exp in selected_expenses:
                                result = update_data_func(expense_table, {
                                    'id': exp.get('id'),
                                    'reimbursement_status': 'printed',
                                    'reimbursement_document_number': document_number,
                                    'reimbursement_recipient': selected_recipient_id,
                                    'updated_at': datetime.now().isoformat()
                                }, "id")
                                
                                if result:
                                    success_count += 1
                            
                            if success_count == len(selected_expenses):
                                st.success(f"✅ {success_count}건 환급 완료 처리! 문서번호: {document_number}")
                                st.rerun()
                            else:
                                st.error(f"⚠️ {success_count}/{len(selected_expenses)}건만 처리되었습니다.")
                else:
                    st.warning("⚠️ 선택한 ID가 환급 대상 목록에 없습니다.")
            except ValueError:
                st.error("⚠️ ID는 숫자로 입력해주세요.")

def render_reimbursement_printed(load_data_func, update_data_func, get_current_user_func, expense_table):
    """프린트 완료 목록 - 테이블 형식"""
    
    st.subheader("🖨️ 프린트 완료 목록")
    
    # 법인별 테이블에서 데이터 로드
    all_expenses = load_data_func(expense_table)
    employees = load_data_func("employees")
    
    if not all_expenses or not employees:
        st.info("데이터를 불러올 수 없습니다.")
        return
    
    # 직원 딕셔너리
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
    # 환급 완료 항목 필터링 (printed 상태만)
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
    
    # 테이블 데이터 생성
    table_data = []
    for exp in printed_expenses:  # ← 수정!
        requester_id = exp.get('requester')
        emp_info = employee_dict.get(requester_id, {})
        emp_name = emp_info.get('name', '알 수 없음')
        
        # 환급대상자
        recipient_id = exp.get('reimbursement_recipient')
        if recipient_id:
            recipient_info = employee_dict.get(recipient_id, {})
            recipient_name = recipient_info.get('name', '알 수 없음')
        else:
            recipient_name = '-'
        
        # 프린트일 추출
        updated_at = exp.get('updated_at', 'N/A')
        if updated_at != 'N/A':
            try:
                dt = datetime.fromisoformat(str(updated_at).replace('Z', '+00:00'))
                updated_at = dt.strftime('%Y-%m-%d')
            except:
                pass
        
        table_data.append({
            'ID': exp.get('id'),
            '환급문서번호': exp.get('reimbursement_document_number', 'N/A'),
            '지출요청서번호': exp.get('document_number', 'N/A'),
            '요청자': emp_name,
            '환급대상자': recipient_name,
            '지출일': exp.get('expense_date', 'N/A'),
            '유형': exp.get('expense_type', 'N/A'),
            '금액': f"{exp.get('amount', 0):,.0f}",
            '통화': exp.get('currency', 'VND'),
            '프린트일': updated_at
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, height=400, hide_index=True)
        
        # 재출력 기능
        st.markdown("---")
        st.info("💡 환급 문서를 재출력하려면 환급문서번호를 입력하세요.")
        
        reprint_doc_number = st.text_input(
            "재출력할 환급문서번호",
            placeholder="예: PAY-251001-001",
            key="reprint_doc_number"
        )
        
        if reprint_doc_number:
            # 해당 문서번호의 지출 항목 찾기
            doc_expenses = [exp for exp in printed_expenses 
                          if exp.get('reimbursement_document_number') == reprint_doc_number]
            
            if doc_expenses:
                # 통화별 합계
                currency_totals = defaultdict(float)
                for exp in doc_expenses:
                    currency = exp.get('currency', 'VND')
                    amount = exp.get('amount', 0)
                    currency_totals[currency] += amount
                
                total_str = ", ".join([f"{amount:,.0f} {curr}" for curr, amount in currency_totals.items()])
                
                st.success(f"✅ 선택된 문서: {reprint_doc_number} - {len(doc_expenses)}건 - {total_str}")
                
                if st.button(f"🖨️ 재출력", type="primary", use_container_width=True):
                    # 통화별 그룹핑
                    grouped_by_currency = defaultdict(list)
                    for exp in doc_expenses:
                        currency = exp.get('currency', 'VND')
                        grouped_by_currency[currency].append(exp)
                    
                    # 환급대상자 ID 추출
                    recipient_id = doc_expenses[0].get('reimbursement_recipient')
                    
                    # 프린트 데이터 저장
                    st.session_state['print_reimbursement'] = {
                        'employee_id': recipient_id,  # ← 환급대상자로 수정
                        'grouped_expenses': dict(grouped_by_currency),
                        'document_number': reprint_doc_number
                    }
                    st.success(f"✅ 재출력 준비 완료!")
                    st.rerun()
            else:
                st.warning("⚠️ 해당 환급문서번호를 찾을 수 없습니다.")

def complete_reimbursement(expense_id, user_id, update_data_func, expense_table):
    """환급 완료 처리 - printed → completed"""
    try:
        update_data = {
            'id': expense_id,
            'reimbursement_status': 'completed',
            'reimbursed_at': datetime.now().isoformat(),
            'reimbursed_by': user_id,
            'updated_at': datetime.now().isoformat()
        }
        return update_data_func(expense_table, update_data, "id")
    except Exception as e:
        st.error(f"환급 완료 처리 중 오류: {str(e)}")
        return False


def render_reimbursement_completed(load_data_func, get_current_user_func, expense_table):
    """최종 완료 내역 - 월별/주별/항목별 필터"""
    
    st.subheader("✅ 최종 완료 내역")
    
    # 법인별 테이블에서 데이터 로드
    all_expenses = load_data_func(expense_table)
    employees = load_data_func("employees")
    
    if not all_expenses or not employees:
        st.info("데이터를 불러올 수 없습니다.")
        return
    
    # 직원 딕셔너리
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
    # 최종 완료 항목 필터링 (completed 상태만)
    completed_expenses = [exp for exp in all_expenses 
                         if exp.get('reimbursement_status') == 'completed']
    
    if not completed_expenses:
        st.info("최종 완료된 내역이 없습니다.")
        return
    
    # 필터 영역
    st.markdown("### 🔍 필터")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 월별 필터
        available_months = set()
        for exp in completed_expenses:
            reimbursed_at = exp.get('reimbursed_at')
            if reimbursed_at:
                try:
                    dt = datetime.fromisoformat(str(reimbursed_at).replace('Z', '+00:00'))
                    available_months.add(dt.strftime('%Y-%m'))
                except:
                    pass
        
        month_options = ["전체"] + sorted(list(available_months), reverse=True)
        selected_month = st.selectbox("월 선택", month_options, key="month_filter")
    
    with col2:
        # 주별 필터 (ISO 주)
        week_options = ["전체", "최근 1주", "최근 2주", "최근 4주"]
        selected_week = st.selectbox("기간 선택", week_options, key="week_filter")
    
    with col3:
        # 지출 유형 필터
        expense_types = set([exp.get('expense_type', '기타') for exp in completed_expenses])
        type_options = ["전체"] + sorted(list(expense_types))
        selected_type = st.selectbox("지출 유형", type_options, key="type_filter")
    
    # 필터링 적용
    filtered_expenses = completed_expenses.copy()
    
    # 월별 필터
    if selected_month != "전체":
        filtered_expenses = [exp for exp in filtered_expenses 
                           if exp.get('reimbursed_at') and 
                           datetime.fromisoformat(str(exp.get('reimbursed_at')).replace('Z', '+00:00')).strftime('%Y-%m') == selected_month]
    
    # 주별 필터
    if selected_week != "전체":
        from datetime import timedelta
        now = datetime.now()
        
        if selected_week == "최근 1주":
            cutoff_date = now - timedelta(days=7)
        elif selected_week == "최근 2주":
            cutoff_date = now - timedelta(days=14)
        elif selected_week == "최근 4주":
            cutoff_date = now - timedelta(days=28)
        
        filtered_expenses = [exp for exp in filtered_expenses 
                           if exp.get('reimbursed_at') and 
                           datetime.fromisoformat(str(exp.get('reimbursed_at')).replace('Z', '+00:00')) >= cutoff_date]
    
    # 지출 유형 필터
    if selected_type != "전체":
        filtered_expenses = [exp for exp in filtered_expenses 
                           if exp.get('expense_type') == selected_type]
    
    if not filtered_expenses:
        st.info("필터 조건에 맞는 데이터가 없습니다.")
        return
    
    # 통계 대시보드
    st.markdown("### 📊 통계")
    
    # 통화별 합계 계산
    currency_totals = defaultdict(float)
    for exp in filtered_expenses:
        currency = exp.get('currency', 'VND')
        amount = exp.get('amount', 0)
        currency_totals[currency] += amount
    
    # 지출 유형별 집계
    type_stats = defaultdict(lambda: {'count': 0, 'amount': 0})
    for exp in filtered_expenses:
        exp_type = exp.get('expense_type', '기타')
        type_stats[exp_type]['count'] += 1
        type_stats[exp_type]['amount'] += exp.get('amount', 0)
    
    # 통계 표시
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    
    with stat_col1:
        st.metric("총 건수", f"{len(filtered_expenses)}건")
    
    with stat_col2:
        total_vnd = currency_totals.get('VND', 0)
        st.metric("총 금액 (VND)", f"{total_vnd:,.0f}")
    
    with stat_col3:
        if 'USD' in currency_totals or 'KRW' in currency_totals:
            other_currencies = ", ".join([f"{curr}: {amt:,.0f}" for curr, amt in currency_totals.items() if curr != 'VND'])
            st.metric("기타 통화", other_currencies if other_currencies else "-")
        else:
            st.metric("평균 금액", f"{total_vnd / len(filtered_expenses):,.0f}" if len(filtered_expenses) > 0 else "0")
    
    # 지출 유형별 통계
    if type_stats:
        st.markdown("#### 📈 지출 유형별 집계")
        type_data = []
        for exp_type, stats in sorted(type_stats.items(), key=lambda x: x[1]['amount'], reverse=True):
            type_data.append({
                '지출 유형': exp_type,
                '건수': stats['count'],
                '금액': f"{stats['amount']:,.0f}"
            })
        
        if type_data:
            type_df = pd.DataFrame(type_data)
            st.dataframe(type_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 정렬 옵션
    sort_option = st.selectbox("정렬", ["최신순", "오래된순", "금액높은순"], key="completed_sort")
    
    if sort_option == "최신순":
        filtered_expenses.sort(key=lambda x: x.get('reimbursed_at', ''), reverse=True)
    elif sort_option == "오래된순":
        filtered_expenses.sort(key=lambda x: x.get('reimbursed_at', ''))
    elif sort_option == "금액높은순":
        filtered_expenses.sort(key=lambda x: x.get('amount', 0), reverse=True)
    
    st.write(f"💚 {len(filtered_expenses)}건의 환급 완료 내역")
    
    # 테이블 데이터 생성
    table_data = []
    for exp in filtered_expenses:
        requester_id = exp.get('requester')
        emp_info = employee_dict.get(requester_id, {})
        emp_name = emp_info.get('name', '알 수 없음')
        
        # 환급일 추출
        reimbursed_at = exp.get('reimbursed_at', 'N/A')
        if reimbursed_at != 'N/A':
            try:
                dt = datetime.fromisoformat(str(reimbursed_at).replace('Z', '+00:00'))
                reimbursed_at = dt.strftime('%Y-%m-%d')
            except:
                pass
        
        table_data.append({
            'ID': exp.get('id'),
            '환급문서번호': exp.get('reimbursement_document_number', 'N/A'),
            '지출요청서번호': exp.get('document_number', 'N/A'),
            '요청자': emp_name,
            '지출일': exp.get('expense_date', 'N/A'),
            '유형': exp.get('expense_type', 'N/A'),
            '금액': f"{exp.get('amount', 0):,.0f}",
            '통화': exp.get('currency', 'VND'),
            '환급일': reimbursed_at
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, height=400, hide_index=True)
        
        # CSV 다운로드
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv_data,
            file_name=f"reimbursement_completed_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )