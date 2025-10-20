"""
제품 관리 시스템 V5
- 제품 등록 (단일 + 일괄 통합)
- 테이블 뷰 목록
- CSV 관리
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def show_product_management(load_func, save_func, update_func, delete_func):
    """제품 관리 메인 페이지"""
    st.title("📦 제품 관리")
    
    # 탭 구성 (일괄 등록 제거)
    tab1, tab2, tab3 = st.tabs([
        "📝 제품 등록",
        "📋 제품 목록",
        "📤 CSV 관리"
    ])
    
    with tab1:
        render_product_form(save_func, load_func)
    
    with tab2:
        render_product_list_table_view(load_func, update_func, delete_func)
    
    with tab3:
        render_product_csv_management(load_func, save_func)


# ==========================================
# 제품 등록 (단일 + 일괄 통합)
# ==========================================

def render_product_form(save_func, load_func):
    """제품 등록 폼"""
    st.header("📝 제품 등록")
    
    # 일괄 등록 모드 체크
    if st.session_state.get('show_bulk_registration_form', False):
        render_bulk_registration_from_search(save_func, load_func)
        return
    
    if st.button("🔍 제품 코드 검색 (단계별 선택)", use_container_width=True, type="secondary"):
        st.session_state.show_code_search = not st.session_state.get('show_code_search', False)
    
    if st.session_state.get('show_code_search', False):
        render_cascading_code_search(load_func, save_func)
        return
    
    st.markdown("---")
    
    # 기본 단일 등록 폼
    with st.form("product_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 기본 정보")
            
            default_code = st.session_state.get('selected_product_code', '')
            
            product_code = st.text_input(
                "제품 코드 *",
                value=default_code,
                placeholder="예: HR-HRS-YMO-ST-20-MCC-xx-00"
            )
            
            product_name_en = st.text_input("제품명 (영문) *", placeholder="예: Hot Runner System")
            product_name_vn = st.text_input("제품명 (베트남어)", placeholder="예: Hệ thống Hot Runner")
            
            unit = st.selectbox("단위", ["EA", "Set", "Pcs", "Box", "Kg", "M", "L"], index=0)
        
        with col2:
            st.subheader("💰 가격 정보")
            
            currency = st.selectbox("기본 통화", ["USD", "VND", "KRW"], index=0)
            cost_price_usd = st.number_input("원가 (USD)", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            selling_price_usd = st.number_input("판매가 (USD)", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            exchange_rate = st.number_input("환율 (USD→VND)", min_value=1000.0, value=26387.45, step=100.0, format="%.2f")
            
            unit_price_vnd = selling_price_usd * exchange_rate
            st.metric("판매가 (VND)", f"{unit_price_vnd:,.0f}")
            
            if cost_price_usd > 0 and selling_price_usd > 0:
                margin = ((selling_price_usd - cost_price_usd) / selling_price_usd) * 100
                if margin >= 0:
                    st.success(f"📈 마진: {margin:.1f}%")
                else:
                    st.error(f"📉 손실: {abs(margin):.1f}%")
        
        st.subheader("📦 재고 및 추가 정보")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            stock_quantity = st.number_input("초기 재고", min_value=0, value=0, step=1)
        with col4:
            minimum_order_qty = st.number_input("최소 주문", min_value=1, value=1, step=1)
        with col5:
            lead_time_days = st.number_input("리드타임(일)", min_value=0, value=30, step=1)
        
        try:
            suppliers_data = load_func('suppliers') if load_func else []
            if suppliers_data:
                supplier_options = ["선택하지 않음"] + [s.get('company_name', 'N/A') for s in suppliers_data]
                supplier = st.selectbox("주 공급업체", supplier_options)
                if supplier == "선택하지 않음":
                    supplier = None
            else:
                supplier = None
        except:
            supplier = None
        
        description = st.text_area("제품 설명", placeholder="제품의 상세 설명")
        specifications = st.text_area("제품 사양", placeholder="기술적 사양이나 특징")
        
        submitted = st.form_submit_button("💾 제품 등록", type="primary", use_container_width=True)
        
        if submitted:
            if not product_code.strip():
                st.error("❌ 제품 코드를 입력해주세요.")
                return
            
            if not product_name_en.strip():
                st.error("❌ 제품명(영문)을 입력해주세요.")
                return
            
            try:
                existing_products = load_func('products') if load_func else []
                if existing_products:
                    existing_codes = [p.get('product_code', '') for p in existing_products]
                    if product_code in existing_codes:
                        st.error(f"❌ 제품 코드 '{product_code}'가 이미 존재합니다.")
                        return
            except Exception as e:
                st.warning(f"중복 확인 중 오류: {str(e)}")
            
            auto_category = st.session_state.get('selected_category', product_code.split('-')[0] if '-' in product_code else '')
            
            product_data = {
                'product_code': product_code.strip(),
                'product_name': product_name_en.strip(),
                'product_name_en': product_name_en.strip(),
                'product_name_vn': product_name_vn.strip() if product_name_vn.strip() else None,
                'category': auto_category,
                'unit': unit,
                'cost_price_usd': cost_price_usd,
                'selling_price_usd': selling_price_usd,
                'unit_price': selling_price_usd,
                'unit_price_vnd': unit_price_vnd,
                'currency': currency,
                'exchange_rate': exchange_rate,
                'supplier': supplier,
                'stock_quantity': stock_quantity,
                'minimum_order_qty': minimum_order_qty,
                'lead_time_days': lead_time_days,
                'description': description.strip() if description.strip() else None,
                'specifications': specifications.strip() if specifications.strip() else None,
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                if save_func('products', product_data):
                    st.success("✅ 제품이 성공적으로 등록되었습니다!")
                    st.balloons()
                    
                    if 'selected_product_code' in st.session_state:
                        del st.session_state['selected_product_code']
                    if 'selected_category' in st.session_state:
                        del st.session_state['selected_category']
                    if 'show_code_search' in st.session_state:
                        del st.session_state['show_code_search']
                    
                    st.rerun()
                else:
                    st.error("❌ 제품 등록에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 저장 중 오류: {str(e)}")


# ==========================================
# 코드 검색 (다단계) - 개선 버전
# ==========================================

def render_cascading_code_search(load_func, save_func):
    """다단계 연동 코드 검색 - 일괄 등록 통합"""
    st.subheader("🔍 제품 코드 검색")
    
    try:
        all_codes = load_func('product_codes') or []
        
        if not all_codes:
            st.warning("등록된 제품 코드가 없습니다.")
            return
        
        # Step 1: 코드 패턴 선택
        st.markdown("### Step 1: 코드 패턴 선택")
        st.caption("각 단계를 순서대로 선택하면 다음 단계 옵션이 자동 필터링됩니다.")
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        with col1:
            code01_options = get_unique_code_values(all_codes, 'code01')
            code01 = st.selectbox("Code01", ["선택"] + code01_options, key="sel_code01")
        
        with col2:
            if code01 != "선택":
                filtered = filter_codes_by_selections(all_codes, {'code01': code01})
                code02_options = get_unique_code_values(filtered, 'code02')
                code02 = st.selectbox("Code02", ["선택"] + code02_options, key="sel_code02")
            else:
                st.selectbox("Code02", ["선택"], disabled=True, key="sel_code02_dis")
                code02 = "선택"
        
        with col3:
            if code01 != "선택" and code02 != "선택":
                filtered = filter_codes_by_selections(all_codes, {'code01': code01, 'code02': code02})
                code03_options = get_unique_code_values(filtered, 'code03')
                code03 = st.selectbox("Code03", ["선택"] + code03_options, key="sel_code03")
            else:
                st.selectbox("Code03", ["선택"], disabled=True, key="sel_code03_dis")
                code03 = "선택"
        
        with col4:
            if code01 != "선택" and code02 != "선택" and code03 != "선택":
                filtered = filter_codes_by_selections(all_codes, {
                    'code01': code01, 'code02': code02, 'code03': code03
                })
                code04_options = get_unique_code_values(filtered, 'code04')
                code04 = st.selectbox("Code04", ["선택"] + code04_options, key="sel_code04")
            else:
                st.selectbox("Code04", ["선택"], disabled=True, key="sel_code04_dis")
                code04 = "선택"
        
        with col5:
            if code04 != "선택":
                filtered = filter_codes_by_selections(all_codes, {
                    'code01': code01, 'code02': code02, 'code03': code03, 'code04': code04
                })
                code05_options = get_unique_code_values(filtered, 'code05')
                code05 = st.selectbox("Code05", ["선택"] + code05_options, key="sel_code05")
            else:
                st.selectbox("Code05", ["선택"], disabled=True, key="sel_code05_dis")
                code05 = "선택"
        
        with col6:
            if code05 != "선택":
                filtered = filter_codes_by_selections(all_codes, {
                    'code01': code01, 'code02': code02, 'code03': code03,
                    'code04': code04, 'code05': code05
                })
                code06_options = get_unique_code_values(filtered, 'code06')
                code06 = st.selectbox("Code06", ["선택"] + code06_options, key="sel_code06")
            else:
                st.selectbox("Code06", ["선택"], disabled=True, key="sel_code06_dis")
                code06 = "선택"
        
        with col7:
            if code06 != "선택":
                filtered = filter_codes_by_selections(all_codes, {
                    'code01': code01, 'code02': code02, 'code03': code03,
                    'code04': code04, 'code05': code05, 'code06': code06
                })
                code07_options = get_unique_code_values(filtered, 'code07')
                code07 = st.selectbox("Code07", ["선택"] + code07_options, key="sel_code07")
            else:
                st.selectbox("Code07", ["선택"], disabled=True, key="sel_code07_dis")
                code07 = "선택"
        
        # 선택값 수집
        selections = {}
        if code01 != "선택":
            selections['code01'] = code01
        if code02 != "선택":
            selections['code02'] = code02
        if code03 != "선택":
            selections['code03'] = code03
        if code04 != "선택":
            selections['code04'] = code04
        if code05 != "선택":
            selections['code05'] = code05
        if code06 != "선택":
            selections['code06'] = code06
        if code07 != "선택":
            selections['code07'] = code07
        
        matching_codes = filter_codes_by_selections(all_codes, selections)
        
        if not selections:
            st.info("Code01부터 순서대로 선택하세요.")
            return
        
        if not matching_codes:
            st.warning("⚠️ 매칭되는 코드가 없습니다.")
            return
        
        # Step 2: 매칭 결과 확인
        st.markdown("---")
        st.markdown(f"### Step 2: 매칭 결과 확인 ({len(matching_codes)}개)")
        
        # Full Code 리스트 표시
        with st.container():
            st.caption("📋 검색된 코드 목록:")
            code_display = "\n".join([code.get('full_code', '') for code in matching_codes])
            st.text_area("", value=code_display, height=200, disabled=True, label_visibility="collapsed")
        
        st.markdown("---")
        
        # ID 선택 영역
        st.markdown("### 📋 ID 선택 (다중 선택 가능)")
        
        # 세션 상태 초기화
        if 'selected_code_ids_bulk' not in st.session_state:
            st.session_state.selected_code_ids_bulk = []
        
        # 전체 선택/해제
        col_all, _ = st.columns([1, 5])
        with col_all:
            select_all = st.checkbox("전체 선택", key="select_all_codes_bulk")
        
        if select_all:
            st.session_state.selected_code_ids_bulk = [c.get('id') for c in matching_codes]
        
        # ID 체크박스 (한 줄에 10개씩)
        ids_per_row = 10
        
        for i in range(0, len(matching_codes), ids_per_row):
            cols = st.columns(ids_per_row)
            for j in range(ids_per_row):
                idx = i + j
                if idx < len(matching_codes):
                    code = matching_codes[idx]
                    code_id = code.get('id')
                    with cols[j]:
                        is_checked = st.checkbox(
                            str(code_id),
                            value=code_id in st.session_state.selected_code_ids_bulk,
                            key=f"check_bulk_id_{code_id}"
                        )
                        
                        if is_checked and code_id not in st.session_state.selected_code_ids_bulk:
                            st.session_state.selected_code_ids_bulk.append(code_id)
                        elif not is_checked and code_id in st.session_state.selected_code_ids_bulk:
                            st.session_state.selected_code_ids_bulk.remove(code_id)
        
        st.markdown("---")
        
        # 선택된 코드 확인 및 다음 단계
        selected_count = len(st.session_state.selected_code_ids_bulk)
        
        if selected_count > 0:
            selected_ids_text = ", ".join([str(id) for id in sorted(st.session_state.selected_code_ids_bulk)])
            st.success(f"✅ {selected_count}개 선택됨 (ID: {selected_ids_text})")
            
            col_next, col_cancel = st.columns(2)
            
            with col_next:
                if st.button(f"➡️ 다음 단계: 공통 정보 입력", type="primary", use_container_width=True):
                    # 선택한 코드들을 세션에 저장
                    selected_codes = [c for c in matching_codes if c.get('id') in st.session_state.selected_code_ids_bulk]
                    st.session_state.bulk_registration_codes = selected_codes
                    st.session_state.show_code_search = False
                    st.session_state.show_bulk_registration_form = True
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ 취소", use_container_width=True):
                    st.session_state.selected_code_ids_bulk = []
                    st.session_state.show_code_search = False
                    st.rerun()
        else:
            st.info("ID를 선택하세요.")
    
    except Exception as e:
        st.error(f"❌ 코드 검색 중 오류: {str(e)}")


def get_unique_code_values(codes, level):
    """특정 레벨의 고유값 추출"""
    values = sorted(set([
        str(c.get(level, ''))
        for c in codes
        if c.get(level)
    ]))
    return values


def filter_codes_by_selections(codes, selections):
    """선택값으로 코드 필터링"""
    filtered = codes.copy()
    
    for level, value in selections.items():
        if value and value != "선택" and value != "전체":
            filtered = [c for c in filtered if str(c.get(level, '')) == value]
    
    return filtered


# ==========================================
# 일괄 등록 폼
# ==========================================

def render_bulk_registration_from_search(save_func, load_func):
    """선택한 코드들 일괄 등록"""
    st.header("📦 선택한 제품 일괄 등록")
    
    selected_codes = st.session_state.get('bulk_registration_codes', [])
    
    if not selected_codes:
        st.warning("선택된 코드가 없습니다.")
        if st.button("◀ 돌아가기"):
            st.session_state.show_bulk_registration_form = False
            st.rerun()
        return
    
    st.info(f"💡 {len(selected_codes)}개 제품의 공통 정보를 입력하세요.")
    
    # 선택된 코드 목록 표시
    with st.expander(f"📋 선택된 코드 목록 ({len(selected_codes)}개)", expanded=False):
        for code in selected_codes:
            st.code(code.get('full_code', ''), language=None)
    
    st.markdown("---")
    
    with st.form("bulk_from_search_form"):
        st.markdown("### 제품명 패턴")
        st.caption("💡 변수 사용: {code01}, {code02}, {code03}, {code04}, {code05}, {code06}, {code07}, {category}, {full_code}")
        
        col_name1, col_name2 = st.columns(2)
        
        with col_name1:
            name_pattern_en = st.text_input(
                "제품명 패턴 (영문) *",
                value="",
                placeholder=""
            )
        
        with col_name2:
            name_pattern_vn = st.text_input(
                "제품명 패턴 (베트남어)",
                value="Hệ thống {code04} {code05}",
                placeholder="예: Hệ thống {code04} {code05}"
            )
        
        st.markdown("### 가격 정보")
        col_price1, col_price2 = st.columns(2)
        
        with col_price1:
            bulk_cost_usd = st.number_input("원가 (USD)", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            bulk_selling_usd = st.number_input("판매가 (USD)", min_value=0.0, value=0.0, step=0.01, format="%.2f")
        
        with col_price2:
            bulk_exchange = st.number_input("환율", min_value=1000.0, value=26387.45, step=100.0, format="%.2f")
            bulk_price_vnd = bulk_selling_usd * bulk_exchange
            st.metric("판매가 (VND)", f"{bulk_price_vnd:,.0f}")
        
        st.markdown("### 재고 정보")
        col_stock1, col_stock2, col_stock3 = st.columns(3)
        
        with col_stock1:
            bulk_stock = st.number_input("재고", min_value=0, value=0, step=1)
        with col_stock2:
            bulk_min_order = st.number_input("최소 주문", min_value=1, value=1, step=1)
        with col_stock3:
            bulk_lead_time = st.number_input("리드타임(일)", min_value=0, value=30, step=1)
        
        st.markdown("---")
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button(
                f"💾 {len(selected_codes)}개 제품 일괄 등록",
                type="primary",
                use_container_width=True
            )
        
        with col_cancel:
            cancel = st.form_submit_button("❌ 취소", use_container_width=True)
        
        if cancel:
            st.session_state.show_bulk_registration_form = False
            st.session_state.bulk_registration_codes = []
            st.session_state.selected_code_ids_bulk = []
            st.rerun()
        
        if submitted:
            if not name_pattern_en.strip():
                st.error("❌ 제품명 패턴(영문)을 입력하세요.")
                return
            
            success_count = 0
            error_count = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, code in enumerate(selected_codes):
                try:
                    # 패턴 치환
                    product_name_en = apply_pattern(name_pattern_en, code)
                    product_name_vn = apply_pattern(name_pattern_vn, code) if name_pattern_vn.strip() else None
                    
                    product_data = {
                        'product_code': code.get('full_code'),
                        'product_name': product_name_en,
                        'product_name_en': product_name_en,
                        'product_name_vn': product_name_vn,
                        'category': code.get('category'),
                        'unit': 'EA',
                        'cost_price_usd': bulk_cost_usd,
                        'selling_price_usd': bulk_selling_usd,
                        'unit_price': bulk_selling_usd,
                        'unit_price_vnd': bulk_price_vnd,
                        'currency': 'USD',
                        'exchange_rate': bulk_exchange,
                        'stock_quantity': bulk_stock,
                        'minimum_order_qty': bulk_min_order,
                        'lead_time_days': bulk_lead_time,
                        'is_active': True,
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    if save_func('products', product_data):
                        success_count += 1
                    else:
                        error_count += 1
                    
                    progress = (idx + 1) / len(selected_codes)
                    progress_bar.progress(progress)
                    status_text.text(f"처리 중... {idx + 1}/{len(selected_codes)}")
                
                except Exception as e:
                    error_count += 1
                    st.warning(f"코드 {code.get('full_code')} 처리 오류: {str(e)}")
            
            progress_bar.empty()
            status_text.empty()
            
            if success_count > 0:
                st.success(f"✅ {success_count}개 제품이 등록되었습니다!")
                if error_count > 0:
                    st.warning(f"⚠️ {error_count}개 제품 등록 실패")
                st.balloons()
                
                # 초기화
                st.session_state.show_bulk_registration_form = False
                st.session_state.bulk_registration_codes = []
                st.session_state.selected_code_ids_bulk = []
                st.rerun()
            else:
                st.error("❌ 모든 제품 등록에 실패했습니다.")


def apply_pattern(pattern, code):
    """패턴에 코드 값 치환"""
    result = pattern
    result = result.replace("{code01}", code.get('code01', '') or '')
    result = result.replace("{code02}", code.get('code02', '') or '')
    result = result.replace("{code03}", code.get('code03', '') or '')
    result = result.replace("{code04}", code.get('code04', '') or '')
    result = result.replace("{code05}", code.get('code05', '') or '')
    result = result.replace("{code06}", code.get('code06', '') or '')
    result = result.replace("{code07}", code.get('code07', '') or '')
    result = result.replace("{category}", code.get('category', '') or '')
    result = result.replace("{full_code}", code.get('full_code', '') or '')
    return result.strip()


# ==========================================
# 제품 목록 (테이블 뷰)
# ==========================================

def render_product_list_table_view(load_func, update_func, delete_func):
    """제품 목록 - 테이블 뷰"""
    st.header("📋 제품 목록")
    
    try:
        products = load_func('products') or []
        
        if not products:
            st.info("등록된 제품이 없습니다.")
            return
        
        if 'show_edit_form_product' not in st.session_state:
            st.session_state.show_edit_form_product = False
        if 'editing_product_id' not in st.session_state:
            st.session_state.editing_product_id = None
        
        render_search_filters_product(products)
        render_edit_delete_controls_product(load_func, update_func, delete_func)
        
        if st.session_state.show_edit_form_product and st.session_state.get('editing_product_data'):
            render_edit_form_expandable_product(update_func)
        
        filtered_products = get_filtered_products(products)
        render_product_table(filtered_products)
    
    except Exception as e:
        st.error(f"❌ 제품 목록 로드 중 오류: {str(e)}")


def render_search_filters_product(products):
    """검색 필터"""
    col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
    
    with col1:
        st.text_input("🔍 검색", placeholder="제품코드/제품명", key="product_search_term")
    
    with col2:
        categories = sorted(list(set([p.get('category', '') for p in products if p.get('category')])))
        st.selectbox("카테고리", ["전체"] + categories, key="product_selected_category")
    
    with col3:
        st.selectbox("상태", ["전체", "활성", "비활성"], key="product_status_filter")
    
    with col4:
        st.write("")
        st.write("")
        if st.button("📥 CSV", use_container_width=True):
            csv_data = generate_products_csv(products)
            st.download_button("다운로드", csv_data, f"products_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")


def render_edit_delete_controls_product(load_func, update_func, delete_func):
    """수정/삭제 컨트롤"""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
    
    with col1:
        product_id_input = st.text_input("수정/삭제할 제품 ID", placeholder="제품 ID 입력", key="product_id_input")
    
    with col2:
        if st.button("✏️ 수정", use_container_width=True, type="primary"):
            if product_id_input and product_id_input.strip().isdigit():
                product_id = int(product_id_input.strip())
                products = load_func('products') or []
                found = next((p for p in products if p.get('id') == product_id), None)
                
                if found:
                    st.session_state.editing_product_id = product_id
                    st.session_state.show_edit_form_product = True
                    st.session_state.editing_product_data = found
                    st.rerun()
                else:
                    st.error(f"❌ ID {product_id}를 찾을 수 없습니다.")
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    with col3:
        if st.button("🗑️ 삭제", use_container_width=True):
            if product_id_input and product_id_input.strip().isdigit():
                st.session_state.deleting_product_id = int(product_id_input.strip())
                st.rerun()
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    if st.session_state.get('deleting_product_id'):
        st.warning(f"⚠️ ID {st.session_state.deleting_product_id} 제품을 삭제하시겠습니까?")
        
        del_col1, del_col2, _ = st.columns([1, 1, 4])
        
        with del_col1:
            if st.button("✅ 예", key="confirm_del_prod"):
                if delete_func('products', st.session_state.deleting_product_id):
                    st.success("✅ 삭제 완료!")
                    st.session_state.pop('deleting_product_id', None)
                    st.rerun()
        
        with del_col2:
            if st.button("❌ 아니오", key="cancel_del_prod"):
                st.session_state.pop('deleting_product_id', None)
                st.rerun()
    
    st.markdown("---")


def render_edit_form_expandable_product(update_func):
    """제품 수정 폼"""
    product = st.session_state.editing_product_data
    product_id = product.get('id')
    
    with st.expander(f"▼ 제품 수정 (ID: {product_id})", expanded=True):
        with st.form(f"edit_prod_{product_id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("제품 코드", value=product.get('product_code', ''), disabled=True)
                new_name_en = st.text_input("제품명(EN)", value=product.get('product_name_en', ''))
                new_name_vn = st.text_input("제품명(VN)", value=product.get('product_name_vn', '') or '')
            
            with col2:
                new_cost = st.number_input("원가(USD)", value=float(product.get('cost_price_usd', 0)), step=0.01)
                new_selling = st.number_input("판매가(USD)", value=float(product.get('selling_price_usd', 0)), step=0.01)
                new_exchange = st.number_input("환율", value=float(product.get('exchange_rate', 26387.45)), step=100.0)
                new_stock = st.number_input("재고", value=int(product.get('stock_quantity', 0)), step=1)
                new_active = st.checkbox("활성", value=product.get('is_active', True))
            
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                save_btn = st.form_submit_button("💾 저장", type="primary", use_container_width=True)
            
            with col_cancel:
                cancel_btn = st.form_submit_button("❌ 취소", use_container_width=True)
            
            if save_btn:
                if not new_name_en.strip():
                    st.error("제품명(영문) 필수")
                    return
                
                update_data = {
                    'id': product_id,
                    'product_name': new_name_en.strip(),
                    'product_name_en': new_name_en.strip(),
                    'product_name_vn': new_name_vn.strip() or None,
                    'cost_price_usd': new_cost,
                    'selling_price_usd': new_selling,
                    'unit_price': new_selling,
                    'unit_price_vnd': new_selling * new_exchange,
                    'exchange_rate': new_exchange,
                    'stock_quantity': new_stock,
                    'is_active': new_active,
                    'updated_at': datetime.now().isoformat()
                }
                
                if update_func('products', update_data):
                    st.success("✅ 수정 완료!")
                    st.session_state.show_edit_form_product = False
                    st.session_state.editing_product_id = None
                    st.session_state.pop('editing_product_data', None)
                    st.rerun()
                else:
                    st.error("❌ 수정 실패")
            
            if cancel_btn:
                st.session_state.show_edit_form_product = False
                st.session_state.editing_product_id = None
                st.session_state.pop('editing_product_data', None)
                st.rerun()


def get_filtered_products(products):
    """필터 적용"""
    filtered = products.copy()
    
    search_term = st.session_state.get('product_search_term', '')
    if search_term:
        filtered = [
            p for p in filtered
            if search_term.lower() in str(p.get('product_code', '')).lower()
            or search_term.lower() in str(p.get('product_name_en', '')).lower()
        ]
    
    category = st.session_state.get('product_selected_category', '전체')
    if category != '전체':
        filtered = [p for p in filtered if p.get('category') == category]
    
    status = st.session_state.get('product_status_filter', '전체')
    if status == "활성":
        filtered = [p for p in filtered if p.get('is_active')]
    elif status == "비활성":
        filtered = [p for p in filtered if not p.get('is_active')]
    
    return sorted(filtered, key=lambda x: x.get('id', 0))


def render_product_table(products):
    """제품 테이블"""
    if not products:
        st.info("조건에 맞는 제품이 없습니다.")
        return
    
    table_data = []
    for p in products:
        table_data.append({
            'ID': p.get('id', ''),
            'Code': p.get('product_code', ''),
            'Name(EN)': p.get('product_name_en', ''),
            'Name(VN)': p.get('product_name_vn', ''),
            'Category': p.get('category', ''),
            'Cost': f"${p.get('cost_price_usd', 0):,.2f}",
            'Price': f"${p.get('selling_price_usd', 0):,.2f}",
            'VND': f"{p.get('unit_price_vnd', 0):,.0f}",
            'Stock': p.get('stock_quantity', 0),
            'Active': '✅' if p.get('is_active') else '❌'
        })
    
    df = pd.DataFrame(table_data)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"📊 총 **{len(products)}개** 제품")


# ==========================================
# CSV 관리
# ==========================================

def render_product_csv_management(load_func, save_func):
    """CSV 관리"""
    st.header("📤 제품 CSV 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 CSV 다운로드")
        if st.button("CSV 다운로드", type="primary"):
            products = load_func('products') or []
            if products:
                csv_data = generate_products_csv(products)
                st.download_button("다운로드", csv_data, f"products_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
            else:
                st.warning("데이터 없음")
    
    with col2:
        st.subheader("📤 CSV 업로드")
        st.info("추후 구현 예정")


def generate_products_csv(products):
    """CSV 생성"""
    csv_data = []
    for p in products:
        csv_data.append({
            'id': p.get('id', ''),
            'product_code': p.get('product_code', ''),
            'product_name_en': p.get('product_name_en', ''),
            'category': p.get('category', ''),
            'cost_price_usd': p.get('cost_price_usd', 0),
            'selling_price_usd': p.get('selling_price_usd', 0),
            'stock': p.get('stock_quantity', 0)
        })
    
    df = pd.DataFrame(csv_data)
    return df.to_csv(index=False, encoding='utf-8-sig')