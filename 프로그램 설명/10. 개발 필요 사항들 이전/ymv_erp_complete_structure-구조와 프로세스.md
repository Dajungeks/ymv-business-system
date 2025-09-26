# YMV ERP 전체 업무 프로세스 맵

## 1. 전체 시스템 구조도

```
[직원 관리] ──┐
              │
[제품 코드] ───┼─── [견적서 관리] ──┐
              │                    │
[고객 관리] ───┤                    ├─── [주문 관리] ──┐
              │                    │                  │
[제품 관리] ───┘                    └─── [발주 관리] ──┤
                                                      │
[구매 관리] ──────────────────────────────────────────┤
                                                      │
[재고 관리] ──────────────────────────────────────────┤
                                                      │
[지출 관리] ──────────────────────────────────────────┘
```

## 2. 핵심 업무 프로세스 시나리오

### 시나리오 A: 영업 프로세스 (견적서 → 수주 → 납품)

#### Step 1: 사전 준비 작업
```
1. 제품 코드 생성 [시스템 관리 > 제품 코드 관리]
   - HR-01-02-ST-KR-00 형태로 생성
   - 7단계 체계적 분류

2. 제품 정보 등록 [제품 관리]
   - 제품 코드 연결
   - 다국어 제품명 (영어/베트남어)
   - 단가, 규격, 설명 등

3. 고객 정보 등록 [고객 관리]
   - 회사명, 담당자, 연락처
   - 거래 조건, 결제 방식
```

#### Step 2: 견적서 작성 프로세스
```
[견적서 관리] 접속
    ↓
기본 정보 입력:
- 고객 선택 (customers 테이블 로딩)
- 견적 유효일 설정
- 견적 제목, 통화 선택
    ↓
제품 추가:
- products 테이블에서 제품 선택 (제품 코드 포함)
- 수량, 단가 입력
- 자동 금액 계산
    ↓
추가 정보:
- 거래 조건, 참고사항 입력
- 회사 정보 자동 로딩 (company_info)
    ↓
견적서 저장:
- quotations 테이블에 마스터 정보
- quotation_items 테이블에 상세 항목
- 자동 견적번호 생성 (YMV-Q-2024-XXXX)
    ↓
견적서 출력 및 발송:
- 다국어 양식으로 출력
- 상태: 작성중 → 발송됨
```

#### Step 3: 수주 후 처리
```
고객 승인 시:
- 견적서 상태: 발송됨 → 승인됨
    ↓
주문서 생성: [주문 관리]
- orders 테이블 생성
- 견적서 정보 복사
- 주문번호 자동 생성
- 납기일, 배송지 추가 입력
    ↓
발주 필요성 판단:
- 재고 확인 (inventory 테이블)
- 부족 시 → 발주 프로세스 진행
```

### 시나리오 B: 구매/발주 프로세스

#### Step 1: 발주 계획
```
[구매 관리] 또는 [발주 관리] 접속
    ↓
발주 사유 선택:
- 고객 주문용 (주문서 연결)
- 재고 보충용
- 사무용품 등
    ↓
제품 선택:
- products 테이블에서 선택
- 제품 코드로 정확한 식별
- 필요 수량 입력
    ↓
공급업체 선택:
- suppliers 테이블 (추가 필요)
- 거래 조건, 납기 확인
```

#### Step 2: 발주서 작성 및 처리
```
발주서 정보 입력:
- 발주번호 자동 생성 (YMV-P-2024-XXXX)
- 납기일, 배송지
- 결제 조건
    ↓
발주서 저장 및 출력:
- purchase_orders 테이블 (추가 필요)
- 승인 프로세스 (금액별 권한)
    ↓
공급업체 전송:
- 이메일/팩스 발송
- 상태: 발주 → 발송됨
```

#### Step 3: 입고 처리
```
물품 입고 시:
- 발주서 상태: 발송됨 → 입고됨
- 입고 수량 확인
    ↓
재고 등록: [재고 관리]
- inventory 테이블에 입고 기록
- 재고 수량 업데이트
- 입고일, 담당자 기록
    ↓
품질 검사:
- 합격 시: 판매 가능 재고
- 불합격 시: 반품 처리
```

### 시나리오 C: 지출 관리 프로세스

#### Step 1: 지출 요청
```
[지출 관리] 접속
    ↓
지출 요청서 작성:
- 지출 유형 선택 (출장비, 사무용품 등)
- 금액, 사용 목적
- 거래처, 결제 방법
- 직원 정보 자동 로딩 (employees)
    ↓
상태: 대기중
```

#### Step 2: 승인 프로세스
```
일반 지출 (< $1000):
- 상태: 대기중 → 승인됨
    ↓
고액 지출 (≥ $1000):
- 상태: 대기중 → CEO승인대기
- CEO 승인 후 → 승인됨
    ↓
지급 처리:
- 상태: 승인됨 → 지급완료
- 실제 지급 후 → 인보이스확인완료
```

## 3. 데이터 연결 관계도

### 3.1 핵심 마스터 데이터
```
employees (직원 정보)
    ├── 모든 문서의 작성자/승인자 정보
    └── 권한별 메뉴 접근 제어

product_codes (제품 코드)
    ├── products (제품 정보)
    ├── quotation_items (견적 항목)
    ├── order_items (주문 항목)
    └── inventory (재고 관리)

customers (고객 정보)
    ├── quotations (견적서)
    ├── orders (주문서)
    └── invoices (인보이스)

company_info (회사 정보)
    ├── 모든 공식 문서의 회사 정보
    └── 견적서, 주문서, 인보이스 헤더
```

### 3.2 트랜잭션 데이터 흐름
```
견적서 (quotations + quotation_items)
    ↓ [승인시]
주문서 (orders + order_items)
    ↓ [발주 필요시]
발주서 (purchase_orders + purchase_items)
    ↓ [입고시]
재고 (inventory)
    ↓ [출고시]
출고서 (deliveries + delivery_items)
    ↓ [완료시]
인보이스 (invoices + invoice_items)
```

## 4. 각 페이지별 필요 정보 로딩

### 4.1 견적서 페이지
```python
# 기본 데이터 로딩
customers = load_data_from_supabase('customers')
products = load_data_from_supabase('products') 
product_codes = load_data_from_supabase('product_codes')
company_info = load_data_from_supabase('company_info')
current_user = get_current_user() # employees 테이블

# 제품 선택 시
product_with_code = join_product_code_info(product_id)
multilingual_names = get_product_multilingual(product_id)
```

### 4.2 발주서 페이지
```python
# 기본 데이터 로딩
suppliers = load_data_from_supabase('suppliers')
products = load_data_from_supabase('products')
product_codes = load_data_from_supabase('product_codes')
purchase_categories = load_data_from_supabase('purchase_categories')
current_user = get_current_user()

# 연결된 주문 정보 (해당시)
related_orders = load_related_orders(order_id)
```

### 4.3 재고 관리 페이지
```python
# 기본 데이터 로딩
inventory = load_data_from_supabase('inventory')
products = load_data_from_supabase('products')
product_codes = load_data_from_supabase('product_codes')
purchase_orders = load_data_from_supabase('purchase_orders')

# 입출고 이력
inventory_transactions = load_inventory_history()
```

## 5. 권한별 메뉴 접근 제어

### 5.1 메뉴 표시 로직
```python
def get_available_menus(user_id):
    permissions = load_user_permissions(user_id)
    available_menus = []
    
    menu_permission_map = {
        '대시보드': 'dashboard_read',
        '견적서 관리': 'quotation_read',
        '주문 관리': 'order_read',
        '발주 관리': 'purchase_read',
        '재고 관리': 'inventory_read',
        '지출 관리': 'expense_read',
        '고객 관리': 'customer_read',
        '제품 관리': 'product_read',
        '직원 관리': 'employee_read'
    }
    
    for menu, required_permission in menu_permission_map.items():
        if has_permission(permissions, required_permission):
            available_menus.append(menu)
    
    return available_menus
```

### 5.2 기능별 권한 체크
```python
def check_action_permission(user_id, module, action):
    # action: 'create', 'read', 'update', 'delete', 'approve'
    permissions = load_user_permissions(user_id)
    return has_action_permission(permissions, module, action)

# 사용 예시
if not check_action_permission(user_id, 'quotation', 'create'):
    st.error("견적서 작성 권한이 없습니다.")
    return
```

## 6. 업무 진행도 및 개발 우선순위

### 6.1 현재 완성도
- 직원 관리: 30% (로그인만 구현, 권한 시스템 미구현)
- 지출 관리: 100% (완전 구현)
- 견적서 관리: 90% (테스트 필요)
- 구매품 관리: 70% (기본 CRUD만)
- 제품 코드: 80% (관리 기능만, 연결 미완성)
- 고객/제품 관리: 0%
- 주문/발주/재고: 0%

### 6.2 개발 순서 제안
```
Phase 1: 기반 완성
1. 직원 권한 시스템 구축
2. 고객 관리 완성
3. 제품 관리 완성
4. 제품 코드 연결 완성

Phase 2: 영업 프로세스
5. 견적서 시스템 완성
6. 주문 관리 구축
7. 인보이스 시스템

Phase 3: 구매 프로세스
8. 공급업체 관리
9. 발주 시스템 구축
10. 재고 관리 시스템

Phase 4: 통합 및 최적화
11. 프로세스 연결 완성
12. 리포팅 시스템
13. 권한 시스템 고도화
```

## 7. 필요한 추가 테이블

### 7.1 영업 관련
```sql
orders, order_items, invoices, invoice_items
suppliers, purchase_orders, purchase_items
inventory_transactions, deliveries, delivery_items
```

### 7.2 시스템 관리
```sql
user_roles, role_permissions, system_logs
document_sequences, approval_workflows
```

이 구조를 바탕으로 단계적으로 개발을 진행하면 완전한 ERP 시스템을 구축할 수 있습니다.