# YMV ERP 시스템 백업 파일 v5.0 - 발주서 프린트 및 연동 개선 준비

## 📊 시스템 현황

### 프로젝트 기본 정보
- **프로젝트명**: YMV 관리 프로그램 (ERP 시스템)
- **개발 언어**: Python + Streamlit
- **데이터베이스**: Supabase (PostgreSQL)
- **현재 진행률**: DB 확인 완료, 기능 개선 준비 (98%)
- **프로젝트 위치**: D:\ymv-business-system

### Supabase 연결 정보
```
SUPABASE_URL = "https://eqplgrbegwzeynnbcuep.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
GitHub: https://github.com/dajungeks/ymv-business-system.git
```

## 🗄️ DB 스키마 현황 (완전 확인됨)

### 주요 테이블 상태
```sql
✅ sales_process (영업 프로세스)
✅ purchase_orders_to_supplier (고객 주문 발주)
✅ purchase_orders_inventory (재고 보충 발주) 
✅ internal_processing (내부 재고 처리)
✅ inventory_receiving (입고 관리)
✅ quality_inspection (검수 관리)
✅ delivery_shipment (출고 관리)
```

### DB 스키마 상세 (확인된 구조)

#### purchase_orders_inventory (재고 보충 발주)
```sql
id: integer (PK, auto)
po_number: varchar (NOT NULL, UNIQUE)
purchase_type: varchar (default 'inventory_replenishment')
sales_process_id: integer (NULL - 재고용이므로)
item_code, item_name, item_description, category: varchar/text
supplier_name (NOT NULL), supplier_contact, supplier_email, supplier_phone: varchar
order_date (NOT NULL), expected_arrival_date: date
quantity (NOT NULL), unit_cost (NOT NULL), total_cost (NOT NULL): numeric
currency (default 'USD'), payment_terms, status (default 'ordered'): varchar
target_warehouse, min_stock_level, reorder_point: varchar/integer
purchase_reason, notes: varchar/text
created_at, updated_at (auto now()), created_by: timestamp/integer
```

#### internal_processing (내부 재고 처리)
```sql
id: integer (PK, auto)
sales_process_id: integer (NOT NULL)
processing_type: varchar (default 'internal_stock')
warehouse_location: varchar (NOT NULL)
processed_quantity: integer (NOT NULL)
processing_date: date (NOT NULL)
processed_by: integer (NOT NULL)
notes: text
created_at: timestamp (auto now())
```

#### purchase_orders_to_supplier (고객 주문 발주)
```sql
id, po_number (NOT NULL), sales_process_id (NOT NULL)
supplier_name (NOT NULL), supplier_contact, supplier_email, supplier_phone
order_date (NOT NULL), expected_arrival_date, actual_arrival_date
item_description (NOT NULL), quantity (NOT NULL), unit_cost (NOT NULL), total_cost (NOT NULL)
currency (default 'USD'), payment_terms, status (default 'ordered')
tracking_number, notes
created_at, updated_at (auto now())
```

## 📁 모듈 구조 (완성됨)

### 현재 파일 구조
```
components/
├── sales_process_main.py (통합 메인)
├── sales_process_dashboard.py (영업 현황)
├── purchase_order_management.py (발주 관리)
├── inventory_management.py (재고 관리)
├── profit_analysis.py (수익 분석)
├── quotation_management.py (견적서 - HTML 양식 보유)
├── customer_management.py
├── product_management.py
└── main.py (메인 앱)
```

### 모듈별 기능 현황

#### 1. sales_process_main.py (통합)
```python
def show_sales_process_management():
    # 4개 탭 구조:
    # tab1: show_sales_process_dashboard(load_func)
    # tab2: show_purchase_order_management(load_func, save_func, update_func, current_user)
    # tab3: show_inventory_management(load_func, save_func, update_func, current_user)
    # tab4: show_profit_analysis(load_func)
```

#### 2. sales_process_dashboard.py (현황)
```python
def show_sales_process_dashboard(load_func):
    # 영업 프로세스 현황 대시보드
    # 메트릭: 총 프로세스, 총 거래액, 완료율, 진행 중
    # 상태별 분포 차트, 지연 알림, 프로세스 목록
    
def render_delay_alerts(processes):
    # 지연된 프로세스 알림 시스템
```

#### 3. purchase_order_management.py (발주)
```python
def show_purchase_order_management(load_func, save_func, update_func, current_user):
    # 3가지 발주 유형:
    # 1. 고객 주문 기반 발주 (내부 재고 vs 외주 발주)
    # 2. 재고 보충 발주 (영업과 무관)
    # 3. 모든 발주서 조회

def render_customer_order_based_purchase():
    # 승인된 영업 프로세스 → 내부 처리 or 외주 발주 선택
    
def process_internal_stock():
    # 내부 재고 처리 → internal_processing 테이블 저장
    
def show_customer_order_external_form():
    # 외주 발주 폼 → purchase_orders_to_supplier 테이블 저장
    
def render_inventory_replenishment_purchase():
    # 재고 보충 발주 → purchase_orders_inventory 테이블 저장

def generate_document_number(doc_type, save_func):
    # POC-2025-0001: 고객 주문 발주
    # POI-2025-0001: 재고 보충 발주
```

#### 4. inventory_management.py (재고)
```python
def show_inventory_management():
    # 3개 탭: 입고 관리, 검수 관리, 출고 관리
    
def render_receiving_management():
    # 발주서 → 입고 처리 → inventory_receiving 저장
    
def render_quality_inspection():
    # 입고 → 검수 처리 → quality_inspection 저장
    
def render_shipping_management():
    # 검수 → 출고 처리 → delivery_shipment 저장
```

#### 5. quotation_management.py (견적서 - HTML 양식 보유)
```python
def generate_quotation_html(quotation, load_func, language='한국어'):
    # ✅ 완성된 HTML 양식 (A4 크기, 프린트 가능)
    # 회사 정보, 고객 정보, 제품 테이블, 프로젝트 정보, 서명란
    # 이 양식을 발주서로 변환 필요
```

## 🎯 즉시 개선 필요 사항

### Phase 1: 발주서 프린트 기능 추가
**목표**: 견적서 HTML → 발주서 HTML 변환

**변경 사항**:
1. `purchase_order_management.py`에 HTML 생성 함수 추가
2. 견적서 양식 → 발주서 양식 변환:
   - 고객 정보 → 공급업체 정보
   - YMV → 발주자, 공급업체 → 수주자
   - 하단 도장: YMV만 표시
   - 프로젝트 정보 테이블 제거
3. 발주서 번호, 발주일, 납기일 등 발주 정보 표시

**구현 위치**:
```python
# purchase_order_management.py에 추가
def generate_purchase_order_html(order_data, order_type='customer'): # customer or inventory
def render_purchase_order_print(load_func): # 프린트 기능
```

### Phase 2: 영업 현황 연결 강화
**목표**: 승인된 프로세스에서 바로 발주 가능

**변경 사항**:
1. `sales_process_dashboard.py` 수정:
   - 프로세스 목록에 "발주하기" 버튼 추가
   - approved 상태인 프로세스만 버튼 표시
2. 버튼 클릭 → 발주 관리 탭으로 이동 + 해당 프로세스 자동 선택

**구현 위치**:
```python
# sales_process_dashboard.py 수정
def show_sales_process_dashboard(load_func):
    # 프로세스 목록에 발주 버튼 추가
    
# sales_process_main.py 수정  
def show_sales_process_management():
    # 탭 간 데이터 공유 로직 추가
```

### Phase 3: 사용자 경험 개선
**목표**: 전체 흐름 최적화

**변경 사항**:
1. 상태 업데이트 자동화
2. 알림 시스템 개선
3. 워크플로우 가이드 추가

## 🔄 비즈니스 프로세스 흐름

### 현재 완성된 흐름
```
1. 견적서 작성 → 승인 → 영업 프로세스 자동 생성
                     ↓
2. 영업 현황에서 확인 → "발주하기" 버튼 (추가 예정)
                     ↓
3. 발주 관리:
   ├─ 내부 재고 처리 → internal_processing
   └─ 외주 발주 → purchase_orders_to_supplier
                     ↓
4. 재고 관리:
   입고 → 검수 → 출고 → 완료
```

### 발주서 출력 흐름 (추가 예정)
```
발주 등록 → 발주서 HTML 생성 → 프린트/다운로드 → 공급업체 전달
```

## 💻 함수 호출 관계도

### 현재 main.py 호출 구조
```python
main() 
└── show_sales_process_management_page()
    └── show_sales_process_management(
        db_operations.load_data,
        db_operations.save_data,
        db_operations.update_func,
        db_operations.delete_data,
        auth_manager.get_current_user,
        auth_manager.check_permission,
        get_approval_status_info,
        calculate_expense_statistics,
        create_csv_download,
        render_print_form
    )
```

### sales_process_main.py 내부 호출
```python
show_sales_process_management()
├── tab1: show_sales_process_dashboard(load_func)
├── tab2: show_purchase_order_management(load_func, save_func, update_func, current_user)
├── tab3: show_inventory_management(load_func, save_func, update_func, current_user)
└── tab4: show_profit_analysis(load_func)
```

## 🔧 개발 가이드

### 견적서 → 발주서 HTML 변환 가이드
**기존 견적서 HTML 구조**:
```html
<div class="header">
    <div> <!-- 고객 정보 --> </div>
    <div> <!-- YMV 정보 --> </div>
</div>
<table> <!-- 제품 정보 --> </table>
<table class="project-table"> <!-- 프로젝트 정보 --> </table>
<div class="signature-section">
    <div>Authorised Signature (YMV)</div>
    <div>Customer Signature</div>
</div>
```

**발주서 HTML 구조** (변경 예정):
```html
<div class="header">
    <div> <!-- YMV 발주자 정보 --> </div>
    <div> <!-- 공급업체 수주자 정보 --> </div>
</div>
<table> <!-- 발주 제품 정보 --> </table>
<!-- 프로젝트 정보 테이블 제거 -->
<div class="signature-section">
    <div>발주자 서명 (YMV만)</div>
</div>
```

### CSS 클래스 재사용
기존 quotation HTML의 CSS 클래스를 그대로 사용하여 일관된 디자인 유지

### 데이터 매핑
```python
# 견적서 데이터 → 발주서 데이터
customer_info → supplier_info
quotation_data → purchase_order_data
quote_number → po_number
```

## 📋 다음 채팅 재개 방법

### 필수 업로드 파일
1. **이 백업 파일**: `ymv_backup_v5_complete.md`
2. **규칙 파일**: `program_development_rules - V10 Final.txt`

### 재개 명령어
```
"백업 v5.0 + 규칙 V10 기준으로 발주서 프린트 기능부터 개발해줘"
```

### 우선 개발 순서
1. **발주서 HTML 생성 함수** (purchase_order_management.py)
2. **영업 현황 발주 버튼** (sales_process_dashboard.py)  
3. **전체 흐름 최적화** (사용자 경험 개선)

## 🎯 핵심 개발 포인트

### 1. 발주서 HTML 템플릿
- 견적서 HTML을 기반으로 발주서 전용 템플릭 생성
- 고객사 → 공급업체 정보로 교체
- 프로젝트 정보 섹션 제거
- YMV 단독 서명란

### 2. 발주서 생성 로직
```python
def generate_purchase_order_html(order_data, order_type):
    if order_type == 'customer':
        # purchase_orders_to_supplier 데이터 사용
    elif order_type == 'inventory':  
        # purchase_orders_inventory 데이터 사용
```

### 3. 영업 현황 연동
- approved 상태 프로세스에 "발주하기" 버튼
- 클릭 시 발주 관리 탭으로 이동 + 자동 선택

### 4. 프린트 기능
- HTML 다운로드
- 브라우저 프린트 기능
- PDF 변환 (선택사항)

## 🔄 개발 완료 시 예상 결과

### 사용자 워크플로우
1. 영업 현황에서 승인된 프로세스 확인
2. "발주하기" 버튼 클릭 → 발주 관리로 이동
3. 내부 재고 or 외주 발주 선택
4. 발주 등록 완료
5. **발주서 프린트** → 공급업체 전달
6. 입고 → 검수 → 출고 완료

### 완성된 기능
- ✅ 견적서 → 영업 프로세스 자동 생성
- ✅ 영업 현황 대시보드  
- ✅ 발주 관리 (고객 주문 + 재고 보충)
- ✅ 재고 관리 (입고/검수/출고)
- ✅ 수익 분석
- 🔲 **발주서 프린트 기능** (개발 예정)
- 🔲 **영업-발주 원클릭 연결** (개발 예정)
- 🔲 **사용자 경험 최적화** (개발 예정)

## 📝 AI 개발자 노트

### 현재 상황
- DB 테이블 모두 정상 존재 확인
- 핵심 비즈니스 로직 완성
- 견적서 HTML 양식 완성 (발주서 변환 가능)
- 모듈 분리 완료로 확장성 확보

### 개발 우선순위
1. **발주서 프린트**: 실무 즉시 필요
2. **영업 연동**: 사용성 대폭 개선
3. **UX 최적화**: 장기적 품질 향상

### 기술적 고려사항
- HTML 템플릿 재사용으로 개발 효율성 극대화
- 기존 모듈 구조 활용으로 안정성 보장
- 소규모 사업장 특성 반영한 단순화된 UI

이 백업을 바탕으로 다음 채팅에서 즉시 개발을 시작할 수 있습니다.