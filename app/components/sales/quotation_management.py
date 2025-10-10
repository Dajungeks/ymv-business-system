import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging


def show_quotation_management(load_func, save_func, update_func, delete_func):
    """견적서 관리 메인 페이지"""
    st.title("견적서 관리")
    
    # 수정 모드 확인
    is_editing = st.session_state.get('editing_quotation_id') is not None
    
    if is_editing:
        # 수정 모드일 때는 견적서 작성 폼만 표시
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("⬅️ 목록으로", use_container_width=True):
                st.session_state.pop('editing_quotation_id', None)
                st.session_state.pop('editing_quotation_data', None)
                st.session_state.pop('active_tab', None)
                st.rerun()
        with col2:
            editing_data = st.session_state.get('editing_quotation_data', {})
            st.info(f"📝 견적서 수정 모드: {editing_data.get('quote_number', '')} ({editing_data.get('revision_number', 'Rv00')})")
        
        st.markdown("---")
        render_quotation_form(save_func, load_func)
    else:
        # 일반 모드일 때는 모든 탭 표시
        tab1, tab2, tab3, tab4 = st.tabs(["견적서 작성", "견적서 목록", "견적서 인쇄", "CSV 관리"])
        
        with tab1:
            render_quotation_form(save_func, load_func)
        
        with tab2:
            render_quotation_list(load_func, update_func, delete_func, save_func)
        
        with tab3:
            render_quotation_print(load_func)
        
        with tab4:
            render_quotation_csv_management(load_func, save_func)

def render_quotation_form(save_func, load_func):
    """완전 개선된 견적서 작성 폼 - 수정 모드 지원"""
    
    # 수정 모드 확인
    is_editing = st.session_state.get('editing_quotation_id') is not None
    editing_data = st.session_state.get('editing_quotation_data', {})
    
    if is_editing:
        st.header("견적서 수정")
    else:
        st.header("새 견적서 작성")
    
    # 기본 데이터 로드
    customers_data = load_func('customers')
    employees_data = load_func('employees')
    products_data = load_func('products')
    
    # DataFrame 변환
    customers_df = pd.DataFrame(customers_data) if customers_data else pd.DataFrame()
    employees_df = pd.DataFrame(employees_data) if employees_data else pd.DataFrame()
    products_df = pd.DataFrame(products_data) if products_data else pd.DataFrame()
    
    # 데이터 확인
    if customers_df.empty:
        st.warning("등록된 고객이 없습니다.")
        if st.button("고객 관리로 이동"):
            st.session_state.current_page = "고객 관리"
            st.rerun()
        return
    
    if employees_df.empty:
        st.warning("등록된 직원이 없습니다.")
        return
    
    if products_df.empty:
        st.warning("등록된 제품이 없습니다.")
        return
    
    # === 실시간 업데이트를 위한 고객 선택 (폼 밖에서) ===
    st.subheader("고객 및 담당자")
    col1, col2 = st.columns(2)
    
    with col1:
        # 고객명 표시 (짧은 이름 우선)
        customer_options = [
            f"{row.get('company_name_short') or row.get('company_name_original')} ({row['id']})" 
            for _, row in customers_df.iterrows()
        ]
        
        # 수정 모드일 때 기존 고객 선택
        default_customer_index = 0
        if is_editing and editing_data.get('customer_id'):
            try:
                default_customer_index = next(
                    i for i, opt in enumerate(customer_options) 
                    if f"({editing_data['customer_id']})" in opt
                )
            except:
                default_customer_index = 0
        
        selected_customer = st.selectbox(
            "고객사", 
            customer_options, 
            index=default_customer_index,
            key="quotation_customer_select"
        )
        customer_id = int(selected_customer.split('(')[-1].split(')')[0])
        
        # 선택된 고객 정보 표시 (실시간 업데이트)
        selected_customer_data = customers_df[customers_df['id'] == customer_id].iloc[0]
        with st.expander("고객 정보", expanded=False):
            st.write(f"담당자: {selected_customer_data.get('contact_person', 'N/A')}")
            st.write(f"이메일: {selected_customer_data.get('email', 'N/A')}")
            st.write(f"전화: {selected_customer_data.get('phone', 'N/A')}")
            st.write(f"주소: {selected_customer_data.get('address', 'N/A')}")
    
    with col2:
        employee_options = [f"{row['name']} ({row['department']}) [{row['id']}]" for _, row in employees_df.iterrows()]
        
        # 수정 모드일 때 기존 직원 선택
        default_employee_index = 0
        if is_editing and editing_data.get('sales_rep_id'):
            try:
                default_employee_index = next(
                    i for i, opt in enumerate(employee_options) 
                    if f"[{editing_data['sales_rep_id']}]" in opt
                )
            except:
                default_employee_index = 0
        
        selected_employee = st.selectbox(
            "영업담당자", 
            employee_options,
            index=default_employee_index,
            key="quotation_employee_select"
        )
        sales_rep_id = int(selected_employee.split('[')[-1].split(']')[0])
    
    # === 실시간 업데이트를 위한 제품 선택 (폼 밖에서) ===
    st.subheader("제품 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        product_options = [f"{row['product_code']} - {row['product_name_en']}" for _, row in products_df.iterrows()]
        
        # 수정 모드일 때 기존 제품 선택
        default_product_index = 0
        if is_editing and editing_data.get('item_code'):
            try:
                default_product_index = next(
                    i for i, opt in enumerate(product_options) 
                    if editing_data['item_code'] in opt
                )
            except:
                default_product_index = 0
        
        selected_product = st.selectbox(
            "제품 선택", 
            product_options,
            index=default_product_index,
            key="quotation_product_select"
        )
        product_code = selected_product.split(' - ')[0]
        
        selected_product_data = products_df[products_df['product_code'] == product_code].iloc[0]
        
        # 제품 정보 표시 (읽기 전용)
        st.text_input("제품 코드", value=selected_product_data['product_code'], disabled=True)
        st.text_input("제품명 (영문)", value=selected_product_data['product_name_en'], disabled=True)
        st.text_input("제품명 (베트남어)", value=selected_product_data.get('product_name_vn', ''), disabled=True)
    
    with col2:
        # 원가 정보 표시 (정확한 컬럼명 사용)
        cost_price_usd = float(selected_product_data.get('cost_price_usd', 0))
        if cost_price_usd > 0:
            st.info(f"🏷️ 제품 원가: ${cost_price_usd:,.2f} USD")
        else:
            st.warning("⚠️ 원가 정보가 설정되지 않았습니다")
        
        # 수량 및 가격 (VND 기준)
        quantity = st.number_input(
            "수량", 
            min_value=1, 
            value=int(editing_data.get('quantity') or 1) if is_editing else 1,
            key="quotation_quantity"
        )
        
        # USD 표준가격을 VND로 변환 (환율 적용)
        std_price_usd = float(selected_product_data.get('unit_price', 0))
        exchange_rate = st.number_input(
            "USD → VND 환율", 
            min_value=1000.0, 
            value=float(editing_data.get('exchange_rate') or 24000.0) if is_editing else 24000.0,
            step=100.0, 
            format="%.0f", 
            key="exchange_rate"
        )
        
        # VND 판매가 계산
        std_price_vnd = std_price_usd * exchange_rate
        unit_price_vnd = st.number_input(
            "표준가격 (VND)", 
            min_value=0.0, 
            value=float(editing_data.get('unit_price_vnd') or std_price_vnd) if is_editing else std_price_vnd,
            format="%.0f", 
            key="quotation_unit_price_vnd"
        )
        
        # USD로도 표시
        unit_price_usd = unit_price_vnd / exchange_rate
        st.caption(f"💱 USD 기준: ${unit_price_usd:,.2f}")
        
        discount_rate = st.number_input(
            "할인율 (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=float(editing_data.get('discount_rate') or 0.0) if is_editing else 0.0,
            format="%.1f", 
            key="quotation_discount"
        )
        
        # VAT율 선택
        vat_rate = st.selectbox(
            "VAT율 (%)", 
            [0.0, 7.0, 10.0], 
            index=1 if not is_editing else ([0.0, 7.0, 10.0].index(editing_data.get('vat_rate') or 7.0) if (editing_data.get('vat_rate') or 7.0) in [0.0, 7.0, 10.0] else 1),
            key="quotation_vat"
        )
        
        # 실시간 가격 계산 표시 (VND 기준)
        if quantity > 0 and unit_price_vnd > 0:
            discounted_price_vnd = unit_price_vnd * (1 - discount_rate / 100)
            subtotal_vnd = quantity * discounted_price_vnd
            vat_amount_vnd = subtotal_vnd * (vat_rate / 100)
            final_amount_vnd = subtotal_vnd + vat_amount_vnd
            
            # USD 기준 계산
            discounted_price_usd = discounted_price_vnd / exchange_rate
            subtotal_usd = subtotal_vnd / exchange_rate
            final_amount_usd = final_amount_vnd / exchange_rate
            
            st.markdown("**💰 가격 계산 (VND)**")
            st.write(f"할인 후 단가: {discounted_price_vnd:,.0f} VND")
            st.write(f"소계: {subtotal_vnd:,.0f} VND")
            st.write(f"VAT ({vat_rate}%): {vat_amount_vnd:,.0f} VND")
            st.write(f"**최종 금액: {final_amount_vnd:,.0f} VND**")
            
            # USD 참고가 표시
            st.caption(f"💱 USD 참고: ${final_amount_usd:,.2f}")
            
            # 마진 계산 (원가가 있는 경우)
            if cost_price_usd > 0:
                margin = ((discounted_price_usd - cost_price_usd) / discounted_price_usd) * 100
                margin_amount_usd = discounted_price_usd - cost_price_usd
                margin_amount_vnd = margin_amount_usd * exchange_rate
                
                if margin > 0:
                    st.success(f"📈 마진율: {margin:.1f}% (${margin_amount_usd:,.2f} = {margin_amount_vnd:,.0f} VND)")
                else:
                    st.error(f"📉 손실: {abs(margin):.1f}% (${abs(margin_amount_usd):,.2f} = {abs(margin_amount_vnd):,.0f} VND)")
            else:
                st.info("💡 원가 정보가 없어 마진을 계산할 수 없습니다")

    # === 폼 영역 (나머지 정보 입력) ===
    with st.form("quotation_form"):
        # === 기본 정보 ===
        st.subheader("기본 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            if is_editing:
                quote_number = editing_data.get('quote_number', '')
                st.text_input("견적번호", value=quote_number, disabled=True)
            else:
                quote_number = generate_quote_number(load_func)
                st.text_input("견적번호", value=quote_number, disabled=True)
            
            quote_date = st.date_input(
                "견적일", 
                value=datetime.fromisoformat(editing_data.get('quote_date')) if is_editing and editing_data.get('quote_date') else datetime.now().date()
            )
        
        with col2:
            valid_until = st.date_input(
                "유효기간", 
                value=datetime.fromisoformat(editing_data.get('valid_until')) if is_editing and editing_data.get('valid_until') else datetime.now().date() + timedelta(days=30)
            )
            currency = st.selectbox("통화", ['VND', 'USD', 'KRW'], index=0)
        
        # === 프로젝트 정보 ===
        st.subheader("프로젝트 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "프로젝트명",
                value=editing_data.get('project_name', '') if is_editing else ''
            )
            part_name = st.text_input(
                "부품명",
                value=editing_data.get('part_name', '') if is_editing else ''
            )
            mold_number = st.text_input(
                "금형번호",
                value=editing_data.get('mold_number', editing_data.get('mold_no', '')) if is_editing else ''
            )
            part_weight = st.number_input(
                "부품 중량(g)", 
                min_value=0.0, 
                value=float(editing_data.get('part_weight') or 0.0) if is_editing else 0.0,
                format="%.2f"
            )
        
        with col2:
            hrs_info = st.text_input(
                "HRS 정보",
                value=editing_data.get('hrs_info', '') if is_editing else ''
            )
            resin_type = st.text_input(
                "수지 종류",
                value=editing_data.get('resin_type', '') if is_editing else ''
            )
            resin_additive = st.text_input(
                "수지 첨가제",
                value=editing_data.get('resin_additive', '') if is_editing else ''
            )
            sol_material = st.text_input(
                "솔/재료",
                value=editing_data.get('sol_material', '') if is_editing else ''
            )
        
        # === 거래 조건 ===
        st.subheader("거래 조건")
        col1, col2 = st.columns(2)
        
        with col1:
            payment_terms = st.text_area(
                "결제 조건", 
                value=editing_data.get('payment_terms', '계약 체결 후 협의') if is_editing else "계약 체결 후 협의"
            )
            
            # 납기일 입력 여부 선택
            has_delivery_date = st.checkbox(
                "납기일 입력", 
                value=True if (is_editing and editing_data.get('delivery_date')) else False
            )
            
            if has_delivery_date:
                delivery_date = st.date_input(
                    "납기일", 
                    value=datetime.fromisoformat(editing_data.get('delivery_date')) if is_editing and editing_data.get('delivery_date') else datetime.now().date() + timedelta(days=30)
                )
            else:
                delivery_date = None
                st.info("💡 납기일 미입력")
        
        with col2:
            lead_time_days = st.number_input(
                "리드타임(일)", 
                min_value=0, 
                value=int(editing_data.get('lead_time_days') or 30) if is_editing else 30
            )
            remarks = st.text_area(
                "비고",
                value=editing_data.get('remarks', editing_data.get('remark', '')) if is_editing else ''
            )
        
        # === 저장 버튼 ===
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        if is_editing:
            # 수정 모드
            with col1:
                save_btn = st.form_submit_button("💾 수정 저장 (Revision 증가)", type="primary", use_container_width=True)
            with col2:
                cancel_btn = st.form_submit_button("❌ 취소", use_container_width=True)
            
            if save_btn:
                # Revision 번호 증가
                current_revision = editing_data.get('revision_number', 'Rv00')
                new_revision = get_next_revision_number(current_revision)
                
                # 폼 밖의 값들을 다시 가져오기
                quantity = st.session_state.get("quotation_quantity", 1)
                unit_price_vnd = st.session_state.get("quotation_unit_price_vnd", 0)
                discount_rate = st.session_state.get("quotation_discount", 0)
                vat_rate = st.session_state.get("quotation_vat", 7.0)
                exchange_rate = st.session_state.get("exchange_rate", 24000)
                
                # VND 기준 계산
                discounted_price_vnd = unit_price_vnd * (1 - discount_rate / 100)
                subtotal_vnd = quantity * discounted_price_vnd
                vat_amount_vnd = subtotal_vnd * (vat_rate / 100)
                final_amount_vnd = subtotal_vnd + vat_amount_vnd
                
                # USD 기준 계산 (참고용)
                unit_price_usd = unit_price_vnd / exchange_rate
                discounted_price_usd = discounted_price_vnd / exchange_rate
                subtotal_usd = subtotal_vnd / exchange_rate
                final_amount_usd = final_amount_vnd / exchange_rate
                
                # 마진 계산
                margin = None
                if cost_price_usd > 0:
                    margin = ((discounted_price_usd - cost_price_usd) / discounted_price_usd) * 100
                
                # 고객 회사명 (공식 이름 사용 - 견적서용)
                customer_company_name = selected_customer_data.get('company_name_original')
                
                # 업데이트 데이터 준비
                quotation_data = {
                    'id': editing_data['id'],
                    
                    # 필수 컬럼들 (NOT NULL)
                    'customer_name': customer_company_name,
                    'company': customer_company_name,
                    'quote_date': quote_date.isoformat(),
                    'valid_until': valid_until.isoformat(),
                    'item_name': selected_product_data['product_name_en'],
                    'quantity': quantity,
                    'unit_price': unit_price_vnd,
                    
                    # 고객 정보
                    'customer_id': customer_id,
                    'contact_person': selected_customer_data.get('contact_person'),
                    'email': selected_customer_data.get('email'),
                    'phone': selected_customer_data.get('phone'),
                    'customer_address': selected_customer_data.get('address'),
                    
                    # 견적서 기본 정보
                    'quote_number': editing_data['quote_number'],  # 기존 번호 유지
                    'revision_number': new_revision,  # Revision 증가
                    'currency': 'VND',
                    'status': editing_data.get('status', 'Draft'),
                    'sales_rep_id': sales_rep_id,
                    
                    # 제품 정보
                    'item_code': selected_product_data['product_code'],
                    'item_name_en': selected_product_data['product_name_en'],
                    'item_name_vn': selected_product_data.get('product_name_vn', ''),
                    
                    # 가격 정보
                    'std_price': unit_price_vnd,
                    'unit_price_vnd': unit_price_vnd,
                    'unit_price_usd': unit_price_usd,
                    'discount_rate': discount_rate,
                    'discounted_price': discounted_price_vnd,
                    'discounted_price_vnd': discounted_price_vnd,
                    'discounted_price_usd': discounted_price_usd,
                    'vat_rate': vat_rate,
                    'vat_amount': vat_amount_vnd,
                    'final_amount': final_amount_vnd,
                    'final_amount_usd': final_amount_usd,
                    'exchange_rate': exchange_rate,
                    
                    # 프로젝트 정보
                    'project_name': project_name if project_name.strip() else None,
                    'part_name': part_name if part_name.strip() else None,
                    'mold_no': mold_number if mold_number.strip() else None,
                    'mold_number': mold_number if mold_number.strip() else None,
                    'part_weight': part_weight if part_weight > 0 else None,
                    'hrs_info': hrs_info if hrs_info.strip() else None,
                    'resin_type': resin_type if resin_type.strip() else None,
                    'resin_additive': resin_additive if resin_additive.strip() else None,
                    'sol_material': sol_material if sol_material.strip() else None,
                    
                    # 거래 조건
                    'payment_terms': payment_terms if payment_terms.strip() else None,
                    'delivery_date': delivery_date.isoformat() if delivery_date else None,
                    'lead_time_days': lead_time_days,
                    'remark': remarks if remarks.strip() else None,
                    'remarks': remarks if remarks.strip() else None,
                    
                    # 원가 및 마진 정보
                    'cost_price_usd': cost_price_usd,
                    'margin_rate': margin,
                    
                    # 시스템 정보
                    'updated_at': datetime.now().isoformat()
                }
                
                # 업데이트 실행
                try:
                    # save_func를 통해 업데이트 (id가 있으면 update로 동작)
                    success = save_func('quotations', quotation_data)
                    
                    if success:
                        st.success(f"✅ 견적서가 수정되었습니다! (Rev: {new_revision})")
                        st.balloons()
                        
                        # 세션 상태 초기화
                        st.session_state.pop('editing_quotation_id', None)
                        st.session_state.pop('editing_quotation_data', None)
                        st.session_state.pop('active_tab', None)
                        st.rerun()
                    else:
                        st.error("❌ 수정 실패")
                        
                except Exception as e:
                    st.error(f"❌ 수정 실패: {str(e)}")
            
            if cancel_btn:
                st.session_state.pop('editing_quotation_id', None)
                st.session_state.pop('editing_quotation_data', None)
                st.session_state.pop('active_tab', None)
                st.info("✅ 수정이 취소되었습니다.")
                st.rerun()
        
        else:
            # 신규 작성 모드 (기존 코드)
            with col1:
                temp_save = st.form_submit_button("임시저장", use_container_width=True)
            with col2:
                final_save = st.form_submit_button("정식저장", type="primary", use_container_width=True)
            
            if temp_save or final_save:
                # 폼 밖의 값들을 다시 가져오기
                quantity = st.session_state.get("quotation_quantity", 1)
                unit_price_vnd = st.session_state.get("quotation_unit_price_vnd", 0)
                discount_rate = st.session_state.get("quotation_discount", 0)
                vat_rate = st.session_state.get("quotation_vat", 7.0)
                exchange_rate = st.session_state.get("exchange_rate", 24000)
                
                # VND 기준 계산
                discounted_price_vnd = unit_price_vnd * (1 - discount_rate / 100)
                subtotal_vnd = quantity * discounted_price_vnd
                vat_amount_vnd = subtotal_vnd * (vat_rate / 100)
                final_amount_vnd = subtotal_vnd + vat_amount_vnd
                
                # USD 기준 계산 (참고용)
                unit_price_usd = unit_price_vnd / exchange_rate
                discounted_price_usd = discounted_price_vnd / exchange_rate
                subtotal_usd = subtotal_vnd / exchange_rate
                final_amount_usd = final_amount_vnd / exchange_rate
                
                # 마진 계산
                margin = None
                if cost_price_usd > 0:
                    margin = ((discounted_price_usd - cost_price_usd) / discounted_price_usd) * 100
                
                # 고객 회사명 (공식 이름 사용 - 견적서용)
                customer_company_name = selected_customer_data.get('company_name_original')
                
                # 데이터 준비 (HTML 양식에 맞춤)
                quotation_data = {
                    # 필수 컬럼들 (NOT NULL)
                    'customer_name': customer_company_name,
                    'company': customer_company_name,
                    'quote_date': quote_date.isoformat(),
                    'valid_until': valid_until.isoformat(),
                    'item_name': selected_product_data['product_name_en'],
                    'quantity': quantity,
                    'unit_price': unit_price_vnd,
                    
                    # 고객 정보 (HTML 필요 필드)
                    'customer_id': customer_id,
                    'contact_person': selected_customer_data.get('contact_person'),
                    'email': selected_customer_data.get('email'),
                    'phone': selected_customer_data.get('phone'),
                    'customer_address': selected_customer_data.get('address'),
                    
                    # 견적서 기본 정보
                    'quote_number': quote_number,
                    'revision_number': 'Rv00',
                    'currency': 'VND',
                    'status': 'Draft' if temp_save else 'Sent',
                    'sales_rep_id': sales_rep_id,
                    
                    # 제품 정보
                    'item_code': selected_product_data['product_code'],
                    'item_name_en': selected_product_data['product_name_en'],
                    'item_name_vn': selected_product_data.get('product_name_vn', ''),
                    
                    # 가격 정보 (HTML 양식에 필요한 모든 필드)
                    'std_price': unit_price_vnd,
                    'unit_price_vnd': unit_price_vnd,
                    'unit_price_usd': unit_price_usd,
                    'discount_rate': discount_rate,
                    'discounted_price': discounted_price_vnd,
                    'discounted_price_vnd': discounted_price_vnd,
                    'discounted_price_usd': discounted_price_usd,
                    'vat_rate': vat_rate,
                    'vat_amount': vat_amount_vnd,
                    'final_amount': final_amount_vnd,
                    'final_amount_usd': final_amount_usd,
                    'exchange_rate': exchange_rate,
                    
                    # 프로젝트 정보
                    'project_name': project_name if project_name.strip() else None,
                    'part_name': part_name if part_name.strip() else None,
                    'mold_no': mold_number if mold_number.strip() else None,
                    'mold_number': mold_number if mold_number.strip() else None,
                    'part_weight': part_weight if part_weight > 0 else None,
                    'hrs_info': hrs_info if hrs_info.strip() else None,
                    'resin_type': resin_type if resin_type.strip() else None,
                    'resin_additive': resin_additive if resin_additive.strip() else None,
                    'sol_material': sol_material if sol_material.strip() else None,
                    
                    # 거래 조건
                    'payment_terms': payment_terms if payment_terms.strip() else None,
                    'delivery_date': delivery_date.isoformat() if delivery_date else None,
                    'lead_time_days': lead_time_days,
                    'remark': remarks if remarks.strip() else None,
                    'remarks': remarks if remarks.strip() else None,
                    
                    # 원가 및 마진 정보
                    'cost_price_usd': cost_price_usd,
                    'margin_rate': margin,
                    
                    # 시스템 정보
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # 저장 실행
                if save_func('quotations', quotation_data):
                    save_type = "임시저장" if temp_save else "정식저장"
                    st.success(f"견적서가 성공적으로 {save_type}되었습니다!")
                    st.balloons()
                    
                    # 저장된 정보 요약 표시
                    with st.expander("저장된 견적서 정보", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"견적번호: {quote_number}")
                            st.write(f"고객사: {customer_company_name}")
                            st.write(f"제품: {selected_product_data['product_name_en']}")
                            st.write(f"수량: {quantity:,}")
                            st.write(f"환율: {exchange_rate:,.0f} VND/USD")
                        with col2:
                            st.write(f"상태: {quotation_data['status']}")
                            st.write(f"최종금액: {final_amount_vnd:,.0f} VND")
                            st.write(f"USD 참고: ${final_amount_usd:,.2f}")
                            st.write(f"유효기간: {valid_until}")
                            if margin:
                                st.write(f"마진율: {margin:.1f}%")
                    
                    st.rerun()
                else:
                    st.error("견적서 저장에 실패했습니다.")

def render_quotation_list(load_func, update_func, delete_func, save_func):
    """견적서 목록 - 영업 프로세스 연동 완성"""
    st.header("견적서 목록")
    
    try:
        # 데이터 로드
        quotations_data = load_func('quotations')
        customers_data = load_func('customers')
        employees_data = load_func('employees')
        
        # DataFrame 변환
        quotations_df = pd.DataFrame(quotations_data) if quotations_data else pd.DataFrame()
        customers_df = pd.DataFrame(customers_data) if customers_data else pd.DataFrame()
        employees_df = pd.DataFrame(employees_data) if employees_data else pd.DataFrame()
        
        if quotations_df.empty:
            st.info("등록된 견적서가 없습니다.")
            return
        
        # 고객명, 담당자명 매핑 (짧은 이름 우선)
        customer_dict = {}
        if not customers_df.empty:
            for _, row in customers_df.iterrows():
                display_name = row.get('company_name_short') or row.get('company_name_original')
                customer_dict[row['id']] = display_name
        
        employee_dict = employees_df.set_index('id')['name'].to_dict() if not employees_df.empty else {}
        
        quotations_df['customer_company'] = quotations_df['customer_id'].map(customer_dict).fillna(quotations_df['customer_name'])
        quotations_df['employee_name'] = quotations_df['sales_rep_id'].map(employee_dict).fillna('알 수 없음')
        
        # 검색 기능
        search_term = st.text_input("검색 (견적번호, 고객명)")
        
        if search_term:
            mask = (
                quotations_df['quote_number'].str.contains(search_term, case=False, na=False) |
                quotations_df['customer_company'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = quotations_df[mask]
        else:
            filtered_df = quotations_df
        
        st.write(f"총 {len(filtered_df)}개의 견적서")
        
        # 견적서 목록 표시
        for idx, row in filtered_df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{row['quote_number']}**")
                    st.caption(f"견적일: {row.get('quote_date', 'N/A')}")
                    st.caption(f"Rev: {row.get('revision_number', 'Rv00')}")
                
                with col2:
                    st.write(f"고객: {row['customer_company']}")
                    st.caption(f"담당자: {row['employee_name']}")
                
                with col3:
                    st.write(f"제품: {row.get('item_name_en', 'N/A')}")
                    final_amount = row.get('final_amount', 0)
                    currency = row.get('currency', 'VND')
                    st.write(f"총액: {final_amount:,.0f} {currency}")
                
                with col4:
                    status = row.get('status', 'Draft')
                    status_colors = {
                        'Draft': '#808080',
                        'Sent': '#1f77b4', 
                        'Approved': '#2ca02c',
                        'Rejected': '#d62728',
                        'Expired': '#ff7f0e'
                    }
                    color = status_colors.get(status, '#808080')
                    st.markdown(f"<span style='color: {color}'>● {status}</span>", unsafe_allow_html=True)
                    
                    # 상태 변경
                    new_status = st.selectbox(
                        "상태 변경",
                        ['Draft', 'Sent', 'Approved', 'Rejected', 'Expired'],
                        index=['Draft', 'Sent', 'Approved', 'Rejected', 'Expired'].index(status),
                        key=f"status_{idx}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != status and st.button("변경", key=f"update_{idx}"):
                        # 견적서 상태 업데이트
                        update_data = {
                            'id': row['id'],
                            'status': new_status,
                            'updated_at': datetime.now().isoformat()
                        }
                        
                        try:
                            success = update_func('quotations', update_data)
                            if success:
                                st.success("상태가 변경되었습니다.")
                                
                                # ⭐ 핵심 추가: 견적서 승인 시 영업 프로세스 자동 생성
                                if new_status == 'Approved':
                                    # 영업 프로세스 생성
                                    sales_process_result = create_sales_process_from_quotation(row, save_func)
                                    
                                    if sales_process_result['success']:
                                        st.success("🚀 영업 프로세스가 자동 생성되었습니다!")
                                        st.info(f"📊 예상 수입: {sales_process_result['expected_income']:,.0f} VND")
                                        st.info(f"📅 예상 수입 월: {sales_process_result['expected_month']}")
                                        st.balloons()
                                    else:
                                        st.warning(f"영업 프로세스 생성 실패: {sales_process_result['message']}")
                                
                                st.rerun()
                            else:
                                st.error("상태 변경 실패")
                        except Exception as e:
                            st.error(f"상태 변경 오류: {str(e)}")
                with col5:
                    # 수정 버튼 추가
                    if st.button("📝 수정", key=f"edit_{idx}", help="견적서 수정", use_container_width=True):
                        # 세션 상태에 수정할 견적서 ID 저장
                        st.session_state['editing_quotation_id'] = int(row['id'])
                        st.session_state['editing_quotation_data'] = row.to_dict()
                        st.session_state['active_tab'] = 'edit'  # 탭 전환 플래그
                        st.success(f"✅ 견적서 {row['quote_number']} 수정 모드로 전환합니다...")
                        st.rerun()
                    
                    # 삭제 버튼 추가
                    if st.button("🗑️", key=f"delete_{idx}", help="견적서 삭제"):
                        st.session_state[f'confirm_delete_{idx}'] = True
                    
                    # 삭제 확인
                    if st.session_state.get(f'confirm_delete_{idx}', False):
                        st.warning("정말 삭제하시겠습니까?")
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("예", key=f"confirm_yes_{idx}"):
                                try:
                                    if delete_func('quotations', row['id']):
                                        st.success("✅ 견적서가 삭제되었습니다!")
                                        st.session_state.pop(f'confirm_delete_{idx}', None)
                                        st.rerun()
                                    else:
                                        st.error("❌ 삭제 실패")
                                except Exception as e:
                                    st.error(f"삭제 오류: {str(e)}")
                        with col_no:
                            if st.button("아니오", key=f"confirm_no_{idx}"):
                                st.session_state.pop(f'confirm_delete_{idx}', None)
                                st.rerun()
                
                # 상세 정보
                with st.expander(f"{row['quote_number']} 상세 정보", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"수량: {row.get('quantity', 0):,}")
                        st.write(f"단가: {row.get('unit_price', 0):,.0f} VND")
                        st.write(f"할인율: {row.get('discount_rate', 0):.1f}%")
                        st.write(f"유효기간: {row.get('valid_until', 'N/A')}")
                        if row.get('project_name'):
                            st.write(f"프로젝트: {row['project_name']}")
                        if row.get('margin_rate'):
                            st.write(f"마진율: {row['margin_rate']:.1f}%")
                    
                    with col2:
                        if row.get('part_name'):
                            st.write(f"부품명: {row['part_name']}")
                        if row.get('mold_no'):
                            st.write(f"금형번호: {row['mold_no']}")
                        if row.get('payment_terms'):
                            st.write(f"결제조건: {row['payment_terms']}")
                        if row.get('delivery_date'):
                            st.write(f"납기일: {row['delivery_date']}")
                        if row.get('remark'):
                            st.write(f"비고: {row['remark']}")
                
                st.markdown("---")
        
        # 통계 정보
        if not filtered_df.empty:
            st.markdown("---")
            st.subheader("통계")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 견적서", len(filtered_df))
            
            with col2:
                total_amount = filtered_df['final_amount'].fillna(0).sum()
                st.metric("총 견적 금액", f"{total_amount:,.0f} VND")
            
            with col3:
                approved_count = len(filtered_df[filtered_df['status'] == 'Approved'])
                st.metric("승인된 견적서", approved_count)
            
            with col4:
                approval_rate = (approved_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
                st.metric("승인율", f"{approval_rate:.1f}%")
        
    except Exception as e:
        logging.error(f"견적서 목록 오류: {str(e)}")
        st.error(f"견적서 목록 로딩 중 오류: {str(e)}")


def create_sales_process_from_quotation(quotation_row, save_func):
    """견적서 승인 시 영업 프로세스 자동 생성 (현금 흐름 예측용)"""
    try:
        # 영업 프로세스 번호 생성
        process_number = generate_sales_process_number()
        
        # 고객 회사명 (공식 이름 - 견적서에 이미 저장된 값 사용)
        customer_company = quotation_row.get('company', quotation_row.get('customer_name', ''))
        
        # 영업 프로세스 데이터 준비
        sales_process_data = {
            'process_number': process_number,
            'quotation_id': quotation_row['id'],
            'customer_name': quotation_row.get('customer_name', ''),
            'customer_company': customer_company,
            'customer_email': quotation_row.get('email', ''),
            'customer_phone': quotation_row.get('phone', ''),
            'sales_rep_id': quotation_row.get('sales_rep_id'),
            
            # 프로세스 상태 (견적서 승인 후 order 상태로 시작)
            'process_status': 'order',
            
            # 제품/견적 정보 (현금 흐름 예측용)
            'item_description': quotation_row.get('item_name_en', ''),
            'quantity': quotation_row.get('quantity', 1),
            'unit_price': quotation_row.get('unit_price', 0),
            'total_amount': quotation_row.get('final_amount', 0),  # 예상 수입액
            'currency': quotation_row.get('currency', 'VND'),
            'profit_margin': quotation_row.get('margin_rate', 0),
            
            # 일정 관리 (현금 흐름 예측용)
            'expected_delivery_date': quotation_row.get('delivery_date'),  # 예상 수입 시기
            
            # 거래 조건
            'payment_terms': quotation_row.get('payment_terms', ''),
            'delivery_terms': '',
            
            # 시스템 정보
            'notes': f"견적서 {quotation_row.get('quote_number', '')} 승인으로 자동 생성",
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 영업 프로세스 저장
        success = save_func('sales_process', sales_process_data)
        
        if success:
            # 예상 수입 월 계산
            expected_month = 'N/A'
            if quotation_row.get('delivery_date'):
                try:
                    delivery_date = datetime.fromisoformat(quotation_row['delivery_date'])
                    expected_month = delivery_date.strftime('%Y년 %m월')
                except:
                    expected_month = quotation_row.get('delivery_date', 'N/A')
            
            return {
                'success': True,
                'message': '영업 프로세스 생성 완료',
                'process_number': process_number,
                'expected_income': quotation_row.get('final_amount', 0),
                'expected_month': expected_month
            }
        else:
            return {
                'success': False,
                'message': '영업 프로세스 저장 실패'
            }
            
    except Exception as e:
        logging.error(f"영업 프로세스 생성 오류: {str(e)}")
        return {
            'success': False,
            'message': f'영업 프로세스 생성 오류: {str(e)}'
        }


def generate_sales_process_number():
    """영업 프로세스 번호 자동 생성"""
    today = datetime.now()
    return f"SP{today.strftime('%y%m%d')}-{today.strftime('%H%M%S')}"

def render_quotation_print(load_func):
    """견적서 인쇄 기능 - 환급 관리 스타일"""
    st.header("견적서 인쇄")
    
    try:
        quotations_data = load_func('quotations')
        if not quotations_data:
            st.info("인쇄할 견적서가 없습니다.")
            return
        
        quotations_df = pd.DataFrame(quotations_data)
        
        # 견적서 선택
        quote_options = [f"{row['quote_number']} ({row.get('revision_number', 'Rv00')}) - {row.get('customer_name', 'N/A')}" 
                        for _, row in quotations_df.iterrows()]
        selected_quote = st.selectbox("인쇄할 견적서 선택", quote_options)
        
        if selected_quote:
            # 견적번호 추출 (첫 번째 부분)
            quote_number = selected_quote.split(' (')[0]
            selected_quotation = quotations_df[quotations_df['quote_number'] == quote_number].iloc[0]
            
            # 언어 선택
            col1, col2 = st.columns([3, 1])
            
            with col1:
                language = st.selectbox("언어 선택", ['한국어', 'English', 'Tiếng Việt'])
            
            with col2:
                st.write("")  # 공백
                st.write("")  # 공백
            
            # 인쇄 버튼
            if st.button("🖨️ 인쇄 (새 창에서 열기)", type="primary", use_container_width=True):
                # HTML 생성
                html_content = generate_quotation_html(selected_quotation, load_func, language)
                
                # 인쇄용 JavaScript 추가
                print_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>견적서 인쇄 - {selected_quotation.get('quote_number', '')}</title>
                    <style>
                        body {{
                            margin: 0;
                            padding: 0;
                        }}
                    </style>
                </head>
                <body>
                    {html_content}
                    <script>
                        // 페이지 로드 후 자동으로 인쇄 대화상자 열기
                        window.onload = function() {{
                            // 약간의 딜레이 후 인쇄 대화상자 표시
                            setTimeout(function() {{
                                window.print();
                            }}, 500);
                        }};
                    </script>
                </body>
                </html>
                """
                
                # 새 창에서 HTML 표시
                st.components.v1.html(
                    print_html,
                    height=800,
                    scrolling=True
                )
                
                st.success("✅ 인쇄 창이 열렸습니다!")
                st.info("""
                **📌 인쇄 방법:**
                1. 인쇄 대화상자가 자동으로 나타납니다
                2. 프린터를 선택하거나 'PDF로 저장' 선택
                3. 인쇄 또는 저장 버튼을 클릭하세요
                
                **💡 Tip:** 
                - PDF 저장: 프린터 → 'Microsoft Print to PDF' 또는 'PDF로 저장' 선택
                - 크롬: Ctrl+P로 인쇄 대화상자 다시 열기 가능
                """)
            
            # 미리보기 (선택사항)
            with st.expander("📄 미리보기", expanded=False):
                html_content = generate_quotation_html(selected_quotation, load_func, language)
                st.components.v1.html(html_content, height=800, scrolling=True)
    
    except Exception as e:
        st.error(f"인쇄 기능 오류: {str(e)}")


def render_quotation_csv_management(load_func, save_func):
    """견적서 CSV 관리"""
    st.header("견적서 CSV 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CSV 다운로드")
        
        if st.button("견적서 CSV 다운로드", type="primary"):
            try:
                quotations_data = load_func('quotations')
                
                if not quotations_data:
                    st.warning("다운로드할 견적서가 없습니다.")
                    return
                
                quotations_df = pd.DataFrame(quotations_data)
                
                if quotations_df.empty:
                    st.warning("다운로드할 견적서가 없습니다.")
                    return
                
                # CSV 생성
                csv_data = quotations_df.to_csv(index=False, encoding='utf-8')
                
                st.download_button(
                    label="CSV 파일 다운로드",
                    data=csv_data,
                    file_name=f"quotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.success(f"총 {len(quotations_df)}개의 견적서 데이터 준비 완료")
                
            except Exception as e:
                st.error(f"CSV 생성 오류: {str(e)}")
    
    with col2:
        st.subheader("CSV 업로드")
        st.info("견적서 CSV 업로드 기능은 추후 구현 예정입니다.")

def generate_quote_number(load_func):
    """견적번호 자동 생성 - YMV-YYMMDD-00x 형식"""
    today = datetime.now()
    date_str = today.strftime('%y%m%d')  # YYMMDD 형식
    
    try:
        # 오늘 날짜로 시작하는 견적서 조회
        quotations_data = load_func('quotations')
        
        if not quotations_data:
            # 견적서가 하나도 없으면 001부터 시작
            return f"YMV-{date_str}-001"
        
        # 오늘 날짜 패턴
        today_pattern = f"YMV-{date_str}-"
        
        # 오늘 생성된 견적서 필터링
        today_quotes = [
            q for q in quotations_data 
            if q.get('quote_number', '').startswith(today_pattern)
        ]
        
        if not today_quotes:
            # 오늘 생성된 견적서가 없으면 001
            return f"YMV-{date_str}-001"
        
        # 가장 큰 번호 찾기
        max_count = 0
        for quote in today_quotes:
            try:
                quote_num = quote.get('quote_number', '')
                # YMV-251008-001 형식에서 001 부분 추출
                count_str = quote_num.split('-')[-1]
                count = int(count_str)
                if count > max_count:
                    max_count = count
            except:
                continue
        
        # 다음 번호
        new_count = max_count + 1
        count_str = f"{new_count:03d}"
        
        return f"YMV-{date_str}-{count_str}"
        
    except Exception as e:
        # 오류 발생 시 타임스탬프 기반으로 생성
        timestamp = today.strftime('%H%M%S')
        return f"YMV-{date_str}-{timestamp[:3]}"


def get_next_revision_number(current_revision):
    """현재 Revision 번호를 증가시킴 (Rv00 → Rv01 → Rv02...)"""
    try:
        # Rv00, Rv01 형식에서 숫자 추출
        if current_revision and current_revision.startswith('Rv'):
            current_num = int(current_revision[2:])
            next_num = current_num + 1
            return f"Rv{next_num:02d}"
        else:
            return "Rv01"
    except:
        return "Rv01"

def generate_quotation_html(quotation, load_func, language='한국어'):
    """견적서 HTML 생성 (완전 구현) - Base64 스탬프 적용"""
    try:
        import base64
        from pathlib import Path
        
        # 스탬프 이미지를 Base64로 인코딩
        stamp_base64 = ""
        stamp_path = Path("D:/ymv-business-system/app/images/Stemp-sign.png")
        
        try:
            if stamp_path.exists():
                with open(stamp_path, "rb") as image_file:
                    stamp_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                    stamp_base64 = f"data:image/png;base64,{stamp_base64}"
            else:
                logging.warning(f"스탬프 이미지를 찾을 수 없습니다: {stamp_path}")
        except Exception as e:
            logging.error(f"스탬프 이미지 로드 오류: {str(e)}")
        
        # 고객 및 직원 정보 로드
        customers_data = load_func('customers')
        employees_data = load_func('employees')
        
        customers_df = pd.DataFrame(customers_data) if customers_data else pd.DataFrame()
        employees_df = pd.DataFrame(employees_data) if employees_data else pd.DataFrame()
        
        # 고객 정보 가져오기
        customer_info = {}
        if not customers_df.empty and quotation.get('customer_id'):
            customer_data = customers_df[customers_df['id'] == quotation['customer_id']]
            if not customer_data.empty:
                customer_info = customer_data.iloc[0].to_dict()
        
        # quotation 데이터에서 직접 고객 정보 사용 (fallback) - 공식 이름 사용
        if not customer_info:
            customer_info = {
                'company_name_original': quotation.get('company', quotation.get('customer_name', '')),
                'address': quotation.get('customer_address', ''),
                'contact_person': quotation.get('contact_person', ''),
                'phone': quotation.get('phone', ''),
                'email': quotation.get('email', '')
            }
        
        # 고객 회사명 (공식 이름 - 견적서용)
        customer_company_name = customer_info.get('company_name_original', '')
        
        # 직원 정보 가져오기
        employee_info = {}
        if not employees_df.empty and quotation.get('sales_rep_id'):
            employee_data = employees_df[employees_df['id'] == quotation['sales_rep_id']]
            if not employee_data.empty:
                employee_info = employee_data.iloc[0].to_dict()
        
        # 스탬프 이미지 태그 생성
        stamp_img_tag = ""
        if stamp_base64:
            stamp_img_tag = f'<img src="{stamp_base64}" class="stamp-image" alt="Company Stamp" />'
        
        # HTML 템플릿 (업데이트된 양식)
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quotation - {quotation.get('quote_number', '')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        
        .quotation {{
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
        
        .quote-info {{
            text-align: right;
            font-size: 12px;
        }}
        
        .office-info {{
            margin-top: 10px;
            font-size: 11px;
        }}
        
        .customer-info {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
        }}
        
        .quote-details {{
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
            table-layout: fixed;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 10px 8px;
            text-align: center;
            word-wrap: break-word;
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
            .quotation {{
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
    <div class="quotation">
        <div class="content-area">
            <!-- 헤더 -->
            <div class="header">
                <!-- 고객 정보 영역 -->
                <div>
                    <div class="company-name">{customer_company_name}</div>
                    <div class="company-info">
                        Address: {customer_info.get('address', '[고객 주소]')}<br><br>
                        Contact Person: {customer_info.get('contact_person', '[고객 담당자]')}<br>
                        Phone No.: {customer_info.get('phone', '[고객 전화번호]')}<br>
                        E-mail: {customer_info.get('email', '[고객 이메일]')}
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
                    </div>
                </div>
            </div>
            
            <!-- 견적 정보 -->
            <div class="quote-details">
                <div>Date: {quotation.get('quote_date', '')}</div>
                <div>Quote No.: {quotation.get('quote_number', '')}</div>
                <div>Rev. No.: {quotation.get('revision_number', 'Rv00')}</div>
                <div>Currency: {quotation.get('currency', 'VND')}</div>
            </div>
            
            <!-- 항목 테이블 (업데이트된 구조) -->
            <table>
                <thead>
                    <tr>
                        <th style="width: 4%;">NO</th>
                        <th style="width: 18%;">Item Code</th>
                        <th style="width: 6%;">Qty.</th>
                        <th style="width: 14%;">Std. Price</th>
                        <th style="width: 8%;">DC. Rate</th>
                        <th style="width: 14%;">Unit Price</th>
                        <th style="width: 16%;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td rowspan="4" style="vertical-align: top; padding-top: 30px; font-weight: bold;">1</td>
                        <td style="font-size: 10px;">{quotation.get('item_code', '')}</td>
                        <td style="font-weight: bold;">{quotation.get('quantity', 1):,}</td>
                        <td class="text-right" style="font-size: 10px;">{quotation.get('std_price', 0):,.0f}</td>
                        <td style="font-weight: bold;">{quotation.get('discount_rate', 0):.1f}%</td>
                        <td class="text-right" style="font-size: 10px; font-weight: bold;">{quotation.get('discounted_price', 0):,.0f}</td>
                        <td class="text-right" style="font-size: 10px; font-weight: bold;">{(quotation.get('quantity', 1) * quotation.get('discounted_price', 0)):,.0f}</td>
                    </tr>
                    <tr>
                        <td colspan="6" style="padding: 8px; border-top: none; text-align: left; font-weight: bold;">
                            {quotation.get('item_name_en', '')}
                        </td>
                    </tr>
                    <tr>
                        <td colspan="6" style="padding: 8px; border-top: none; text-align: left; font-style: italic; color: #666;">
                            {quotation.get('item_name_vn', '')}
                        </td>
                    </tr>
                    <tr>
                        <td colspan="6" style="padding: 8px; border-top: none; text-align: left;">
                            {quotation.get('remark', quotation.get('remarks', ''))}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- 하단 고정 영역 -->
        <div class="bottom-fixed">
            <!-- 합계 -->
            <div class="totals">
                <table>
                    <tr>
                        <td class="text-right">TOTAL {quotation.get('currency', 'VND')} Excl. VAT</td>
                        <td>{quotation.get('currency', 'VND')}</td>
                        <td class="text-right">{(quotation.get('quantity', 1) * quotation.get('discounted_price', 0)):,.0f}</td>
                    </tr>
                    <tr>
                        <td class="text-right">TOTAL {quotation.get('currency', 'VND')} {quotation.get('vat_rate', 0):.1f}% VAT</td>
                        <td>{quotation.get('currency', 'VND')}</td>
                        <td class="text-right">{quotation.get('vat_amount', 0):,.0f}</td>
                    </tr>
                    <tr class="total-row">
                        <td class="text-right">TOTAL {quotation.get('currency', 'VND')} Incl. VAT</td>
                        <td>{quotation.get('currency', 'VND')}</td>
                        <td class="text-right">{quotation.get('final_amount', 0):,.0f}</td>
                    </tr>
                </table>
            </div>
            
            <!-- 프로젝트 정보 -->
            <div class="project-info">
                <table class="project-table">
                    <tr>
                        <td>Project Name:</td>
                        <td>{quotation.get('project_name', '')}</td>
                        <td>Part Name:</td>
                        <td>{quotation.get('part_name', '')}</td>
                    </tr>
                    <tr>
                        <td>Mold No.:</td>
                        <td>{quotation.get('mold_no', quotation.get('mold_number', ''))}</td>
                        <td>Part Weight:</td>
                        <td style="text-align: right;">{quotation.get('part_weight', '')} g</td>
                    </tr>
                    <tr>
                        <td>HRS Info:</td>
                        <td>{quotation.get('hrs_info', '')}</td>
                        <td>Resin Type:</td>
                        <td>{quotation.get('resin_type', '')}</td>
                    </tr>
                    <tr>
                        <td>Remark:</td>
                        <td>{quotation.get('remark', quotation.get('remarks', ''))}</td>
                        <td>Valid Date:</td>
                        <td>{quotation.get('valid_until', '')}</td>
                    </tr>
                    <tr>
                        <td>Resin/Additive:</td>
                        <td>{quotation.get('resin_additive', '')}</td>
                        <td>Sales Rep:</td>
                        <td>{employee_info.get('name', '')}</td>
                    </tr>
                    <tr>
                        <td>Sol/Material:</td>
                        <td>{quotation.get('sol_material', '')}</td>
                        <td>Contact:</td>
                        <td>{employee_info.get('email', '')}</td>
                    </tr>
                    <tr>
                        <td>Payment Terms:</td>
                        <td>{quotation.get('payment_terms', '')}</td>
                        <td>Phone:</td>
                        <td>{employee_info.get('phone', '')}</td>
                    </tr>
                    <tr>
                        <td>Delivery Date:</td>
                        <td>{quotation.get('delivery_date', '')}</td>
                        <td>Account:</td>
                        <td style="font-size: 10px;">700-038-038199 (Shinhan Bank Vietnam)</td>
                    </tr>
                </table>
            </div>
            
            <!-- 공급업체 이름 -->
            <div style="text-align: center; margin: 30px 0; font-size: 16px; font-weight: bold;">
                YUMOLD VIETNAM CO., LTD
            </div>
            
            <!-- 서명란 (Base64 스탬프 이미지 포함) -->
            <div class="signature-section">
                <div class="signature-box">
                    <div>Authorised Signature</div>
                    <div class="signature-line"></div>
                    {stamp_img_tag}
                </div>
                <div class="signature-box">
                    <div>Customer Signature</div>
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
        logging.error(f"HTML 생성 오류: {str(e)}")
        return f"<html><body><h1>오류: {str(e)}</h1></body></html>"