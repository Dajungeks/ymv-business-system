# app/components/specifications/customer_section.py

import streamlit as st
from datetime import date

def render_customer_section(load_func, save_func):
    """고객 및 프로젝트 정보 입력 섹션"""
    
    st.markdown("### 📋 Customer & Project Information")
    
    # 견적서 선택 (옵션)
    with st.expander("🔗 Link to Quotation (Optional)", expanded=False):
        quotations = load_func('quotations', {'status': 'approved'}) if load_func else []
        
        if quotations:
            quotation_options = ["None - Manual Entry"] + [
                f"{q.get('quotation_number', q.get('id', 'N/A'))} - {q.get('customer_name', 'N/A')}"
                for q in quotations
            ]
            
            selected_quotation = st.selectbox(
                "Select Quotation",
                quotation_options,
                key="selected_quotation"
            )
            
            # 견적서 선택 시 데이터 자동 입력
            if selected_quotation != "None - Manual Entry":
                selected_idx = quotation_options.index(selected_quotation) - 1
                quotation_data = quotations[selected_idx]
                
                st.session_state['quotation_id'] = quotation_data.get('id')
                st.session_state['auto_customer_name'] = quotation_data.get('customer_name', '')
                st.session_state['auto_project_name'] = quotation_data.get('item_name_en', '')
            else:
                st.session_state['quotation_id'] = None
                st.session_state['auto_customer_name'] = ''
                st.session_state['auto_project_name'] = ''
        else:
            st.info("No approved quotations available")
    
    # 고객 정보 입력
    col1, col2 = st.columns(2)
    
    with col1:
        # 고객 선택 또는 신규 입력
        customers = load_func('customers') if load_func else []
        
        if customers:
            customer_mode = st.radio(
                "Customer Entry Mode",
                ["Select Existing", "New Customer"],
                horizontal=True,
                key="customer_mode"
            )
            
            if customer_mode == "Select Existing":
                customer_options = [c.get('name', 'N/A') for c in customers]
                selected_customer = st.selectbox(
                    "🔴 Customer *",
                    customer_options,
                    key="customer_select"
                )
                
                # 선택된 고객 정보 가져오기
                customer_data = next((c for c in customers if c.get('name') == selected_customer), {})
                customer_name = customer_data.get('name', '')
                customer_id = customer_data.get('id')
            else:
                customer_name = st.text_input(
                    "🔴 Customer *",
                    value=st.session_state.get('auto_customer_name', ''),
                    key="customer_name_new"
                )
                customer_id = None
        else:
            customer_name = st.text_input(
                "🔴 Customer *",
                value=st.session_state.get('auto_customer_name', ''),
                key="customer_name"
            )
            customer_id = None
        
        # 프로젝트명
        project_name = st.text_input(
            "🔴 Project Name *",
            value=st.session_state.get('auto_project_name', ''),
            key="project_name"
        )
        
        # 금형번호
        mold_no = st.text_input(
            "Mold No",
            key="mold_no"
        )
    
    with col2:
        # 납품처
        delivery_to = st.text_input(
            "🔴 Delivery To *",
            key="delivery_to"
        )
        
        # 부품명
        part_name = st.text_input(
            "Part Name",
            key="part_name"
        )
        
        # YMV 번호
        ymv_no = st.text_input(
            "YMV No",
            key="ymv_no"
        )
    
    # 추가 정보
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # 영업담당 (직원 DB에서 불러오기)
        employees = load_func('employees') if load_func else []
        
        if employees:
            sales_employees = [e for e in employees if e.get('role') in ['Manager', 'Admin', 'CEO']]
            employee_options = [f"{e.get('name', 'N/A')} - {e.get('position', '')}" for e in sales_employees]
            
            selected_employee = st.selectbox(
                "🔴 Sales Contact *",
                employee_options,
                key="sales_contact"
            )
            
            # 선택된 직원 ID 가져오기
            sales_contact_id = sales_employees[employee_options.index(selected_employee)].get('id')
        else:
            sales_contact_text = st.text_input(
                "🔴 Sales Contact *",
                key="sales_contact_text"
            )
            sales_contact_id = None
        
        # Resin
        resin = st.text_input(
            "Resin",
            key="resin"
        )
    
    with col4:
        # 사출기 TON
        injection_ton = st.number_input(
            "Injection TON",
            min_value=0,
            step=10,
            key="injection_ton"
        )
        
        # 첨가제
        additive = st.text_input(
            "Additive",
            key="additive"
        )
    
    # 선택 옵션
    st.markdown("---")
    st.markdown("### 🔧 Order Options")
    
    col5, col6 = st.columns(2)
    
    with col5:
        color_change = st.radio(
            "🔴 Color Change *",
            ["NO", "YES"],
            horizontal=True,
            key="color_change"
        )
    
    with col6:
        order_type = st.radio(
            "🔴 Order Type *",
            ["SYSTEM", "SEMI", "TOTAL"],
            horizontal=True,
            key="order_type"
        )
    
    # 데이터 반환
    customer_data = {
        'quotation_id': st.session_state.get('quotation_id'),
        'customer_id': customer_id,
        'customer_name': customer_name,
        'delivery_to': delivery_to,
        'project_name': project_name,
        'part_name': part_name,
        'mold_no': mold_no,
        'ymv_no': ymv_no,
        'sales_contact': sales_contact_id,
        'injection_ton': injection_ton,
        'resin': resin,
        'additive': additive,
        'color_change': color_change == "YES",
        'order_type': order_type
    }
    
    return customer_data

def validate_customer_data(data):
    """필수 입력 검증"""
    required_fields = {
        'customer_name': 'Customer',
        'delivery_to': 'Delivery To',
        'project_name': 'Project Name',
        'sales_contact': 'Sales Contact'
    }
    
    missing_fields = []
    
    for field, label in required_fields.items():
        value = data.get(field)
        # None 또는 빈 문자열 체크
        if value is None or (isinstance(value, str) and not value.strip()):
            missing_fields.append(label)
    
    if missing_fields:
        return False, f"Required fields missing: {', '.join(missing_fields)}"
    
    return True, "OK"