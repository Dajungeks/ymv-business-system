# YMV ERP 시스템 백업 파일

**백업 일시:** 2025-10-01  
**작업 내용:** 지출요청서 테이블형 UI 개선, 문서번호 시스템 구축 완료

---

## 📊 시스템 현황

### 프로젝트 기본 정보
- **프로젝트명:** YMV 관리 프로그램 (ERP 시스템)
- **개발 언어:** Python + Streamlit
- **데이터베이스:** Supabase (PostgreSQL)
- **회사 규모:** 10인 중소기업
- **프로젝트 위치:** D:\ymv-business-system
- **현재 진행률:** 문서번호 시스템 완료

### Supabase 연결 정보
```
SUPABASE_URL = "https://eqplgrbegwzeynnbcuep.supabase.co"
GitHub: https://github.com/Dajungeks/ymv-business-system.git
```

---

## 🎯 완료된 작업

### Step 27: 프린트 기능 개선
1. HTML 템플릿 A4 최적화
2. 회사 주소 삭제 (Tax Code만 표시)
3. CEO 이름 자동 표시
4. 결재란 날짜 좌측 정렬
5. 결재란 A4 하단 고정
6. 통화 단위 VND 통일

### 문서번호 시스템 구축
1. **DB 컬럼 추가:**
   - `expenses` 테이블에 `document_number VARCHAR` 추가
   
2. **문서번호 형식:**
   - `EXP-YYMMDD-Count`
   - 예: `EXP-250914-001`, `EXP-250914-002`
   
3. **기존 데이터 처리:**
   - 46건의 지출요청서에 문서번호 자동 생성
   - expense_date 기준으로 날짜별 순번 부여

4. **UI 개선:**
   - 테이블형 레이아웃 (8개 컬럼)
   - 문서번호 첫 번째 컬럼에 표시
   - 검정 실선 구분
   - 상세 정보 expander 전체 너비로 확장

5. **프린트 템플릿:**
   - 문서번호 상단 표시
   - 문서 하단에도 Document ID 표시

---

## 🗄️ 데이터베이스 구조

### employees 테이블
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
    role VARCHAR,
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

**주요 직원:**
- id=3: Lưu Thị Hằng (2508002, Admin)
- id=4: KIM CHUNGSUNG (2508001, CEO)

### expenses 테이블
```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    document_number VARCHAR,  -- 추가됨
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
    status VARCHAR DEFAULT 'pending',
    vendor VARCHAR,
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES employees(id),
    approval_comment TEXT,
    receipt_number VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**현재 데이터:** 46건의 지출요청서 (모두 문서번호 보유)

---

## 📋 파일 구조

```
app/
├── templates/
│   └── expense_print_template.html  ✅ 문서번호 추가, 결재란 하단 고정
├── utils/
│   └── helpers.py                   ✅ document_number 변수 추가
├── components/
│   └── expense_management.py        ✅ 테이블형 UI, 8개 컬럼
└── main.py
```

---

## 💻 주요 함수 변경사항

### 1. expense_management.py - render_expense_list()

**주요 변경:**
- 컬럼 개수: 7개 → 8개
- 컬럼 비율: `[1.2, 0.5, 1, 1, 1.2, 2, 1.2, 1]`
- 헤더: 문서번호, No, 날짜, 유형, 요청자, 금액, 상태, 액션
- expander 전체 너비로 확장
- 검정 실선 구분: `<hr style='margin: 2px 0; border: none; border-top: 1px solid #000;'>`

```python
# 테이블 헤더
header_cols = st.columns([1.2, 0.5, 1, 1, 1.2, 2, 1.2, 1])
header_cols[0].markdown("**문서번호**")
header_cols[1].markdown("**No**")
# ...

# 각 행
row_cols = st.columns([1.2, 0.5, 1, 1, 1.2, 2, 1.2, 1])
row_cols[0].write(document_number)
# ...

# 검정 실선
st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #000;'>", unsafe_allow_html=True)

# expander
with st.expander("", expanded=False):
    # 상세 정보 전체 너비 사용
```

### 2. helpers.py - PrintFormGenerator.render_print_form()

**추가된 부분:**
```python
# 문서번호
document_number = expense.get('document_number', 'N/A')

# 템플릿 변수 치환
print_html = template.format(
    expense_id=expense.get('id', 'N/A'),
    document_number=document_number,  # 추가
    # ... 나머지 변수들
)
```

### 3. expense_print_template.html

**주요 변경:**
1. 문서번호 표시:
```html
<div class="document-title">
    <h1>지출 요청서</h1>
    <p>EXPENSE REQUEST FORM</p>
    <p class="document-number">문서번호: {document_number}</p>
</div>
```

2. 결재란 하단 고정:
```css
.approval-section {
    position: absolute;
    bottom: 50mm;
    left: 12mm;
    right: 12mm;
}

.document-footer {
    position: absolute;
    bottom: 12mm;
    left: 12mm;
    right: 12mm;
}

.print-container {
    position: relative;
}
```

3. 날짜 좌측 정렬:
```css
.date-space {
    text-align: left !important;
    padding-left: 10px;
}
```

---

## 🔑 핵심 정보

### 로그인 계정
- Master: 2508111
- CEO: 2508001 (KIM CHUNGSUNG, id=4)
- Admin: 2508002 (Lưu Thị Hằng, id=3)

### 권한 체계
- **Staff:** 본인 지출요청서 작성만
- **Manager:** 본인 지출요청서 작성, 구매품 전체 조회
- **Admin:** 지출요청서 작성/관리, 직원 관리 (승인 불가)
- **CEO:** 지출요청서 승인/반려, 직원 관리
- **Master:** 모든 권한

### DB 상태값
- expenses.status: **pending, approved, rejected** (영문)

---

## 🎯 정상 작동 기능

- ✅ Role 5단계 (Staff → Master)
- ✅ Position 영문화
- ✅ 지출요청서 작성/수정
- ✅ 승인/반려 프로세스
- ✅ 재신청 기능
- ✅ 프린트 기능 (A4 1장, 결재란 하단 고정)
- ✅ 문서번호 시스템 (EXP-YYMMDD-Count)
- ✅ 테이블형 목록 UI
- ✅ 통화 단위 VND 통일

---

## 🔧 알려진 제한사항

### 문서번호 자동 생성 미구현
**현상:** 새로 지출요청서 작성 시 문서번호가 자동 생성되지 않음

**임시 해결:** 수동으로 DB에서 문서번호 생성 필요

**향후 개선 필요:**
- `render_expense_form()` 함수에서 저장 시 자동 생성 로직 추가
- 같은 날짜의 마지막 Count 조회 → +1

---

## 💡 재개 방법

### 새 채팅에서 시작하기

1. **파일 업로드:**
   - 이 백업 파일
   - `program_development_rules - V10 Final.txt`

2. **명령어:**
   ```
   규칙 V10 + 이 백업 기준으로 개발 이어가줘
   ```

3. **즉시 확인 가능:**
   - 지출요청서 목록 테이블형 UI
   - 문서번호 표시
   - 프린트 기능 정상 작동

---

## 🚀 다음 작업 (미완료)

### 회계 확인 기능 개발

**요구사항:**
1. 승인 후 "회계 확인" 단계 추가
2. 회계 확인 완료 시 "최종 완료" 처리
3. 회계 완료 리스트 별도 표시 (엑셀 형식)

**구현 계획:**

#### 1단계: DB 수정
```sql
ALTER TABLE expenses 
ADD COLUMN accounting_confirmed BOOLEAN DEFAULT FALSE,
ADD COLUMN accounting_confirmed_by INTEGER REFERENCES employees(id),
ADD COLUMN accounting_confirmed_at TIMESTAMP;
```

#### 2단계: 상태 흐름
```
pending → approved → accounting_confirmed
(대기)    (승인됨)    (회계확인 완료)
```

#### 3단계: 화면 구성
- 지출요청서 목록: 회계 확인 대기 표시
- 회계 확인 버튼: Admin/CEO만
- 새 탭: "회계 완료 리스트" (엑셀 형식 테이블)

#### 4단계: 권한
- 승인: CEO/Master
- 회계 확인: Admin/CEO/Master

**수정 파일:**
- `expense_management.py`: 새 탭 추가, 회계 확인 버튼
- `helpers.py`: 상태 정보 추가
- `main.py`: 탭 추가

---

## 📊 문서번호 생성 이력

### 최근 생성된 문서번호 (2025-10-01)

| ID | 문서번호 | 날짜 | 유형 | 금액 | 요청자 |
|----|---------|------|------|------|--------|
| 36 | EXP-250907-001 | 09-07 | 접대비 | 691,200 | id=3 |
| 35 | EXP-250909-001 | 09-09 | 접대비 | 553,200 | id=3 |
| 31 | EXP-250910-001 | 09-10 | 교통비 | 820,170 | id=3 |
| 38 | EXP-250912-002 | 09-12 | 사무용품 | 453,600 | id=3 |
| 37 | EXP-250913-001 | 09-13 | 사무용품 | 3,904,000 | id=3 |
| 39 | EXP-250914-004 | 09-14 | 접대비 | 4,760,081 | id=3 |
| 33 | EXP-250925-002 | 09-25 | 접대비 | 1,380,000 | id=3 |
| 32 | EXP-250926-002 | 09-26 | 접대비 | 205,200 | id=3 |
| 40 | EXP-250926-003 | 09-26 | 사무용품 | 1,050,000 | id=3 |
| 41 | EXP-250929-001 | 09-29 | 접대비 | 1,639,600 | id=3 |
| 34 | EXP-251001-001 | 10-01 | 접대비 | 553,200 | id=3 |

---

**백업 생성 일시:** 2025-10-01  
**작업자:** YMV ERP 개발팀  
**다음 작업:** 회계 확인 기능 개발

이 백업 시점에서 YMV ERP 시스템의 지출요청서 문서번호 시스템은 완료되었으며, 회계 확인 기능 개발을 위한 준비가 완료되었습니다.
