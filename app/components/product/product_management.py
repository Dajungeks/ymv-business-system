import streamlit as st
import pandas as pd
from datetime import datetime
import logging

def show_product_management(load_func, save_func, update_func, delete_func):
    """제품 관리 메인 페이지"""
    st.title("제품 관리")
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["제품 등록", "제품 목록", "CSV 관리"])
    
    with tab1:
        render_product_form(save_func, load_func)
    
    with tab2:
        render_product_list(load_func, update_func, delete_func)
    
    with tab3:
        render_product_csv_management(load_func, save_func)

def render_product_form(save_func, load_func):
    """제품 등록 폼"""
    st.header("새 제품 등록")
    
    with st.form("product_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("기본 정보")
            product_code = st.text_input("제품 코드 *", placeholder="예: HR-01-02-ST-KR-00")
            product_name_en = st.text_input("제품명 (영문) *", placeholder="예: Hot Runner Timer")
            product_name_vn = st.text_input("제품명 (베트남어)", placeholder="예: Bộ đếm thời gian Hot Runner")
            
            # 제품 카테고리 - 기존 데이터에서 동적 로드
            category_options = ["Hot Runner System", "Temperature Controller", "Sequence Timer", "기타"]
            
            # 기존 제품에서 카테고리 추가 로드
            try:
                existing_products = load_func('products') if load_func else []
                if existing_products:
                    for product in existing_products:
                        cat = product.get('category', '')
                        if cat and cat not in category_options:
                            category_options.insert(-1, cat)  # "기타" 전에 삽입
            except:
                pass
            
            category = st.selectbox("제품 카테고리", category_options, index=0)
            
            # "기타" 선택시 직접 입력
            if category == "기타":
                category = st.text_input("카테고리 직접 입력", placeholder="새 카테고리명")
        
        with col2:
            st.subheader("가격 정보")
            
            # 통화 선택
            currency = st.selectbox("기본 통화", ["USD", "VND", "KRW"], index=0)
            
            # 가격 입력 - 실제 DB 컬럼명 사용
            cost_price_usd = st.number_input(
                "원가 (USD)", 
                min_value=0.0, 
                value=0.0, 
                step=0.01,
                key="product_cost_price_usd"
            )
            
            selling_price_usd = st.number_input(
                "판매가 (USD)", 
                min_value=0.0, 
                value=0.0, 
                step=0.01,
                key="product_selling_price_usd"
            )
            
            unit_price_vnd = st.number_input(
                "판매가 (VND)", 
                min_value=0, 
                value=0, 
                step=1000,
                key="product_unit_price_vnd"
            )
            
            # 마진 계산 및 표시
            if cost_price_usd > 0 and selling_price_usd > 0:
                margin = ((selling_price_usd - cost_price_usd) / selling_price_usd) * 100
                if margin >= 0:
                    st.success(f"마진: {margin:.1f}%")
                else:
                    st.error(f"손실: {abs(margin):.1f}%")
            
            # 기타 정보
            unit = st.selectbox("단위", ["EA", "Set", "Pcs", "Box", "Kg", "M", "L"], index=0)
            
            # 재고 관리
            st.subheader("재고 정보")
            initial_stock = st.number_input(
                "초기 재고", 
                min_value=0, 
                value=0, 
                step=1,
                key="product_initial_stock"
            )
            min_stock = st.number_input(
                "최소 재고", 
                min_value=0, 
                value=0, 
                step=1,
                key="product_min_stock"
            )
        
        # 추가 정보
        st.subheader("추가 정보")
        col3, col4 = st.columns(2)
        
        with col3:
            # 공급업체 정보
            suppliers_data = load_func('suppliers') if load_func else []
            if suppliers_data:
                suppliers_df = pd.DataFrame(suppliers_data)
                supplier_options = ["선택하지 않음"] + [f"{row['company_name']} ({row['id']})" for _, row in suppliers_df.iterrows()]
                selected_supplier = st.selectbox("주 공급업체", supplier_options)
                
                if selected_supplier != "선택하지 않음":
                    supplier_id = int(selected_supplier.split('(')[-1].split(')')[0])
                else:
                    supplier_id = None
            else:
                supplier_id = None
                st.info("등록된 공급업체가 없습니다.")
        
        with col4:
            # 상태
            status = st.selectbox("상태", ["Active", "Inactive", "Discontinued"], index=0)
        
        # 설명
        description = st.text_area("제품 설명", placeholder="제품의 상세 설명을 입력하세요")
        specifications = st.text_area("제품 사양", placeholder="기술적 사양이나 특징을 입력하세요")
        
        # 저장 버튼 (필수)
        submitted = st.form_submit_button("제품 등록", type="primary", use_container_width=True)
        
        if submitted:
            # 필수 필드 검증
            if not product_code.strip():
                st.error("제품 코드를 입력해주세요.")
                return
            
            if not product_name_en.strip():
                st.error("제품명(영문)을 입력해주세요.")
                return
            
            # 중복 확인
            try:
                existing_products = load_func('products') if load_func else []
                if existing_products:
                    existing_codes = [p.get('product_code', '') for p in existing_products]
                    if product_code in existing_codes:
                        st.error(f"제품 코드 '{product_code}'가 이미 존재합니다.")
                        return
            except Exception as e:
                st.warning(f"중복 확인 중 오류: {str(e)}")
            
            # 제품 데이터 준비 (실제 DB 스키마에 맞춤)
            product_data = {
                'product_code': product_code,
                'product_name': product_name_en,  # 기본 제품명
                'product_name_en': product_name_en,
                'product_name_vn': product_name_vn if product_name_vn.strip() else None,
                'category': category,
                'unit': unit,
                'cost_price_usd': cost_price_usd,
                'selling_price_usd': selling_price_usd,
                'unit_price': selling_price_usd,  # 호환성용
                'unit_price_vnd': unit_price_vnd,
                'currency': currency,
                'supplier': selected_supplier if selected_supplier != "선택하지 않음" else None,
                'description': description if description.strip() else None,
                'specifications': specifications if specifications.strip() else None,
                'is_active': status == "Active",
                'stock_quantity': initial_stock,
                'minimum_order_qty': 1,
                'lead_time_days': 30,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # 저장 실행
            try:
                if save_func('products', product_data):
                    st.success("제품이 성공적으로 등록되었습니다!")
                    st.balloons()
                    
                    # 등록된 제품 정보 요약
                    with st.expander("등록된 제품 정보", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**제품 코드:** {product_code}")
                            st.write(f"**제품명:** {product_name_en}")
                            st.write(f"**카테고리:** {category}")
                        with col2:
                            st.write(f"**가격:** {unit_price:,.2f} {currency}")
                            st.write(f"**상태:** {status}")
                            if cost_price > 0 and unit_price > 0:
                                margin = ((unit_price - cost_price) / unit_price) * 100
                                st.write(f"**마진:** {margin:.1f}%")
                    
                    st.rerun()
                else:
                    st.error("제품 등록에 실패했습니다.")
            except Exception as e:
                st.error(f"저장 중 오류가 발생했습니다: {str(e)}")

def render_product_list(load_func, update_func, delete_func):
    """제품 목록"""
    st.header("제품 목록")
    
    try:
        # 데이터 로드
        products_data = load_func('products')
        
        if not products_data:
            st.info("등록된 제품이 없습니다.")
            return
        
        # DataFrame 변환
        products_df = pd.DataFrame(products_data)
        
        # 검색 및 필터
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("검색 (제품코드/제품명)", key="product_search")
        
        with col2:
            if 'category' in products_df.columns:
                categories = ['전체'] + sorted(products_df['category'].dropna().unique().tolist())
                selected_category = st.selectbox("카테고리 필터", categories)
            else:
                selected_category = '전체'
        
        with col3:
            status_filter = st.selectbox("상태 필터", ['전체', 'Active', 'Inactive', 'Discontinued'])
        
        # 필터링 적용
        filtered_df = products_df.copy()
        
        # 검색어 필터
        if search_term:
            mask = (
                filtered_df.get('product_code', pd.Series()).astype(str).str.contains(search_term, case=False, na=False) |
                filtered_df.get('product_name_en', pd.Series()).astype(str).str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # 카테고리 필터
        if selected_category != '전체' and 'category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        
        # 상태 필터
        if status_filter != '전체' and 'status' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        st.write(f"총 {len(filtered_df)}개의 제품")
        
        # 제품 목록 표시
        for idx, product in filtered_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{product.get('product_code', 'N/A')}**")
                    st.write(product.get('product_name_en', 'N/A'))
                    if product.get('product_name_vn'):
                        st.caption(product['product_name_vn'])
                
                with col2:
                    category = product.get('category', 'N/A')
                    st.write(f"카테고리: {category}")
                    st.caption(f"단위: {product.get('unit', 'EA')}")
                
                with col3:
                    currency = product.get('currency', 'USD')
                    selling_price_usd = product.get('selling_price_usd', 0)
                    unit_price_vnd = product.get('unit_price_vnd', 0)
                    cost_price_usd = product.get('cost_price_usd', 0)
                    
                    st.write(f"USD: ${selling_price_usd:,.2f}")
                    st.write(f"VND: {unit_price_vnd:,.0f}")
                    st.caption(f"원가: ${cost_price_usd:,.2f}")
                    
                    if cost_price_usd > 0 and selling_price_usd > 0:
                        margin = ((selling_price_usd - cost_price_usd) / selling_price_usd) * 100
                        st.caption(f"마진: {margin:.1f}%")
                    
                    # 재고 정보
                    stock = product.get('stock_quantity', 0)
                    st.info(f"재고: {stock}")
                
                with col4:
                    status = product.get('status', 'Active')
                    status_colors = {
                        "Active": "#28a745",
                        "Inactive": "#6c757d", 
                        "Discontinued": "#dc3545"
                    }
                    color = status_colors.get(status, "#28a745")
                    st.markdown(f"<span style='color: {color}'>● {status}</span>", 
                               unsafe_allow_html=True)
                    
                    # 편집 버튼
                    product_id = product.get('id', f"temp_{idx}")
                    
                    if st.button("편집", key=f"edit_btn_{product_id}"):
                        st.session_state[f"edit_product_{product_id}"] = True
                        st.rerun()
                
                # 편집 폼 (조건부 표시)
                if st.session_state.get(f"edit_product_{product_id}", False):
                    with st.expander("제품 편집", expanded=True):
                        render_simple_edit_form(product, update_func, product_id)
                
                st.markdown("---")
        
        # 통계 정보
        if not filtered_df.empty:
            st.markdown("---")
            st.subheader("제품 통계")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 제품 수", len(filtered_df))
            
            with col2:
                if 'status' in filtered_df.columns:
                    active_count = len(filtered_df[filtered_df['status'] == 'Active'])
                else:
                    active_count = 0
                st.metric("활성 제품", active_count)
            
            with col3:
                if 'category' in filtered_df.columns:
                    unique_categories = filtered_df['category'].nunique()
                    st.metric("카테고리 수", unique_categories)
                else:
                    st.metric("카테고리 수", "N/A")
            
            with col4:
                # 평균 가격 계산
                if 'unit_price' in filtered_df.columns:
                    avg_price = filtered_df['unit_price'].mean()
                    currency = filtered_df['currency'].iloc[0] if 'currency' in filtered_df.columns else 'USD'
                    st.metric("평균 가격", f"{avg_price:,.0f} {currency}")
                else:
                    st.metric("평균 가격", "N/A")
    
    except Exception as e:
        st.error(f"제품 목록을 로드하는 중 오류가 발생했습니다: {str(e)}")

def render_simple_edit_form(product, update_func, product_id):
    """간단한 제품 편집 폼"""
    with st.form(f"simple_edit_form_{product_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name_en = st.text_input("제품명 (영문)", value=product.get('product_name_en', ''))
            new_name_vn = st.text_input("제품명 (베트남어)", value=product.get('product_name_vn', '') or '')
            
            # 안전한 카테고리 선택
            category_options = ["Hot Runner System", "Temperature Controller", "Sequence Timer", "기타"]
            current_category = product.get('category', '')
            if current_category and current_category in category_options:
                cat_index = category_options.index(current_category)
            else:
                if current_category:
                    category_options.insert(-1, current_category)
                    cat_index = category_options.index(current_category)
                else:
                    cat_index = 0
            
            new_category = st.selectbox("카테고리", category_options, index=cat_index)
        
        with col2:
            new_cost_price_usd = st.number_input(
                "원가 (USD)", 
                value=float(product.get('cost_price_usd', 0)), 
                step=0.01,
                key=f"simple_cost_usd_{product_id}"
            )
            new_selling_price_usd = st.number_input(
                "판매가 (USD)", 
                value=float(product.get('selling_price_usd', 0)), 
                step=0.01,
                key=f"simple_selling_usd_{product_id}"
            )
            
            status_options = ["Active", "Inactive", "Discontinued"]
            current_status = "Active" if product.get('is_active', True) else "Inactive"
            if current_status in status_options:
                status_index = status_options.index(current_status)
            else:
                status_index = 0
            
            new_status = st.selectbox("상태", status_options, index=status_index)
        
        # 버튼
        col_save, col_cancel = st.columns(2)
        with col_save:
            save_changes = st.form_submit_button("저장", type="primary")
        with col_cancel:
            cancel_edit = st.form_submit_button("취소")
        
        if cancel_edit:
            edit_key = f"edit_product_{product_id}"
            if edit_key in st.session_state:
                del st.session_state[edit_key]
            st.rerun()
        
        if save_changes:
            # 업데이트 데이터 준비 (실제 DB 컬럼명 사용)
            update_data = {
                'id': product_id,
                'product_name_en': new_name_en,
                'product_name_vn': new_name_vn if new_name_vn.strip() else None,
                'category': new_category,
                'cost_price_usd': new_cost_price_usd,
                'selling_price_usd': new_selling_price_usd,
                'unit_price': new_selling_price_usd,  # 호환성용
                'is_active': new_status == "Active",
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                # database.py의 update_data 함수 호출 (table, data 순서)
                success = update_func('products', update_data)
                
                if success:
                    st.success("제품 정보가 수정되었습니다!")
                    edit_key = f"edit_product_{product_id}"
                    if edit_key in st.session_state:
                        del st.session_state[edit_key]
                    st.rerun()
                else:
                    st.error("수정에 실패했습니다.")
            
            except Exception as e:
                st.error(f"수정 중 오류: {str(e)}")

def render_product_csv_management(load_func, save_func):
    """제품 CSV 관리"""
    st.header("제품 CSV 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CSV 다운로드")
        
        if st.button("제품 목록 CSV 다운로드", type="primary"):
            try:
                products_data = load_func('products')
                
                if not products_data:
                    st.warning("다운로드할 제품 데이터가 없습니다.")
                    return
                
                products_df = pd.DataFrame(products_data)
                
                # CSV 생성
                csv_data = products_df.to_csv(index=False, encoding='utf-8')
                
                st.download_button(
                    label="CSV 파일 다운로드",
                    data=csv_data,
                    file_name=f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.success(f"총 {len(products_df)}개의 제품 데이터 준비 완료")
                
            except Exception as e:
                st.error(f"CSV 생성 중 오류: {str(e)}")
    
    with col2:
        st.subheader("CSV 업로드")
        st.info("CSV 업로드 기능은 추후 구현 예정입니다.")