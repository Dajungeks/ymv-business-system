"""
구매품 관리 컴포넌트 (승인 기능 포함)
Operations - Purchase Management Component with Approval
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime, date

def show_purchase_management(load_func, save_func, update_func, delete_func, current_user):
    """구매품 관리 메인 함수"""
    st.title("🛒 구매품 관리")
    
    user_role = current_user.get('role', 'Staff') if current_user else 'Staff'
    
    # 탭 구성 - CEO, Master만 승인 탭 추가
    if user_role in ['CEO', 'Master']:
        tab1, tab2, tab3 = st.tabs(["📝 구매 요청 등록", "✅ 승인 관리", "📋 구매 요청 목록"])
        
        with tab1:
            render_purchase_form(current_user, save_func)
        
        with tab2:
            render_approval_management(current_user, load_func, update_func, save_func)
        
        with tab3:
            render_purchase_list(current_user, user_role, load_func, update_func, delete_func)
    else:
        tab1, tab2 = st.tabs(["📝 구매 요청 등록", "📋 구매 요청 목록"])
        
        with tab1:
            render_purchase_form(current_user, save_func)
        
        with tab2:
            render_purchase_list(current_user, user_role, load_func, update_func, delete_func)

def render_purchase_form(current_user, save_func):
    """구매 요청 등록 폼"""
    st.subheader("📝 구매 요청 등록")
    
    with st.form("purchase_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox("카테고리", ["사무용품", "전자제품", "가구", "소모품", "기타"])
            item_name = st.text_input("품목명 *")
            quantity = st.number_input("수량", min_value=1, value=1, step=1)
            unit = st.selectbox("단위", ["개", "박스", "세트", "kg", "L"])
        
        with col2:
            currency = st.selectbox("통화", ["KRW", "USD", "VND"])
            currency_steps = {"USD": 10, "VND": 10000, "KRW": 1000}
            step = currency_steps.get(currency, 1000)
            
            unit_price = st.number_input("단가 *", min_value=0.0, value=0.0, step=float(step))
            supplier = st.text_input("공급업체 *")
            request_date = st.date_input("요청일", value=st.session_state.get('today', date.today()))
            urgency = st.selectbox("긴급도", ["낮음", "보통", "높음", "긴급"], index=1)
        
        notes = st.text_area("비고")
        submitted = st.form_submit_button("📝 구매 요청 등록", type="primary")
        
        if submitted:
            if not item_name.strip():
                st.error("품목명을 입력해주세요.")
            elif not supplier.strip():
                st.error("공급업체를 입력해주세요.")
            elif unit_price <= 0:
                st.error("단가를 입력해주세요.")
            else:
                purchase_data = {
                    "category": category,
                    "item_name": item_name,
                    "quantity": quantity,
                    "unit": unit,
                    "unit_price": unit_price,
                    "currency": currency,
                    "supplier": supplier,
                    "request_date": request_date.isoformat(),
                    "urgency": urgency,
                    "status": "대기중",
                    "approval_status": "승인대기",
                    "notes": notes if notes.strip() else None,
                    "requester": current_user['id'],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                if save_func("purchases", purchase_data):
                    st.success("✅ 구매 요청이 등록되었습니다! 승인 대기 중입니다.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 구매 요청 등록에 실패했습니다.")

def render_approval_management(current_user, load_func, update_func, save_func):
    """승인 관리 (CEO, Master만) - 테이블 형식"""
    st.subheader("✅ 구매 요청 승인 관리")
    
    purchases = load_func("purchases") or []
    employees = load_func("employees") or []
    
    # 승인 대기 중인 항목만 필터링
    pending_purchases = [p for p in purchases if p.get('approval_status') == '승인대기']
    
    if not pending_purchases:
        st.info("승인 대기 중인 구매 요청이 없습니다.")
        return
    
    st.write(f"📋 총 {len(pending_purchases)}건의 승인 대기")
    
    # 직원 딕셔너리
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
    # 테이블 데이터 생성
    table_data = []
    for purchase in pending_purchases:
        requester_id = purchase.get('requester')
        emp_info = employee_dict.get(requester_id, {})
        emp_name = emp_info.get('name', '알 수 없음')
        
        total_price = purchase.get('unit_price', 0) * purchase.get('quantity', 1)
        
        table_data.append({
            'ID': purchase.get('id'),
            '요청자': emp_name,
            '카테고리': purchase.get('category', 'N/A'),
            '품목명': purchase.get('item_name', 'N/A'),
            '수량': f"{purchase.get('quantity', 0)} {purchase.get('unit', '개')}",
            '단가': f"{purchase.get('unit_price', 0):,.0f}",
            '총액': f"{total_price:,.0f}",
            '통화': purchase.get('currency', 'KRW'),
            '공급업체': purchase.get('supplier', 'N/A'),
            '요청일': purchase.get('request_date', 'N/A'),
            '긴급도': purchase.get('urgency', '보통')
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, height=400, hide_index=True)
        
        # 승인/반려 처리
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ 승인")
            approve_ids_input = st.text_input(
                "승인할 ID (쉼표로 구분)",
                placeholder="예: 15, 14, 7",
                key="approve_ids"
            )
            
            if approve_ids_input:
                try:
                    approve_ids = [int(id.strip()) for id in approve_ids_input.split(',')]
                    selected_purchases = [p for p in pending_purchases if p.get('id') in approve_ids]
                    
                    if selected_purchases:
                        # 통화별 합계
                        currency_totals = {}
                        for p in selected_purchases:
                            currency = p.get('currency', 'KRW')
                            total = p.get('unit_price', 0) * p.get('quantity', 1)
                            currency_totals[currency] = currency_totals.get(currency, 0) + total
                        
                        total_str = ", ".join([f"{amount:,.0f} {curr}" for curr, amount in currency_totals.items()])
                        
                        st.info(f"선택된 항목: {len(selected_purchases)}건 - {total_str}")
                        
                        if st.button(f"✅ 승인 처리 ({len(selected_purchases)}건)", type="primary", use_container_width=True):
                            success_count = 0
                            
                            for purchase in selected_purchases:
                                if approve_purchase(purchase, current_user, update_func, save_func, load_func, employee_dict):
                                    success_count += 1
                            
                            if success_count == len(selected_purchases):
                                st.success(f"✅ {len(selected_purchases)}건 승인 완료 및 지출요청서 생성!")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.warning(f"⚠️ {success_count}/{len(selected_purchases)}건만 처리되었습니다.")
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
                key="reject_ids"
            )
            
            reject_reason = st.text_input("반려 사유 *", key="reject_reason")
            
            if reject_ids_input:
                try:
                    reject_ids = [int(id.strip()) for id in reject_ids_input.split(',')]
                    selected_purchases = [p for p in pending_purchases if p.get('id') in reject_ids]
                    
                    if selected_purchases:
                        st.info(f"선택된 항목: {len(selected_purchases)}건")
                        
                        if st.button(f"❌ 반려 처리 ({len(selected_purchases)}건)", type="secondary", use_container_width=True):
                            if not reject_reason.strip():
                                st.error("반려 사유를 입력해주세요.")
                            else:
                                success_count = 0
                                
                                for purchase in selected_purchases:
                                    update_data = {
                                        'id': purchase.get('id'),
                                        'approval_status': '반려',
                                        'approver_id': current_user['id'],
                                        'approved_at': datetime.now().isoformat(),
                                        'rejected_reason': reject_reason,
                                        'status': '반려',
                                        'updated_at': datetime.now().isoformat()
                                    }
                                    
                                    if update_func("purchases", update_data, "id"):
                                        success_count += 1
                                
                                if success_count == len(selected_purchases):
                                    st.success(f"✅ {len(selected_purchases)}건 반려 완료!")
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.warning(f"⚠️ {success_count}/{len(selected_purchases)}건만 반려되었습니다.")
                                    time.sleep(2)
                                    st.rerun()
                    else:
                        st.warning("⚠️ 선택한 ID가 승인 대기 목록에 없습니다.")
                except ValueError:
                    st.error("⚠️ ID는 숫자로 입력해주세요.")

def approve_purchase(purchase, current_user, update_func, save_func, load_func, employee_dict):
    """구매 요청 승인 + 지출요청서 자동 생성"""
    try:
        # 1. 구매 요청 승인 처리
        total_amount = purchase.get('unit_price', 0) * purchase.get('quantity', 1)
        
        # 2. 지출요청서 문서번호 생성 (순차번호)
        today = datetime.now()
        date_prefix = f"EXP-{today.strftime('%y%m%d')}"
        
        # 오늘 날짜의 기존 문서번호 조회
        all_expenses = load_func("expenses") or []
        today_expenses = [exp for exp in all_expenses if exp.get('document_number', '').startswith(date_prefix)]
        
        # 다음 순차번호 계산
        if today_expenses:
            existing_numbers = []
            for exp in today_expenses:
                doc_num = exp.get('document_number', '')
                if '-' in doc_num:
                    try:
                        seq = int(doc_num.split('-')[-1])
                        existing_numbers.append(seq)
                    except:
                        pass
            next_seq = max(existing_numbers) + 1 if existing_numbers else 1
        else:
            next_seq = 1
        
        doc_number = f"{date_prefix}-{next_seq:03d}"
        
        # 3. 지출요청서 생성
        expense_data = {
            'document_number': doc_number,
            'expense_type': f"구매품-{purchase.get('category', '기타')}",
            'description': f"{purchase.get('item_name', '')} ({purchase.get('quantity', 0)}{purchase.get('unit', '개')}) - {purchase.get('supplier', '')}",
            'amount': total_amount,
            'currency': purchase.get('currency', 'KRW'),
            'expense_date': purchase.get('request_date', date.today().isoformat()),
            'payment_method': '미정',
            'receipt_required': True,
            'notes': f"구매요청서 ID: {purchase.get('id')} | {purchase.get('notes', '')}",
            'requester': purchase.get('requester'),
            'approval_status': 'pending',
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # expenses 테이블에 저장
        expense_result = save_func("expenses", expense_data)
        
        if expense_result:
            # 저장된 expense ID 조회 (방금 생성된 문서번호로)
            all_expenses_updated = load_func("expenses") or []
            created_expense = next((exp for exp in all_expenses_updated 
                                  if exp.get('document_number') == doc_number), None)
            
            expense_id = created_expense.get('id') if created_expense else None
            
            # 4. 구매 요청 업데이트 (expense_id 포함)
            purchase_update = {
                'id': purchase.get('id'),
                'approval_status': '승인완료',
                'approver_id': current_user['id'],
                'approved_at': datetime.now().isoformat(),
                'status': '승인완료',
                'expense_id': expense_id,  # 연결된 지출요청서 ID
                'updated_at': datetime.now().isoformat()
            }
            
            return update_func("purchases", purchase_update, "id")
        
        return False
        
    except Exception as e:
        st.error(f"승인 처리 중 오류: {str(e)}")
        return False

def render_purchase_list(current_user, user_role, load_func, update_func, delete_func):
    """구매 요청 목록 - 테이블 형식"""
    st.subheader("📋 구매품 목록")
    
    purchases = load_func("purchases") or []
    employees = load_func("employees") or []
    
    if not purchases:
        st.info("등록된 구매품이 없습니다.")
        return
    
    # 권한별 필터링 (Master, CEO, Admin, Manager는 전체 조회)
    if user_role not in ['Master', 'CEO', 'Admin', 'Manager']:
        purchases = [p for p in purchases if p.get('requester') == current_user['id']]
    
    st.write(f"📦 총 {len(purchases)}건의 구매 요청")
    
    # 직원 딕셔너리
    employee_dict = {emp.get('id'): emp for emp in employees if emp.get('id')}
    
    # 테이블 데이터 생성
    table_data = []
    for purchase in purchases:
        requester_id = purchase.get('requester')
        emp_info = employee_dict.get(requester_id, {})
        emp_name = emp_info.get('name', '알 수 없음')
        
        # 승인자 정보
        approver_id = purchase.get('approver_id')
        approver_name = '미승인'
        if approver_id:
            approver_info = employee_dict.get(approver_id, {})
            approver_name = approver_info.get('name', '알 수 없음')
        
        total_price = purchase.get('unit_price', 0) * purchase.get('quantity', 1)
        
        table_data.append({
            'ID': purchase.get('id'),
            '카테고리': purchase.get('category', 'N/A'),
            '품목명': purchase.get('item_name', 'N/A'),
            '수량': f"{purchase.get('quantity', 0)} {purchase.get('unit', '개')}",
            '단가': f"{purchase.get('unit_price', 0):,.0f}",
            '총액': f"{total_price:,.0f}",
            '통화': purchase.get('currency', 'KRW'),
            '공급업체': purchase.get('supplier', 'N/A'),
            '요청자': emp_name,
            '요청일': purchase.get('request_date', 'N/A'),
            '긴급도': purchase.get('urgency', '보통'),
            '승인상태': purchase.get('approval_status', '승인대기'),
            '승인자': approver_name,
            '상태': purchase.get('status', '대기중')
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, height=400, hide_index=True)
        
        # 관리 기능 (권한 있는 사용자만)
        if user_role in ['Master', 'CEO', 'Admin', 'Manager']:
            st.markdown("---")
            st.subheader("🔧 관리 기능")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ✏️ 수정")
                edit_id = st.number_input("수정할 ID", min_value=1, step=1, key="edit_id")
                
                if st.button("수정 폼 열기", key="open_edit"):
                    # 승인 상태 확인
                    purchase_to_edit = next((p for p in purchases if p.get('id') == edit_id), None)
                    
                    if purchase_to_edit:
                        approval_status = purchase_to_edit.get('approval_status', '승인대기')
                        
                        if approval_status == '승인완료':
                            st.error(f"⚠️ 승인완료 상태인 항목은 수정할 수 없습니다.")
                        else:
                            st.session_state['editing_purchase_id'] = edit_id
                            st.rerun()
                    else:
                        st.warning("⚠️ 해당 ID를 찾을 수 없습니다.")
            
            with col2:
                st.markdown("#### 🗑️ 삭제")
                delete_id = st.number_input("삭제할 ID", min_value=1, step=1, key="delete_id")
                
                if st.button("삭제", type="secondary", key="delete_btn"):
                    purchase_to_delete = next((p for p in purchases if p.get('id') == delete_id), None)
                    
                    if purchase_to_delete:
                        approval_status = purchase_to_delete.get('approval_status', '승인대기')
                        
                        if approval_status == '승인완료':
                            st.error(f"⚠️ 승인완료 상태인 항목은 삭제할 수 없습니다.")
                        else:
                            if delete_func("purchases", delete_id):
                                st.success(f"✅ ID {delete_id} 구매품이 삭제되었습니다!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ 삭제에 실패했습니다.")
                    else:
                        st.warning("⚠️ 해당 ID를 찾을 수 없습니다.")
            
            # 수정 폼
            if 'editing_purchase_id' in st.session_state:
                render_purchase_edit_form(st.session_state['editing_purchase_id'], purchases, update_func)

def render_purchase_edit_form(purchase_id, purchases, update_func):
    """구매품 수정 폼"""
    st.markdown("---")
    st.subheader(f"✏️ 구매품 수정 (ID: {purchase_id})")
    
    # 해당 구매품 찾기
    purchase = next((p for p in purchases if p.get('id') == purchase_id), None)
    
    if not purchase:
        st.error("⚠️ 해당 구매품을 찾을 수 없습니다.")
        if st.button("닫기"):
            del st.session_state['editing_purchase_id']
            st.rerun()
        return
    
    with st.form(f"edit_purchase_form_{purchase_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox("카테고리", 
                                   ["사무용품", "전자제품", "가구", "소모품", "기타"],
                                   index=["사무용품", "전자제품", "가구", "소모품", "기타"].index(purchase.get('category', '기타')))
            item_name = st.text_input("품목명", value=purchase.get('item_name', ''))
            quantity = st.number_input("수량", min_value=1, value=purchase.get('quantity', 1), step=1)
            unit = st.selectbox("단위", 
                               ["개", "박스", "세트", "kg", "L"],
                               index=["개", "박스", "세트", "kg", "L"].index(purchase.get('unit', '개')))
        
        with col2:
            currency = st.selectbox("통화", 
                                   ["KRW", "USD", "VND"],
                                   index=["KRW", "USD", "VND"].index(purchase.get('currency', 'KRW')))
            currency_steps = {"USD": 10, "VND": 10000, "KRW": 1000}
            step = currency_steps.get(currency, 1000)
            
            unit_price = st.number_input("단가", min_value=0.0, value=float(purchase.get('unit_price', 0)), step=float(step))
            supplier = st.text_input("공급업체", value=purchase.get('supplier', ''))
            
            # 요청일 변환
            request_date_str = purchase.get('request_date')
            if request_date_str:
                try:
                    request_date_value = datetime.fromisoformat(str(request_date_str)).date()
                except:
                    request_date_value = date.today()
            else:
                request_date_value = date.today()
            
            request_date = st.date_input("요청일", value=request_date_value)
            urgency = st.selectbox("긴급도", 
                                  ["낮음", "보통", "높음", "긴급"],
                                  index=["낮음", "보통", "높음", "긴급"].index(purchase.get('urgency', '보통')))
        
        status = st.selectbox("상태",
                             ["대기중", "승인완료", "발주완료", "입고완료", "반려", "취소"],
                             index=["대기중", "승인완료", "발주완료", "입고완료", "반려", "취소"].index(purchase.get('status', '대기중')))
        
        notes = st.text_area("비고", value=purchase.get('notes', '') or '')
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 수정 저장", type="primary", use_container_width=True)
        with col_btn2:
            cancelled = st.form_submit_button("❌ 취소", use_container_width=True)
        
        if submitted:
            if not item_name.strip():
                st.error("품목명을 입력해주세요.")
            elif not supplier.strip():
                st.error("공급업체를 입력해주세요.")
            elif unit_price <= 0:
                st.error("단가를 입력해주세요.")
            else:
                update_data = {
                    'id': purchase_id,
                    "category": category,
                    "item_name": item_name,
                    "quantity": quantity,
                    "unit": unit,
                    "unit_price": unit_price,
                    "currency": currency,
                    "supplier": supplier,
                    "request_date": request_date.isoformat(),
                    "urgency": urgency,
                    "status": status,
                    "notes": notes if notes.strip() else None,
                    "updated_at": datetime.now().isoformat()
                }
                
                if update_func("purchases", update_data, "id"):
                    st.success("✅ 구매품이 수정되었습니다!")
                    del st.session_state['editing_purchase_id']
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 수정에 실패했습니다.")
        
        if cancelled:
            del st.session_state['editing_purchase_id']
            st.rerun()