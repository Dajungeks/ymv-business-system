markdown
# YMV ERP 시스템 백업 파일 - Role 및 Position 영문 변경 완료

**백업 일시**: 2025-09-29
**작업 내용**: Role 5단계 구조 변경, Position 영문화, 지출요청서 승인 프로세스 개선, DB 상태값 통일

---

## 📊 시스템 현황

### 프로젝트 기본 정보
- **프로젝트명**: YMV 관리 프로그램 (ERP 시스템)
- **개발 언어**: Python + Streamlit
- **데이터베이스**: Supabase (PostgreSQL)
- **회사 규모**: 10인 중소기업
- **프로젝트 위치**: D:\ymv-business-system
- **현재 진행률**: Role/Position 영문 변경 완료, 지출요청서 승인 프로세스 개선 완료

### Supabase 연결 정보
SUPABASE_URL = "https://eqplgrbegwzeynnbcuep.supabase.co" SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." GitHub: https://github.com/dajungeks/ymv-business-system.git


---

## 🎯 최근 완료 작업

### 1. Role 구조 변경 (5단계)

#### 변경 전
employee, manager, admin, master (4단계)


#### 변경 후
Staff, Manager, Admin, CEO, Master (5단계)


#### 권한 체계
Staff < Manager < Admin < CEO < Master


**권한 상세:**
- **Staff**: 본인 지출요청서 작성만
- **Manager**: 본인 지출요청서 작성, 구매품 전체 조회
- **Admin**: 지출요청서 작성/관리, 직원 관리 (승인 불가)
- **CEO**: 지출요청서 승인/반려, 직원 관리, 비밀번호 관리
- **Master**: 모든 권한 (시스템 관리)

### 2. Position 영문화

#### 변경 전
사원, 주임, 대리, 과장, 부장


#### 변경 후
Staff, Junior Manager, Manager, Senior Manager, Director, CEO


### 3. 지출요청서 승인 프로세스 개선

#### 새로운 워크플로우
Admin 작성 → pending
CEO/Master 승인/반려
승인 → approved (완료)
반려 (사유 필수) → rejected
반려된 경우:
Admin 수정 → 재신청 (pending)

#### 주요 기능
- ✅ 반려 시 사유 필수 입력
- ✅ 반려된 항목 수정 기능 (Admin 본인, Master 전체)
- ✅ 재신청 버튼 (rejected → pending)
- ✅ Master 전체 권한 (모든 항목 수정/삭제)

### 4. DB 상태값 통일

#### 실행한 SQL
```sql
UPDATE expenses 
SET status = CASE 
    WHEN status = '대기중' THEN 'pending'
    WHEN status = '승인됨' THEN 'approved'
    WHEN status = '거부됨' THEN 'rejected'
    ELSE status
END;
결과
pending: 11건
approved: 15건
rejected: 0건
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
    employment_status VARCHAR DEFAULT 'active',  -- active, inactive, resigned
    hire_date DATE,
    salary NUMERIC,
    work_type VARCHAR DEFAULT 'full_time',  -- full_time, part_time, contract
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
    status VARCHAR DEFAULT '대기중',  -- pending, approved, rejected
    vendor VARCHAR,
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES employees(id),
    approval_comment TEXT,  -- 승인 의견 or 반려 사유
    receipt_number VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
📋 함수 리스트
employee_management.py
메인 함수
python
show_employee_management(load_func, save_func, update_func, delete_func, 
                        get_current_user_func, check_permission_func,
                        get_approval_status_info, calculate_statistics,
                        create_csv_download, render_print_form)
핵심 함수들
python
# 탭 렌더링
render_employee_list()          # 직원 목록
render_employee_form()          # 직원 등록/수정
render_organization_chart()     # 조직도
render_attendance_management()  # 근태 관리
render_payroll_management()     # 급여 관리 (Master, CEO만)
render_password_management()    # 비밀번호 관리 (Master, CEO만)

# 헬퍼 함수
get_positions_list()           # Position 목록 (영문)
get_departments_list()         # 부서 목록
get_managers_list()            # 관리자 목록
apply_employee_filters()       # 필터링
display_employee_table()       # 테이블 표시
validate_employee_form()       # 폼 검증
record_employee_history()      # 이력 기록
calculate_vietnam_tax()        # 베트남 세금 계산
expense_management.py
메인 함수
python
show_expense_management(load_data_func, save_data_func, update_data_func, delete_data_func,
                       get_current_user_func, get_approval_status_info_func,
                       calculate_expense_statistics_func, create_csv_download_func,
                       render_print_form_func)
핵심 함수들
python
# 탭 렌더링
render_expense_form()           # 작성/수정 (수정 모드 추가)
render_expense_list()           # 목록 (수정/재신청 버튼 추가)
render_expense_statistics()     # 통계
render_approval_management()    # 승인 관리 (CEO, Master만)

# 주요 로직
- 수정 모드: st.session_state['edit_expense'] 사용
- 재신청: rejected → pending 상태 변경
- 반려 사유 필수: approval_comment 검증
auth.py
핵심 함수들
python
class AuthManager:
    login_user()                # 로그인
    logout_user()               # 로그아웃
    get_current_user()          # 현재 사용자
    check_permission()          # 권한 체크 (Master, CEO, Admin)
    require_manager_role()      # 관리자 권한 (Master, CEO)
    change_password()           # 비밀번호 변경
main.py
메인 함수
python
main()                          # 메인 애플리케이션

# 페이지 함수들
show_dashboard()
show_expense_management_page()
show_employee_management_page()
show_product_management_page()
show_supplier_management_page()
show_customer_management_page()
show_sales_process_management_page()
show_purchase_management()
show_quotation_management_page()
show_code_management()
show_multilingual_input()

# 구매품 관리
render_purchase_form()
render_purchase_list()          # 권한 필터: Master, CEO, Admin, Manager
🔄 함수 호출 관계도
지출요청서 관리 흐름
main() → show_expense_management_page()
    ↓
show_expense_management()
    ├── render_expense_form()           # 작성/수정
    │   ├── load_data("employees")
    │   ├── save_data("expenses")       # 신규
    │   └── update_data("expenses")     # 수정
    │
    ├── render_expense_list()           # 목록
    │   ├── load_data("expenses")
    │   ├── update_data()               # 재신청
    │   ├── delete_data()               # 삭제
    │   └── render_print_form()
    │
    ├── render_expense_statistics()     # 통계
    │   └── calculate_expense_statistics()
    │
    └── render_approval_management()    # 승인 (CEO, Master)
        └── update_data()               # 승인/반려
직원 관리 흐름
main() → show_employee_management_page()
    ↓
show_employee_management()
    ├── render_employee_list()
    ├── render_employee_form()
    │   ├── get_positions_list()        # 영문 Position
    │   ├── get_departments_list()
    │   └── get_managers_list()
    │
    ├── render_organization_chart()
    ├── render_attendance_management()
    ├── render_payroll_management()     # Master, CEO만
    │   └── calculate_vietnam_tax()
    │
    └── render_password_management()    # Master, CEO만
        └── update_data("employees")
승인 프로세스 흐름
Admin 작성
    ↓ (save_data)
status = 'pending'
    ↓
CEO/Master 검토 (render_approval_management)
    ↓
승인 선택
    ├── 승인 → update_data(status='approved')
    │
    └── 반려 → approval_comment 필수 체크
              → update_data(status='rejected', approval_comment='사유')
                  ↓
              Admin 수정 (render_expense_form with edit_expense)
                  ↓
              재신청 버튼 → update_data(status='pending')
💻 수정된 파일 목록
1. employee_management.py
수정 내용:

get_positions_list(): 영문 Position 반환
render_employee_form(): Role 5단계 선택, 호환성 매핑 추가
display_employee_table(): Role 영문 표시
render_password_management(): 권한 체크 (Master, CEO)
render_payroll_management(): 권한 체크 (Master, CEO)
2. expense_management.py
수정 내용:

render_expense_form(): 수정 모드 지원 (edit_expense)
render_expense_list():
Master 전체 권한
Admin 반려 항목 수정
재신청 버튼
권한별 수정/삭제 로직
render_approval_management():
CEO, Master만 승인
반려 시 사유 필수
3. auth.py
수정 내용:

check_permission(): Master, CEO, Admin 권한 체크
require_manager_role(): Master, CEO만
4. main.py
수정 내용:

show_purchase_management(): 기본 Role 'Staff'
render_purchase_list(): Master, CEO, Admin, Manager 전체 조회
🔧 주요 코드 변경 사항
employee_management.py
get_positions_list 함수
python
def get_positions_list(load_func) -> List[str]:
    try:
        positions = load_func("positions", filters={"is_active": True})
        return [pos['position_name'] for pos in positions] if positions else \
               ["Staff", "Junior Manager", "Manager", "Senior Manager", "Director", "CEO"]
    except:
        return ["Staff", "Junior Manager", "Manager", "Senior Manager", "Director", "CEO"]
Role 호환성 매핑
python
# 구버전 Role 호환
role_mapping = {
    'employee': 'Staff',
    'manager': 'Manager',
    'admin': 'Admin',
    'ceo': 'CEO',
    'master': 'Master'
}
current_role = role_mapping.get(current_role.lower(), current_role)
expense_management.py
수정 모드 지원
python
# 세션에서 수정 대상 가져오기
edit_expense = st.session_state.get('edit_expense', None)

if edit_expense:
    st.info(f"📝 지출요청서 수정 모드 (ID: {edit_expense.get('id')})")
    # 기존 데이터로 폼 채우기
재신청 버튼
python
if expense_status == 'rejected' and expense.get('requester') == current_user_id:
    if st.button("🔄 재신청", key=f"resubmit_{expense.get('id')}"):
        resubmit_data = {
            'id': expense.get('id'),
            'status': 'pending',
            'approval_comment': None,
            'approved_by': None,
            'approved_at': None,
            'updated_at': datetime.now().isoformat()
        }
        update_data_func("expenses", resubmit_data, "id")
반려 사유 필수
python
if st.button("❌ 반려", key=f"reject_{expense.get('id')}"):
    if not approval_comment or not approval_comment.strip():
        st.error("⚠️ 반려 사유를 반드시 입력해주세요!")
    else:
        # 반려 처리
📌 진행 사항
완료된 작업
 Role 5단계 구조 변경 (Staff ~ Master)
 Position 영문화
 지출요청서 승인 프로세스 개선
 반려 사유 필수 입력
 반려된 항목 수정 기능
 재신청 버튼 구현
 Master 전체 권한 적용
 DB 상태값 영문 통일
 비밀번호 관리 권한 수정
테스트 완료
 직원 등록 (Role 5단계)
 Position 영문 표시
 비밀번호 변경 (Master/CEO, 본인)
 지출요청서 작성/수정
 승인/반려 프로세스
 재신청 기능
 DB 상태값 통일
🎯 다음 단계
우선순위 1: 프린트 기능 개선 (대기 중)
목표: 지출요청서 프린트 양식 개선

 회사 정보 헤더 추가
 결재란 추가
 A4 용지 최적화
 PDF 다운로드 옵션
우선순위 2: 코드별 발주 시스템 (Step 25)
목표: 현실적 코드별 발주 시스템 구현

 process_item_breakdown 테이블 생성
 코드별 분할 입력 UI
 재고 확인 로직
 내부/외주 발주 처리
🤖 AI 추가 판단 사항
시스템 안정성
현재 상태: 안정적
권한 체계: 명확하게 정의됨
DB 일관성: 상태값 통일로 개선됨
개선 필요 영역
프린트 기능: helpers.py의 PrintFormGenerator 개선 필요
에러 처리: 일부 함수에 try-except 추가 권장
로깅: 중요 작업에 로그 기록 추가 고려
호환성 고려사항
기존 DB에 소문자 Role이 있을 경우 role_mapping 사용
신규 데이터는 모두 영문 대문자 시작 (Staff, Manager 등)
점진적 마이그레이션 전략 유지
📝 main.py 함수 호출 방식
초기화 순서
python
1. st.set_page_config()           # 페이지 설정 (최우선)
2. init_supabase()                # Supabase 클라이언트 (@cache_resource)
3. init_managers()                # DB, Auth 매니저 (@cache_resource)
4. main()                         # 메인 애플리케이션 시작
로그인 플로우
python
main()
    ↓
if not auth_manager.is_logged_in():
    show_login_page()
        ↓
    auth_manager.login_user(employee_id, password)
        ↓
    st.rerun()
페이지 라우팅
python
main() → st.session_state.current_page 확인
    ├── "대시보드" → show_dashboard()
    ├── "직원 관리" → show_employee_management_page()
    ├── "지출 요청서" → show_expense_management_page()
    ├── "구매품 관리" → show_purchase_management()
    └── ...
DB 함수 전달 패턴
python
# 모든 컴포넌트에 일관된 방식으로 전달
show_component(
    db_operations.load_data,      # 조회
    db_operations.save_data,      # 저장
    db_operations.update_data,    # 수정
    db_operations.delete_data,    # 삭제
    auth_manager.get_current_user,     # 현재 사용자
    auth_manager.check_permission,     # 권한 체크
    get_approval_status_info,          # 상태 정보
    calculate_expense_statistics,      # 통계 계산
    create_csv_download,               # CSV 생성
    render_print_form                  # 프린트
)
세션 상태 관리
python
st.session_state.logged_in          # 로그인 상태
st.session_state.user_info          # 사용자 정보
st.session_state.current_page       # 현재 페이지
st.session_state.edit_expense       # 수정 중인 지출요청서
st.session_state.today              # 오늘 날짜
st.session_state.now                # 현재 시간
🔧 문제 해결 이력
1. 지출요청서 데이터 안 보이는 문제
원인: DB 상태값 한글 vs 코드 영문 불일치 해결: SQL로 DB 상태값 영문 통일

sql
UPDATE expenses SET status = CASE 
    WHEN status = '대기중' THEN 'pending'
    WHEN status = '승인됨' THEN 'approved'
    WHEN status = '거부됨' THEN 'rejected'
    ELSE status END;
2. 관리자 비밀번호 변경 안 되는 문제
원인: update_func 호출 시 id_field 파라미터 누락 해결: update_func("employees", update_data, "id") 3번째 파라미터 추가

📌 재개 방법
필수 업로드 파일
규칙 파일: program_development_rules - V10 Final.txt
이 백업 파일: ymv_backup_2025-09-29.md
재개 명령어
"규칙 V10 + 이 백업 기준으로 개발 이어가줘"
즉시 시작 가능한 상태
Role 5단계 구조 완료
Position 영문화 완료
지출요청서 승인 프로세스 개선 완료
DB 상태값 통일 완료
모든 파일 수정 완료
시스템 안정적 작동
백업 생성 일시: 2025-09-29 작업자: YMV ERP 개발팀 다음 작업 추천: 프린트 기능 개선

이 백업 시점에서 YMV ERP 시스템은 Role/Position 영문 변경, 지출요청서 승인 프로세스 개선, DB 통일이 완료된 안정적인 상태입니다.

