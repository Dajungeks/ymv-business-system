# YMV ERP 시스템 완전 개발 문서 - v18 완성 + 고객 관리 추가

## 🎯 현재 상황
- **견적서 관리 시스템**: Step 18-4 완전 완성 (6개 컴포넌트 모두 동작)
- **고객 관리 시스템**: 새로 완성 (4개 컴포넌트 완성)
- **현재 상태**: 두 시스템 모두 코드 완성, main.py 통합 대기
- **다음 작업**: main.py에 고객 관리 추가 및 통합 테스트

---

## 📊 완성된 시스템 현황

### ✅ 견적서 관리 시스템 (100% 완성)
```
app/components/quotation/
├── quotation_utils.py         ✅ 완성 (호환성 문제 해결)
├── quotation_form.py          ✅ 완성 (폼 리셋, 복사 모드)
├── quotation_list.py          ✅ 완성 (페이지네이션, 필터링)
├── quotation_edit.py          ✅ 완성 (자동 로드, 모드별 처리)
├── quotation_print.py         ✅ 완성 (3개국어, HTML 템플릿)
├── quotation_status.py        ✅ 동작 (format_currency 문제 해결)
└── quotation_management.py    ✅ 완성 (메인 통합, 오류 처리)
```

### ✅ 고객 관리 시스템 (100% 완성)
```
app/components/customer/
├── customer_utils.py          ✅ 새로 완성
├── customer_form.py           ✅ 새로 완성 (KAM 정보 포함)
├── customer_list.py           ✅ 새로 완성 (검색, 필터, 페이지네이션)
└── customer_management.py     ✅ 새로 완성 (메인 통합)
```

---

## 🗄️ 데이터베이스 스키마

### 견적서 테이블 (quotations) - 기존 유지
```sql
quotations (
    id, customer_id, sales_rep_id, quote_number, revision_number,
    quote_date, valid_until, item_code, item_name_en, item_name_vn,
    quantity, unit_price, discount_rate, discounted_price, 
    total_amount, currency, vat_rate, vat_amount, final_amount,
    project_name, part_name, mold_number, part_weight, hrs_info,
    resin_type, resin_additive, sol_material, payment_terms,
    delivery_date, lead_time_days, remarks, status,
    created_at, updated_at, cost_price_usd, margin_rate, exchange_rate
)
```

### 고객 테이블 (customers) - KAM 정보 추가
```sql
customers (
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
    -- KAM 정보 추가
    kam_name            varchar(255),
    kam_phone           varchar(50),
    kam_position        varchar(100),
    kam_notes           text,
    status              varchar(50) DEFAULT 'Active',
    notes               text,
    created_at          timestamp DEFAULT NOW(),
    updated_at          timestamp DEFAULT NOW()
)
```

---

## 🔧 해결된 주요 오류들

### Step 18-4에서 해결된 문제들
1. **Session State 키 충돌**: 모든 키에 고유 접두사 추가
2. **함수 매개변수 불일치**: load_customers(load_func=None) 호환성 처리
3. **이모지 문법 오류**: 모든 이모지 문자를 텍스트로 변경
4. **format_currency 임포트 오류**: quotation_utils.py에 함수 추가
5. **HTML 템플릿 불일치**: 완전 일치하는 템플릿으로 교체

### 견적서 시스템 현재 동작 상태
- ✅ 견적서 작성: 폼 리셋, 실시간 계산, 복사 모드
- ✅ 견적서 목록: 페이지네이션, 필터링, 일괄 작업
- ✅ 견적서 수정: 자동 로드, 3가지 모드 (리비전/직접/복사)
- ✅ 견적서 인쇄: 3개국어, HTML 다운로드, 인쇄 최적화
- ⚠️ 견적서 상태: 동작하지만 경고 메시지 (기능상 문제없음)

---

## 🏗️ 컴포넌트 아키텍처

### 견적서 관리 함수 호출 구조
```python
# main.py에서 호출
show_quotation_management(load_func, save_func, update_func, delete_func)

# quotation_management.py에서 각 컴포넌트 호출
├── render_quotation_form(save_func, load_func)           # 작성
├── render_quotation_list(load_func, update_func, delete_func)  # 목록
├── render_quotation_status_management(load_func, update_func, save_func)  # 상태
├── render_quotation_edit(load_func, update_func, save_func)     # 수정
└── render_quotation_print(load_func)                    # 인쇄
```

### 고객 관리 함수 호출 구조
```python
# main.py에서 호출 (추가 필요)
show_customer_management(load_func, save_func, update_func, delete_func)

# customer_management.py에서 각 컴포넌트 호출
├── render_customer_form(save_func, load_func)           # 등록
├── render_customer_list(load_func, update_func, delete_func)   # 목록
├── render_customer_details(load_func, update_func)     # 상세
├── render_customer_quotation_history(load_func)        # 견적서 이력
└── render_customer_system_info(load_func)              # 시스템 정보
```

---

## 🔍 주요 함수 목록

### quotation_utils.py 핵심 함수들
```python
# 데이터 로드 (호환성 지원)
- load_customers(load_func=None)
- load_employees(load_func=None) 
- load_products(load_func=None)

# 견적서 관리
- generate_quote_number()              # YMV-Q240928-XXX-Rv00
- generate_revision_number(base_number)
- validate_quotation_data(data)        # 새 형식 반환
- prepare_quotation_data(form_data)
- calculate_pricing(quantity, unit_price)  # 간단 버전

# 상태 관리
- get_status_color(status)
- update_quotation_status(id, status, update_func)
- create_sales_process_from_quotation(quotation, save_func, load_func)

# 유틸리티
- get_customer_by_id(id, df)
- get_employee_by_id(id, df)
- reset_quotation_form()
- format_currency(amount, currency)    # 새로 추가
```

### customer_utils.py 핵심 함수들
```python
# 데이터 로드
- load_customers(load_func=None)
- load_employees(load_func=None)

# 고객 관리
- validate_customer_data(data)         # 이메일, 전화번호 검증
- prepare_customer_data(form_data)
- get_customer_by_id(id, df)
- get_customer_quotations(customer_id, load_func)
- calculate_customer_statistics(customer_id, load_func)

# 검색 및 필터링
- search_customers(df, search_term)
- filter_customers_by_status(df, status)
- filter_customers_by_country(df, country)

# 유틸리티
- validate_email(email)
- validate_phone(phone)
- get_customer_display_name(customer)
- format_customer_info(customer)
- reset_customer_form()
- export_customers_to_csv(df)
```

---

## 🎨 주요 기능 특징

### 견적서 관리 시스템
1. **견적서 작성**: 
   - 실시간 가격 계산 (관리비 20% 포함)
   - 제품 자동 연동 (product_codes 조인)
   - 복사 모드 지원
   - 폼 자동 리셋

2. **견적서 목록**:
   - 페이지네이션 (10/20/50/100개)
   - 다중 필터 (상태/고객/담당자/검색어)
   - 일괄 상태 변경
   - 실시간 통계

3. **견적서 수정**:
   - 3가지 모드: 새 리비전/직접 수정/복사
   - 기존 데이터 자동 로드
   - 실시간 가격 재계산

4. **견적서 인쇄**:
   - 3개국어 지원 (한국어/English/Tiếng Việt)
   - HTML 다운로드
   - 인쇄 최적화 CSS
   - 로고/약관 옵션

### 고객 관리 시스템
1. **고객 등록**:
   - 기본 정보 (회사, 업종, 국가)
   - 담당자 정보 (이메일, 전화번호 검증)
   - KAM 정보 (이름, 전화, 직책, 노트)
   - 담당 직원 배정
   - 미리보기 기능

2. **고객 목록**:
   - 검색 (회사명/담당자/이메일)
   - 다중 필터 (상태/국가/정렬)
   - 페이지네이션
   - CSV 내보내기
   - 상태 변경 (Active/Inactive)

3. **고객 상세**:
   - 전체 정보 조회
   - KAM 정보 표시
   - 견적서 이력 연결

4. **견적서 이력**:
   - 고객별 견적서 목록
   - 통계 (총액, 승인율)
   - 상태별 분류

---

## ⚙️ 시스템 통합 상태

### 현재 main.py 구조
```python
# 기존 메뉴들
- 대시보드 ✅
- 직원 관리 ✅
- 제품 관리 ✅
- 공급업체 관리 ✅
- 견적서 관리 ✅ (Step 18-4 완성)
- 영업프로세스 관리 ✅
- 지출 관리 ✅
- 코드 관리 ✅

# 추가 필요
- 고객 관리 ❌ (코드 완성, main.py 추가 대기)
```

### main.py에 추가할 코드
```python
# import 추가
from components.customer_management import show_customer_management

# 사이드바 메뉴에 추가 (견적서 관리 다음에)
elif page == "고객 관리":
    show_customer_management(
        db_ops.load_data, 
        db_ops.save_data, 
        db_ops.update_data, 
        db_ops.delete_data
    )
```

---

## 🔧 오류 기록 및 해결 방법

### 발생했던 주요 오류들
1. **SyntaxError: invalid character '⚠'**: 이모지 문자 사용 금지
2. **load_customers() takes 0 positional arguments**: 함수 시그니처 불일치
3. **cannot import name 'format_currency'**: 누락된 함수 추가
4. **Session State 키 충돌**: 고유 접두사 사용
5. **HTML 템플릿 불일치**: 완전 일치하는 템플릿 필요

### 해결 패턴
- 모든 함수에 매개변수 기본값 설정: `load_func=None`
- 세션 상태 키에 컴포넌트별 접두사: `quotation_`, `customer_`
- 이모지 대신 텍스트 사용
- 임포트 오류 시 try-except로 안전 처리

---

## 📋 다음 단계 계획

### 즉시 진행할 작업 (다음 채팅)
1. **main.py 수정**: 고객 관리 메뉴 추가
2. **통합 테스트**: 견적서↔고객 연동 확인
3. **데이터 흐름 검증**: 견적서 작성 시 고객 선택 정상 동작 확인
4. **UI/UX 개선**: 메뉴 순서, 네비게이션 최적화

### 추가 개발 계획
1. **고객 수정 기능**: customer_edit.py 구현
2. **고급 통계**: 고객별 매출 분석, 트렌드
3. **데이터 동기화**: 견적서↔고객 정보 실시간 업데이트
4. **권한 관리**: 사용자별 고객 접근 제한
5. **알림 시스템**: 고객 활동 알림

---

## 🧪 테스트 체크리스트

### 견적서 관리 테스트 (완료)
- ✅ 견적서 작성: 제품 선택, 가격 계산, 저장
- ✅ 견적서 목록: 필터링, 페이지네이션, 상태 변경