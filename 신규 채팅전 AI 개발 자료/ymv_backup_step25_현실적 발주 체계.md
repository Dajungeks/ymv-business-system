# YMV ERP 시스템 백업 파일 - 현실적 코드별 발주 시스템

## 📊 시스템 현황

### 프로젝트 기본 정보
- **프로젝트명**: YMV 관리 프로그램 (ERP 시스템)
- **개발 언어**: Python + Streamlit
- **데이터베이스**: Supabase (PostgreSQL)
- **회사 규모**: 10인 중소기업
- **현재 진행률**: 모듈 분리 완료 + 현실적 코드별 발주 설계 완료
- **프로젝트 위치**: D:\ymv-business-system

### Supabase 연결 정보
```
SUPABASE_URL = "https://eqplgrbegwzeynnbcuep.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
GitHub: https://github.com/dajungeks/ymv-business-system.git
```

## 🎯 현실적 접근 방식 확정

### 기본 원칙
- **기존 시스템 구조 유지**: quotations_detail, sales_process 그대로 사용
- **최소한의 변경**: 테이블 1개 추가, UI 기능 추가만
- **점진적 개선**: 전면 개편 없이 필요 기능만 추가
- **10인 기업 적합**: 복잡하지 않고 실용적인 해결책

### 현재 작동 중인 시스템 유지
- 견적서 관리 (quotation_management.py) - 변경 없음
- 영업 프로세스 (sales_process_main.py) - 기능 추가만
- 발주 관리 (purchase_order_management.py) - 기능 확장

## 🗄️ 현재 DB 구조 (유지)

### 기존 핵심 테이블들
```sql
-- 견적서 (현재 사용 중)
quotations_detail:
├── id, customer_name, item_name, item_code
├── quantity, unit_price, total_amount
└── status (Approved 시 sales_process 생성)

-- 영업 프로세스 (현재 사용 중)
sales_process:
├── id, process_number, quotation_id
├── customer_name, item_description, quantity
├── unit_price, total_amount, process_status
└── expected_delivery_date

-- 제품 마스터 (재고 확인용)
products:
├── id, product_code, product_name
├── stock_quantity (현재 재고)
└── category, supplier

-- 공급업체 (발주용)
suppliers:
├── id, name, company_name
├── contact_person, email, phone
└── payment_terms, delivery_terms
```

## 🔄 추가할 새로운 기능

### A. 신규 테이블: process_item_breakdown

```sql
CREATE TABLE process_item_breakdown (
    id SERIAL PRIMARY KEY,
    sales_process_id INTEGER REFERENCES sales_process(id),
    
    -- 분할된 코드 정보
    item_code VARCHAR(100) NOT NULL,
    item_description TEXT,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(15,2),
    line_total NUMERIC(15,2),
    
    -- 재고 분석
    current_stock INTEGER DEFAULT 0,
    available_stock INTEGER DEFAULT 0,
    
    -- 처리 방안
    internal_quantity INTEGER DEFAULT 0,
    external_quantity INTEGER DEFAULT 0,
    processing_type VARCHAR(20) CHECK (processing_type IN ('internal', 'external', 'mixed')),
    
    -- 발주 결과 연결
    internal_processing_id INTEGER REFERENCES internal_processing(id),
    external_order_id INTEGER REFERENCES purchase_orders_to_supplier(id),
    
    -- 상태 관리
    item_status VARCHAR(20) DEFAULT 'pending' CHECK (
        item_status IN ('pending', 'stock_checked', 'processed', 'completed')
    ),
    
    -- 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER REFERENCES employees(id)
);

-- 인덱스 추가
CREATE INDEX idx_process_item_breakdown_process_id ON process_item_breakdown(sales_process_id);
CREATE INDEX idx_process_item_breakdown_code ON process_item_breakdown(item_code);
```

### B. 코드별 발주 프로세스

```
영업 프로세스 완료 후:
1. [코드별 발주 분할] 버튼 클릭
2. 코드 입력 화면 표시
3. 각 코드별 재고 확인
4. 처리 방안 결정 (내부/외주/혼합)
5. 개별 발주 실행
```

## 💻 수정할 파일들

### 1. sales_process_main.py (기능 추가)

#### 추가할 함수들

```python
def show_code_breakdown_button(process_id, load_func, save_func, update_func, current_user):
    """코드별 발주 분할 버튼"""
    if st.button(f"📦 코드별 발주 분할", key=f"breakdown_{process_id}"):
        st.session_state[f'show_breakdown_{process_id}'] = True
        st.rerun()
    
    if st.session_state.get(f'show_breakdown_{process_id}', False):
        render_code_breakdown_form(process_id, load_func, save_func, update_func, current_user)

def render_code_breakdown_form(process_id, load_func, save_func, update_func, current_user):
    """코드 분할 입력 폼"""
    st.subheader("📦 코드별 발주 분할")
    
    # 영업 프로세스 정보 조회
    process = get_sales_process_by_id(process_id, load_func)
    
    if not process:
        st.error("영업 프로세스를 찾을 수 없습니다.")
        return
    
    # 기존 분할 내역 확인
    existing_breakdowns = load_func('process_item_breakdown')
    existing_items = [item for item in existing_breakdowns if item.get('sales_process_id') == process_id]
    
    if existing_items:
        render_existing_breakdown(existing_items, load_func, update_func, current_user)
    else:
        render_new_breakdown_form(process, save_func, current_user)

def render_new_breakdown_form(process, save_func, current_user):
    """신규 코드 분할 폼"""
    st.write(f"**영업 프로세스**: {process['process_number']}")
    st.write(f"**고객**: {process['customer_name']}")
    st.write(f"**총 금액**: {process['total_amount']:,} {process.get('currency', 'VND')}")
    
    with st.form("code_breakdown_form"):
        st.write("**코드별 분할 입력**")
        
        # 동적 아이템 추가
        if 'breakdown_items' not in st.session_state:
            st.session_state.breakdown_items = [{'item_code': '', 'quantity': 1, 'description': ''}]
        
        breakdown_items = []
        total_quantity = 0
        
        for i, item in enumerate(st.session_state.breakdown_items):
            col1, col2, col3, col4 = st.columns([3, 2, 3, 1])
            
            with col1:
                item_code = st.text_input(f"상품 코드 {i+1}", 
                                        value=item.get('item_code', ''),
                                        key=f"code_{i}")
            
            with col2:
                quantity = st.number_input(f"수량 {i+1}", 
                                         min_value=1, 
                                         value=item.get('quantity', 1),
                                         key=f"qty_{i}")
            
            with col3:
                description = st.text_input(f"설명 {i+1}",
                                          value=item.get('description', ''),
                                          key=f"desc_{i}")
            
            with col4:
                if st.form_submit_button("🗑️", key=f"del_{i}"):
                    if len(st.session_state.breakdown_items) > 1:
                        st.session_state.breakdown_items.pop(i)
                        st.rerun()
            
            if item_code:
                breakdown_items.append({
                    'item_code': item_code,
                    'quantity': quantity,
                    'description': description
                })
                total_quantity += quantity
        
        # 아이템 추가 버튼
        if st.form_submit_button("➕ 코드 추가"):
            st.session_state.breakdown_items.append({'item_code': '', 'quantity': 1, 'description': ''})
            st.rerun()
        
        # 재고 확인 및 저장
        submitted = st.form_submit_button("✅ 코드별 분할 저장", type="primary")
        
        if submitted:
            if breakdown_items:
                save_breakdown_items(process, breakdown_items, save_func, current_user)
                st.success("코드별 분할이 저장되었습니다!")
                # 세션 상태 초기화
                del st.session_state.breakdown_items
                st.rerun()
            else:
                st.error("최소 하나의 코드를 입력해주세요.")

def save_breakdown_items(process, breakdown_items, save_func, current_user):
    """코드별 분할 저장"""
    for item in breakdown_items:
        # 재고 확인
        stock_info = check_product_stock(item['item_code'], save_func)
        
        breakdown_data = {
            'sales_process_id': process['id'],
            'item_code': item['item_code'],
            'item_description': item['description'],
            'quantity': item['quantity'],
            'unit_price': process['unit_price'],  # 영업 프로세스 단가 사용
            'line_total': item['quantity'] * process['unit_price'],
            'current_stock': stock_info['current_stock'],
            'available_stock': stock_info['available_stock'],
            'item_status': 'stock_checked',
            'created_by': current_user['id'],
            'created_at': datetime.now()
        }
        
        save_func('process_item_breakdown', breakdown_data)

def check_product_stock(product_code, load_func):
    """제품 재고 확인"""
    products = load_func('products')
    product = next((p for p in products if p.get('product_code') == product_code), None)
    
    if product:
        return {
            'current_stock': product.get('stock_quantity', 0),
            'available_stock': product.get('stock_quantity', 0)  # 단순화
        }
    else:
        return {
            'current_stock': 0,
            'available_stock': 0
        }

def render_existing_breakdown(existing_items, load_func, update_func, current_user):
    """기존 분할 내역 표시 및 발주 처리"""
    st.write("**기존 코드별 분할 내역**")
    
    for item in existing_items:
        with st.expander(f"📦 {item['item_code']} - {item.get('item_description', 'N/A')}"):
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                st.write(f"**수량**: {item['quantity']}개")
                st.write(f"**현재 재고**: {item['current_stock']}개")
                st.write(f"**상태**: {item['item_status']}")
            
            with col2:
                # 처리 방안 선택
                available_stock = item['current_stock']
                required_quantity = item['quantity']
                
                if available_stock >= required_quantity:
                    st.info("✅ 내부 재고로 완전 처리 가능")
                    processing_option = st.radio(
                        "처리 방안:",
                        ["내부 재고 처리"],
                        key=f"option_{item['id']}"
                    )
                elif available_stock > 0:
                    st.warning("⚠️ 혼합 처리 필요")
                    st.write(f"내부 가능: {available_stock}개")
                    st.write(f"외주 필요: {required_quantity - available_stock}개")
                    processing_option = st.radio(
                        "처리 방안:",
                        ["혼합 처리", "전체 외주 발주"],
                        key=f"option_{item['id']}"
                    )
                else:
                    st.error("❌ 재고 부족 - 외주 발주 필요")
                    processing_option = st.radio(
                        "처리 방안:",
                        ["외주 발주"],
                        key=f"option_{item['id']}"
                    )
            
            with col3:
                # 발주 처리 버튼
                if item['item_status'] == 'stock_checked':
                    if st.button(f"🚀 발주 처리", key=f"process_{item['id']}"):
                        process_item_order(item, processing_option, update_func, current_user)
                        st.success("발주 처리가 완료되었습니다!")
                        st.rerun()
                else:
                    st.success("✅ 처리 완료")

def process_item_order(item, processing_option, update_func, current_user):
    """개별 아이템 발주 처리"""
    available_stock = item['current_stock']
    required_quantity = item['quantity']
    
    if processing_option == "내부 재고 처리":
        # 내부 처리만
        update_breakdown_status(item['id'], 'processed', 'internal', 
                              required_quantity, 0, update_func)
        
    elif processing_option == "혼합 처리":
        # 내부 + 외주
        internal_qty = min(available_stock, required_quantity)
        external_qty = required_quantity - internal_qty
        update_breakdown_status(item['id'], 'processed', 'mixed', 
                              internal_qty, external_qty, update_func)
        
    elif processing_option == "전체 외주 발주" or processing_option == "외주 발주":
        # 외주만
        update_breakdown_status(item['id'], 'processed', 'external', 
                              0, required_quantity, update_func)

def update_breakdown_status(item_id, status, processing_type, internal_qty, external_qty, update_func):
    """분할 아이템 상태 업데이트"""
    update_data = {
        'item_status': status,
        'processing_type': processing_type,
        'internal_quantity': internal_qty,
        'external_quantity': external_qty,
        'updated_at': datetime.now()
    }
    
    update_func('process_item_breakdown', item_id, update_data)

def get_sales_process_by_id(process_id, load_func):
    """영업 프로세스 ID로 조회"""
    processes = load_func('sales_process')
    return next((p for p in processes if p.get('id') == process_id), None)
```

### 2. sales_process_dashboard.py (표시 기능 추가)

#### 추가할 함수

```python
def show_breakdown_status(processes):
    """코드별 분할 현황 표시"""
    st.subheader("📦 코드별 발주 현황")
    
    # process_item_breakdown 데이터 로드는 load_func 필요
    # 대시보드에서는 간단한 통계만 표시
    
    breakdown_processes = [p for p in processes if p.get('process_status') in ['completed', 'order']]
    
    if breakdown_processes:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("발주 분할 대상", len(breakdown_processes))
        with col2:
            st.metric("분할 완료", "구현 필요")  # 실제로는 breakdown 데이터 확인
        with col3:
            st.metric("발주 처리율", "구현 필요")
    else:
        st.info("코드별 발주 분할 대상이 없습니다.")
```

### 3. purchase_order_management.py (연동 기능 추가)

#### 추가할 탭

```python
def show_breakdown_based_purchase(load_func, save_func, update_func, current_user):
    """코드별 분할 기반 발주"""
    st.subheader("📦 코드별 분할 발주")
    
    # 분할된 아이템 중 외주 발주 대상 조회
    breakdowns = load_func('process_item_breakdown')
    external_items = [
        item for item in breakdowns 
        if item.get('processing_type') in ['external', 'mixed'] 
        and item.get('external_quantity', 0) > 0
        and item.get('external_order_id') is None  # 아직 발주되지 않은 것
    ]
    
    if not external_items:
        st.info("외주 발주 대상인 분할 아이템이 없습니다.")
        return
    
    st.write(f"📋 외주 발주 대상: {len(external_items)}건")
    
    for item in external_items:
        with st.expander(f"🏭 {item['item_code']} - 외주 {item['external_quantity']}개"):
            render_breakdown_external_order_form(item, save_func, update_func, current_user)

def render_breakdown_external_order_form(item, save_func, update_func, current_user):
    """분할 아이템 외주 발주 폼"""
    with st.form(f"external_order_{item['id']}"):
        st.write(f"**상품 코드**: {item['item_code']}")
        st.write(f"**발주 수량**: {item['external_quantity']}개")
        
        # 공급업체 선택 (suppliers 테이블에서)
        suppliers = load_func('suppliers')
        supplier_options = {f"{s['name']} ({s['company_name']})": s for s in suppliers}
        
        selected_supplier_key = st.selectbox(
            "공급업체 선택:",
            list(supplier_options.keys()),
            key=f"supplier_{item['id']}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            order_date = st.date_input("발주일", value=date.today())
            expected_arrival = st.date_input("예상 도착일", value=date.today() + timedelta(days=7))
        
        with col2:
            unit_cost = st.number_input("단가 (USD)", min_value=0.0, format="%.2f")
            total_cost = unit_cost * item['external_quantity']
            st.write(f"**총 금액**: ${total_cost:.2f}")
        
        payment_terms = st.text_input("결제 조건", value="30일 후 지급")
        notes = st.text_area("비고")
        
        submitted = st.form_submit_button("📤 외주 발주 등록")
        
        if submitted and selected_supplier_key and unit_cost > 0:
            supplier = supplier_options[selected_supplier_key]
            create_breakdown_external_order(item, supplier, order_date, expected_arrival, 
                                          unit_cost, total_cost, payment_terms, notes, 
                                          save_func, update_func, current_user)

def create_breakdown_external_order(item, supplier, order_date, expected_arrival, 
                                   unit_cost, total_cost, payment_terms, notes, 
                                   save_func, update_func, current_user):
    """분할 아이템 외주 발주 생성"""
    # 발주서 번호 생성
    po_number = generate_document_number('POB', save_func)  # Purchase Order Breakdown
    
    order_data = {
        'po_number': po_number,
        'sales_process_id': item['sales_process_id'],
        'supplier_name': supplier['name'],
        'supplier_contact': supplier.get('contact_person'),
        'supplier_email': supplier.get('email'),
        'supplier_phone': supplier.get('phone'),
        'item_description': f"{item['item_code']} - {item.get('item_description', '')}",
        'quantity': item['external_quantity'],
        'unit_cost': unit_cost,
        'total_cost': total_cost,
        'order_date': order_date,
        'expected_arrival_date': expected_arrival,
        'payment_terms': payment_terms,
        'status': 'ordered',
        'notes': f"코드별 분할 발주 - {notes}",
        'created_at': datetime.now(),
        'created_by': current_user['id']
    }
    
    # 발주서 저장
    result = save_func('purchase_orders_to_supplier', order_data)
    
    if result:
        # breakdown 아이템에 발주서 ID 연결
        update_func('process_item_breakdown', item['id'], {
            'external_order_id': result.get('id'),
            'item_status': 'completed',
            'updated_at': datetime.now()
        })
        
        st.success(f"✅ 발주서 {po_number}가 등록되었습니다!")
    else:
        st.error("발주서 등록에 실패했습니다.")
```

## 🚀 구현 순서

### 1단계: DB 테이블 생성 (30분)
```sql
-- process_item_breakdown 테이블 생성
-- 인덱스 추가
```

### 2단계: sales_process_main.py 수정 (2시간)
- 코드별 분할 버튼 추가
- 분할 입력 폼 구현
- 재고 확인 로직 구현
- 발주 처리 로직 구현

### 3단계: purchase_order_management.py 연동 (1시간)
- 분할 기반 발주 탭 추가
- 외주 발주 폼 구현

### 4단계: 테스트 및 디버깅 (1시간)

**총 예상 시간: 4-5시간**

## 🎯 사용자 시나리오

### 실제 사용 흐름
```
1. 영업 프로세스 완료 (기존과 동일)
   - 견적서 작성 → 승인 → sales_process 생성

2. 코드별 발주 분할 (신규 기능)
   - [코드별 발주 분할] 버튼 클릭
   - HR-ST-OP-16 (5개), HR-HT-12 (3개) 입력
   - 재고 자동 확인: HR-ST-OP-16 재고 2개, HR-HT-12 재고 0개

3. 처리 방안 자동 제안
   - HR-ST-OP-16: 내부 2개, 외주 3개 (혼합 처리)
   - HR-HT-12: 외주 3개 (외주 발주)

4. 개별 발주 실행
   - 외주 발주 대상 자동 연동
   - 공급업체 선택 후 발주서 생성
```

## 📋 함수 호출 관계도

```
sales_process_main.py:
├── show_sales_process_management()
│   ├── 기존 탭들 (영업 현황, 발주 관리, 재고 관리, 수익 분석)
│   └── 영업 현황 탭에서:
│       └── show_code_breakdown_button() ← 신규 추가
│           ├── render_code_breakdown_form()
│           │   ├── render_new_breakdown_form()
│           │   │   └── save_breakdown_items()
│           │   └── render_existing_breakdown()
│           │       └── process_item_order()
│           └── check_product_stock()

purchase_order_management.py:
├── show_purchase_order_management()
│   ├── 기존 탭들 (고객 주문 발주, 재고 보충 발주, 내부 처리)
│   └── 신규 탭: show_breakdown_based_purchase() ← 신규 추가
│       └── render_breakdown_external_order_form()
│           └── create_breakdown_external_order()
```

## 🔄 데이터 흐름

```
영업 프로세스 (기존) → 코드별 분할 (신규) → 발주 처리 (확장)

sales_process
    ↓ (코드 분할)
process_item_breakdown
    ↓ (외주 발주)
purchase_orders_to_supplier
    ↓ (재고 처리)
internal_processing
```

## 🛠️ 필요한 import 추가

```python
# sales_process_main.py 상단에 추가
from datetime import datetime, date, timedelta
import streamlit as st

# purchase_order_management.py 상단에 추가  
from datetime import datetime, date, timedelta
```

## 📌 재개 방법

### 필수 업로드 파일
1. **규칙 V10 파일**: `program_development_rules - V10 Final.txt`
2. **이 백업 파일**: `ymv_backup_realistic_code_breakdown.md`

### 재개 명령어
```
"규칙 V10 + 이 백업 기준으로 코드별 발주 시스템 개발 시작해줘"
```

### 즉시 시작 가능한 상태
- DB 테이블 생성 SQL 준비됨
- 모든 함수 코드 설계 완료
- 구현 순서 및 시간 계획 수립
- 기존 파일 수정 범위 명확화

## 🎯 기대 효과

### 비즈니스 개선
- 영업 프로세스 완료 후 즉시 코드별 발주 가능
- 재고 확인 자동화로 정확한 발주 결정
- 내부 재고 우선 사용으로 비용 절감
- 발주 추적 및 관리 체계화

### 시스템 개선
- 기존 시스템 안정성 유지
- 최소한의 변경으로 최대 효과
- 10인 기업에 적합한 실용적 솔루션
- 향후 확장 가능한 구조

이 백업 시점에서 YMV ERP 시스템은 현실적이고 실용적인 코드별 발주 시스템 구현 준비가 완료되었습니다.