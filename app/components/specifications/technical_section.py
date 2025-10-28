# app/components/specifications/technical_section.py

import streamlit as st
import pandas as pd
import json
from utils.language_config import get_label

def render_product_code_search(load_func, language='KO'):
    """제품 CODE 검색 UI - Code 1~7 검색 가능 (제품 관리와 동일한 방식)"""
    
    st.markdown("#### 🔍 제품 CODE 검색")
    
    # 제품 목록 조회
    products = load_func('products') if load_func else []
    
    if not products:
        st.warning("등록된 제품이 없습니다.")
        return None
    
    # Code 1~7 검색 옵션
    search_col1, search_col2 = st.columns([1, 3])
    
    with search_col1:
        code_number = st.selectbox(
            "Code 선택",
            ["전체", "1", "2", "3", "4", "5", "6", "7"],
            key="product_code_number_select"
        )
    
    with search_col2:
        search_term = st.text_input(
            "제품 CODE 또는 이름 검색",
            placeholder="예: HRS-YMO-ST-1-MCC-01-00",
            key="product_code_search"
        )
    
    # 검색 결과
    if search_term or code_number != "전체":
        filtered_products = products
        
        # Code 번호 필터
        if code_number != "전체":
            filtered_products = [
                p for p in filtered_products
                if f"-{code_number}-" in p.get('product_code', '')
            ]
        
        # 검색어 필터
        if search_term:
            filtered_products = [
                p for p in filtered_products 
                if (search_term.upper() in p.get('product_code', '').upper() or
                    search_term.lower() in p.get('product_name_en', '').lower() or
                    search_term.lower() in p.get('product_name_vn', '').lower())
            ]
        
        if filtered_products:
            st.markdown(f"**검색 결과: {len(filtered_products)}건**")
            
            # 테이블 형식으로 표시
            df_data = []
            for prod in filtered_products[:10]:  # 최대 10개
                df_data.append({
                    'ID': prod.get('id'),
                    'CODE': prod.get('product_code', 'N/A'),
                    '제품명 (EN)': prod.get('product_name_en', 'N/A'),
                    '제품명 (VN)': prod.get('product_name_vn', 'N/A')
                })
            
            df = pd.DataFrame(df_data)
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'ID': st.column_config.NumberColumn('ID', width='small'),
                    'CODE': st.column_config.TextColumn('CODE', width='medium'),
                    '제품명 (EN)': st.column_config.TextColumn('제품명 (EN)', width='medium'),
                    '제품명 (VN)': st.column_config.TextColumn('제품명 (VN)', width='medium')
                }
            )
            
            # 선택 입력
            selected_id = st.number_input(
                "선택할 제품 ID 입력",
                min_value=1,
                step=1,
                key="selected_product_id_input"
            )
            
            if st.button("✓ 선택", type="primary"):
                selected_product = next((p for p in filtered_products if p.get('id') == selected_id), None)
                if selected_product:
                    return selected_product.get('product_code', '')
                else:
                    st.error("❌ 해당 ID의 제품을 찾을 수 없습니다.")
        else:
            st.warning("검색 결과 없음")
    
    return None


def render_technical_section(load_func, language='KO'):
    """기술 사양 입력 섹션"""
    
    # BASE 정보
    st.markdown(f"### 🗂️ BASE 정보")
    
    with st.expander("BASE 치수", expanded=False):
        st.markdown(f"#### 치수 테이블")
        
        base_cols = st.columns(4)
        
        with base_cols[0]:
            st.markdown(f"**구분**")
            st.markdown("PLATE")
            st.markdown("TOP")
            st.markdown("SPACE")
            st.markdown("HOLDING")
        
        with base_cols[1]:
            st.markdown(f"**폭 (mm)**")
            plate_w = st.number_input("", min_value=0.0, step=0.1, key="plate_width", label_visibility="collapsed")
            top_w = st.number_input("", min_value=0.0, step=0.1, key="top_width", label_visibility="collapsed")
            space_w = st.number_input("", min_value=0.0, step=0.1, key="space_width", label_visibility="collapsed")
            holding_w = st.number_input("", min_value=0.0, step=0.1, key="holding_width", label_visibility="collapsed")
        
        with base_cols[2]:
            st.markdown(f"**길이 (mm)**")
            plate_l = st.number_input("", min_value=0.0, step=0.1, key="plate_length", label_visibility="collapsed")
            top_l = st.number_input("", min_value=0.0, step=0.1, key="top_length", label_visibility="collapsed")
            space_l = st.number_input("", min_value=0.0, step=0.1, key="space_length", label_visibility="collapsed")
            holding_l = st.number_input("", min_value=0.0, step=0.1, key="holding_length", label_visibility="collapsed")
        
        with base_cols[3]:
            st.markdown(f"**높이 (mm)**")
            plate_h = st.number_input("", min_value=0.0, step=0.1, key="plate_height", label_visibility="collapsed")
            top_h = st.number_input("", min_value=0.0, step=0.1, key="top_height", label_visibility="collapsed")
            space_h = st.number_input("", min_value=0.0, step=0.1, key="space_height", label_visibility="collapsed")
            holding_h = st.number_input("", min_value=0.0, step=0.1, key="holding_height", label_visibility="collapsed")
        
        base_processor = st.text_input("BASE 가공", key="base_processor")
        cooling_pt_tap = st.text_input("냉각 PT TAP", key="cooling_pt_tap")
    
    # NOZZLE
    st.markdown("---")
    st.markdown(f"### 🔩 노즐 사양")
    
    # 현재 모드 확인
    quotation_mode = st.session_state.get('quotation_mode', None)
    
    nozzle_code = ""
    
    # 모드 A: 견적서 연결 - 제품 CODE 자동 입력
    if quotation_mode == 'A':
        st.info("✅ 모드 A: 견적서에서 제품 CODE 자동 입력")
        nozzle_code = st.session_state.get('auto_product_code', '')
        
        st.text_input(
            "🔴 제품 CODE *",
            value=nozzle_code,
            key="nozzle_code_display",
            disabled=True,
            help="견적서에서 자동으로 가져온 제품 CODE입니다."
        )
    
    # 모드 B: 독립 작성 - 제품 CODE 검색 또는 수동 선택
    else:
        st.info("📝 모드 B: 제품 CODE를 검색하거나 직접 선택하세요")
        
        # 검색 UI
        searched_code = render_product_code_search(load_func, language)
        
        if searched_code:
            st.session_state['searched_product_code'] = searched_code
            st.success(f"✅ 선택된 CODE: {searched_code}")
        
        # 수동 선택 UI
        st.markdown("---")
        st.markdown("**또는 직접 선택:**")
        
        col_code1, col_code2 = st.columns(2)
        
        with col_code1:
            # CODE 선택 (1~7)
            product_code_select = st.selectbox(
                "제품 CODE (1~7)",
                ["1", "2", "3", "4", "5", "6", "7"],
                key="product_code_select"
            )
        
        with col_code2:
            # MCC CODE 선택 (01~04)
            mcc_code_select = st.selectbox(
                "MCC CODE (01~04)",
                ["01", "02", "03", "04"],
                key="mcc_code_select"
            )
        
        # 최종 CODE 결정
        if st.session_state.get('searched_product_code'):
            nozzle_code = st.session_state['searched_product_code']
        else:
            nozzle_code = f"HRS-YMO-ST-{product_code_select}-MCC-{mcc_code_select}-00"
        
        st.text_input(
            "🔴 제품 CODE *",
            value=nozzle_code,
            key="nozzle_code_final"
        )
    
    st.markdown("---")
    
    # HRS 시스템 타입 선택
    st.markdown("#### 🎯 HRS 시스템 타입")
    
    nozzle_col1, nozzle_col2 = st.columns(2)
    
    with nozzle_col1:
        # 타입 선택: Valve or Open
        hrs_system_type = st.radio(
            "🔴 시스템 타입 *",
            ["Valve", "Open"],
            horizontal=True,
            key="hrs_system_type",
            help="Valve: 게이트 타입 선택 가능 | Open: 게이트 선택 없음"
        )
        
        # Gate Type - Selectbox (드롭다운)
        if hrs_system_type == "Valve":
            gate_close = st.selectbox(
                "🔴 Gate Type *",
                ["STRAIGHT", "TAPER", "None"],
                index=0,
                key="gate_close_valve"
            )
        else:
            # Open 선택 시 비활성화
            gate_close = "None"
            st.selectbox(
                "Gate Type",
                ["STRAIGHT", "TAPER", "None"],
                index=2,
                key="gate_close_disabled",
                disabled=True
            )
            st.info("ℹ️ Open 타입은 게이트 선택이 없습니다.")
        
        # 노즐 수량 - 견적서에서 자동 입력
        quotation_mode = st.session_state.get('quotation_mode', None)
        auto_quantity = st.session_state.get('auto_quantity', 0)
        
        if quotation_mode == 'A' and auto_quantity > 0:
            nozzle_qty = st.number_input(
                f"🔴 수량 * (견적서 자동)",
                min_value=0,
                step=1,
                value=auto_quantity,
                key="nozzle_qty",
                help="견적서에서 자동으로 입력된 수량입니다."
            )
        else:
            nozzle_qty = st.number_input(
                f"🔴 수량 *",
                min_value=0,
                step=1,
                key="nozzle_qty"
            )
    
    with nozzle_col2:
        ht_type = st.radio(
            f"🔴 HT 타입 *",
            ["COIL", "ALLOY"],
            horizontal=True,
            key="ht_type"
        )
    
    # MANIFOLD
    st.markdown("---")
    st.markdown(f"### 🔀 MANIFOLD 사양")
    
    manifold_col1, manifold_col2 = st.columns(2)
    
    with manifold_col1:
        manifold_type = st.radio(
            f"🔴 MANIFOLD 타입 *",
            ["H", "I", "X", "T"],
            horizontal=True,
            key="manifold_type"
        )
    
    with manifold_col2:
        manifold_standard = st.radio(
            f"🔴 MANIFOLD 표준 *",
            ["ISO", "General"],
            index=1,  # General이 기본값
            horizontal=True,
            key="manifold_standard"
        )
    
    st.text_input(
        f"HT 타입 (고정)",
        value="SHEATH HEATER",
        disabled=True,
        key="manifold_ht_fixed"
    )
    
    # 센서 (실린더 & 센서 → 센서로 변경)
    st.markdown("---")
    st.markdown(f"### 🔧 센서")
    
    sensor_type = st.radio(
        f"🔴 센서 타입 *",
        ["J(I.C)", "K(C.A)"],
        horizontal=True,
        key="sensor_type"
    )
    
    # TIMER & CONNECTOR
    st.markdown("---")
    st.markdown(f"### 🔌 타이머 및 커넥터")
    
    timer_col1, timer_col2 = st.columns(2)
    
    with timer_col1:
        sol_volt = st.radio(
            f"🔴 솔레노이드 전압 *",
            ["AC220V", "DC24V"],
            horizontal=True,
            key="sol_volt"
        )
        
        sol_control = st.radio(
            f"🔴 솔레노이드 제어 *",
            ["개별", "통합"],
            horizontal=True,
            key="sol_control"
        )
    
    with timer_col2:
        timer_pin_type = st.radio(
            f"🔴 핀 타입 *",
            ["24PIN", "16PIN"],
            horizontal=True,
            key="timer_pin_type"
        )
        
        timer_buried = st.radio(
            f"🔴 매립 *",
            ["없음", "있음"],
            horizontal=True,
            key="timer_buried"
        )
    
    timer_location = st.selectbox(
        f"🔴 위치 *",
        ["G", "A", "B", "C", "D", "E", "F", "H", "I", "J", "K", "L", "UP"],
        key="timer_location"
    )
    
    # HEATER CONNECTOR
    st.markdown("---")
    st.markdown(f"### 🔥 히터 커넥터")
    
    heater_col1, heater_col2 = st.columns(2)
    
    with heater_col1:
        heater_pin_type = st.radio(
            f"🔴 핀 타입 *",
            ["24PIN", "16PIN"],
            horizontal=True,
            key="heater_pin_type"
        )
        
        con_type = st.radio(
            f"🔴 커넥터 타입 *",
            ["BOX", "HOUSING"],
            horizontal=True,
            key="con_type"
        )
    
    with heater_col2:
        heater_buried = st.radio(
            f"🔴 매립 *",
            ["없음", "있음"],
            horizontal=True,
            key="heater_buried"
        )
        
        heater_location = st.selectbox(
            f"🔴 위치 *",
            ["G", "A", "B", "C", "D", "E", "F", "H", "I", "J", "K", "L", "UP"],
            key="heater_location"
        )
    
    # ID CARD
    st.markdown("---")
    st.markdown(f"### 🆔 ID 카드")
    
    id_card_type = st.radio(
        f"🔴 ID 카드 타입 *",
        ["국내", "글로벌"],
        horizontal=True,
        key="id_card_type"
    )
    
    # NL 정보
    st.markdown("---")
    st.markdown(f"### 📏 NL 정보")
    
    nl_col1, nl_col2, nl_col3 = st.columns(3)
    
    with nl_col1:
        nl_phi = st.number_input("NL PHI", min_value=0.0, step=0.1, key="nl_phi")
    
    with nl_col2:
        nl_sr = st.number_input("NL SR", min_value=0.0, step=0.1, key="nl_sr")
    
    with nl_col3:
        locate_ring = st.text_input("LOCATE RING", key="locate_ring")
    
    # 데이터 수집
    technical_data = {
        'base_dimensions': {
            'plate': {'width': plate_w, 'length': plate_l, 'height': plate_h},
            'top': {'width': top_w, 'length': top_l, 'height': top_h},
            'space': {'width': space_w, 'length': space_l, 'height': space_h},
            'holding': {'width': holding_w, 'length': holding_l, 'height': holding_h}
        },
        'base_processor': base_processor,
        'cooling_pt_tap': cooling_pt_tap,
        'nozzle_specs': {
            'code': nozzle_code,
            'hrs_system_type': hrs_system_type,
            'gate_close': gate_close,
            'qty': nozzle_qty,
            'ht_type': ht_type
        },
        'manifold_type': manifold_type,
        'manifold_standard': manifold_standard,
        'sensor_type': sensor_type,
        'timer_connector': {
            'sol_volt': sol_volt,
            'sol_control': sol_control,
            'type': timer_pin_type,
            'buried': timer_buried == "있음",
            'location': timer_location
        },
        'heater_connector': {
            'type': heater_pin_type,
            'con_type': con_type,
            'buried': heater_buried == "있음",
            'location': heater_location
        },
        'id_card_type': id_card_type,
        'nl_phi': nl_phi,
        'nl_sr': nl_sr,
        'locate_ring': locate_ring
    }
    
    return technical_data
