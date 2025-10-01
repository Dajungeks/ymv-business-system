# YMV ERP 시스템 백업 파일

**백업 일시:** 2025-10-01  
**작업 내용:** 회계 확인 기능 개발 완료, 반려 요청서 수정 권한 개선

---

## 📊 시스템 현황

### 프로젝트 기본 정보
- **프로젝트명:** YMV 관리 프로그램 (ERP 시스템)
- **개발 언어:** Python + Streamlit
- **데이터베이스:** Supabase (PostgreSQL)
- **회사 규모:** 10인 중소기업
- **프로젝트 위치:** D:\ymv-business-system
- **현재 진행률:** Step 28 완료 (회계 확인 기능)

### Supabase 연결 정보
```
SUPABASE_URL = "https://eqplgrbegwzeynnbcuep.supabase.co"
GitHub: https://github.com/Dajungeks/ymv-business-system.git
```

---

## 🎯 Step 28 완료 작업: 회계 확인 기능

### ✅ 완료된 작업

#### 1. DB 구조 확장
- `expenses` 테이블에 회계 확인 관련 컬럼 추가 완료:
  - `accounting_confirmed` BOOLEAN DEFAULT FALSE
  - `accounting_confirmed_by` INTEGER REFERENCES employees(id)  
  - `accounting_confirmed_at` TIMESTAMP

#### 2. 새 컴포넌트 생성
- **`accounting_management.py`**: 회계 확인 전용 컴포넌트
  - `show_accounting_management()`: 독립 페이지용 (안내 메시지)
  - `show_accounting_management_with_data()`: 실제 기능 (데이터 로드)
  - `render_accounting_table()`: 엑셀 형식 테이블 표시
  - `confirm_accounting_with_data()`: 회계 확인 처리

#### 3. expense_management.py 기능 확장
- **새 탭 추가**: "💼 회계 확인" (Admin/CEO/Master만)
- **회계 확인 상태 컬럼**: 테이블에 "회계" 컬럼 추가
- **회계 확인 버튼**: 승인된 항목에 ✅ 버튼
- **회계 확인 대기 목록**: `render_accounting_pending_list()` 함수
- **필터 옵션**: "회계확인완료" 상태 필터 추가
- **회계 확인 정보**: 상세 정보에 확인자/확인일 표시

#### 4. main.py 업데이트
- **import 추가**: `from components.accounting_management import show_accounting_management`
- **새 페이지 함수**: `show_accounting_management_page()`
- **사이드바 메뉴**: "💼 회계 확인" 버튼 (권한 있는 사용자만)
- **라우팅**: `elif current_page == "회계 확인"` 추가
- **버전 업데이트**: v4.1 → v4.2

#### 5. 권한 및 수정 기능 개선
- **반려 요청서 수정**: 요청자 본인이 권한에 관계없이 수정 가능
- **수정 버튼 조건**:
  ```python
  can_edit = False
  if user_role == 'Master':
      can_edit = True
  elif expense_status == 'rejected' and expense.get('requester') == current_user_id:
      can_edit = True  # 반려된 요청서는 본인이 수정 가능
  elif user_role in ['Admin', 'CEO'] and expense_status == 'pending':
      can_edit = True  # Admin/CEO는 대기중인 요청서 수정 가능
  ```

### 🔄 상태 흐름
```
pending → approved → accounting_confirmed
(대기)    (승인됨)    (회계확인 완료)
```

### 🔑 권한별 기능
- **CEO/Master**: 승인 + 회계 확인 가능
- **Admin**: 회계 확인만 가능  
- **Staff/Manager**: 요청서 작성, 반려된 본인 요청서 수정 가능

---

## 🗄️ 데이터베이스 구조

### expenses 테이블 (회계 확인 컬럼 추가)
```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    document_number VARCHAR,
    expense_type VARCHAR NOT NULL,
    amount NUMERIC NOT NULL,
    currency VARCHAR DEFAULT 'USD',
    payment_method VARCHAR NOT NULL,
    expense_date DATE NOT NULL,
    department VARCHAR,
    requester INTEGER REFERENCES employees(id),
    urgency VARCHAR DEFAULT '보통',
    description TEXT NOT NULL,
    business_purpose TEXT,
    status VARCHAR DEFAULT 'pending',  -- pending, approved, rejected
    vendor VARCHAR,
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES employees(id),
    approval_comment TEXT,
    receipt_number VARCHAR,
    accounting_confirmed BOOLEAN DEFAULT FALSE,  -- 새로 추가
    accounting_confirmed_by INTEGER REFERENCES employees(id),  -- 새로 추가
    accounting_confirmed_at TIMESTAMP,  -- 새로 추가
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### employees 테이블 (변경사항 없음)
```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    username VARCHAR,
    employee_id VARCHAR,
    password VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    department VARCHAR,
    position VARCHAR,
    role VARCHAR,  -- Staff, Manager, Admin, CEO, Master
    manager_id INTEGER REFERENCES employees(id),
    employment_status VARCHAR DEFAULT 'active',
    hire_date DATE,
    salary NUMERIC,
    work_type VARCHAR DEFAULT 'full_time',
    birth_date DATE,
    address TEXT,
    emergency_contact VARCHAR,
    emergency_phone VARCHAR,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 📋 파일 구조

```
app/
├── components/
│   ├── accounting_management.py     ✅ 새로 추가 (회계 확인 전용)
│   └── expense_management.py        ✅ 수정됨 (회계 확인 기능 통합)
├── templates/
│   └── expense_print_template.html  ✅ 문서번호 포함, A4 최적화
├── utils/
│   └── helpers.py                   ✅ 기존 유지
└── main.py                          ✅ 수정됨 (회계 확인 페이지 추가)
```

---

## 💻 주요 함수 및 기능

### 1. accounting_management.py

#### `show_accounting_management()`
- **용도**: 독립 회계 확인 페이지용 (안내 메시지만)
- **표시**: 회계 확인 프로세스 설명

#### `show_accounting_management_with_data(load_data_func, update_data_func, get_current_user_func)`
- **용도**: 실제 회계 확인 기능
- **기능**: 
  - 회계 확인 완료된 지출요청서 조회
  - 정렬 옵션 (회계확인일순, 지출일순, 금액순)
  - Excel/CSV 다운로드

#### `render_accounting_table(expenses, employee_dict, export_format)`
- **용도**: 회계 완료 리스트를 엑셀 형식으로 표시
- **컬럼**: 문서번호, 지출일, 지출유형, 요청자, 부서, 금액, 통화, 결제방법, 지출내역, 사업목적, 공급업체, 영수증번호, 승인일, 승인자, 회계확인일, 회계확인자, 처리의견

#### `confirm_accounting_with_data(expense_id, user_id, update_data_func)`
- **용도**: 회계 확인 처리
- **업데이트**: accounting_confirmed, accounting_confirmed_by, accounting_confirmed_at

### 2. expense_management.py 주요 변경사항

#### 탭 구조 변경
```python
if user_role in ['Admin', 'CEO', 'Master']:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 지출요청서 작성", 
        "📋 지출요청서 목록", 
        "📊 지출 통계", 
        "👨‍💼 승인 관리",
        "💼 회계 확인"  # 새 탭
    ])
```

#### 테이블 컬럼 확장 (8개 → 9개)
```python
header_cols = st.columns([1.2, 0.5, 1, 1, 1.2, 1.5, 1.2, 1, 1])
# 문서번호, No, 날짜, 유형, 요청자, 금액, 상태, 회계, 액션
```

#### 회계 확인 버튼 로직
```python
if expense_status == 'approved' and not accounting_confirmed and user_role in ['Admin', 'CEO', 'Master']:
    if st.button("✅", key=f"accounting_{expense.get('id')}", help="회계 확인"):
        if confirm_accounting_expense(expense.get('id'), current_user.get('id'), update_data_func):
            st.success("회계 확인 완료!")
            st.rerun()
```

#### `render_accounting_pending_list()` 함수
- **위치**: expense_management.py 내부
- **기능**: 회계 확인 대기 중인 항목을 expander에 표시 (최대 5건)

### 3. main.py 변경사항

#### 새 페이지 함수
```python
def show_accounting_management_page():
    """회계 확인 관리 페이지"""
    current_user = auth_manager.get_current_user()
    user_role = current_user.get('role', 'Staff') if current_user else 'Staff'
    
    if user_role not in ['Admin', 'CEO', 'Master']:
        st.warning("⚠️ 회계 확인 권한이 없습니다.")
        return
    
    from components.accounting_management import show_accounting_management_with_data
    show_accounting_management_with_data(
        db_operations.load_data,
        db_operations.update_data,
        auth_manager.get_current_user
    )
```

#### 사이드바 메뉴 추가
```python
if current_user and current_user.get('role') in ['Admin', 'CEO', 'Master']:
    if st.button("💼 회계 확인", use_container_width=True,
                type="primary" if st.session_state.current_page == "회계 확인" else "secondary"):
        st.session_state.current_page = "회계 확인"
        st.rerun()
```

---

## 🔧 해결된 문제들

### 1. Import 오류 해결
- **문제**: `from app.components.accounting_management`
- **해결**: `from components.accounting_management`

### 2. ConnectionWrapper 의존성 제거
- **문제**: `utils.helpers`에 ConnectionWrapper 없음
- **해결**: 기존 `db_operations` 활용

### 3. Circular Import 방지
- **문제**: accounting_management에서 main.py import 시 set_page_config 중복
- **해결**: 함수 매개변수로 데이터 로드 함수 전달

### 4. 반려 요청서 수정 권한 확장
- **문제**: Admin만 본인 반려 요청서 수정 가능
- **해결**: 모든 사용자가 본인 반려 요청서 수정 가능

---

## 🎯 정상 작동 기능

### 기존 기능 (유지)
- ✅ Role 5단계 (Staff → Master)
- ✅ Position 영문화
- ✅ 지출요청서 작성/수정
- ✅ 승인/반려 프로세스
- ✅ 재신청 기능
- ✅ 프린트 기능 (A4 1장, 결재란 하단 고정)
- ✅ 문서번호 시스템 (EXP-YYMMDD-Count)
- ✅ 테이블형 목록 UI
- ✅ 통화 단위 VND 통일

### 새 기능 (Step 28 추가)
- ✅ 회계 확인 기능 (Admin/CEO/Master)
- ✅ 회계 확인 상태 표시
- ✅ 회계 완료 리스트 (Excel/CSV 다운로드)
- ✅ 회계 확인 대기 목록
- ✅ 회계확인완료 필터 옵션
- ✅ 반려 요청서 수정 권한 확장

---

## 🔑 핵심 정보

### 로그인 계정
- **Master**: 2508111
- **CEO**: 2508001 (KIM CHUNGSUNG, id=4)
- **Admin**: 2508002 (Lưu Thị Hằng, id=3)

### 권한별 회계 확인 기능
- **CEO/Master**: 승인 + 회계 확인
- **Admin**: 회계 확인만 가능
- **Staff/Manager**: 요청서 작성, 반려된 본인 요청서 수정

### DB 상태값
- **expenses.status**: pending, approved, rejected (영문)
- **expenses.accounting_confirmed**: false/true (회계 확인 여부)

---

## 🚀 사용 방법

### 회계 확인 프로세스
1. **지출 요청서 작성**: Staff/Manager 등이 작성
2. **승인**: CEO/Master가 승인
3. **회계 확인 대기**: 승인된 항목이 대기 상태
4. **회계 확인**: Admin/CEO/Master가 회계 확인
5. **최종 완료**: 회계 완료 리스트에 표시

### 접근 경로
- **회계 확인 수행**: 지출 요청서 > 지출요청서 목록 > 회계 컬럼 ✅ 버튼
- **회계 확인 대기**: 지출 요청서 > 지출요청서 목록 > ⏳ 회계 확인 대기 목록
- **회계 완료 리스트**: 
  - 지출 요청서 > 회계 확인 탭
  - 또는 사이드바 > 💼 회계 확인 메뉴

### 필터링
- **상태 필터**: 전체, 대기, 승인, 거부, **회계확인완료**
- **회계 상태**: ✅ (완료), ⏳ (대기), — (해당없음)

---

## ⚠️ 알려진 제한사항

### 회계 확인 페이지 데이터 표시 이슈
**현상**: 독립 회계 확인 페이지에서 데이터가 표시되지 않음
**원인**: `show_accounting_management()` 함수가 안내 메시지만 표시
**해결**: main.py의 `show_accounting_management_page()`에서 `show_accounting_management_with_data()` 호출 필요

**수정 필요한 코드**:
```python
# main.py의 show_accounting_management_page() 함수에서
from components.accounting_management import show_accounting_management_with_data
show_accounting_management_with_data(
    db_operations.load_data,
    db_operations.update_data,
    auth_manager.get_current_user
)
```

---

## 💡 재개 방법

### 새 채팅에서 시작하기
1. **파일 업로드**: 
   - 이 백업 파일
   - `program_development_rules - V10 Final.txt`

2. **명령어**: 
   ```
   규칙 V10 + 이 백업 기준으로 개발 이어가줘
   ```

3. **즉시 확인 가능**:
   - 회계 확인 기능 정상 작동
   - 반려 요청서 수정 가능
   - 회계 완료 리스트 표시

---

## 🔍 다음 작업 후보

### 미완료 작업
1. **회계 확인 페이지 데이터 표시 수정**
2. **문서번호 자동 생성** (새 지출요청서 작성 시)
3. **대시보드 회계 통계 추가**

### 향후 개선 사항
- 구매 요청 기능 추가
- 재고 관리 기능
- 다국어 지원 (베트남어/영어) 
- 모바일 반응형 개선
- 알림 시스템 구축

---

**백업 생성 일시**: 2025-10-01  
**작업자**: YMV ERP 개발팀  
**다음 작업**: 회계 확인 페이지 데이터 표시 수정

이 백업 시점에서 YMV ERP 시스템의 회계 확인 기능은 완료되었으며, 승인-회계확인-완료의 3단계 프로세스가 구현되었습니다.