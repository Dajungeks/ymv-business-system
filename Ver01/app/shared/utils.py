"""
YMV 비즈니스 시스템 - 공통 유틸리티 함수들
"""

import streamlit as st
import pandas as pd
import json
import hashlib
import secrets
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import re

def format_currency(amount: float, currency: str = "VND") -> str:
    """통화 포맷팅 - 베트남 비즈니스 기준"""
    if currency == "VND":
        return f"{amount:,.0f} VND"  # 베트남동: 천 단위 쉼표, 소수점 없음
    elif currency == "USD":
        return f"${amount:,.2f}"  # 달러: 소수점 2자리
    elif currency == "KRW":
        return f"₩{amount:,.0f}"
    elif currency == "CNY":
        return f"¥{amount:,.2f}"
    elif currency == "THB":
        return f"฿{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def generate_document_number(doc_type: str, date_obj: date = None) -> str:
    """문서 번호 생성 (YMV-Qyymmdd-count, YMV-Pyymmdd-count)"""
    if date_obj is None:
        date_obj = date.today()
    
    date_str = date_obj.strftime("%y%m%d")
    
    if doc_type.upper() == "QUOTATION":
        prefix = f"YMV-Q{date_str}"
    elif doc_type.upper() == "PURCHASE":
        prefix = f"YMV-P{date_str}"
    else:
        prefix = f"YMV-{doc_type[0].upper()}{date_str}"
    
    # TODO: 데이터베이스에서 오늘 날짜의 마지막 번호 조회하여 +1
    # 현재는 임시로 랜덤 번호 사용
    count = secrets.randbelow(99) + 1
    
    return f"{prefix}-{count:02d}"

def validate_email(email: str) -> bool:
    """이메일 유효성 검사"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """전화번호 유효성 검사 (베트남/한국 형식)"""
    # 베트남: +84-xxx-xxx-xxxx 또는 84xxxxxxxxx
    # 한국: +82-xx-xxxx-xxxx 또는 82xxxxxxxxxx
    pattern = r'^(\+?84|84|\+?82|82)[0-9]{8,10}$'
    clean_phone = re.sub(r'[-\s()]', '', phone)
    return re.match(pattern, clean_phone) is not None

def convert_currency(amount: float, from_currency: str, to_currency: str, 
                    exchange_rates: Dict[str, float]) -> float:
    """환율 변환"""
    if from_currency == to_currency:
        return amount
    
    # USD 기준으로 변환
    if from_currency != "USD":
        amount = amount / exchange_rates.get(from_currency, 1)
    
    if to_currency != "USD":
        amount = amount * exchange_rates.get(to_currency, 1)
    
    return round(amount, 2)

def export_to_csv(data: List[Dict], filename: str) -> bytes:
    """데이터를 CSV로 내보내기"""
    if not data:
        return b""
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

def export_to_excel(data: List[Dict], filename: str) -> bytes:
    """데이터를 Excel로 내보내기"""
    if not data:
        return b""
    
    df = pd.DataFrame(data)
    
    # BytesIO를 사용하여 메모리에서 Excel 파일 생성
    from io import BytesIO
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    
    return output.getvalue()

def show_success_message(message: str):
    """성공 메시지 표시"""
    st.success(f"✅ {message}")

def show_error_message(message: str):
    """에러 메시지 표시"""
    st.error(f"❌ {message}")

def show_warning_message(message: str):
    """경고 메시지 표시"""
    st.warning(f"⚠️ {message}")

def show_info_message(message: str):
    """정보 메시지 표시"""
    st.info(f"ℹ️ {message}")

def create_download_button(data: bytes, filename: str, 
                          label: str = "다운로드", mime_type: str = "text/csv"):
    """다운로드 버튼 생성"""
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime_type
    )

def format_date(date_obj: date, format: str = "%Y-%m-%d") -> str:
    """날짜 포맷팅"""
    if date_obj:
        return date_obj.strftime(format)
    return ""

def parse_date(date_str: str, format: str = "%Y-%m-%d") -> Optional[date]:
    """문자열을 날짜로 변환"""
    try:
        return datetime.strptime(date_str, format).date()
    except:
        return None

def generate_hash(text: str) -> str:
    """텍스트 해시 생성"""
    return hashlib.sha256(text.encode()).hexdigest()

def clean_text(text: str) -> str:
    """텍스트 정리 (공백 제거, 특수문자 처리)"""
    if not text:
        return ""
    return text.strip()

def paginate_data(data: List[Dict], page: int, items_per_page: int = 20) -> tuple:
    """데이터 페이지네이션"""
    total_items = len(data)
    total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    return data[start_idx:end_idx], total_pages, total_items