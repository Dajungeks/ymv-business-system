import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
import time

def show_quotation_management(save_func, load_func, update_func, delete_func, current_user):
    """견적서 관리 메인"""
    st.title("📋 견적서 관리")
    
    if not current_user:
        st.error("로그인이 필요합니다.")
        return
    
    # 법인별 테이블명 생성
    from utils.helpers import get_company_table
    
    company_code = current_user.get('company')
    if not company_code:
        st.error("법인 정보가 없습니다.")
        return
    
    customer_table = get_company_table('customers', company_code)
    quotation_table = get_company_table('quotations', company_code)
    
    # 탭 3개로 변경
    tab1, tab2, tab3 = st.tabs([
        "📝 견적서 작성",
        "📋 견적서 목록",
        "📊 CSV 관리"
    ])
    
    with tab1:
        render_quotation_form(save_func, load_func, update_func, customer_table, quotation_table)
    
    with tab2:
        render_quotation_list(load_func, update_func, delete_func, save_func, customer_table, quotation_table)
    
    with tab3:
        render_quotation_csv_management(load_func, save_func, quotation_table)


def safe_strip(value):
    """안전한 strip 함수 - None 체크 포함"""
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return value


def render_product_selection_for_quotation(load_func, mode='new'):
    """견적서용 제품 선택 UI"""
    st.subheader("🔍 제품 검색 및 선택")
    
    try:
        all_codes = load_func('product_codes') or []
        
        # 법인별 제품 테이블
        current_user = st.session_state.get('current_user', {})
        company_code = current_user.get('company', 'YMV')
        from utils.helpers import get_company_table
        products_table = get_company_table('products', company_code)
        products_data = load_func(products_table) or []  # ✅        
        if not all_codes:
            st.warning("등록된 제품 코드가 없습니다.")
            return
        
        if not products_data:
            st.warning("등록된 제품이 없습니다.")
            return
        
        products_df = pd.DataFrame(products_data)
        
        st.markdown("### 📋 제품 코드 필터")
        st.caption("각 단계를 선택하여 제품을 필터링하세요.")
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        with col1:
            code01_options = get_unique_code_values(all_codes, 'code01')
            code01 = st.selectbox("Code01", ["전체"] + code01_options, key=f"quot_{mode}_code01")
        
        with col2:
            if code01 != "전체":
                filtered = filter_codes_by_selections(all_codes, {'code01': code01})
                code02_options = get_unique_code_values(filtered, 'code02')
                code02 = st.selectbox("Code02", ["전체"] + code02_options, key=f"quot_{mode}_code02")
            else:
                st.selectbox("Code02", ["전체"], disabled=True, key=f"quot_{mode}_code02_dis")
                code02 = "전체"
        
        with col3:
            if code01 != "전체" and code02 != "전체":
                filtered = filter_codes_by_selections(all_codes, {'code01': code01, 'code02': code02})
                code03_options = get_unique_code_values(filtered, 'code03')
                code03 = st.selectbox("Code03", ["전체"] + code03_options, key=f"quot_{mode}_code03")
            else:
                st.selectbox("Code03", ["전체"], disabled=True, key=f"quot_{mode}_code03_dis")
                code03 = "전체"
        
        with col4:
            if code01 != "전체" and code02 != "전체" and code03 != "전체":
                filtered = filter_codes_by_selections(all_codes, {'code01': code01, 'code02': code02, 'code03': code03})
                code04_options = get_unique_code_values(filtered, 'code04')
                code04 = st.selectbox("Code04", ["전체"] + code04_options, key=f"quot_{mode}_code04")
            else:
                st.selectbox("Code04", ["전체"], disabled=True, key=f"quot_{mode}_code04_dis")
                code04 = "전체"
        
        with col5:
            if code04 != "전체":
                filtered = filter_codes_by_selections(all_codes, {'code01': code01, 'code02': code02, 'code03': code03, 'code04': code04})
                code05_options = get_unique_code_values(filtered, 'code05')
                code05 = st.selectbox("Code05", ["전체"] + code05_options, key=f"quot_{mode}_code05")
            else:
                st.selectbox("Code05", ["전체"], disabled=True, key=f"quot_{mode}_code05_dis")
                code05 = "전체"
        
        with col6:
            if code05 != "전체":
                filtered = filter_codes_by_selections(all_codes, {'code01': code01, 'code02': code02, 'code03': code03, 'code04': code04, 'code05': code05})
                code06_options = get_unique_code_values(filtered, 'code06')
                code06 = st.selectbox("Code06", ["전체"] + code06_options, key=f"quot_{mode}_code06")
            else:
                st.selectbox("Code06", ["전체"], disabled=True, key=f"quot_{mode}_code06_dis")
                code06 = "전체"
        
        with col7:
            if code06 != "전체":
                filtered = filter_codes_by_selections(all_codes, {'code01': code01, 'code02': code02, 'code03': code03, 'code04': code04, 'code05': code05, 'code06': code06})
                code07_options = get_unique_code_values(filtered, 'code07')
                code07 = st.selectbox("Code07", ["전체"] + code07_options, key=f"quot_{mode}_code07")
            else:
                st.selectbox("Code07", ["전체"], disabled=True, key=f"quot_{mode}_code07_dis")
                code07 = "전체"
        
        selections = {}
        if code01 != "전체":
            selections['code01'] = code01
        if code02 != "전체":
            selections['code02'] = code02
        if code03 != "전체":
            selections['code03'] = code03
        if code04 != "전체":
            selections['code04'] = code04
        if code05 != "전체":
            selections['code05'] = code05
        if code06 != "전체":
            selections['code06'] = code06
        if code07 != "전체":
            selections['code07'] = code07
        
        matching_codes = filter_codes_by_selections(all_codes, selections)
        
        st.markdown("---")
        
        if matching_codes:
            matching_product_codes = [code.get('full_code') for code in matching_codes]
            filtered_products = products_df[products_df['product_code'].isin(matching_product_codes)]
            
            if not filtered_products.empty:
                st.info(f"🔍 {len(filtered_products)}개 제품 매칭")
                
                table_data = []
                for _, product in filtered_products.iterrows():
                    cost_usd = float(product.get('cost_price_usd', 0))
                    selling_vnd = float(product.get('actual_selling_price_vnd', 0))
                    
                    table_data.append({
                        'ID': product.get('id', ''),
                        'Code': product.get('product_code', ''),
                        '원가(USD)': f"${cost_usd:,.2f}",
                        '실제판매가(VND)': f"{selling_vnd:,.0f}"
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns([3, 1, 3])
                
                with col1:
                    product_id_input = st.text_input("선택할 제품 ID", placeholder="제품 ID 입력", key=f"quot_{mode}_product_id")
                
                with col2:
                    if st.button("➡️ 선택", use_container_width=True, type="primary", key=f"quot_{mode}_select_btn"):
                        if product_id_input and product_id_input.strip().isdigit():
                            product_id = int(product_id_input.strip())
                            selected = filtered_products[filtered_products['id'] == product_id]
                            
                            if not selected.empty:
                                if mode == 'new':
                                    st.session_state.selected_product_for_quotation_new = selected.iloc[0].to_dict()
                                else:
                                    st.session_state.selected_product_for_quotation_edit = selected.iloc[0].to_dict()
                                    st.session_state.pop('show_product_selector_edit', None)
                                
                                st.success(f"✅ 제품 선택 완료: {selected.iloc[0]['product_code']}")
                                st.rerun()
                            else:
                                st.error(f"❌ ID {product_id}를 찾을 수 없습니다.")
                        else:
                            st.error("❌ 올바른 ID를 입력하세요.")
            else:
                st.warning("⚠️ 매칭되는 제품이 없습니다.")
        else:
            st.info("💡 코드 필터를 선택하여 제품을 검색하세요.")
    
    except Exception as e:
        st.error(f"❌ 제품 선택 중 오류: {str(e)}")


def get_unique_code_values(codes, level):
    """특정 레벨의 고유값 추출"""
    values = sorted(set([str(c.get(level, '')) for c in codes if c.get(level)]))
    return values


def filter_codes_by_selections(codes, selections):
    """선택값으로 코드 필터링"""
    filtered = codes.copy()
    for level, value in selections.items():
        if value and value != "선택" and value != "전체":
            filtered = [c for c in filtered if str(c.get(level, '')) == value]
    return filtered

def render_quotation_form(save_func, load_func, update_func, customer_table, quotation_table):
    """견적서 작성 폼 - 고객 선택 + 전체 양식"""
    
    # 수정 모드는 목록에서 처리
    if st.session_state.get('editing_quotation_id'):
        st.info("💡 수정은 '견적서 목록' 탭에서 진행됩니다.")
        if st.button("📋 목록으로 이동"):
            st.session_state.pop('editing_quotation_id', None)
            st.session_state.pop('editing_quotation_data', None)
            st.rerun()
        return
    
    st.header("새 견적서 작성")
    
    # ✅ 고객 검색 UI
    st.subheader("🔍 고객 검색")
    
    try:
        customers_data = load_func(customer_table) 
        if not customers_data:
            st.warning("등록된 고객이 없습니다.")
            return
        
        customers_df = pd.DataFrame(customers_data)
        st.caption("고객사명 또는 담당자명으로 검색하세요.")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            search_term = st.text_input("검색어", placeholder="고객사명 또는 담당자명", key="customer_search_quotation_new")
        with col2:
            st.write("")
            st.write("")
            search_btn = st.button("🔍 검색", use_container_width=True, type="primary", key="search_customer_new")
        
        if search_term or search_btn:
            if search_term:
                mask = (
                    customers_df['company_name_original'].str.contains(search_term, case=False, na=False) |
                    customers_df['company_name_short'].str.contains(search_term, case=False, na=False) |
                    customers_df['contact_person'].str.contains(search_term, case=False, na=False)
                )
                filtered_customers = customers_df[mask]
            else:
                filtered_customers = customers_df
            
            st.markdown("---")
            
            if not filtered_customers.empty:
                st.info(f"🔍 {len(filtered_customers)}개 고객 매칭")
                
                table_data = []
                for _, customer in filtered_customers.iterrows():
                    display_name = customer.get('company_name_short') or customer.get('company_name_original')
                    table_data.append({
                        'ID': customer.get('id', ''),
                        'Company': display_name,
                        'Contact': customer.get('contact_person', ''),
                        'Email': customer.get('email', ''),
                        'Phone': customer.get('phone', '')
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns([3, 1, 3])
                with col1:
                    customer_id_input = st.text_input("선택할 고객 ID", placeholder="ID 입력", key="customer_id_input_quot_new")
                with col2:
                    if st.button("➡️ 선택", use_container_width=True, type="primary", key="select_customer_new"):
                        if customer_id_input and customer_id_input.strip().isdigit():
                            customer_id = int(customer_id_input.strip())
                            selected = filtered_customers[filtered_customers['id'] == customer_id]
                            if not selected.empty:
                                st.session_state.selected_customer_for_quotation = selected.iloc[0].to_dict()
                                st.rerun()
                            else:
                                st.error(f"❌ ID {customer_id}를 찾을 수 없습니다.")
                        else:
                            st.error("❌ 올바른 ID를 입력하세요.")
            else:
                st.warning("⚠️ 검색 결과가 없습니다.")
        else:
            st.info("💡 검색어를 입력하고 검색 버튼을 클릭하세요.")
    except Exception as e:
        st.error(f"❌ 고객 검색 중 오류: {str(e)}")
    
    # ✅ 고객 선택되면 바로 양식 표시
    if st.session_state.get('selected_customer_for_quotation'):
        st.markdown("---")
        st.markdown("---")
        
        current_user = st.session_state.get('current_user', {})
        company_code = current_user.get('company', 'YMV')
        from utils.helpers import get_company_table
        product_table = get_company_table('products', company_code)
        
        render_quotation_form_with_customer(save_func, load_func, customer_table, quotation_table, product_table)

def render_customer_search_for_quotation(load_func, customer_table):
    """고객 검색"""
    st.subheader("🔍 고객 검색")
    
    try:
        # 법인별 고객 테이블에서 로드
        customers_data = load_func(customer_table) 
        if not customers_data:
            st.warning("등록된 고객이 없습니다.")
            return
        
        customers_df = pd.DataFrame(customers_data)
        st.caption("고객사명 또는 담당자명으로 검색하세요.")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            search_term = st.text_input("검색어", placeholder="고객사명 또는 담당자명", key="customer_search_quotation")
        with col2:
            st.write("")
            st.write("")
            search_btn = st.button("🔍 검색", use_container_width=True, type="primary")
        
        if search_term or search_btn:
            if search_term:
                mask = (
                    customers_df['company_name_original'].str.contains(search_term, case=False, na=False) |
                    customers_df['company_name_short'].str.contains(search_term, case=False, na=False) |
                    customers_df['contact_person'].str.contains(search_term, case=False, na=False)
                )
                filtered_customers = customers_df[mask]
            else:
                filtered_customers = customers_df
            
            st.markdown("---")
            
            if not filtered_customers.empty:
                st.info(f"🔍 {len(filtered_customers)}개 고객 매칭")
                
                table_data = []
                for _, customer in filtered_customers.iterrows():
                    display_name = customer.get('company_name_short') or customer.get('company_name_original')
                    table_data.append({
                        'ID': customer.get('id', ''),
                        'Company': display_name,
                        'Contact': customer.get('contact_person', ''),
                        'Email': customer.get('email', ''),
                        'Phone': customer.get('phone', '')
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns([3, 1, 3])
                with col1:
                    customer_id_input = st.text_input("선택할 고객 ID", placeholder="ID 입력", key="customer_id_input_quot")
                with col2:
                    if st.button("➡️ 선택", use_container_width=True, type="primary"):
                        if customer_id_input and customer_id_input.strip().isdigit():
                            customer_id = int(customer_id_input.strip())
                            selected = filtered_customers[filtered_customers['id'] == customer_id]
                            if not selected.empty:
                                st.session_state.selected_customer_for_quotation = selected.iloc[0].to_dict()
                                st.session_state.show_quotation_input_form = True
                                st.rerun()
                            else:
                                st.error(f"❌ ID {customer_id}를 찾을 수 없습니다.")
                        else:
                            st.error("❌ 올바른 ID를 입력하세요.")
            else:
                st.warning("⚠️ 검색 결과가 없습니다.")
        else:
            st.info("💡 검색어를 입력하고 검색 버튼을 클릭하세요.")
    except Exception as e:
        st.error(f"❌ 고객 검색 중 오류: {str(e)}")

def render_quotation_form_with_customer(save_func, load_func, customer_table, quotation_table, product_table):
    """선택한 고객으로 견적서 작성 - 여러 제품 추가 가능"""
    selected_customer = st.session_state.get('selected_customer_for_quotation', {})
    
    if not selected_customer:
        st.error("고객 정보가 없습니다.")
        if st.button("◀ 고객 선택으로 돌아가기"):
            st.session_state.pop('selected_customer_for_quotation', None)
            st.session_state.show_quotation_input_form = False
            st.rerun()
        return
    
    display_name = selected_customer.get('company_name_short') or selected_customer.get('company_name_original')
    st.success(f"📋 선택된 고객: **{display_name}** (ID: {selected_customer['id']})")
    
    if st.button("🔄 다른 고객 선택"):
        st.session_state.pop('selected_customer_for_quotation', None)
        st.session_state.show_quotation_input_form = False
        st.rerun()
    
    st.markdown("---")
    
    employees_data = load_func('employees')
    products_data = load_func(product_table)
    
    employees_df = pd.DataFrame(employees_data) if employees_data else pd.DataFrame()
    products_df = pd.DataFrame(products_data) if products_data else pd.DataFrame()
    
    if employees_df.empty or products_df.empty:
        st.warning("필요한 데이터가 없습니다.")
        return
    
    with st.expander("고객 정보", expanded=False):
        st.write(f"**회사명:** {selected_customer.get('company_name_original')}")
        st.write(f"**담당자:** {selected_customer.get('contact_person', 'N/A')}")
        st.write(f"**이메일:** {selected_customer.get('email', 'N/A')}")
        st.write(f"**전화:** {selected_customer.get('phone', 'N/A')}")
        st.write(f"**주소:** {selected_customer.get('address', 'N/A')}")
    
    st.subheader("영업 담당자")
    employee_options = [f"{row['name']} ({row['department']}) [{row['id']}]" for _, row in employees_df.iterrows()]
    selected_employee = st.selectbox("영업담당자", employee_options, key="quotation_employee_select_new")
    sales_rep_id = int(selected_employee.split('[')[-1].split(']')[0])
    
    st.markdown("---")   
    st.subheader("📦 제품 항목 추가")

    # 견적 항목 리스트 초기화
    if 'quotation_items' not in st.session_state:
        st.session_state.quotation_items = []

    # ✅ 최대 5개 제한 표시
    st.info(f"📋 현재 {len(st.session_state.quotation_items)}/5 개 제품 추가됨")

    # ✅ 최대 5개 제한 체크
    if len(st.session_state.quotation_items) >= 5:
        st.warning("⚠️ 최대 5개 제품까지만 추가할 수 있습니다.")
        st.caption("제품을 추가하려면 먼저 기존 항목을 삭제하세요.")
    else:
        # 제품 선택 및 추가
        if not st.session_state.get('selected_product_for_quotation_new'):
            render_product_selection_for_quotation(load_func, mode='new')
        else:
            selected_product_data = st.session_state.selected_product_for_quotation_new
            
            st.success(f"✅ 선택된 제품: {selected_product_data.get('product_code', '')} - {selected_product_data.get('product_name_vn', '')}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                item_quantity = st.number_input("수량", min_value=1, value=1, key="item_qty_temp")
            with col2:
                item_unit_price = st.number_input("단가 (VND)", min_value=0.0, value=float(selected_product_data.get('actual_selling_price_vnd', 0)), step=10000.0, format="%.0f", key="item_price_temp")
            with col3:
                st.metric("합계", f"{item_quantity * item_unit_price:,.0f} VND")
            
            # ✅ 상세 설명 입력란 추가
            item_detail_description = st.text_area(
                "상세 설명 (선택사항)", 
                placeholder="예: 특수 코팅, 색상 지정, 포장 방법, 기타 요구사항 등",
                height=80,
                key="item_detail_desc_temp",
                help="이 내용은 견적서 출력 시 제품명 아래에 표시됩니다."
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
            with col_btn2:
                if st.button("➕ 항목 추가", type="primary", use_container_width=True):
                    if len(st.session_state.quotation_items) < 5:
                        item = {
                            'product_id': selected_product_data.get('id'),
                            'product_code': selected_product_data.get('product_code'),
                            'product_name_vn': selected_product_data.get('product_name_vn'),
                            'product_name_en': selected_product_data.get('product_name_en'),
                            'quantity': item_quantity,
                            'unit_price_vnd': item_unit_price,
                            'line_total': item_quantity * item_unit_price,
                            'cost_price_usd': selected_product_data.get('cost_price_usd', 0),
                            'item_detail_description': item_detail_description.strip() if item_detail_description else ''
                        }
                        st.session_state.quotation_items.append(item)
                        st.session_state.pop('selected_product_for_quotation_new', None)
                        st.success("✅ 항목이 추가되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 최대 5개까지만 추가 가능합니다.")

    # 추가된 항목 목록 표시
    if st.session_state.quotation_items:
        st.markdown("---")
        st.subheader("📋 견적 항목 목록")
        
        items_data = []
        for idx, item in enumerate(st.session_state.quotation_items):
            detail_text = item.get('item_detail_description', '')
            detail_preview = detail_text[:30] + '...' if len(detail_text) > 30 else detail_text
            
            items_data.append({
                'No': idx + 1,
                'Code': item['product_code'],
                '품명': item['product_name_vn'],
                '상세설명': detail_preview if detail_preview else '-',
                '수량': f"{item['quantity']:,}",
                '단가': f"{item['unit_price_vnd']:,.0f}",
                '합계': f"{item['line_total']:,.0f}",
            })
        
        df_items = pd.DataFrame(items_data)
        st.dataframe(df_items[['No', 'Code', '품명', '상세설명', '수량', '단가', '합계']], use_container_width=True, hide_index=True)
        
        # ✅ 항목 수정/삭제
        st.markdown("---")
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        
        with col1:
            action_idx = st.number_input("항목 번호", min_value=1, max_value=len(st.session_state.quotation_items), value=1, key="action_item_idx")
        
        with col2:
            if st.button("✏️ 수정", use_container_width=True):
                st.session_state.editing_item_idx = action_idx - 1
                st.rerun()
        
        with col3:
            if st.button("🗑️ 삭제", use_container_width=True):
                st.session_state.quotation_items.pop(action_idx - 1)
                st.success("✅ 항목이 삭제되었습니다!")
                st.rerun()
        
        # ✅ 항목 수정 UI
        if st.session_state.get('editing_item_idx') is not None:
            editing_idx = st.session_state.editing_item_idx
            editing_item = st.session_state.quotation_items[editing_idx]
            
            st.markdown("---")
            st.subheader(f"📝 항목 {editing_idx + 1} 수정")
            
            st.info(f"제품: {editing_item['product_code']} - {editing_item['product_name_vn']}")
            
            col1, col2 = st.columns(2)
            with col1:
                edit_quantity = st.number_input("수량", min_value=1, value=editing_item['quantity'], key="edit_qty")
            with col2:
                edit_unit_price = st.number_input("단가 (VND)", min_value=0.0, value=float(editing_item['unit_price_vnd']), step=10000.0, format="%.0f", key="edit_price")
            
            edit_detail_description = st.text_area(
                "상세 설명", 
                value=editing_item.get('item_detail_description', ''),
                height=80,
                key="edit_detail_desc"
            )
            
            st.metric("합계", f"{edit_quantity * edit_unit_price:,.0f} VND")
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 수정 저장", type="primary", use_container_width=True):
                    st.session_state.quotation_items[editing_idx]['quantity'] = edit_quantity
                    st.session_state.quotation_items[editing_idx]['unit_price_vnd'] = edit_unit_price
                    st.session_state.quotation_items[editing_idx]['line_total'] = edit_quantity * edit_unit_price
                    st.session_state.quotation_items[editing_idx]['item_detail_description'] = edit_detail_description.strip()
                    st.session_state.pop('editing_item_idx', None)
                    st.success("✅ 항목이 수정되었습니다!")
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ 취소", use_container_width=True):
                    st.session_state.pop('editing_item_idx', None)
                    st.rerun()
        
        # 총 금액 계산
        exchange_rate = 26387.45
        total_vnd = sum(item['line_total'] for item in st.session_state.quotation_items)
        discount_rate = st.number_input("전체 할인율 (%)", min_value=0.0, max_value=100.0, value=0.0, format="%.1f", key="quotation_discount_new")
        vat_rate = st.selectbox("VAT율 (%)", [0.0, 7.0, 10.0], index=2, key="quotation_vat_new")
        
        discounted_total = total_vnd * (1 - discount_rate / 100)
        vat_amount = discounted_total * (vat_rate / 100)
        final_amount = discounted_total + vat_amount
        
        st.markdown("---")
        st.subheader("💰 금액 계산")
        
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        with calc_col1:
            st.metric("소계", f"{total_vnd:,.0f} VND")
        with calc_col2:
            st.metric("할인 후", f"{discounted_total:,.0f} VND")
            st.caption(f"VAT: {vat_amount:,.0f}")
        with calc_col3:
            st.metric("최종 금액", f"{final_amount:,.0f} VND")
            st.caption(f"${final_amount / exchange_rate:,.2f}")
    
    # 항목이 없으면 저장 불가
    if not st.session_state.quotation_items:
        st.warning("⚠️ 최소 1개 이상의 제품을 추가해주세요.")
        return
    
    with st.form("quotation_form_new"):
        st.subheader("기본 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            quote_number = generate_quote_number(load_func, quotation_table)
            st.text_input("견적번호", value=quote_number, disabled=True)
            quote_date = st.date_input("견적일", value=datetime.now().date())
        
        with col2:
            valid_until = st.date_input("유효기간", value=datetime.now().date() + timedelta(days=30))
            currency = st.selectbox("통화", ['VND', 'USD', 'KRW'], index=0)
        
        st.subheader("프로젝트 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("프로젝트명", value='')
            part_name = st.text_input("부품명", value='')
            mold_number = st.text_input("금형번호", value='')
            part_weight = st.number_input("부품 중량(g)", min_value=0.0, value=0.0, format="%.2f")
        
        with col2:
            hrs_info = st.text_input("HRS 정보", value='')
            resin_type = st.text_input("수지 종류", value='')
            resin_additive = st.text_input("수지 첨가제", value='')
            sol_voltage = st.radio("솔레노이드 전압", ["DC 24V", "AC 220V"], horizontal=True, key="sol_voltage_new")
        
        st.subheader("거래 조건")
        col1, col2 = st.columns(2)
        
        with col1:
            payment_terms = st.radio(
                "결제 조건",
                ["T/T 30 days", "T/T 60 days", "T/T 90 days", "L/C at sight", "CAD"],
                horizontal=True,
                key="payment_terms_new"
            )
            st.text_input(
                "납기일 / Delivery Date",
                value="15 ngày làm việc sau khi phê duyệt PO và bản vẽ / 15 working days after PO & drawing approval",
                disabled=True,
                key="delivery_terms_display"
            )
            delivery_date = None
        
        with col2:
            lead_time_days = st.number_input("리드타임(일)", min_value=0, value=15)
            remarks = st.text_area("비고", value='')
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            temp_save = st.form_submit_button("임시저장", use_container_width=True)
        with col2:
            final_save = st.form_submit_button("정식저장", type="primary", use_container_width=True)
        
        if temp_save or final_save:
            discount_rate = st.session_state.get("quotation_discount_new", 0)
            vat_rate = st.session_state.get("quotation_vat_new", 7.0)
            exchange_rate = 26387.45
            
            total_vnd = sum(item['line_total'] for item in st.session_state.quotation_items)
            discounted_total = total_vnd * (1 - discount_rate / 100)
            vat_amount = discounted_total * (vat_rate / 100)
            final_amount = discounted_total + vat_amount
            
            customer_company_name = selected_customer.get('company_name_original')
            

            # 견적서 기본 정보
            quotation_data = {
                'customer_name': customer_company_name[:100],
                'company': customer_company_name[:200],
                'quote_date': quote_date.isoformat(),
                'valid_until': valid_until.isoformat(),
                'customer_id': selected_customer['id'],
                'contact_person': (selected_customer.get('contact_person') or '')[:100],
                'email': (selected_customer.get('email') or '')[:100],
                'phone': (selected_customer.get('phone') or '')[:20],
                'customer_address': selected_customer.get('address'),
                'quote_number': quote_number[:30],
                'revision_number': 'Rv00',
                'currency': 'VND',
                'status': 'Draft' if temp_save else 'Sent',
                'sales_rep_id': sales_rep_id,
                'item_name': None,
                'item_code': None,
                'item_name_en': None,
                'item_name_vn': None,
                'quantity': None,
                'unit_price': None,
                'unit_price_vnd': None,
                'std_price': None,
                'discounted_price': None,
                'discount_rate': discount_rate,
                'vat_rate': vat_rate,
                'vat_amount': vat_amount,
                'final_amount': final_amount,
                'final_amount_usd': final_amount / exchange_rate,
                'exchange_rate': exchange_rate,
                'project_name': (safe_strip(project_name) or None)[:200] if safe_strip(project_name) else None,
                'part_name': (safe_strip(part_name) or None)[:200] if safe_strip(part_name) else None,
                'mold_number': (safe_strip(mold_number) or None)[:100] if safe_strip(mold_number) else None,
                'part_weight': part_weight if part_weight > 0 else None,
                'hrs_info': (safe_strip(hrs_info) or None)[:200] if safe_strip(hrs_info) else None,
                'resin_type': (safe_strip(resin_type) or None)[:100] if safe_strip(resin_type) else None,
                'resin_additive': (safe_strip(resin_additive) or None)[:200] if safe_strip(resin_additive) else None,
                'sol_voltage': sol_voltage[:20],
                'payment_terms': (safe_strip(payment_terms) or None)[:200] if safe_strip(payment_terms) else None,
                'delivery_date': delivery_date.isoformat() if delivery_date else None,
                'lead_time_days': lead_time_days,
                'remarks': safe_strip(remarks),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            # ✅ 견적서 저장
            quotation_result = save_func(quotation_table, quotation_data)
            
            if quotation_result:
                # ✅ 딕셔너리에서 ID 추출
                quotation_id = quotation_result.get('id') if isinstance(quotation_result, dict) else quotation_result
                
                # quotation_items 저장
                current_user = st.session_state.get('current_user', {})
                company_code = current_user.get('company', 'YMV')
                from utils.helpers import get_company_table
                quotation_items_table = f'quotation_items_{company_code.lower()}'

                # ✅ quotation_items 저장 (item_detail_description 추가)
                for item in st.session_state.quotation_items:
                    item_data = {
                        'quotation_id': quotation_id,
                        'product_id': item['product_id'],
                        'item_description': f"{item['product_code']} - {item['product_name_vn']}",
                        'item_detail_description': item.get('item_detail_description', ''),
                        'quantity': item['quantity'],
                        'unit_price': item['unit_price_vnd'],
                        'line_total': item['line_total']
                    }
                    save_func(quotation_items_table, item_data)

                save_type = "임시저장" if temp_save else "정식저장"
                st.success(f"✅ 견적서가 성공적으로 {save_type}되었습니다!")
                st.session_state.pop('selected_customer_for_quotation', None)
                st.session_state.show_quotation_input_form = False
                st.session_state.pop('quotation_items', None)
                st.session_state.pop('editing_item_idx', None)
                st.rerun()
            else:
                st.error("❌ 견적서 저장에 실패했습니다.")

def render_quotation_list(load_func, update_func, delete_func, save_func, 
                         customer_table, quotation_table):
    """견적서 목록 및 관리"""
    
    # 프린트 모드 체크
    if st.session_state.get('print_quotation'):
        print_quotation = st.session_state['print_quotation']
        customer_table_for_print = st.session_state.get('print_customer_table', customer_table)
        
        # HTML 생성
        html_content = generate_quotation_html(print_quotation, load_func, customer_table_for_print)
        
        # HTML 표시
        st.components.v1.html(html_content, height=800, scrolling=True)
        
        # 돌아가기 버튼
        if st.button("← 목록으로 돌아가기", type="primary"):
            del st.session_state['print_quotation']
            st.rerun()
        return
    
    # 수정 모드 체크
    if st.session_state.get('editing_quotation_id'):
        render_quotation_edit_inline(load_func, update_func, save_func, delete_func, customer_table, quotation_table)
        return
    
    st.subheader("📋 견적서 목록")
    
    # 데이터 로드
    quotations = load_func(quotation_table) or []
    customers = load_func(customer_table) or []
    
    if not quotations:
        st.info("등록된 견적서가 없습니다.")
        return
    
    # 고객 딕셔너리 생성
    customer_dict = {c.get('id'): c for c in customers}
    
    # 검색 및 필터
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 검색", placeholder="견적번호/고객명")
    
    with col2:
        status_filter = st.selectbox("상태", ["전체", "Draft", "Sent", "Approved", "Rejected", "Expired"])
    
    with col3:
        sort_order = st.selectbox("정렬", ["최신순", "오래된순"])
    
    # 필터링
    filtered = quotations.copy()
    
    if search_term:
        filtered = [q for q in filtered 
                   if search_term.lower() in q.get('quote_number', '').lower()
                   or search_term.lower() in customer_dict.get(q.get('customer_id'), {}).get('company_name_short', '').lower()]
    
    if status_filter != "전체":
        filtered = [q for q in filtered if q.get('status') == status_filter]
    
    # 정렬
    if sort_order == "최신순":
        filtered.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    else:
        filtered.sort(key=lambda x: x.get('created_at', ''))
    
    # 테이블 표시
    if filtered:
        table_data = []
        for q in filtered:
            customer = customer_dict.get(q.get('customer_id'), {})
            table_data.append({
                'ID': q.get('id'),
                '견적번호': q.get('quote_number', 'N/A'),
                '고객': customer.get('company_name_short', 'N/A'),
                '견적일': q.get('quote_date', 'N/A'),
                '유효기한': q.get('valid_until', 'N/A'),
                '상태': q.get('status', 'Draft'),
                '금액': f"{q.get('final_amount', 0):,}",
                '통화': q.get('currency', 'USD')
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"📊 총 **{len(filtered)}건** 견적서")
    else:
        st.info("검색 결과가 없습니다.")
    
    st.markdown("---")
    
    # 컨트롤 버튼
    render_quotation_controls(load_func, update_func, delete_func, save_func, quotation_table, customer_table)

def render_quotation_edit_inline(load_func, update_func, save_func, delete_func, customer_table, quotation_table):
    """목록 내 인라인 수정 - 여러 제품 지원"""
   
    editing_data = st.session_state.get('editing_quotation_data', {})
    
    st.header("견적서 수정")
    
    current_user = st.session_state.get('current_user', {})
    company_code = current_user.get('company', 'YMV')
    from utils.helpers import get_company_table
    
    customers_data = load_func(customer_table)
    employees_data = load_func('employees')
    products_table = get_company_table('products', company_code)
    products_data = load_func(products_table)
    quotation_items_table = f'quotation_items_{company_code.lower()}'
    
    customers_df = pd.DataFrame(customers_data) if customers_data else pd.DataFrame()
    employees_df = pd.DataFrame(employees_data) if employees_data else pd.DataFrame()
    products_df = pd.DataFrame(products_data) if products_data else pd.DataFrame()
    
    if customers_df.empty or employees_df.empty or products_df.empty:
        st.warning("필요한 데이터가 없습니다.")
        return
    
    # ✅ 기존 quotation_items 로드
    if 'editing_quotation_items' not in st.session_state:
        existing_items_data = load_func(quotation_items_table)
        if existing_items_data:
            existing_items = [item for item in existing_items_data if item.get('quotation_id') == editing_data['id']]
            
            # 제품 정보와 매칭
            st.session_state.editing_quotation_items = []
            for item in existing_items:
                product = products_df[products_df['id'] == item.get('product_id')]
                if not product.empty:
                    product_data = product.iloc[0]
                    st.session_state.editing_quotation_items.append({
                        'product_id': item.get('product_id'),
                        'product_code': product_data.get('product_code'),
                        'product_name_vn': product_data.get('product_name_vn'),
                        'product_name_en': product_data.get('product_name_en'),
                        'quantity': item.get('quantity', 1),
                        'unit_price_vnd': item.get('unit_price', 0),
                        'line_total': item.get('line_total', 0),
                        'cost_price_usd': product_data.get('cost_price_usd', 0),
                        'item_detail_description': item.get('item_detail_description', '')
                    })
        else:
            st.session_state.editing_quotation_items = []
    
    st.subheader("고객 및 담당자")
    col1, col2 = st.columns(2)
    
    with col1:
        customer_options = [f"{row.get('company_name_short') or row.get('company_name_original')} ({row['id']})" for _, row in customers_df.iterrows()]
        default_customer_index = 0
        if editing_data.get('customer_id'):
            try:
                default_customer_index = next(i for i, opt in enumerate(customer_options) if f"({editing_data['customer_id']})" in opt)
            except:
                pass
        
        selected_customer = st.selectbox("고객사", customer_options, index=default_customer_index, key="quotation_customer_select_edit")
        customer_id = int(selected_customer.split('(')[-1].split(')')[0])
        selected_customer_data = customers_df[customers_df['id'] == customer_id].iloc[0]
        
        with st.expander("고객 정보", expanded=False):
            st.write(f"담당자: {selected_customer_data.get('contact_person', 'N/A')}")
            st.write(f"이메일: {selected_customer_data.get('email', 'N/A')}")
            st.write(f"전화: {selected_customer_data.get('phone', 'N/A')}")
            st.write(f"주소: {selected_customer_data.get('address', 'N/A')}")
    
    with col2:
        employee_options = [f"{row['name']} ({row['department']}) [{row['id']}]" for _, row in employees_df.iterrows()]
        default_employee_index = 0
        if editing_data.get('sales_rep_id'):
            try:
                default_employee_index = next(i for i, opt in enumerate(employee_options) if f"[{editing_data['sales_rep_id']}]" in opt)
            except:
                pass
        
        selected_employee = st.selectbox("영업담당자", employee_options, index=default_employee_index, key="quotation_employee_select_edit")
        sales_rep_id = int(selected_employee.split('[')[-1].split(']')[0])
    
    st.subheader("📦 제품 항목 추가/수정")
    
    # ✅ 최대 5개 제한 표시
    st.info(f"📋 현재 {len(st.session_state.editing_quotation_items)}/5 개 제품")
    
    # ✅ 제품 추가 UI (5개 미만일 때만)
    if len(st.session_state.editing_quotation_items) < 5:
        if not st.session_state.get('selected_product_for_quotation_edit'):
            render_product_selection_for_quotation(load_func, mode='edit')
        else:
            selected_product_data = st.session_state.selected_product_for_quotation_edit
            
            st.success(f"✅ 선택된 제품: {selected_product_data.get('product_code', '')} - {selected_product_data.get('product_name_vn', '')}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                item_quantity = st.number_input("수량", min_value=1, value=1, key="item_qty_temp_edit")
            with col2:
                item_unit_price = st.number_input("단가 (VND)", min_value=0.0, value=float(selected_product_data.get('actual_selling_price_vnd', 0)), step=10000.0, format="%.0f", key="item_price_temp_edit")
            with col3:
                st.metric("합계", f"{item_quantity * item_unit_price:,.0f} VND")
            
            # ✅ 상세 설명 입력란 추가
            item_detail_description = st.text_area(
                "상세 설명 (선택사항)", 
                placeholder="예: 특수 코팅, 색상 지정, 포장 방법, 기타 요구사항 등",
                height=80,
                key="item_detail_desc_temp_edit",
                help="이 내용은 견적서 출력 시 제품명 아래에 표시됩니다."
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
            with col_btn2:
                if st.button("➕ 항목 추가", type="primary", use_container_width=True, key="add_item_edit"):
                    if len(st.session_state.editing_quotation_items) < 5:
                        item = {
                            'product_id': selected_product_data.get('id'),
                            'product_code': selected_product_data.get('product_code'),
                            'product_name_vn': selected_product_data.get('product_name_vn'),
                            'product_name_en': selected_product_data.get('product_name_en'),
                            'quantity': item_quantity,
                            'unit_price_vnd': item_unit_price,
                            'line_total': item_quantity * item_unit_price,
                            'cost_price_usd': selected_product_data.get('cost_price_usd', 0),
                            'item_detail_description': item_detail_description.strip() if item_detail_description else ''
                        }
                        st.session_state.editing_quotation_items.append(item)
                        st.session_state.pop('selected_product_for_quotation_edit', None)
                        st.success("✅ 항목이 추가되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 최대 5개까지만 추가 가능합니다.")
    else:
        st.warning("⚠️ 최대 5개 제품까지만 추가할 수 있습니다.")
    
    # ✅ 추가된 항목 목록 표시
    if st.session_state.editing_quotation_items:
        st.markdown("---")
        st.subheader("📋 견적 항목 목록")
        
        items_data = []
        for idx, item in enumerate(st.session_state.editing_quotation_items):
            detail_text = item.get('item_detail_description', '')
            detail_preview = detail_text[:30] + '...' if len(detail_text) > 30 else detail_text
            
            items_data.append({
                'No': idx + 1,
                'Code': item['product_code'],
                '품명': item['product_name_vn'],
                '상세설명': detail_preview if detail_preview else '-',
                '수량': f"{item['quantity']:,}",
                '단가': f"{item['unit_price_vnd']:,.0f}",
                '합계': f"{item['line_total']:,.0f}",
            })
        
        df_items = pd.DataFrame(items_data)
        st.dataframe(df_items[['No', 'Code', '품명', '상세설명', '수량', '단가', '합계']], use_container_width=True, hide_index=True)

        # ✅ 항목 수정/삭제 UI
        st.markdown("---")
        st.markdown("### 항목 관리")
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        
        with col1:
            action_idx = st.number_input("항목 번호", min_value=1, max_value=len(st.session_state.editing_quotation_items), value=1, key="action_item_idx_edit")
        
        with col2:
            if st.button("✏️ 수정", use_container_width=True, key="btn_edit_item_edit"):
                st.session_state.editing_item_idx_edit = action_idx - 1
                st.rerun()
        
        with col3:
            if st.button("🗑️ 삭제", use_container_width=True, key="btn_delete_item_edit"):
                st.session_state.editing_quotation_items.pop(action_idx - 1)
                st.success("✅ 항목이 삭제되었습니다!")
                st.rerun()

        # ✅ 항목 수정 UI
        if st.session_state.get('editing_item_idx_edit') is not None:
            editing_idx = st.session_state.editing_item_idx_edit
            editing_item = st.session_state.editing_quotation_items[editing_idx]
            
            st.markdown("---")
            st.subheader(f"📝 항목 {editing_idx + 1} 수정")
            
            st.info(f"제품: {editing_item['product_code']} - {editing_item['product_name_vn']}")
            
            col1, col2 = st.columns(2)
            with col1:
                edit_quantity = st.number_input("수량", min_value=1, value=int(editing_item['quantity']), key="edit_qty_edit")
            with col2:
                edit_unit_price = st.number_input("단가 (VND)", min_value=0.0, value=float(editing_item['unit_price_vnd']), step=10000.0, format="%.0f", key="edit_price_edit")
            
            edit_detail_description = st.text_area(
                "상세 설명", 
                value=editing_item.get('item_detail_description', ''),
                height=80,
                key="edit_detail_desc_edit"
            )
            
            st.metric("합계", f"{edit_quantity * edit_unit_price:,.0f} VND")
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 수정 저장", type="primary", use_container_width=True, key="btn_save_edit_edit"):
                    st.session_state.editing_quotation_items[editing_idx]['quantity'] = edit_quantity
                    st.session_state.editing_quotation_items[editing_idx]['unit_price_vnd'] = edit_unit_price
                    st.session_state.editing_quotation_items[editing_idx]['line_total'] = edit_quantity * edit_unit_price
                    st.session_state.editing_quotation_items[editing_idx]['item_detail_description'] = edit_detail_description.strip()
                    st.session_state.pop('editing_item_idx_edit', None)
                    st.success("✅ 항목이 수정되었습니다!")
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ 취소", use_container_width=True, key="btn_cancel_edit_edit"):
                    st.session_state.pop('editing_item_idx_edit', None)
                    st.rerun()


        # 총 금액 계산
        exchange_rate = 26387.45
        total_vnd = sum(item['line_total'] for item in st.session_state.editing_quotation_items)
        discount_rate = st.number_input("전체 할인율 (%)", min_value=0.0, max_value=100.0, value=float(editing_data.get('discount_rate', 0.0)), format="%.1f", key="quotation_discount_edit")
        vat_rate = st.selectbox("VAT율 (%)", [0.0, 7.0, 10.0], index=[0.0, 7.0, 10.0].index(editing_data.get('vat_rate', 10.0)) if editing_data.get('vat_rate', 10.0) in [0.0, 7.0, 10.0] else 2, key="quotation_vat_edit")
        
        discounted_total = total_vnd * (1 - discount_rate / 100)
        vat_amount = discounted_total * (vat_rate / 100)
        final_amount = discounted_total + vat_amount
        
        st.markdown("---")
        st.subheader("💰 금액 계산")
        
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        with calc_col1:
            st.metric("소계", f"{total_vnd:,.0f} VND")
        with calc_col2:
            st.metric("할인 후", f"{discounted_total:,.0f} VND")
            st.caption(f"VAT: {vat_amount:,.0f}")
        with calc_col3:
            st.metric("최종 금액", f"{final_amount:,.0f} VND")
            st.caption(f"${final_amount / exchange_rate:,.2f}")
    
    # 항목이 없으면 저장 불가
    if not st.session_state.editing_quotation_items:
        st.warning("⚠️ 최소 1개 이상의 제품을 추가해주세요.")
        if st.button("❌ 취소", use_container_width=True, key="cancel_edit_no_items"):
            st.session_state.pop('editing_quotation_id', None)
            st.session_state.pop('editing_quotation_data', None)
            st.session_state.pop('editing_quotation_items', None)
            st.session_state.pop('selected_product_for_quotation_edit', None)
            st.session_state.pop('show_product_selector_edit', None)
            st.rerun()
        return
    
    with st.form("quotation_form_edit"):
        st.subheader("기본 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("견적번호", value=editing_data.get('quote_number', ''), disabled=True)
            quote_date = st.date_input("견적일", value=datetime.fromisoformat(editing_data.get('quote_date')) if editing_data.get('quote_date') else datetime.now().date())
        
        with col2:
            valid_until = st.date_input("유효기간", value=datetime.fromisoformat(editing_data.get('valid_until')) if editing_data.get('valid_until') else datetime.now().date() + timedelta(days=30))
            currency = st.selectbox("통화", ['VND', 'USD', 'KRW'], index=0)
        
        st.subheader("프로젝트 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("프로젝트명", value=editing_data.get('project_name') or '')
            part_name = st.text_input("부품명", value=editing_data.get('part_name') or '')
            mold_number = st.text_input("금형번호", value=editing_data.get('mold_number', editing_data.get('mold_no')) or '')
            part_weight = st.number_input("부품 중량(g)", min_value=0.0, value=float(editing_data.get('part_weight') or 0.0), format="%.2f")
        
        with col2:
            hrs_info = st.text_input("HRS 정보", value=editing_data.get('hrs_info') or '')
            resin_type = st.text_input("수지 종류", value=editing_data.get('resin_type') or '')
            resin_additive = st.text_input("수지 첨가제", value=editing_data.get('resin_additive') or '')
            sol_voltage = st.radio(
                "솔레노이드 전압", 
                ["DC 24V", "AC 220V"], 
                horizontal=True,
                index=0 if editing_data.get('sol_voltage') == 'DC 24V' else 1,
                key="sol_voltage_edit"
            )
        
        st.subheader("거래 조건")
        col1, col2 = st.columns(2)
        
        with col1:
            payment_terms = st.radio(
                "결제 조건",
                ["T/T 30 days", "T/T 60 days", "T/T 90 days", "L/C at sight", "CAD"],
                horizontal=True,
                index=0,
                key="payment_terms_edit"
            )
            
            st.text_input(
                "납기일 / Delivery Date",
                value="15 ngày làm việc sau khi phê duyệt PO và bản vẽ / 15 working days after PO & drawing approval",
                disabled=True,
                key="delivery_terms_edit"
            )
            
            delivery_date = None
        with col2:
            lead_time_days = st.number_input("리드타임(일)", min_value=0, value=int(editing_data.get('lead_time_days') or 30))
            remarks = st.text_area("비고", value=editing_data.get('remarks', editing_data.get('remark')) or '')
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            save_btn = st.form_submit_button("💾 수정 저장 (Revision 증가)", type="primary", use_container_width=True)
        with col2:
            cancel_btn = st.form_submit_button("❌ 취소", use_container_width=True)
        
        if save_btn:
            current_revision = editing_data.get('revision_number', 'Rv00')
            new_revision = get_next_revision_number(current_revision)
            
            discount_rate = st.session_state.get("quotation_discount_edit", 0)
            vat_rate = st.session_state.get("quotation_vat_edit", 7.0)
            exchange_rate = 26387.45
            
            total_vnd = sum(item['line_total'] for item in st.session_state.editing_quotation_items)
            discounted_total = total_vnd * (1 - discount_rate / 100)
            vat_amount = discounted_total * (vat_rate / 100)
            final_amount = discounted_total + vat_amount
            
            customer_company_name = selected_customer_data.get('company_name_original')
            
            quotation_data = {
                'id': editing_data['id'],
                'customer_name': customer_company_name[:100],
                'company': customer_company_name[:200],
                'quote_date': quote_date.isoformat(),
                'valid_until': valid_until.isoformat(),
                'customer_id': customer_id,
                'contact_person': (selected_customer_data.get('contact_person') or '')[:100],
                'email': (selected_customer_data.get('email') or '')[:100],
                'phone': (selected_customer_data.get('phone') or '')[:20],
                'customer_address': selected_customer_data.get('address'),
                'quote_number': editing_data['quote_number'],
                'revision_number': new_revision,
                'currency': 'VND',
                'status': editing_data.get('status', 'Draft'),
                'sales_rep_id': sales_rep_id,
                'item_name': None,
                'item_code': None,
                'item_name_en': None,
                'item_name_vn': None,
                'quantity': None,
                'unit_price': None,
                'unit_price_vnd': None,
                'std_price': None,
                'discounted_price': None,
                'discount_rate': discount_rate,
                'vat_rate': vat_rate,
                'vat_amount': vat_amount,
                'final_amount': final_amount,
                'final_amount_usd': final_amount / exchange_rate,
                'exchange_rate': exchange_rate,
                'project_name': (safe_strip(project_name) or None)[:200] if safe_strip(project_name) else None,
                'part_name': (safe_strip(part_name) or None)[:200] if safe_strip(part_name) else None,
                'mold_number': (safe_strip(mold_number) or None)[:100] if safe_strip(mold_number) else None,
                'part_weight': part_weight if part_weight > 0 else None,
                'hrs_info': (safe_strip(hrs_info) or None)[:200] if safe_strip(hrs_info) else None,
                'resin_type': (safe_strip(resin_type) or None)[:100] if safe_strip(resin_type) else None,
                'resin_additive': (safe_strip(resin_additive) or None)[:200] if safe_strip(resin_additive) else None,
                'sol_voltage': sol_voltage[:20],
                'payment_terms': (safe_strip(payment_terms) or None)[:200] if safe_strip(payment_terms) else None,
                'delivery_date': delivery_date.isoformat() if delivery_date else None,
                'lead_time_days': lead_time_days,
                'remarks': safe_strip(remarks),
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                # ✅ 견적서 업데이트
                success = update_func(quotation_table, quotation_data)
                
                if success:
                    # ✅ 기존 quotation_items 삭제
                    try:
                        existing_items = load_func(quotation_items_table)
                        if existing_items:
                            for item in existing_items:
                                if item.get('quotation_id') == editing_data['id']:
                                    item_id = item.get('item_id')
                                    if item_id:
                                        delete_func(quotation_items_table, item_id, id_field='item_id')
                    except Exception as delete_error:
                        st.warning(f"기존 항목 삭제 중 오류: {str(delete_error)}")
                    
                    # ✅ 새 quotation_items 저장 (item_detail_description 포함)
                    for item in st.session_state.editing_quotation_items:
                        item_data = {
                            'quotation_id': editing_data['id'],
                            'product_id': item['product_id'],
                            'item_description': f"{item['product_code']} - {item['product_name_vn']}",
                            'item_detail_description': item.get('item_detail_description', ''),
                            'quantity': item['quantity'],
                            'unit_price': item['unit_price_vnd'],
                            'line_total': item['line_total']
                        }
                        save_func(quotation_items_table, item_data)
                    
                    st.success(f"✅ 견적서가 수정되었습니다! (Rev: {new_revision})")
                    st.session_state.pop('editing_quotation_id', None)
                    st.session_state.pop('editing_quotation_data', None)
                    st.session_state.pop('editing_quotation_items', None)
                    st.session_state.pop('selected_product_for_quotation_edit', None)
                    st.session_state.pop('show_product_selector_edit', None)
                    st.session_state.pop('editing_item_idx_edit', None)
                    st.rerun()
                else:
                    st.error("❌ 수정 실패")
            except Exception as e:
                st.error(f"❌ 수정 실패: {str(e)}")
        
        if cancel_btn:
            st.session_state.pop('editing_quotation_id', None)
            st.session_state.pop('editing_quotation_data', None)
            st.session_state.pop('editing_quotation_items', None)
            st.session_state.pop('selected_product_for_quotation_edit', None)
            st.session_state.pop('show_product_selector_edit', None)
            st.session_state.pop('editing_item_idx_edit', None)
            st.info("✅ 수정이 취소되었습니다.")
            st.rerun()

def render_quotation_search_filters(quotations_df):
    """검색 필터"""
    st.markdown("### 🔍 견적서 검색")
    
    col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
    
    with col1:
        st.text_input("🔍 검색", placeholder="견적번호/고객사명", key="quotation_search_term")
    
    with col2:
        statuses = ['Draft', 'Sent', 'Approved', 'Rejected', 'Expired']
        st.selectbox("상태", ["전체"] + statuses, key="quotation_status_filter")
    
    with col3:
        date_options = ["전체", "오늘", "이번주", "이번달", "사용자 지정"]
        st.selectbox("기간", date_options, key="quotation_date_filter")
    
    with col4:
        st.write("")
        st.write("")
        if st.button("📥 CSV", use_container_width=True):
            csv_data = generate_quotations_csv(quotations_df)
            st.download_button("다운로드", csv_data, f"quotations_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    
    st.markdown("---")


def get_filtered_quotations(quotations_df):
    """필터 적용"""
    filtered = quotations_df.copy()
    
    search_term = st.session_state.get('quotation_search_term', '')
    if search_term:
        filtered = filtered[
            filtered['quote_number'].str.contains(search_term, case=False, na=False) |
            filtered['customer_company'].str.contains(search_term, case=False, na=False)
        ]
    
    status = st.session_state.get('quotation_status_filter', '전체')
    if status != '전체':
        filtered = filtered[filtered['status'] == status]
    
    date_filter = st.session_state.get('quotation_date_filter', '전체')
    if date_filter != '전체':
        today = datetime.now().date()
        
        if date_filter == "오늘":
            filtered = filtered[pd.to_datetime(filtered['quote_date']).dt.date == today]
        elif date_filter == "이번주":
            week_start = today - timedelta(days=today.weekday())
            filtered = filtered[pd.to_datetime(filtered['quote_date']).dt.date >= week_start]
        elif date_filter == "이번달":
            month_start = today.replace(day=1)
            filtered = filtered[pd.to_datetime(filtered['quote_date']).dt.date >= month_start]
    
    return filtered.sort_values('id', ascending=False)

def render_quotation_table(quotations_df):
    """견적서 테이블 - 기존 방식"""
    if quotations_df.empty:
        st.info("조건에 맞는 견적서가 없습니다.")
        return
    
    table_data = []
    for _, row in quotations_df.iterrows():
        table_data.append({
            'ID': row.get('id', ''),
            'Quote No': row.get('quote_number', ''),
            'Rev': row.get('revision_number', 'Rv00'),
            'Customer': row.get('customer_company', ''),
            'Project': row.get('project_name', ''),
            'Item': row.get('item_name_en', ''),
            'Resin': row.get('resin_type', ''),
            'Qty': f"{row.get('quantity', 0):,}",
            'Amount': f"{row.get('final_amount', 0):,.0f}",
            'Currency': row.get('currency', 'VND'),
            'Date': row.get('quote_date', ''),
            'Status': row.get('status', 'Draft')
        })
    
    df = pd.DataFrame(table_data)
    
    def highlight_status(val):
        colors = {
            'Draft': 'background-color: #808080; color: white',
            'Sent': 'background-color: #1f77b4; color: white',
            'Approved': 'background-color: #2ca02c; color: white',
            'Rejected': 'background-color: #d62728; color: white',
            'Expired': 'background-color: #ff7f0e; color: white'
        }
        return colors.get(val, '')
    
    styled_df = df.style.applymap(highlight_status, subset=['Status'])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    st.caption(f"📊 총 **{len(quotations_df)}개** 견적서")
    
    if not quotations_df.empty:
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_amount = quotations_df['final_amount'].fillna(0).sum()
            st.metric("총 견적 금액", f"{total_amount:,.0f} VND")
        
        with col2:
            approved_count = len(quotations_df[quotations_df['status'] == 'Approved'])
            st.metric("승인된 견적서", approved_count)
        
        with col3:
            sent_count = len(quotations_df[quotations_df['status'] == 'Sent'])
            st.metric("발송된 견적서", sent_count)
        
        with col4:
            approval_rate = (approved_count / len(quotations_df) * 100) if len(quotations_df) > 0 else 0
            st.metric("승인율", f"{approval_rate:.1f}%")


def generate_quotations_csv(quotations_df):
    """CSV 생성"""
    csv_data = []
    for _, row in quotations_df.iterrows():
        csv_data.append({
            'id': row.get('id', ''),
            'quote_number': row.get('quote_number', ''),
            'revision_number': row.get('revision_number', ''),
            'customer': row.get('customer_company', ''),
            'item': row.get('item_name_en', ''),
            'quantity': row.get('quantity', 0),
            'amount': row.get('final_amount', 0),
            'status': row.get('status', ''),
            'date': row.get('quote_date', '')
        })
    
    df = pd.DataFrame(csv_data)
    return df.to_csv(index=False, encoding='utf-8-sig')

def render_quotation_csv_management(load_func, save_func, quotation_table):
    """견적서 CSV 관리"""
    st.header("견적서 CSV 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CSV 다운로드")
        if st.button("견적서 CSV 다운로드", type="primary"):
            try:
                # 법인별 테이블에서 로드
                quotations_data = load_func(quotation_table)
                if not quotations_data:
                    st.warning("다운로드할 견적서가 없습니다.")
                    return
                
                quotations_df = pd.DataFrame(quotations_data)
                csv_data = quotations_df.to_csv(index=False, encoding='utf-8')
                st.download_button("CSV 파일 다운로드", csv_data, f"quotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")
                st.success(f"총 {len(quotations_df)}개의 견적서 데이터 준비 완료")
            except Exception as e:
                st.error(f"CSV 생성 오류: {str(e)}")
    
    with col2:
        st.subheader("CSV 업로드")
        st.info("견적서 CSV 업로드 기능은 추후 구현 예정입니다.")

def generate_quote_number(load_func, quotation_table='quotations'):
    """견적번호 자동 생성"""
    today = datetime.now()
    date_str = today.strftime('%y%m%d')
    
    try:
        quotations_data = load_func(quotation_table)  # ← quotation_table 사용
        if not quotations_data:
            return f"YMV-{date_str}-001"
        
        today_pattern = f"YMV-{date_str}-"
        today_quotes = [q for q in quotations_data if q.get('quote_number', '').startswith(today_pattern)]
        
        if not today_quotes:
            return f"YMV-{date_str}-001"
        
        max_count = 0
        for quote in today_quotes:
            try:
                count_str = quote.get('quote_number', '').split('-')[-1]
                count = int(count_str)
                if count > max_count:
                    max_count = count
            except:
                continue
        
        new_count = max_count + 1
        return f"YMV-{date_str}-{new_count:03d}"
    except:
        timestamp = today.strftime('%H%M%S')
        return f"YMV-{date_str}-{timestamp[:3]}"

def get_next_revision_number(current_revision):
    """Revision 번호 증가"""
    try:
        if current_revision and current_revision.startswith('Rv'):
            current_num = int(current_revision[2:])
            next_num = current_num + 1
            return f"Rv{next_num:02d}"
        else:
            return "Rv01"
    except:
        return "Rv01"

def generate_quotation_html(quotation, load_func, customer_table, language='한국어'):
    """견적서 HTML 생성"""
    try:
        import base64
        from pathlib import Path
        
        stamp_base64 = ""
        stamp_path = Path("D:/ymv-business-system/app/images/Stemp-sign.png")
        
        try:
            if stamp_path.exists():
                with open(stamp_path, "rb") as image_file:
                    stamp_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                    stamp_base64 = f"data:image/png;base64,{stamp_base64}"
        except Exception as e:
            logging.error(f"스탬프 이미지 로드 오류: {str(e)}")
        
        customers_data = load_func(customer_table)
        employees_data = load_func('employees')
        
        # ✅ quotation_items 로드
        current_user = st.session_state.get('current_user', {})
        company_code = current_user.get('company', 'YMV')
        from utils.helpers import get_company_table
        quotation_items_table = f'quotation_items_{company_code.lower()}'
        quotation_items_data = load_func(quotation_items_table)
        
        # 해당 견적서의 항목만 필터링
        items = []
        if quotation_items_data:
            items = [item for item in quotation_items_data if item.get('quotation_id') == quotation.get('id')]
        
        customers_df = pd.DataFrame(customers_data) if customers_data else pd.DataFrame()
        employees_df = pd.DataFrame(employees_data) if employees_data else pd.DataFrame()
        
        customer_info = {}
        if not customers_df.empty and quotation.get('customer_id'):
            customer_data = customers_df[customers_df['id'] == quotation['customer_id']]
            if not customer_data.empty:
                customer_info = customer_data.iloc[0].to_dict()
        
        if not customer_info:
            customer_info = {
                'company_name_original': quotation.get('company', quotation.get('customer_name', '')),
                'address': quotation.get('customer_address', ''),
                'contact_person': quotation.get('contact_person', ''),
                'phone': quotation.get('phone', ''),
                'email': quotation.get('email', '')
            }
        
        customer_company_name = customer_info.get('company_name_original', '')
        
        employee_info = {}
        if not employees_df.empty and quotation.get('sales_rep_id'):
            employee_data = employees_df[employees_df['id'] == quotation['sales_rep_id']]
            if not employee_data.empty:
                employee_info = employee_data.iloc[0].to_dict()
        
        stamp_img_tag = ""
        if stamp_base64:
            stamp_img_tag = f'<img src="{stamp_base64}" class="stamp-image" alt="Company Stamp" />'
        

        # ✅ 제품 테이블 HTML 생성 (3행 구조: 1)기본정보, 2)제품명, 3)상세설명)
        items_rows = ""
        if items:
            for idx, item in enumerate(items, 1):
                item_desc = item.get('item_description', '')
                # 제품 코드와 제품명 분리
                parts = item_desc.split(' - ')
                item_code = parts[0] if len(parts) > 0 else ''
                item_name_vn = parts[1] if len(parts) > 1 else item_desc
                
                # ✅ 상세 설명 가져오기
                detail_description = item.get('item_detail_description', '').strip()
                
                qty = item.get('quantity', 0)
                unit_price = item.get('unit_price', 0)
                line_total = item.get('line_total', 0)
                discount_rate = quotation.get('discount_rate', 0)
                discounted_price = unit_price * (1 - discount_rate / 100)
                
                # ✅ 3행 구조: 1) 기본 정보, 2) 제품명(베트남어), 3) 상세 설명
                items_rows += f"""
                    <tr>
                        <td rowspan="3" style="vertical-align: top; padding-top: 30px; font-weight: bold;">{idx}</td>
                        <td style="font-size: 10px;">{item_code}</td>
                        <td style="font-weight: bold;">{qty:,}</td>
                        <td class="text-right" style="font-size: 10px;">{unit_price:,.0f}</td>
                        <td style="font-weight: bold;">{discount_rate:.1f}%</td>
                        <td class="text-right" style="font-size: 10px; font-weight: bold;">{discounted_price:,.0f}</td>
                        <td class="text-right" style="font-size: 10px; font-weight: bold;">{line_total:,.0f}</td>
                    </tr>
                    <tr>
                        <td colspan="6" style="padding: 6px; border-top: none; text-align: left; color: #000; font-size: 11px;">
                            {item_name_vn}
                        </td>
                    </tr>
                    <tr>
                        <td colspan="6" style="padding: 8px; border-top: none; text-align: left; font-size: 10px; color: #555;">
                            {detail_description if detail_description else ''}
                        </td>
                    </tr>
                """
        else:
            # ✅ 항목이 없을 때
            items_rows = """
                <tr>
                    <td rowspan="3" style="vertical-align: top; padding-top: 30px; font-weight: bold;">1</td>
                    <td style="font-size: 10px;">No Item</td>
                    <td style="font-weight: bold;">0</td>
                    <td class="text-right" style="font-size: 10px;">0</td>
                    <td style="font-weight: bold;">0.0%</td>
                    <td class="text-right" style="font-size: 10px; font-weight: bold;">0</td>
                    <td class="text-right" style="font-size: 10px; font-weight: bold;">0</td>
                </tr>
                <tr>
                    <td colspan="6" style="padding: 8px; border-top: none; text-align: left; color: #000;"></td>
                </tr>
                <tr>
                    <td colspan="6" style="padding: 8px; border-top: none; text-align: left;"></td>
                </tr>
            """
        
        # ✅ 총액 계산
        discount_rate = quotation.get('discount_rate', 0)
        vat_rate = quotation.get('vat_rate', 0)
        subtotal = sum(item.get('line_total', 0) for item in items) if items else 0
        discounted_total = subtotal * (1 - discount_rate / 100)
        vat_amount = quotation.get('vat_amount', 0)
        final_amount = quotation.get('final_amount', 0)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Quotation - {quotation.get('quote_number', '')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
        .quotation {{ width: 210mm; min-height: 297mm; margin-bottom: 20px auto; background: white; padding: 15mm; box-shadow: 0 0 10px rgba(0,0,0,0.1); box-sizing: border-box; display: flex; flex-direction: column; }}
        .content-area {{ flex: 1; }}
        .bottom-fixed {{ margin-top: auto; }}
        
        .quotation-title {{ text-align: center; margin-bottom: 30px; }}
        .quotation-title h1 {{ font-size: 18px; font-weight: bold; margin: 0; letter-spacing: 3px; color: #000; }}
        
        .header {{ display: flex; justify-content: space-between; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #000; }}
        .company-name {{ font-size: 14px; font-weight: bold; }}
        .company-info {{ font-size: 12px; line-height: 1.4; }}
        .office-info {{ margin-top: 10px; font-size: 11px; }}
        .quote-details {{ display: flex; justify-content: space-between; margin-bottom: 20px; font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 11px; table-layout: fixed; }}
        th, td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: center; word-wrap: break-word; }}
        th {{ background-color: #f8f9fa; font-weight: bold; }}
        .text-left {{ text-align: left; }}
        .text-right {{ text-align: right; }}
        .totals {{ margin-top: 20px; }}
        .totals table {{ width: 350px; margin-left: auto; }}
        .totals table td {{ width: auto; }}
        .totals table td:nth-child(1) {{ width: 50%; text-align: center; }}
        .totals table td:nth-child(2) {{ width: 15%; text-align: center; }}
        .totals table td:nth-child(3) {{ width: 35%; text-align: right; }}
        .total-row {{ background-color: #e9ecef; font-weight: bold; }}
        .project-info {{ margin-top: 1px; border-top: 1px solid #ddd; padding-top: 1px; }}
        .project-table {{ width: 100%; font-size: 11px; }}
        .project-table td {{ padding: 6px; border: 1px solid #ddd; vertical-align: middle; }}
        .project-table td:nth-child(1) {{ width: 15%; font-weight: bold; background-color: #f8f9fa; }}
        .project-table td:nth-child(2) {{ width: 35%; }}
        .project-table td:nth-child(3) {{ width: 15%; font-weight: bold; background-color: #f8f9fa; }}
        .project-table td:nth-child(4) {{ width: 35%; }}
        .signature-section {{ margin-top: 40px; display: flex; justify-content: space-between; }}
        .signature-box {{ text-align: center; width: 200px; position: relative; }}
        .signature-line {{ border-bottom: 1px solid #000; margin: 30px 0 10px 0; height: 1px; }}
        .stamp-image {{ position: absolute; top: -60px; left: 50%; transform: translateX(-50%) rotate(-15deg); width: 120px; height: 120px; opacity: 0.8; }}
        @media print {{ body {{ background: white; margin: 0; padding: 0; }} .quotation {{ width: 210mm; min-height: 297mm; margin: 0; padding: 15mm; box-shadow: none; page-break-after: always; }} @page {{ size: A4; margin: 0; }} }}
    </style>
</head>
<body>
    <div class="quotation">
        <div class="content-area">
            
            <div class="quotation-title">
                <h1>QUOTATION</h1>
            </div>
            
            <div class="header">
                <div>
                    <div class="company-name">{customer_company_name}</div>
                    <div class="company-info">
                        Address: {customer_info.get('address', '')}<br><br>
                        Contact Person: {customer_info.get('contact_person', '')}<br>
                        Phone No.: {customer_info.get('phone', '')}<br>
                        E-mail: {customer_info.get('email', '')}
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
            <div class="quote-details">
                <div>Date: {quotation.get('quote_date', '')}</div>
                <div>Quote No.: {quotation.get('quote_number', '')}</div>
                <div>Rev. No.: {quotation.get('revision_number', 'Rv00')}</div>
                <div>Currency: {quotation.get('currency', 'VND')}</div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 3%;">NO</th>
                        <th style="width: 22%;">Item Code</th>
                        <th style="width: 5%;">Qty.</th>
                        <th style="width: 14%;">Std. Price</th>
                        <th style="width: 8%;">DC. Rate</th>
                        <th style="width: 12%;">Unit Price</th>
                        <th style="width: 16%;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {items_rows}
                </tbody>
            </table>
        </div>
        <div class="bottom-fixed">
            <div class="totals">
                <table>
                    <tr>
                        <td class="text-right">TOTAL VND Excl. VAT</td>
                        <td>VND</td>
                        <td class="text-right">{discounted_total:,.0f}</td>
                    </tr>
                    <tr>
                        <td class="text-right">TOTAL VND {vat_rate:.1f}% VAT</td>
                        <td>VND</td>
                        <td class="text-right">{vat_amount:,.0f}</td>
                    </tr>
                    <tr class="total-row">
                        <td class="text-right">TOTAL VND Incl. VAT</td>
                        <td>VND</td>
                        <td class="text-right">{final_amount:,.0f}</td>
                    </tr>
                </table>
            </div>
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
                        <td>{quotation.get('mold_number', '')}</td>
                        <td>Part Weight:</td>
                        <td>{quotation.get('part_weight') or ''} g</td>
                    </tr>
                    <tr>
                        <td>HRS Info:</td>
                        <td>{quotation.get('hrs_info', '')}</td>
                        <td>Resin Type:</td>
                        <td>{quotation.get('resin_type', '')}</td>
                    </tr>
                    <tr>
                        <td>Remark:</td>
                        <td>{quotation.get('remarks', '')}</td>
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
                        <td>Sol/Voltage:</td>
                        <td>{quotation.get('sol_voltage', '')}</td>
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
                        <td>15 working days after PO & drawing approval</td>
                        <td>Account:</td>
                        <td style="font-size: 9px;">700-038-038199 (Shinhan Bank Vietnam)</td>
                    </tr>
                </table>
            </div>
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

def render_quotation_table_with_status_control(quotations_df, update_func, save_func):
    """견적서 테이블 + 상태 변경 기능"""
    if quotations_df.empty:
        st.info("조건에 맞는 견적서가 없습니다.")
        return
    
    # 견적서 목록 표시
    for idx, row in quotations_df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2.5, 2.5, 2])
            
            with col1:
                st.markdown(f"**{row.get('quote_number', 'N/A')}**")
                st.caption(f"Rev: {row.get('revision_number', 'Rv00')}")
                st.caption(f"견적일: {row.get('quote_date', 'N/A')}")
            
            with col2:
                st.write(f"**{row.get('customer_company', 'N/A')}**")
                st.caption(f"담당: {row.get('employee_name', 'N/A')}")
            
            with col3:
                st.write(f"제품: {row.get('item_name_en', 'N/A')}")
                st.caption(f"수량: {row.get('quantity', 0):,}")
                final_amount = row.get('final_amount', 0)
                currency = row.get('currency', 'VND')
                st.write(f"💰 {final_amount:,.0f} {currency}")
            
            with col4:
                # 현재 상태 표시
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
                
                # 상태 변경 selectbox
                status_options = ['Draft', 'Sent', 'Approved', 'Rejected', 'Expired']
                current_index = status_options.index(status) if status in status_options else 0
                
                new_status = st.selectbox(
                    "상태",
                    status_options,
                    index=current_index,
                    key=f"status_select_{row.get('id')}_{idx}",
                    label_visibility="collapsed"
                )
                
                # 상태 변경 버튼
                if new_status != status:
                    if st.button("✅ 변경", key=f"update_status_{row.get('id')}_{idx}", use_container_width=True):
                        try:
                            update_data = {
                                'id': row.get('id'),
                                'status': new_status,
                                'updated_at': datetime.now().isoformat()
                            }
                            
                            success = update_func('quotations', update_data)
                            
                            if success:
                                st.success(f"✅ 상태가 {new_status}로 변경되었습니다.")
                                
                                # Approved 시 영업 프로세스 자동 생성
                                if new_status == 'Approved':
                                    process_result = create_sales_process_from_quotation(row, save_func)
                                    
                                    if process_result.get('success'):
                                        st.success("🚀 영업 프로세스가 자동 생성되었습니다!")
                                    else:
                                        st.warning(f"영업 프로세스 생성 실패: {process_result.get('message')}")
                                
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ 상태 변경 실패")
                        
                        except Exception as e:
                            st.error(f"❌ 오류: {str(e)}")
            
            # 상세 정보 (접기)
            with st.expander(f"상세 정보", expanded=False):
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.write(f"**프로젝트:** {row.get('project_name', 'N/A')}")
                    st.write(f"**부품명:** {row.get('part_name', 'N/A')}")
                    st.write(f"**금형번호:** {row.get('mold_number', 'N/A')}")
                    st.write(f"**수지:** {row.get('resin_type', 'N/A')}")
                
                with detail_col2:
                    st.write(f"**단가:** {row.get('unit_price_vnd', 0):,.0f} VND")
                    st.write(f"**할인율:** {row.get('discount_rate', 0):.1f}%")
                    st.write(f"**VAT:** {row.get('vat_rate', 0):.1f}%")
                    st.write(f"**유효기간:** {row.get('valid_until', 'N/A')}")
                
                if row.get('notes'):
                    st.write(f"**비고:** {row.get('notes')}")
            
            st.markdown("---")
    
    # 통계 정보
    if not quotations_df.empty:
        st.markdown("### 📊 견적서 통계")
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            total_amount = quotations_df['final_amount'].fillna(0).sum()
            st.metric("총 견적 금액", f"{total_amount:,.0f} VND")
        
        with stat_col2:
            approved_count = len(quotations_df[quotations_df['status'] == 'Approved'])
            st.metric("승인된 견적서", approved_count)
        
        with stat_col3:
            sent_count = len(quotations_df[quotations_df['status'] == 'Sent'])
            st.metric("발송된 견적서", sent_count)
        
        with stat_col4:
            approval_rate = (approved_count / len(quotations_df) * 100) if len(quotations_df) > 0 else 0
            st.metric("승인율", f"{approval_rate:.1f}%")


def create_sales_process_from_quotation(quotation_dict, save_func):
    """견적서 승인 시 영업 프로세스 자동 생성"""
    try:
        from datetime import datetime, timedelta
        
        # 프로세스 번호 생성
        today = datetime.now()
        process_number = f"SP-{today.strftime('%Y%m')}-{today.strftime('%d%H%M')}"
        
        # 영업 프로세스 데이터 구성
        process_data = {
            'process_number': process_number,
            'quotation_id': quotation_dict.get('id'),
            'customer_name': quotation_dict.get('customer_name', ''),
            'customer_company': quotation_dict.get('customer_company', ''),
            'customer_id': quotation_dict.get('customer_id'),
            'sales_rep_id': quotation_dict.get('sales_rep_id'),
            'process_status': 'approved',
            'item_description': quotation_dict.get('item_name_en', ''),
            'quantity': quotation_dict.get('quantity', 0),
            'unit_price': quotation_dict.get('unit_price_vnd', 0),
            'total_amount': quotation_dict.get('final_amount', 0),
            'currency': quotation_dict.get('currency', 'VND'),
            'expected_delivery_date': (datetime.now() + timedelta(days=30)).date().isoformat(),
            'project_name': quotation_dict.get('project_name'),
            'part_name': quotation_dict.get('part_name'),
            'mold_number': quotation_dict.get('mold_number'),
            'resin_type': quotation_dict.get('resin_type'),
            'notes': f"견적서 {quotation_dict.get('quote_number')}에서 전환",
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # DB 저장
        result = save_func('sales_process', process_data)
        
        if result:
            return {
                'success': True,
                'process_number': process_number,
                'message': 'Successfully created'
            }
        else:
            return {
                'success': False,
                'message': 'Database save failed'
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

def render_quotation_controls(load_func, update_func, delete_func, save_func, quotation_table, customer_table):
    """견적서 수정/삭제/인쇄/상태변경 통합 컨트롤"""
    st.markdown("---")
    
    col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1.5, 1])
    
    with col1:
        quotation_id_input = st.text_input("견적서 ID", placeholder="ID 입력", key="quotation_control_id")
    
    with col2:
        if st.button("✏️ 수정", use_container_width=True, type="primary", key="btn_edit_quot"):  # ✅ key 추가
            if quotation_id_input and quotation_id_input.strip().isdigit():
                quotation_id = int(quotation_id_input.strip())
                quotations = load_func(quotation_table) or []
                found = next((q for q in quotations if q.get('id') == quotation_id), None)
                
                if found:
                    st.session_state.editing_quotation_id = quotation_id
                    st.session_state.editing_quotation_data = found
                    st.rerun()
                else:
                    st.error(f"❌ ID {quotation_id}를 찾을 수 없습니다.")
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    with col3:
        if st.button("🗑️ 삭제", use_container_width=True, key="btn_delete_quot"):  # ✅ key 추가
            if quotation_id_input and quotation_id_input.strip().isdigit():
                st.session_state.deleting_quotation_id = int(quotation_id_input.strip())
                st.rerun()
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    with col4:
        if st.button("🖨️ 프린트", use_container_width=True, key="btn_print_quot"):  # ✅ key 추가
            if quotation_id_input and quotation_id_input.strip().isdigit():
                quotation_id = int(quotation_id_input.strip())
                quotations = load_func(quotation_table) or []
                found = next((q for q in quotations if q.get('id') == quotation_id), None)
                
                if found:
                    st.session_state['print_quotation'] = found
                    st.session_state['print_customer_table'] = customer_table
                    st.rerun()
                else:
                    st.error(f"❌ ID {quotation_id}를 찾을 수 없습니다.")
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    with col5:
        new_status = st.selectbox(
            "상태",
            ['Draft', 'Sent', 'Approved', 'Rejected', 'Expired'],
            key="status_control_select",
            label_visibility="collapsed"
        )
    
    with col6:
        if st.button("✅ 변경", use_container_width=True, key="btn_status_quot"):  # ✅ key 추가
            if quotation_id_input and quotation_id_input.strip().isdigit():
                quotation_id = int(quotation_id_input.strip())
                quotations = load_func(quotation_table) or []
                found = next((q for q in quotations if q.get('id') == quotation_id), None)
                
                if found:
                    update_data = {
                        'id': quotation_id,
                        'status': new_status,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    if update_func(quotation_table, update_data):
                        st.success(f"✅ 상태가 {new_status}로 변경되었습니다!")
                        
                        if new_status == 'Approved':
                            result = create_sales_process_from_quotation(found, save_func)
                            if result.get('success'):
                                st.success("🚀 영업 프로세스 생성!")
                        
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ 상태 변경 실패")
    
    # 삭제 확인
    if st.session_state.get('deleting_quotation_id'):
        st.warning(f"⚠️ ID {st.session_state.deleting_quotation_id} 견적서를 삭제하시겠습니까?")
        
        del_col1, del_col2, _ = st.columns([1, 1, 4])
        
        with del_col1:
            if st.button("✅ 예", key="confirm_del_quot"):
                if delete_func(quotation_table, st.session_state.deleting_quotation_id):
                    st.success("✅ 삭제 완료!")
                    st.session_state.pop('deleting_quotation_id', None)
                    st.rerun()
        
        with del_col2:
            if st.button("❌ 아니오", key="cancel_del_quot"):
                st.session_state.pop('deleting_quotation_id', None)
                st.rerun()


