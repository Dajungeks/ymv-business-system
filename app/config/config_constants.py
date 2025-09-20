# app/config/constants.py

# 문서 타입 코드
DOCUMENT_TYPES = {
    'QUOTATION': 'Q',
    'PURCHASE': 'P', 
    'EXPENSE': 'E',
    'ORDER': 'O'
}

# 상태 코드
STATUS_CODES = {
    'DRAFT': '작성중',
    'PENDING': '대기중',
    'APPROVED': '승인됨',
    'REJECTED': '반려됨',
    'SENT': '발송됨',
    'ACCEPTED': '수락됨',
    'EXPIRED': '만료됨',
    'CANCELLED': '취소됨',
    'PAID': '지급완료',
    'CONFIRMED': '확인됨',
    'COMPLETED': '완료됨'
}

# 사용자 역할
USER_ROLES = {
    'MASTER': 'master',
    'ADMIN': 'admin',
    'MANAGER': 'manager',
    'USER': 'user'
}

# 색상 코드
COLORS = {
    'PRIMARY': '#2c3e50',
    'SECONDARY': '#3498db',
    'SUCCESS': '#27ae60',
    'WARNING': '#f39c12',
    'DANGER': '#e74c3c',
    'INFO': '#17a2b8',
    'LIGHT': '#f8f9fa',
    'DARK': '#343a40'
}

# 구매 카테고리
PURCHASE_CATEGORIES = ['사무용품', '판매제품', '핫런너', '기타']

# 지출 유형
EXPENSE_TYPES = [
    '출장비', '사무용품', '접대비', '교육비', '교통비', 
    '식비', '통신비', '장비구입', '유지보수', '마케팅', '기타'
]

# 결제 방법
PAYMENT_METHODS = ['현금', '법인카드', '계좌이체', '수표', '기타']

# 통화 기호
CURRENCY_SYMBOLS = {
    'USD': '$',
    'VND': '₫',
    'KRW': '₩',
    'CNY': '¥',
    'THB': '฿',
    'JPY': '¥',
    'EUR': '€'
}

# 날짜 형식
DATE_FORMATS = {
    'DEFAULT': '%Y-%m-%d',
    'DISPLAY': '%Y년 %m월 %d일',
    'FILENAME': '%Y%m%d_%H%M%S'
}

# 언어 코드 매핑
LANGUAGE_MAPPING = {
    'ko': '한국어',
    'en': 'English', 
    'vn': 'Tiếng Việt'
}

# 긴급도 옵션
URGENCY_LEVELS = ['보통', '긴급', '매우긴급']

# 단위 옵션
UNIT_OPTIONS = ['개', '세트', '대', 'kg', 'g', 'm', 'cm', '리터', '박스', '팩']