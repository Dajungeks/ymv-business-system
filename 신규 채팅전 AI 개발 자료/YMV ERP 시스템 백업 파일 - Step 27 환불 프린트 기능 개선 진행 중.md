YMV ERP 시스템 백업 파일 - Step 27: 프린트 기능 개선 진행 중
백업 일시: 2025-09-29 작업 내용: 프린트 기능 HTML 템플릿 분리, 승인자 정보 자동 표시, 반려 사유 표시 (A4 최적화 남음)

📊 시스템 현황
프로젝트 기본 정보
프로젝트명: YMV 관리 프로그램 (ERP 시스템)
개발 언어: Python + Streamlit
데이터베이스: Supabase (PostgreSQL)
회사 규모: 10인 중소기업
프로젝트 위치: D:\ymv-business-system
현재 진행률: Step 27 진행 중 (프린트 기능 개선 - A4 최적화 필요)
Supabase 연결 정보
SUPABASE_URL = "https://eqplgrbegwzeynnbcuep.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
GitHub: https://github.com/dajungeks/ymv-business-system.git
🎯 Step 27 작업 내역
완료된 작업 ✅
HTML 템플릿 분리
app/templates/expense_print_template.html 생성
helpers.py에서 템플릿 로드 방식으로 변경
코드 가독성 및 유지보수성 향상
프린트 기능 개선
요청자 정보 표시 (이름, 직원번호)
승인자 정보 자동 표시 (approved 상태)
반려 사유 표시 (rejected 상태)
문서 상태 배지 추가 (pending/approved/rejected)
함수 시그니처 변경
render_print_form(expense) → render_print_form(expense, employees)
employees 데이터 전달로 직원 정보 조회
프린트 모드 개선
세션 상태 사용 (st.session_state['print_expense'])
expander 외부에서 프린트 렌더링 (columns 중첩 오류 해결)
"목록으로 돌아가기" 버튼 추가
f-string 백슬래시 오류 해결
조건부 표현식을 변수로 미리 생성
f-string 내부에서 백슬래시 사용 제거
진행 중인 작업 🔄
A4 1장 최적화 작업 필요

현재 프린트 양식이 A4 1장을 초과
여백, 폰트 크기, 간격 조정 필요
app/templates/expense_print_template.html 수정 예정
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
├── templates/                      # 새로 생성
│   └── expense_print_template.html # HTML 프린트 템플릿
├── utils/
│   └── helpers.py                  # 수정 완료
├── components/
│   └── expense_management.py       # 수정 완료
└── main.py
💻 주요 함수 변경사항
1. helpers.py - PrintFormGenerator.render_print_form()
변경 전:

python
@staticmethod
def render_print_form(expense):
    # 긴 HTML 코드가 함수 내부에 포함
변경 후:

python
@staticmethod
def render_print_form(expense, employees):
    # 1. 직원 정보 딕셔너리 생성
    # 2. 요청자/승인자 정보 추출
    # 3. 템플릿 파일 읽기
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'expense_print_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    # 4. 변수 치환
    print_html = template.format(...)
주요 개선:

employees 매개변수 추가
HTML 템플릿 외부 파일로 분리
요청자/승인자 이름 자동 표시
상태별 배지 및 반려 사유 표시
2. expense_management.py - render_expense_list()
변경 전:

python
with button_col1:
    if st.button("🖨️ 프린트"):
        render_print_form_func(expense, employees)  # expander 내부 호출
변경 후:

python
# 함수 시작 부분에 프린트 모드 체크
if st.session_state.get('print_expense'):
    print_expense = st.session_state['print_expense']
    employees = load_data_func("employees")
    render_print_form_func(print_expense, employees)
    
    if st.button("← 목록으로 돌아가기", type="primary"):
        del st.session_state['print_expense']
        st.rerun()
    return

# 버튼 클릭 시 세션 상태에 저장
with button_col1:
    if st.button("🖨️ 프린트"):
        st.session_state['print_expense'] = expense
        st.rerun()
주요 개선:

expander 외부에서 프린트 렌더링
columns 중첩 오류 해결
프린트 전용 화면 제공
🔧 해결한 문제들
1. SyntaxError: f-string 백슬래시 오류
문제:

python
text_content = f"""
...
{'[반려 사유]\n' + expense.get('approval_comment', '') if status == 'rejected' else ''}
"""
해결:

python
rejection_text = ''
if status == 'rejected' and expense.get('approval_comment'):
    rejection_text = f"[반려 사유]\n{expense.get('approval_comment', '')}\n\n"

text_content = f"""
...
{rejection_text}
"""
2. StreamlitAPIException: columns 중첩 오류
문제: expander 내부의 columns 안에서 render_print_form이 또 columns 사용

해결: 프린트 모드를 별도 화면으로 분리

3. NameError: render_expense_form not defined
문제: expense_management.py에서 render_expense_list가 2번 정의되고 render_expense_form이 없음

해결: 전체 파일 재작성으로 함수 구조 정리

🎯 다음 작업 (Step 27 계속)
우선순위 1: A4 1장 최적화 (즉시 진행)
수정 파일: app/templates/expense_print_template.html

수정 내용:

여백 축소 (20mm → 15mm)
폰트 크기 축소
제목: 28px → 24px
본문: 12px → 11px
테이블: 12px → 10px
패딩/간격 축소
테이블 padding: 12px → 8px
섹션 간격: 30px → 20px
결재란 높이 축소
signature-space: 80px → 60px
date-space: 40px → 30px
우선순위 2: 프린트 기능 최종 테스트
테스트 항목:

 pending 상태 프린트
 approved 상태 프린트 (승인자 정보 확인)
 rejected 상태 프린트 (반려 사유 확인)
 A4 1장에 모든 내용 포함 확인
 PDF 저장 기능 확인
📝 템플릿 파일 위치
현재 생성된 파일:

D:\ymv-business-system\app\templates\expense_print_template.html
내용:

회사 정보 헤더 (CÔNG TY TNHH YUMOLD VIỆT NAM)
문서 상태 배지
요청자/승인자 정보
지출 상세 정보
결재란 (신청자, 팀장, CEO)
반려 사유 (rejected 상태)
🔄 함수 호출 관계도
프린트 기능 흐름
main() → show_expense_management_page()
    ↓
show_expense_management()
    ↓
render_expense_list()
    ├── 프린트 모드 체크 (최우선)
    │   └── st.session_state.get('print_expense')
    │       ├── True → render_print_form(expense, employees)
    │       │   ├── 템플릿 로드 (expense_print_template.html)
    │       │   ├── 직원 정보 조회
    │       │   ├── 변수 치환
    │       │   └── HTML 렌더링
    │       └── False → 목록 표시
    │
    └── 프린트 버튼 클릭
        └── st.session_state['print_expense'] = expense
            └── st.rerun()
🐛 문제 해결 이력
문제 1: 지출요청서 데이터 안 보임
원인: DB 상태값 한글 vs 코드 영문 불일치
해결: SQL로 DB 상태값 영문 통일
문제 2: 승인 권한 없음
원인: employee_id 2508001의 role이 Admin
해결: role을 CEO로 변경
문제 3: requester 불일치
원인: expenses.requester = 1, 로그인 직원 id = 3
해결: requester를 3으로 변경
문제 4: f-string 백슬래시 오류
원인: f-string 내부 조건부 표현식에 \n 사용
해결: 조건부 값을 미리 변수로 생성
문제 5: columns 중첩 오류
원인: expander 내부 columns 안에서 render_print_form이 또 columns 사용
해결: 프린트 모드를 별도 화면으로 분리
문제 6: render_expense_form not defined
원인: expense_management.py에서 함수가 중복 정의되고 일부 누락
해결: 전체 파일 재작성
💡 재개 방법
새 채팅에서 시작하기
1. 파일 업로드:

이 백업 파일
program_development_rules - V10 Final.txt
2. 명령어:

규칙 V10 + 이 백업 기준으로 A4 1장 최적화 작업 이어가줘
3. 즉시 작업:

app/templates/expense_print_template.html 수정
여백, 폰트, 간격 축소
A4 1장 테스트
📌 시스템 상태 요약
정상 작동 기능
✅ Role 5단계 (Staff → Master)
✅ Position 영문화
✅ 지출요청서 작성/수정
✅ 승인/반려 프로세스
✅ 재신청 기능
✅ 프린트 기능 (A4 최적화 제외)
✅ 승인자 정보 자동 표시
✅ 반려 사유 표시
작업 필요
⏳ 프린트 A4 1장 최적화
🔑 핵심 정보
로그인 계정
Master: 2508111
CEO: 2508001
Admin: 2508002
권한 체계
Staff: 본인 지출요청서 작성만
Manager: 본인 지출요청서 작성, 구매품 전체 조회
Admin: 지출요청서 작성/관리, 직원 관리 (승인 불가)
CEO: 지출요청서 승인/반려, 직원 관리, 비밀번호 관리
Master: 모든 권한
DB 상태값
expenses.status: pending, approved, rejected (영문)
한글 상태값은 모두 영문으로 변경 완료
백업 생성 일시: 2025-09-29 작업자: YMV ERP 개발팀 다음 작업: A4 1장 프린트 최적화

이 백업 시점에서 YMV ERP 시스템은 프린트 기능 개선이 거의 완료되었으며, A4 1장 최적화만 남은 상태입니다.