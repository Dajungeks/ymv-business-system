# YMV ERP 시스템 완전 개발 문서 - v15.0
## 다음 채팅에서 에러 없는 개발을 위한 종합 가이드

### 데이터 현황 및 샘플 데이터

#### customers 테이블 실제 데이터 (10개 업체)
```sql
-- 베트남 실제 제조업체들
1. HTMP Vietnam Co., Ltd.           -- 한국계, Automobile, Mold maker
2. TOHO Vietnam Co., Ltd.           -- 일본계, Automobile, Injection
3. Panasonic Vietnam Co., Ltd.      -- 일본계, Home Appliances, Injection & Mold Maker
4. Samsung Electronics Vietnam      -- 한국계, Mobile phone, Injection
5. LG Display Vietnam              -- 한국계, Mobile phone, Injection
6. Hyundai Motor Vietnam           -- 한국계, Automobile, Injection & Mold Maker
7. Canon Vietnam Co., Ltd.         -- 일본계, Office, Injection
8. Sharp Vietnam Co., Ltd.         -- 일본계, Home Appliances, Injection
9. Sumitomo Vietnam Co., Ltd.      -- 일본계, Automobile, Mold maker
10. Foxconn Vietnam               -- 대만계, Mobile phone, Injection & Mold Maker
```

#### product_codes 테이블 샘플 데이터
```sql
-- Hot Runner System 카테고리
HR | HR-01-02-ST-KR-00 | Hot Runner Standard 16MAE        | TRUE
HR | HR-01-02-MCC-KR-00| Hot Runner Standard 16MCC       | TRUE  
HR | HR-ST-OP-20-MAA-00| Hot Runner Standard 20MAA       | TRUE

-- Mold Parts 카테고리  
MP | MP-01-ST-16-KR-00 | Mold Parts Standard 16           | TRUE
MP | MP-02-AL-20-US-01 | Mold Parts Aluminum 20          | TRUE

-- A, B 카테고리들 (확장 가능)
A  | A-01-ST-KR-00     | Type A Standard                  | TRUE
B  | B-02-AL-US-01     | Type B Aluminum                  | TRUE
```

#### quotations 테이블 현재 상태
```sql
-- 고객 연동은 완성됨
customer_id: 1 (HTMP Vietnam)
customer_name: "HTMP Vietnam Co., Ltd."
sales_rep_id: 1 (Master)

-- 코드 연동이 누락됨 (현재 텍스트 입력)
item_code: "YMV-P-001" (수동 입력)
item_name: "Injection Mold" (수동 입력)

-- 연동 후 예상 데이터
item_code: "HR-01-02-ST-KR-00" (product_codes에서 선택)
item_name_en: "Hot Runner Standard 16MAE" (자동 입력)
```

### 베트남 비즈니스 규칙
```sql
-- 통화 우선순위
고객 대면: VND (베트남 동) 기본
공급업체: USD 기본  
내부 관리: KRW 가능

-- VAT 및 세율
표준 VAT: 10%
환율: 24,000 VND/USD (고정)

-- 문서 번호 체계
견적서: YMV-Q250928-001-Rv00
영업: YMV-S250928-001
발주: YMV-P250928-001
```

### 시스템 설정 테이블들
```sql
-- document_sequences (문서 번호 관리)
sequence_id     | table_name  | last_number | prefix
quotation_seq   | quotations  | 15         | YMV-Q
sales_seq       | sales       | 8          | YMV-S
purchase_seq    | purchases   | 23         | YMV-P

-- system_settings (시스템 설정)
setting_key        | setting_value
default_currency   | VND
default_vat_rate   | 10.00
exchange_rate_usd  | 24000.00
company_name       | YMV Vietnam Co., Ltd.

-- exchange_rates (환율 관리)
from_currency | to_currency | rate    | date
USD          | VND         | 24000   | 2024-09-28
KRW          | VND         | 18.5    | 2024-09-28
```

### View 테이블들의 역할
```sql
-- quotations_detail (견적서 상세 뷰)
-- quotations + customers + employees + product_codes 조인
-- 실제 연동 후 사용될 뷰

-- products_with_codes (제품-코드 조인 뷰)  
-- products + product_codes 연결
-- 향후 제품 마스터 확장 시 사용

-- sales_process_analysis (영업 분석 뷰)
-- 수익성 분석, KPI 계산용
```

### 중요한 인덱스 정보
```sql
-- 성능 최적화를 위한 인덱스들
CREATE INDEX idx_quotations_customer_id ON quotations(customer_id);
CREATE INDEX idx_quotations_quote_date ON quotations(quote_date);
CREATE INDEX idx_product_codes_category ON product_codes(category);
CREATE INDEX idx_product_codes_active ON product_codes(is_active);
CREATE UNIQUE INDEX idx_product_codes_full_code ON product_codes(full_code);
```

### 권한 및 보안 설정
```sql
-- RLS (Row Level Security) 정책들
-- 사용자별 데이터 접근 제한
-- 부서별 견적서 접근 제한
-- 관리자 전체 접근 권한

-- 사용자 역할
employees.role:
- 'manager': 전체 접근 가능
- 'employee': 본인 생성 데이터만 접근
- 'viewer': 읽기 전용
```

---

## 📋 시스템 개요

### 기본 정보
- **프로젝트명**: YMV 관리 프로그램 v4.0
- **위치**: D:\ymv-business-system
- **현재 완성도**: 99% (견적서-코드 연동만 남음)
- **배포 URL**: https://ymv-business-system.streamlit.app
- **테스트 계정**: Master / 1023
- **목표**: 견적서-코드 연동 완성으로 100% 달성

### 기술 스택
- **프레임워크**: Streamlit
- **데이터베이스**: Supabase (PostgreSQL)
- **언어**: Python
- **배포**: Streamlit Cloud

---

## 🏗️ 아키텍처 구조

### 디렉토리 구조
```
D:\ymv-business-system/
├── app/
│   ├── main.py (363줄, 전체 라우팅)
│   ├── components/ (8개 완성 모듈)
│   │   ├── __init__.py
│   │   ├── dashboard.py (완전 작동)
│   │   ├── expense_management.py (완전 작동)
│   │   ├── employee_management.py (베트남 급여 시스템 완성)
│   │   ├── quotation_management.py (고객 연동 완성, 코드 연동 누락)
│   │   ├── code_management.py (CSV 업로드, 중복 확인 완성)
│   │   ├── multilingual_input.py (정상 작동)
│   │   └── sales_process_management.py (재고 관리 세부 기능 완성)
│   └── utils/ (5개 유틸리티)
│       ├── __init__.py
│       ├── database.py (ConnectionWrapper 완성)
│       ├── auth.py (AuthManager 완성)
│       ├── helpers.py (통계/CSV/프린트)
│       └── html_templates.py (HTML 템플릿 분리)
├── database/ (SQL 실행 완료)
├── requirements.txt
├── .streamlit/config.toml
└── .env (Supabase 연결 정보)
```

---

## 📊 데이터베이스 완전 구조 분석

### 전체 테이블 목록 (40개 테이블)
```sql
-- BASE TABLES (핵심 비즈니스 테이블들)
attendance                  -- 출퇴근 관리
audit_logs                  -- 감사 로그
cash_flows                  -- 현금 흐름
company_info                -- 회사 정보
customers                   -- 고객 관리 ✅
delivery_shipment           -- 출고 관리
departments                 -- 부서 관리
document_sequences          -- 문서 번호 시퀀스
employee_history            -- 직원 이력
employee_leaves             -- 휴가 관리
employees                   -- 직원 관리 ✅
exchange_rates              -- 환율 정보
expenses                    -- 지출 요청서 ✅
inventory_receiving         -- 입고 관리
monthly_budgets             -- 월별 예산
orders                      -- 주문 관리
payroll                     -- 급여 관리
positions                   -- 직급 관리
product_categories          -- 제품 카테고리
product_codes               -- 제품 코드 ✅
products                    -- 제품 마스터
purchase_categories         -- 구매 카테고리
purchase_orders_to_supplier -- 공급업체 발주 ✅
purchases                   -- 구매품 관리 ✅
quality_inspection          -- 품질 검수
quotation_items             -- 견적서 아이템
quotations                  -- 견적서 ✅
sales_process               -- 영업 프로세스 ✅
sales_process_history       -- 영업 프로세스 이력
system_settings             -- 시스템 설정
translations                -- 다국어 번역
user_permissions            -- 사용자 권한
users                       -- 시스템 사용자

-- VIEWS (보기용 테이블들)
employee_details            -- 직원 상세 뷰
expenses_detail             -- 지출 상세 뷰
products_multilingual       -- 다국어 제품 뷰
products_with_codes         -- 제품-코드 조인 뷰
purchases_detail            -- 구매 상세 뷰
quotations_detail           -- 견적서 상세 뷰
sales_process_analysis      -- 영업 프로세스 분석 뷰
```

### 핵심 테이블 상세 스키마

#### 1. quotations (견적서) - 36개 컬럼
```sql
CREATE TABLE quotations (
    -- 기본 식별자
    id INTEGER PRIMARY KEY,
    quote_number VARCHAR(30),           -- YMV-Q250928-001-Rv00
    revision_number VARCHAR(10) DEFAULT 'Rv01',
    
    -- 고객 정보 (외래키 연동 완성)
    customer_id INTEGER,                -- → customers.id ✅
    customer_name VARCHAR(100) NOT NULL,
    company VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    customer_address TEXT,
    
    -- 일자 정보
    quote_date DATE NOT NULL,
    valid_until DATE NOT NULL,
    delivery_date DATE,
    
    -- 제품 정보 (코드 연동 대상)
    item_code VARCHAR(50),              -- 🎯 product_codes.full_code 연결 대상
    item_name VARCHAR(200) NOT NULL,
    item_name_en VARCHAR(200),
    item_name_vn VARCHAR(200),
    
    -- 가격 정보
    currency VARCHAR(3) DEFAULT 'USD',
    quantity INTEGER NOT NULL,
    unit_price NUMERIC NOT NULL,
    std_price NUMERIC,
    discount_rate NUMERIC DEFAULT 0.00,
    total_amount NUMERIC,
    vat_rate NUMERIC DEFAULT 10.00,
    
    -- 프로젝트 정보
    project_name VARCHAR(200),
    part_name VARCHAR(200),
    mold_no VARCHAR(100),
    part_weight NUMERIC,
    hrs_info VARCHAR(200),
    
    -- 재료 정보
    resin_type VARCHAR(100),
    resin_additive VARCHAR(200),
    sol_material VARCHAR(200),
    
    -- 거래 조건
    payment_terms VARCHAR(200),
    
    -- 메모 및 상태
    notes TEXT,
    remark TEXT,
    status VARCHAR(20) DEFAULT '작성중',
    
    -- 담당자 (외래키 연동 완성)
    sales_rep_id INTEGER,              -- → employees.id ✅
    created_by INTEGER,
    
    -- 시간 정보
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 2. product_codes (제품 코드) - 12개 컬럼
```sql
CREATE TABLE product_codes (
    id INTEGER PRIMARY KEY,
    
    -- 카테고리 정보
    category VARCHAR NOT NULL,          -- HR, MP, A, B 등
    description TEXT,                   -- 카테고리 설명
    
    -- 7단계 코드 구조
    code01 VARCHAR,                     -- 첫 번째 코드
    code02 VARCHAR,                     -- 두 번째 코드
    code03 VARCHAR,                     -- 세 번째 코드
    code04 VARCHAR,                     -- 네 번째 코드
    code05 VARCHAR,                     -- 다섯 번째 코드
    code06 VARCHAR,                     -- 여섯 번째 코드
    code07 VARCHAR,                     -- 일곱 번째 코드
    
    -- 생성된 코드 (HR-01-02-ST-KR-00 형태)
    full_code VARCHAR,                  -- 🎯 quotations.item_code 연결 소스
    
    -- 상태 관리
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 3. customers (고객) - 외래키 연동 완성
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    company_name VARCHAR NOT NULL,
    business_type VARCHAR,              -- Mold maker, Injection 등
    industry VARCHAR,                   -- Automobile, Home Appliances 등
    contact_person VARCHAR,
    phone VARCHAR,
    email VARCHAR,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 4. employees (직원) - 외래키 연동 완성
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE,
    password VARCHAR,
    name VARCHAR NOT NULL,
    department VARCHAR,
    position VARCHAR,
    role VARCHAR DEFAULT 'employee',    -- manager, employee
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 외래키 관계도
```
                    customers (10개 업체)
                         ↑
                   customer_id (FK)
                         |
    employees ← sales_rep_id ← quotations → item_code → product_codes
       ↑                         |                        (7단계 코드)
  created_by (FK)                |
                                 ↓
                         sales_process
                              |
                    ┌─────────┼─────────┐
                    ↓         ↓         ↓
         purchase_orders  inventory  delivery_shipment
                         receiving
```

### 현재 연동 상태
```
✅ 완성된 외래키 연동:
- quotations.customer_id → customers.id
- quotations.sales_rep_id → employees.id
- sales_process와 하위 테이블들 완전 연동

❌ 누락된 연동:
- quotations.item_code ↔ product_codes.full_code (텍스트 매칭만)
```

### 베트남 현지화 데이터
```sql
-- customers 테이블 실제 데이터 (10개 업체)
HTMP Vietnam Co., Ltd.          -- 한국계 자동차 부품
TOHO Vietnam Co., Ltd.          -- 일본계 사출업체
Panasonic Vietnam Co., Ltd.     -- 일본계 가전업체
Samsung Electronics Vietnam     -- 한국계 전자업체
LG Display Vietnam              -- 한국계 디스플레이
[기타 5개 업체...]

-- 업종 분류
business_type: 'Mold maker', 'Injection', 'Injection & Mold Maker'
industry: 'Automobile', 'Home Appliances', 'Mobile phone', 'Office'

-- 통화 및 VAT
currency: VND (기본), USD, KRW
vat_rate: 10% (베트남 표준)
```

### 제품 코드 시스템
```sql
-- 카테고리별 코드 예시
HR (Hot Runner System):
├── HR-01-02-ST-KR-00 (Hot Runner Standard 16MAE)
├── HR-01-02-MCC-KR-00 (Hot Runner Standard 16MCC)
└── HR-ST-OP-20-MAA-xx-00 (Hot Runner Standard 20MAA)

MP (Mold Parts):
├── MP-01-ST-16-KR-00
└── MP-02-AL-20-US-01

A, B (기타 카테고리들)
```

### 중요한 제약 조건
```sql
-- 제거된 제약 조건 (Step 14에서 해결)
-- product_codes_category_key (카테고리 중복 방지) → 삭제됨
-- 이제 하나의 카테고리에 여러 제품 코드 저장 가능

-- 현재 활성 제약 조건
quotations.customer_id REFERENCES customers(id)
quotations.sales_rep_id REFERENCES employees(id)
product_codes.category NOT NULL
quotations.quote_date NOT NULL
```

---

---

## 💻 코드 구조 분석

### main.py 구조 (363줄)
```python
# 1. 임포트 구조 (표준화됨)
표준 라이브러리 → 서드파티 → 내부 컴포넌트 → 유틸리티

# 2. 전역 초기화 (@st.cache_resource)
def init_supabase()        # Supabase 클라이언트
def init_managers()        # DB 및 Auth 매니저

# 3. 로그인 시스템
def show_login_page()      # 기본 로그인 폼

# 4. 페이지 함수들 (8개 메뉴)
def show_dashboard()
def show_expense_management_page()
def show_employee_management_page()
def show_sales_process_management_page()
def show_purchase_management()         # main.py에 직접 구현
def show_quotation_management_page()   # 🎯 코드 연동 필요
def show_code_management()
def show_multilingual_input()

# 5. 메인 라우팅
def main()                 # 순수 라우팅 로직
```

### database.py 구조 (완벽한 설계)
```python
class ConnectionWrapper:
    # 안전한 DB 연결 관리
    def execute_query(operation, table, data, filters, columns)
    def _execute_select/insert/update/delete()
    def _handle_error()
    def get_connection_status()

class DatabaseOperations:
    # 표준 인터페이스
    def load_data(table, columns, filters)
    def save_data(table, data)
    def update_data(table, data, id_field)
    def delete_data(table, item_id, id_field)
    def bulk_insert(table, data_list)

def create_database_operations(supabase_client)
```

### auth.py 구조 (중앙 집중식)
```python
class AuthManager:
    def login_user(username, password)
    def logout_user()
    def get_current_user()
    def is_logged_in()
    def check_permission(required_role, required_permissions)
    def require_manager_role()
    def update_user_profile(user_data)
    def change_password(current_password, new_password)
```

### quotation_management.py 구조 (고객 연동 완성)
```python
# 완성된 기능
def show_quotation_management(load_func, save_func, update_func, delete_func)
def load_customers(load_func)          # 고객 데이터 로드
def load_employees(load_func)          # 직원 데이터 로드
def generate_quote_number(...)         # YMV-Q250928-001-Rv00 형태

# 코드 연동 누락 함수 (구현 필요)
def load_product_codes(load_func)      # 🎯 구현 필요

def render_quotation_form(...):
    # 현재: 텍스트 입력
    item_code = st.text_input("제품 코드*")
    
    # 필요: selectbox 변경
    # selected_code = st.selectbox("제품 코드 선택*", code_options)
```

### code_management.py 구조 (완전 완성)
```python
class CodeManagementComponent:
    # 7단계 코드 시스템 완성
    def render_code_management_page()      # 3개 탭
    def _render_code_registration()        # 개별 등록
    def _render_code_list()                # 목록 관리
    def _upload_codes_csv()                # CSV 업로드
    def _check_duplicate_codes()           # 3단계 중복 확인
    def get_active_categories()            # 활성 카테고리 조회
```

---

## 🎯 견적서-코드 연동 구현 계획

### 현재 상황
- ✅ quotations.item_code (VARCHAR 50) 필드 존재
- ✅ product_codes 테이블 완전 구축
- ❌ 외래키 관계 없음 (텍스트 연결만 가능)
- ❌ 견적서 작성 시 코드 선택 기능 없음

### 구현 방법 (DB 스키마 변경 없음)
```python
# 1. load_product_codes() 함수 추가
def load_product_codes(load_func):
    """활성 제품 코드 로드"""
    codes = load_func('product_codes', '*', {'is_active': True})
    return codes

# 2. 견적서 작성 폼 수정
# quotation_management.py의 render_quotation_form() 내부
product_codes = load_product_codes(load_func)

# 제품 코드 selectbox 구현
if product_codes:
    code_options = ["제품 코드를 선택하세요..."]
    code_dict = {}
    
    for code in product_codes:
        display = f"{code['full_code']} - {code['description']}"
        code_options.append(display)
        code_dict[display] = code
    
    selected_code_display = st.selectbox("제품 코드 선택*", code_options)
    
    if selected_code_display != "제품 코드를 선택하세요...":
        selected_code = code_dict[selected_code_display]
        
        # 자동 입력
        item_code = selected_code['full_code']          # quotations.item_code에 저장
        item_name_en = selected_code['description']     # 자동 입력
        category_info = selected_code['category']       # 추가 정보

# 3. 견적서 저장 시 연결
quotation_data = {
    ...
    'item_code': selected_code['full_code'],    # 기존 필드 활용
    'item_name_en': selected_code['description'],
    ...
}
```

### 수정할 파일
```
app/components/quotation_management.py
├── load_product_codes() 함수 추가 (10줄)
├── render_quotation_form() 수정 (50줄 수정/추가)
└── 제품 정보 영역 selectbox 변경 (30줄)

총 수정량: 약 90줄
```

---

## 🧪 테스트 시나리오

### 1. 현재 작동 테스트
```
1. Master / 1023 로그인
2. 코드관리 → 제품 코드 등록 확인
3. 견적서관리 → 고객 연동 작동 확인
4. 현재 item_code 텍스트 입력 확인
```

### 2. 연동 후 테스트
```
1. 견적서관리 → 새 견적서 작성
2. 고객 선택 (HTMP Vietnam 등)
3. 제품 코드 selectbox에서 HR-01-02-ST-KR-00 선택
4. 제품명 자동 입력 확인
5. 견적서 저장 → item_code에 full_code 저장 확인
6. 견적서 목록에서 제품 코드 표시 확인
```

### 3. 통합 테스트
```
1. 코드관리에서 새 코드 등록
2. 견적서에서 새 코드 즉시 선택 가능 확인
3. 견적서 → 영업 프로세스 전환 테스트
4. 전체 워크플로우 검증
```

---

## ⚠️ 주의사항 및 에러 방지

### 개발 규칙 준수
1. **규칙 21**: 코딩 전 설명하고 승인받기
2. **규칙 2**: 항상 전체 코드(파일 단위) 제공
3. **규칙 18**: ConnectionWrapper 클래스 활용
4. **규칙 20**: 가능하면 DB 수정보다 코드 수정 우선

### 예상 에러 포인트
```python
# 1. 제품 코드 데이터 없을 때
if not product_codes:
    st.warning("등록된 제품 코드가 없습니다.")
    return

# 2. 선택 없이 진행할 때
if selected_code_display == "제품 코드를 선택하세요...":
    st.error("제품 코드를 선택해주세요.")
    return

# 3. DB 저장 실패 시
try:
    save_func('quotations', quotation_data)
    st.success("견적서 저장 완료!")
except Exception as e:
    st.error(f"저장 실패: {str(e)}")
```

### 기존 코드 보존
- 고객 연동 로직 완전 보존
- 견적서 번호 생성 로직 유지
- 기존 필드들 모두 유지
- 하위 호환성 보장

---

## 🗄️ 환경 설정

### Supabase 연결
```python
SUPABASE_URL = "https://eqplgrbegwzeynnbcuep.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIs..."
```

### 핵심 라이브러리
```python
import streamlit as st
import pandas as pd
from datetime import datetime, date
import supabase
from supabase import create_client, Client
```

---

## 🚀 다음 개발 단계

### Step 15: 견적서-코드 연동 (99% → 100%)
1. **quotation_management.py 수정**
   - load_product_codes() 함수 추가
   - render_quotation_form() 내 제품 선택 로직 변경
   - 자동 입력 기능 구현

2. **테스트 및 검증**
   - 코드 선택 → 자동 입력 → 저장 플로우
   - 기존 기능 영향 없음 확인

3. **최종 문서화**
   - 100% 완성 시스템 백업
   - 운영 가이드 작성

### Phase 2: 시스템 최적화 (선택사항)
- HTML 프린트 기능 완성
- 다국어 번역 완료
- 성능 최적화

---

## 📋 개발 체크리스트

### 사전 확인
- [ ] 현재 시스템 정상 작동 확인
- [ ] product_codes 테이블 데이터 존재 확인
- [ ] 기존 견적서 고객 연동 작동 확인

### 구현 단계
- [ ] load_product_codes() 함수 구현
- [ ] 제품 코드 selectbox UI 구현
- [ ] 선택 시 자동 입력 로직 구현
- [ ] 견적서 저장 시 코드 연결 구현

### 테스트 단계
- [ ] 새 견적서 작성 테스트
- [ ] 제품 코드 선택 테스트
- [ ] 자동 입력 기능 테스트
- [ ] 견적서 저장 및 조회 테스트
- [ ] 기존 기능 영향 없음 확인

### 완성 확인
- [ ] 99% → 100% 완성도 달성
- [ ] 전체 워크플로우 정상 작동
- [ ] 에러 없는 안정적 동작

---

## 💡 즉시 시작 가능한 개발

**준비 완료 상태입니다!**

다음 채팅에서 이 문서를 업로드하고 다음과 같이 요청하면 즉시 개발이 가능합니다:

> "이 개발 문서를 기반으로 견적서-코드 연동을 구현해줘. Step 15를 완성해서 99%를 100%로 만들어줘."

**필요한 작업:**
1. quotation_management.py 파일 요청
2. load_product_codes() 함수 추가
3. render_quotation_form() 수정
4. 테스트 및 완성도 확인

**예상 소요 시간:** 30-60분
**수정 파일:** 1개 (quotation_management.py)
**수정량:** 약 90줄