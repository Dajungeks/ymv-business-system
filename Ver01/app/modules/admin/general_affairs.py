"""
YMV 비즈니스 시스템 - 총무 관리 모듈
구매 관리 및 현금 흐름 관리
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

from app.shared.database import get_db
from app.shared.utils import (
    show_success_message, show_error_message, show_warning_message,
    format_currency, generate_document_number, export_to_csv
)
from app.shared.translations import t
from app.modules.auth.login import get_auth_manager

def general_affairs_page():
    """총무 관리 메인 페이지"""
    st.markdown(f"# 🏢 총무 관리")
    
    # 권한 확인
    auth = get_auth_manager()
    current_user = auth.get_current_user()
    
    if not current_user:
        st.error("로그인이 필요합니다.")
        return
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["🛒 구매 관리", "💰 현금 흐름", "📊 예산 관리"])
    
    with tab1:
        purchase_management()
    
    with tab2:
        cash_flow_management()
    
    with tab3:
        budget_management()

def purchase_management():
    """구매 관리"""
    st.markdown("### 🛒 구매 관리")
    
    subtab1, subtab2, subtab3 = st.tabs(["📋 구매 목록", "➕ 새 구매", "📂 카테고리"])
    
    with subtab1:
        show_purchase_list()
    
    with subtab2:
        add_new_purchase()
    
    with subtab3:
        manage_purchase_categories()

def show_purchase_list():
    """구매 목록 표시"""
    st.markdown("#### 구매 내역")
    
    db = get_db()
    if not db:
        st.error("데이터베이스 연결 실패")
        return
    
    # 필터 옵션
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_from = st.date_input("시작일", value=date.today() - timedelta(days=30))
    
    with col2:
        date_to = st.date_input("종료일", value=date.today())
    
    with col3:
        # 카테고리 목록 조회
        categories = db.execute_query("purchase_categories", columns="category_name")
        category_names = ["전체"] + [cat['category_name'] for cat in categories] if categories else ["전체"]
        selected_category = st.selectbox("카테고리", category_names)
    
    with col4:
        status_options = ["전체", "pending", "approved", "rejected", "paid"]
        selected_status = st.selectbox("상태", status_options)
    
    # 구매 데이터 조회
    try:
        purchases = db.execute_query("purchases")
        
        if purchases:
            # 날짜 필터링
            filtered_purchases = []
            for purchase in purchases:
                purchase_date = datetime.strptime(purchase['purchase_date'], '%Y-%m-%d').date()
                if date_from <= purchase_date <= date_to:
                    if selected_category == "전체" or purchase.get('category_name') == selected_category:
                        if selected_status == "전체" or purchase['status'] == selected_status:
                            filtered_purchases.append(purchase)
            
            if filtered_purchases:
                # 데이터프레임 생성
                df = pd.DataFrame(filtered_purchases)
                
                # 표시할 컬럼 선택 및 이름 변경
                display_columns = {
                    'purchase_number': '구매번호',
                    'vendor_name': '공급업체',
                    'purchase_date': '구매일',
                    'amount_usd': '금액(USD)',
                    'description': '설명',
                    'status': '상태'
                }
                
                df_display = df[list(display_columns.keys())].copy()
                df_display.columns = list(display_columns.values())
                
                # 상태 한국어 변환
                status_map = {
                    'pending': '대기중',
                    'approved': '승인됨',
                    'rejected': '거부됨',
                    'paid': '지급완료'
                }
                df_display['상태'] = df_display['상태'].map(status_map)
                
                # 금액 포맷팅
                df_display['금액(USD)'] = df_display['금액(USD)'].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # 통계 정보
                col1, col2, col3 = st.columns(3)
                
                total_amount = sum([p['amount_usd'] for p in filtered_purchases])
                pending_count = len([p for p in filtered_purchases if p['status'] == 'pending'])
                approved_amount = sum([p['amount_usd'] for p in filtered_purchases if p['status'] in ['approved', 'paid']])
                
                with col1:
                    st.metric("총 구매 금액", f"${total_amount:,.2f}")
                
                with col2:
                    st.metric("대기중인 구매", f"{pending_count}건")
                
                with col3:
                    st.metric("승인된 금액", f"${approved_amount:,.2f}")
                
                # 내보내기
                if st.button("📥 CSV 내보내기"):
                    csv_data = export_to_csv(filtered_purchases, "purchases.csv")
                    st.download_button(
                        label="다운로드",
                        data=csv_data,
                        file_name=f"purchases_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                # 구매 항목 수정/삭제
                st.markdown("---")
                st.markdown("#### ✏️ 구매 항목 편집")
                
                selected_purchase_id = st.selectbox(
                    "편집할 구매 항목 선택",
                    options=[p['purchase_id'] for p in filtered_purchases],
                    format_func=lambda x: next((f"{p['purchase_number']} - {p['vendor_name']} (${p['amount_usd']:,.2f})") for p in filtered_purchases if p['purchase_id'] == x)
                )
                
                if selected_purchase_id:
                    edit_purchase(selected_purchase_id)
            
            else:
                st.info("선택한 기간에 구매 내역이 없습니다.")
        
        else:
            st.info("등록된 구매 내역이 없습니다.")
    
    except Exception as e:
        st.error(f"구매 목록 조회 오류: {e}")


def add_new_purchase():
    """새 구매 등록"""
    st.markdown("#### 새 구매 등록")
    
    db = get_db()
    if not db:
        return
    
    # 카테고리 조회
    categories = db.execute_query("purchase_categories", columns="category_id, category_name")
    
    if not categories:
        st.warning("구매 카테고리를 먼저 설정해주세요.")
        return
    
    # 환율 조회
    exchange_rates = db.execute_query("exchange_rates", columns="currency_code, rate_to_usd")
    rates_dict = {rate['currency_code']: rate['rate_to_usd'] for rate in exchange_rates} if exchange_rates else {}
    
    with st.form("add_purchase_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            vendor_name = st.text_input("공급업체명 *")
            category_id = st.selectbox(
                "카테고리 *",
                options=[cat['category_id'] for cat in categories],
                format_func=lambda x: next(cat['category_name'] for cat in categories if cat['category_id'] == x)
            )
            purchase_date = st.date_input("구매일", value=date.today())
        
        with col2:
            currency = st.selectbox("통화", ["USD", "VND", "KRW", "CNY", "THB"])  # USD를 첫 번째로
            amount = st.number_input("금액", min_value=0.0, step=0.01)
            
            # USD 환산 금액 표시
            if currency == "USD":
                amount_usd = amount
            else:
                rate = rates_dict.get(currency, 1)
                amount_usd = amount * rate
            
            st.info(f"USD 환산: ${amount_usd:,.2f}")
        
        description = st.text_area("구매 내용 설명")
        
        submitted = st.form_submit_button("🛒 구매 등록", use_container_width=True)
        
        if submitted:
            if not vendor_name or amount <= 0:
                show_error_message("필수 항목을 모두 입력해주세요.")
                return
            
            # 구매 번호 생성
            purchase_number = generate_document_number("PURCHASE", purchase_date)
            
            # 현재 사용자 정보
            current_user = get_auth_manager().get_current_user()
            
            purchase_data = {
                'purchase_number': purchase_number,
                'category_id': category_id,
                'vendor_name': vendor_name,
                'purchase_date': purchase_date.isoformat(),
                'amount': amount,
                'currency': currency,
                'amount_usd': amount_usd,
                'description': description,
                'status': 'pending',
                'requested_by': current_user['user_id']
            }
            
            result = db.execute_query("purchases", "insert", data=purchase_data)
            
            if result:
                show_success_message(f"구매가 등록되었습니다. (구매번호: {purchase_number})")
                st.rerun()
            else:
                show_error_message("구매 등록에 실패했습니다.")

def manage_purchase_categories():
    """구매 카테고리 관리"""
    st.markdown("#### 구매 카테고리 관리")
    
    db = get_db()
    if not db:
        return
    
    # 기존 카테고리 표시
    categories = db.execute_query("purchase_categories")
    
    if categories:
        st.markdown("**기존 카테고리:**")
        
        for cat in categories:
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.write(cat['category_code'])
            
            with col2:
                st.write(cat['category_name'])
            
            with col3:
                if st.button("삭제", key=f"del_{cat['category_id']}"):
                    db.execute_query("purchase_categories", "delete", conditions={"category_id": cat['category_id']})
                    st.rerun()
    
    st.markdown("---")
    
    # 새 카테고리 추가
    with st.form("add_category_form"):
        st.markdown("**새 카테고리 추가**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            category_code = st.text_input("카테고리 코드")
        
        with col2:
            category_name = st.text_input("카테고리명")
        
        description = st.text_input("설명")
        
        submitted = st.form_submit_button("추가")
        
        if submitted:
            if category_code and category_name:
                cat_data = {
                    'category_code': category_code,
                    'category_name': category_name,
                    'description': description,
                    'is_active': True
                }
                
                result = db.execute_query("purchase_categories", "insert", data=cat_data)
                
                if result:
                    show_success_message("카테고리가 추가되었습니다.")
                    st.rerun()
                else:
                    show_error_message("카테고리 추가에 실패했습니다.")

def cash_flow_management():
    """현금 흐름 관리"""
    st.markdown("### 💰 현금 흐름 관리")
    
    subtab1, subtab2 = st.tabs(["📊 현금 흐름", "➕ 거래 등록"])
    
    with subtab1:
        show_cash_flow()
    
    with subtab2:
        add_cash_transaction()

def show_cash_flow():
    """현금 흐름 표시"""
    st.markdown("#### 현금 흐름 현황")
    
    db = get_db()
    if not db:
        return
    
    # 기간 선택
    col1, col2 = st.columns(2)
    
    with col1:
        date_from = st.date_input("시작일", value=date.today() - timedelta(days=30), key="cf_from")
    
    with col2:
        date_to = st.date_input("종료일", value=date.today(), key="cf_to")
    
    # 현금 흐름 데이터 조회
    cash_flows = db.execute_query("cash_flows")
    
    if cash_flows:
        # 날짜 필터링
        filtered_flows = []
        for flow in cash_flows:
            transaction_date = datetime.strptime(flow['transaction_date'], '%Y-%m-%d').date()
            if date_from <= transaction_date <= date_to:
                filtered_flows.append(flow)
        
        if filtered_flows:
            # 수입/지출 합계
            income_total = sum([f['amount_usd'] for f in filtered_flows if f['type'] == 'income'])
            expense_total = sum([f['amount_usd'] for f in filtered_flows if f['type'] == 'expense'])
            net_flow = income_total - expense_total
            
            # 메트릭 표시
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 수입", f"${income_total:,.2f}", delta=None)
            
            with col2:
                st.metric("총 지출", f"${expense_total:,.2f}", delta=None)
            
            with col3:
                st.metric("순 현금흐름", f"${net_flow:,.2f}", delta=f"${net_flow:+,.2f}")
            
            # 데이터 테이블
            df = pd.DataFrame(filtered_flows)
            
            display_columns = {
                'transaction_date': '거래일',
                'type': '구분',
                'category': '카테고리',
                'amount_usd': '금액(USD)',
                'description': '설명'
            }
            
            df_display = df[list(display_columns.keys())].copy()
            df_display.columns = list(display_columns.values())
            
            # 구분 한국어 변환
            df_display['구분'] = df_display['구분'].map({'income': '수입', 'expense': '지출'})
            df_display['금액(USD)'] = df_display['금액(USD)'].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # CSV 내보내기
            if st.button("📥 CSV 내보내기", key="cash_export"):
                csv_data = export_to_csv(filtered_flows, "cash_flows.csv")
                st.download_button(
                    label="다운로드",
                    data=csv_data,
                    file_name=f"cash_flows_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="cash_download"
                )
            
            # 현금 거래 편집
            st.markdown("---")
            st.markdown("#### ✏️ 현금 거래 편집")
            
            selected_flow_id = st.selectbox(
                "편집할 거래 선택",
                options=[f['flow_id'] for f in filtered_flows],
                format_func=lambda x: next((f"{f['transaction_date']} - {f['category']} (${f['amount_usd']:,.2f})") for f in filtered_flows if f['flow_id'] == x)
            )
            
            if selected_flow_id:
                edit_cash_transaction(selected_flow_id)
            
        else:
            st.info("선택한 기간에 거래 내역이 없습니다.")
    
    else:
        st.info("등록된 현금 흐름이 없습니다.")

        
def add_cash_transaction():
    """현금 거래 등록"""
    st.markdown("#### 현금 거래 등록")
    
    with st.form("add_transaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_date = st.date_input("거래일", value=date.today())
            trans_type = st.selectbox("구분", ["income", "expense"], format_func=lambda x: "수입" if x == "income" else "지출")
            category = st.text_input("카테고리")
        
        with col2:
            currency = st.selectbox("통화", ["VND", "USD", "KRW", "CNY", "THB"], key="cash_currency")  # VND를 첫 번째로
            amount = st.number_input("금액", min_value=0.0, step=0.01)
            account = st.text_input("계정/계좌")
        
        description = st.text_area("거래 내용")
        reference_number = st.text_input("참조번호 (선택)")
        
        submitted = st.form_submit_button("💰 거래 등록")
        
        if submitted:
            if not category or amount <= 0:
                show_error_message("필수 항목을 모두 입력해주세요.")
                return
            
            # USD 환산 (임시로 1:1 비율 사용)
            amount_usd = amount  # 실제로는 환율 적용 필요
            
            current_user = get_auth_manager().get_current_user()
            
            transaction_data = {
                'transaction_date': transaction_date.isoformat(),
                'type': trans_type,
                'category': category,
                'amount': amount,
                'currency': currency,
                'amount_usd': amount_usd,
                'description': description,
                'reference_number': reference_number,
                'account': account,
                'created_by': current_user['user_id']
            }
            
            db = get_db()
            result = db.execute_query("cash_flows", "insert", data=transaction_data)
            
            if result:
                show_success_message("거래가 등록되었습니다.")
                st.rerun()
            else:
                show_error_message("거래 등록에 실패했습니다.")

def budget_management():
    """예산 관리"""
    st.markdown("### 📊 예산 관리")
    st.info("예산 관리 기능은 향후 업데이트 예정입니다.")


def edit_purchase(purchase_id: int):
    """구매 항목 편집"""
    db = get_db()
    if not db:
        return
    
    # 현재 구매 정보 조회
    purchase = db.execute_query("purchases", conditions={"purchase_id": purchase_id})
    if not purchase:
        st.error("구매 항목을 찾을 수 없습니다.")
        return
    
    purchase = purchase[0]
    
    # 카테고리 조회
    categories = db.execute_query("purchase_categories", columns="category_id, category_name")
    
    with st.form(f"edit_purchase_{purchase_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            vendor_name = st.text_input("공급업체명", value=purchase['vendor_name'])
            
            # 현재 카테고리 찾기
            current_cat_index = 0
            if categories:
                for i, cat in enumerate(categories):
                    if cat['category_id'] == purchase['category_id']:
                        current_cat_index = i
                        break
            
            category_id = st.selectbox(
                "카테고리",
                options=[cat['category_id'] for cat in categories] if categories else [1],
                index=current_cat_index,
                format_func=lambda x: next((cat['category_name'] for cat in categories if cat['category_id'] == x), "Unknown") if categories else "None"
            )
            
            purchase_date = st.date_input("구매일", value=datetime.strptime(purchase['purchase_date'], '%Y-%m-%d').date())
        
        with col2:
            currency = st.selectbox("통화", ["USD", "VND", "KRW", "CNY", "THB"], 
                                  index=["USD", "VND", "KRW", "CNY", "THB"].index(purchase['currency']))
            amount = st.number_input("금액", value=float(purchase['amount']), min_value=0.0, step=0.01)
            
            status_options = ["pending", "approved", "rejected", "paid"]
            status_labels = ["대기중", "승인됨", "거부됨", "지급완료"]
            current_status_index = status_options.index(purchase['status'])
            
            status = st.selectbox("상태", status_options, 
                                index=current_status_index,
                                format_func=lambda x: status_labels[status_options.index(x)])
        
        description = st.text_area("구매 내용 설명", value=purchase['description'] or "")
        
        col1, col2 = st.columns(2)
        
        with col1:
            update_submitted = st.form_submit_button("💾 구매 정보 수정")
        
        with col2:
            delete_submitted = st.form_submit_button("🗑️ 구매 항목 삭제", type="secondary")
        
        if update_submitted:
            # USD 환산 (실제로는 환율 적용 필요)
            amount_usd = amount  # 임시
            
            update_data = {
                'vendor_name': vendor_name,
                'category_id': category_id,
                'purchase_date': purchase_date.isoformat(),
                'amount': amount,
                'currency': currency,
                'amount_usd': amount_usd,
                'description': description,
                'status': status
            }
            
            result = db.execute_query("purchases", "update", data=update_data, conditions={"purchase_id": purchase_id})
            
            if result:
                show_success_message("구매 정보가 수정되었습니다.")
                st.rerun()
            else:
                show_error_message("구매 정보 수정에 실패했습니다.")
        
        if delete_submitted:
            if st.session_state.get(f'confirm_delete_purchase_{purchase_id}', False):
                # 실제 삭제 실행
                result = db.execute_query("purchases", "delete", conditions={"purchase_id": purchase_id})
                if result:
                    show_success_message(f"구매 항목 '{purchase['purchase_number']}'이 삭제되었습니다.")
                    st.rerun()
                else:
                    show_error_message("구매 항목 삭제에 실패했습니다.")
            else:
                # 삭제 확인
                st.session_state[f'confirm_delete_purchase_{purchase_id}'] = True
                show_warning_message("다시 삭제 버튼을 클릭하면 구매 항목이 영구 삭제됩니다.")
                st.rerun()

def edit_cash_transaction(flow_id: int):
    """현금 거래 편집"""
    db = get_db()
    if not db:
        return
    
    # 현재 거래 정보 조회
    transaction = db.execute_query("cash_flows", conditions={"flow_id": flow_id})
    if not transaction:
        st.error("거래를 찾을 수 없습니다.")
        return
    
    transaction = transaction[0]
    
    with st.form(f"edit_transaction_{flow_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_date = st.date_input("거래일", value=datetime.strptime(transaction['transaction_date'], '%Y-%m-%d').date())
            trans_type = st.selectbox("구분", ["income", "expense"], 
                                    index=0 if transaction['type'] == 'income' else 1,
                                    format_func=lambda x: "수입" if x == "income" else "지출")
            category = st.text_input("카테고리", value=transaction['category'])
        
        with col2:
            currency = st.selectbox("통화", ["USD", "VND", "KRW", "CNY", "THB"], 
                                  index=["USD", "VND", "KRW", "CNY", "THB"].index(transaction['currency']))
            amount = st.number_input("금액", value=float(transaction['amount']), min_value=0.0, step=0.01)
            account = st.text_input("계정/계좌", value=transaction['account'] or "")
        
        description = st.text_area("거래 내용", value=transaction['description'] or "")
        reference_number = st.text_input("참조번호", value=transaction['reference_number'] or "")
        
        col1, col2 = st.columns(2)
        
        with col1:
            update_submitted = st.form_submit_button("💾 거래 정보 수정")
        
        with col2:
            delete_submitted = st.form_submit_button("🗑️ 거래 삭제", type="secondary")
        
        if update_submitted:
            amount_usd = amount  # 임시
            
            update_data = {
                'transaction_date': transaction_date.isoformat(),
                'type': trans_type,
                'category': category,
                'amount': amount,
                'currency': currency,
                'amount_usd': amount_usd,
                'description': description,
                'reference_number': reference_number,
                'account': account
            }
            
            result = db.execute_query("cash_flows", "update", data=update_data, conditions={"flow_id": flow_id})
            
            if result:
                show_success_message("거래 정보가 수정되었습니다.")
                st.rerun()
            else:
                show_error_message("거래 정보 수정에 실패했습니다.")
        
        if delete_submitted:
            if st.session_state.get(f'confirm_delete_transaction_{flow_id}', False):
                result = db.execute_query("cash_flows", "delete", conditions={"flow_id": flow_id})
                if result:
                    show_success_message("거래가 삭제되었습니다.")
                    st.rerun()
                else:
                    show_error_message("거래 삭제에 실패했습니다.")
            else:
                st.session_state[f'confirm_delete_transaction_{flow_id}'] = True
                show_warning_message("다시 삭제 버튼을 클릭하면 거래가 영구 삭제됩니다.")
                st.rerun()

if __name__ == "__main__":
    general_affairs_page()