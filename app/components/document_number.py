from datetime import datetime

def generate_document_number(doc_type, save_func=None):
    """문서 번호 생성"""
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    
    # 간단한 시간 기반 번호 생성
    time_suffix = f"{current_month:02d}{current_day:02d}{datetime.now().hour:02d}{datetime.now().minute:02d}"
    
    return f"{doc_type}-{current_year}-{time_suffix}"