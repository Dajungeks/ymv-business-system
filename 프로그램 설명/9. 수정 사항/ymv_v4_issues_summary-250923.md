# YMV Business System v4.0 - 발견된 문제점 및 해결방안 정리

## 📋 프로젝트 현재 상태

**프로젝트**: YMV 관리 프로그램 v4.0  
**위치**: D:\ymv-business-system  
**데이터베이스**: Supabase PostgreSQL  
**개발 단계**: Step 1 (DB 업그레이드) 완료, 로컬 테스트 중  
**주요 문제**: 데이터베이스 스키마와 애플리케이션 코드 간 불일치

---

## 🚨 발견된 주요 문제들

### 1. 데이터베이스 스키마 불일치 문제

#### A) 지출 요청서 (expenses 테이블)
```
오류: Could not find the 'purpose' column of 'expenses'
```
**문제**: `purpose` 컬럼이 데이터베이스에 없음  
**원인**: Step 1 스키마 업그레이드 시 누락되었거나 컬럼명이 다름

#### B) 고객 관리 (customers 테이블)
```
오류: Could not find the 'business_type' column of 'customers'
```
**문제**: `business_type` 컬럼이 데이터베이스에 없음

#### C) 회사 정보 (company_info 테이블)
```
오류: Could not find the 'business_number' column of 'company_info'
```
**문제**: `business_number` 컬럼이 데이터베이스에 없음

### 2. 제품 관리 관련 문제

#### A) products_multilingual 뷰 문제
```
오류: Could not find the table 'public.products_multilingual'
```
**문제**: Step 1에서 생성된 뷰가 정상 작동하지 않음

#### B) 제품 코드 연동 문제
**현재 상황**: 코드 관리와 제품 등록 간 연동 안됨  
**요구사항**: 카테고리 선택 → 해당 카테고리 코드들 드롭다운 표시

### 3. 견적서 관리 문제

#### A) 제품 선택 로직 수정 필요
**현재**: 언어 선택 → 제품 선택  
**요구사항**: 카테고리 선택 → 코드 선택 → 자동 단가 + 다국어명 표시

#### B) Widget 중복 오류
```
오류: DuplicateWidgetID: key='quotation_selector'
```
**해결 상태**: 수정 방법 제시됨

### 4. CRUD 기능 문제

#### A) 고객 목록 수정 기능
**문제**: 수정 버튼 작동하지 않음

#### B) 직원 관리 수정 기능  
**문제**: 수정 기능 작동하지 않음

#### C) 환율 관리 개선 필요
**요구사항**: 
- 1 USD 기준 다른 통화 환율 계산
- 엑셀 형태 표 표시
- 수정/삭제 기능 재검토

---

## 🔧 해결 방안

### 단계 1: 데이터베이스 스키마 점검 및 수정

#### A) 현재 테이블 구조 확인
Supabase에서 다음 테이블들의 실제 컬럼 확인 필요:
- `expenses` (purpose 컬럼 확인)
- `customers` (business_type 컬럼 확인)  
- `company_info` (business_number 컬럼 확인)

#### B) 누락된 컬럼 추가
```sql
-- expenses 테이블 수정
ALTER TABLE expenses ADD COLUMN IF NOT EXISTS purpose TEXT;

-- customers 테이블 수정  
ALTER TABLE customers ADD COLUMN IF NOT EXISTS business_type VARCHAR(100);

-- company_info 테이블 수정
ALTER TABLE company_info ADD COLUMN IF NOT EXISTS business_number VARCHAR(50);
```

#### C) 뷰 재생성
```sql
-- products_multilingual 뷰 재생성
DROP VIEW IF EXISTS products_multilingual;
CREATE VIEW products_multilingual AS
SELECT 
    p.*,
    pc.description as category_description,
    pc.full_code as category_code
FROM products p
LEFT JOIN product_codes pc ON p.code_category = pc.category;
```

### 단계 2: 제품 관리 로직 수정

#### A) 제품 등록 폼 개선
```python
# 카테고리 선택 → 사용 가능한 코드 드롭다운
def get_available_codes_for_category(category):
    used_codes = [p['product_code'] for p in load_data_from_supabase('products')]
    base_code = get_base_code_for_category(category)
    available_codes = []
    for i in range(100):
        code = f"{base_code}{i:02d}"
        if code not in used_codes:
            available_codes.append(code)
    return available_codes
```

#### B) 제품-코드 연동 강화
- 코드 선택 시 자동 카테고리 설정
- 코드 형식 검증 로직 추가

### 단계 3: 견적서 로직 재설계

#### A) 제품 선택 프로세스 단순화
```
1. 카테고리 선택
2. 해당 카테고리의 등록된 제품 코드 선택
3. 자동으로 영어명/베트남어명/단가 표시
4. 수량 입력 → 총액 계산
```

#### B) Widget 키 충돌 해결
```python
# 고유한 키 생성
key=f"{key_prefix}_selector_{language}_{timestamp}"
```

### 단계 4: CRUD 기능 표준화

#### A) 수정 기능 통일
```python
def render_edit_form(item_type, item_data, item_id):
    # 표준화된 수정 폼 렌더링
    # 성공 시 st.rerun() 호출
    pass
```

#### B) 삭제 확인 모달 추가
```python
def confirm_delete(item_type, item_id):
    if st.button(f"정말 삭제하시겠습니까?"):
        delete_data_from_supabase(item_type, item_id)
        st.success("삭제되었습니다.")
        st.rerun()
```

### 단계 5: 환율 관리 고도화

#### A) 환율 계산 로직
```python
def calculate_exchange_rates(base_currency="USD"):
    # 1 USD 기준으로 모든 환율 계산
    rates = load_data_from_supabase('exchange_rates')
    calculated_rates = {}
    for rate in rates:
        if rate['from_currency'] == base_currency:
            calculated_rates[rate['to_currency']] = rate['exchange_rate']
    return calculated_rates
```

#### B) 환율 표 UI
```python
def render_exchange_rate_table():
    rates = calculate_exchange_rates()
    df = pd.DataFrame(rates.items(), columns=['통화', '환율'])
    st.dataframe(df, use_container_width=True)
```

---

## 📋 우선순위별 작업 계획

### 🔴 높음 (시스템 정상화)
1. **데이터베이스 스키마 수정** (누락된 컬럼 추가)
2. **products_multilingual 뷰 재생성**
3. **Widget 중복 오류 수정**

### 🟡 중간 (핵심 기능)
4. **제품 코드 연동 로직 구현**
5. **견적서 제품 선택 프로세스 재설계**
6. **CRUD 수정 기능 복구**

### 🟢 낮음 (개선사항)
7. **환율 관리 고도화**
8. **UI/UX 개선**
9. **성능 최적화**

---

## 🔍 다음 단계 진행 방법

### 1. 새 채팅창에서 계속하기
다음 채팅창에서 이 파일과 함께 다음과 같이 시작:

```
"YMV v4.0 문제 해결을 계속 진행합니다. 
첨부한 문제점 정리 파일을 확인해주세요.
우선순위 높음 항목부터 해결하겠습니다."
```

### 2. 단계별 해결
- **1단계**: 데이터베이스 스키마 수정 (SQL 실행)
- **2단계**: 뷰 재생성 및 확인
- **3단계**: 애플리케이션 코드 수정

### 3. 테스트 및 검증
- 각 단계 완료 후 즉시 테스트
- 문제 발생 시 즉시 롤백 및 재수정

---

## 📊 현재 상태 요약

### ✅ 완료된 작업
- Step 1: 데이터베이스 기본 구조 생성
- 컴포넌트 파일 생성 (code_management.py, multilingual_input.py)
- 메인 애플리케이션 v4.0 코드 적용

### 🔄 진행 중 작업
- 로컬 테스트 및 오류 수정
- 데이터베이스 스키마 정합성 확보

### ❌ 해결 필요 사항
- 데이터베이스 컬럼 누락 문제 (4개)
- 제품 관리 연동 로직 (2개)
- CRUD 수정 기능 (2개)
- Widget 중복 오류 (1개)

---

## 📝 참고 정보

### 프로젝트 구조
```
D:\ymv-business-system\
├── app\
│   ├── main.py (v4.0 업그레이드 완료)
│   └── components\
│       ├── code_management.py
│       └── multilingual_input.py
├── .streamlit\
│   └── secrets.toml (로컬 설정 완료)
└── 기타 파일들...
```

### 데이터베이스 정보
- **URL**: https://eqplgrbegwzeynnbcuep.supabase.co
- **상태**: 연결 성공
- **문제**: 일부 테이블 스키마 불일치

### 개발 환경
- **Python**: 3.10
- **Streamlit**: 최신 버전
- **로컬 테스트**: http://localhost:8501

---

**마지막 업데이트**: 2025-09-23  
**다음 작업**: 데이터베이스 스키마 수정부터 시작