from datetime import datetime

def generate_document_number(doc_type, save_func=None, load_func=None):
    """문서 번호 생성 - DOC-YYMMDD-001 형식"""
    
    today = datetime.now().strftime('%y%m%d')
    prefix = f"{doc_type}-{today}"
    
    # doc_type에 따라 조회할 컬럼 결정
    if doc_type == 'PAY':
        column_name = 'reimbursement_document_number'
    elif doc_type == 'EXP':
        column_name = 'document_number'
    else:
        column_name = 'document_number'
    
    # DB에서 오늘 날짜 문서 중 최대 번호 조회
    if load_func:
        try:
            expenses = load_func('expenses')
            today_docs = [
                exp.get(column_name, '') 
                for exp in expenses 
                if exp.get(column_name, '') and 
                   exp.get(column_name, '').startswith(prefix) and
                   exp.get(column_name, '') != 'TEMP'  # TEMP 제외
            ]
            
            if today_docs:
                # 마지막 번호 추출
                last_numbers = []
                for doc in today_docs:
                    try:
                        num = int(doc.split('-')[-1])
                        last_numbers.append(num)
                    except:
                        continue
                
                if last_numbers:
                    next_num = max(last_numbers) + 1
                else:
                    next_num = 1
            else:
                next_num = 1
        except:
            next_num = 1
    else:
        next_num = 1
    
    return f"{prefix}-{next_num:03d}"