# YMV ERP 시스템 완전 개발 백업 - v20 견적서+제품관리 통합완성

## 🎯 현재 개발 상황 요약

### ✅ 완성된 시스템
1. **견적서 관리 시스템** - 100% 완성
2. **고객 관리 시스템** - 100% 완성  
3. **제품 관리 시스템** - 95% 완성 (DB 연동 완료)
4. **main.py 통합** - 완료

### ⚠️ 현재 해결 중인 문제
- **견적서-제품 원가 연동 문제**: 제품 DB에는 `cost_price_usd` 저장됨, 견적서에서 조회 실패

---

## 📊 데이터베이스 스키마 현황

### products 테이블 (완전 확인됨)
```sql
CREATE TABLE products (
    id                  serial PRIMARY KEY,
    product_code        varchar NOT NULL,
    product_name        varchar NOT NULL,
    product_name_en     varchar,
    product_name_vn     varchar,
    product_name_kr     varchar,
    category            varchar NOT NULL,
    code_category       varchar,
    display_category    varchar,
    product_code_id     integer,
    
    -- 가격 정보
    unit_price          numeric DEFAULT 0,
    unit_price_vnd      numeric DEFAULT 0,
    cost_price_usd      numeric DEFAULT 0,     -- ✅ 원가 (USD)
    cost_price_cny      numeric DEFAULT 0,     -- ✅ 원가 (CNY)
    selling_price_usd   numeric DEFAULT 0,     -- ✅ 판매가 (USD)
    
    -- 기본 정보
    unit                varchar DEFAULT '개',
    currency            varchar DEFAULT 'USD',
    supplier            varchar,
    stock_quantity      integer DEFAULT 0,
    minimum_order_qty   integer DEFAULT 1,
    lead_time_days      integer DEFAULT 30,
    
    -- 상세 정보
    description         text,
    specifications      text,
    material            varchar,
    weight_kg           numeric,
    dimensions          varchar,
    notes               text,
    
    -- 상태 관리
    is_active           boolean DEFAULT true,
    created_at          timestamptz DEFAULT now(),
    updated_at          timestamptz DEFAULT now()
);
```

### quotations 테이블 (Step 18-4 완성)
```sql
CREATE TABLE quotations (
    id                  serial PRIMARY KEY,
    quote_number        varchar(255),
    revision_number     varchar(50),
    quote_date          date,
    valid_until         date,
    currency            varchar(10),
    status              varchar(50),
    
    -- 고객 정보
    customer_id         integer REFERENCES customers(id),
    
    -- 담당자 정보  
    sales_rep_id        integer REFERENCES employees(id),
    
    -- 제품 정보
    item_code           varchar(100),
    item_name_en        varchar(255),
    item_name_vn        varchar(255),
    quantity            integer,
    
    -- 가격 정보 (VND 기준)
    unit_price          numeric,        -- VND 단가
    unit_price_vnd      numeric,        -- VND 단가 (명시적)
    unit_price_usd      numeric,        -- USD 참고가
    discount_rate       numeric,
    discounted_price    numeric,        -- VND 할인가
    discounted_price_vnd numeric,       -- VND 할인가 (명시적)
    discounted_price_usd numeric,       -- USD 참고 할인가
    total_amount        numeric,        -- VND 소계
    vat_rate            numeric,
    vat_amount          numeric,        -- VND VAT
    final_amount        numeric,        -- VND 최종 금액
    final_amount_usd    numeric,        -- USD 참고 최종 금액
    exchange_rate       numeric,        -- 적용된 환율
    
    -- 프로젝트 정보
    project_name        varchar(255),
    part_name           varchar(255),
    mold_number         varchar(255),
    part_weight         numeric,
    hrs_info            text,
    resin_type          varchar(255),
    resin_additive      varchar(255),
    sol_material        varchar(255),
    
    -- 거래 조건
    payment_terms       text,
    delivery_date       date,
    lead_time_days      integer,
    remarks             text,
    
    -- 원가 및 마진 정보
    cost_price_usd      numeric,        -- USD 원가
    margin_rate         numeric,
    
    -- 시스템 정보
    created_at          timestamptz,
    updated_at          timestamptz
);
```

### customers 테이블 (Step 18-4 완성)
```sql
CREATE TABLE customers (
    id                  serial PRIMARY KEY,
    company_name        varchar(255) NOT NULL,
    business_number     varchar(50),
    business_type       varchar(100),
    country             varchar(100),
    address             text,
    contact_person      varchar(255) NOT NULL,
    position            varchar(100),
    email               varchar(255) NOT NULL,
    phone               varchar(50) NOT NULL,
    mobile              varchar(50),
    tax_id              varchar(100),
    payment_terms       varchar(100),
    assigned_employee_id integer REFERENCES employees(id),
    
    -- KAM 정보
    kam_name            varchar(255),
    kam_phone           varchar(50),
    kam_position        varchar(100),
    kam_notes           text,
    
    status              varchar(50) DEFAULT 'Active',
    notes               text,
    created_at          timestamptz DEFAULT NOW(),
    updated_at          timestamptz DEFAULT NOW()
);
```

---

## 🏗️ 완성된 시스템 아키텍처

### main.py 구조
```python
# 완성된 Import 구조
from components.quotation_management import show_quotation_management
from components.customer_management import show_customer_management  
from components.product_management import show_product_management
from utils.database import create_database_operations

# 완성된 메뉴 구조
영업 관리:
├── 고객 관리 ✅ (완성)
├── 견적서 관리 ✅ (완성) 
└── 영업 프로세스 ✅ (기존)

운영 관리:
├── 제품 관리 ✅ (완성)
├── 공급업체 관리 ✅ (기존)
└── 구매품 관리 ✅ (기존)
```

### 견적서 관리 시스템 (100% 완성)
**파일**: `components/quotation_management.py`

**주요 기능**:
1. **견적서 작성**: 
   - 실시간 고객/제품 선택 (폼 밖에서)
   - VND 기준 가격 계산
   - USD 환율 적용 (기본 24,000)
   - 실시간 마진 계산 표시
   - 완전한 프로젝트 정보 입력

2. **견적서 목록**: 
   - 페이지네이션, 필터링
   - 상태 변경 기능
   - 통계 정보

3. **견적서 인쇄**: 
   - HTML 다운로드
   - 3개국어 지원

4. **CSV 관리**: 
   - 다운로드 기능

**핵심 함수**:
```python
def show_quotation_management(load_func, save_func, update_func, delete_func)
def render_quotation_form(save_func, load_func)  # 실시간 업데이트
def render_quotation_list(load_func, update_func, delete_func)
def render_quotation_print(load_func)
def generate_quotation_html(quotation, load_func, language)
```

### 고객 관리 시스템 (100% 완성)
**파일**: `components/customer_management.py`

**주요 기능**:
1. **고객 등록**: KAM 정보 포함 완전한 등록
2. **고객 목록**: 검색, 필터링, 편집, 삭제
3. **CSV 관리**: 업로드/다운로드
4. **안전한 삭제**: 견적서 연결 확인

**핵심 함수**:
```python
def show_customer_management(load_func, save_func, update_func, delete_func)
def render_customer_form(save_func)
def render_customer_list(load_func, update_func, delete_func)
def check_customer_deletion_safety(customer_id, load_func)
```

### 제품 관리 시스템 (95% 완성)
**파일**: `components/product_management.py`

**주요 기능**:
1. **제품 등록**: 
   - USD 원가/판매가 입력
   - VND 판매가 입력
   - 실시간 마진 계산
   - 동적 카테고리 관리

2. **제품 목록**: 
   - 검색, 필터링
   - 인라인 편집
   - 원가/마진 표시

3. **CSV 관리**: 다운로드 기능

**실제 DB 컬럼 매핑**:
```python
product_data = {
    'product_name': product_name_en,        # 기본명
    'product_name_en': product_name_en,     # 영문명
    'product_name_vn': product_name_vn,     # 베트남어명
    'cost_price_usd': cost_price_usd,       # USD 원가 ✅
    'selling_price_usd': selling_price_usd, # USD 판매가
    'unit_price_vnd': unit_price_vnd,       # VND 판매가
    'is_active': status == "Active",        # Boolean 상태
}
```

---

## ⚠️ 현재 문제 및 해결 방안

### 1. 견적서-제품 원가 연동 문제

**문제 상황**:
- 제품 관리: `cost_price_usd` 컬럼에 원가 저장 ✅
- 견적서: "⚠️ 원가 정보가 설정되지 않았습니다" 표시 ❌

**원인 분석**:
```python
# 견적서 코드에서 (quotation_management.py)
cost_price = float(selected_product_data.get('cost_price', 0))  # ❌ 잘못된 컬럼명

# 올바른 방법
cost_price_usd = float(selected_product_data.get('cost_price_usd', 0))  # ✅
```

**해결 방법**:
견적서 `render_quotation_form()` 함수에서 다음 변경 필요:
1. `cost_price` → `cost_price_usd` 변경
2. 조건 검사 `if cost_price_usd > 0:` 변경
3. 마진 계산 로직 수정

---

## 🔧 시스템 통합 상태

### ConnectionWrapper 및 DatabaseOperations (규칙 18 완성)
**파일**: `utils/database.py`

**주요 클래스**:
```python
class ConnectionWrapper:
    def execute_query(operation, table, data, filters)
    def _execute_update(table, data, filters)  # ID 포함 방식

class DatabaseOperations:
    def update_data(table, data, id_field="id")  # data에 ID 포함 필요
```

**올바른 업데이트 방식**:
```python
# 제품 수정 시
update_data['id'] = product_id  # ID 포함 필수
success = update_func('products', update_data)
```

---

## 🎨 주요 기능 특징

### 견적서 시스템 특징
1. **실시간 인터랙션**: 
   - 고객 선택 → 즉시 정보 업데이트
   - 제품 선택 → 즉시 원가/가격 표시
   - 수량/할인율 변경 → 실시간 계산

2. **VND 중심 가격 체계**:
   - 환율 입력 (기본 24,000 VND/USD)
   - VND 기준 최종 견적
   - USD 참고가 병행 표시

3. **완전한 HTML 출력**:
   - 인쇄 최적화 CSS
   - 3개국어 지원
   - 모든 프로젝트 정보 포함

### 제품 관리 특징
1. **다중 통화 지원**:
   - USD 원가/판매가
   - VND 판매가
   - 실시간 마진 계산

2. **동적 카테고리**: 
   - 기존 제품에서 카테고리 자동 로드
   - 새 카테고리 직접 입력 가능

3. **안전한 CRUD**: 
   - 중복 코드 방지
   - DB 스키마 완전 호환

---

## 📋 다음 단계 우선순위

### 즉시 해결 (Critical)
1. **견적서 원가 연동 수정**: 
   - `cost_price` → `cost_price_usd` 변경
   - 마진 계산 로직 수정

### 단기 개선 (High)
2. **제품 관리 고도화**:
   - 대량 CSV 업로드 구현
   - 재고 관리 기능 강화

3. **견적서 워크플로우**:
   - 승인 프로세스 추가
   - 리비전 관리 고도화

### 중기 개발 (Medium)
4. **통합 대시보드**: 
   - 견적서-고객-제품 연동 통계
   - 매출/마진 분석

5. **고급 기능**:
   - 자동 견적번호 생성 개선
   - 이메일 발송 기능

---

## 🧪 테스트 상태

### 완료된 테스트
- ✅ 고객 관리: 등록/수정/삭제/검색
- ✅ 제품 관리: 등록/수정/상태변경
- ✅ 견적서 작성: 기본 기능 동작
- ✅ 견적서 목록: 필터링/페이지네이션
- ✅ 견적서 인쇄: HTML 다운로드

### 테스트 필요
- ⚠️ 견적서 원가 표시 수정 후 재테스트
- 📝 제품-견적서 완전 연동 테스트
- 📝 마진 계산 정확성 검증

---

## 💾 백업 활용 방법

### 새 채팅에서 개발 계속하기
1. 이 백업 파일 업로드
2. "이 백업을 기반으로 견적서 원가 연동 문제를 해결해줘" 요청
3. 즉시 개발 재개 가능

### 현재 상태 요약
- **전체 진행률**: 95% 완성
- **남은 작업**: 견적서-제품 원가 연동 1개 이슈만 해결하면 완성
- **예상 완료 시간**: 10분 이내

---

## 🔍 기술적 고려사항

### 성능 최적화
- DataFrame 캐싱 적용
- 실시간 계산 최적화
- DB 쿼리 효율성 확보

### 보안 고려사항
- SQL Injection 방지 (Supabase 자동 처리)
- 사용자 권한 관리 (기존 auth 시스템 활용)
- 데이터 유효성 검증 강화

### 확장성 고려사항
- 컴포넌트 기반 아키텍처 유지
- 다국어 지원 확장 준비
- API 연동 준비 (Excel 연동 등)

---

**📌 중요**: 현재 시스템이 거의 완성 단계이므로, 견적서-제품 원가 연동 문제만 해결하면 완전한 ERP 시스템이 됩니다. 백업 시점 기준으로 모든 기본 기능이 구현되었고, 실제 업무에 사용 가능한 수준입니다.