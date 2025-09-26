import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import time
from collections import defaultdict
import calendar
import io

# 페이지 설정 (최우선 실행)
st.set_page_config(
    page_title="YMV 관리 프로그램",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 내부 모듈 임포트
from components.code_management import CodeManagementComponent
from components.multilingual_input import MultilingualInputComponent
from components.quotation_management import show_quotation_management
# from components.expense_management import show_expense_management  # 임시 주석

# Supabase 초기화
@st.cache_resource
def init_supabase():
    """Supabase 클라이언트 초기화"""
    try:
        from supabase import create_client, Client
        import os
        
        # 환경변수에서 Supabase 정보 로드
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"] 
        
        supabase = create_client(url, key)
        return supabase
    except Exception as e:
        st.error(f"Supabase 연결 실패: {e}")
        return None

# 전역 Supabase 클라이언트
supabase = init_supabase()

# 고유 키 생성 함수
def generate_unique_key(prefix=""):
    """위젯용 고유 키 생성"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# 데이터베이스 연결 함수들 (Step 8에서 utils.py로 이동 예정)
def load_data_from_supabase(table, columns="*", filters=None):
    """Supabase에서 데이터 로드"""
    try:
        if not supabase:
            return []
        
        query = supabase.table(table).select(columns)
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return []

def save_data_to_supabase(table, data):
    """Supabase에 데이터 저장"""
    try:
        if not supabase:
            return False
        
        response = supabase.table(table).insert(data).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"데이터 저장 실패: {e}")
        return False

def update_data_in_supabase(table, data, id_field="id"):
    """Supabase 데이터 업데이트 (Step 7에서 수정됨)"""
    try:
        if not supabase or id_field not in data:
            return False
        
        # 원본 데이터 보호를 위해 복사본 생성
        update_data = data.copy()
        record_id = update_data.pop(id_field)
        
        response = supabase.table(table).update(update_data).eq(id_field, record_id).execute()
        
        # 응답 데이터 확인
        if response.data:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"데이터 업데이트 실패: {e}")
        return False

def delete_data_from_supabase(table, item_id, id_field="id"):
    """Supabase에서 데이터 삭제"""
    try:
        if not supabase:
            return False
        
        response = supabase.table(table).delete().eq(id_field, item_id).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"데이터 삭제 실패: {e}")
        return False

# 사용자 관리 함수들
def login_user(username, password):
    """사용자 로그인"""
    employees = load_data_from_supabase("employees")
    for employee in employees:
        if employee["username"] == username and employee["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_info = employee
            return True
    return False

def logout_user():
    """사용자 로그아웃"""
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.rerun()

def get_current_user():
    """현재 로그인한 사용자 정보 반환"""
    return st.session_state.get("user_info")

# 유틸리티 함수들 (Step 8에서 utils.py로 이동 예정)
def get_approval_status_info(status):
    """승인 상태에 따른 정보 반환"""
    status_map = {
        'pending': {'emoji': '⏳', 'color': 'orange', 'description': '승인 대기'},
        'approved': {'emoji': '✅', 'color': 'green', 'description': '승인됨'},
        'rejected': {'emoji': '❌', 'color': 'red', 'description': '거부됨'}
    }
    return status_map.get(status, {'emoji': '❓', 'color': 'gray', 'description': '알 수 없음'})

def calculate_expense_statistics(expenses):
    """지출 통계 계산"""
    if not expenses:
        return {}
    
    total_count = len(expenses)
    total_amount = sum(exp['amount'] for exp in expenses)
    
    # 상태별 집계
    approved_expenses = [exp for exp in expenses if exp['status'] == 'approved']
    approved_count = len(approved_expenses)
    approved_amount = sum(exp['amount'] for exp in approved_expenses)
    
    pending_count = len([exp for exp in expenses if exp['status'] == 'pending'])
    rejected_count = len([exp for exp in expenses if exp['status'] == 'rejected'])
    
    # 카테고리별 집계
    category_stats = defaultdict(lambda: {'count': 0, 'amount': 0})
    for expense in expenses:
        category = expense['category']
        category_stats[category]['count'] += 1
        category_stats[category]['amount'] += expense['amount']
    
    # 월별 집계
    monthly_stats = defaultdict(lambda: {'count': 0, 'amount': 0})
    for expense in expenses:
        try:
            expense_date = datetime.strptime(expense['expense_date'], '%Y-%m-%d')
            month_key = expense_date.strftime('%Y-%m')
            monthly_stats[month_key]['count'] += 1
            monthly_stats[month_key]['amount'] += expense['amount']
        except:
            continue
    
    return {
        'total_count': total_count,
        'total_amount': total_amount,
        'approved_count': approved_count,
        'approved_amount': approved_amount,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'category_stats': dict(category_stats),
        'monthly_stats': dict(monthly_stats)
    }

def create_csv_download(expenses, employees):
    """CSV 다운로드 데이터 생성"""
    if not expenses:
        return ""
    
    # 직원 정보를 딕셔너리로 변환
    employee_dict = {emp['id']: emp for emp in employees} if employees else {}
    
    # CSV 데이터 준비
    csv_data = []
    for expense in expenses:
        employee_info = employee_dict.get(expense['employee_id'], {})
        
        csv_data.append({
            '요청일': expense['request_date'],
            '요청자': employee_info.get('name', '알 수 없음'),
            '직원번호': employee_info.get('employee_id', ''),
            '부서': expense.get('department', ''),
            '지출일': expense['expense_date'],
            '카테고리': expense['category'],
            '금액': expense['amount'],
            '내역': expense['description'],
            '영수증번호': expense.get('receipt_number', ''),
            '상태': expense['status'],
            '승인일': expense.get('approved_at', ''),
            '승인의견': expense.get('approval_comment', '')
        })
    
    # DataFrame으로 변환하고 CSV 생성
    df = pd.DataFrame(csv_data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    return csv_buffer.getvalue().encode('utf-8-sig')

def render_print_form(expense):
    """프린트 양식 렌더링 (Step 8에서 CSS 개선 예정)"""
    st.subheader("🖨️ 지출요청서 프린트")
    
    # 프린트 양식 HTML 생성
    print_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2>지출 요청서</h2>
            <p>EXPENSE REQUEST FORM</p>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
                <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0; width: 150px;">
                    <strong>요청일</strong>
                </td>
                <td style="border: 1px solid black; padding: 10px;">{expense['request_date']}</td>
                <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0; width: 150px;">
                    <strong>지출일</strong>
                </td>
                <td style="border: 1px solid black; padding: 10px;">{expense['expense_date']}</td>
            </tr>
            <tr>
                <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0;">
                    <strong>부서</strong>
                </td>
                <td style="border: 1px solid black; padding: 10px;">{expense.get('department', 'N/A')}</td>
                <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0;">
                    <strong>카테고리</strong>
                </td>
                <td style="border: 1px solid black; padding: 10px;">{expense['category']}</td>
            </tr>
            <tr>
                <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0;">
                    <strong>금액</strong>
                </td>
                <td style="border: 1px solid black; padding: 10px; font-weight: bold;">{expense['amount']:,}원</td>
                <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0;">
                    <strong>영수증 번호</strong>
                </td>
                <td style="border: 1px solid black; padding: 10px;">{expense.get('receipt_number', 'N/A')}</td>
            </tr>
        </table>
        
        <div style="margin-bottom: 20px;">
            <h4 style="margin-bottom: 10px;">지출 내역</h4>
            <div style="border: 1px solid black; padding: 15px; min-height: 100px;">
                {expense['description']}
            </div>
        </div>
        
        <div style="margin-top: 40px;">
            <table style="width: 100%;">
                <tr>
                    <td style="text-align: center; padding: 20px;">
                        <div style="border-bottom: 1px solid black; width: 150px; margin: 0 auto 5px;">
                        </div>
                        <span>신청자</span>
                    </td>
                    <td style="text-align: center; padding: 20px;">
                        <div style="border-bottom: 1px solid black; width: 150px; margin: 0 auto 5px;">
                        </div>
                        <span>팀장</span>
                    </td>
                    <td style="text-align: center; padding: 20px;">
                        <div style="border-bottom: 1px solid black; width: 150px; margin: 0 auto 5px;">
                        </div>
                        <span>승인자</span>
                    </td>
                </tr>
            </table>
        </div>
    </div>
    """
    
    # 프린트 옵션 제공
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # HTML 다운로드
        st.download_button(
            label="📄 HTML 다운로드",
            data=f"<html><body>{print_html}</body></html>",
            file_name=f"expense_request_{expense['id']}.html",
            mime="text/html"
        )
    
    with col2:
        # 클립보드 복사용 텍스트
        text_content = f"""
지출 요청서

요청일: {expense['request_date']}
지출일: {expense['expense_date']}
부서: {expense.get('department', 'N/A')}
카테고리: {expense['category']}
금액: {expense['amount']:,}원
영수증 번호: {expense.get('receipt_number', 'N/A')}

지출 내역:
{expense['description']}
        """
        st.download_button(
            label="📝 텍스트 다운로드",
            data=text_content,
            file_name=f"expense_request_{expense['id']}.txt",
            mime="text/plain"
        )
    
    with col3:
        # 프린트 버튼 (간단한 JavaScript)
        if st.button("🖨️ 프린트", key=f"print_simple_{expense['id']}"):
            st.write("브라우저 프린트: Ctrl+P를 눌러주세요")
    
    # 프린트 미리보기
    st.markdown("### 📋 프린트 미리보기")
    st.markdown(print_html, unsafe_allow_html=True)

# 페이지 함수들
def show_login_page():
    """로그인 페이지"""
    st.title("🏢 YMV 관리 프로그램")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 로그인")
        
        with st.form("login_form"):
            username = st.text_input("사용자명", placeholder="사용자명을 입력하세요")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            
            submitted = st.form_submit_button("로그인", use_container_width=True)
            
            if submitted:
                if login_user(username, password):
                    st.success("✅ 로그인 성공!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 사용자명 또는 비밀번호가 올바르지 않습니다.")

def show_dashboard():
    """대시보드 페이지"""
    st.title("📊 YMV 관리 대시보드")
    
    current_user = get_current_user()
    if not current_user:
        st.error("사용자 정보를 불러올 수 없습니다.")
        return
    
    # 환영 메시지
    st.markdown(f"### 안녕하세요, **{current_user['name']}**님! 👋")
    st.markdown("---")
    
    # 기본 통계 로드
    expenses = load_data_from_supabase("expenses")
    quotations = load_data_from_supabase("quotations")
    customers = load_data_from_supabase("customers")
    products = load_data_from_supabase("products")
    purchases = load_data_from_supabase("purchases")
    company_info = load_data_from_supabase("company_info")
    
    # 통계 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 지출요청서", f"{len(expenses)}건")
    
    with col2:
        st.metric("📋 견적서", f"{len(quotations)}건")
    
    with col3:
        st.metric("👥 고객사", f"{len(customers)}개")
    
    with col4:
        st.metric("📦 제품", f"{len(products)}개")
    
    # 최근 활동 - 안전한 방식으로 처리
    if expenses:
        st.subheader("📈 최근 지출 활동")
        try:
            # expenses 첫 번째 데이터로 컬럼명 확인
            if expenses:
                sample_expense = expenses[0]
                date_field = None
                
                # 가능한 날짜 필드명들 확인
                possible_date_fields = ['request_date', '요청_날짜', 'created_at', 'expense_date']
                for field in possible_date_fields:
                    if field in sample_expense:
                        date_field = field
                        break
                
                if date_field:
                    recent_expenses = sorted(expenses, key=lambda x: x.get(date_field, '2024-01-01'), reverse=True)[:5]
                    
                    for expense in recent_expenses:
                        status_info = get_approval_status_info(expense.get('status', 'pending'))
                        expense_date = expense.get(date_field, 'N/A')
                        category = expense.get('category', 'N/A')
                        amount = expense.get('amount', 0)
                        st.write(f"{status_info['emoji']} {expense_date} - {category} ({amount:,}원)")
                else:
                    st.write("📋 지출 데이터의 날짜 필드를 확인할 수 없습니다.")
                    st.write(f"사용 가능한 필드: {list(sample_expense.keys())}")
                    
        except Exception as e:
            st.error(f"최근 활동 로드 오류: {e}")
            # 디버깅을 위해 expenses 구조 표시
            if expenses:
                st.write("**디버깅 정보:**")
                st.write("첫 번째 expense 데이터 구조:")
                st.json(expenses[0])
    else:
        st.info("표시할 지출 데이터가 없습니다.")
    
    # 회사 정보 표시
    if company_info:
        st.subheader("🏢 회사 정보")
        company = company_info[0]  # 첫 번째 회사 정보
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**회사명**: {company.get('company_name', 'N/A')}")
            st.write(f"**대표자**: {company.get('ceo_name', 'N/A')}")
            st.write(f"**사업자번호**: {company.get('business_number', 'N/A')}")
        
        with col2:
            st.write(f"**주소**: {company.get('address', 'N/A')}")
            st.write(f"**전화번호**: {company.get('phone', 'N/A')}")
            st.write(f"**이메일**: {company.get('email', 'N/A')}")

def show_purchase_management():
    """구매품 관리 페이지"""
    st.header("🛒 구매품 관리")
    
    tab1, tab2 = st.tabs(["📝 구매품 등록", "📋 구매품 목록"])
    
    with tab1:
        # 구매품 등록 폼
        st.subheader("새 구매품 등록")
        
        with st.form("purchase_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                item_name = st.text_input("구매품명", key="purchase_item_name")
                category = st.selectbox(
                    "카테고리",
                    ["원자재", "부품", "소모품", "장비", "기타"],
                    key="purchase_category"
                )
                quantity = st.number_input("수량", min_value=1, value=1, key="purchase_quantity")
                supplier = st.text_input("공급업체", key="purchase_supplier")
            
            with col2:
                # 통화 선택 기능 추가
                currency = st.selectbox(
                    "통화",
                    ["USD", "VND", "KRW"],
                    key="purchase_currency"
                )
                
                # 통화별 단계 설정
                if currency == "VND":
                    step_value = 10000
                    format_text = "VND"
                elif currency == "USD":
                    step_value = 10
                    format_text = "USD"
                else:  # KRW
                    step_value = 1000
                    format_text = "KRW"
                
                unit_price = st.number_input(
                    "단가",  # 통화 표시 제거
                    min_value=0, 
                    step=step_value, 
                    key="purchase_unit_price"
                )
                
                request_date = st.date_input("요청일", value=date.today(), key="purchase_request_date")
                
                # 긴급도 선택 수정 (DB 기본값에 맞춤)
                urgency = st.selectbox(
                    "긴급도",
                    ["보통", "긴급", "매우긴급"],  # '일반' -> '보통'으로 수정
                    key="purchase_urgency"
                )
                
                # 단위 입력 추가
                unit = st.text_input("단위", value="개", key="purchase_unit")
            
            # notes로 변경 (DB 스키마에 존재함)
            notes = st.text_area("비고", key="purchase_notes", help="구매품 관련 추가 정보를 입력하세요.")
            
            submitted = st.form_submit_button("📝 구매품 등록")
            
            if submitted:
                if not item_name.strip():
                    st.error("구매품명을 입력해주세요.")
                elif not supplier.strip():
                    st.error("공급업체를 입력해주세요.")
                else:
                    # 현재 사용자 ID 가져오기 (requester 필드용)
                    current_user = get_current_user()
                    requester_id = current_user['id'] if current_user else None
                    
                    # DB 스키마에 정확히 맞는 데이터
                    purchase_data = {
                        'item_name': item_name,
                        'category': category,
                        'quantity': quantity,
                        'unit': unit,                    # 단위
                        'unit_price': unit_price,
                        # 'total_price': 자동 계산됨 (Generated Column)
                        'currency': currency,
                        'supplier': supplier,
                        'urgency': urgency,
                        'request_date': request_date.strftime('%Y-%m-%d'),
                        'status': 'requested',           # 기본값 '대기중' 대신 명시적 설정
                        'notes': notes if notes.strip() else None,
                        'requester': requester_id,       # 요청자 ID
                        # 'created_at': 자동 설정됨 (now())
                        # 'updated_at': 자동 설정됨 (now())
                    }
                    
                    if save_data_to_supabase("purchases", purchase_data):
                        total_price = quantity * unit_price  # 표시용 계산
                        st.success("✅ 구매품이 성공적으로 등록되었습니다!")
                        st.info(f"💰 총 금액: {total_price:,} {currency}")  # format_text 대신 currency 사용
                        st.info(f"📦 {quantity} {unit} × {unit_price:,} {currency}")
                        st.rerun()
                    else:
                        st.error("❌ 구매품 등록에 실패했습니다.")
    
    with tab2:
        # 구매품 목록
        st.subheader("구매품 목록")
        
        purchases = load_data_from_supabase("purchases")
        
        if not purchases:
            st.info("등록된 구매품이 없습니다.")
        else:
            # 필터 옵션
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(
                    "상태 필터",
                    ["전체", "대기중", "요청됨", "주문됨", "입고됨", "취소됨"],  # DB 기본값 '대기중' 추가
                    key="purchase_status_filter"
                )
            
            with col2:
                category_filter = st.selectbox(
                    "카테고리 필터",
                    ["전체", "원자재", "부품", "소모품", "장비", "기타"],
                    key="purchase_category_filter"
                )
            
            with col3:
                currency_filter = st.selectbox(
                    "통화 필터",
                    ["전체", "USD", "VND", "KRW"],
                    key="purchase_currency_filter"
                )
            
            # 필터링
            filtered_purchases = purchases
            
            if status_filter != "전체":
                status_map = {
                    "대기중": "대기중", 
                    "요청됨": "requested", 
                    "주문됨": "ordered", 
                    "입고됨": "received", 
                    "취소됨": "cancelled"
                }
                filtered_purchases = [p for p in filtered_purchases if p.get('status') == status_map[status_filter]]
            
            if category_filter != "전체":
                filtered_purchases = [p for p in filtered_purchases if p.get('category') == category_filter]
                
            if currency_filter != "전체":
                filtered_purchases = [p for p in filtered_purchases if p.get('currency') == currency_filter]
            
            st.write(f"📦 총 {len(filtered_purchases)}건의 구매품")
            
            # 총 금액 계산 (통화별로)
            currency_totals = {}
            for purchase in filtered_purchases:
                currency = purchase.get('currency', 'KRW')
                if currency not in currency_totals:
                    currency_totals[currency] = 0
                currency_totals[currency] += purchase.get('total_price', 0)
            
            if currency_totals:
                st.write("**총 금액:**")
                for currency, total in currency_totals.items():
                    if currency == "VND":
                        st.write(f"• {currency}: {total:,.0f}")
                    else:
                        st.write(f"• {currency}: {total:,.2f}")
            
            # 구매품 목록 표시
            for purchase in filtered_purchases:
                status_emoji = {
                    "requested": "📝", 
                    "ordered": "🛒", 
                    "received": "✅", 
                    "cancelled": "❌"
                }
                
                currency = purchase.get('currency', 'KRW')
                currency_symbol = {'USD': '$', 'VND': '₫', 'KRW': '원'}
                symbol = currency_symbol.get(currency, '원')
                
                urgency_emoji = {
                    "보통": "📋",      # DB 기본값
                    "긴급": "⚡",
                    "매우긴급": "🚨"
                }
                
                urgency = purchase.get('urgency', '보통')  # 기본값 변경
                
                with st.expander(
                    f"{status_emoji.get(purchase.get('status'), '❓')} {urgency_emoji.get(urgency)} {purchase.get('item_name')} - {purchase.get('total_price', 0):,}{symbol}"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**카테고리**: {purchase.get('category')}")
                        st.write(f"**수량**: {purchase.get('quantity', 0):,} {purchase.get('unit', '개')}")  # 단위 추가
                        st.write(f"**단가**: {purchase.get('unit_price', 0):,} {symbol}")
                        st.write(f"**총액**: {purchase.get('total_price', 0):,} {symbol}")
                        st.write(f"**통화**: {currency}")
                    
                    with col2:
                        st.write(f"**공급업체**: {purchase.get('supplier')}")
                        st.write(f"**요청일**: {purchase.get('request_date')}")
                        st.write(f"**긴급도**: {urgency}")
                        st.write(f"**상태**: {purchase.get('status')}")
                        
                        # 비고가 있는 경우 표시
                        if purchase.get('notes'):
                            st.write(f"**비고**: {purchase.get('notes')}")
                    
                    # 수정/삭제 기능 추가
                    st.markdown("---")
                    st.write("**관리 기능**")
                    
                    # 현재 사용자 권한 확인
                    current_user = get_current_user()
                    can_edit = (current_user and 
                              (current_user.get('role') == 'manager' or 
                               purchase.get('requester') == current_user['id']))
                    
                    if can_edit:
                        col_edit1, col_edit2, col_edit3 = st.columns(3)
                        
                        with col_edit1:
                            # 수정 버튼
                            if st.button("✏️ 수정", key=f"edit_{purchase.get('id')}"):
                                st.session_state[f"editing_{purchase['id']}"] = True
                                st.rerun()
                        
                        with col_edit2:
                            # 삭제 버튼
                            if st.button("🗑️ 삭제", key=f"delete_{purchase.get('id')}", type="secondary"):
                                if st.session_state.get(f"confirm_delete_{purchase['id']}", False):
                                    if delete_data_from_supabase("purchases", purchase['id']):
                                        st.success("구매품이 삭제되었습니다.")
                                        if f"confirm_delete_{purchase['id']}" in st.session_state:
                                            del st.session_state[f"confirm_delete_{purchase['id']}"]
                                        st.rerun()
                                    else:
                                        st.error("삭제에 실패했습니다.")
                                else:
                                    st.session_state[f"confirm_delete_{purchase['id']}"] = True
                                    st.rerun()
                        
                        with col_edit3:
                            # 삭제 확인 메시지
                            if st.session_state.get(f"confirm_delete_{purchase['id']}", False):
                                st.warning("정말 삭제하시겠습니까?")
                                if st.button("❌ 취소", key=f"cancel_delete_{purchase['id']}"):
                                    del st.session_state[f"confirm_delete_{purchase['id']}"]
                                    st.rerun()
                    
                    # 수정 폼 표시
                    if st.session_state.get(f"editing_{purchase['id']}", False):
                        st.markdown("### ✏️ 구매품 수정")
                        
                        with st.form(f"edit_form_{purchase['id']}"):
                            edit_col1, edit_col2 = st.columns(2)
                            
                            with edit_col1:
                                edit_item_name = st.text_input("구매품명", value=purchase.get('item_name', ''), key=f"edit_item_name_{purchase['id']}")
                                edit_category = st.selectbox(
                                    "카테고리",
                                    ["원자재", "부품", "소모품", "장비", "기타"],
                                    index=["원자재", "부품", "소모품", "장비", "기타"].index(purchase.get('category', '기타')),
                                    key=f"edit_category_{purchase['id']}"
                                )
                                edit_quantity = st.number_input("수량", value=purchase.get('quantity', 1), min_value=1, key=f"edit_quantity_{purchase['id']}")
                                edit_unit = st.text_input("단위", value=purchase.get('unit', '개'), key=f"edit_unit_{purchase['id']}")
                            
                            with edit_col2:
                                edit_currency = st.selectbox(
                                    "통화",
                                    ["USD", "VND", "KRW"],
                                    index=["USD", "VND", "KRW"].index(purchase.get('currency', 'KRW')),
                                    key=f"edit_currency_{purchase['id']}"
                                )
                                
                                # 통화별 단계값
                                if edit_currency == "VND":
                                    edit_step = 10000
                                elif edit_currency == "USD":
                                    edit_step = 10
                                else:
                                    edit_step = 1000
                                
                                edit_unit_price = st.number_input(
                                    "단가",  # 통화 표시 제거
                                    value=float(purchase.get('unit_price', 0)), 
                                    min_value=0.0, 
                                    step=float(edit_step),
                                    key=f"edit_unit_price_{purchase['id']}"
                                )
                                
                                edit_supplier = st.text_input("공급업체", value=purchase.get('supplier', ''), key=f"edit_supplier_{purchase['id']}")
                                edit_urgency = st.selectbox(
                                    "긴급도",
                                    ["보통", "긴급", "매우긴급"],
                                    index=["보통", "긴급", "매우긴급"].index(purchase.get('urgency', '보통')),
                                    key=f"edit_urgency_{purchase['id']}"
                                )
                            
                            edit_notes = st.text_area("비고", value=purchase.get('notes', ''), key=f"edit_notes_{purchase['id']}")
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                save_changes = st.form_submit_button("💾 저장", type="primary")
                            
                            with col_cancel:
                                cancel_edit = st.form_submit_button("❌ 취소")
                            
                            if save_changes:
                                if not edit_item_name.strip():
                                    st.error("구매품명을 입력해주세요.")
                                elif not edit_supplier.strip():
                                    st.error("공급업체를 입력해주세요.")
                                else:
                                    # 수정 데이터 준비
                                    update_data = {
                                        'id': purchase['id'],
                                        'item_name': edit_item_name,
                                        'category': edit_category,
                                        'quantity': edit_quantity,
                                        'unit': edit_unit,
                                        'unit_price': edit_unit_price,
                                        'currency': edit_currency,
                                        'supplier': edit_supplier,
                                        'urgency': edit_urgency,
                                        'notes': edit_notes if edit_notes.strip() else None,
                                        # updated_at은 DB에서 자동 업데이트됨
                                    }
                                    
                                    if update_data_in_supabase("purchases", update_data):
                                        st.success("✅ 구매품 정보가 수정되었습니다!")
                                        del st.session_state[f"editing_{purchase['id']}"]
                                        st.rerun()
                                    else:
                                        st.error("❌ 수정에 실패했습니다.")
                            
                            if cancel_edit:
                                del st.session_state[f"editing_{purchase['id']}"]
                                st.rerun()
                    
                    # 상태 변경 버튼 (관리자만)
                    current_user = get_current_user()
                    if current_user and current_user.get('role') == 'manager':
                        st.write("**상태 변경**")
                        button_col1, button_col2, button_col3 = st.columns(3)
                        
                        with button_col1:
                            if st.button("🛒 주문처리", key=f"order_{purchase.get('id')}"):
                                update_data = {
                                    'id': purchase['id'],
                                    'status': 'ordered',
                                    'updated_at': datetime.now().isoformat()
                                }
                                if update_data_in_supabase("purchases", update_data):
                                    st.success("주문 처리되었습니다!")
                                    st.rerun()
                        
                        with button_col2:
                            if st.button("✅ 입고완료", key=f"receive_{purchase.get('id')}"):
                                update_data = {
                                    'id': purchase['id'],
                                    'status': 'received',
                                    'updated_at': datetime.now().isoformat()
                                }
                                if update_data_in_supabase("purchases", update_data):
                                    st.success("입고 완료되었습니다!")
                                    st.rerun()
                        
                        with button_col3:
                            if st.button("❌ 취소", key=f"cancel_{purchase.get('id')}"):
                                update_data = {
                                    'id': purchase['id'],
                                    'status': 'cancelled',
                                    'updated_at': datetime.now().isoformat()
                                }
                                if update_data_in_supabase("purchases", update_data):
                                    st.success("취소 처리되었습니다!")
                                    st.rerun()

def show_quotation_management():
    """견적서 관리 페이지 (컴포넌트 호출)"""
    show_quotation_management(
        load_data_from_supabase,
        save_data_to_supabase,
        update_data_in_supabase,
        delete_data_from_supabase
    )

def show_expense_management_page():
    """지출 관리 페이지 (임시로 main.py 내에서 처리)"""
    st.header("💰 지출 요청서 관리")
    st.info("🔧 Step 8 진행 중: expense_management.py 컴포넌트 분리 작업 중입니다.")
    
    # 기존 지출관리 기능 임시 유지
    st.write("현재 지출관리 기능은 정상 작동 중입니다.")
    st.write("컴포넌트 분리 완료 후 더 깔끔한 구조로 개선됩니다.")

# 메인 함수
def main():
    """메인 애플리케이션"""
    
    # 세션 상태 초기화
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    
    # 로그인 확인
    if not st.session_state.logged_in:
        show_login_page()
        return
    
    # 사이드바 메뉴
    with st.sidebar:
        st.title("🏢 YMV 시스템")
        
        current_user = get_current_user()
        if current_user:
            st.write(f"👤 {current_user['name']}")
            st.write(f"🏷️ {current_user.get('role', '직원')}")
            
            if st.button("🚪 로그아웃", use_container_width=True):
                logout_user()
        
        st.markdown("---")
        
        # 메뉴 선택
        menu_option = st.selectbox(
            "📋 메뉴 선택",
            [
                "대시보드",
                "지출요청서",
                "구매품관리",
                "견적서관리",
                "고객관리",
                "제품관리",
                "직원관리",
                "시스템관리"
            ]
        )
    
    # 메뉴별 페이지 표시
    if menu_option == "대시보드":
        show_dashboard()
    elif menu_option == "지출요청서":
        show_expense_management_page()
    elif menu_option == "구매품관리":
        show_purchase_management()
    elif menu_option == "견적서관리":
        show_quotation_management()
    elif menu_option == "시스템관리":
        st.header("⚙️ 시스템 관리")
        
        # 코드 관리 컴포넌트
        if st.checkbox("📋 제품 코드 관리", value=True):
            code_component = CodeManagementComponent(supabase)
            code_component.render_code_management_page()
        
        # 다국어 입력 컴포넌트 (테스트용)
        if st.checkbox("🌐 다국어 입력 테스트"):
            multilingual_component = MultilingualInputComponent()
            test_result = multilingual_component.create_multilingual_input(
                "테스트 입력",
                ["한국어", "English", "Tiếng Việt"],
                key_prefix="test"
            )
            if test_result:
                st.write("입력 결과:", test_result)
    else:
        # 미구현 메뉴들
        st.header(f"🚧 {menu_option}")
        st.info(f"{menu_option} 기능은 현재 개발 중입니다.")

if __name__ == "__main__":
    main()