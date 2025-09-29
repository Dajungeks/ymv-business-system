# YMV ERP 시스템 백업 파일 - 아이템별 발주 시스템 설계 완료

## 📊 현재 상황

### 프로젝트 기본 정보
- **프로젝트명**: YMV 관리 프로그램 (ERP 시스템)
- **개발 언어**: Python + Streamlit
- **데이터베이스**: Supabase (PostgreSQL)
- **현재 진행률**: 모듈 분리 완료 + 아이템별 발주 시스템 설계 완료
- **프로젝트 위치**: D:\ymv-business-system

### Supabase 연결 정보
```
SUPABASE_URL = "https://eqplgrbegwzeynnbcuep.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
GitHub: https://github.com/dajungeks/ymv-business-system.git
```

## 🎯 완료된 작업

### 1. 모듈 분리 완료 (이전 단계)
- sales_process_dashboard.py: 영업 현황 대시보드
- purchase_order_management.py: 발주 관리 (개선 예정)
- inventory_management.py: 재고 관리
- profit_analysis.py: 수익 분석
- sales_process_main.py: 통합 메인

### 2. 현재 시스템 문제점 분석 완료

#### 기존 DB 구조 문제점
1. **quotations_detail**: 견적서당 1개 아이템만 처리
2. **quotation_items**: 설계되었지만 미사용 상태
3. **sales_process**: 견적서 전체를 하나로 통합 처리
4. **발주 시스템**: 아이템별 처리 불가능

#### 비즈니스 로직 문제점
- 견적서에 여러 아이템이 있을 때 개별 처리 불가
- 아이템별 재고 확인 및 발주 결정 불가
- 제품과 서비스의 구분 처리 미흡

## 🗄️ 현재 DB 테이블 현황

### 기존 테이블 목록 (확인됨)
```
attendance, audit_logs, cash_flows, company_info, customers, 
delivery_shipment, departments, document_sequences, employee_details, 
employee_history, employee_leaves, employees, exchange_rates, expenses, 
expenses_detail, internal_processing, inventory_receiving, monthly_budgets, 
orders, payroll, positions, product_categories, product_codes, products, 
products_master, products_multilingual, products_with_codes, purchase_categories, 
purchase_orders_inventory, purchase_orders_to_supplier, purchases, purchases_detail, 
quality_inspection, quotation_items, quotations, quotations_detail, sales_orders, 
sales_process, sales_process_analysis, sales_process_history, suppliers, 
system_settings, translations, user_permissions, users
```

### 핵심 테이블 구조 분석

#### quotation_items (설계됨, 미사용)
- item_id, quotation_id, product_id, item_description
- quantity, unit_price, line_total, notes

#### quotations_detail (실제 사용 중)
- 견적서당 1개 아이템만 처리하는 한계적 구조
- item_name, item_code, quantity, unit_price 등

#### sales_process (현재)
- 견적서 전체를 하나의 프로세스로 처리
- quotation_id 연결되어 있으나 아이템별 분할 불가

#### products (활용 가능)
- product_code, product_name, stock_quantity
- 재고 정보 포함, 아이템별 발주 결정에 활용

#### suppliers (활용 가능)  
- name, company_name, contact_person, email, phone
- 발주 시 공급업체 선택에 활용

## 🔄 근본적 해결을 위한 새로운 설계

### A. 새로운 DB 구조 설계

#### 1. quotation_items 테이블 재활성화
```sql
DROP TABLE IF EXISTS quotation_items CASCADE;
CREATE TABLE quotation_items (
    id SERIAL PRIMARY KEY,
    quotation_id INTEGER REFERENCES quotations(id),
    
    -- 제품 연결
    product_id INTEGER REFERENCES products(id),
    product_code VARCHAR(100),
    
    -- 아이템 정보
    item_description TEXT NOT NULL,
    item_type VARCHAR(20) DEFAULT 'product' CHECK (item_type IN ('product', 'service')),
    
    -- 수량/가격
    quantity NUMERIC(10,2) NOT NULL,
    unit_price NUMERIC(15,2) NOT NULL,
    line_total NUMERIC(15,2) NOT NULL,
    
    -- 메타데이터
    line_number INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. sales_process_items 테이블 신규 생성
```sql
DROP TABLE IF EXISTS sales_process_items CASCADE;
CREATE TABLE sales_process_items (
    id SERIAL PRIMARY KEY,
    
    -- 연결 정보
    quotation_id INTEGER REFERENCES quotations(id),
    quotation_item_id INTEGER REFERENCES quotation_items(id),
    product_id INTEGER REFERENCES products(id),
    
    -- 프로세스 정보
    process_number VARCHAR(50) UNIQUE NOT NULL,
    item_process_status VARCHAR(50) DEFAULT 'approved',
    
    -- 고객 정보 (성능을 위해 복사)
    customer_name VARCHAR(200),
    customer_company VARCHAR(200),
    customer_email VARCHAR(100),
    customer_phone VARCHAR(50),
    
    -- 아이템 정보
    product_code VARCHAR(100),
    item_description TEXT,
    item_type VARCHAR(20),
    
    -- 수량/가격
    approved_quantity NUMERIC(10,2),
    unit_price NUMERIC(15,2),
    line_total NUMERIC(15,2),
    currency VARCHAR(10),
    
    -- 재고 분석
    current_stock INTEGER DEFAULT 0,
    reserved_stock INTEGER DEFAULT 0,
    available_stock INTEGER DEFAULT 0,
    
    -- 처리 계획
    internal_quantity INTEGER DEFAULT 0,
    external_quantity INTEGER DEFAULT 0,
    processing_type VARCHAR(20) CHECK (processing_type IN ('internal', 'external', 'mixed', 'service')),
    
    -- 처리 결과 연결
    internal_processing_id INTEGER REFERENCES internal_processing(id),
    external_order_id INTEGER REFERENCES purchase_orders_to_supplier(id),
    
    -- 일정
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    
    -- 영업 담당
    sales_rep_id INTEGER REFERENCES employees(id),
    
    -- 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    processed_by INTEGER REFERENCES employees(id)
);
```

### B. 데이터 마이그레이션 계획

#### 1단계: 기존 데이터 백업
```sql
CREATE TABLE quotations_detail_backup AS SELECT * FROM quotations_detail;
CREATE TABLE sales_process_backup AS SELECT * FROM sales_process;
```

#### 2단계: 데이터 변환
```sql
-- quotations_detail → quotations + quotation_items
-- sales_process → sales_process_items (아이템별 분할)
```

#### 3단계: 기존 테이블 정리
- quotations_detail 비활성화 또는 백업 전용
- sales_process 레거시 테이블로 변경

### C. 새로운 비즈니스 프로세스

#### 견적서 승인 → 아이템별 프로세스 생성
```
견적서 승인 시:
quotations(approved) → sales_process_items 생성
(각 quotation_items → 개별 sales_process_items)
```

#### 아이템별 발주 프로세스
```
각 sales_process_items에 대해:
├── 아이템 타입 확인 (product/service)
├── 재고 확인 (products.stock_quantity)
├── 처리 방안 결정:
│   ├── 재고 충분 → internal_processing
│   ├── 재고 부족 → purchase_orders_to_supplier  
│   ├── 혼합 처리 → 둘 다 생성 (수량 분할)
│   └── 서비스 → 발주 제외, 바로 완료
└── 개별 발주 실행
```

#### 발주 관리 UI 흐름
```
고객 주문 기반 발주:
1. 승인된 견적서 선택
2. 아이템별 목록 표시:
   [ITEM-001] Hot Runner Nozzle (수량: 10개)
   ├── 현재 재고: 6개
   ├── 처리 가능: 6개 (내부)
   ├── 부족 수량: 4개 (외주)
   └── [처리 방안 선택] [내부 처리] [외주 발주]
3. 각 아이템별 개별 처리
```

## 💻 영향받는 기존 코드

### 높은 영향도 (완전 재작성 필요)
- **quotation_management.py**: 다중 아이템 견적서 지원
- **sales_process_main.py**: sales_process_items 기반으로 변경
- **purchase_order_management.py**: 아이템별 발주 로직 구현
- **sales_process_dashboard.py**: 아이템별 현황 표시

### 중간 영향도 (부분 수정 필요)
- **profit_analysis.py**: 아이템별 수익 분석
- **dashboard.py**: 통계 로직 변경

### 낮은 영향도 (거의 변경 없음)
- customer_management.py
- product_management.py  
- supplier_management.py
- employee_management.py
- expense_management.py

## 🚀 확정된 진행 계획

### 옵션 1: 전면 개편 (선택됨)
1. **DB 구조 먼저 변경**
2. **기존 코드 순차적 업데이트**
3. **완전한 아이템별 시스템 구축**

### 예상 작업 순서
1. **DB 테이블 생성 및 마이그레이션**
2. **견적서 관리 시스템 재작성**
3. **영업 프로세스 관리 재작성**
4. **발주 관리 시스템 재작성**
5. **대시보드 및 분석 화면 수정**
6. **전체 시스템 테스트**

## 📋 다음 단계

### 즉시 진행할 작업
1. **새로운 테이블 생성 SQL 실행**
2. **기존 데이터 마이그레이션 스크립트 작성**
3. **견적서 관리 화면 재설계**

### 단계별 개발 순서
1. DB 구조 변경 (1-2일)
2. 견적서 시스템 재작성 (2-3일)  
3. 영업 프로세스 재작성 (2-3일)
4. 발주 시스템 재작성 (3-4일)
5. 통합 테스트 (1-2일)

## 🎯 기대 효과

### 비즈니스 개선
- 견적서 다중 아이템 완벽 지원
- 아이템별 개별 재고 관리 및 발주
- 제품/서비스 구분 처리
- 실제 비즈니스 프로세스와 완벽 일치

### 시스템 개선
- 데이터 정합성 향상
- 확장성 확보
- 유지보수성 개선
- 코드 구조 최적화

## 🔄 재개 방법

### 필수 업로드 파일
1. **규칙 V10 파일**: `program_development_rules - V10 Final.txt`
2. **이 백업 파일**: `ymv_backup_aitem_based_purchase_system.md`

### 재개 명령어
```
"규칙 V10 + 이 백업 기준으로 아이템별 발주 시스템 개발 계속해줘"
```

### 현재 진행 상황
- 아이템별 발주 시스템 완전 설계 완료
- DB 구조 재설계 완료
- 전면 개편 방식 확정
- 다음: DB 테이블 생성 및 마이그레이션 작업 시작

## 📌 중요 참고사항

### 설계 원칙
- 근본적 문제 해결 우선
- DB 변경을 통한 구조적 개선
- 실제 비즈니스 로직 완벽 반영
- 확장 가능한 아키텍처 구축

### 개발 우선순위
1. 데이터 정합성 확보
2. 비즈니스 로직 정확성
3. 사용자 경험 개선
4. 코드 품질 향상

이 시점에서 YMV ERP 시스템은 단순한 모듈 분리를 넘어서 완전한 아이템별 발주 시스템으로 진화할 준비가 완료되었습니다.