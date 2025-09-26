import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import time
from collections import defaultdict

def generate_unique_key(prefix=""):
    """고유한 위젯 키 생성"""
    timestamp = str(int(time.time() * 1000))
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{unique_id}"

def get_quotation_status_info(status):
    """견적서 상태별 정보 반환"""
    status_info = {
        '작성중': {'emoji': '📝', 'color': '#6c757d', 'description': '견적서 작성 중'},
        '검토중': {'emoji': '👀', 'color': '#ffc107', 'description': '내부 검토 중'},
        '발송대기': {'emoji': '📤', 'color': '#17a2b8', 'description': '고객 발송 대기'},
        '발송됨': {'emoji': '📧', 'color': '#28a745', 'description': '고객에게 발송 완료'},
        '승인됨': {'emoji': '✅', 'color': '#007bff', 'description': '고객 승인 완료'},
        '거절됨': {'emoji': '❌', 'color': '#dc3545', 'description': '고객 거절'},
        '만료됨': {'emoji': '⏰', 'color': '#6c757d', 'description': '유효기간 만료'}
    }
    return status_info.get(status, {'emoji': '❓', 'color': '#6c757d', 'description': '알 수 없음'})

def render_quotation_form(load_data_func, save_data_func, update_data_func, delete_data_func):
    """견적서 작성 폼 (main.py DB 함수 구조에 맞춤)"""
    
    # 기본 데이터 로드 (main.py 함수 시그니처 사용)
    customers = load_data_func('customers')
    products = load_data_func('products')
    
    if not customers:
        st.error("고객 정보가 없습니다. 먼저 고객을 등록해주세요.")
        return False
    
    if not products:
        st.error("제품 정보가 없습니다. 먼저 제품을 등록해주세요.")
        return False
    
    with st.form("quotation_form"):
        st.subheader("📋 견적서 작성")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 고객 정보 (기존 customers 테이블에서 선택)
            st.write("**고객 정보**")
            
            # 고객 선택 드롭다운
            customer_options = {}
            for customer in customers:
                display_name = f"{customer.get('company_name', 'N/A')} ({customer.get('contact_person', 'N/A')})"
                customer_options[display_name] = customer
            
            selected_customer_key = st.selectbox("고객 선택", list(customer_options.keys()))
            selected_customer = customer_options[selected_customer_key]
            
            # 선택된 고객 정보 표시
            st.info(f"""
            **회사명:** {selected_customer.get('company_name', 'N/A')}  
            **담당자:** {selected_customer.get('contact_person', 'N/A')} ({selected_customer.get('position', '')})  
            **연락처:** {selected_customer.get('phone', 'N/A')}  
            **이메일:** {selected_customer.get('email', 'N/A')}  
            **업종:** {selected_customer.get('industry', 'N/A')}
            """)
            
            # 날짜 정보
            quote_date = st.date_input("견적일", value=datetime.now().date())
            valid_until = st.date_input("유효일", value=(datetime.now() + timedelta(days=30)).date())
        
        with col2:
            # 제품 정보 (기존 products 테이블에서 선택)
            st.write("**제품 정보**")
            
            # 제품 선택 드롭다운
            product_options = {}
            for product in products:
                display_name = f"{product.get('product_name', 'N/A')} ({product.get('product_code', 'N/A')})"
                product_options[display_name] = product
            
            selected_product_key = st.selectbox("제품 선택", list(product_options.keys()))
            selected_product = product_options[selected_product_key]
            
            # 선택된 제품 정보 표시 및 가격 자동 입력
            st.info(f"""
            **제품명:** {selected_product.get('product_name', 'N/A')}  
            **제품코드:** {selected_product.get('product_code', 'N/A')}  
            **카테고리:** {selected_product.get('category', 'N/A')}  
            **공급업체:** {selected_product.get('supplier', 'N/A')}  
            **재고:** {selected_product.get('stock_quantity', 0)} {selected_product.get('unit', '개')}
            """)
            
            quantity = st.number_input("수량", min_value=1, value=1)
            
            # 통화 선택에 따른 가격 표시
            currency = st.selectbox("통화", ["USD", "VND"])
            
            if currency == "USD":
                default_price = float(selected_product.get('unit_price', 0))
                price_label = f"단가 (USD) - 기본가: ${default_price:.2f}"
            else:
                default_price = float(selected_product.get('unit_price_vnd', 0))
                price_label = f"단가 (VND) - 기본가: ₫{default_price:,.0f}"
            
            unit_price = st.number_input(price_label, min_value=0.0, value=default_price, format="%.2f")
            
            # 자동 계산
            total_amount = quantity * unit_price
            if currency == "USD":
                st.write(f"**총 금액: ${total_amount:.2f}**")
            else:
                st.write(f"**총 금액: ₫{total_amount:,.0f}**")
            
            status = st.selectbox("상태", ["작성중", "검토중", "발송대기", "발송됨", "승인됨", "거절됨", "만료됨"])
        
        # 추가 정보
        st.subheader("📝 추가 정보")
        notes = st.text_area("참고사항", height=100)
        
        # 저장 버튼
        submit_save = st.form_submit_button("💾 견적서 저장", use_container_width=True)
        
        if submit_save:
            # quotation_data 생성 (total_amount 포함)
            quotation_data = {
                'customer_id': selected_customer.get('id'),
                'customer_name': selected_customer.get('contact_person'),
                'company': selected_customer.get('company_name'),
                'contact_person': selected_customer.get('contact_person'),
                'email': selected_customer.get('email'),
                'phone': selected_customer.get('phone'),
                'quote_date': quote_date.isoformat(),
                'valid_until': valid_until.isoformat(),
                'currency': currency,
                'item_name': selected_product.get('product_name'),
                'quantity': quantity,
                'unit_price': unit_price,
                'total_amount': total_amount,  # total_amount 포함
                'notes': notes,
                'status': status,
                'created_by': 1,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            if save_data_func('quotations', quotation_data):
                st.success("✅ 견적서가 저장되었습니다!")
                st.rerun()
            else:
                st.error("❌ 견적서 저장에 실패했습니다.")
    
    return True

def render_quotation_list(load_data_func, save_data_func, update_data_func, delete_data_func):
    """견적서 목록 표시"""
    
    # 필터링 옵션
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        status_filter = st.selectbox("상태 필터", 
                                   ['전체'] + ['작성중', '검토중', '발송대기', '발송됨', '승인됨', '거절됨', '만료됨'],
                                   key=generate_unique_key("status_filter"))
    
    with col2:
        sort_order = st.selectbox("정렬 기준", 
                                ['생성일 최신순', '생성일 오래된순', '금액 높은순', '금액 낮은순'],
                                key=generate_unique_key("sort_order"))
    
    with col3:
        if st.button("📄 CSV 다운로드"):
            quotations = load_data_func('quotations')
            if quotations:
                df = pd.DataFrame(quotations)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="CSV 파일 다운로드",
                    data=csv,
                    file_name=f"quotations_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    # 데이터 로드
    quotations = load_data_func('quotations')
    
    if not quotations:
        st.info("등록된 견적서가 없습니다.")
        return
    
    # 필터링
    if status_filter != '전체':
        quotations = [q for q in quotations if q.get('status') == status_filter]
    
    # 정렬
    if sort_order == '생성일 최신순':
        quotations = sorted(quotations, key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_order == '생성일 오래된순':
        quotations = sorted(quotations, key=lambda x: x.get('created_at', ''))
    elif sort_order == '금액 높은순':
        quotations = sorted(quotations, key=lambda x: x.get('total_amount', 0), reverse=True)
    elif sort_order == '금액 낮은순':
        quotations = sorted(quotations, key=lambda x: x.get('total_amount', 0))
    
    # 견적서 목록 표시
    if quotations:
        for quotation in quotations:
            quotation_id = quotation.get('id')
            status_info = get_quotation_status_info(quotation.get('status', '작성중'))
            
            # expander 제목
            currency_symbol = "$" if quotation.get('currency') == 'USD' else "₫"
            amount = quotation.get('total_amount', 0)
            amount_display = f"{currency_symbol}{amount:,.2f}" if quotation.get('currency') == 'USD' else f"{currency_symbol}{amount:,.0f}"
            
            title = f"{status_info['emoji']} {quotation.get('company', 'N/A')} - {quotation.get('item_name', 'N/A')} - {amount_display}"
            
            with st.expander(title):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**고객명:** {quotation.get('customer_name', 'N/A')}")
                    st.write(f"**회사:** {quotation.get('company', 'N/A')}")
                    st.write(f"**담당자:** {quotation.get('contact_person', 'N/A')}")
                    st.write(f"**연락처:** {quotation.get('phone', 'N/A')}")
                    st.write(f"**이메일:** {quotation.get('email', 'N/A')}")
                
                with col2:
                    st.write(f"**제품/서비스:** {quotation.get('item_name', 'N/A')}")
                    st.write(f"**견적일:** {quotation.get('quote_date', 'N/A')}")
                    st.write(f"**유효일:** {quotation.get('valid_until', 'N/A')}")
                    st.write(f"**수량:** {quotation.get('quantity', 0)}")
                    st.write(f"**단가:** {quotation.get('unit_price', 0):.2f}")
                    st.write(f"**총액:** {amount_display}")
                    st.write(f"**상태:** {quotation.get('status', 'N/A')}")
                
                with col3:
                    # 액션 버튼들
                    if st.button("📄 출력", key=f"print_{quotation_id}"):
                        st.session_state[f"print_quotation_{quotation_id}"] = True
                        st.rerun()
                    
                    if st.button("✏️ 수정", key=f"edit_{quotation_id}"):
                        st.info("수정 기능은 곧 구현됩니다.")
                    
                    if st.button("🗑️ 삭제", key=f"delete_{quotation_id}"):
                        if delete_data_func('quotations', quotation_id):
                            st.success("✅ 견적서가 삭제되었습니다!")
                            st.rerun()
                        else:
                            st.error("❌ 견적서 삭제에 실패했습니다.")
                
                # 참고사항
                if quotation.get('notes'):
                    st.write(f"**참고사항:** {quotation.get('notes')}")
                
                # 출력 미리보기 (조건부 표시)
                if st.session_state.get(f"print_quotation_{quotation_id}", False):
                    st.markdown("---")
                    st.markdown("### 🖨️ 견적서 출력 미리보기")
                    render_quotation_print(quotation)
                    if st.button("❌ 미리보기 닫기", key=f"close_print_{quotation_id}"):
                        st.session_state[f"print_quotation_{quotation_id}"] = False
                        st.rerun()
    else:
        st.info("조건에 맞는 견적서가 없습니다.")

def render_quotation_print(quotation):
    """견적서 출력 미리보기 - 개선된 프린트 기능"""
    
    currency_symbol = "$" if quotation.get('currency') == 'USD' else "₫"
    amount = quotation.get('total_amount', 0)
    unit_price = quotation.get('unit_price', 0)
    
    if quotation.get('currency') == 'USD':
        amount_display = f"{currency_symbol}{amount:.2f}"
        unit_price_display = f"{currency_symbol}{unit_price:.2f}"
    else:
        amount_display = f"{currency_symbol}{amount:,.0f}"
        unit_price_display = f"{currency_symbol}{unit_price:,.0f}"
    
    # 프린트 전용 ID 생성
    print_id = f"quotation_print_{quotation.get('id', 'default')}"
    
    print_html = f"""
    <div id="{print_id}" style="background: white; padding: 2rem; border: 1px solid #ddd; font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
        <div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 1rem; margin-bottom: 2rem;">
            <h1 style="margin: 0; font-size: 2rem; font-weight: bold;">QUOTATION</h1>
            <h2 style="margin: 0.5rem 0; font-size: 1.5rem; color: #666;">견적서</h2>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 2rem;">
            <div style="flex: 1;">
                <h3 style="color: #333; border-bottom: 1px solid #ddd; padding-bottom: 0.5rem;">고객 정보 / Customer Info</h3>
                <p style="margin: 0.5rem 0;"><strong>회사명:</strong> {quotation.get('company', 'N/A')}</p>
                <p style="margin: 0.5rem 0;"><strong>담당자:</strong> {quotation.get('contact_person', 'N/A')}</p>
                <p style="margin: 0.5rem 0;"><strong>이메일:</strong> {quotation.get('email', 'N/A')}</p>
                <p style="margin: 0.5rem 0;"><strong>전화:</strong> {quotation.get('phone', 'N/A')}</p>
            </div>
            <div style="flex: 1; text-align: right;">
                <h3 style="color: #333; border-bottom: 1px solid #ddd; padding-bottom: 0.5rem;">YMV Company</h3>
                <p style="margin: 0.5rem 0;">Vietnam Office</p>
                <p style="margin: 0.5rem 0;">Contact: +84-xxx-xxxx</p>
                <p style="margin: 0.5rem 0;">Email: info@ymv.com</p>
            </div>
        </div>
        
        <div style="margin-bottom: 2rem; display: flex; justify-content: space-between;">
            <p><strong>견적일:</strong> {quotation.get('quote_date', 'N/A')}</p>
            <p><strong>유효일:</strong> {quotation.get('valid_until', 'N/A')}</p>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; margin: 2rem 0; border: 2px solid #000;">
            <thead>
                <tr style="background: #f8f9fa;">
                    <th style="border: 1px solid #000; padding: 12px; text-align: left; font-weight: bold;">제품/서비스</th>
                    <th style="border: 1px solid #000; padding: 12px; text-align: center; font-weight: bold;">수량</th>
                    <th style="border: 1px solid #000; padding: 12px; text-align: right; font-weight: bold;">단가</th>
                    <th style="border: 1px solid #000; padding: 12px; text-align: right; font-weight: bold;">금액</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="border: 1px solid #000; padding: 12px;">{quotation.get('item_name', 'N/A')}</td>
                    <td style="border: 1px solid #000; padding: 12px; text-align: center;">{quotation.get('quantity', 0)}</td>
                    <td style="border: 1px solid #000; padding: 12px; text-align: right;">{unit_price_display}</td>
                    <td style="border: 1px solid #000; padding: 12px; text-align: right; font-weight: bold;">{amount_display}</td>
                </tr>
            </tbody>
        </table>
        
        <div style="text-align: right; margin: 2rem 0; border-top: 2px solid #000; padding-top: 1rem;">
            <p style="font-size: 1.2rem; font-weight: bold; color: #000;">총 합계: {amount_display}</p>
        </div>
        
        {f'<div style="margin: 2rem 0;"><h3 style="color: #333; border-bottom: 1px solid #ddd; padding-bottom: 0.5rem;">참고사항 / Notes</h3><p style="padding: 1rem; background: #f9f9f9; border-left: 4px solid #007bff;">{quotation.get("notes", "")}</p></div>' if quotation.get('notes') else ''}
        
        <div style="display: flex; justify-content: space-between; margin-top: 4rem; border-top: 1px solid #ddd; padding-top: 2rem;">
            <div style="text-align: center;">
                <p style="margin-bottom: 3rem; font-weight: bold;">고객 서명 / Customer Signature</p>
                <p style="border-bottom: 1px solid #000; width: 200px; margin: 0 auto;">&nbsp;</p>
                <p style="margin-top: 0.5rem;">날짜: _______________</p>
            </div>
            <div style="text-align: center;">
                <p style="margin-bottom: 3rem; font-weight: bold;">YMV 서명 / YMV Signature</p>
                <p style="border-bottom: 1px solid #000; width: 200px; margin: 0 auto;">&nbsp;</p>
                <p style="margin-top: 0.5rem;">날짜: _______________</p>
            </div>
        </div>
    </div>
    
    <style>
        @media print {{
            body * {{
                visibility: hidden;
            }}
            #{print_id}, #{print_id} * {{
                visibility: visible;
            }}
            #{print_id} {{
                position: absolute;
                left: 0;
                top: 0;
                width: 100%;
                background: white !important;
                -webkit-print-color-adjust: exact;
            }}
            .stButton, button, .css-* {{
                display: none !important;
            }}
        }}
    </style>
    """
    
    st.markdown(print_html, unsafe_allow_html=True)
    
    # 개선된 프린트 옵션들
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 브라우저 프린트 (개선된 방법)
        if st.button("🖨️ 브라우저 프린트", key=f"browser_print_{quotation.get('id')}"):
            st.components.v1.html(f"""
            <script>
                function printQuotation() {{
                    var printContents = document.getElementById('{print_id}').outerHTML;
                    var printWindow = window.open('', '_blank');
                    printWindow.document.write('<html><head><title>견적서</title>');
                    printWindow.document.write('<style>');
                    printWindow.document.write('body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}');
                    printWindow.document.write('table {{ border-collapse: collapse; width: 100%; }}');
                    printWindow.document.write('th, td {{ border: 1px solid #000; padding: 8px; }}');
                    printWindow.document.write('</style></head><body>');
                    printWindow.document.write(printContents);
                    printWindow.document.write('</body></html>');
                    printWindow.document.close();
                    printWindow.print();
                    printWindow.close();
                }}
                printQuotation();
            </script>
            """, height=0)
            st.success("✅ 새 창에서 프린트 대화상자가 열렸습니다!")
    
    with col2:
        # PDF 다운로드 (HTML to PDF)
        if st.button("📄 PDF 다운로드", key=f"pdf_download_{quotation.get('id')}"):
            # HTML을 텍스트로 변환하여 다운로드 제공
            pdf_content = f"""
견적서 / QUOTATION

고객 정보:
- 회사명: {quotation.get('company', 'N/A')}
- 담당자: {quotation.get('contact_person', 'N/A')}
- 이메일: {quotation.get('email', 'N/A')}
- 전화: {quotation.get('phone', 'N/A')}

견적 정보:
- 견적일: {quotation.get('quote_date', 'N/A')}
- 유효일: {quotation.get('valid_until', 'N/A')}

제품 정보:
- 제품/서비스: {quotation.get('item_name', 'N/A')}
- 수량: {quotation.get('quantity', 0)}
- 단가: {unit_price_display}
- 총액: {amount_display}

{f"참고사항: {quotation.get('notes', '')}" if quotation.get('notes') else ''}

YMV Company
Vietnam Office
Contact: +84-xxx-xxxx
Email: info@ymv.com
            """
            
            st.download_button(
                label="📄 텍스트 파일 다운로드",
                data=pdf_content.encode('utf-8'),
                file_name=f"quotation_{quotation.get('id', 'default')}.txt",
                mime="text/plain"
            )
            st.success("✅ 텍스트 파일로 다운로드 가능합니다!")
    
    with col3:
        # 복사 버튼
        if st.button("📋 클립보드 복사", key=f"copy_clipboard_{quotation.get('id')}"):
            copy_text = f"""견적서 - {quotation.get('company', 'N/A')}
제품: {quotation.get('item_name', 'N/A')}
수량: {quotation.get('quantity', 0)}
단가: {unit_price_display}
총액: {amount_display}
견적일: {quotation.get('quote_date', 'N/A')}
유효일: {quotation.get('valid_until', 'N/A')}"""
            
            st.code(copy_text, language=None)
            st.success("✅ 위 내용을 복사해서 사용하세요!")

def show_quotation_statistics(load_data_func):
    """견적서 통계 표시"""
    
    quotations = load_data_func('quotations')
    
    if not quotations:
        st.info("통계를 표시할 견적서가 없습니다.")
        return
    
    # 기본 통계
    total_count = len(quotations)
    total_amount_usd = sum(q.get('total_amount', 0) for q in quotations if q.get('currency') == 'USD')
    total_amount_vnd = sum(q.get('total_amount', 0) for q in quotations if q.get('currency') == 'VND')
    
    # 상태별 통계
    status_stats = defaultdict(int)
    for quotation in quotations:
        status_stats[quotation.get('status', '작성중')] += 1
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 견적서", f"{total_count}건")
    
    with col2:
        st.metric("USD 총액", f"${total_amount_usd:,.2f}")
    
    with col3:
        st.metric("VND 총액", f"₫{total_amount_vnd:,.0f}")
    
    # 상태별 통계
    st.subheader("📊 상태별 현황")
    status_col1, status_col2, status_col3, status_col4 = st.columns(4)
    
    status_columns = [status_col1, status_col2, status_col3, status_col4]
    status_list = list(status_stats.items())
    
    for idx, (status, count) in enumerate(status_list):
        if idx < len(status_columns):
            with status_columns[idx]:
                status_info = get_quotation_status_info(status)
                st.metric(f"{status_info['emoji']} {status}", f"{count}건")
    
    # 월별 통계
    monthly_stats = defaultdict(lambda: {'count': 0, 'amount_usd': 0, 'amount_vnd': 0})
    for quotation in quotations:
        quote_date = quotation.get('quote_date', '')
        if quote_date:
            month = quote_date[:7]  # YYYY-MM
            monthly_stats[month]['count'] += 1
            if quotation.get('currency') == 'USD':
                monthly_stats[month]['amount_usd'] += quotation.get('total_amount', 0)
            else:
                monthly_stats[month]['amount_vnd'] += quotation.get('total_amount', 0)
    
    if monthly_stats:
        st.subheader("📅 월별 견적서 현황")
        
        monthly_data = []
        for month in sorted(monthly_stats.keys()):
            data = monthly_stats[month]
            monthly_data.append({
                '월': month,
                '건수': data['count'],
                'USD 금액': f"${data['amount_usd']:,.2f}",
                'VND 금액': f"₫{data['amount_vnd']:,.0f}"
            })
        
        monthly_df = pd.DataFrame(monthly_data)
        st.dataframe(monthly_df, use_container_width=True, hide_index=True)

def show_quotation_management(load_data_func, save_data_func, update_data_func, delete_data_func):
    """견적서 관리 메인 함수 - main.py DB 함수에 완전히 맞춤"""
    
    st.markdown('<div style="background: linear-gradient(90deg, #1f4e79, #2e6da4); color: white; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 2rem;"><h1>📋 견적서 관리 시스템</h1><p>기존 고객/제품 정보를 활용한 견적서 생성 및 관리</p></div>', unsafe_allow_html=True)
    
    # 기본 데이터 확인
    customers = load_data_func('customers')
    products = load_data_func('products')
    
    # 데이터베이스 스키마 문제 메시지 제거 (실제로는 테이블이 존재함)
    if not customers or not products:
        st.warning("⚠️ 견적서 작성을 위해서는 고객 정보와 제품 정보가 필요합니다.")
        
        col1, col2 = st.columns(2)
        with col1:
            if not customers:
                st.error("❌ 고객 정보가 없습니다. 고객 관리에서 고객을 등록해주세요.")
        
        with col2:
            if not products:
                st.error("❌ 제품 정보가 없습니다. 제품 관리에서 제품을 등록해주세요.")
        
        return
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📝 견적서 작성", "📋 견적서 목록", "📊 견적서 통계"])
    
    with tab1:
        st.subheader("새 견적서 작성")
        render_quotation_form(load_data_func, save_data_func, update_data_func, delete_data_func)
    
    with tab2:
        st.subheader("견적서 목록 및 관리")
        render_quotation_list(load_data_func, save_data_func, update_data_func, delete_data_func)
    
    with tab3:
        st.subheader("견적서 통계 및 분석")
        show_quotation_statistics(load_data_func)