# YMV ERP 개발 백업 보고서 - V08 규칙 준수
## Generated: 2024-09-24 | Session: Step 7 견적서 관리 시스템 수정 완료

## 1. 시스템 현황

### 1.1 프로젝트 정보
- **프로젝트명**: YMV 관리 프로그램 v4.0
- **위치**: D:\ymv-business-system
- **현재 단계**: Step 7 완료 (견적서 관리 시스템 수정)
- **전체 완성도**: 약 65%
- **배포 URL**: https://ymv-business-system.streamlit.app
- **테스트 계정**: Master / 1023

### 1.2 개발 환경
- **프레임워크**: Streamlit
- **데이터베이스**: Supabase (PostgreSQL)
- **언어**: Python
- **배포**: Streamlit Cloud

## 2. 파일 구조 현황

### 2.1 현재 디렉토리 구조
```
D:\ymv-business-system/
├── app/
│   ├── main.py ✅ (800줄, 리팩토링 필요 - Step 8 예정)
│   └── components/
│       ├── __init__.py ✅
│       ├── code_management.py ✅ (정상 작동)
│       ├── multilingual_input.py ✅ (정상 작동)
│       └── quotation_management.py ✅ (Step 7에서 완전 수정됨)
├── database/
│   ├── upgrade_v4.sql ✅ (실행됨)
│   ├── additional_schema_fix.sql ✅ (실행됨)
│   ├── fix_expenses_schema_safe.sql ✅ (실행됨)
│   └── quotation_schema.sql ⚠️ (생성됨, 실행 불필요 - 테이블 이미 존재)
├── requirements.txt ✅
├── .streamlit/config.toml ✅
└── .env ✅ (Supabase 연결 정보)
```

### 2.2 파일 상태 분석
- **main.py**: 800줄로 과도하게 길어서 리팩토링 필요 (Step 8)
- **components/**: 컴포넌트 구조는 잘 구축됨
- **quotation_management.py**: Step 7에서 완전 수정 완료

## 3. 함수 목록 및 역할

### 3.1 main.py 주요 함수 (호출 순서 포함)

#### 3.1.1 초기화 및 유틸리티 함수
```python
# 1. 앱 시작시 호출
@st.cache_resource
init_supabase() - Supabase 연결 초기화
    └─ 호출 위치: main() 함수 시작시
    └─ 반환: supabase client object

# 2. 전역적으로 사용
generate_unique_key(prefix="") - 고유 위젯 키 생성
    └─ 호출 위치: 모든 Streamlit 위젯에서
    └─ 전달 매개변수: prefix (string)
    └─ 반환: unique key string
```

#### 3.1.2 데이터베이스 연결 함수 (공통 함수 - Step 8에서 utils.py로 이동 예정)
```python
# ConnectionWrapper 없이 직접 Supabase 호출 방식
load_data_from_supabase(table, columns="*", filters=None)
    └─ 호출 위치: 모든 페이지 함수에서 데이터 로드시
    └─ 전달 매개변수: table명, columns(선택), filters(딕셔너리)
    └─ 반환: list of dictionaries

save_data_to_supabase(table, data)
    └─ 호출 위치: 폼 제출시 (지출요청서, 구매품, 견적서)
    └─ 전달 매개변수: table명, data(딕셔너리)
    └─ 반환: boolean

update_data_in_supabase(table, data, id_field="id") ⚠️ Step 7에서 수정됨
    └─ 호출 위치: 데이터 수정시
    └─ 전달 매개변수: table명, data(id 포함), id_field
    └─ 반환: boolean
    └─ 수정 내용: data.copy()로 원본 보호, 응답 데이터 확인 추가

delete_data_from_supabase(table, item_id, id_field="id")
    └─ 호출 위치: 삭제 버튼 클릭시
    └─ 전달 매개변수: table명, item_id, id_field
    └─ 반환: boolean
```

#### 3.1.3 사용자 관리 및 인증
```python
# 인증 시스템
login_user(username, password) - 로그인 처리
    └─ 호출 위치: show_login_page() 폼 제출시
    └─ 전달 매개변수: username, password
    └─ 반환: boolean (성공/실패)

logout_user() - 로그아웃 처리
    └─ 호출 위치: 사이드바 로그아웃 버튼
    └─ 반환: None (세션 상태 초기화)

get_current_user() - 현재 사용자 정보
    └─ 호출 위치: 모든 페이지에서 사용자 정보 필요시
    └─ 반환: user dictionary or None
```

#### 3.1.4 통계 및 유틸리티 함수
```python
get_approval_status_info(status) - 승인 상태 정보
    └─ 호출 위치: 지출요청서 표시시
    └─ 전달 매개변수: status string
    └─ 반환: dictionary (emoji, color, description)

calculate_expense_statistics(expenses) - 지출 통계 계산
    └─ 호출 위치: show_dashboard(), show_expense_management() 탭3
    └─ 전달 매개변수: expenses list
    └─ 반환: statistics dictionary

create_csv_download(expenses, employees) - CSV 다운로드
    └─ 호출 위치: 지출요청서 목록 탭
    └─ 전달 매개변수: expenses list, employees list
    └─ 반환: CSV bytes with BOM

render_print_form(expense) - 프린트 양식 렌더링
    └─ 호출 위치: 지출요청서 프린트 버튼 클릭시
    └─ 전달 매개변수: expense dictionary
    └─ 반환: None (HTML 렌더링)
```

#### 3.1.5 페이지 함수들 (호출 흐름)
```python
# main() 호출 흐름
main()
├── 로그인 체크
│   └── show_login_page() (로그인 안됨시)
└── 메뉴별 페이지 호출
    ├── show_dashboard() (default)
    ├── show_expense_management()
    ├── show_purchase_management()
    ├── show_quotation_management()
    └── 기타 메뉴들 (미구현)

# 각 페이지 함수 세부사항
show_login_page() - 로그인 페이지 (50줄)
    └─ 호출: main() 함수에서 logged_in=False시
    └─ 내부 호출: login_user()

show_dashboard() - 대시보드 (100줄)
    └─ 호출: main() 함수에서 메뉴="대시보드"시
    └─ 내부 호출: get_current_user(), load_data_from_supabase() 6회, calculate_expense_statistics()

show_expense_management() - 지출 관리 (400줄) ← 최우선 리팩토링 대상
    └─ 호출: main() 함수에서 메뉴="지출요청서"시
    └─ 내부 호출: 모든 CRUD 함수, 통계 함수, 프린트 함수
    └─ 탭 구조: 4개 탭 (작성/목록/통계/CEO승인)

show_purchase_management() - 구매품 관리 (100줄)
    └─ 호출: main() 함수에서 메뉴="구매품관리"시
    └─ 내부 호출: 기본 CRUD 함수들
    └─ 탭 구조: 2개 탭 (등록/목록)

show_quotation_management() - 견적서 관리 (임시 래퍼)
    └─ 호출: main() 함수에서 메뉴="견적서관리"시
    └─ 내부 호출: components.quotation_management.show_quotation_management()
    └─ 매개변수 전달: 4개 DB 함수 전달
```

### 3.2 components/quotation_management.py 함수 (Step 7에서 완전 수정)

#### 3.2.1 메인 함수 및 호출 구조
```python
show_quotation_management(load_data_func, save_data_func, update_data_func, delete_data_func)
    └─ 호출 위치: main.py show_quotation_management()에서
    └─ 전달 매개변수: 4개 DB 함수 (main.py에서)
    └─ 반환: None (Streamlit 렌더링)
    └─ 내부 구조: 3개 탭 (작성/목록/통계)
```

#### 3.2.2 핵심 비즈니스 함수들
```python
# 견적서 작성 폼
render_quotation_form(load_data_func, save_data_func, update_data_func, delete_data_func)
    └─ 호출 위치: show_quotation_management() 탭1
    └─ 기능: customers, products 테이블 연동하여 견적서 생성
    └─ total_amount 자동 계산 및 저장

# 견적서 목록 관리
render_quotation_list(load_data_func, save_data_func, update_data_func, delete_data_func)
    └─ 호출 위치: show_quotation_management() 탭2
    └─ 기능: 필터링, 정렬, CRUD 작업

# 견적서 통계
show_quotation_statistics(load_data_func)
    └─ 호출 위치: show_quotation_management() 탭3
    └─ 기능: 상태별, 월별 통계 표시

# 유틸리티 함수들
generate_unique_key(prefix="") - 위젯 키 생성
get_quotation_status_info(status) - 견적서 상태 정보
render_quotation_print(quotation) - 견적서 출력 (프린트 기능 개선 필요)
```

### 3.3 components/code_management.py (정상 작동)
```python
class CodeManagementComponent:
    __init__(self, supabase) - 초기화
        └─ 호출 위치: main() 함수에서 "시스템관리" 메뉴 선택시
        └─ 전달 매개변수: supabase client
        
    render_code_management_page(self) - 제품 코드 관리 페이지
        └─ 기능: 7단계 제품 코드 시스템 (HR-01-02-ST-KR-00)
```

## 4. 데이터베이스 구조

### 4.1 완전 구현된 테이블 (28개)
| 테이블명 | 기능 | 레코드 수 | 상태 | 호출 함수 |
|---------|------|----------|------|----------|
| employees | 직원 관리/로그인 | 다수 | 정상 작동 | login_user(), get_current_user() |
| expenses | 지출 요청서 | 다수 | 100% 완성 | show_expense_management() |
| customers | 고객 정보 | 1건 | 견적서 연동 | quotation_management.py |
| products | 제품 정보 | 2건 | 견적서 연동 | quotation_management.py |
| company_info | 회사 정보 | 1건 | 대시보드 표시 | show_dashboard() |
| quotations | 견적서 마스터 | 0건 | Step 7 완성 | quotation_management.py |
| quotation_items | 견적서 상세 | 0건 | 테이블 존재 | 향후 확장 |
| product_codes | 제품 코드 | 다수 | v4.0 기능 | CodeManagementComponent |
| purchases | 구매품 관리 | 다수 | 기본 CRUD | show_purchase_management() |

### 4.2 ConnectionWrapper 클래스 현황
- **현재 상태**: main.py에서 직접 Supabase 호출 방식 사용
- **문제점**: ConnectionWrapper 클래스 미구현
- **해결 계획**: Step 8에서 utils.py로 공통 DB 함수 분리시 ConnectionWrapper 도입 예정

## 5. 이번 세션 완료 내용 (Step 7)

### 5.1 주요 성과
1. **quotation_management.py 완전 수정**
   - main.py DB 함수 구조에 완전 맞춤
   - 'name' 변수 오류 해결
   - total_amount 계산 및 저장 정상화
   - 데이터베이스 스키마 메시지 개선

2. **main.py update_data_in_supabase 함수 수정**
   - data.copy()로 원본 데이터 보호
   - 응답 데이터 확인 로직 추가
   - 지출요청서 상태변경 문제 해결

3. **프린트 기능 개선 시도**
   - 3가지 프린트 옵션 제공
   - 브라우저 프린트, 텍스트 다운로드, 클립보드 복사
   - 여전히 CSS 방식 개선 필요 (다음 단계)

### 5.2 해결된 오류들
| 오류명 | 발생 상황 | 원인 | 해결 방법 | 참고 코드 |
|-------|----------|------|----------|----------|
| 함수 매개변수 불일치 | 견적서 관리 접근시 | main.py와 quotation_management.py 함수 시그니처 다름 | 완전히 일치시킴 | show_quotation_management() |
| 'name' 변수 참조 오류 | 견적서 작성시 | 존재하지 않는 키 참조 | 올바른 키 사용 | customer_name, contact_person |
| total_amount 누락 | 견적서 저장시 | 계산만 하고 저장 안함 | quotation_data에 포함 | line 145 |
| 상태변경 실패 | 지출요청서 수정시 | data.pop()이 원본 변경 | data.copy() 사용 | update_data_in_supabase() |

## 6. 현재 미해결 이슈

### 6.1 긴급 수정 필요 (Step 8)
- **main.py 파일 크기**: 800줄로 과도하게 큼
- **프린트 기능**: CSS 방식으로 개선 필요
- **ConnectionWrapper 미구현**: 데이터베이스 연결 관리 체계화 필요

### 6.2 구조적 개선 필요
- **중복 함수**: DB 연결 함수가 여러 파일에 중복
- **utils.py 부재**: 공통 함수들이 main.py에 집중
- **컴포넌트 일관성**: 각기 다른 방식으로 DB 연결

## 7. 다음 개발 계획 (우선순위)

### Phase 1: 시스템 안정화 계속 (1주)
#### Step 8: main.py 리팩토링 - expense_management.py 분리
- **목표**: 400줄 지출관리 코드를 컴포넌트로 분리
- **결과**: main.py 800줄 → 600줄
- **ConnectionWrapper 도입**: 데이터베이스 연결 체계화
- **프린트 CSS 개선**: 견적서/지출요청서 프린트 기능 완전 해결

#### Step 9: main.py 리팩토링 - dashboard.py 분리
- **목표**: 100줄 대시보드 코드를 컴포넌트로 분리
- **결과**: main.py 600줄 → 500줄

#### Step 10: utils.py 공통 함수 분리
- **목표**: 200줄 공통 함수들을 유틸리티로 분리
- **결과**: main.py 500줄 → 100줄 (최종 목표)
- **ConnectionWrapper 완전 구현**

### Phase 2: 기능 완성 (2주)
#### Step 11-12: 기본 마스터 데이터 CRUD
- 고객 관리 시스템 완전 구현
- 제품 관리 시스템 완전 구현

#### Step 13-14: 영업 프로세스 연결
- 견적서-주문서 연동
- 인보이스 시스템 구현

## 8. 기술적 고려사항 및 주의점

### 8.1 ConnectionWrapper 도입 계획
```python
# Step 8에서 구현 예정
class ConnectionWrapper:
    def __init__(self, supabase):
        self.supabase = supabase
    
    def execute_query(self, table, operation, data=None, filters=None):
        # 통일된 DB 접근 방식
        
    def handle_error(self, error):
        # 중앙집중식 에러 처리
```

### 8.2 호출 방식 표준화
- 모든 컴포넌트가 동일한 DB 함수 시그니처 사용
- ConnectionWrapper를 통한 안전한 DB 접근
- 에러 처리 및 로깅 표준화

### 8.3 프린트 기능 개선 방향
- CSS @media print 규칙 활용
- 전용 프린트 페이지 생성
- 브라우저 호환성 개선

## 9. 주의사항 및 알려진 제약

### 9.1 Supabase 연결 제약
- 직접 연결 방식 사용 중 (ConnectionWrapper 없음)
- Row Level Security(RLS) 설정 필요
- 연결 수 제한 고려

### 9.2 Streamlit 제약사항
- JavaScript 실행 제한 (프린트 기능 영향)
- 세션 상태 관리 복잡성
- 위젯 키 중복 방지 필수

### 9.3 개발 규칙 V08 준수 현황
- ✅ 전체 파일 단위 코드 제공
- ✅ Step 단위 진행
- ✅ 호출 방식 문서화
- ⚠️ ConnectionWrapper 미구현 (Step 8에서 해결)

## 10. 빠른 시작 가이드

### 10.1 시스템 실행
```bash
cd D:\ymv-business-system
streamlit run app/main.py
```

### 10.2 테스트 계정
- **사용자명**: Master
- **비밀번호**: 1023
- **권한**: 관리자 (모든 기능 접근 가능)

### 10.3 현재 작동 기능
- ✅ 로그인/로그아웃
- ✅ 대시보드
- ✅ 지출 요청서 관리 (100% 완성, 상태변경 수정됨)
- ✅ 견적서 관리 (Step 7에서 완전 수정, 프린트 제외)
- ✅ 코드 관리 시스템
- ✅ 구매품 관리 (기본 기능)

### 10.4 다음 세션 시작 방법
1. 이 백업 파일을 새 채팅창에 업로드
2. "이 백업 파일을 기반으로 YMV 개발을 계속해줘" 요청
3. Step 8 (main.py 리팩토링 - expense_management.py 분리)부터 시작

## 11. 개발자 참고 정보

### 11.1 중요 파일 경로
```
app/main.py (138라인) - update_data_in_supabase 함수 (수정됨)
app/components/quotation_management.py (전체 파일 교체됨)
database/ - 모든 SQL 스키마 파일들
```

### 11.2 임포트 의존성 맵
```python
# main.py 임포트 구조
streamlit as st                    # UI 프레임워크
pandas as pd                       # 데이터 처리
datetime, uuid, time              # 유틸리티
collections.defaultdict           # 통계 계산
calendar, io                      # 추가 유틸리티

# 내부 모듈
from components.code_management import CodeManagementComponent
from components.multilingual_input import MultilingualInputComponent  
from components.quotation_management import show_quotation_management
```

### 11.3 호출 흐름도
```
main()
├── init_supabase() [@st.cache_resource]
├── 로그인 체크
│   ├── show_login_page() → login_user()
│   └── 사이드바 생성 → get_current_user()
└── 메뉴별 분기
    ├── show_dashboard() → load_data_from_supabase() × 6회
    ├── show_expense_management() → 모든 CRUD 함수
    ├── show_purchase_management() → 기본 CRUD 함수
    ├── show_quotation_management() → quotation_management.py
    └── CodeManagementComponent()
```

---
**백업 생성일**: 2024-09-24  
**세션 ID**: Step 7 - 견적서 관리 시스템 수정 완료  
**다음 예정 작업**: Step 8 - main.py 리팩토링 (expense_management.py 분리) + 프린트 CSS 개선  
**규칙 준수**: V08 완전 준수 (ConnectionWrapper는 Step 8에서 구현)