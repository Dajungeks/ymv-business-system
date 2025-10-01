import streamlit as st
import pandas as pd
from datetime import datetime

def show_accounting_management():
    """회계 확인 관리 메인 함수"""
    
    st.subheader("📊 회계 완료 리스트")
    
    # 현재 사용자 정보는 세션 상태나 매개변수로 받아옴
    # 직접 데이터 조회는 하지 않고, 상위에서 전달받은 함수 사용
    st.info("회계 확인 기능은 지출 요청서 관리의 '회계 확인' 탭에서 사용하실 수 있습니다.")
    st.info("이 페이지는 독립적인 회계 확인 관리 페이지입니다.")
    
    # 간단한 안내 메시지
    st.write("""
    ### 회계 확인 프로세스
    1. **승인 완료**: CEO/Master가 지출요청서 승인
    2. **회계 확인 대기**: 승인된 항목이 회계 확인 대기 상태
    3. **회계 확인**: Admin/CEO/Master가 회계 확인 수행
    4. **최종 완료**: 회계 확인 완료 후 완료 리스트에 표시
    
    ### 접근 방법
    - **지출 요청서 > 회계 확인** 탭에서 회계 확인 수행
    - **지출 요청서 > 지출요청서 목록**에서 회계 확인 상태 확인
    """)

def render_accounting_table(expenses, employee_dict, export_format):
    """회계 완료 리스트를 엑셀 형식 테이블로 표시"""
    
    # DataFrame 생성을 위한 데이터 준비
    table_data = []
    
    for expense in expenses:
        # 직원 정보
        requester_id = expense.get('requester')
        employee_info = employee_dict.get(requester_id, {})
        employee_name = employee_info.get('name', '알 수 없음')
        employee_id = employee_info.get('employee_id', f"ID{requester_id}")
        
        # 승인자 정보
        approved_by_id = expense.get('approved_by')
        approver_info = employee_dict.get(approved_by_id, {})
        approver_name = approver_info.get('name', '알 수 없음') if approved_by_id else 'N/A'
        
        # 회계 확인자 정보
        accounting_confirmed_by_id = expense.get('accounting_confirmed_by')
        accounting_confirmer_info = employee_dict.get(accounting_confirmed_by_id, {})
        accounting_confirmer_name = accounting_confirmer_info.get('name', '알 수 없음') if accounting_confirmed_by_id else 'N/A'
        
        # 날짜 포맷팅
        expense_date = expense.get('expense_date', 'N/A')
        approved_at = 'N/A'
        if expense.get('approved_at'):
            try:
                dt = datetime.fromisoformat(str(expense['approved_at']).replace('Z', '+00:00'))
                approved_at = dt.strftime('%Y-%m-%d')
            except:
                approved_at = str(expense['approved_at'])[:10]
        
        accounting_confirmed_at = 'N/A'
        if expense.get('accounting_confirmed_at'):
            try:
                dt = datetime.fromisoformat(str(expense['accounting_confirmed_at']).replace('Z', '+00:00'))
                accounting_confirmed_at = dt.strftime('%Y-%m-%d')
            except:
                accounting_confirmed_at = str(expense['accounting_confirmed_at'])[:10]
        
        table_data.append({
            '문서번호': expense.get('document_number', 'N/A'),
            '지출일': expense_date,
            '지출유형': expense.get('expense_type', '기타'),
            '요청자': f"{employee_name}({employee_id})",
            '부서': expense.get('department', 'N/A'),
            '금액': f"{expense.get('amount', 0):,}",
            '통화': expense.get('currency', 'VND'),
            '결제방법': expense.get('payment_method', 'N/A'),
            '지출내역': expense.get('description', 'N/A'),
            '사업목적': expense.get('business_purpose', 'N/A'),
            '공급업체': expense.get('vendor', 'N/A'),
            '영수증번호': expense.get('receipt_number', 'N/A'),
            '승인일': approved_at,
            '승인자': approver_name,
            '회계확인일': accounting_confirmed_at,
            '회계확인자': accounting_confirmer_name,
            '처리의견': expense.get('approval_comment', 'N/A')
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        
        # 테이블 표시
        st.dataframe(df, use_container_width=True, height=400)
        
        # 다운로드 버튼
        if export_format == "Excel 형식":
            # Excel 파일 생성
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='회계완료리스트')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Excel 다운로드",
                data=excel_data,
                file_name=f"회계완료리스트_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        else:  # CSV 형식
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=f"회계완료리스트_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

def show_accounting_management_with_data(load_data_func, update_data_func, get_current_user_func):
    """데이터 로드 함수를 받아서 회계 확인 관리 수행 (실제 기능)"""
    
    current_user = get_current_user_func()
    user_role = current_user.get('role', 'Staff') if current_user else 'Staff'
    
    # 권한 체크: Admin, CEO, Master만 접근 가능
    if user_role not in ['Admin', 'CEO', 'Master']:
        st.warning("⚠️ 회계 확인 권한이 없습니다.")
        return
    
    st.subheader("📊 회계 완료 리스트")
    
    # 데이터 조회
    all_expenses = load_data_func("expenses")
    employees = load_data_func("employees")
    
    if not employees:
        st.error("직원 정보를 불러올 수 없습니다.")
        return
    
    if not all_expenses:
        st.info("지출요청서 데이터가 없습니다.")
        return
    
    # 회계 확인 완료된 항목만 필터링
    completed_expenses = [exp for exp in all_expenses 
                         if exp.get('accounting_confirmed', False)]
    
    # 직원 정보를 딕셔너리로 변환
    employee_dict = {}
    for emp in employees:
        emp_id = emp.get('id')
        if emp_id:
            employee_dict[emp_id] = emp
    
    if not completed_expenses:
        st.info("회계 확인이 완료된 지출요청서가 없습니다.")
        return
    
    # 정렬 옵션
    col1, col2 = st.columns(2)
    with col1:
        sort_option = st.selectbox(
            "정렬 기준",
            ["회계확인일순", "지출일순", "금액높은순", "금액낮은순"],
            key="accounting_sort"
        )
    
    with col2:
        export_format = st.selectbox(
            "내보내기 형식",
            ["Excel 형식", "CSV 형식"],
            key="export_format"
        )
    
    # 정렬 처리
    if sort_option == "회계확인일순":
        completed_expenses.sort(key=lambda x: x.get('accounting_confirmed_at', ''), reverse=True)
    elif sort_option == "지출일순":
        completed_expenses.sort(key=lambda x: x.get('expense_date', ''), reverse=True)
    elif sort_option == "금액높은순":
        completed_expenses.sort(key=lambda x: x.get('amount', 0), reverse=True)
    elif sort_option == "금액낮은순":
        completed_expenses.sort(key=lambda x: x.get('amount', 0))
    
    st.write(f"📋 총 {len(completed_expenses)}건의 회계 확인 완료 건")
    
    # 엑셀 형식 테이블 (DataFrame으로 표시)
    render_accounting_table(completed_expenses, employee_dict, export_format)

def confirm_accounting_with_data(expense_id, user_id, update_data_func):
    """데이터 업데이트 함수를 받아서 회계 확인 처리"""
    try:
        update_data = {
            'id': expense_id,
            'accounting_confirmed': True,
            'accounting_confirmed_by': user_id,
            'accounting_confirmed_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        return update_data_func("expenses", update_data, "id")
    except Exception as e:
        st.error(f"회계 확인 처리 중 오류: {str(e)}")
        return False