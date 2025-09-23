import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import time
from collections import defaultdict
import calendar
import io

# 컴포넌트 임포트
from components.code_management import CodeManagementComponent
from components.multilingual_input import MultilingualInputComponent

# 페이지 설정
st.set_page_config(
    page_title="YMV 관리 프로그램 v4.0",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 (프린트 지원 포함)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2e6da4);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stats-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin-bottom: 1rem;
    }
    .expense-stats-card {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .warning-stats-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    .ceo-approval-card {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin-bottom: 1rem;
    }
    .month-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #6c757d;
    }
    .expense-table {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 프린트 전용 스타일 */
    @media print {
        .main-header, .sidebar, button, .stButton, .stSelectbox, .stTabs {
            display: none !important;
        }
        .print-form {
            display: block !important;
            page-break-inside: avoid;
        }
        .print-header {
            text-align: center;
            margin-bottom: 2rem;
            border-bottom: 2px solid #000;
            padding-bottom: 1rem;
        }
        .print-content {
            font-size: 12pt;
            line-height: 1.5;
        }
        .print-signature {
            margin-top: 3rem;
            display: flex;
            justify-content: space-between;
        }
        .print-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        .print-table th, .print-table td {
            border: 1px solid #000;
            padding: 8px;
            text-align: left;
        }
        body { margin: 1cm; }
    }
    
    .print-form {
        display: none;
        background: white;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Supabase 연결 설정
@st.cache_resource
def init_supabase():
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase 연결 실패: {e}")
        return None

supabase = init_supabase()

# 유틸리티 함수들
def generate_unique_key(prefix=""):
    """고유한 위젯 키 생성"""
    timestamp = str(int(time.time() * 1000))
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{unique_id}"

def load_data_from_supabase(table, columns="*", filters=None):
    """Supabase에서 데이터 로드"""
    if not supabase:
        return []
    
    try:
        query = supabase.table(table).select(columns)
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"데이터 로드 실패 ({table}): {e}")
        return []

def save_data_to_supabase(table, data):
    """Supabase에 데이터 저장"""
    if not supabase:
        return False
    
    try:
        response = supabase.table(table).insert(data).execute()
        return True
    except Exception as e:
        st.error(f"데이터 저장 실패 ({table}): {e}")
        return False

def update_data_in_supabase(table, data, id_field="id"):
    """Supabase에서 데이터 업데이트"""
    if not supabase:
        return False
    
    try:
        item_id = data.pop(id_field)
        response = supabase.table(table).update(data).eq(id_field, item_id).execute()
        return True
    except Exception as e:
        st.error(f"데이터 업데이트 실패 ({table}): {e}")
        return False

def delete_data_from_supabase(table, item_id, id_field="id"):
    """Supabase에서 데이터 삭제"""
    if not supabase:
        return False
    
    try:
        response = supabase.table(table).delete().eq(id_field, item_id).execute()
        return True
    except Exception as e:
        st.error(f"데이터 삭제 실패 ({table}): {e}")
        return False

def get_current_user():
    """현재 로그인한 사용자 정보 반환"""
    if 'user_id' in st.session_state:
        users = load_data_from_supabase('employees', '*', {'id': st.session_state.user_id})
        return users[0] if users else None
    return None

def get_approval_status_info(status):
    """승인 상태별 정보 반환"""
    status_info = {
        '대기중': {'emoji': '📝', 'color': '#6c757d', 'description': '직원이 작성한 초기 상태'},
        'CEO승인대기': {'emoji': '👔', 'color': '#ff9800', 'description': 'CEO 승인 필요'},
        '승인됨': {'emoji': '✅', 'color': '#28a745', 'description': 'CEO 승인 완료'},
        '지급완료': {'emoji': '💰', 'color': '#17a2b8', 'description': '실제 지급 완료'},
        '인보이스 확인완료': {'emoji': '📋', 'color': '#007bff', 'description': '최종 인보이스 확인 완료'},
        '반려됨': {'emoji': '❌', 'color': '#dc3545', 'description': 'CEO가 반려'}
    }
    return status_info.get(status, {'emoji': '❓', 'color': '#6c757d', 'description': '알 수 없음'})

def calculate_expense_statistics(expenses):
    """지출 통계 계산"""
    if not expenses:
        return {}
    
    # 현재 날짜
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    current_year = str(now.year)
    
    stats = {
        'total_count': len(expenses),
        'total_amount_usd': 0,
        'total_amount_vnd': 0,
        'total_amount_krw': 0,
        'current_month_amount_usd': 0,
        'current_year_amount_usd': 0,
        'by_type': defaultdict(lambda: {'count': 0, 'amount': 0}),
        'by_status': defaultdict(lambda: {'count': 0, 'amount': 0}),
        'by_month': defaultdict(lambda: {'count': 0, 'amount_usd': 0, 'amount_vnd': 0, 'amount_krw': 0}),
        'pending_count': 0,
        'ceo_approval_waiting': 0,
        'approved_count': 0,
        'completed_count': 0,
        'rejected_count': 0,
        'invoice_confirmed_count': 0
    }
    
    for expense in expenses:
        amount = expense.get('amount', 0)
        currency = expense.get('currency', 'USD')
        expense_type = expense.get('expense_type', '기타')
        status = expense.get('status', '대기중')
        expense_date = expense.get('expense_date', '')
        
        # 총 금액 (통화별)
        if currency == 'USD':
            stats['total_amount_usd'] += amount
        elif currency == 'VND':
            stats['total_amount_vnd'] += amount
        elif currency == 'KRW':
            stats['total_amount_krw'] += amount
        
        # 월별/연도별 통계
        if expense_date:
            try:
                expense_month = expense_date[:7]  # YYYY-MM
                expense_year = expense_date[:4]   # YYYY
                
                if currency == 'USD':
                    stats['by_month'][expense_month]['amount_usd'] += amount
                elif currency == 'VND':
                    stats['by_month'][expense_month]['amount_vnd'] += amount
                elif currency == 'KRW':
                    stats['by_month'][expense_month]['amount_krw'] += amount
                
                stats['by_month'][expense_month]['count'] += 1
                
                # 현재 월/연도 통계
                if expense_month == current_month and currency == 'USD':
                    stats['current_month_amount_usd'] += amount
                if expense_year == current_year and currency == 'USD':
                    stats['current_year_amount_usd'] += amount
            except:
                pass
        
        # 유형별 통계 (USD 기준)
        if currency == 'USD':
            stats['by_type'][expense_type]['count'] += 1
            stats['by_type'][expense_type]['amount'] += amount
        
        # 상태별 통계
        stats['by_status'][status]['count'] += 1
        if currency == 'USD':
            stats['by_status'][status]['amount'] += amount
        
        # 상태별 카운트 (CEO 승인 워크플로우)
        if status == '대기중':
            stats['pending_count'] += 1
        elif status == 'CEO승인대기':
            stats['ceo_approval_waiting'] += 1
        elif status == '승인됨':
            stats['approved_count'] += 1
        elif status == '지급완료':
            stats['completed_count'] += 1
        elif status == '인보이스 확인완료':
            stats['invoice_confirmed_count'] += 1
        elif status == '반려됨':
            stats['rejected_count'] += 1
    
    return stats

def create_csv_download(expenses, employees):
    """CSV 다운로드 데이터 생성 - 한글 깨짐 완전 해결"""
    if not expenses:
        return None
    
    employee_dict = {emp['id']: emp['name'] for emp in employees}
    
    # CSV용 데이터 가공
    csv_data = []
    for expense in expenses:
        csv_data.append({
            '지출일': expense.get('expense_date', ''),
            '지출유형': expense.get('expense_type', ''),
            '금액': expense.get('amount', 0),
            '통화': expense.get('currency', ''),
            '결제방법': expense.get('payment_method', ''),
            '거래처': expense.get('vendor', ''),
            '사업목적': expense.get('purpose', ''),
            '지출내역': expense.get('description', ''),
            '상태': expense.get('status', ''),
            '요청자': employee_dict.get(expense.get('requester'), 'N/A'),
            '등록일': expense.get('created_at', '')[:10]
        })
    
    # DataFrame 생성
    df = pd.DataFrame(csv_data)
    
    # CSV 생성 (BOM 포함)
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    csv_string = output.getvalue()
    
    # BOM 추가
    csv_bytes = '\ufeff' + csv_string
    
    return csv_bytes.encode('utf-8')

def render_print_form(expense):
    """프린트 가능한 지출 요청서 양식"""
    employee_dict = {emp['id']: emp['name'] for emp in load_data_from_supabase('employees')}
    requester_name = employee_dict.get(expense.get('requester'), 'N/A')
    
    status_info = get_approval_status_info(expense.get('status', '대기중'))
    
    print_html = f"""
    <div class="print-form" id="print-form-{expense.get('id')}">
        <div class="print-header">
            <h1>YMV 지출 요청서</h1>
            <p>요청번호: EXP-{expense.get('id'):04d} | 작성일: {expense.get('created_at', '')[:10]}</p>
        </div>
        
        <div class="print-content">
            <table class="print-table">
                <tr>
                    <th width="20%">요청자</th>
                    <td width="30%">{requester_name}</td>
                    <th width="20%">지출일</th>
                    <td width="30%">{expense.get('expense_date', 'N/A')}</td>
                </tr>
                <tr>
                    <th>지출유형</th>
                    <td>{expense.get('expense_type', 'N/A')}</td>
                    <th>금액</th>
                    <td>{expense.get('amount', 0):,.2f} {expense.get('currency', 'USD')}</td>
                </tr>
                <tr>
                    <th>결제방법</th>
                    <td>{expense.get('payment_method', 'N/A')}</td>
                    <th>거래처</th>
                    <td>{expense.get('vendor', 'N/A')}</td>
                </tr>
                <tr>
                    <th>상태</th>
                    <td colspan="3">{status_info['emoji']} {expense.get('status', 'N/A')}</td>
                </tr>
            </table>
            
            <div style="margin: 1rem 0;">
                <strong>사업 목적:</strong><br>
                {expense.get('purpose', 'N/A')}
            </div>
            
            <div style="margin: 1rem 0;">
                <strong>지출 내역:</strong><br>
                {expense.get('description', 'N/A')}
            </div>
            
            <div class="print-signature">
                <div>
                    <p>요청자 서명</p>
                    <p>_________________</p>
                    <p>{requester_name}</p>
                </div>
                <div>
                    <p>CEO 승인</p>
                    <p>_________________</p>
                    <p>날짜: __________</p>
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(print_html, unsafe_allow_html=True)
    
    # 프린트 버튼
    if st.button(f"🖨️ 프린트", key=f"print_{expense.get('id')}"):
        st.markdown("""
        <script>
        setTimeout(function() {
            window.print();
        }, 100);
        </script>
        """, unsafe_allow_html=True)
        st.success("프린트 창이 열렸습니다. 인쇄를 완료해주세요.")

# 인증 함수들
def login_user(username, password):
    """사용자 로그인"""
    employees = load_data_from_supabase('employees')
    for emp in employees:
        if emp['username'] == username and emp['password'] == password and emp['is_active']:
            st.session_state.user_id = emp['id']
            st.session_state.username = emp['username']
            st.session_state.is_admin = emp['is_admin']
            st.session_state.logged_in = True
            return True
    return False

def logout_user():
    """사용자 로그아웃"""
    for key in ['user_id', 'username', 'is_admin', 'logged_in']:
        if key in st.session_state:
            del st.session_state[key]

# 로그인 페이지
def show_login_page():
    """로그인 페이지 표시"""
    st.markdown('<div class="main-header"><h1>🏢 YMV 관리 프로그램 v4.0</h1><p>베트남 소재 한국 기업을 위한 통합 비즈니스 관리 시스템</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("🔐 로그인")
            username = st.text_input("사용자명", placeholder="사용자명을 입력하세요")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            
            if st.form_submit_button("로그인", use_container_width=True):
                if username and password:
                    if login_user(username, password):
                        st.success("로그인 성공!")
                        st.rerun()
                    else:
                        st.error("로그인 정보가 올바르지 않습니다.")
                else:
                    st.error("사용자명과 비밀번호를 입력해주세요.")
        
        with st.expander("💡 기본 계정 정보"):
            st.info("""
            **기본 관리자 계정:**
            - 사용자명: Master
            - 비밀번호: 1023
            
            **v4.0 새로운 기능:**
            - 🏷️ 제품 코드 관리 시스템
            - 🌍 다국어 제품명 지원 (영어/베트남어)
            - 📋 다국어 견적서 출력
            - 👔 CEO 승인 워크플로우
            """)

# 대시보드
def show_dashboard():
    """대시보드 페이지"""
    user = get_current_user()
    if not user:
        st.error("사용자 정보를 불러올 수 없습니다.")
        return
    
    st.markdown(f'<div class="main-header"><h1>🏠 대시보드</h1><p>환영합니다, {user["name"]}님!</p></div>', unsafe_allow_html=True)
    
    # 통계 정보 로드
    purchases = load_data_from_supabase('purchases')
    expenses = load_data_from_supabase('expenses')
    quotations = load_data_from_supabase('quotations')
    customers = load_data_from_supabase('customers')
    products = load_data_from_supabase('products')
    employees = load_data_from_supabase('employees')
    product_codes = load_data_from_supabase('product_codes', '*', {'is_active': True})
    
    # 지출 통계 계산
    expense_stats = calculate_expense_statistics(expenses)
    
    # 상단 통계 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3>📦 구매품</h3>
            <h2>{len(purchases)}건</h2>
            <p>대기중: {len([p for p in purchases if p.get('status') == '대기중'])}건</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <h3>💰 지출요청</h3>
            <h2>{len(expenses)}건</h2>
            <p>CEO 승인대기: {expense_stats.get('ceo_approval_waiting', 0)}건</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <h3>📋 견적서</h3>
            <h2>{len(quotations)}건</h2>
            <p>발송됨: {len([q for q in quotations if q.get('status') == '발송됨'])}건</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <h3>🏷️ 제품코드</h3>
            <h2>{len(product_codes)}개</h2>
            <p>v4.0 신규 기능</p>
        </div>
        """, unsafe_allow_html=True)
    
    # CEO 승인 대기 알림 (관리자만)
    if user.get('is_admin') and expense_stats.get('ceo_approval_waiting', 0) > 0:
        st.markdown(f"""
        <div class="ceo-approval-card">
            <h3>👔 CEO 승인 필요</h3>
            <h2>{expense_stats.get('ceo_approval_waiting', 0)}건</h2>
            <p>승인이 필요한 지출 요청서가 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # v4.0 새 기능 소개
    st.markdown("### 🆕 v4.0 새로운 기능")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **🏷️ 제품 코드 관리**
        - 7단계 체계적 제품 코드 시스템
        - HR-01-02-ST-KR-00 형식
        - 카테고리 기반 자동 생성
        """)
    
    with col2:
        st.info("""
        **🌍 다국어 제품명**
        - 영어/베트남어 제품명 지원
        - 현지 고객 맞춤 견적서
        - 언어별 우선순위 표시
        """)
    
    with col3:
        st.info("""
        **👔 CEO 승인 워크플로우**
        - 4단계 승인 프로세스
        - 프린트 가능한 공식 양식
        - 승인 이력 추적
        """)

# 지출 요청서 관리
def show_expense_management():
    """지출 요청서 관리 페이지"""
    st.markdown('<div class="main-header"><h1>💰 지출 요청서 관리</h1></div>', unsafe_allow_html=True)
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📝 지출 요청서 작성", "📋 지출 요청서 목록", "📊 비용 통계", "👔 CEO 승인"])
    
    with tab1:
        st.subheader("새 지출 요청서 작성")
        
        with st.form("expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                expense_type = st.selectbox("지출 유형", [
                    "출장비", "사무용품", "접대비", "교육비", "교통비", 
                    "식비", "통신비", "장비구입", "유지보수", "마케팅", "기타"
                ])
                
                expense_date = st.date_input("지출 예정일", value=datetime.now().date())
                
                amount = st.number_input("금액", min_value=0.0, format="%.2f")
                
                currency = st.selectbox("통화", ["USD", "VND", "KRW"])
            
            with col2:
                payment_method = st.selectbox("결제 방법", [
                    "현금", "법인카드", "계좌이체", "수표"
                ])
                
                vendor = st.text_input("거래처/공급업체")
                
                purpose = st.text_area("사업 목적", placeholder="지출의 목적과 사유를 입력하세요")
                
                # 일반 직원은 '대기중'만 선택 가능, 관리자는 모든 상태 선택 가능
                user = get_current_user()
                if user and user.get('is_admin'):
                    status = st.selectbox("상태", ["대기중", "CEO승인대기", "승인됨", "지급완료", "반려됨", "인보이스 확인완료"])
                else:
                    status = st.selectbox("상태", ["대기중", "CEO승인대기"])
            
            description = st.text_area("지출 내역", placeholder="상세한 지출 내역을 입력하세요")
            
            if st.form_submit_button("지출 요청서 등록", use_container_width=True):
                if expense_type and amount > 0 and description:
                    user = get_current_user()
                    if user:
                        new_expense = {
                            'expense_type': expense_type,
                            'expense_date': expense_date.isoformat(),
                            'amount': amount,
                            'currency': currency,
                            'payment_method': payment_method,
                            'vendor': vendor,
                            'purpose': purpose,
                            'description': description,
                            'status': status,
                            'requester': user['id'],
                            'created_at': datetime.now().isoformat()
                        }
                        
                        if save_data_to_supabase('expenses', new_expense):
                            st.success("✅ 지출 요청서가 등록되었습니다!")
                            st.rerun()
                        else:
                            st.error("❌ 지출 요청서 등록에 실패했습니다.")
                    else:
                        st.error("❌ 사용자 정보를 확인할 수 없습니다.")
                else:
                    st.error("❌ 필수 항목을 입력해주세요.")
    
    with tab2:
        st.subheader("지출 요청서 목록")
        
        # 필터링 및 정렬 옵션
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            filter_type = st.selectbox("유형 필터", 
                ["전체"] + ["출장비", "사무용품", "접대비", "교육비", "교통비", 
                "식비", "통신비", "장비구입", "유지보수", "마케팅", "기타"],
                key=generate_unique_key("expense_type"))
        
        with col2:
            filter_status = st.selectbox("상태 필터", 
                ["전체"] + ["대기중", "CEO승인대기", "승인됨", "지급완료", "반려됨", "인보이스 확인완료"],
                key=generate_unique_key("expense_status"))
        
        with col3:
            sort_order = st.selectbox("정렬 기준", 
                ["지출일 최신순", "지출일 오래된순", "금액 높은순", "금액 낮은순"],
                key=generate_unique_key("expense_sort"))
        
        with col4:
            # CSV 다운로드 버튼
            expenses_for_csv = load_data_from_supabase('expenses')
            employees_for_csv = load_data_from_supabase('employees')
            
            if expenses_for_csv:
                csv_data = create_csv_download(expenses_for_csv, employees_for_csv)
                st.download_button(
                    label="📁 CSV 다운로드",
                    data=csv_data,
                    file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key=generate_unique_key("download_expenses")
                )
        
        # 데이터 로드 및 처리
        expenses = load_data_from_supabase('expenses')
        employees = load_data_from_supabase('employees')
        
        if not expenses:
            st.info("등록된 지출 요청서가 없습니다.")
            return
        
        # 직원 정보 매핑
        employee_dict = {emp['id']: emp['name'] for emp in employees}
        
        # 데이터 가공
        for expense in expenses:
            expense['requester_name'] = employee_dict.get(expense.get('requester'), 'N/A')
            # 날짜 형식 처리
            expense_date = expense.get('expense_date', '')
            if expense_date:
                try:
                    expense['expense_date_formatted'] = datetime.fromisoformat(expense_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                    expense['month_key'] = expense['expense_date_formatted'][:7]  # YYYY-MM
                except:
                    expense['expense_date_formatted'] = expense_date[:10] if len(expense_date) >= 10 else expense_date
                    expense['month_key'] = expense_date[:7] if len(expense_date) >= 7 else 'N/A'
            else:
                expense['expense_date_formatted'] = 'N/A'
                expense['month_key'] = 'N/A'
        
        # 필터링
        filtered_expenses = expenses
        
        if filter_type != "전체":
            filtered_expenses = [e for e in filtered_expenses if e.get('expense_type') == filter_type]
        
        if filter_status != "전체":
            filtered_expenses = [e for e in filtered_expenses if e.get('status') == filter_status]
        
        # 정렬
        if sort_order == "지출일 최신순":
            filtered_expenses = sorted(filtered_expenses, key=lambda x: x.get('expense_date', ''), reverse=True)
        elif sort_order == "지출일 오래된순":
            filtered_expenses = sorted(filtered_expenses, key=lambda x: x.get('expense_date', ''))
        elif sort_order == "금액 높은순":
            filtered_expenses = sorted(filtered_expenses, key=lambda x: x.get('amount', 0), reverse=True)
        elif sort_order == "금액 낮은순":
            filtered_expenses = sorted(filtered_expenses, key=lambda x: x.get('amount', 0))
        
        # 엑셀 형태 테이블로 표시
        if filtered_expenses:
            st.markdown('<div class="expense-table">', unsafe_allow_html=True)
            
            # 테이블 데이터 준비
            table_data = []
            for expense in filtered_expenses:
                status_info = get_approval_status_info(expense.get('status', '대기중'))
                
                table_data.append({
                    '지출일': expense['expense_date_formatted'],
                    '유형': expense.get('expense_type', 'N/A'),
                    '금액': f"{expense.get('amount', 0):,.0f} {expense.get('currency', '')}",
                    '거래처': expense.get('vendor', 'N/A'),
                    '결제방법': expense.get('payment_method', 'N/A'),
                    '상태': f"{status_info['emoji']} {expense.get('status', 'N/A')}",
                    '요청자': expense['requester_name']
                })
            
            # DataFrame 생성 및 표시
            df = pd.DataFrame(table_data)
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    '지출일': st.column_config.DateColumn("지출일", width="medium"),
                    '유형': st.column_config.TextColumn("유형", width="medium"),
                    '금액': st.column_config.TextColumn("금액", width="medium"),
                    '거래처': st.column_config.TextColumn("거래처", width="medium"),
                    '결제방법': st.column_config.TextColumn("결제방법", width="medium"),
                    '상태': st.column_config.TextColumn("상태", width="medium"),
                    '요청자': st.column_config.TextColumn("요청자", width="small")
                }
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 월단위 상세 정보 표시
            st.markdown("### 📅 월단위 상세 정보")
            
            # 월별 그룹핑
            monthly_expenses = defaultdict(list)
            for expense in filtered_expenses:
                month_key = expense['month_key']
                monthly_expenses[month_key].append(expense)
            
            # 월별 정렬 (최신순)
            sorted_months = sorted(monthly_expenses.keys(), reverse=True)
            
            for month in sorted_months:
                if month == 'N/A':
                    continue
                    
                month_expenses = monthly_expenses[month]
                month_total_usd = sum(e.get('amount', 0) for e in month_expenses if e.get('currency') == 'USD')
                month_total_vnd = sum(e.get('amount', 0) for e in month_expenses if e.get('currency') == 'VND')
                month_total_krw = sum(e.get('amount', 0) for e in month_expenses if e.get('currency') == 'KRW')
                
                # 월 이름 변환
                try:
                    year, month_num = month.split('-')
                    month_name = calendar.month_name[int(month_num)]
                    display_month = f"{year}년 {month_name}"
                except:
                    display_month = month
                
                with st.expander(f"📅 {display_month} ({len(month_expenses)}건)", expanded=False):
                    # 월별 요약
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if month_total_usd > 0:
                            st.metric("USD 총액", f"${month_total_usd:,.2f}")
                    with col2:
                        if month_total_vnd > 0:
                            st.metric("VND 총액", f"₫{month_total_vnd:,.0f}")
                    with col3:
                        if month_total_krw > 0:
                            st.metric("KRW 총액", f"₩{month_total_krw:,.0f}")
                    
                    # 월별 상세 목록
                    for idx, expense in enumerate(month_expenses):
                        expense_id = expense.get('id')
                        status_info = get_approval_status_info(expense.get('status', '대기중'))
                        
                        st.markdown(f"""
                        **{status_info['emoji']} {expense.get('expense_type', 'N/A')}** - {expense['expense_date_formatted']} - {expense.get('amount', 0):,.0f} {expense.get('currency', '')}
                        """)
                        
                        col1, col2, col3 = st.columns([2, 2, 2])
                        
                        with col1:
                            st.write(f"거래처: {expense.get('vendor', 'N/A')}")
                            st.write(f"결제방법: {expense.get('payment_method', 'N/A')}")
                        
                        with col2:
                            st.write(f"상태: {expense.get('status', 'N/A')}")
                            st.write(f"요청자: {expense['requester_name']}")
                        
                        with col3:
                            # 액션 버튼들
                            button_col1, button_col2, button_col3, button_col4 = st.columns(4)
                            
                            with button_col1:
                                if st.button("📝", key=f"edit_btn_{expense_id}_{idx}", help="수정"):
                                    st.session_state[f"edit_expense_{expense_id}"] = True
                                    st.rerun()
                            
                            with button_col2:
                                if st.button("🔄", key=f"status_btn_{expense_id}_{idx}", help="상태변경"):
                                    st.session_state[f"change_status_{expense_id}"] = True
                                    st.rerun()
                            
                            with button_col3:
                                if st.button("🖨️", key=f"print_btn_{expense_id}_{idx}", help="프린트"):
                                    st.session_state[f"show_print_{expense_id}"] = True
                                    st.rerun()
                            
                            with button_col4:
                                if st.button("❌", key=f"delete_btn_{expense_id}_{idx}", help="삭제"):
                                    if delete_data_from_supabase('expenses', expense_id):
                                        st.success("✅ 삭제되었습니다!")
                                        st.rerun()
                        
                        # 상세 정보
                        if expense.get('purpose'):
                            st.write(f"**사업 목적:** {expense.get('purpose')}")
                        if expense.get('description'):
                            st.write(f"**지출 내역:** {expense.get('description')}")
                        
                        # 프린트 폼 표시 (조건부)
                        if st.session_state.get(f"show_print_{expense_id}", False):
                            st.markdown("---")
                            st.markdown("### 🖨️ 지출 요청서 출력")
                            render_print_form(expense)
                            if st.button("❌ 닫기", key=f"close_print_{expense_id}"):
                                st.session_state[f"show_print_{expense_id}"] = False
                                st.rerun()
                        
                        # 수정 폼 (조건부 표시)
                        if st.session_state.get(f"edit_expense_{expense_id}", False):
                            st.markdown("---")
                            st.markdown("### ✏️ 지출 요청서 수정")
                            
                            with st.form(f"edit_expense_form_{expense_id}"):
                                edit_col1, edit_col2 = st.columns(2)
                                
                                with edit_col1:
                                    edit_expense_type = st.selectbox("지출 유형", 
                                        ["출장비", "사무용품", "접대비", "교육비", "교통비", "식비", "통신비", "장비구입", "유지보수", "마케팅", "기타"],
                                        index=["출장비", "사무용품", "접대비", "교육비", "교통비", "식비", "통신비", "장비구입", "유지보수", "마케팅", "기타"].index(expense.get('expense_type', '기타')))
                                    
                                    try:
                                        edit_expense_date = st.date_input("지출 예정일", value=datetime.fromisoformat(expense.get('expense_date', datetime.now().isoformat())).date())
                                    except:
                                        edit_expense_date = st.date_input("지출 예정일", value=datetime.now().date())
                                    
                                    edit_amount = st.number_input("금액", value=expense.get('amount', 0.0), format="%.2f")
                                    edit_currency = st.selectbox("통화", ["USD", "VND", "KRW"], index=["USD", "VND", "KRW"].index(expense.get('currency', 'USD')))
                                
                                with edit_col2:
                                    edit_payment_method = st.selectbox("결제 방법", 
                                        ["현금", "법인카드", "계좌이체", "수표"],
                                        index=["현금", "법인카드", "계좌이체", "수표"].index(expense.get('payment_method', '현금')))
                                    
                                    edit_vendor = st.text_input("거래처/공급업체", value=expense.get('vendor', ''))
                                    edit_purpose = st.text_area("사업 목적", value=expense.get('purpose', ''))
                                    
                                    user = get_current_user()
                                    if user and user.get('is_admin'):
                                        edit_status = st.selectbox("상태", 
                                            ["대기중", "CEO승인대기", "승인됨", "지급완료", "반려됨", "인보이스 확인완료"],
                                            index=["대기중", "CEO승인대기", "승인됨", "지급완료", "반려됨", "인보이스 확인완료"].index(expense.get('status', '대기중')))
                                    else:
                                        edit_status = st.selectbox("상태", 
                                            ["대기중", "CEO승인대기"],
                                            index=["대기중", "CEO승인대기"].index(expense.get('status', '대기중')) if expense.get('status') in ["대기중", "CEO승인대기"] else 0)
                                
                                edit_description = st.text_area("지출 내역", value=expense.get('description', ''))
                                
                                submit_col1, submit_col2 = st.columns(2)
                                with submit_col1:
                                    if st.form_submit_button("💾 수정 저장", use_container_width=True):
                                        update_data = {
                                            'id': expense_id,
                                            'expense_type': edit_expense_type,
                                            'expense_date': edit_expense_date.isoformat(),
                                            'amount': edit_amount,
                                            'currency': edit_currency,
                                            'payment_method': edit_payment_method,
                                            'vendor': edit_vendor,
                                            'purpose': edit_purpose,
                                            'description': edit_description,
                                            'status': edit_status,
                                            'updated_at': datetime.now().isoformat()
                                        }
                                        
                                        if update_data_in_supabase('expenses', update_data):
                                            st.success("✅ 수정이 완료되었습니다!")
                                            st.session_state[f"edit_expense_{expense_id}"] = False
                                            st.rerun()
                                        else:
                                            st.error("❌ 수정에 실패했습니다.")
                                
                                with submit_col2:
                                    if st.form_submit_button("❌ 취소", use_container_width=True):
                                        st.session_state[f"edit_expense_{expense_id}"] = False
                                        st.rerun()
                        
                        # 상태 변경 폼 (조건부 표시)
                        if st.session_state.get(f"change_status_{expense_id}", False):
                            st.markdown("---")
                            st.markdown("### 🔄 상태 변경")
                            
                            with st.form(f"status_change_form_{expense_id}"):
                                user = get_current_user()
                                if user and user.get('is_admin'):
                                    status_options = ["대기중", "CEO승인대기", "승인됨", "지급완료", "반려됨", "인보이스 확인완료"]
                                else:
                                    status_options = ["대기중", "CEO승인대기"]
                                
                                new_status = st.selectbox("새 상태 선택", 
                                    status_options,
                                    index=status_options.index(expense.get('status', '대기중')) if expense.get('status') in status_options else 0)
                                
                                status_col1, status_col2 = st.columns(2)
                                with status_col1:
                                    if st.form_submit_button("💾 상태 변경", use_container_width=True):
                                        status_update_data = {
                                            'id': expense_id,
                                            'status': new_status,
                                            'updated_at': datetime.now().isoformat()
                                        }
                                        
                                        if update_data_in_supabase('expenses', status_update_data):
                                            st.success(f"✅ 상태가 '{new_status}'으로 변경되었습니다!")
                                            st.session_state[f"change_status_{expense_id}"] = False
                                            st.rerun()
                                        else:
                                            st.error("❌ 상태 변경에 실패했습니다.")
                                
                                with status_col2:
                                    if st.form_submit_button("❌ 취소", use_container_width=True):
                                        st.session_state[f"change_status_{expense_id}"] = False
                                        st.rerun()
                        
                        st.markdown("---")
        else:
            st.info("조건에 맞는 지출 요청서가 없습니다.")
    
    with tab3:
        st.subheader("📊 비용 사용현황 통계")
        
        # 데이터 로드
        expenses = load_data_from_supabase('expenses')
        
        if not expenses:
            st.info("통계를 표시할 지출 요청서가 없습니다.")
            return
        
        # 통계 계산
        stats = calculate_expense_statistics(expenses)
        
        # 상단 요약 통계
        st.markdown("### 📈 전체 요약")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="expense-stats-card">
                <h3>📝 총 건수</h3>
                <h2>{stats['total_count']}건</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="expense-stats-card">
                <h3>💰 USD 총액</h3>
                <h2>${stats['total_amount_usd']:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="expense-stats-card">
                <h3>💴 VND 총액</h3>
                <h2>₫{stats['total_amount_vnd']:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="expense-stats-card">
                <h3>💸 KRW 총액</h3>
                <h2>₩{stats['total_amount_krw']:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # 승인 워크플로우 현황
        st.markdown("### 👔 승인 워크플로우 현황")
        flow_col1, flow_col2, flow_col3, flow_col4, flow_col5, flow_col6 = st.columns(6)
        
        with flow_col1:
            st.markdown(f"""
            <div class="warning-stats-card">
                <h4>📝 대기중</h4>
                <h3>{stats['pending_count']}건</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with flow_col2:
            st.markdown(f"""
            <div class="ceo-approval-card">
                <h4>👔 CEO승인대기</h4>
                <h3>{stats['ceo_approval_waiting']}건</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with flow_col3:
            st.markdown(f"""
            <div class="expense-stats-card">
                <h4>✅ 승인됨</h4>
                <h3>{stats['approved_count']}건</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with flow_col4:
            st.markdown(f"""
            <div class="expense-stats-card">
                <h4>💰 지급완료</h4>
                <h3>{stats['completed_count']}건</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with flow_col5:
            st.markdown(f"""
            <div class="expense-stats-card">
                <h4>📋 인보이스완료</h4>
                <h3>{stats['invoice_confirmed_count']}건</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with flow_col6:
            st.markdown(f"""
            <div class="error-message">
                <h4>❌ 반려됨</h4>
                <h3>{stats['rejected_count']}건</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # 유형별 통계
        st.markdown("### 📊 지출 유형별 통계 (USD)")
        if stats['by_type']:
            type_data = []
            for expense_type, data in stats['by_type'].items():
                type_data.append({
                    '지출유형': expense_type,
                    '건수': data['count'],
                    '금액': f"${data['amount']:,.2f}"
                })
            
            type_df = pd.DataFrame(type_data)
            st.dataframe(type_df, use_container_width=True, hide_index=True)
        
        # 월별 추이
        st.markdown("### 📅 월별 지출 추이")
        if stats['by_month']:
            month_data = []
            sorted_months = sorted(stats['by_month'].keys())
            
            for month in sorted_months:
                data = stats['by_month'][month]
                month_data.append({
                    '월': month,
                    '건수': data['count'],
                    'USD': data['amount_usd'],
                    'VND': data['amount_vnd'],
                    'KRW': data['amount_krw']
                })
            
            month_df = pd.DataFrame(month_data)
            st.dataframe(month_df, use_container_width=True, hide_index=True)
            
            # 차트로 표시
            if len(month_data) > 0:
                st.markdown("### 📈 월별 USD 지출 차트")
                st.line_chart(month_df.set_index('월')['USD'])
    
    with tab4:
        st.subheader("👔 CEO 승인 관리")
        
        user = get_current_user()
        if not user or not user.get('is_admin'):
            st.warning("CEO 승인 기능은 관리자만 사용할 수 있습니다.")
            return
        
        # CEO 승인 대기 목록
        expenses = load_data_from_supabase('expenses')
        employees = load_data_from_supabase('employees')
        employee_dict = {emp['id']: emp['name'] for emp in employees}
        
        # CEO 승인 대기 건만 필터링
        pending_expenses = [e for e in expenses if e.get('status') == 'CEO승인대기']
        
        if not pending_expenses:
            st.info("CEO 승인 대기 중인 지출 요청서가 없습니다.")
            return
        
        st.markdown(f"### 📋 승인 대기 목록 ({len(pending_expenses)}건)")
        
        for idx, expense in enumerate(pending_expenses):
            expense_id = expense.get('id')
            requester_name = employee_dict.get(expense.get('requester'), 'N/A')
            
            with st.expander(f"👔 EXP-{expense_id:04d} - {expense.get('expense_type', 'N/A')} - {expense.get('amount', 0):,.0f} {expense.get('currency', 'USD')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # 지출 요청서 정보
                    st.write(f"**요청자:** {requester_name}")
                    st.write(f"**지출일:** {expense.get('expense_date', 'N/A')}")
                    st.write(f"**지출유형:** {expense.get('expense_type', 'N/A')}")
                    st.write(f"**금액:** {expense.get('amount', 0):,.2f} {expense.get('currency', 'USD')}")
                    st.write(f"**거래처:** {expense.get('vendor', 'N/A')}")
                    st.write(f"**결제방법:** {expense.get('payment_method', 'N/A')}")
                    
                    if expense.get('purpose'):
                        st.write(f"**사업목적:** {expense.get('purpose')}")
                    if expense.get('description'):
                        st.write(f"**지출내역:** {expense.get('description')}")
                
                with col2:
                    st.markdown("**CEO 승인 결정**")
                    
                    # 승인 버튼
                    if st.button("✅ 승인", key=f"approve_{expense_id}_{idx}", use_container_width=True):
                        status_update = {
                            'id': expense_id,
                            'status': '승인됨',
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        if update_data_in_supabase('expenses', status_update):
                            st.success("✅ 승인이 완료되었습니다!")
                            st.rerun()
                        else:
                            st.error("❌ 승인 처리에 실패했습니다.")
                    
                    # 반려 버튼
                    if st.button("❌ 반려", key=f"reject_{expense_id}_{idx}", use_container_width=True):
                        status_update = {
                            'id': expense_id,
                            'status': '반려됨',
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        if update_data_in_supabase('expenses', status_update):
                            st.success("❌ 반려 처리가 완료되었습니다!")
                            st.rerun()
                        else:
                            st.error("❌ 반려 처리에 실패했습니다.")
                    
                    # 프린트 버튼
                    if st.button("🖨️ 출력", key=f"print_approval_{expense_id}_{idx}", use_container_width=True):
                        st.session_state[f"show_approval_print_{expense_id}"] = True
                        st.rerun()
                
                # 승인용 프린트 폼 (조건부)
                if st.session_state.get(f"show_approval_print_{expense_id}", False):
                    st.markdown("---")
                    st.markdown("### 🖨️ CEO 승인용 지출 요청서")
                    render_print_form(expense)
                    if st.button("❌ 닫기", key=f"close_approval_print_{expense_id}"):
                        st.session_state[f"show_approval_print_{expense_id}"] = False
                        st.rerun()

# 구매품 관리 (기존과 동일)
def show_purchase_management():
    """구매품 관리 페이지"""
    st.markdown('<div class="main-header"><h1>📦 구매품 관리</h1></div>', unsafe_allow_html=True)
    
    # 탭 구성
    tab1, tab2 = st.tabs(["📝 구매품 등록", "📋 구매품 목록"])
    
    with tab1:
        st.subheader("새 구매품 등록")
        
        with st.form("purchase_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                category = st.selectbox("카테고리", 
                    ["사무용품", "판매제품", "핫런너", "기타"])
                item_name = st.text_input("품목명")
                quantity = st.number_input("수량", min_value=1, value=1)
                unit = st.text_input("단위", value="개")
            
            with col2:
                unit_price = st.number_input("단가 (USD)", min_value=0.0, format="%.2f")
                supplier = st.text_input("공급업체")
                urgency = st.selectbox("긴급도", ["보통", "긴급", "매우긴급"])
                status = st.selectbox("상태", ["대기중", "승인됨", "주문완료", "취소됨"])
            
            description = st.text_area("설명")
            
            if st.form_submit_button("구매품 등록", use_container_width=True):
                if item_name and supplier:
                    user = get_current_user()
                    if user:
                        new_purchase = {
                            'category': category,
                            'item_name': item_name,
                            'quantity': quantity,
                            'unit': unit,
                            'unit_price': unit_price,
                            'total_amount': quantity * unit_price,
                            'supplier': supplier,
                            'urgency': urgency,
                            'status': status,
                            'description': description,
                            'requester': user['id'],
                            'created_at': datetime.now().isoformat()
                        }
                        
                        if save_data_to_supabase('purchases', new_purchase):
                            st.success("✅ 구매품이 등록되었습니다!")
                            st.rerun()
                        else:
                            st.error("❌ 구매품 등록에 실패했습니다.")
                    else:
                        st.error("❌ 사용자 정보를 확인할 수 없습니다.")
                else:
                    st.error("❌ 필수 항목을 입력해주세요.")
    
    with tab2:
        st.subheader("구매품 목록")
        
        # 필터링
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            filter_category = st.selectbox("카테고리 필터", 
                ["전체"] + ["사무용품", "판매제품", "핫런너", "기타"],
                key=generate_unique_key("purchase_category"))
        with col2:
            filter_status = st.selectbox("상태 필터", 
                ["전체"] + ["대기중", "승인됨", "주문완료", "취소됨"],
                key=generate_unique_key("purchase_status"))
        with col3:
            if st.button("📁 CSV 다운로드"):
                purchases = load_data_from_supabase('purchases')
                if purchases:
                    df = pd.DataFrame(purchases)
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="CSV 파일 다운로드",
                        data=csv,
                        file_name=f"purchases_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        # 데이터 로드 및 필터링
        purchases = load_data_from_supabase('purchases')
        
        if filter_category != "전체":
            purchases = [p for p in purchases if p.get('category') == filter_category]
        if filter_status != "전체":
            purchases = [p for p in purchases if p.get('status') == filter_status]
        
        # 구매품 목록 표시
        if purchases:
            for purchase in purchases:
                with st.expander(f"📦 {purchase.get('item_name', 'N/A')} - {purchase.get('status', 'N/A')}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**카테고리:** {purchase.get('category', 'N/A')}")
                        st.write(f"**수량:** {purchase.get('quantity', 0)} {purchase.get('unit', '')}")
                        st.write(f"**단가:** ${purchase.get('unit_price', 0):.2f}")
                        st.write(f"**총액:** ${purchase.get('total_amount', 0):.2f}")
                    
                    with col2:
                        st.write(f"**공급업체:** {purchase.get('supplier', 'N/A')}")
                        st.write(f"**긴급도:** {purchase.get('urgency', 'N/A')}")
                        st.write(f"**등록일:** {purchase.get('created_at', 'N/A')[:10]}")
                        if purchase.get('description'):
                            st.write(f"**설명:** {purchase.get('description')}")
                    
                    with col3:
                        if st.button("🔄 상태변경", key=f"status_{purchase.get('id')}"):
                            st.info("상태 변경 기능은 곧 구현됩니다.")
                        if st.button("❌ 삭제", key=f"delete_{purchase.get('id')}"):
                            if delete_data_from_supabase('purchases', purchase.get('id')):
                                st.success("✅ 삭제되었습니다!")
                                st.rerun()
        else:
            st.info("조건에 맞는 구매품이 없습니다.")

# 메인 애플리케이션
def main():
    """메인 애플리케이션"""
    
    # 로그인 체크
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        show_login_page()
        return
    
    # 메뉴 초기화 (세션 상태에서 관리)
    if 'current_menu' not in st.session_state:
        st.session_state.current_menu = "🏠 대시보드"
    
    # 사이드바 메뉴
    with st.sidebar:
        st.markdown("### 🏢 YMV 관리 프로그램 v4.0")
        
        user = get_current_user()
        if user:
            st.success(f"👋 {user['name']}님 환영합니다!")
            st.caption(f"부서: {user.get('department', 'N/A')} | 직책: {user.get('position', 'N/A')}")
            
            # CEO 승인 대기 알림 (관리자만)
            if user.get('is_admin'):
                expenses = load_data_from_supabase('expenses')
                ceo_pending = len([e for e in expenses if e.get('status') == 'CEO승인대기'])
                if ceo_pending > 0:
                    st.warning(f"👔 CEO 승인 대기: {ceo_pending}건")
        
        st.markdown("---")
        
        # 메뉴 버튼들
        menu_items = [
            "🏠 대시보드",
            "📦 구매품 관리", 
            "💰 지출 요청서",
            "📋 견적서 관리",
            "👥 고객 관리",
            "📦 제품 관리",
            "👨‍💼 직원 관리",
            "⚙️ 시스템 관리"
        ]
        
        st.markdown("### 📋 메뉴")
        for menu_item in menu_items:
            if st.button(menu_item, use_container_width=True, 
                        key=f"menu_{menu_item}",
                        type="primary" if st.session_state.current_menu == menu_item else "secondary"):
                st.session_state.current_menu = menu_item
                st.rerun()
        
        st.markdown("---")
        
        # 빠른 통계
        st.markdown("### 📊 빠른 통계")
        purchases = load_data_from_supabase('purchases')
        expenses = load_data_from_supabase('expenses')
        quotations = load_data_from_supabase('quotations')
        customers = load_data_from_supabase('customers')
        
        st.metric("구매품", len(purchases))
        st.metric("지출요청", len(expenses))
        st.metric("견적서", len(quotations))
        st.metric("고객", len(customers))
        
        st.markdown("---")
        
        if st.button("🚪 로그아웃", use_container_width=True):
            logout_user()
            st.rerun()
    
    # 선택된 메뉴에 따라 페이지 표시
    current_menu = st.session_state.current_menu
    
    if current_menu == "🏠 대시보드":
        show_dashboard()
    elif current_menu == "📦 구매품 관리":
        show_purchase_management()
    elif current_menu == "💰 지출 요청서":
        show_expense_management()
    elif current_menu == "📋 견적서 관리":
        st.info("견적서 관리 기능은 Step 6에서 구현됩니다.")
    elif current_menu == "👥 고객 관리":
        st.info("고객 관리 기능은 Step 7에서 구현됩니다.")
    elif current_menu == "📦 제품 관리":
        st.info("제품 관리 기능은 Step 8에서 구현됩니다.")
    elif current_menu == "👨‍💼 직원 관리":
        st.info("직원 관리 기능은 향후 구현됩니다.")
    elif current_menu == "⚙️ 시스템 관리":
        # 코드 관리 컴포넌트 사용
        code_mgmt = CodeManagementComponent(supabase)
        code_mgmt.render_code_management_page()

if __name__ == "__main__":
    main()