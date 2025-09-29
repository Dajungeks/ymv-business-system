📌 YMV ERP 시스템 백업 파일 - Step 27 완료
백업 일시: 2025-09-29
작업 내용: 프린트 기능 A4 최적화 완료, CEO 이름 표시 수정, DB 데이터 정리 완료

📊 시스템 현황
프로젝트 기본 정보
프로젝트명: YMV 관리 프로그램 (ERP 시스템)
개발 언어: Python + Streamlit
데이터베이스: Supabase (PostgreSQL)
회사 규모: 10인 중소기업
프로젝트 위치: D:\ymv-business-system
현재 진행률: Step 27 완료
Supabase 연결 정보
SUPABASE_URL = "https://eqplgrbegwzeynnbcuep.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
GitHub: https://github.com/dajungeks/ymv-business-system.git
🎯 Step 27 완료 작업
✅ 완료된 작업
HTML 템플릿 A4 최적화
전체 크기 10% 축소
회사 주소 2줄 삭제 (Tax Code만 표시)
표 높이 5% 축소
지출 내역/사업 목적 칸 10% 축소
결재란 높이 축소
프린트 레이아웃 개선
padding: 13.5mm → 12mm
폰트 크기 전반적 축소
섹션 간격 축소
A4 1장 내 모든 내용 포함 완료
결재란 개선
CEO 이름 자동 표시 기능 구현
날짜 좌측 정렬
승인 상태별 배경색 표시
helpers.py 수정
타입 안전 처리 추가 (int 변환)
employee_dict 키를 정수형으로 통일
approved_by 매칭 로직 개선
DB 데이터 정리
approved 상태인데 approved_by가 null인 데이터 수정
approved_by = 4 (CEO) 설정
approved_at = created_at으로 설정
🗄️ 데이터베이스 구조
employees 테이블
sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    username VARCHAR,
    employee_id VARCHAR,
    password VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    department VARCHAR,
    position VARCHAR,  -- Staff, Junior Manager, Manager, Senior Manager, Director, CEO
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
expenses 테이블
sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
📋 파일 구조
app/
├── templates/
│   └── expense_print_template.html  ✅ A4 최적화 완료
├── utils/
│   └── helpers.py                   ✅ 타입 안전 처리 완료
├── components/
│   └── expense_management.py        ✅ 정상 작동
└── main.py
💻 주요 함수 및 호출 관계
1. PrintFormGenerator.render_print_form()
위치: app/utils/helpers.py

매개변수:

expense (dict): 지출요청서 데이터
employees (list): 직원 목록
주요 로직:

python
# 1. 직원 정보를 딕셔너리로 변환 (타입 안전)
employee_dict = {}
for emp in employees:
    emp_id = emp.get('id')
    if emp_id is not None:
        employee_dict[int(emp_id)] = emp  # 정수형 통일

# 2. 요청자 정보 추출
requester_id = int(expense.get('requester'))
requester_info = employee_dict.get(requester_id, {})

# 3. 승인자 정보 추출
approved_by = expense.get('approved_by')
if approved_by is not None:
    approved_by = int(approved_by)
    approver_info = employee_dict.get(approved_by, {})
    approver_name = approver_info.get('name', 'N/A')

# 4. 템플릿 파일 읽기 및 변수 치환
template_path = 'app/templates/expense_print_template.html'
with open(template_path, 'r', encoding='utf-8') as f:
    template = f.read()
print_html = template.format(...)
반환값: HTML 문자열 (st.components.v1.html로 렌더링)

2. expense_management.py - 프린트 흐름
show_expense_management()
    ↓
render_expense_list()
    ├── 프린트 모드 체크 (최우선)
    │   └── st.session_state.get('print_expense')
    │       ├── True → render_print_form(expense, employees)
    │       │   ├── 템플릿 로드
    │       │   ├── 직원 정보 조회 (타입 안전)
    │       │   ├── 변수 치환
    │       │   └── HTML 렌더링
    │       └── False → 목록 표시
    │
    └── 프린트 버튼 클릭
        └── st.session_state['print_expense'] = expense
            └── st.rerun()
🔧 해결한 문제들
1. CEO 이름 N/A 표시
원인: 타입 불일치 (employee_dict 키와 approved_by 값)

해결:

python
# 변경 전
employee_dict[emp_id] = emp

# 변경 후
employee_dict[int(emp_id)] = emp
2. HTML 템플릿 중괄호 오류
원인: Python .format() 메서드가 CSS 중괄호를 변수로 인식

해결: CSS의 모든 { → {{, } → }}

3. DB 데이터 누락
원인: approved 상태인데 approved_by, approved_at이 null

해결:

sql
UPDATE expenses
SET approved_by = 4, approved_at = created_at
WHERE status = 'approved' AND approved_by IS NULL;
4. A4 1장 초과
해결:

padding: 13.5mm → 12mm
폰트 크기 전반적 축소
섹션 간격 축소
회사 주소 삭제
📝 템플릿 파일 주요 스펙
expense_print_template.html
크기:

용지: A4 (210mm × 297mm)
패딩: 12mm
max-height: 297mm
주요 섹션:

문서 상태 배지 (13px)
회사 정보 (15px, Tax Code만)
문서 제목 (20px)
정보 테이블 (9px, 5행)
지출 내역/사업 목적 (9px, min-height: 50px)
반려 사유 (조건부)
결재란 (9px, signature: 50px, date: 25px)
문서 하단 (7px)
날짜 정렬:

모든 날짜 칸: 좌측 정렬 (text-align: left)
🔑 핵심 정보
로그인 계정
Master: 2508111
CEO: 2508001 (KIM CHUNGSUNG, id=4)
Admin: 2508002 (Lưu Thị Hằng, id=3)
권한 체계
Staff: 본인 지출요청서 작성만
Manager: 본인 지출요청서 작성, 구매품 전체 조회
Admin: 지출요청서 작성/관리, 직원 관리 (승인 불가)
CEO: 지출요청서 승인/반려, 직원 관리, 비밀번호 관리
Master: 모든 권한
DB 상태값
expenses.status: pending, approved, rejected (영문 통일 완료)
🎯 정상 작동 기능
Role 5단계 (Staff → Master)
Position 영문화
지출요청서 작성/수정
승인/반려 프로세스
재신청 기능
프린트 기능 (A4 1장 최적화 완료)
승인자(CEO) 정보 자동 표시
반려 사유 표시
날짜 좌측 정렬
💡 재개 방법
새 채팅에서 시작하기
파일 업로드:
이 백업 파일
program_development_rules - V10 Final.txt
명령어:
   규칙 V10 + 이 백업 기준으로 개발 이어가줘
즉시 확인 가능:
프린트 기능 정상 작동
CEO 이름 표시
A4 1장 레이아웃
📌 다음 단계 제안
현재 시스템은 Step 27까지 완료되었습니다. 다음 작업 후보:

구매 요청 기능 추가
재고 관리 기능
대시보드 통계 개선
다국어 지원 (베트남어/영어)
모바일 반응형 개선
백업 생성 일시: 2025-09-29
작업자: YMV ERP 개발팀
다음 작업: 사용자 요청 대기

이 백업 시점에서 YMV ERP 시스템의 지출요청서 프린트 기능은 완전히 작동하며, A4 1장에 모든 내용이 포함됩니다.