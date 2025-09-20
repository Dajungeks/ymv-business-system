import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from supabase import create_client, Client
from dotenv import load_dotenv
import json

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="YMV 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1e3c72;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-approved { background-color: #d4edda; color: #155724; }
    .status-completed { background-color: #d1ecf1; color: #0c5460; }
    .status-cancelled { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# Supabase 클라이언트 초기화
@st.cache_resource
def init_supabase():
    """Supabase 클라이언트 초기화"""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            st.error("❌ Supabase 연결 정보가 설정되지 않았습니다. .env 파일을 확인해주세요.")
            st.stop()
        
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        st.error(f"❌ Supabase 연결 실패: {str(e)}")
        st.stop()

# Supabase 클라이언트
supabase = init_supabase()

# 데이터베이스 연결 확인
def check_connection():
    """데이터베이스 연결 확인"""
    try:
        result = supabase.table('employees').select('id').limit(1).execute()
        return True
    except Exception as e:
        st.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
        return False

# 데이터 로드 함수 (Supabase)
@st.cache_data(ttl=60)  # 1분 캐시
def load_data_from_supabase(table_name, select_fields="*", filters=None):
    """Supabase에서 데이터 로드"""
    try:
        query = supabase.table(table_name).select(select_fields)
        
        if filters:
            for field, value in filters.items():
                query = query.eq(field, value)
        
        result = query.execute()
        return result.data if result.data else []
    except Exception as e:
        st.error(f"❌ 데이터 로드 실패 ({table_name}): {str(e)}")
        return []

# 데이터 삽입 함수
def insert_data_to_supabase(table_name, data):
    """Supabase에 데이터 삽입"""
    try:
        result = supabase.table(table_name).insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"❌ 데이터 삽입 실패 ({table_name}): {str(e)}")
        return None

# 데이터 업데이트 함수
def update_data_in_supabase(table_name, data, id_field="id", id_value=None):
    """Supabase에서 데이터 업데이트"""
    try:
        result = supabase.table(table_name).update(data).eq(id_field, id_value).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"❌ 데이터 업데이트 실패 ({table_name}): {str(e)}")
        return None

# 데이터 삭제 함수
def delete_data_from_supabase(table_name, id_field="id", id_value=None):
    """Supabase에서 데이터 삭제"""
    try:
        result = supabase.table(table_name).delete().eq(id_field, id_value).execute()
        return True
    except Exception as e:
        st.error(f"❌ 데이터 삭제 실패 ({table_name}): {str(e)}")
        return False

# CSV 다운로드 함수
def download_csv(data, filename):
    """CSV 파일 다운로드 버튼 생성"""
    if data:
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📁 CSV 다운로드",
            data=csv,
            file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# CSV 업로드 처리 함수
def process_csv_upload(uploaded_file, required_columns):
    """CSV 파일 업로드 처리"""
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        # 필수 컬럼 확인
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}")
            return None
            
        return df.to_dict('records')
    except Exception as e:
        st.error(f"CSV 파일 처리 중 오류가 발생했습니다: {str(e)}")
        return None

# 로그인 시스템
def login_system():
    """로그인 시스템"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.current_user = None

    if not st.session_state.logged_in:
        st.markdown("""
        <div class="main-header">
            <h1>🏢 YMV 관리 시스템</h1>
            <p>베트남 소재 한국 기업을 위한 통합 비즈니스 관리 시스템</p>
            <p>🔗 <strong>Supabase 연결 버전</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # 연결 상태 확인
        if not check_connection():
            st.error("❌ 데이터베이스에 연결할 수 없습니다.")
            return False
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("🔐 로그인")
            
            # 직원 데이터 로드
            employees = load_data_from_supabase('employees', 'id, username, password, name, department, position, email, is_active, is_admin')
            
            username = st.text_input("사용자명")
            password = st.text_input("비밀번호", type="password")
            
            if st.button("로그인", use_container_width=True):
                # 사용자 인증
                user = None
                for emp in employees:
                    if emp.get('username') == username and emp.get('password') == password:
                        if emp.get('is_active', True):
                            user = emp
                            break
                
                if user:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    st.cache_data.clear()  # 캐시 클리어
                    st.rerun()
                else:
                    st.error("잘못된 사용자명 또는 비밀번호입니다.")
        
        return False
    
    return True

# 메인 대시보드
def dashboard():
    """대시보드 페이지"""
    st.markdown("""
    <div class="main-header">
        <h1>🏢 YMV 관리 시스템 대시보드</h1>
        <p>🔗 Supabase 연결 | 현재 시스템 현황을 한눈에 확인하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사용자 정보 표시
    user = st.session_state.current_user
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"👋 안녕하세요, **{user['name']}**님! ({user['department']} - {user['position']})")
    with col2:
        if st.button("🚪 로그아웃"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.cache_data.clear()
            st.rerun()
    
    # 통계 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        purchases = load_data_from_supabase('purchases', 'id')
        st.metric("📦 구매품", len(purchases))
    
    with col2:
        expenses = load_data_from_supabase('expenses', 'id')
        st.metric("💰 지출요청", len(expenses))
    
    with col3:
        quotations = load_data_from_supabase('quotations', 'id')
        st.metric("📋 견적서", len(quotations))
    
    with col4:
        customers = load_data_from_supabase('customers', 'id')
        st.metric("👥 고객", len(customers))
    
    st.divider()
    
    # 최근 활동
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 최근 구매품")
        recent_purchases = load_data_from_supabase('purchases', '*')
        if recent_purchases:
            # 최신 5개만 표시
            recent_purchases = sorted(recent_purchases, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
            for item in recent_purchases:
                with st.expander(f"{item.get('item_name', 'N/A')} - {item.get('status', 'N/A')}"):
                    st.write(f"**카테고리**: {item.get('category')}")
                    st.write(f"**수량**: {item.get('quantity')} {item.get('unit')}")
                    st.write(f"**금액**: ${item.get('total_price', 0):.2f}")
        else:
            st.info("등록된 구매품이 없습니다.")
    
    with col2:
        st.subheader("📋 최근 견적서")
        recent_quotes = load_data_from_supabase('quotations', '*')
        if recent_quotes:
            # 최신 5개만 표시
            recent_quotes = sorted(recent_quotes, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
            for quote in recent_quotes:
                with st.expander(f"{quote.get('customer_name', 'N/A')} - {quote.get('status', 'N/A')}"):
                    st.write(f"**회사**: {quote.get('company')}")
                    st.write(f"**견적일**: {quote.get('quote_date')}")
                    st.write(f"**총액**: {quote.get('currency', 'USD')} {quote.get('total_amount', 0):.2f}")
        else:
            st.info("등록된 견적서가 없습니다.")

# 구매품 관리
def purchase_management():
    """구매품 관리 페이지"""
    st.header("📦 구매품 관리")
    
    tab1, tab2 = st.tabs(["📝 구매품 등록", "📋 구매품 목록"])
    
    with tab1:
        st.subheader("새 구매품 등록")
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("카테고리", ["사무용품", "판매제품", "핫런너", "기타"])
            item_name = st.text_input("품목명")
            quantity = st.number_input("수량", min_value=1, value=1)
            unit = st.text_input("단위", value="개")
        
        with col2:
            unit_price = st.number_input("단가 (USD)", min_value=0.0, format="%.2f")
            supplier = st.text_input("공급업체")
            urgency = st.selectbox("긴급도", ["보통", "긴급", "매우긴급"])
            notes = st.text_area("비고")
        
        if st.button("구매품 등록", use_container_width=True):
            if item_name and supplier:
                new_purchase = {
                    'category': category,
                    'item_name': item_name,
                    'quantity': quantity,
                    'unit': unit,
                    'unit_price': unit_price,
                    'supplier': supplier,
                    'request_date': date.today().isoformat(),
                    'urgency': urgency,
                    'status': '대기중',
                    'notes': notes,
                    'requester': st.session_state.current_user['id']
                }
                
                result = insert_data_to_supabase('purchases', new_purchase)
                if result:
                    st.success("구매품이 성공적으로 등록되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("구매품 등록 중 오류가 발생했습니다.")
            else:
                st.error("품목명과 공급업체는 필수 입력 사항입니다.")
    
    with tab2:
        st.subheader("구매품 목록")
        
        purchases = load_data_from_supabase('purchases_detail', '*')  # 뷰 사용
        
        if purchases:
            # 필터 옵션
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_category = st.selectbox("카테고리 필터", ["전체"] + ["사무용품", "판매제품", "핫런너", "기타"])
            with col2:
                filter_status = st.selectbox("상태 필터", ["전체", "대기중", "승인됨", "주문완료", "취소됨"])
            with col3:
                download_csv(purchases, "구매품목록")
            
            # 필터 적용
            filtered_purchases = purchases.copy()
            if filter_category != "전체":
                filtered_purchases = [p for p in filtered_purchases if p.get('category') == filter_category]
            if filter_status != "전체":
                filtered_purchases = [p for p in filtered_purchases if p.get('status') == filter_status]
            
            # 구매품 목록 표시
            for purchase in sorted(filtered_purchases, key=lambda x: x.get('created_at', ''), reverse=True):
                with st.expander(f"📦 {purchase.get('item_name')} - {purchase.get('status')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**ID**: {purchase.get('id')}")
                        st.write(f"**카테고리**: {purchase.get('category')}")
                        st.write(f"**품목명**: {purchase.get('item_name')}")
                        st.write(f"**공급업체**: {purchase.get('supplier')}")
                    
                    with col2:
                        st.write(f"**수량**: {purchase.get('quantity')} {purchase.get('unit')}")
                        st.write(f"**단가**: ${purchase.get('unit_price', 0):.2f}")
                        st.write(f"**총액**: ${purchase.get('total_price', 0):.2f}")
                        st.write(f"**긴급도**: {purchase.get('urgency')}")
                    
                    with col3:
                        st.write(f"**상태**: {purchase.get('status')}")
                        st.write(f"**요청일**: {purchase.get('request_date')}")
                        st.write(f"**요청자**: {purchase.get('requester_name', 'N/A')}")
                        if purchase.get('notes'):
                            st.write(f"**비고**: {purchase.get('notes')}")
                    
                    # 수정/삭제 버튼
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"📝 수정", key=f"edit_purchase_{purchase['id']}"):
                            st.session_state[f"editing_purchase_{purchase['id']}"] = True
                    with col2:
                        new_status = st.selectbox("상태 변경", 
                                                ["대기중", "승인됨", "주문완료", "취소됨"],
                                                index=["대기중", "승인됨", "주문완료", "취소됨"].index(purchase.get('status', '대기중')),
                                                key=f"status_{purchase['id']}")
                        if new_status != purchase.get('status'):
                            update_data_in_supabase('purchases', {'status': new_status}, 'id', purchase['id'])
                            st.cache_data.clear()
                            st.rerun()
                    with col3:
                        if st.button(f"❌ 삭제", key=f"delete_purchase_{purchase['id']}"):
                            if delete_data_from_supabase('purchases', 'id', purchase['id']):
                                st.success("구매품이 삭제되었습니다.")
                                st.cache_data.clear()
                                st.rerun()
                    
                    # 수정 폼
                    if st.session_state.get(f"editing_purchase_{purchase['id']}", False):
                        st.write("---")
                        st.write("**수정하기**")
                        col1, col2 = st.columns(2)
                        with col1:
                            new_item_name = st.text_input("품목명", value=purchase.get('item_name', ''), key=f"edit_item_{purchase['id']}")
                            new_quantity = st.number_input("수량", value=purchase.get('quantity', 1), key=f"edit_qty_{purchase['id']}")
                            new_unit_price = st.number_input("단가", value=purchase.get('unit_price', 0.0), key=f"edit_price_{purchase['id']}")
                        with col2:
                            new_supplier = st.text_input("공급업체", value=purchase.get('supplier', ''), key=f"edit_supplier_{purchase['id']}")
                            new_urgency = st.selectbox("긴급도", ["보통", "긴급", "매우긴급"], 
                                                     index=["보통", "긴급", "매우긴급"].index(purchase.get('urgency', '보통')),
                                                     key=f"edit_urgency_{purchase['id']}")
                            new_notes = st.text_area("비고", value=purchase.get('notes', ''), key=f"edit_notes_{purchase['id']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 저장", key=f"save_purchase_{purchase['id']}"):
                                update_data = {
                                    'item_name': new_item_name,
                                    'quantity': new_quantity,
                                    'unit_price': new_unit_price,
                                    'supplier': new_supplier,
                                    'urgency': new_urgency,
                                    'notes': new_notes
                                }
                                
                                if update_data_in_supabase('purchases', update_data, 'id', purchase['id']):
                                    st.session_state[f"editing_purchase_{purchase['id']}"] = False
                                    st.success("구매품 정보가 수정되었습니다.")
                                    st.cache_data.clear()
                                    st.rerun()
                        with col2:
                            if st.button("❌ 취소", key=f"cancel_purchase_{purchase['id']}"):
                                st.session_state[f"editing_purchase_{purchase['id']}"] = False
                                st.rerun()
        else:
            st.info("등록된 구매품이 없습니다.")

# 지출 요청서 관리
def expense_management():
    """지출 요청서 관리 페이지"""
    st.header("💰 지출 요청서 관리")
    
    tab1, tab2 = st.tabs(["📝 지출 요청서 작성", "📋 지출 요청서 목록"])
    
    with tab1:
        st.subheader("새 지출 요청서 작성")
        
        col1, col2 = st.columns(2)
        with col1:
            expense_type = st.selectbox("지출 유형", 
                ["출장비", "사무용품", "접대비", "교육비", "교통비", "식비", "통신비", "장비구입", "유지보수", "마케팅", "기타"])
            amount = st.number_input("금액", min_value=0.0, format="%.2f")
            currency = st.selectbox("통화", ["USD", "VND", "KRW"])
            payment_method = st.selectbox("결제 방법", ["현금", "법인카드", "계좌이체", "수표"])
        
        with col2:
            expense_date = st.date_input("지출 예정일", value=date.today())
            department = st.text_input("부서", value=st.session_state.current_user.get('department', ''))
            urgency = st.selectbox("긴급도", ["보통", "긴급", "매우긴급"])
            
        description = st.text_area("지출 내역")
        business_purpose = st.text_area("사업 목적")
        
        if st.button("지출 요청서 작성", use_container_width=True):
            if description and business_purpose and amount > 0:
                new_expense = {
                    'expense_type': expense_type,
                    'amount': amount,
                    'currency': currency,
                    'payment_method': payment_method,
                    'expense_date': expense_date.isoformat(),
                    'department': department,
                    'requester': st.session_state.current_user['id'],
                    'urgency': urgency,
                    'description': description,
                    'business_purpose': business_purpose,
                    'status': '대기중'
                }
                
                result = insert_data_to_supabase('expenses', new_expense)
                if result:
                    st.success("지출 요청서가 성공적으로 작성되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("지출 요청서 작성 중 오류가 발생했습니다.")
            else:
                st.error("모든 필수 정보를 입력해주세요.")
    
    with tab2:
        st.subheader("지출 요청서 목록")
        
        expenses = load_data_from_supabase('expenses_detail', '*')
        
        if expenses:
            # 필터 및 다운로드
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_status = st.selectbox("상태 필터", ["전체", "대기중", "승인됨", "지급완료", "반려됨"])
            with col2:
                filter_type = st.selectbox("유형 필터", ["전체"] + ["출장비", "사무용품", "접대비", "교육비", "교통비", "식비", "통신비", "장비구입", "유지보수", "마케팅", "기타"])
            with col3:
                download_csv(expenses, "지출요청서목록")
            
            # 필터 적용
            filtered_expenses = expenses.copy()
            if filter_status != "전체":
                filtered_expenses = [e for e in filtered_expenses if e.get('status') == filter_status]
            if filter_type != "전체":
                filtered_expenses = [e for e in filtered_expenses if e.get('expense_type') == filter_type]
            
            # 지출 요청서 목록 표시
            for expense in sorted(filtered_expenses, key=lambda x: x.get('created_at', ''), reverse=True):
                with st.expander(f"💰 {expense.get('expense_type')} - {expense.get('currency')} {expense.get('amount', 0):,.2f}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**ID**: {expense.get('id')}")
                        st.write(f"**지출 유형**: {expense.get('expense_type')}")
                        st.write(f"**금액**: {expense.get('currency')} {expense.get('amount', 0):,.2f}")
                        st.write(f"**결제 방법**: {expense.get('payment_method')}")
                    
                    with col2:
                        st.write(f"**지출 예정일**: {expense.get('expense_date')}")
                        st.write(f"**부서**: {expense.get('department')}")
                        st.write(f"**요청자**: {expense.get('requester_name', 'N/A')}")
                        st.write(f"**긴급도**: {expense.get('urgency')}")
                    
                    with col3:
                        st.write(f"**상태**: {expense.get('status')}")
                        st.write(f"**작성일**: {expense.get('created_at', '')[:10]}")
                    
                    st.write(f"**지출 내역**: {expense.get('description')}")
                    st.write(f"**사업 목적**: {expense.get('business_purpose')}")
                    
                    # 수정/삭제 버튼
                    col1, col2, col3 = st.columns(3)
                    with col2:
                        new_status = st.selectbox("상태 변경", 
                                                ["대기중", "승인됨", "지급완료", "반려됨"],
                                                index=["대기중", "승인됨", "지급완료", "반려됨"].index(expense.get('status', '대기중')),
                                                key=f"expense_status_{expense['id']}")
                        if new_status != expense.get('status'):
                            update_data_in_supabase('expenses', {'status': new_status}, 'id', expense['id'])
                            st.cache_data.clear()
                            st.rerun()
                    with col3:
                        if st.button(f"❌ 삭제", key=f"delete_expense_{expense['id']}"):
                            if delete_data_from_supabase('expenses', 'id', expense['id']):
                                st.success("지출 요청서가 삭제되었습니다.")
                                st.cache_data.clear()
                                st.rerun()
        else:
            st.info("등록된 지출 요청서가 없습니다.")

# 견적서 관리
def quotation_management():
    """견적서 관리 페이지"""
    st.header("📋 견적서 관리")
    
    tab1, tab2 = st.tabs(["📝 견적서 작성", "📋 견적서 목록"])
    
    with tab1:
        st.subheader("새 견적서 작성")
        
        # 고객 정보 섹션
        st.write("### 👥 고객 정보")
        customers = load_data_from_supabase('customers', '*')
        
        col1, col2 = st.columns(2)
        with col1:
            if customers:
                customer_options = ["직접 입력"] + [f"{c['company_name']} ({c['contact_person']})" for c in customers]
                selected_customer = st.selectbox("기존 고객 선택", customer_options)
                
                if selected_customer != "직접 입력":
                    # 기존 고객 정보 자동 입력
                    customer_data = customers[customer_options.index(selected_customer) - 1]
                    customer_name = st.text_input("고객명", value=customer_data['contact_person'])
                    company = st.text_input("회사명", value=customer_data['company_name'])
                    email = st.text_input("이메일", value=customer_data.get('email', ''))
                    phone = st.text_input("연락처", value=customer_data.get('phone', ''))
                else:
                    customer_name = st.text_input("고객명")
                    company = st.text_input("회사명")
                    email = st.text_input("이메일")
                    phone = st.text_input("연락처")
            else:
                customer_name = st.text_input("고객명")
                company = st.text_input("회사명")
                email = st.text_input("이메일")
                phone = st.text_input("연락처")
        
        with col2:
            quote_date = st.date_input("견적일", value=date.today())
            valid_until = st.date_input("유효기간")
            currency = st.selectbox("통화", ["USD", "VND", "KRW"])
        
        # 견적 항목 섹션
        st.write("### 📦 견적 항목")
        products = load_data_from_supabase('products', '*')
        
        col1, col2 = st.columns(2)
        with col1:
            if products:
                product_options = ["직접 입력"] + [f"{p['product_code']} - {p['product_name']}" for p in products]
                selected_product = st.selectbox("기존 제품 선택", product_options)
                
                if selected_product != "직접 입력":
                    # 기존 제품 정보 자동 입력
                    product_data = products[product_options.index(selected_product) - 1]
                    item_name = st.text_input("제품명", value=product_data['product_name'])
                    
                    # 환율 적용
                    exchange_rates = load_data_from_supabase('exchange_rates', '*')
                    base_price = product_data.get('unit_price', 0)
                    
                    if currency == 'VND' and product_data.get('currency') == 'USD':
                        # USD -> VND 변환
                        usd_to_vnd = 24000  # 기본값
                        for rate in exchange_rates:
                            if rate.get('from_currency') == 'USD' and rate.get('to_currency') == 'VND':
                                usd_to_vnd = rate.get('rate', 24000)
                                break
                        unit_price = st.number_input("단가", value=base_price * usd_to_vnd, format="%.2f")
                    else:
                        unit_price = st.number_input("단가", value=base_price, format="%.2f")
                else:
                    item_name = st.text_input("제품명")
                    unit_price = st.number_input("단가", min_value=0.0, format="%.2f")
            else:
                item_name = st.text_input("제품명")
                unit_price = st.number_input("단가", min_value=0.0, format="%.2f")
        
        with col2:
            quantity = st.number_input("수량", min_value=1, value=1)
            total_amount = quantity * unit_price
            st.write(f"**총액**: {currency} {total_amount:,.2f}")
        
        notes = st.text_area("특이사항")
        
        if st.button("견적서 작성", use_container_width=True):
            if customer_name and company and item_name:
                new_quotation = {
                    'customer_name': customer_name,
                    'company': company,
                    'contact_person': customer_name,
                    'email': email,
                    'phone': phone,
                    'quote_date': quote_date.isoformat(),
                    'valid_until': valid_until.isoformat(),
                    'currency': currency,
                    'item_name': item_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'notes': notes,
                    'status': '작성중',
                    'created_by': st.session_state.current_user['id']
                }
                
                result = insert_data_to_supabase('quotations', new_quotation)
                if result:
                    st.success("견적서가 성공적으로 작성되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("견적서 작성 중 오류가 발생했습니다.")
            else:
                st.error("고객명, 회사명, 제품명은 필수 입력 사항입니다.")
    
    with tab2:
        st.subheader("견적서 목록")
        
        quotations = load_data_from_supabase('quotations_detail', '*')
        
        if quotations:
            # 필터 및 다운로드
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_status = st.selectbox("상태 필터", ["전체", "작성중", "발송됨", "승인됨", "거절됨", "만료됨"])
            with col2:
                filter_currency = st.selectbox("통화 필터", ["전체", "USD", "VND", "KRW"])
            with col3:
                download_csv(quotations, "견적서목록")
            
            # 필터 적용
            filtered_quotations = quotations.copy()
            if filter_status != "전체":
                filtered_quotations = [q for q in filtered_quotations if q.get('status') == filter_status]
            if filter_currency != "전체":
                filtered_quotations = [q for q in filtered_quotations if q.get('currency') == filter_currency]
            
            # 견적서 목록 표시
            for quotation in sorted(filtered_quotations, key=lambda x: x.get('created_at', ''), reverse=True):
                with st.expander(f"📋 {quotation.get('company')} - {quotation.get('currency')} {quotation.get('total_amount', 0):,.2f}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**견적서 번호**: {quotation.get('id')}")
                        st.write(f"**고객명**: {quotation.get('customer_name')}")
                        st.write(f"**회사명**: {quotation.get('company')}")
                        st.write(f"**연락처**: {quotation.get('phone')}")
                    
                    with col2:
                        st.write(f"**견적일**: {quotation.get('quote_date')}")
                        st.write(f"**유효기간**: {quotation.get('valid_until')}")
                        st.write(f"**제품명**: {quotation.get('item_name')}")
                        st.write(f"**수량**: {quotation.get('quantity')}")
                    
                    with col3:
                        st.write(f"**단가**: {quotation.get('currency')} {quotation.get('unit_price', 0):,.2f}")
                        st.write(f"**총액**: {quotation.get('currency')} {quotation.get('total_amount', 0):,.2f}")
                        st.write(f"**상태**: {quotation.get('status')}")
                        st.write(f"**작성자**: {quotation.get('created_by_name', 'N/A')}")
                    
                    if quotation.get('notes'):
                        st.write(f"**특이사항**: {quotation.get('notes')}")
                    
                    # 수정/삭제 버튼
                    col1, col2, col3 = st.columns(3)
                    with col2:
                        new_status = st.selectbox("상태 변경", 
                                                ["작성중", "발송됨", "승인됨", "거절됨", "만료됨"],
                                                index=["작성중", "발송됨", "승인됨", "거절됨", "만료됨"].index(quotation.get('status', '작성중')),
                                                key=f"quote_status_{quotation['id']}")
                        if new_status != quotation.get('status'):
                            update_data_in_supabase('quotations', {'status': new_status}, 'id', quotation['id'])
                            st.cache_data.clear()
                            st.rerun()
                    with col3:
                        if st.button(f"❌ 삭제", key=f"delete_quote_{quotation['id']}"):
                            if delete_data_from_supabase('quotations', 'id', quotation['id']):
                                st.success("견적서가 삭제되었습니다.")
                                st.cache_data.clear()
                                st.rerun()
        else:
            st.info("등록된 견적서가 없습니다.")

# 고객 관리
def customer_management():
    """고객 관리 페이지"""
    st.header("👥 고객 관리")
    
    tab1, tab2, tab3 = st.tabs(["📝 고객 등록", "📋 고객 목록", "📁 CSV 업로드"])
    
    with tab1:
        st.subheader("새 고객 등록")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("회사명")
            contact_person = st.text_input("담당자명")
            position = st.text_input("직책")
            phone = st.text_input("연락처")
        
        with col2:
            email = st.text_input("이메일")
            address = st.text_area("주소")
            industry = st.text_input("업종")
            notes = st.text_area("비고")
        
        if st.button("고객 등록", use_container_width=True):
            if company_name and contact_person:
                new_customer = {
                    'company_name': company_name,
                    'contact_person': contact_person,
                    'position': position,
                    'phone': phone,
                    'email': email,
                    'address': address,
                    'industry': industry,
                    'notes': notes
                }
                
                result = insert_data_to_supabase('customers', new_customer)
                if result:
                    st.success("고객이 성공적으로 등록되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("고객 등록 중 오류가 발생했습니다.")
            else:
                st.error("회사명과 담당자명은 필수 입력 사항입니다.")
    
    with tab2:
        st.subheader("고객 목록")
        
        customers = load_data_from_supabase('customers', '*')
        
        if customers:
            # 검색 및 다운로드
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("🔍 검색 (회사명, 담당자명, 업종)")
            with col2:
                download_csv(customers, "고객목록")
            
            # 검색 필터 적용
            if search_term:
                filtered_customers = []
                for customer in customers:
                    if (search_term.lower() in customer.get('company_name', '').lower() or
                        search_term.lower() in customer.get('contact_person', '').lower() or
                        search_term.lower() in customer.get('industry', '').lower()):
                        filtered_customers.append(customer)
            else:
                filtered_customers = customers
            
            # 고객 목록 표시
            for customer in sorted(filtered_customers, key=lambda x: x.get('created_at', ''), reverse=True):
                with st.expander(f"👥 {customer.get('company_name')} - {customer.get('contact_person')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**ID**: {customer.get('id')}")
                        st.write(f"**회사명**: {customer.get('company_name')}")
                        st.write(f"**담당자**: {customer.get('contact_person')}")
                        st.write(f"**직책**: {customer.get('position')}")
                    
                    with col2:
                        st.write(f"**연락처**: {customer.get('phone')}")
                        st.write(f"**이메일**: {customer.get('email')}")
                        st.write(f"**업종**: {customer.get('industry')}")
                    
                    with col3:
                        st.write(f"**주소**: {customer.get('address')}")
                        st.write(f"**등록일**: {customer.get('created_at', '')[:10]}")
                        if customer.get('notes'):
                            st.write(f"**비고**: {customer.get('notes')}")
                    
                    # 삭제 버튼
                    if st.button(f"❌ 삭제", key=f"delete_customer_{customer['id']}"):
                        if delete_data_from_supabase('customers', 'id', customer['id']):
                            st.success("고객이 삭제되었습니다.")
                            st.cache_data.clear()
                            st.rerun()
        else:
            st.info("등록된 고객이 없습니다.")
    
    with tab3:
        st.subheader("CSV 파일 업로드")
        
        # CSV 템플릿 다운로드
        st.write("### 📁 CSV 템플릿")
        template_data = [{
            'company_name': '샘플회사',
            'contact_person': '홍길동',
            'position': '구매팀장',
            'phone': '010-1234-5678',
            'email': 'hong@sample.com',
            'address': '서울시 강남구',
            'industry': '제조업',
            'notes': '주요 고객'
        }]
        template_df = pd.DataFrame(template_data)
        csv_template = template_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV 템플릿 다운로드",
            data=csv_template,
            file_name="고객_템플릿.csv",
            mime="text/csv"
        )
        
        # CSV 파일 업로드
        st.write("### 📤 CSV 파일 업로드")
        uploaded_file = st.file_uploader("CSV 파일을 선택하세요", type=['csv'])
        
        if uploaded_file is not None:
            required_columns = ['company_name', 'contact_person', 'position', 'phone', 'email', 'address', 'industry', 'notes']
            new_customers_data = process_csv_upload(uploaded_file, required_columns)
            
            if new_customers_data:
                st.write("### 📋 업로드 데이터 미리보기")
                preview_df = pd.DataFrame(new_customers_data)
                st.dataframe(preview_df)
                
                if st.button("💾 고객 데이터 저장", use_container_width=True):
                    success_count = 0
                    for customer_data in new_customers_data:
                        result = insert_data_to_supabase('customers', customer_data)
                        if result:
                            success_count += 1
                    
                    if success_count > 0:
                        st.success(f"✅ {success_count}개의 고객이 성공적으로 등록되었습니다!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ 고객 데이터 저장 중 오류가 발생했습니다.")

# 제품 관리
def product_management():
    """제품 관리 페이지"""
    st.header("📦 제품 관리")
    
    tab1, tab2, tab3 = st.tabs(["📝 제품 등록", "📋 제품 목록", "📁 CSV 업로드"])
    
    with tab1:
        st.subheader("새 제품 등록")
        
        col1, col2 = st.columns(2)
        with col1:
            product_code = st.text_input("제품 코드")
            product_name = st.text_input("제품명")
            category = st.selectbox("카테고리", ["핫런너", "사무용품", "기계부품", "전자제품", "기타"])
            unit = st.text_input("단위", value="개")
        
        with col2:
            unit_price_usd = st.number_input("단가 (USD)", min_value=0.0, format="%.2f")
            
            # 환율 정보 로드 및 VND 판매가 계산
            exchange_rates = load_data_from_supabase('exchange_rates', '*')
            usd_to_vnd_rate = 24000  # 기본값
            for rate in exchange_rates:
                if rate.get('from_currency') == 'USD' and rate.get('to_currency') == 'VND':
                    usd_to_vnd_rate = rate.get('rate', 24000)
                    break
            
            vnd_price = unit_price_usd * usd_to_vnd_rate
            unit_price_vnd = st.number_input("판매가 (VND)", value=vnd_price, format="%.0f")
            
            supplier = st.text_input("공급업체")
            stock_quantity = st.number_input("재고수량", min_value=0, value=0)
        
        description = st.text_area("제품 설명")
        
        if st.button("제품 등록", use_container_width=True):
            if product_code and product_name:
                new_product = {
                    'product_code': product_code,
                    'product_name': product_name,
                    'category': category,
                    'unit': unit,
                    'unit_price': unit_price_usd,
                    'unit_price_vnd': unit_price_vnd,
                    'currency': 'USD',
                    'supplier': supplier,
                    'stock_quantity': stock_quantity,
                    'description': description
                }
                
                result = insert_data_to_supabase('products', new_product)
                if result:
                    st.success("제품이 성공적으로 등록되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("제품 등록 중 오류가 발생했습니다.")
            else:
                st.error("제품 코드와 제품명은 필수 입력 사항입니다.")
    
    with tab2:
        st.subheader("제품 목록")
        
        products = load_data_from_supabase('products', '*')
        
        if products:
            # 검색 및 필터
            col1, col2, col3 = st.columns(3)
            with col1:
                search_term = st.text_input("🔍 검색 (제품명, 제품코드)")
            with col2:
                filter_category = st.selectbox("카테고리 필터", ["전체"] + ["핫런너", "사무용품", "기계부품", "전자제품", "기타"])
            with col3:
                download_csv(products, "제품목록")
            
            # 필터 적용
            filtered_products = products.copy()
            if search_term:
                filtered_products = [p for p in filtered_products 
                                   if search_term.lower() in p.get('product_name', '').lower() or 
                                      search_term.lower() in p.get('product_code', '').lower()]
            if filter_category != "전체":
                filtered_products = [p for p in filtered_products if p.get('category') == filter_category]
            
            # 제품 목록 표시
            for product in sorted(filtered_products, key=lambda x: x.get('created_at', ''), reverse=True):
                with st.expander(f"📦 {product.get('product_code')} - {product.get('product_name')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**제품 코드**: {product.get('product_code')}")
                        st.write(f"**제품명**: {product.get('product_name')}")
                        st.write(f"**카테고리**: {product.get('category')}")
                        st.write(f"**단위**: {product.get('unit')}")
                    
                    with col2:
                        st.write(f"**단가**: ${product.get('unit_price', 0):,.2f}")
                        st.write(f"**판매가**: ₫{product.get('unit_price_vnd', 0):,.0f}")
                        st.write(f"**공급업체**: {product.get('supplier')}")
                        st.write(f"**재고**: {product.get('stock_quantity', 0)}")
                    
                    with col3:
                        st.write(f"**등록일**: {product.get('created_at', '')[:10]}")
                        if product.get('description'):
                            st.write(f"**설명**: {product.get('description')}")
                    
                    # 삭제 버튼
                    if st.button(f"❌ 삭제", key=f"delete_product_{product['id']}"):
                        if delete_data_from_supabase('products', 'id', product['id']):
                            st.success("제품이 삭제되었습니다.")
                            st.cache_data.clear()
                            st.rerun()
        else:
            st.info("등록된 제품이 없습니다.")
    
    with tab3:
        st.subheader("CSV 파일 업로드")
        
        # CSV 템플릿 다운로드
        st.write("### 📁 CSV 템플릿")
        template_data = [{
            'product_code': 'HR001',
            'product_name': '핫런너 시스템 A형',
            'category': '핫런너',
            'unit': '세트',
            'unit_price': 1500.0,
            'unit_price_vnd': 36000000,
            'supplier': '핫런너코리아',
            'stock_quantity': 10,
            'description': '고성능 핫런너 시스템'
        }]
        template_df = pd.DataFrame(template_data)
        csv_template = template_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV 템플릿 다운로드",
            data=csv_template,
            file_name="제품_템플릿.csv",
            mime="text/csv"
        )
        
        # CSV 파일 업로드
        st.write("### 📤 CSV 파일 업로드")
        uploaded_file = st.file_uploader("CSV 파일을 선택하세요", type=['csv'])
        
        if uploaded_file is not None:
            required_columns = ['product_code', 'product_name', 'category', 'unit', 'unit_price', 'unit_price_vnd', 'supplier', 'stock_quantity', 'description']
            new_products_data = process_csv_upload(uploaded_file, required_columns)
            
            if new_products_data:
                st.write("### 📋 업로드 데이터 미리보기")
                preview_df = pd.DataFrame(new_products_data)
                st.dataframe(preview_df)
                
                if st.button("💾 제품 데이터 저장", use_container_width=True):
                    success_count = 0
                    for product_data in new_products_data:
                        result = insert_data_to_supabase('products', product_data)
                        if result:
                            success_count += 1
                    
                    if success_count > 0:
                        st.success(f"✅ {success_count}개의 제품이 성공적으로 등록되었습니다!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ 제품 데이터 저장 중 오류가 발생했습니다.")

# 직원 관리
def employee_management():
    """직원 관리 페이지"""
    st.header("👨‍💼 직원 관리")
    
    tab1, tab2 = st.tabs(["📝 직원 등록", "📋 직원 목록"])
    
    with tab1:
        st.subheader("새 직원 등록")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름")
            username = st.text_input("사용자명 (로그인용)")
            password = st.text_input("비밀번호", type="password")
            department = st.selectbox("부서", ["총무", "영업", "생산", "품질", "구매", "관리", "시스템관리"])
        
        with col2:
            position = st.text_input("직책")
            email = st.text_input("이메일")
            phone = st.text_input("연락처")
            is_admin = st.checkbox("관리자 권한")
        
        notes = st.text_area("비고")
        
        if st.button("직원 등록", use_container_width=True):
            if name and username and password:
                new_employee = {
                    'name': name,
                    'username': username,
                    'password': password,
                    'department': department,
                    'position': position,
                    'email': email,
                    'phone': phone,
                    'is_admin': is_admin,
                    'is_active': True,
                    'notes': notes
                }
                
                result = insert_data_to_supabase('employees', new_employee)
                if result:
                    st.success("직원이 성공적으로 등록되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("직원 등록 중 오류가 발생했습니다.")
            else:
                st.error("이름, 사용자명, 비밀번호는 필수 입력 사항입니다.")
    
    with tab2:
        st.subheader("직원 목록")
        
        employees = load_data_from_supabase('employees', '*')
        
        if employees:
            # 필터 및 다운로드
            col1, col2 = st.columns(2)
            with col1:
                filter_department = st.selectbox("부서 필터", ["전체"] + ["총무", "영업", "생산", "품질", "구매", "관리", "시스템관리"])
            with col2:
                # 비밀번호 제외하고 다운로드
                download_employees = []
                for emp in employees:
                    emp_copy = emp.copy()
                    emp_copy.pop('password', None)  # 비밀번호 제거
                    download_employees.append(emp_copy)
                download_csv(download_employees, "직원목록")
            
            # 필터 적용
            filtered_employees = employees.copy()
            if filter_department != "전체":
                filtered_employees = [e for e in filtered_employees if e.get('department') == filter_department]
            
            # 직원 목록 표시
            for employee in sorted(filtered_employees, key=lambda x: x.get('created_at', ''), reverse=True):
                status_icon = "✅" if employee.get('is_active', True) else "❌"
                admin_icon = "👑" if employee.get('is_admin', False) else ""
                
                with st.expander(f"{status_icon} {admin_icon} {employee.get('name')} - {employee.get('department')} ({employee.get('position')})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**ID**: {employee.get('id')}")
                        st.write(f"**이름**: {employee.get('name')}")
                        st.write(f"**사용자명**: {employee.get('username')}")
                        st.write(f"**부서**: {employee.get('department')}")
                    
                    with col2:
                        st.write(f"**직책**: {employee.get('position')}")
                        st.write(f"**이메일**: {employee.get('email')}")
                        st.write(f"**연락처**: {employee.get('phone')}")
                        st.write(f"**관리자**: {'예' if employee.get('is_admin') else '아니오'}")
                    
                    with col3:
                        st.write(f"**상태**: {'활성' if employee.get('is_active', True) else '비활성'}")
                        st.write(f"**등록일**: {employee.get('created_at', '')[:10]}")
                        if employee.get('notes'):
                            st.write(f"**비고**: {employee.get('notes')}")
                    
                    # 수정/삭제 버튼
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_status = not employee.get('is_active', True)
                        status_text = "비활성화" if employee.get('is_active', True) else "활성화"
                        if st.button(f"🔄 {status_text}", key=f"toggle_employee_{employee['id']}"):
                            update_data_in_supabase('employees', {'is_active': new_status}, 'id', employee['id'])
                            st.cache_data.clear()
                            st.rerun()
                    with col2:
                        pass  # 공간 확보
                    with col3:
                        # Master 계정은 삭제 불가
                        if employee.get('username') != 'Master':
                            if st.button(f"❌ 삭제", key=f"delete_employee_{employee['id']}"):
                                if delete_data_from_supabase('employees', 'id', employee['id']):
                                    st.success("직원이 삭제되었습니다.")
                                    st.cache_data.clear()
                                    st.rerun()
                        else:
                            st.write("*시스템 계정*")
        else:
            st.info("등록된 직원이 없습니다.")

# 시스템 관리
def system_management():
    """시스템 관리 페이지"""
    st.header("⚙️ 시스템 관리")
    
    tab1, tab2 = st.tabs(["🏢 회사 정보", "💱 환율 관리"])
    
    with tab1:
        st.subheader("회사 기본 정보")
        
        company_info = load_data_from_supabase('company_info', '*')
        
        if company_info:
            company_data = company_info[0]
        else:
            company_data = {}
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("회사명", value=company_data.get('company_name', ''))
            address = st.text_area("주소", value=company_data.get('address', ''))
            phone = st.text_input("전화번호", value=company_data.get('phone', ''))
            email = st.text_input("이메일", value=company_data.get('email', ''))
        
        with col2:
            tax_number = st.text_input("사업자등록번호", value=company_data.get('tax_number', ''))
            ceo_name = st.text_input("대표자명", value=company_data.get('ceo_name', ''))
            business_type = st.text_input("업종", value=company_data.get('business_type', ''))
            notes = st.text_area("비고", value=company_data.get('notes', ''))
        
        if st.button("💾 회사 정보 저장", use_container_width=True):
            new_company_data = {
                'company_name': company_name,
                'address': address,
                'phone': phone,
                'email': email,
                'tax_number': tax_number,
                'ceo_name': ceo_name,
                'business_type': business_type,
                'notes': notes
            }
            
            if company_info:
                # 업데이트
                if update_data_in_supabase('company_info', new_company_data, 'id', company_info[0]['id']):
                    st.success("회사 정보가 성공적으로 수정되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
            else:
                # 새로 생성
                if insert_data_to_supabase('company_info', new_company_data):
                    st.success("회사 정보가 성공적으로 저장되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
    
    with tab2:
        st.subheader("환율 관리")
        
        # 환율 등록
        col1, col2, col3 = st.columns(3)
        with col1:
            from_currency = st.selectbox("기준 통화", ["USD", "VND", "KRW"])
        with col2:
            to_currency = st.selectbox("대상 통화", ["VND", "USD", "KRW"])
        with col3:
            rate = st.number_input("환율", min_value=0.0, format="%.4f")
        
        if st.button("환율 등록"):
            if from_currency != to_currency and rate > 0:
                new_rate = {
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'rate': rate,
                    'effective_date': date.today().isoformat(),
                    'created_by': st.session_state.current_user['id']
                }
                
                if insert_data_to_supabase('exchange_rates', new_rate):
                    st.success("환율이 등록되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
        
        # 등록된 환율 목록
        st.write("### 등록된 환율")
        exchange_rates = load_data_from_supabase('exchange_rates', '*')
        if exchange_rates:
            download_csv(exchange_rates, "환율목록")
            for rate in sorted(exchange_rates, key=lambda x: x.get('effective_date', ''), reverse=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{rate['from_currency']} → {rate['to_currency']}**: {rate['rate']:,.4f} (적용일: {rate['effective_date']})")
                with col2:
                    if st.button(f"❌ 삭제", key=f"delete_rate_{rate['id']}"):
                        if delete_data_from_supabase('exchange_rates', 'id', rate['id']):
                            st.success("환율이 삭제되었습니다.")
                            st.cache_data.clear()
                            st.rerun()
        else:
            st.info("등록된 환율이 없습니다.")

# 메인 애플리케이션
def main():
    """메인 애플리케이션"""
    
    # 로그인 확인
    if not login_system():
        return
    
    # 사이드바 메뉴
    with st.sidebar:
        st.markdown(f"""
        ### 👋 환영합니다!
        **{st.session_state.current_user['name']}**님  
        ({st.session_state.current_user['department']} - {st.session_state.current_user['position']})
        
        🔗 **Supabase 연결됨**
        """)
        
        st.divider()
        
        menu = st.selectbox(
            "📋 메뉴 선택",
            [
                "🏠 대시보드",
                "📦 구매품 관리", 
                "💰 지출 요청서",
                "📋 견적서 관리",
                "👥 고객 관리",
                "📦 제품 관리", 
                "👨‍💼 직원 관리",
                "⚙️ 시스템 관리"
            ]
        )
        
        st.divider()
        
        # 시스템 정보
        st.write("### ℹ️ 시스템 정보")
        st.write(f"**버전**: v2.1.0 (Supabase)")
        st.write(f"**로그인 시간**: {datetime.now().strftime('%H:%M')}")
        st.write(f"**DB**: 연결됨 ✅")
        
        # 빠른 통계
        st.write("### 📊 빠른 통계")
        purchases = load_data_from_supabase('purchases', 'id')
        expenses = load_data_from_supabase('expenses', 'id')
        quotations = load_data_from_supabase('quotations', 'id')
        customers = load_data_from_supabase('customers', 'id')
        products = load_data_from_supabase('products', 'id')
        employees = load_data_from_supabase('employees', 'id', {'is_active': True})
        
        st.metric("구매품", len(purchases))
        st.metric("지출요청", len(expenses))
        st.metric("견적서", len(quotations))
        st.metric("고객", len(customers))
        st.metric("제품", len(products))
        st.metric("직원", len(employees))
    
    # 메인 컨텐츠
    if menu == "🏠 대시보드":
        dashboard()
    elif menu == "📦 구매품 관리":
        purchase_management()
    elif menu == "💰 지출 요청서":
        expense_management()
    elif menu == "📋 견적서 관리":
        quotation_management()
    elif menu == "👥 고객 관리":
        customer_management()
    elif menu == "📦 제품 관리":
        product_management()
    elif menu == "👨‍💼 직원 관리":
        employee_management()
    elif menu == "⚙️ 시스템 관리":
        system_management()

if __name__ == "__main__":
    main()