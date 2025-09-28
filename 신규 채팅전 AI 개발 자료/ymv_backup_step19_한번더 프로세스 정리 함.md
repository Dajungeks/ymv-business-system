# YMV ERP 통합 현금 흐름 관리 시스템 요약

## 핵심 추가 내용

### 1. 통합 현금 흐름 계산

#### 수입원 (영업 프로세스)
- 견적서 승인된 영업 프로세스
- 예상 배송일 기준 월별 수입 예측

#### 지출원 (지출요청서)
- 승인된/대기중인 지출요청서
- 지출 예정일 기준 월별 지출 예측

### 2. 실시간 재무 상태 모니터링

```python
get_current_financial_status()
- 파이프라인 총 가치 (예상 수입)
- 승인된 지출 총액
- 순 현금 흐름 전망 (수입 - 지출)
- 재무 건전성 지표
```

### 3. 통합 대시보드 기능

- **전체 재무 상태**: 4개 핵심 지표 카드
- **월별 현금 흐름 차트**: 수입/지출/순흐름 시각화
- **월별 상세 내역**: 수입/지출 항목별 세부 정보
- **현금 흐름 경고**: 적자 예상 월, 대규모 지출 알림

### 4. 실제 업무 시나리오

```
견적서 승인 → 영업 프로세스 생성 → 예상 수입 등록
    ↓
지출요청서 승인 → 예상 지출 등록
    ↓
월별 통합 현금 흐름 = 예상 수입 - 예상 지출
    ↓
순 현금 흐름 기반 경영 의사결정
```

### 5. 핵심 개선점

- **실시간 순 현금흐름**: 흑자/적자 즉시 파악
- **월별 상세 분석**: 수입/지출 항목별 추적
- **경고 시스템**: 적자 예상 월 사전 알림
- **부서별 지출 추적**: 지출요청서 부서별 집계

## 시스템 특징

### 통합성
- 영업 수입과 총무 지출을 하나의 현금 흐름으로 통합 관리
- 실시간 데이터 연동으로 즉시 반영

### 예측성
- 견적서 승인 즉시 미래 수입 예측 시작
- 지출요청서 승인으로 미래 지출 예측
- 최대 6개월 전 현금 흐름 예측 가능

### 의사결정 지원
- 월별 순 현금흐름으로 흑자/적자 사전 파악
- 적자 예상 시 조기 경고 시스템
- 부서별 지출 패턴 분석

### 시각화
- 직관적인 차트와 그래프
- 색상 코딩으로 위험 상황 즉시 인식
- 드릴다운 가능한 상세 정보

## 활용 효과

### 경영진
- 회사 전체 현금 흐름 한눈에 파악
- 투자 및 지출 의사결정 근거 제공
- 리스크 관리 및 예방

### 영업팀
- 견적서 승인이 현금 흐름에 미치는 영향 즉시 확인
- 영업 성과의 재무적 임팩트 측정

### 총무팀
- 지출 계획이 전체 현금 흐름에 미치는 영향 분석
- 적절한 지출 타이밍 결정

### 재무팀
- 통합 재무 현황 실시간 모니터링
- 예산 대비 실적 추적
- 현금 관리 최적화
# YMV ERP 시스템 완전 개발 가이드 - Supabase 기반 v3.0 Final

## 🎯 프로젝트 기본 정보

### 시스템 개요
- **프로젝트명**: YMV 관리 프로그램 (ERP 시스템)
- **개발 언어**: Python + Streamlit
- **데이터베이스**: Supabase (PostgreSQL)
- **아키텍처**: 컴포넌트 기반 모듈화
- **현재 진행률**: 95% 완성

### Supabase 연결 정보
```
SUPABASE_URL = "https://eqplgrbegwzeynnbcuep.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
프로젝트 위치: D:\ymv-business-system
GitHub: https://github.com/dajungeks/ymv-business-system.git
```

---

## 📐 핵심 개발 원칙 (절대 준수)

### 1. DB 우선 원칙 ⭐⭐⭐
```
❌ 추측성 코딩 절대 금지
✅ 실제 DB 스키마 확인 후 코딩
✅ 컬럼명/타입 정확히 매핑 후 개발
✅ 아래 확정된 스키마 정보 기준으로만 개발
```

### 2. 개발 규칙 V10 준수
```
- 항상 전체 파일 단위 코드 제공
- 수정 전 설명 → 승인 → 코딩
- Step 단위 진행
- 1가지 최적 방법만 제시
- 추측 금지, DB/코드 요청 후 확인
```

### 3. Supabase 전용 아키텍처
```
- ConnectionWrapper 클래스 사용 필수
- 직접 DB 연결 호출 금지
- utils/database.py 통한 DB 작업
- 모든 예외 처리 및 로깅
```

---

## 🗄️ 확정된 DB 스키마 (Supabase 실제)

### 1. products 테이블 (제품 관리)
```sql
-- 핵심 컬럼들
id                  integer (PK, auto)
product_code        varchar(50) NOT NULL
product_name        varchar(200) NOT NULL
product_name_en     varchar(200)
product_name_vn     varchar(200) 
product_name_kr     varchar(200)
category            varchar(50) NOT NULL
unit                varchar(20) DEFAULT '개'

-- 가격 정보 (정확한 컬럼명)
unit_price          numeric DEFAULT 0          -- 기본 단가
unit_price_vnd      numeric DEFAULT 0          -- VND 단가
cost_price_usd      numeric DEFAULT 0          -- ✅ USD 원가
cost_price_cny      numeric DEFAULT 0          -- CNY 원가  
selling_price_usd   numeric DEFAULT 0          -- ✅ USD 판매가

-- 기타 정보
currency            varchar(3) DEFAULT 'USD'
supplier            varchar(200)
stock_quantity      integer DEFAULT 0
description         text
specifications      text
weight_kg           numeric
dimensions          varchar(100)
material            varchar(100)
lead_time_days      integer DEFAULT 30
minimum_order_qty   integer DEFAULT 1
is_active           boolean DEFAULT true
notes               text
created_at          timestamptz DEFAULT now()
updated_at          timestamptz DEFAULT now()
```

### 2. quotations 테이블 (견적서 관리)
```sql
-- 기본 정보
id                  integer (PK, auto)
quote_number        varchar(30)
revision_number     varchar(10) DEFAULT 'Rv01'
quote_date          date NOT NULL
valid_until         date NOT NULL
currency            varchar(3) DEFAULT 'USD'
status              varchar(20) DEFAULT '작성중'

-- 고객 정보
customer_id         integer (FK to customers)
customer_name       varchar(100) NOT NULL
company             varchar(200) NOT NULL
contact_person      varchar(100)
email               varchar(100)
phone               varchar(20)
customer_address    text

-- 제품/견적 정보
item_code           varchar(50)
item_name           varchar(200) NOT NULL
item_name_en        varchar(200)
item_name_vn        varchar(200)
quantity            integer NOT NULL
unit_price          numeric NOT NULL        -- 견적 단가
std_price           numeric                 -- 표준가
discount_rate       numeric DEFAULT 0.00    -- 할인율
total_amount        numeric                 -- 총액

-- 프로젝트 정보
project_name        varchar(200)
part_name           varchar(200)
mold_no             varchar(100)
part_weight         numeric
hrs_info            varchar(200)
resin_type          varchar(100)
resin_additive      varchar(200)
sol_material        varchar(200)

-- 거래 조건
payment_terms       varchar(200)
delivery_date       date
vat_rate            numeric DEFAULT 10.00
remark              text
notes               text

-- 시스템 정보
sales_rep_id        integer (FK to employees)
created_by          integer (FK to employees)
created_at          timestamptz DEFAULT now()
updated_at          timestamptz DEFAULT now()
```

**⚠️ 중요: quotations 테이블에는 원가 컬럼이 없음!**
견적서에서 원가 정보가 필요할 때는 products 테이블의 `cost_price_usd`를 조회해야 함.

### 3. customers 테이블 (고객 관리)
```sql
-- 기본 정보
id                   integer (PK, auto)
company_name         varchar(200) NOT NULL
contact_person       varchar(100) NOT NULL
position             varchar(100)
phone                varchar(20)
email                varchar(100)
mobile               varchar(50)
address              text

-- 사업자 정보
business_type        varchar(100)
business_number      varchar(50)
country              varchar(100)
tax_id               varchar(100)
payment_terms        varchar(100)

-- KAM 정보
assigned_employee_id integer (FK to employees)
kam_name             varchar(255)
kam_phone            varchar(50)
kam_position         varchar(100)
kam_notes            text

-- 상태 관리
status               varchar(50) DEFAULT 'Active'
notes                text
created_at           timestamptz DEFAULT now()
updated_at           timestamptz DEFAULT now()
```

### 4. employees 테이블 (직원 관리)
```sql
-- 기본 정보
id                integer (PK, auto)
name              varchar(100) NOT NULL
username          varchar(50) NOT NULL
password          varchar(255) NOT NULL
employee_id       varchar(20)

-- 조직 정보
department        varchar(50) NOT NULL
position          varchar(100)
manager_id        integer (FK to employees)
role              varchar(20) DEFAULT 'employee'

-- 연락처
email             varchar(100)
phone             varchar(20)
address           text
emergency_contact varchar(100)
emergency_phone   varchar(20)

-- 근무 정보
hire_date         date
salary            numeric
employment_status varchar(20) DEFAULT 'active'
work_type         varchar(20) DEFAULT 'full_time'
birth_date        date

-- 권한
is_admin          boolean DEFAULT false
is_active         boolean DEFAULT true

-- 메타
notes             text
created_at        timestamptz DEFAULT now()
updated_at        timestamptz DEFAULT now()
```

### 5. expenses 테이블 (지출 요청서)
```sql
-- 기본 정보
id               integer (PK, auto)
expense_type     varchar(50) NOT NULL
amount           numeric NOT NULL
currency         varchar(3) DEFAULT 'USD'
payment_method   varchar(50) NOT NULL
expense_date     date NOT NULL

-- 요청 정보
department       varchar(50)
requester        integer (FK to employees)
urgency          varchar(20) DEFAULT '보통'
description      text NOT NULL
business_purpose text
purpose          text
vendor           varchar(200)

-- 상태 관리
status           varchar(20) DEFAULT '대기중'
created_at       timestamptz DEFAULT now()
updated_at       timestamptz DEFAULT now()
```

### 6. purchases 테이블 (구매품 관리)
```sql
-- 기본 정보
id           integer (PK, auto)
category     varchar(50) NOT NULL
item_name    varchar(200) NOT NULL
quantity     integer NOT NULL
unit         varchar(20) DEFAULT '개'

-- 가격 정보
unit_price   numeric NOT NULL
total_price  numeric
currency     varchar(3) DEFAULT 'KRW'

-- 공급업체
supplier     varchar(200)

-- 요청 정보
request_date date NOT NULL
urgency      varchar(20) DEFAULT '보통'
status       varchar(20) DEFAULT '대기중'
requester    integer (FK to employees)
notes        text

-- 메타
created_at   timestamptz DEFAULT now()
updated_at   timestamptz DEFAULT now()
```

### 7. suppliers 테이블 (공급업체 관리)
```sql
-- 기본 정보
id             integer (PK, auto)
name           varchar(200) NOT NULL
company_name   varchar(200) NOT NULL
contact_person varchar(100)
email          varchar(100)
phone          varchar(50)
address        text

-- 사업 정보
business_type  varchar(100)
payment_terms  varchar(100)
delivery_terms varchar(100)
rating         integer DEFAULT 5

-- 상태 관리
is_active      boolean DEFAULT true
notes          text
created_at     timestamptz DEFAULT now()
updated_at     timestamptz DEFAULT now()
```

### 8. exchange_rates 테이블 (환율 관리)
```sql
-- 기본 정보
id             integer (PK, auto)
from_currency  varchar(3) NOT NULL
to_currency    varchar(3) NOT NULL
rate           numeric NOT NULL
effective_date date NOT NULL

-- 메타
notes          text
created_by     integer (FK to employees)
created_at     timestamptz DEFAULT now()
updated_at     timestamptz DEFAULT now()
```

### 9. company_info 테이블 (회사 정보)
```sql
-- 기본 정보
id              integer (PK, auto)
company_name    varchar(200) NOT NULL
address         text
phone           varchar(20)
email           varchar(100)

-- 사업자 정보
business_number varchar(50)
tax_number      varchar(50)
ceo_name        varchar(100)
business_type   varchar(100)

-- 메타
notes           text
created_at      timestamptz DEFAULT now()
updated_at      timestamptz DEFAULT now()
```

---

## 🏗️ 시스템 아키텍처

### main.py 구조 (확정)
```python
# Import 순서 (규칙 15)
# 1. 표준 라이브러리
import streamlit as st
import time

# 2. 서드파티
import supabase
from supabase import create_client, Client

# 3. 내부 모듈
from components.quotation_management import show_quotation_management
from components.customer_management import show_customer_management  
from components.product_management import show_product_management
from utils.database import create_database_operations
```

### 컴포넌트 구조
```
app/
├── main.py                          # 라우팅만
├── components/                      # 기능별 모듈
│   ├── quotation_management.py     # 견적서 관리
│   ├── customer_management.py      # 고객 관리
│   ├── product_management.py       # 제품 관리
│   ├── expense_management.py       # 지출 관리
│   ├── employee_management.py      # 직원 관리
│   └── supplier_management.py      # 공급업체 관리
└── utils/                          # 공통 유틸리티
    ├── database.py                 # DB 연결 관리
    ├── auth.py                     # 인증 관리
    └── helpers.py                  # 공통 함수들
```

---

## 🔧 핵심 개발 패턴

### 1. DB 연결 패턴 (ConnectionWrapper 필수)
```python
# utils/database.py
class ConnectionWrapper:
    def __init__(self, supabase_client):
        self.client = supabase_client
    
    def execute_query(self, operation, table, data=None, filters=None):
        """모든 DB 작업의 통일된 인터페이스"""
        try:
            if operation == "select":
                query = self.client.table(table).select("*")
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                return query.execute()
            
            elif operation == "insert":
                return self.client.table(table).insert(data).execute()
            
            elif operation == "update":
                if 'id' not in data:
                    raise ValueError("Update 시 ID 필수")
                update_data = {k: v for k, v in data.items() if k != 'id'}
                return self.client.table(table).update(update_data).eq('id', data['id']).execute()
            
            elif operation == "delete":
                return self.client.table(table).delete().eq('id', filters['id']).execute()
                
        except Exception as e:
            # 로깅 후 재전달
            print(f"DB Error: {str(e)}")
            raise e

# 사용 패턴
db_operations = create_database_operations(supabase_client)
```

### 2. 컴포넌트 함수 호출 패턴
```python
# 모든 컴포넌트는 동일한 시그니처
def show_component_management(load_func, save_func, update_func, delete_func):
    """표준 컴포넌트 구조"""
    
    # main.py에서 호출
    show_product_management(
        load_func=db_operations.load_data,
        save_func=db_operations.save_data,
        update_func=db_operations.update_data,
        delete_func=db_operations.delete_data
    )
```

### 3. 제품-견적서 원가 연동 패턴 (중요!)
```python
# 견적서에서 제품 원가 조회 시
def get_product_cost_price(product_id, load_func):
    """제품 원가 조회 - 정확한 컬럼명 사용"""
    products = load_func("products")
    product = next((p for p in products if p['id'] == product_id), None)
    
    if product:
        # ✅ 정확한 컬럼명 사용
        return product.get('cost_price_usd', 0)  # cost_price가 아님!
    return 0

# 견적서 마진 계산
def calculate_margin(selling_price, cost_price_usd):
    """마진 계산"""
    if cost_price_usd > 0:
        margin = ((selling_price - cost_price_usd) / selling_price) * 100
        return round(margin, 2)
    return 0
```

### 4. 데이터 업데이트 패턴
```python
# 제품 수정 시 (ID 포함 필수)
def update_product(product_data, update_func):
    """제품 수정 - ID 포함 방식"""
    update_data = {
        'id': product_data['id'],  # ID 포함 필수
        'product_name': product_data['product_name'],
        'cost_price_usd': product_data['cost_price_usd'],
        # ... 기타 필드들
    }
    
    return update_func('products', update_data)
```

### 10. sales_process 테이블 (영업 프로세스 메인)
```sql
-- 기본 정보
id                     integer (PK, auto)
process_number         varchar(20) NOT NULL        -- 영업번호
quotation_id           integer (FK to quotations)  -- 견적서 연결
order_id               integer (FK to orders)      -- 주문서 연결

-- 고객 정보 (중복 저장)
customer_name          varchar(255) NOT NULL
customer_company       varchar(255) NOT NULL
customer_email         varchar(255)
customer_phone         varchar(20)

-- 영업 담당자
sales_rep_id           integer (FK to employees) NOT NULL

-- 프로세스 상태
process_status         varchar(20) DEFAULT 'quotation'
-- 상태값: quotation → negotiation → contract → order → delivery → completed

-- 제품/견적 정보
item_description       text NOT NULL
quantity               integer NOT NULL
unit_price             numeric NOT NULL
total_amount           numeric NOT NULL
currency               varchar(3) DEFAULT 'VND'
profit_margin          numeric                     -- 마진율

-- 일정 관리
expected_delivery_date date
actual_delivery_date   date

-- 거래 조건
customer_po_number     varchar(50)                 -- 고객 PO번호
payment_terms          varchar(100)
delivery_terms         varchar(100)

-- 메타
notes                  text
created_at             timestamp DEFAULT now()
updated_at             timestamp DEFAULT now()
```

### 11. sales_process_history 테이블 (영업 이력)
```sql
-- 기본 정보
id               integer (PK, auto)
sales_process_id integer (FK to sales_process) NOT NULL

-- 상태 변경 추적
status_from      varchar(20)                    -- 이전 상태
status_to        varchar(20) NOT NULL           -- 변경된 상태
changed_by       integer (FK to employees) NOT NULL
change_date      timestamp DEFAULT now()

-- 변경 사유
change_reason    text
notes            text
```

### 12. orders 테이블 (주문서)
```sql
-- 기본 정보
order_id         integer (PK, auto)
order_number     varchar(50) NOT NULL
quotation_id     integer (FK to quotations)
customer_id      integer (FK to customers)

-- 일정
order_date       date DEFAULT CURRENT_DATE
delivery_date    date

-- 상태 관리
status           varchar(20) DEFAULT 'pending'
-- 상태값: pending → processing → shipped → delivered → completed

-- 금액 정보
subtotal         numeric DEFAULT 0
tax_amount       numeric DEFAULT 0
total_amount     numeric DEFAULT 0
currency         varchar(3) DEFAULT 'USD'

-- 배송 정보
shipping_address text

-- 메타
notes            text
created_by       integer (FK to employees)
created_at       timestamptz DEFAULT CURRENT_TIMESTAMP
updated_at       timestamptz DEFAULT CURRENT_TIMESTAMP
```

---

## 🔄 영업 프로세스 워크플로우 (현금 흐름 관리 목적)

### 전체 영업 프로세스 (3단계)
```
1. 견적서 관리 단계 (quotations 테이블)
   - 견적서 작성 → 발송 → 협상 → 승인/거절
   ↓ (승인 즉시 영업 프로세스 시작)
2. 영업 프로세스 시작 (현금 흐름 예측)
   - 주문(order) → 배송(delivery) → 완료(completed)
   ↓
3. 주문서 처리 (orders 테이블)
   - 주문 접수 → 처리 → 배송 → 완료
```

### 영업 프로세스 상태값 (3단계 + 현금 흐름 정보)
```
order      → 주문 예정 (월별 예상 수입 계산 시작)
delivery   → 배송 중 (지출 발생: 배송비, 제조비 등)
completed  → 완료 (실제 수입 확정)
cancelled  → 취소 (언제든 가능)
```

### 상세 프로세스 흐름

#### 1단계: 견적서 승인 → 영업 프로세스 즉시 시작
```sql
-- 견적서 승인 후 → 영업 프로세스 자동 생성 (현금 흐름 예측용)
INSERT INTO sales_process (
    process_number,        -- SP240001 형태
    quotation_id,          -- 승인된 견적서 ID
    customer_name,
    customer_company,
    sales_rep_id,
    process_status,        -- 'order' (주문 예정 상태로 시작)
    item_description,
    quantity,
    unit_price,
    total_amount,          -- 예상 수입액
    currency,
    expected_delivery_date, -- 예상 수입 시기
    profit_margin          -- 예상 마진
) VALUES (...)

-- 현금 흐름 예측 정보 추가
-- 이 정보로 월별 예상 수입/지출 계산
```

#### 2단계: 통합 현금 흐름 관리 (수입 + 지출)
```python
def calculate_comprehensive_cash_flow(load_func):
    """수입(영업 프로세스) + 지출(지출요청서) 통합 현금 흐름 계산"""
    
    # 영업 프로세스 - 예상 수입
    sales_processes = load_func("sales_process")
    # 지출요청서 - 예상 지출
    expenses = load_func("expenses")
    
    monthly_cash_flow = {}
    
    # 1. 예상 수입 계산 (영업 프로세스)
    for process in sales_processes:
        if process.get('process_status') in ['order', 'delivery']:
            delivery_date = process.get('expected_delivery_date')
            if delivery_date:
                month_key = delivery_date[:7]  # YYYY-MM
                
                if month_key not in monthly_cash_flow:
                    monthly_cash_flow[month_key] = {
                        'expected_income': 0,
                        'expected_expenses': 0,
                        'net_cash_flow': 0,
                        'income_items': [],
                        'expense_items': []
                    }
                
                # 예상 수입 누적
                amount = process.get('total_amount', 0)
                monthly_cash_flow[month_key]['expected_income'] += amount
                monthly_cash_flow[month_key]['income_items'].append({
                    'type': 'sales',
                    'description': process.get('item_description'),
                    'amount': amount,
                    'customer': process.get('customer_company'),
                    'process_number': process.get('process_number')
                })
    
    # 2. 예상 지출 계산 (지출요청서)
    for expense in expenses:
        if expense.get('status') in ['대기중', '승인됨']:  # 승인된 지출만
            expense_date = expense.get('expense_date')
            if expense_date:
                month_key = expense_date[:7]  # YYYY-MM
                
                if month_key not in monthly_cash_flow:
                    monthly_cash_flow[month_key] = {
                        'expected_income': 0,
                        'expected_expenses': 0,
                        'net_cash_flow': 0,
                        'income_items': [],
                        'expense_items': []
                    }
                
                # 예상 지출 누적
                amount = expense.get('amount', 0)
                monthly_cash_flow[month_key]['expected_expenses'] += amount
                monthly_cash_flow[month_key]['expense_items'].append({
                    'type': 'expense',
                    'description': expense.get('description'),
                    'amount': amount,
                    'expense_type': expense.get('expense_type'),
                    'department': expense.get('department'),
                    'urgency': expense.get('urgency')
                })
    
    # 3. 순 현금 흐름 계산
    for month_key in monthly_cash_flow:
        income = monthly_cash_flow[month_key]['expected_income']
        expenses = monthly_cash_flow[month_key]['expected_expenses']
        monthly_cash_flow[month_key]['net_cash_flow'] = income - expenses
    
    return monthly_cash_flow

def get_current_financial_status(load_func):
    """현재 재무 상태 요약"""
    
    # 파이프라인 총 가치 (예상 수입)
    pipeline_value = get_current_pipeline_value(load_func)
    
    # 승인된 지출 총액
    expenses = load_func("expenses")
    approved_expenses = sum(
        e.get('amount', 0) for e in expenses 
        if e.get('status') in ['승인됨', '대기중']
    )
    
    # 순 현금 흐름 전망
    net_outlook = pipeline_value - approved_expenses
    
    return {
        'pipeline_value': pipeline_value,
        'approved_expenses': approved_expenses,
        'net_outlook': net_outlook,
        'cash_flow_health': 'positive' if net_outlook > 0 else 'negative'
    }
```

### 통합 현금 흐름 대시보드 기능
```python
def render_comprehensive_cash_flow_dashboard(load_func):
    """수입/지출 통합 현금 흐름 대시보드"""
    
    # 전체 현금 흐름 계산
    cash_flow_data = calculate_comprehensive_cash_flow(load_func)
    financial_status = get_current_financial_status(load_func)
    
    st.subheader("💰 통합 현금 흐름 현황")
    
    # 1. 전체 재무 상태
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "파이프라인 총 가치", 
            f"{financial_status['pipeline_value']:,} VND",
            help="진행 중인 영업 프로세스 총 가치"
        )
    
    with col2:
        st.metric(
            "승인된 지출 총액", 
            f"{financial_status['approved_expenses']:,} VND",
            help="승인되었거나 대기 중인 지출 총액"
        )
    
    with col3:
        net_value = financial_status['net_outlook']
        delta_color = "normal" if net_value >= 0 else "inverse"
        st.metric(
            "순 현금 흐름 전망", 
            f"{net_value:,} VND",
            delta=f"{'흑자' if net_value >= 0 else '적자'} 예상",
            delta_color=delta_color
        )
    
    with col4:
        active_processes = len([p for p in load_func("sales_process") 
                              if p.get('process_status') in ['order', 'delivery']])
        st.metric("진행 중인 영업", f"{active_processes}건")
    
    # 2. 월별 현금 흐름 차트
    if cash_flow_data:
        st.subheader("📊 월별 현금 흐름 분석")
        
        # 데이터 준비
        months = sorted(cash_flow_data.keys())
        income_data = [cash_flow_data[m]['expected_income'] for m in months]
        expense_data = [cash_flow_data[m]['expected_expenses'] for m in months]
        net_data = [cash_flow_data[m]['net_cash_flow'] for m in months]
        
        # 차트 생성 (Streamlit의 line_chart 사용)
        import pandas as pd
        
        chart_data = pd.DataFrame({
            '월': months,
            '예상 수입': income_data,
            '예상 지출': expense_data,
            '순 현금흐름': net_data
        })
        
        st.line_chart(chart_data.set_index('월'))
    
    # 3. 월별 상세 내역
    st.subheader("📋 월별 상세 현금 흐름")
    
    for month in sorted(cash_flow_data.keys())[:6]:  # 최근 6개월
        with st.expander(f"📅 {month} 현금 흐름 상세"):
            month_data = cash_flow_data[month]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**💰 예상 수입**")
                for item in month_data['income_items']:
                    st.write(f"- {item['customer']}: {item['description']} ({item['amount']:,} VND)")
            
            with col2:
                st.write("**💸 예상 지출**")
                for item in month_data['expense_items']:
                    urgency_icon = "🔴" if item['urgency'] == '긴급' else "🟡" if item['urgency'] == '높음' else "🟢"
                    st.write(f"- {urgency_icon} {item['expense_type']}: {item['description']} ({item['amount']:,} VND)")
            
            # 월별 순 현금흐름
            net_flow = month_data['net_cash_flow']
            if net_flow >= 0:
                st.success(f"💰 순 현금흐름: +{net_flow:,} VND (흑자)")
            else:
                st.error(f"💸 순 현금흐름: {net_flow:,} VND (적자)")

def get_cash_flow_alerts(load_func):
    """현금 흐름 경고 알림"""
    
    cash_flow_data = calculate_comprehensive_cash_flow(load_func)
    alerts = []
    
    for month, data in cash_flow_data.items():
        net_flow = data['net_cash_flow']
        
        # 적자 경고
        if net_flow < 0:
            alerts.append({
                'type': 'warning',
                'month': month,
                'message': f"{month} 적자 예상: {net_flow:,} VND",
                'recommendation': "지출 계획 재검토 또는 수입 확대 필요"
            })
        
        # 대규모 지출 경고
        if data['expected_expenses'] > 1000000000:  # 10억 VND 이상
            alerts.append({
                'type': 'info',
                'month': month,
                'message': f"{month} 대규모 지출 예정: {data['expected_expenses']:,} VND",
                'recommendation': "현금 보유량 확인 필요"
            })
    
    return alerts
```

### 지출요청서 승인 시 현금 흐름 업데이트
```python
def on_expense_approval(expense_id, approver_id, update_func, load_func):
    """지출요청서 승인 시 현금 흐름 즉시 업데이트"""
    
    # 지출요청서 승인 처리
    expense_update = {
        'id': expense_id,
        'status': '승인됨',
        'updated_at': datetime.now().isoformat()
    }
    update_func("expenses", expense_update)
    
    # 현금 흐름 영향 계산
    expenses = load_func("expenses")
    expense = next((e for e in expenses if e['id'] == expense_id), None)
    
    if expense:
        expense_month = expense.get('expense_date', '')[:7]
        expense_amount = expense.get('amount', 0)
        
        return {
            'success': True,
            'message': f'지출요청서가 승인되었습니다.',
            'cash_flow_impact': {
                'month': expense_month,
                'amount': expense_amount,
                'type': 'expense_increase'
            }
        }
    
    return {'success': False, 'message': '지출요청서 승인 실패'}
```

#### 3단계: 실제 주문 접수 → 배송 → 완료
```sql
-- 고객 PO 접수 시 (상태는 그대로 order)
UPDATE sales_process 
SET customer_po_number = ?,
    notes = '고객 PO 접수 완료'
WHERE id = ?

-- 주문서 생성 (실제 주문 처리)
INSERT INTO orders (
    order_number,
    quotation_id,
    customer_id,
    subtotal,
    tax_amount,
    total_amount,
    status               -- 'pending'
) VALUES (...)

-- 배송 시작
UPDATE sales_process 
SET process_status = 'delivery',
    actual_delivery_date = ?
WHERE id = ?

-- 완료 (실제 수입 확정)
UPDATE sales_process 
SET process_status = 'completed'
WHERE id = ?
```

### 현금 흐름 대시보드 기능

### 영업 프로세스 트리거 (현금 흐름 중심)
```python
def on_quotation_approval_for_cashflow(quotation_id, save_func, load_func):
    """견적서 승인 시 현금 흐름 예측을 위한 영업 프로세스 생성"""
    
    quotation = get_quotation_by_id(quotation_id, load_func)
    
    # 영업 프로세스 생성 (현금 흐름 예측용)
    sales_process_data = {
        'process_number': generate_process_number(),
        'quotation_id': quotation_id,
        'customer_name': quotation.get('customer_name'),
        'customer_company': quotation.get('company'),
        'sales_rep_id': quotation.get('sales_rep_id'),
        'process_status': 'order',  # 주문 예정 상태로 시작
        'item_description': quotation.get('item_name'),
        'quantity': quotation.get('quantity'),
        'unit_price': quotation.get('unit_price'),
        'total_amount': quotation.get('total_amount'),  # 예상 수입
        'currency': quotation.get('currency'),
        'expected_delivery_date': quotation.get('delivery_date'),  # 예상 수입 시기
        'payment_terms': quotation.get('payment_terms'),
        'profit_margin': calculate_margin_from_quotation(quotation)  # 예상 마진
    }
    
    # 현금 흐름 예측 시작
    return save_func("sales_process", sales_process_data)
```

### 영업 프로세스 조회 패턴

#### 전체 영업 현황 조회
```python
def get_sales_process_overview(load_func):
    """영업 프로세스 전체 현황"""
    sales_processes = load_func("sales_process")
    
    # 단계별 집계
    status_counts = {}
    for process in sales_processes:
        status = process.get('process_status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return status_counts

# 결과 예시
# {
#   'quotation': 15,
#   'negotiation': 8,
#   'contract': 3,
#   'order': 12,
#   'delivery': 5,
#   'completed': 45
# }
```

#### 영업 담당자별 현황
```python
def get_sales_by_rep(sales_rep_id, load_func):
    """영업 담당자별 프로세스 현황"""
    sales_processes = load_func("sales_process")
    rep_processes = [p for p in sales_processes if p.get('sales_rep_id') == sales_rep_id]
    
    # 금액 집계
    total_amount = sum(p.get('total_amount', 0) for p in rep_processes)
    
    return {
        'total_processes': len(rep_processes),
        'total_amount': total_amount,
        'processes_by_status': group_by_status(rep_processes)
    }
```

#### 영업 이력 추적
```python
def get_process_history(process_id, load_func):
    """특정 영업 프로세스의 전체 이력"""
    history = load_func("sales_process_history")
    process_history = [h for h in history if h.get('sales_process_id') == process_id]
    
    # 시간 순 정렬
    process_history.sort(key=lambda x: x.get('change_date', ''))
    
    return process_history
```

### 영업 프로세스 상태 관리 (현금 흐름 중심)

#### 상태 전환 규칙 (견적서 승인 후 order부터 시작)
```python
VALID_STATUS_TRANSITIONS = {
    # 견적서 승인 후 주문부터 시작 (현금 흐름 예측 즉시 시작)
    'order': ['delivery', 'cancelled'],       # 주문 → 배송 or 취소
    'delivery': ['completed', 'order'],       # 배송 → 완료 or 주문(반품)
    'completed': [],                          # 최종 상태 (실제 수입 확정)
    'cancelled': []                           # 종료 상태
}

def validate_status_change(current_status, new_status):
    """상태 전환 유효성 검증"""
    valid_transitions = VALID_STATUS_TRANSITIONS.get(current_status, [])
    return new_status in valid_transitions
```

#### 견적서 승인 시 현금 흐름 예측 시작
```python
def handle_quotation_approval_for_cashflow(quotation_id, approver_id, update_func, save_func, load_func):
    """견적서 승인 시 현금 흐름 예측을 위한 영업 프로세스 즉시 시작"""
    
    # 1. 견적서 상태 업데이트
    quotation_update = {
        'id': quotation_id,
        'status': '승인됨',
        'updated_at': datetime.now().isoformat()
    }
    update_func("quotations", quotation_update)
    
    # 2. 영업 프로세스 즉시 생성 (현금 흐름 예측용)
    success = on_quotation_approval_for_cashflow(quotation_id, save_func, load_func)
    
    if success:
        # 3. 현금 흐름 대시보드 업데이트 트리거
        return {
            'success': True,
            'message': '견적서 승인완료! 현금 흐름 예측이 시작되었습니다.',
            'cash_flow_impact': {
                'expected_income': get_expected_income_from_quotation(quotation_id, load_func),
                'expected_month': get_expected_delivery_month(quotation_id, load_func)
            }
        }
    
    return {'success': False, 'message': '영업 프로세스 생성 실패'}
```

#### 자동 상태 동기화
```python
def sync_process_status(process_id, update_func, load_func):
    """견적서/주문서 상태와 영업 프로세스 동기화"""
    process = get_sales_process_by_id(process_id, load_func)
    
    # 견적서 상태 확인
    if process.get('quotation_id'):
        quotation = get_quotation_by_id(process['quotation_id'], load_func)
        if quotation.get('status') == '승인됨' and process.get('process_status') == 'negotiation':
            update_process_status(process_id, 'contract', update_func)
    
    # 주문서 상태 확인
    if process.get('order_id'):
        order = get_order_by_id(process['order_id'], load_func)
        if order.get('status') == 'delivered' and process.get('process_status') == 'delivery':
            update_process_status(process_id, 'completed', update_func)
```

---

## 🎨 주요 기능별 개발 가이드

### 1. 견적서 관리 (quotations)
**핵심 기능:**
- 실시간 고객/제품 선택 연동
- VND 기준 가격 계산 (환율 적용)
- 제품 원가 연동 마진 계산
- HTML 출력 (인쇄용)

**중요 개발 포인트:**
```python
# 제품 선택 시 원가 정보 로드
selected_product = get_product_by_id(product_id)
cost_price_usd = selected_product.get('cost_price_usd', 0)  # 정확한 컬럼명

# VND 변환
exchange_rate = 24000  # 기본값
unit_price_vnd = unit_price_usd * exchange_rate

# 마진 계산
margin_rate = calculate_margin(unit_price_usd, cost_price_usd)
```

### 2. 제품 관리 (products)
**핵심 기능:**
- USD 원가/판매가 관리
- VND 판매가 자동 계산
- 다국어 제품명 지원
- 재고 관리

**중요 개발 포인트:**
```python
# 제품 등록 시 정확한 컬럼 매핑
product_data = {
    'product_name': product_name_en,        # 기본명
    'product_name_en': product_name_en,     # 영문명
    'product_name_vn': product_name_vn,     # 베트남어명
    'cost_price_usd': cost_price_usd,       # USD 원가
    'selling_price_usd': selling_price_usd, # USD 판매가
    'unit_price_vnd': unit_price_vnd,       # VND 판매가
    'is_active': True,                      # Boolean 상태
}
```

### 3. 고객 관리 (customers)
**핵심 기능:**
- KAM 정보 관리
- 사업자 정보 관리
- 견적서 연결 확인
- CSV 업로드/다운로드

### 4. 지출 관리 (expenses)
**핵심 기능:**
- 다중 통화 지원
- 승인 워크플로우
- 출력 양식 생성

---

## 🚨 현재 문제 및 해결 방안

### 1. 견적서-제품 원가 연동 문제 (Critical)
**문제:** quotations 테이블에 원가 컬럼 없음
**해결:** products 테이블의 cost_price_usd 조회

```python
# ❌ 잘못된 방법
cost_price = quotation_data.get('cost_price', 0)

# ✅ 올바른 방법  
product_id = quotation_data.get('product_id')
products = load_func("products")
product = next((p for p in products if p['id'] == product_id), None)
cost_price_usd = product.get('cost_price_usd', 0) if product else 0
```

### 2. 컬럼명 불일치 문제
**주의사항:**
- `cost_price` (X) → `cost_price_usd` (O)
- `selling_price` (X) → `selling_price_usd` (O)
- `unit_price_vnd` (O) - 정확함

---

## 📋 다음 단계 우선순위

### 즉시 해결 (Critical)
1. **견적서 원가 연동 수정**: cost_price → cost_price_usd
2. **마진 계산 로직 수정**: 제품 테이블 조회 방식 변경

### 단기 개선 (High)  
3. **제품 관리 고도화**: CSV 업로드, 재고 관리
4. **견적서 워크플로우**: 승인 프로세스, 리비전 관리

### 중기 개발 (Medium)
5. **통합 대시보드**: 견적-고객-제품 연동 통계
6. **고급 기능**: 자동 견적번호, 이메일 발송

---

## 💾 백업 및 연속성 관리

### 백업 파일 생성 (규칙 10)
매 개발 세션 종료 시 다음 정보 포함:
- 시스템 현황 및 완성도
- 함수 리스트 및 호출 관계
- 실제 DB 스키마 정보
- 진행 사항 및 다음 단계
- 현재 문제점 및 해결 방안

### 새 채팅에서 개발 재개
1. 최신 규칙 파일 (V10) 업로드
2. 백업 파일 업로드  
3. "규칙 V10 + 이 백업 기준으로 개발 계속해줘"

---

## 🔍 개발 시 체크리스트

### DB 관련 작업 전
- [ ] 실제 테이블 스키마 확인
- [ ] 컬럼명 정확히 매핑
- [ ] 데이터 타입 확인
- [ ] FK 관계 확인

### 코딩 전
- [ ] 수정 내용 설명
- [ ] 사용자 승인 받기
- [ ] 전체 파일 단위로 작성
- [ ] Import 순서 준수

### 완료 후
- [ ] 동작 테스트
- [ ] 에러 처리 확인
- [ ] 백업 파일 업데이트

---

## 🎯 최종 목표

**완전한 ERP 시스템 구축**
- 견적서-고객-제품 완전 연동
- 실시간 마진 계산 및 분석
- 다국어 지원 (한국어, 영어, 베트남어)
- 인쇄/출력 최적화
- CSV 업로드/다운로드
- 권한 기반 사용자 관리

**현재 상태: 95% 완성**
- 남은 작업: 견적서 원가 연동 1개 이슈
- 예상 완료 시간: 10분

---

## 📚 추가 참고사항

### Supabase 특화 고려사항
- Row Level Security (RLS) 설정
- Realtime 기능 활용 가능
- PostgreSQL 함수 활용
- 자동 API 생성 활용

### 성능 최적화
- 쿼리 최적화 (필요한 컬럼만 조회)
- 인덱스 활용
- 캐싱 전략
- 페이지네이션

이 가이드를 기준으로 새로운 채팅에서도 일관된 품질의 개발이 가능합니다.