import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging

def show_sales_order_management(load_func, save_func, update_func, delete_func):
    """영업 발주 관리 메인 페이지"""
    st.title("📋 영업 발주 관리")
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["발주 작성", "발주 목록", "발주서 출력"])
    
    with tab1:
        render_sales_order_form(save_func, load_func)
    
    with tab2:
        render_sales_order_list(load_func, update_func, delete_func)
    
    with tab3:
        render_sales_order_print(load_func)

def render_sales_order_form(save_func, load_func):
    """영업 발주 작성 폼"""
    st.header("새 발주서 작성")
    
    # 기본 데이터 로드
    suppliers_data = load_func('suppliers')
    products_data = load_func('products')
    sales_processes_data = load_func('sales_process')
    
    # DataFrame 변환
    suppliers_df = pd.DataFrame(suppliers_data) if suppliers_data else pd.DataFrame()
    products_df = pd.DataFrame(products_data) if products_data else pd.DataFrame()
    sales_processes_df = pd.DataFrame(sales_processes_data) if sales_processes_data else pd.DataFrame()
    
    # 데이터 확인
    if suppliers_df.empty:
        st.warning("등록된 공급업체가 없습니다.")
        if st.button("공급업체 관리로 이동"):
            st.session_state.current_page = "공급업체 관리"
            st.rerun()
        return
    
    if products_df.empty:
        st.warning("등록된 제품이 없습니다.")
        return
    
    # === 공급업체 및 프로젝트 선택 ===
    st.subheader("공급업체 및 프로젝트 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        supplier_options = [f"{row['company_name']} ({row['id']})" for _, row in suppliers_df.iterrows()]
        selected_supplier = st.selectbox("공급업체", supplier_options, key="sales_order_supplier_select")
        supplier_id = int(selected_supplier.split('(')[-1].split(')')[0])
        
        # 선택된 공급업체 정보 표시
        selected_supplier_data = suppliers_df[suppliers_df['id'] == supplier_id].iloc[0]
        with st.expander("공급업체 정보", expanded=False):
            st.write(f"담당자: {selected_supplier_data.get('contact_person', 'N/A')}")
            st.write(f"이메일: {selected_supplier_data.get('email', 'N/A')}")
            st.write(f"전화: {selected_supplier_data.get('phone', 'N/A')}")
            st.write(f"주소: {selected_supplier_data.get('address', 'N/A')}")
    
    with col2:
        # 영업 프로세스 연동 (선택 사항)
        if not sales_processes_df.empty:
            process_options = ["직접 입력"] + [f"{row['process_number']} - {row['customer_company']}" for _, row in sales_processes_df.iterrows()]
            selected_process = st.selectbox("연관 영업 프로세스 (선택사항)", process_options)
            
            if selected_process != "직접 입력":
                process_number = selected_process.split(' - ')[0]
                process_data = sales_processes_df[sales_processes_df['process_number'] == process_number].iloc[0]
                st.info(f"고객: {process_data.get('customer_company', 'N/A')}")
                st.info(f"제품: {process_data.get('item_description', 'N/A')}")
        else:
            selected_process = "직접 입력"
            st.info("등록된 영업 프로세스가 없습니다.")
    
    # === 제품 선택 및 가격 정보 ===
    st.subheader("제품 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        product_options = [f"{row['product_code']} - {row['product_name_en']}" for _, row in products_df.iterrows()]
        selected_product = st.selectbox("제품 선택", product_options, key="sales_order_product_select")
        product_code = selected_product.split(' - ')[0]
        
        selected_product_data = products_df[products_df['product_code'] == product_code].iloc[0]
        
        # 제품 정보 표시
        st.text_input("제품 코드", value=selected_product_data['product_code'], disabled=True)
        st.text_input("제품명 (영문)", value=selected_product_data['product_name_en'], disabled=True)
        st.text_input("제품명 (베트남어)", value=selected_product_data.get('product_name_vn', ''), disabled=True)
    
    with col2:
        # 발주 수량 및 가격
        quantity = st.number_input("발주 수량", min_value=1, value=1, key="sales_order_quantity")
        
        # 기본 원가 정보 표시
        cost_price_usd = float(selected_product_data.get('cost_price_usd', 0))
        if cost_price_usd > 0:
            st.info(f"🏷️ 참고 원가: ${cost_price_usd:,.2f} USD")
        
        # 발주 단가 입력
        currency = st.selectbox("통화", ['USD', 'VND', 'CNY'], index=0, key="sales_order_currency")
        
        if currency == 'USD':
            unit_price = st.number_input("발주 단가 (USD)", min_value=0.0, value=cost_price_usd, format="%.2f")
        elif currency == 'VND':
            exchange_rate = 24000  # USD to VND
            unit_price_vnd = cost_price_usd * exchange_rate
            unit_price = st.number_input("발주 단가 (VND)", min_value=0.0, value=unit_price_vnd, format="%.0f")
        else:  # CNY
            exchange_rate = 7.2  # USD to CNY
            unit_price_cny = cost_price_usd * exchange_rate
            unit_price = st.number_input("발주 단가 (CNY)", min_value=0.0, value=unit_price_cny, format="%.2f")
        
        # 총 발주 금액 계산
        total_amount = quantity * unit_price
        st.metric("총 발주 금액", f"{total_amount:,.2f} {currency}")

    # === 폼 영역 ===
    with st.form("sales_order_form"):
        # === 기본 정보 ===
        st.subheader("발주 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            order_number = generate_sales_order_number()
            st.text_input("발주번호", value=order_number, disabled=True)
            order_date = st.date_input("발주일", value=datetime.now().date())
        
        with col2:
            expected_delivery_date = st.date_input("납기 예정일", value=datetime.now().date() + timedelta(days=30))
            priority = st.selectbox("우선순위", ['낮음', '보통', '높음', '긴급'], index=1)
        
        # === 프로젝트 정보 ===
        st.subheader("프로젝트 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            customer_project = st.text_input("고객 프로젝트명")
            project_reference = st.text_input("프로젝트 참조번호")
        
        with col2:
            delivery_address = st.text_area("배송 주소")
            special_instructions = st.text_area("특별 지시사항")
        
        # === 결제 조건 ===
        st.subheader("거래 조건")
        col1, col2 = st.columns(2)
        
        with col1:
            payment_terms = st.selectbox("결제 조건", 
                ["현금 결제", "30일 후 결제", "60일 후 결제", "계약 체결 후 협의"])
            delivery_terms = st.selectbox("배송 조건", 
                ["FOB", "CIF", "EXW", "DDP"])
        
        with col2:
            quality_requirements = st.text_area("품질 요구사항")
            notes = st.text_area("비고")
        
        # === 저장 버튼 ===
        submitted = st.form_submit_button("📋 발주서 작성 완료", type="primary")
        
        if submitted:
            # 폼 밖의 값들을 다시 가져오기
            quantity = st.session_state.get("sales_order_quantity", 1)
            currency = st.session_state.get("sales_order_currency", "USD")
            
            # 발주서 데이터 준비
            sales_order_data = {
                # 기본 정보
                'sales_order_number': order_number,
                'supplier_id': supplier_id,
                'supplier_name': selected_supplier_data['company_name'],
                'supplier_contact': selected_supplier_data.get('contact_person'),
                'supplier_email': selected_supplier_data.get('email'),
                'supplier_phone': selected_supplier_data.get('phone'),
                'supplier_address': selected_supplier_data.get('address'),
                
                # 제품 정보
                'item_code': selected_product_data['product_code'],
                'item_name': selected_product_data['product_name_en'],
                'item_name_vn': selected_product_data.get('product_name_vn', ''),
                'quantity': quantity,
                'unit_price': unit_price,
                'currency': currency,
                'total_amount': total_amount,
                
                # 일정 정보
                'order_date': order_date.isoformat(),
                'expected_delivery_date': expected_delivery_date.isoformat(),
                'priority': priority,
                
                # 프로젝트 정보
                'customer_project': customer_project if customer_project.strip() else None,
                'project_reference': project_reference if project_reference.strip() else None,
                'delivery_address': delivery_address if delivery_address.strip() else None,
                'special_instructions': special_instructions if special_instructions.strip() else None,
                
                # 거래 조건
                'payment_terms': payment_terms,
                'delivery_terms': delivery_terms,
                'quality_requirements': quality_requirements if quality_requirements.strip() else None,
                
                # 상태 관리
                'status': '발주완료',
                'notes': notes if notes.strip() else None,
                
                # 영업 프로세스 연동
                'related_process': selected_process if selected_process != "직접 입력" else None,
                
                # 시스템 정보
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # 저장 실행
            if save_func('sales_orders', sales_order_data):
                st.success("발주서가 성공적으로 작성되었습니다!")
                st.balloons()
                
                # 저장된 정보 요약 표시
                with st.expander("저장된 발주서 정보", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"발주번호: {order_number}")
                        st.write(f"공급업체: {selected_supplier_data['company_name']}")
                        st.write(f"제품: {selected_product_data['product_name_en']}")
                        st.write(f"수량: {quantity:,}")
                    with col2:
                        st.write(f"단가: {unit_price:,.2f} {currency}")
                        st.write(f"총액: {total_amount:,.2f} {currency}")
                        st.write(f"납기: {expected_delivery_date}")
                        st.write(f"우선순위: {priority}")
                
                st.rerun()
            else:
                st.error("발주서 저장에 실패했습니다.")

def render_sales_order_list(load_func, update_func, delete_func):
    """영업 발주 목록"""
    st.header("발주서 목록")
    
    try:
        # 데이터 로드
        sales_orders_data = load_func('sales_orders')
        suppliers_data = load_func('suppliers')
        
        # DataFrame 변환
        sales_orders_df = pd.DataFrame(sales_orders_data) if sales_orders_data else pd.DataFrame()
        suppliers_df = pd.DataFrame(suppliers_data) if suppliers_data else pd.DataFrame()
        
        if sales_orders_df.empty:
            st.info("등록된 발주서가 없습니다.")
            return
        
        # 공급업체명 매핑
        supplier_dict = suppliers_df.set_index('id')['company_name'].to_dict() if not suppliers_df.empty else {}
        sales_orders_df['supplier_company'] = sales_orders_df['supplier_id'].map(supplier_dict).fillna(sales_orders_df['supplier_name'])
        
        # 검색 기능
        search_term = st.text_input("검색 (발주번호, 공급업체명, 제품명)")
        
        if search_term:
            mask = (
                sales_orders_df['sales_order_number'].str.contains(search_term, case=False, na=False) |
                sales_orders_df['supplier_company'].str.contains(search_term, case=False, na=False) |
                sales_orders_df['item_name'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = sales_orders_df[mask]
        else:
            filtered_df = sales_orders_df
        
        st.write(f"총 {len(filtered_df)}개의 발주서")
        
        # 발주서 목록 표시
        for idx, row in filtered_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{row['sales_order_number']}**")
                    st.caption(f"발주일: {row.get('order_date', 'N/A')}")
                
                with col2:
                    st.write(f"공급업체: {row['supplier_company']}")
                    st.caption(f"제품: {row.get('item_name', 'N/A')}")
                
                with col3:
                    st.write(f"수량: {row.get('quantity', 0):,}")
                    total_amount = row.get('total_amount', 0)
                    currency = row.get('currency', 'USD')
                    st.write(f"총액: {total_amount:,.2f} {currency}")
                
                with col4:
                    status = row.get('status', '발주완료')
                    status_colors = {
                        '발주완료': '#1f77b4',
                        '제작중': '#ff7f0e',
                        '배송중': '#2ca02c',
                        '입고완료': '#2ca02c',
                        '취소': '#d62728'
                    }
                    color = status_colors.get(status, '#808080')
                    st.markdown(f"<span style='color: {color}'>● {status}</span>", unsafe_allow_html=True)
                    
                    # 상태 변경
                    new_status = st.selectbox(
                        "상태 변경",
                        ['발주완료', '제작중', '배송중', '입고완료', '취소'],
                        index=['발주완료', '제작중', '배송중', '입고완료', '취소'].index(status),
                        key=f"sales_order_status_{idx}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != status and st.button("변경", key=f"sales_order_update_{idx}"):
                        update_data = {
                            'id': row['id'],
                            'status': new_status,
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        try:
                            success = update_func('sales_orders', update_data)
                            if success:
                                st.success("상태가 변경되었습니다.")
                                st.rerun()
                            else:
                                st.error("상태 변경 실패")
                        except Exception as e:
                            st.error(f"상태 변경 오류: {str(e)}")
                
                # 상세 정보
                with st.expander(f"{row['sales_order_number']} 상세 정보", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"단가: {row.get('unit_price', 0):,.2f} {currency}")
                        st.write(f"납기: {row.get('expected_delivery_date', 'N/A')}")
                        st.write(f"우선순위: {row.get('priority', 'N/A')}")
                        if row.get('customer_project'):
                            st.write(f"고객 프로젝트: {row['customer_project']}")
                        if row.get('payment_terms'):
                            st.write(f"결제 조건: {row['payment_terms']}")
                    
                    with col2:
                        if row.get('delivery_terms'):
                            st.write(f"배송 조건: {row['delivery_terms']}")
                        if row.get('special_instructions'):
                            st.write(f"특별 지시: {row['special_instructions']}")
                        if row.get('quality_requirements'):
                            st.write(f"품질 요구: {row['quality_requirements']}")
                        if row.get('notes'):
                            st.write(f"비고: {row['notes']}")
                
                st.markdown("---")
        
        # 통계 정보
        if not filtered_df.empty:
            st.markdown("---")
            st.subheader("통계")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 발주서", len(filtered_df))
            
            with col2:
                # USD 기준으로 통합 계산
                total_usd = 0
                for _, row in filtered_df.iterrows():
                    amount = row.get('total_amount', 0)
                    currency = row.get('currency', 'USD')
                    if currency == 'USD':
                        total_usd += amount
                    elif currency == 'VND':
                        total_usd += amount / 24000
                    elif currency == 'CNY':
                        total_usd += amount / 7.2
                st.metric("총 발주 금액", f"${total_usd:,.2f} USD")
            
            with col3:
                completed_count = len(filtered_df[filtered_df['status'] == '입고완료'])
                st.metric("입고 완료", completed_count)
            
            with col4:
                completion_rate = (completed_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
                st.metric("완료율", f"{completion_rate:.1f}%")
        
    except Exception as e:
        logging.error(f"발주서 목록 오류: {str(e)}")
        st.error(f"발주서 목록 로딩 중 오류: {str(e)}")

def render_sales_order_print(load_func):
    """발주서 인쇄 기능"""
    st.header("발주서 인쇄")
    
    try:
        sales_orders_data = load_func('sales_orders')
        if not sales_orders_data:
            st.info("인쇄할 발주서가 없습니다.")
            return
        
        sales_orders_df = pd.DataFrame(sales_orders_data)
        
        # 발주서 선택
        order_options = [f"{row['sales_order_number']} - {row.get('supplier_name', 'N/A')}" for _, row in sales_orders_df.iterrows()]
        selected_order = st.selectbox("인쇄할 발주서 선택", order_options)
        
        if selected_order:
            order_number = selected_order.split(' - ')[0]
            selected_sales_order = sales_orders_df[sales_orders_df['sales_order_number'] == order_number].iloc[0]
            
            # 언어 선택
            language = st.selectbox("언어 선택", ['한국어', 'English', 'Tiếng Việt'])
            
            # 미리보기 및 다운로드
            if st.button("HTML 다운로드", type="primary"):
                html_content = generate_sales_order_html(selected_sales_order, load_func, language)
                
                st.download_button(
                    label="HTML 파일 다운로드",
                    data=html_content,
                    file_name=f"{order_number}_{language}.html",
                    mime="text/html"
                )
                
                st.success("HTML 파일이 준비되었습니다!")
                
                # 미리보기
                with st.expander("미리보기", expanded=True):
                    st.components.v1.html(html_content, height=800, scrolling=True)
    
    except Exception as e:
        st.error(f"인쇄 기능 오류: {str(e)}")

def generate_sales_order_number():
    """발주번호 자동 생성"""
    today = datetime.now()
    return f"SO{today.strftime('%y%m%d')}-{today.strftime('%H%M%S')}"

def generate_sales_order_html(sales_order, load_func, language='한국어'):
    """발주서 HTML 생성 (견적서 양식 기반, 공급업체 정보로 변경)"""
    try:
        # 공급업체 정보는 sales_order에 이미 저장되어 있음
        supplier_info = {
            'company_name': sales_order.get('supplier_name', '[공급업체명]'),
            'address': sales_order.get('supplier_address', '[공급업체 주소]'),
            'contact_person': sales_order.get('supplier_contact', '[담당자명]'),
            'phone': sales_order.get('supplier_phone', '[전화번호]'),
            'email': sales_order.get('supplier_email', '[이메일]')
        }
        
        # HTML 템플릿 (견적서 기반으로 발주서 양식 생성)
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Purchase Order - {sales_order.get('sales_order_number', '')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        
        .purchase-order {{
            width: 210mm;
            min-height: 297mm;
            margin: 20px auto;
            background: white;
            padding: 15mm;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }}
        
        .content-area {{
            flex: 1;
        }}
        
        .bottom-fixed {{
            margin-top: auto;
        }}
        
        .header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #000;
        }}
        
        .company-name {{
            font-size: 18px;
            font-weight: bold;
        }}
        
        .company-info {{
            font-size: 12px;
            line-height: 1.4;
        }}
        
        .order-info {{
            text-align: right;
            font-size: 12px;
        }}
        
        .office-info {{
            margin-top: 10px;
            font-size: 11px;
        }}
        
        .order-details {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            font-size: 12px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 11px;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        
        .text-left {{
            text-align: left;
        }}
        
        .text-right {{
            text-align: right;
        }}
        
        .totals {{
            margin-top: 20px;
        }}
        
        .totals table {{
            width: 300px;
            margin-left: auto;
        }}
        
        .total-row {{
            background-color: #e9ecef;
            font-weight: bold;
        }}
        
        .project-info {{
            margin-top: 30px;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
        
        .project-table {{
            width: 100%;
            font-size: 11px;
        }}
        
        .project-table td {{
            padding: 8px;
            border: 1px solid #ddd;
            vertical-align: middle;
        }}
        
        .project-table td:nth-child(1) {{
            width: 20%;
            font-weight: bold;
            background-color: #f8f9fa;
        }}
        
        .project-table td:nth-child(2) {{
            width: 30%;
        }}
        
        .project-table td:nth-child(3) {{
            width: 20%;
            font-weight: bold;
            background-color: #f8f9fa;
        }}
        
        .project-table td:nth-child(4) {{
            width: 30%;
        }}
        
        .signature-section {{
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
        }}
        
        .signature-box {{
            text-align: center;
            width: 200px;
            position: relative;
        }}
        
        .signature-line {{
            border-bottom: 1px solid #000;
            margin: 30px 0 10px 0;
            height: 1px;
        }}
        
        .stamp-image {{
            position: absolute;
            top: -60px;
            left: 50%;
            transform: translateX(-50%) rotate(-15deg);
            width: 120px;
            height: 120px;
            opacity: 0.8;
        }}
        
        @media print {{
            body {{
                background: white;
                margin: 0;
                padding: 0;
            }}
            .purchase-order {{
                width: 210mm;
                min-height: 297mm;
                margin: 0;
                padding: 15mm;
                box-shadow: none;
                page-break-after: always;
            }}
            @page {{
                size: A4;
                margin: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="purchase-order">
        <div class="content-area">
            <!-- 헤더 -->
            <div class="header">
                <!-- 공급업체 정보 영역 -->
                <div>
                    <div class="company-name">{supplier_info.get('company_name', '[공급업체명]')}</div>
                    <div class="company-info">
                        Address: {supplier_info.get('address', '[공급업체 주소]')}<br><br>
                        Contact Person: {supplier_info.get('contact_person', '[담당자명]')}<br>
                        Phone No.: {supplier_info.get('phone', '[전화번호]')}<br>
                        E-mail: {supplier_info.get('email', '[이메일]')}
                    </div>
                </div>
                
                <div>
                    <div class="company-name">YUMOLD VIETNAM CO., LTD</div>
                    <div class="company-info">
                        Tax Code (MST): 0111146237<br>
                        <div class="office-info">
                            <strong>Hanoi Accounting Office:</strong><br>
                            Room 1201-2, 12th Floor, Keangnam Hanoi Landmark 72, E6 Area,<br>
                            Yen Hoa Ward, Hanoi City
                        </div>
                        <div class="office-info">
                            <strong>Bac Ninh Sales Office:</strong><br>
                            6th Floor, No. 255 Le Thanh Tong Street, Vo Cuong Ward, Bac Ninh<br>
                            Province
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 발주 정보 -->
            <div class="order-details">
                <div>Date: {sales_order.get('order_date', '')}</div>
                <div>Purchase Order No.: {sales_order.get('sales_order_number', '')}</div>
                <div>Expected Delivery: {sales_order.get('expected_delivery_date', '')}</div>
                <div>Currency: {sales_order.get('currency', 'USD')}</div>
            </div>
            
            <!-- 항목 테이블 -->
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">NO</th>
                        <th style="width: 15%;">Item Code</th>
                        <th style="width: 25%;">Description</th>
                        <th style="width: 10%;">Qty.</th>
                        <th style="width: 15%;">Unit Price</th>
                        <th style="width: 15%;">Amount</th>
                        <th style="width: 15%;">Priority</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>{sales_order.get('item_code', '')}</td>
                        <td class="text-left">
                            <strong>{sales_order.get('item_name', '')}</strong><br>
                            <span style="font-style: italic; color: #666;">{sales_order.get('item_name_vn', '')}</span>
                        </td>
                        <td>{sales_order.get('quantity', 1):,}</td>
                        <td class="text-right">{sales_order.get('unit_price', 0):,.2f}</td>
                        <td class="text-right">{sales_order.get('total_amount', 0):,.2f}</td>
                        <td>{sales_order.get('priority', '보통')}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- 하단 고정 영역 -->
        <div class="bottom-fixed">
            <!-- 합계 -->
            <div class="totals">
                <table>
                    <tr class="total-row">
                        <td class="text-right">TOTAL {sales_order.get('currency', 'USD')}</td>
                        <td>{sales_order.get('currency', 'USD')}</td>
                        <td class="text-right">{sales_order.get('total_amount', 0):,.2f}</td>
                    </tr>
                </table>
            </div>
            
            <!-- 프로젝트 정보 -->
            <div class="project-info">
                <table class="project-table">
                    <tr>
                        <td>Customer Project:</td>
                        <td>{sales_order.get('customer_project', '')}</td>
                        <td>Project Reference:</td>
                        <td>{sales_order.get('project_reference', '')}</td>
                    </tr>
                    <tr>
                        <td>Payment Terms:</td>
                        <td>{sales_order.get('payment_terms', '')}</td>
                        <td>Delivery Terms:</td>
                        <td>{sales_order.get('delivery_terms', '')}</td>
                    </tr>
                    <tr>
                        <td>Delivery Address:</td>
                        <td colspan="3">{sales_order.get('delivery_address', '')}</td>
                    </tr>
                    <tr>
                        <td>Quality Requirements:</td>
                        <td colspan="3">{sales_order.get('quality_requirements', '')}</td>
                    </tr>
                    <tr>
                        <td>Special Instructions:</td>
                        <td colspan="3">{sales_order.get('special_instructions', '')}</td>
                    </tr>
                    <tr>
                        <td>Notes:</td>
                        <td colspan="3">{sales_order.get('notes', '')}</td>
                    </tr>
                </table>
            </div>
            
            <!-- 발주처 이름 -->
            <div style="text-align: center; margin: 30px 0; font-size: 16px; font-weight: bold;">
                YUMOLD VIETNAM CO., LTD
            </div>
            
            <!-- 서명란 -->
            <div class="signature-section">
                <div class="signature-box">
                    <div>Purchaser Signature</div>
                    <div class="signature-line"></div>
                    <!-- 이미지 파일로 스탬프 표시 -->
                    <img src="assets/stamp.png" class="stamp-image" alt="Company Stamp" />
                </div>
                <div class="signature-box">
                    <div>Supplier Signature</div>
                    <div class="signature-line"></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
        
    except Exception as e:
        logging.error(f"발주서 HTML 생성 오류: {str(e)}")
        return f"<html><body><h1>오류: {str(e)}</h1></body></html>"