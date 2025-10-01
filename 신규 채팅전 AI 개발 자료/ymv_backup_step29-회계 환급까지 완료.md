YVM ERP 시스템 백업 파일 (V1.0)
백업 날짜: 2025-10-01
프로젝트: YVM Business Management System
마지막 작업: 화던 발행 확인 기능 추가 및 용어 변경

📋 시스템 현황
주요 기능
지출 요청서 관리
지출요청서 작성/수정
목록 조회 (테이블형)
승인 관리 (CEO/Master)
화던 발행 확인 (Admin/CEO/Master)
통계 대시보드
환급 관리
환급 대기 목록 (프린트)
프린트 완료 목록 (최종 환급 처리)
최종 완료 내역
🗂️ 파일 구조
app/
├── main.py
├── components/
│   ├── expense_management.py (수정 완료)
│   ├── reimbursement_management.py (수정 완료)
│   ├── document_number.py
│   └── accounting_management.py (사용 안 함 - 제거 예정)
├── templates/
│   └── reimbursement_print_template.html
└── database/
📊 데이터베이스 구조
expenses 테이블 주요 필드
필드명	타입	설명
id	int	고유 ID
document_number	string	문서번호 (EXP-YYMMDD-XXX)
requester	int	요청자 ID (employees.id)
department	string	부서
expense_date	date	지출일
expense_type	string	지출 유형
amount	decimal	금액
currency	string	통화 (VND/USD/KRW)
payment_method	string	결제 방법
description	text	지출 내역
status	string	승인 상태 (pending/approved/rejected)
approved_by	int	승인자 ID
approved_at	datetime	승인 시간
approval_comment	text	승인/반려 의견
accounting_confirmed	boolean	화던 발행 확인 여부
accounting_confirmed_by	int	화던 확인자 ID
accounting_confirmed_at	datetime	화던 확인 시간
reimbursement_status	string	환급 상태 (pending/printed/completed/not_required)
reimbursement_document_number	string	환급 문서번호 (PAY-YYMMDD-XXX)
reimbursement_amount	decimal	환급 금액
reimbursed_by	int	환급 처리자 ID
reimbursed_at	datetime	환급 완료 시간
created_at	datetime	생성 시간
updated_at	datetime	수정 시간
🔄 전체 프로세스 흐름
[1단계: 지출 요청서 작성]
├─ 직원이 작성
├─ status: pending
└─ document_number: EXP-YYMMDD-XXX 자동 생성

↓

[2단계: 승인 관리]
├─ CEO/Master가 승인/반려
├─ 승인: status → approved
├─ 반려: status → rejected
└─ 반려 시: 수정 후 재신청 가능

↓ (승인된 경우만)

[3단계: 화던 발행 확인 (Hóa đơn)]
├─ Admin/CEO/Master가 확인
├─ accounting_confirmed: true
└─ 결제 방법에 따라 환급 상태 자동 설정:
    ├─ 법인카드: reimbursement_status → not_required
    └─ 기타: reimbursement_status → pending

↓ (환급 필요한 경우만)

[4단계: 환급 대기]
├─ 환급 필요 항목 표시
├─ 프린트 버튼 → 문서번호 생성 (PAY-YYMMDD-XXX)
└─ reimbursement_status: pending → printed

↓

[5단계: 프린트 완료]
├─ 실제 현금 지급
├─ 최종 환급 완료 버튼
└─ reimbursement_status: printed → completed

↓

[6단계: 최종 완료]
└─ 완료 내역 조회 (읽기 전용)
🔑 함수 리스트
expense_management.py
show_expense_management()
메인 함수
탭 구성 및 권한 체크
호출: main.py → show_expense_management_page()
generate_document_number(load_data_func)
지출요청서 문서번호 생성 (EXP-YYMMDD-XXX)
입력: load_data_func
출력: 문서번호 문자열
render_expense_form()
지출요청서 작성/수정 폼
신규 작성 또는 수정 모드
render_expense_list()
지출요청서 목록 표시 (테이블형)
필터링, 정렬, 상세보기
render_invoice_check_tab()
화던 발행 확인 탭
직원별 그룹핑, 다중 선택
confirm_invoice_expense(expense_id, user_id, update_data_func, load_data_func)
화던 발행 확인 처리
환급 상태 자동 설정
입력: expense_id, user_id, update_data_func, load_data_func
출력: True/False
render_expense_statistics()
지출 통계 대시보드
render_approval_management()
승인 관리 (CEO/Master 전용)
reimbursement_management.py
show_reimbursement_management()
메인 함수
3개 탭 구성
호출: main.py → show_reimbursement_management_page()
render_reimbursement_pending()
환급 대기 목록
프린트 기능
reimbursement_status: pending
render_reimbursement_printed()
프린트 완료 목록
최종 환급 완료 버튼
reimbursement_status: printed
render_reimbursement_completed()
최종 완료 내역
reimbursement_status: completed
complete_reimbursement(expense_id, user_id, update_data_func)
환급 완료 처리
입력: expense_id, user_id, update_data_func
출력: True/False
render_reimbursement_print()
환급 확인서 프린트 화면
HTML 템플릿 사용
document_number.py
generate_document_number(doc_type, save_func=None, load_func=None)
문서번호 생성
doc_type: 'EXP' 또는 'PAY'
입력: doc_type, load_func
출력: 문서번호 문자열
🎯 main.py 함수 호출 방식
python
# 지출 요청서 관리
if menu == "지출 요청서 관리":
    show_expense_management(
        load_data_func=load_data,
        save_data_func=save_data,
        update_data_func=update_data,
        delete_data_func=delete_data,
        get_current_user_func=get_current_user,
        get_approval_status_info_func=get_approval_status_info,
        calculate_expense_statistics_func=calculate_expense_statistics,
        create_csv_download_func=create_csv_download,
        render_print_form_func=render_print_form
    )

# 환급 관리
if menu == "환급 관리":
    show_reimbursement_management(
        load_data_func=load_data,
        update_data_func=update_data,
        get_current_user_func=get_current_user
    )
🚨 최근 수정 사항
2025-10-01
용어 변경
"회계 확인" → "화던 발행 확인 (Hóa đơn)"
accounting → invoice (UI 텍스트만)
메뉴 구조 정리
메인 메뉴에서 "회계 확인" 제거
지출 요청서 관리 내 탭으로 통합
화던 발행 확인 탭 개선
직원별 그룹핑
다중 선택 기능
일괄 처리
버그 수정
confirm_invoice_expense() 함수 파라미터 수정
load_data_func 추가
⚙️ 컴포넌트 연결 관계
main.py
├─ load_data() → DB 조회
├─ save_data() → DB 저장
├─ update_data() → DB 수정
├─ delete_data() → DB 삭제
└─ get_current_user() → 현재 사용자 정보

↓ 전달

expense_management.py
├─ render_invoice_check_tab()
│   └─ confirm_invoice_expense() → update_data_func 사용
└─ render_expense_list()
    └─ confirm_invoice_expense() → update_data_func, load_data_func 사용

reimbursement_management.py
├─ render_reimbursement_pending()
│   └─ generate_document_number() → load_func 사용
└─ render_reimbursement_printed()
    └─ complete_reimbursement() → update_data_func 사용
📝 다음 작업 예정
UI 개선
지출 요청서 목록을 환급 관리 스타일로 변경
직원별 그룹핑 적용
기능 추가
대기 건수 표시 (탭 이름에)
상태 흐름 시각화
파일 정리
accounting_management.py 삭제 (사용 안 함)
🐛 알려진 이슈
없음
📚 참고 사항
베트남 화던(Hóa đơn)
베트남의 공식 세금계산서/영수증
법적으로 유효한 지출 증빙
화던 발행 확인 후 환급 처리 가능
환급 상태
pending: 환급 대기
printed: 프린트 완료 (환급 확인서 발행)
completed: 최종 환급 완료
not_required: 환급 불필요 (법인카드 사용 시)
🔒 백업 복구 방법
새 채팅 시작
이 백업 파일 업로드
"이 파일 기준으로 개발 이어가줘" 입력
규칙 파일(V10) 함께 업로드
백업 완료!