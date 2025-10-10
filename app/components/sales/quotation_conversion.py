import streamlit as st
from datetime import datetime, timedelta

def show_quotation_conversion(load_func, save_func, current_user):
    """견적서 → 영업 프로세스 전환"""
    
    st.subheader("⚡ 견적서 → 영업 프로세스 전환")
    
    # 권한 확인
    if current_user.get('role') not in ['admin', 'manager']:
        st.error("영업 프로세스 전환 권한이 없습니다.")
        return
    
    try:
        # 승인 가능한 견적서 로드 (작성중 또는 검토중 상태)
        quotations = load_func("quotations", filters={"status": ["작성중", "검토중", "승인대기"]})
        customers_data = load_func('customers')
        
        # DataFrame 변환
        customers_df = pd.DataFrame(customers_data) if customers_data else pd.DataFrame()
        
        if not quotations:
            st.info("전환 가능한 견적서가 없습니다.")
            return
        
        # 견적서 선택
        st.write("### 📄 전환할 견적서 선택")
        
        # 견적서 목록 표시
        for quota in quotations:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                # 고객명 표시 (짧은 이름 우선)
                customer_display_name = 'N/A'
                if not customers_df.empty and quota.get('customer_id'):
                    customer_row = customers_df[customers_df['id'] == quota['customer_id']]
                    if not customer_row.empty:
                        customer_display_name = customer_row.iloc[0].get('company_name_short') or customer_row.iloc[0].get('company_name_original')
                
                # fallback: 견적서에 저장된 회사명 사용
                if customer_display_name == 'N/A':
                    customer_display_name = quota.get('company', quota.get('customer_name', 'N/A'))
                
                with col1:
                    st.write(f"**{customer_display_name}**")
                    st.write(f"상품: {quota.get('item_name', 'N/A')}")
                    st.write(f"수량: {quota.get('quantity', 0):,}개")
                
                with col2:
                    amount = float(quota.get('total_amount', 0))
                    currency = quota.get('currency', 'VND')
                    st.write(f"**금액: {amount:,.0f} {currency}**")
                    st.write(f"상태: {quota.get('status', 'N/A')}")
                    st.write(f"작성일: {quota.get('created_at', 'N/A')[:10] if quota.get('created_at') else 'N/A'}")
                
                with col3:
                    if st.button(f"전환하기", key=f"convert_{quota['id']}"):
                        convert_quotation_to_process(quota, current_user, save_func)
                
                st.divider()
        
    except Exception as e:
        st.error(f"견적서 로드 중 오류 발생: {str(e)}")

def convert_quotation_to_process(quotation, current_user, save_func):
    """견적서를 영업 프로세스로 전환"""
    
    try:
        # 프로세스 번호 생성
        process_number = generate_document_number('sales_process', save_func)
        
        # 고객 회사명 (견적서에 저장된 공식 이름 사용)
        customer_company = quotation.get('company', quotation.get('customer_name', ''))
        
        # 영업 프로세스 데이터 생성
        process_data = {
            'process_number': process_number,
            'quotation_id': quotation['id'],
            'customer_name': quotation.get('customer_name', ''),
            'customer_company': customer_company,
            'customer_email': quotation.get('email', ''),
            'customer_phone': quotation.get('phone', ''),
            'sales_rep_id': current_user['id'],
            'process_status': 'approved',
            'item_description': quotation.get('item_name', ''),
            'quantity': quotation.get('quantity', 0),
            'unit_price': quotation.get('unit_price', 0),
            'total_amount': quotation.get('total_amount', 0),
            'currency': quotation.get('currency', 'VND'),
            'expected_delivery_date': (datetime.now() + timedelta(days=30)).date().isoformat(),
            'notes': quotation.get('notes', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 영업 프로세스 저장
        save_func("sales_process", process_data)
        
        # 견적서 상태 업데이트
        update_quotation_status(quotation['id'], '승인됨', save_func)
        
        # 프로세스 이력 기록
        record_process_history(
            process_number, None, 'approved', 
            current_user['id'], '견적서에서 전환', save_func
        )
        
        st.success(f"✅ 영업 프로세스가 생성되었습니다: {process_number}")
        st.balloons()
        st.rerun()
        
    except Exception as e:
        st.error(f"프로세스 전환 중 오류 발생: {str(e)}")


def generate_document_number(doc_type, save_func):
    """동적 문서 번호 생성"""
    
    current_year = datetime.now().year
    
    # document_sequences에서 prefix 및 번호 가져오기
    sequences = save_func.load_data("document_sequences", filters={"document_type": doc_type})
    
    if not sequences:
        # 기본값 생성
        prefix = f"{doc_type.upper()[:2]}-"
        last_number = 0
    else:
        seq = sequences[0]
        prefix = seq.get('date_prefix', f"{doc_type.upper()[:2]}-")
        last_number = seq.get('last_number', 0)
    
    # 다음 번호 계산
    next_number = last_number + 1
    
    # 문서 번호 생성: SP-2025-0001
    document_number = f"{prefix}{current_year}-{next_number:04d}"
    
    # 번호 업데이트
    try:
        # document_sequences 업데이트 로직 (실제 구현시 update_func 사용)
        pass
    except:
        pass
    
    return document_number

def update_quotation_status(quotation_id, new_status, save_func):
    """견적서 상태 업데이트"""
    try:
        # 실제 구현시 update_func 사용
        pass
    except:
        pass

def record_process_history(process_number, status_from, status_to, changed_by, reason, save_func):
    """프로세스 이력 기록"""
    
    history_data = {
        'sales_process_id': process_number,  # 실제로는 ID로 변경 필요
        'status_from': status_from,
        'status_to': status_to,
        'changed_by': changed_by,
        'change_date': datetime.now().isoformat(),
        'change_reason': reason
    }
    
    try:
        save_func("sales_process_history", history_data)
    except:
        pass