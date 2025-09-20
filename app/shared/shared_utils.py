# app/shared/utils.py
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List
import streamlit as st

def create_directories():
    """필요한 디렉토리 생성"""
    directories = ['uploads', 'exports', 'logs', 'fonts', 'data']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        # .gitkeep 파일 생성 (빈 디렉토리도 Git에서 추적)
        gitkeep_file = Path(directory) / '.gitkeep'
        if not gitkeep_file.exists():
            gitkeep_file.touch()

def format_currency(amount: float, currency: str = 'USD') -> str:
    """통화 포맷팅"""
    from app.config.constants import CURRENCY_SYMBOLS
    
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    
    if currency in ['VND', 'KRW']:
        return f"{symbol} {int(amount):,}"
    else:
        return f"{symbol} {amount:,.2f}"

def generate_document_number(doc_type: str, date=None) -> str:
    """문서 번호 생성"""
    from app.config.constants import DOCUMENT_TYPES
    
    if date is None:
        date = datetime.now()
    
    type_code = DOCUMENT_TYPES.get(doc_type, doc_type)
    date_str = date.strftime("%y%m%d")
    
    # 간단한 카운터 (실제로는 데이터베이스에서 조회)
    if 'document_counters' not in st.session_state:
        st.session_state.document_counters = {}
    
    counter_key = f"{type_code}{date_str}"
    if counter_key not in st.session_state.document_counters:
        st.session_state.document_counters[counter_key] = 0
    
    st.session_state.document_counters[counter_key] += 1
    count = st.session_state.document_counters[counter_key]
    
    return f"YMV-{type_code}{date_str}-{count:03d}"

def save_data_to_file(data: Dict[str, Any], filename: str):
    """데이터를 JSON 파일로 저장"""
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    filepath = data_dir / f"{filename}.json"
    
    # 날짜 객체를 문자열로 변환
    def serialize_dates(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return obj
    
    # 기존 데이터 로드
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except:
            existing_data = []
    else:
        existing_data = []
    
    # 새 데이터 추가
    existing_data.append(serialize_dates(data))
    
    # 파일에 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2, default=serialize_dates)

def load_data_from_file(filename: str) -> List[Dict[str, Any]]:
    """JSON 파일에서 데이터 로드"""
    data_dir = Path('data')
    filepath = data_dir / f"{filename}.json"
    
    if not filepath.exists():
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def validate_file_upload(uploaded_file, allowed_extensions: List[str], max_size: int = 10485760):
    """파일 업로드 유효성 검사"""
    if uploaded_file is None:
        return False, "파일이 선택되지 않았습니다."
    
    # 파일 확장자 확인
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        return False, f"허용되지 않은 파일 형식입니다. 허용 형식: {', '.join(allowed_extensions)}"
    
    # 파일 크기 확인
    if uploaded_file.size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f"파일 크기가 너무 큽니다. 최대 크기: {max_size_mb:.1f}MB"
    
    return True, "파일이 유효합니다."

def export_to_excel(data: List[Dict], filename: str):
    """데이터를 Excel 파일로 내보내기"""
    try:
        import pandas as pd
        
        df = pd.DataFrame(data)
        export_dir = Path('exports')
        export_dir.mkdir(exist_ok=True)
        
        filepath = export_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        return str(filepath)
    except Exception as e:
        st.error(f"Excel 파일 생성 중 오류: {str(e)}")
        return None

def format_date(date_obj, format_type='display'):
    """날짜 포맷팅"""
    from app.config.constants import DATE_FORMATS
    
    if date_obj is None:
        return ""
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj)
        except:
            return date_obj
    
    format_str = DATE_FORMATS.get(format_type.upper(), DATE_FORMATS['DEFAULT'])
    return date_obj.strftime(format_str)

def get_status_color(status: str) -> str:
    """상태에 따른 색상 반환"""
    status_colors = {
        '작성중': '#95a5a6',
        '대기중': '#f39c12',
        '승인됨': '#27ae60',
        '반려됨': '#e74c3c',
        '발송됨': '#3498db',
        '완료됨': '#27ae60',
        '취소됨': '#e74c3c'
    }
    return status_colors.get(status, '#95a5a6')

def display_status_badge(status: str):
    """상태 배지 표시"""
    color = get_status_color(status)
    return f'<span style="background-color: {color}; color: white; padding: 0.3rem 0.6rem; border-radius: 15px; font-size: 0.8rem;">{status}</span>'