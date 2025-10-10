import streamlit as st
import pandas as pd
from datetime import datetime

def show_product_code_management(load_func, save_func, update_func, delete_func):
    """제품 코드 간편 관리 - 핵심 정보만"""
    st.title("제품 코드 관리")
    
    st.info("💡 제품의 핵심 정보(코드, 이름, 가격)만 빠르게 관리합니다. 상세 정보는 '제품 관리' 메뉴를 이용하세요.")
    
    # 탭 구성
    tab1, tab2 = st.tabs(["제품 코드 목록", "신규 등록"])
    
    with tab1:
        render_product_code_list(load_func, update_func, delete_func)
    
    with tab2:
        render_product_code_registration(save_func, load_func)

def render_product_code_list(load_func, update_func, delete_func):
    """제품 코드 목록 - 테이블 형식"""
    st.header("제품 코드 목록")
    
    try:
        # 데이터 로드
        products_data = load_func('products')
        
        if not products_data:
            st.info("등록된 제품 코드가 없습니다.")
            return
        
        # DataFrame 변환
        products_df = pd.DataFrame(products_data)
        
        # 필요한 컬럼만 선택
        display_columns = [
            'id', 'product_code', 'product_name_en', 'product_name_vn',
            'cost_price_usd', 'selling_price_usd', 'unit_price_vnd', 'is_active'
        ]
        
        # 존재하는 컬럼만 필터링
        available_columns = [col for col in display_columns if col in products_df.columns]
        display_df = products_df[available_columns].copy()
        
        # 검색 기능
        search_term = st.text_input("🔍 검색 (제품코드/제품명)", key="code_search")
        
        if search_term:
            mask = (
                display_df['product_code'].astype(str).str.contains(search_term, case=False, na=False) |
                display_df['product_name_en'].astype(str).str.contains(search_term, case=False, na=False)
            )
            display_df = display_df[mask]
        
        st.write(f"총 {len(display_df)}개의 제품 코드")
        
        # 제품 코드 카드 형식으로 표시
        for idx, row in display_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{row['product_code']}**")
                    st.caption(f"{row['product_name_en']}")
                    if pd.notna(row.get('product_name_vn')) and row.get('product_name_vn'):
                        st.caption(f"🇻🇳 {row['product_name_vn']}")
                
                with col2:
                    cost_usd = row.get('cost_price_usd', 0)
                    st.write(f"💵 원가: ${cost_usd:,.2f}")
                
                with col3:
                    selling_usd = row.get('selling_price_usd', 0)
                    selling_vnd = row.get('unit_price_vnd', 0)
                    st.write(f"💰 판매가: ${selling_usd:,.2f}")
                    st.caption(f"{selling_vnd:,.0f} VND")
                
                with col4:
                    # 활성 상태
                    if row.get('is_active', True):
                        st.success("✅")
                    else:
                        st.error("❌")
                    
                    # 삭제 버튼
                    if st.button("🗑️", key=f"delete_product_{idx}", help="제품 코드 삭제"):
                        st.session_state[f'confirm_delete_product_{idx}'] = True
                    
                    # 삭제 확인
                    if st.session_state.get(f'confirm_delete_product_{idx}', False):
                        st.warning("삭제하시겠습니까?")
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("예", key=f"confirm_yes_product_{idx}"):
                                try:
                                    # products 테이블의 id 가져오기
                                    product_id = products_df[products_df['product_code'] == row['product_code']].iloc[0]['id']
                                    
                                    if delete_func('products', product_id):
                                        st.success("✅ 제품 코드가 삭제되었습니다!")
                                        st.session_state.pop(f'confirm_delete_product_{idx}', None)
                                        st.rerun()
                                    else:
                                        st.error("❌ 삭제 실패")
                                except Exception as e:
                                    st.error(f"삭제 오류: {str(e)}")
                        with col_no:
                            if st.button("아니오", key=f"confirm_no_product_{idx}"):
                                st.session_state.pop(f'confirm_delete_product_{idx}', None)
                                st.rerun()
                
                st.markdown("---")
        
        # 편집 영역
        st.markdown("---")
        st.subheader("제품 코드 편집")
        
        # 원본 데이터에서 선택
        product_options = [f"{row['product_code']} - {row['product_name_en']}" 
                          for _, row in products_df.iterrows()]
        
        if product_options:
            selected_product = st.selectbox("편집할 제품 선택", ["선택하세요..."] + product_options)
            
            if selected_product != "선택하세요...":
                product_code = selected_product.split(' - ')[0]
                selected_product_data = products_df[products_df['product_code'] == product_code].iloc[0]
                
                render_inline_edit_form(selected_product_data, update_func)
    
    except Exception as e:
        st.error(f"제품 코드 목록 로드 오류: {str(e)}")

def render_inline_edit_form(product_data, update_func):
    """인라인 편집 폼 - 등록 폼과 동일한 구조 (실시간 계산)"""
    st.markdown("### 제품 코드 편집")
    st.info(f"📝 편집 중: **{product_data['product_code']}**")
    
    # 기본 정보 (폼 밖에서 입력 - 실시간 계산을 위해)
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("제품 코드", value=product_data['product_code'], disabled=True, key=f"edit_code_{product_data['id']}")
        new_name_en = st.text_input(
            "제품명(영문) *", 
            value=product_data.get('product_name_en', ''),
            key=f"edit_name_en_{product_data['id']}"
        )
        new_name_vn = st.text_input(
            "제품명(베트남어)", 
            value=product_data.get('product_name_vn', '') or '',
            key=f"edit_name_vn_{product_data['id']}"
        )
    
    with col2:
        # 원가(USD)
        new_cost_usd = st.number_input(
            "원가(USD) *",
            min_value=0.0,
            value=float(product_data.get('cost_price_usd', 0)),
            step=0.01,
            format="%.2f",
            key=f"edit_cost_{product_data['id']}"
        )
        
        # 환율
        new_exchange_rate = st.number_input(
            "환율(USD→VND) *",
            min_value=1000.0,
            value=float(product_data.get('exchange_rate', 26387.45)),
            step=100.0,
            format="%.2f",
            key=f"edit_exchange_{product_data['id']}"
        )
        
        # 원가(VND) 자동 계산
        cost_price_vnd = new_cost_usd * new_exchange_rate
        st.info(f"💱 원가(VND): {cost_price_vnd:,.0f}")
    
    # 물류비 및 관리비
    st.markdown("---")
    col3, col4 = st.columns(2)
    
    with col3:
        # 물류비(USD)
        logistics_cost_usd = st.number_input(
            "물류비(USD)",
            min_value=0.0,
            value=float(product_data.get('logistics_cost_vnd', 0)) / new_exchange_rate if new_exchange_rate > 0 else 0.0,
            step=0.01,
            format="%.2f",
            key=f"edit_logistics_{product_data['id']}"
        )
        logistics_cost_vnd = logistics_cost_usd * new_exchange_rate
        st.info(f"💱 물류비(VND): {logistics_cost_vnd:,.0f}")
    
    with col4:
        # 관리비 적용 여부
        apply_admin_cost = st.checkbox(
            "관리비 적용 (원가 기준)",
            value=product_data.get('apply_admin_cost', True),
            key=f"edit_apply_admin_{product_data['id']}"
        )
        
        # 관리비율 및 관리비 계산
        if apply_admin_cost:
            admin_cost_rate = st.number_input(
                "관리비율 (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(product_data.get('admin_cost_rate', 20.0)),
                step=1.0,
                format="%.1f",
                key=f"edit_admin_rate_{product_data['id']}"
            )
            admin_cost_vnd = cost_price_vnd * (admin_cost_rate / 100)
        else:
            admin_cost_rate = 0.0
            admin_cost_vnd = 0.0
        
        st.info(f"💼 관리비(VND): {admin_cost_vnd:,.0f}")
    
    # 가격 계산 표시
    st.markdown("---")
    st.subheader("📊 가격 계산")
    
    col5, col6, col7 = st.columns(3)
    
    # 원가에 40% 마진 적용
    base_margin = cost_price_vnd * 0.40
    selling_price_base = cost_price_vnd + base_margin
    
    # 최종 판매가 (마진 포함된 원가 + 물류비 + 관리비)
    recommended_price_vnd = selling_price_base + logistics_cost_vnd + admin_cost_vnd
    
    with col5:
        st.metric("원가(VND)", f"{cost_price_vnd:,.0f}")
        st.caption(f"USD ${new_cost_usd:,.2f}")
    
    with col6:
        st.metric("기본 마진(40%)", f"{base_margin:,.0f}")
        st.caption("원가 × 0.40")
    
    with col7:
        st.metric("권장 판매가", f"{recommended_price_vnd:,.0f}")
        st.caption(f"+ 물류비 {logistics_cost_vnd:,.0f}")
        if admin_cost_vnd > 0:
            st.caption(f"+ 관리비 {admin_cost_vnd:,.0f}")
    
    # 실제 판매가 입력
    st.markdown("---")
    new_price_vnd = st.number_input(
        "실제 판매가(VND) *",
        min_value=0.0,
        value=float(product_data.get('unit_price_vnd', 0)),
        step=1000.0,
        format="%.0f",
        key=f"edit_selling_price_{product_data['id']}"
    )
    
    new_selling_usd = new_price_vnd / new_exchange_rate if new_exchange_rate > 0 else 0
    
    # 실제 마진 계산 (판매가 - 원가 - 물류비)
    actual_margin_vnd = new_price_vnd - cost_price_vnd - logistics_cost_vnd
    actual_margin_rate = (actual_margin_vnd / cost_price_vnd * 100) if cost_price_vnd > 0 else 0
    
    col8, col9, col10 = st.columns(3)
    
    with col8:
        st.metric("총 원가", f"{cost_price_vnd + logistics_cost_vnd:,.0f}")
        st.caption("원가 + 물류비")
    
    with col9:
        st.metric("실제 마진", f"{actual_margin_vnd:,.0f}")
        st.caption("판매가 - 원가 - 물류비")
    
    with col10:
        if actual_margin_rate >= 40:
            st.success(f"✅ 마진율: {actual_margin_rate:.1f}%")
        elif actual_margin_rate >= 0:
            st.warning(f"⚠️ 마진율: {actual_margin_rate:.1f}% (최소 40% 권장)")
        else:
            st.error(f"❌ 손실: {abs(actual_margin_rate):.1f}%")
    
    # 저장 버튼
    st.markdown("---")
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("💾 수정 저장", type="primary", use_container_width=True, key=f"save_edit_{product_data['id']}"):
            # 필수 필드 검증
            if not new_name_en.strip():
                st.error("제품명(영문)을 입력해주세요.")
                return
            
            if new_cost_usd <= 0:
                st.error("원가(USD)를 입력해주세요.")
                return
            
            if new_price_vnd <= 0:
                st.error("실제 판매가(VND)를 입력해주세요.")
                return
            
            # 업데이트 데이터 준비
            update_data = {
                'id': product_data['id'],
                'product_name': new_name_en,
                'product_name_en': new_name_en,
                'product_name_vn': new_name_vn if new_name_vn.strip() else None,
                
                # 가격 정보
                'cost_price_usd': new_cost_usd,
                'exchange_rate': new_exchange_rate,
                'logistics_cost_vnd': logistics_cost_vnd,
                'apply_admin_cost': apply_admin_cost,
                'admin_cost_rate': admin_cost_rate,
                'admin_cost_vnd': admin_cost_vnd,
                'unit_price_vnd': new_price_vnd,
                'selling_price_usd': new_selling_usd,
                'unit_price': new_selling_usd,
                
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                success = update_func('products', update_data)
                if success:
                    st.success("✅ 제품 코드가 수정되었습니다!")
                    st.balloons()
                    
                    with st.expander("📋 수정된 정보", expanded=True):
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.write(f"**제품 코드:** {product_data['product_code']}")
                            st.write(f"**제품명:** {new_name_en}")
                            st.write(f"**원가:** ${new_cost_usd:,.2f} (USD)")
                            st.write(f"**환율:** {new_exchange_rate:,.2f}")
                        
                        with col_b:
                            st.write(f"**판매가:** {new_price_vnd:,.0f} (VND)")
                            st.write(f"**물류비:** {logistics_cost_vnd:,.0f} (VND)")
                            st.write(f"**관리비:** {admin_cost_vnd:,.0f} (VND)")
                            st.write(f"**실제 마진:** {actual_margin_vnd:,.0f} (VND)")
                            st.write(f"**마진율:** {actual_margin_rate:.1f}%")
                    
                    st.rerun()
                else:
                    st.error("❌ 수정 실패")
            except Exception as e:
                st.error(f"수정 오류: {str(e)}")
    
    with col_cancel:
        if st.button("❌ 취소", use_container_width=True, key=f"cancel_edit_{product_data['id']}"):
            st.rerun()

def render_product_code_registration(save_func, load_func):
    """제품 코드 신규 등록 폼"""
    st.header("신규 제품 코드 등록")
    
    # 기본 정보 (폼 밖에서 입력 - 실시간 계산을 위해)
    col1, col2 = st.columns(2)
    
    with col1:
        product_code = st.text_input("제품 코드 *", placeholder="예: HR-01-02", key="pc_code")
        product_name_en = st.text_input("제품명(영문) *", placeholder="예: Hot Runner Timer", key="pc_name_en")
        product_name_vn = st.text_input("제품명(베트남어)", placeholder="예: Bộ đếm thời gian", key="pc_name_vn")
    
    with col2:
        # 원가(USD)
        cost_price_usd = st.number_input(
            "원가(USD) *",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.2f",
            key="pc_cost"
        )
        
        # 환율
        exchange_rate = st.number_input(
            "환율(USD→VND) *",
            min_value=1000.0,
            value=26387.45,
            step=100.0,
            format="%.2f",
            key="pc_exchange"
        )
        
        # 원가(VND) 자동 계산
        cost_price_vnd = cost_price_usd * exchange_rate
        st.info(f"💱 원가(VND): {cost_price_vnd:,.0f}")
    
    # 물류비 및 관리비
    st.markdown("---")
    col3, col4 = st.columns(2)
    
    with col3:
        # 물류비(USD)
        logistics_cost_usd = st.number_input(
            "물류비(USD)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.2f",
            key="pc_logistics"
        )
        logistics_cost_vnd = logistics_cost_usd * exchange_rate
        st.info(f"💱 물류비(VND): {logistics_cost_vnd:,.0f}")
    
    with col4:
        # 관리비 적용 여부
        apply_admin_cost = st.checkbox(
            "관리비 적용 (원가 기준)",
            value=True,
            key="pc_apply_admin"
        )
        
        # 관리비율 및 관리비 계산
        if apply_admin_cost:
            admin_cost_rate = st.number_input(
                "관리비율 (%)",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=1.0,
                format="%.1f",
                key="pc_admin_rate"
            )
            admin_cost_vnd = cost_price_vnd * (admin_cost_rate / 100)
        else:
            admin_cost_rate = 0.0
            admin_cost_vnd = 0.0
        
        st.info(f"💼 관리비(VND): {admin_cost_vnd:,.0f}")
    
    # 가격 계산 표시
    st.markdown("---")
    st.subheader("📊 가격 계산")
    
    col5, col6, col7 = st.columns(3)
    
    # 원가에 40% 마진 적용
    base_margin = cost_price_vnd * 0.40
    selling_price_base = cost_price_vnd + base_margin
    
    # 최종 판매가 (마진 포함된 원가 + 물류비 + 관리비)
    recommended_price_vnd = selling_price_base + logistics_cost_vnd + admin_cost_vnd
    
    with col5:
        st.metric("원가(VND)", f"{cost_price_vnd:,.0f}")
        st.caption(f"USD ${cost_price_usd:,.2f}")
    
    with col6:
        st.metric("기본 마진(40%)", f"{base_margin:,.0f}")
        st.caption("원가 × 0.40")
    
    with col7:
        st.metric("권장 판매가", f"{recommended_price_vnd:,.0f}")
        st.caption(f"+ 물류비 {logistics_cost_vnd:,.0f}")
        if admin_cost_vnd > 0:
            st.caption(f"+ 관리비 {admin_cost_vnd:,.0f}")
    
    # 실제 판매가 입력
    st.markdown("---")
    unit_price_vnd = st.number_input(
        "실제 판매가(VND) *",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        format="%.0f",
        key="pc_selling_price"
    )
    
    selling_price_usd = unit_price_vnd / exchange_rate if exchange_rate > 0 else 0
    
    # 실제 마진 계산 (판매가 - 원가 - 물류비)
    actual_margin_vnd = unit_price_vnd - cost_price_vnd - logistics_cost_vnd
    actual_margin_rate = (actual_margin_vnd / cost_price_vnd * 100) if cost_price_vnd > 0 else 0
    
    col8, col9, col10 = st.columns(3)
    
    with col8:
        st.metric("총 원가", f"{cost_price_vnd + logistics_cost_vnd:,.0f}")
        st.caption("원가 + 물류비")
    
    with col9:
        st.metric("실제 마진", f"{actual_margin_vnd:,.0f}")
        st.caption("판매가 - 원가 - 물류비")
    
    with col10:
        if actual_margin_rate >= 40:
            st.success(f"✅ 마진율: {actual_margin_rate:.1f}%")
        elif actual_margin_rate >= 0:
            st.warning(f"⚠️ 마진율: {actual_margin_rate:.1f}% (최소 40% 권장)")
        else:
            st.error(f"❌ 손실: {abs(actual_margin_rate):.1f}%")
    
    # 등록 버튼 (폼으로 감싸기)
    if st.button("💾 제품 코드 등록", type="primary", use_container_width=True):
        # 필수 필드 검증
        if not product_code.strip():
            st.error("제품 코드를 입력해주세요.")
            return
        
        if not product_name_en.strip():
            st.error("제품명(영문)을 입력해주세요.")
            return
        
        if cost_price_usd <= 0:
            st.error("원가(USD)를 입력해주세요.")
            return
        
        if unit_price_vnd <= 0:
            st.error("실제 판매가(VND)를 입력해주세요.")
            return
        
        # 중복 확인
        try:
            existing_products = load_func('products') or []
            existing_codes = [p.get('product_code', '') for p in existing_products]
            
            if product_code in existing_codes:
                st.error(f"제품 코드 '{product_code}'가 이미 존재합니다.")
                return
        except Exception as e:
            st.warning(f"중복 확인 오류: {str(e)}")
        
        # 데이터 준비
        product_data = {
            'product_code': product_code,
            'product_name': product_name_en,
            'product_name_en': product_name_en,
            'product_name_vn': product_name_vn if product_name_vn.strip() else None,
            
            # 가격 정보
            'cost_price_usd': cost_price_usd,
            'exchange_rate': exchange_rate,
            'logistics_cost_vnd': logistics_cost_vnd,
            'apply_admin_cost': apply_admin_cost,
            'admin_cost_rate': admin_cost_rate,
            'admin_cost_vnd': admin_cost_vnd,
            'unit_price_vnd': unit_price_vnd,
            'selling_price_usd': selling_price_usd,
            'unit_price': selling_price_usd,
            
            # 기본 정보
            'category': 'General',
            'unit': 'EA',
            'currency': 'USD',
            'is_active': True,
            'stock_quantity': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 저장
        try:
            if save_func('products', product_data):
                st.success("✅ 제품 코드가 등록되었습니다!")
                st.balloons()
                
                with st.expander("📋 등록된 정보", expanded=True):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**제품 코드:** {product_code}")
                        st.write(f"**제품명:** {product_name_en}")
                        st.write(f"**원가:** ${cost_price_usd:,.2f} (USD)")
                        st.write(f"**환율:** {exchange_rate:,.2f}")
                    
                    with col_b:
                        st.write(f"**판매가:** {unit_price_vnd:,.0f} (VND)")
                        st.write(f"**물류비:** {logistics_cost_vnd:,.0f} (VND)")
                        st.write(f"**관리비:** {admin_cost_vnd:,.0f} (VND)")
                        st.write(f"**실제 마진:** {actual_margin_vnd:,.0f} (VND)")
                        st.write(f"**마진율:** {actual_margin_rate:.1f}%")
                
                st.rerun()
            else:
                st.error("❌ 등록 실패")
        except Exception as e:
            st.error(f"저장 오류: {str(e)}")