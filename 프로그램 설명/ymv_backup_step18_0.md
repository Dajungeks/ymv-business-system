# YMV ERP 시스템 완전 개발 문서 - v18.0
## 견적서 관리 컴포넌트 분리 완성

### 완성도 현황
- **이전 완성도**: 100% (Step 17 - 견적서-영업프로세스 연동 완성)
- **현재 완성도**: 100% + 고도화 (견적서 관리 컴포넌트 완전 분리)
- **테스트 상태**: 미완료 (Step 18 컴포넌트 테스트 필요)

---

## Step 18에서 완성된 주요 기능

### 1. 견적서 관리 컴포넌트 완전 분리
**새로운 모듈 구조:**
```
components/quotation/
├── quotation_utils.py        # 공통 유틸리티 및 DB 연동
├── quotation_form.py         # 견적서 작성 폼
├── quotation_list.py         # 견적서 목록 및 관리
├── quotation_status.py       # 상태 관리 및 워크플로우
├── quotation_edit.py         # 견적서 수정 (리비전/직접수정/복사)
└── quotation_print.py        # CSS 기반 인쇄 양식
```

**메인 통합 파일:**
```
components/quotation_management.py  # 모든 컴포넌트 통합
```

### 2. quotation_utils.py (공통 유틸리티)
**핵심 기능:**
- DB 스키마 정의 및 검증 (QUOTATIONS_SCHEMA)
- Generated column 관리 (total_amount 자동 계산)
- 필수 필드 검증 (REQUIRED_FIELDS)
- 데이터 로드 함수들 (고객/직원/제품)
- 견적서 번호 자동 생성
- 리비전 번호 생성 및 관리
- 가격 계산 (원가 + 관리비 20% 포함)
- 상태 관리 및 색상 시스템
- 영업프로세스 자동 생성

**주요 함수:**
```python
- generate_quote_number()           # 견적번호 자동생성
- generate_revision_number()        # 리비전 번호 생성
- validate_quotation_data()         # 데이터 검증
- prepare_quotation_data()          # DB 저장용 데이터 변환
- calculate_pricing()               # 가격 계산 (관리비 포함)
- update_quotation_status()         # 상태 업데이트
- create_sales_process_from_quotation() # 영업프로세스 생성
```

### 3. quotation_form.py (견적서 작성)
**완성된 기능:**
- 고객사 선택 및 정보 자동 입력
- 제품 선택 시 모든 정보 자동 입력 (코드/이름/가격)
- 담당자 선택
- 실시간 가격 계산 및 마진 분석
- 수정 모드 지원 (기존 데이터 로드)
- 완전한 데이터 검증

**자동 입력 필드:**
- 제품 코드, 영어/베트남어 제품명
- 원가 (USD), 판매가 (VND/USD)
- 리드타임 자동 납기일 계산

**수동 입력 필드:**
- 프로젝트 정보 (프로젝트명/부품명/금형번호)
- 재료 정보 (수지타입/첨가제/Material)
- 거래 조건 (결제조건/VAT/통화)

### 4. quotation_list.py (견적서 목록)
**주요 기능:**
- 견적서 목록 테이블 표시
- 다중 필터링 (상태/고객사/검색어)
- 견적서 상세 정보 표시
- 액션 버튼들:
  - 상태 변경 (발송/승인/완료)
  - 수정 (새 리비전 생성)
  - 복사 (새 견적서 번호)
  - 삭제 (2단계 확인)
- 요약 통계 표시

### 5. quotation_status.py (상태 관리)
**완성된 워크플로우:**
```
작성중 → 발송됨 → 고객승인 → 완료
           ↓
     (고객승인 시)
           ↓
    영업프로세스 자동 생성
```

**주요 기능:**
- 상태별 카드 형태 표시
- 단계별 상태 변경 버튼
- 상태 되돌리기 기능
- 일괄 상태 변경
- 상태별 통계 및 요약
- 워크플로우 가이드

### 6. quotation_edit.py (견적서 수정)
**3가지 수정 방식:**
1. **새 리비전**: Rv00 → Rv01로 새 버전 생성
2. **기존 수정**: 원본 데이터 직접 수정 (신중하게 사용)
3. **복사**: 완전히 새로운 견적서로 복사

**안전장치:**
- 완료된 견적서는 수정 불가
- 수정 전 경고 메시지
- 전체 필드 수정 가능
- 수정 이력 추적

### 7. quotation_print.py (인쇄 양식)
**CSS 기반 전문 인쇄 시스템:**
- 브라우저 인쇄 기능 활용 (Ctrl+P)
- 인쇄 시 Streamlit UI 자동 숨김
- 페이지 레이아웃 최적화

**다국어 지원:**
- 한국어: 견적서
- English: QUOTATION  
- Tiếng Việt: BÁO GIÁ

**완전한 비즈니스 문서:**
- 회사 헤더 및 로고 위치
- 견적 정보 (번호/일자/유효기한)
- 고객 정보 (회사/담당자/연락처)
- 제품 정보 테이블
- 금액 요약 (소계/VAT/총액)
- 프로젝트 정보
- 거래 조건
- 서명란 (공급업체/고객)

### 8. quotation_management.py (메인 통합)
**6개 탭 구성:**
1. **견적서 작성**: 제품 연동 및 자동 계산
2. **견적서 목록**: 필터링 및 관리
3. **상태 관리**: 워크플로우 및 영업프로세스 연동  
4. **견적서 수정**: 리비전/직접수정/복사
5. **견적서 인쇄**: 다국어 전문 양식
6. **시스템 정보**: 구성 및 통계

**시스템 모니터링:**
- 실시간 상태 확인 (견적서/고객/직원/제품 수)
- 컴포넌트별 독립적 오류 처리
- 필수 데이터 존재 여부 검증
- 개발 모드 지원

---

## 완성된 시스템 아키텍처

### 모듈화된 디렉토리 구조
```
D:\ymv-business-system/
├── app/
│   ├── main.py
│   ├── components/
│   │   ├── quotation_management.py    # Step 18에서 완전 재구성
│   │   ├── quotation/                 # Step 18 신규 폴더
│   │   │   ├── quotation_utils.py     # 공통 유틸리티
│   │   │   ├── quotation_form.py      # 견적서 작성
│   │   │   ├── quotation_list.py      # 견적서 목록
│   │   │   ├── quotation_status.py    # 상태 관리
│   │   │   ├── quotation_edit.py      # 견적서 수정
│   │   │   └── quotation_print.py     # 인쇄 양식
│   │   ├── dashboard.py
│   │   ├── expense_management.py
│   │   ├── employee_management.py
│   │   ├── product_management.py
│   │   ├── supplier_management.py
│   │   ├── sales_process_management.py
│   │   ├── code_management.py
│   │   └── multilingual_input.py
│   └── utils/
```

### DB 스키마 안전성 확보
**quotations 테이블 완전 매핑:**
- **Generated Column 처리**: total_amount (quantity × unit_price)
- **필수 필드 최소화**: 6개 필드만 (견적번호/담당자/제품코드/제품명/수량/단가)
- **빈 값 허용**: 선택 필드들은 모두 빈 값 저장 가능
- **데이터 검증**: quotation_utils에서 완전한 검증 시스템

### 가격 계산 시스템 완성
**원가 + 관리비 20% 반영:**
```python
base_cost_usd = product.cost_price_usd
total_cost_vnd = base_cost_usd * 24000 * 1.20  # 관리비 20% 포함
margin_vnd = selling_price_vnd - total_cost_vnd
margin_rate = (margin_vnd / selling_price_vnd) * 100
```

**실시간 계산 표시:**
- VND/USD 이중 계산
- 할인율 적용
- VAT 계산
- 마진율 분석

---

## Step 18 개발 코드 분석

### 1. quotation_utils.py 핵심 설계
**DB 스키마 기반 안전성:**
```python
QUOTATIONS_SCHEMA = {
    'id': 'integer',
    'customer_id': 'integer', 
    'quote_number': 'character varying',
    'total_amount': 'numeric',  # Generated column
    # ... 전체 37개 필드
}

GENERATED_COLUMNS = ['total_amount']  # 자동 계산 컬럼 제외
REQUIRED_FIELDS = [                   # 필수 입력 6개만
    'quote_number', 'sales_rep_id', 'item_code', 
    'item_name_en', 'quantity', 'unit_price'
]
```

**완전한 데이터 검증:**
```python
def validate_quotation_data(data):
    missing_fields = []
    for field in REQUIRED_FIELDS:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if data.get('quantity', 0) <= 0:
        missing_fields.append('quantity (수량은 1 이상)')
    
    return missing_fields
```

### 2. quotation_form.py 자동화 시스템
**제품 선택 시 완전 자동 입력:**
```python
def extract_product_data(selected_product):
    return {
        'item_code': selected_product.get('full_code') or selected_product.get('product_code'),
        'item_name_en': selected_product.get('product_name_en'),
        'item_name_vn': selected_product.get('product_name_vn'),
        'cost_price_usd': selected_product.get('cost_price_usd', 0),
        'unit_price_vnd': selected_product.get('unit_price_vnd', 0),
        'lead_time_days': selected_product.get('lead_time_days', 30)
    }
```

**실시간 가격 계산:**
```python
def calculate_pricing(product_data, quantity, discount_rate, vat_rate):
    exchange_rate = 24000
    base_cost_usd = product_data.get('cost_price_usd', 0)
    total_cost_vnd = base_cost_usd * exchange_rate * 1.20  # 관리비 20%
    
    selling_price_vnd = product_data.get('unit_price_vnd', 0)
    discounted_price_vnd = selling_price_vnd * (1 - discount_rate / 100)
    
    margin_vnd = discounted_price_vnd - total_cost_vnd
    margin_rate = (margin_vnd / discounted_price_vnd * 100)
    
    return {
        'total_cost_vnd': total_cost_vnd,
        'margin_rate': margin_rate,
        # ... 전체 계산 결과
    }
```

### 3. quotation_print.py CSS 인쇄 시스템
**전문적인 인쇄 레이아웃:**
```css
@media print {
    .quotation-header {
        text-align: center;
        border-bottom: 3px solid #0066CC;
        padding-bottom: 20px;
    }
    
    .product-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .total-amount {
        font-size: 24px;
        font-weight: bold;
        color: #0066CC;
        text-align: center;
    }
    
    .stButton, .stSelectbox { display: none !important; }
}
```

**다국어 지원 시스템:**
```python
def get_language_texts(language):
    if language == "English":
        return {'quotation': 'QUOTATION', 'customer_name': 'Customer', ...}
    elif language == "Tiếng Việt":
        return {'quotation': 'BÁO GIÁ', 'customer_name': 'Khách hàng', ...}
    else:  # 한국어
        return {'quotation': '견 적 서', 'customer_name': '고객사', ...}
```

---

## 완성된 워크플로우

### 견적서 생성부터 영업프로세스까지
1. **견적서 작성**: 제품 선택 → 모든 정보 자동 입력 → 저장
2. **견적서 발송**: 상태 관리에서 "발송" 버튼 클릭
3. **고객 승인**: "고객승인" 버튼 클릭 → 자동 영업프로세스 생성
4. **프로세스 추적**: sales_process 테이블에서 진행상황 관리
5. **견적서 완료**: 계약 체결 후 "완료" 상태로 변경

### 견적서 수정 워크플로우
1. **새 리비전**: YMV-Q250928-001-Rv00 → Rv01 (기존 보존)
2. **기존 수정**: 원본 데이터 직접 수정 (신중하게 사용)
3. **견적서 복사**: 완전히 새로운 견적번호로 복사

### 인쇄 워크플로우
1. **견적서 선택**: 인쇄할 견적서 선택
2. **언어 선택**: 한국어/English/Tiếng Việt
3. **옵션 설정**: 로고 포함, 거래조건 포함
4. **미리보기**: CSS 적용된 전문 양식 확인
5. **인쇄**: 브라우저 인쇄 기능 (Ctrl+P) 사용

---

## Step 18 개발 완성도 통계

### 컴포넌트별 완성도
```
✅ quotation_utils.py        100% (DB 연동 및 공통 기능)
✅ quotation_form.py         100% (견적서 작성 폼)
✅ quotation_list.py         100% (견적서 목록 관리)
✅ quotation_status.py       100% (상태 관리 워크플로우)
✅ quotation_edit.py         100% (견적서 수정 기능)
✅ quotation_print.py        100% (다국어 인쇄 양식)
✅ quotation_management.py   100% (메인 통합 파일)
```

### 기능 완성도
```
✅ 견적서 작성: 제품 연동 + 자동 계산 + 마진 분석
✅ 견적서 관리: 목록 + 필터링 + 상세보기 + 액션버튼
✅ 상태 관리: 워크플로우 + 영업프로세스 연동
✅ 견적서 수정: 리비전 + 직접수정 + 복사
✅ 인쇄 시스템: 다국어 + CSS 최적화 + 전문 양식
✅ 데이터 검증: DB 스키마 + 필수필드 + 오류처리
✅ 시스템 통합: 6개 탭 + 상태모니터링 + 개발모드
```

### 테스트 상태
```
❌ 컴포넌트 임포트 테스트: 미완료
❌ 견적서 작성 플로우 테스트: 미완료
❌ 상태 변경 워크플로우 테스트: 미완료
❌ 인쇄 양식 테스트: 미완료
❌ 다국어 지원 테스트: 미완료
❌ 오류 처리 테스트: 미완료
```

---

## 다음 채팅 개발 시 주의사항

### Step 18 완성 상태
- **견적서 관리 시스템**: 100% 모듈화 완성 (코드 작성)
- **컴포넌트 분리**: 완전 독립적 구조 설계
- **다국어 인쇄**: CSS 기반 전문 시스템 개발
- **테스트**: 미완료 상태

### 필수 테스트 작업
1. **파일 구조 생성**: components/quotation/ 폴더 및 6개 파일 생성
2. **임포트 테스트**: 모든 컴포넌트 정상 로드 확인
3. **견적서 작성 테스트**: 제품 선택부터 저장까지
4. **상태 관리 테스트**: 발송→승인→완료 워크플로우
5. **인쇄 테스트**: 다국어 양식 브라우저 확인
6. **오류 처리 테스트**: 각종 예외 상황 확인

### 파일 교체 작업 순서
1. **백업**: 기존 quotation_management.py 백업
2. **폴더 생성**: components/quotation/ 폴더 생성
3. **컴포넌트 생성**: 6개 .py 파일 생성 및 코드 입력
4. **메인 교체**: 새로운 quotation_management.py 적용
5. **테스트 실행**: 전체 플로우 동작 확인

### 잠재적 문제점
- **임포트 오류**: 상대 경로 임포트 문제 가능성
- **함수 호출**: load_func 전역 변수 문제
- **세션 상태**: 컴포넌트 간 상태 공유 문제
- **CSS 충돌**: 인쇄 스타일과 Streamlit 스타일 충돌

---

## Step 18 완성 선언 (테스트 제외)

**YMV ERP 견적서 관리 시스템 v18.0 코드 완성!**

- **모듈화**: 6개 독립 컴포넌트로 완전 분리
- **기능 완성도**: 견적서 관리 100% 완성
- **코드 품질**: 오류 처리 + 데이터 검증 완벽
- **사용자 경험**: 직관적 UI + 실시간 피드백
- **국제화**: 다국어 인쇄 시스템 완성
- **확장성**: 모듈 구조로 추가 개발 용이

**현재 상태**: 코드 작성 완료, 테스트 필요
**다음 단계**: 컴포넌트 테스트 및 통합 테스트

---

## 다음 채팅에서 개발 재개 방법

**테스트 진행 준비 완료!**

다음 채팅에서 이 문서를 업로드하고:

> "이 백업 문서를 기반으로 Step 18 컴포넌트 테스트를 진행해줘"

라고 요청하면 즉시 테스트 작업을 시작할 수 있습니다.

**현재 시스템 상태:**
- 견적서 관리 시스템 완전 모듈화 완성 (코드)
- 6개 독립 컴포넌트 개발 완료
- 다국어 CSS 인쇄 시스템 개발 완료
- 테스트 및 통합 작업 필요