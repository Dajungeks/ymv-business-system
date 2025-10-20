# app/components/specifications/technical_section.py

import streamlit as st
import json

def render_technical_section():
    """기술 사양 입력 섹션"""
    
    # BASE 정보
    st.markdown("### 📏 BASE Information")
    
    with st.expander("BASE Dimensions", expanded=False):
        st.markdown("#### Dimensions Table")
        
        base_cols = st.columns(4)
        
        with base_cols[0]:
            st.markdown("**Part**")
            st.markdown("PLATE")
            st.markdown("TOP")
            st.markdown("SPACE")
            st.markdown("HOLDING")
        
        with base_cols[1]:
            st.markdown("**Width (mm)**")
            plate_w = st.number_input("", min_value=0.0, step=0.1, key="plate_width", label_visibility="collapsed")
            top_w = st.number_input("", min_value=0.0, step=0.1, key="top_width", label_visibility="collapsed")
            space_w = st.number_input("", min_value=0.0, step=0.1, key="space_width", label_visibility="collapsed")
            holding_w = st.number_input("", min_value=0.0, step=0.1, key="holding_width", label_visibility="collapsed")
        
        with base_cols[2]:
            st.markdown("**Length (mm)**")
            plate_l = st.number_input("", min_value=0.0, step=0.1, key="plate_length", label_visibility="collapsed")
            top_l = st.number_input("", min_value=0.0, step=0.1, key="top_length", label_visibility="collapsed")
            space_l = st.number_input("", min_value=0.0, step=0.1, key="space_length", label_visibility="collapsed")
            holding_l = st.number_input("", min_value=0.0, step=0.1, key="holding_length", label_visibility="collapsed")
        
        with base_cols[3]:
            st.markdown("**Height (mm)**")
            plate_h = st.number_input("", min_value=0.0, step=0.1, key="plate_height", label_visibility="collapsed")
            top_h = st.number_input("", min_value=0.0, step=0.1, key="top_height", label_visibility="collapsed")
            space_h = st.number_input("", min_value=0.0, step=0.1, key="space_height", label_visibility="collapsed")
            holding_h = st.number_input("", min_value=0.0, step=0.1, key="holding_height", label_visibility="collapsed")
        
        base_processor = st.text_input("Base Processor", key="base_processor")
        cooling_pt_tap = st.text_input("Cooling PT TAP", key="cooling_pt_tap")
    
    # NOZZLE
    st.markdown("---")
    st.markdown("### 🔩 NOZZLE Specifications")
    
    nozzle_col1, nozzle_col2 = st.columns(2)
    
    with nozzle_col1:
        nozzle_type = st.text_input("Type", key="nozzle_type")
        
        gate_close = st.radio(
            "Gate Close",
            ["STRAIGHT", "TAPPER"],
            horizontal=True,
            key="gate_close"
        )
        
        nozzle_qty = st.number_input(
            "Quantity",
            min_value=0,
            step=1,
            key="nozzle_qty"
        )
    
    with nozzle_col2:
        ht_type = st.radio(
            "H/T Type",
            ["COIL", "ALLOY"],
            horizontal=True,
            key="ht_type"
        )
        
        nozzle_length = st.number_input(
            "LENGTH (mm)",
            min_value=0.0,
            step=0.1,
            key="nozzle_length"
        )
        
        st.info("📏 Refer to nozzle height diagram")
    
    # MANIFOLD
    st.markdown("---")
    st.markdown("### 🔀 MANIFOLD Specifications")
    
    manifold_col1, manifold_col2 = st.columns(2)
    
    with manifold_col1:
        manifold_type = st.radio(
            "Manifold Type",
            ["H", "I", "X", "T"],
            horizontal=True,
            key="manifold_type"
        )
    
    with manifold_col2:
        manifold_standard = st.radio(
            "Manifold Standard",
            ["ISO", "General"],
            horizontal=True,
            key="manifold_standard"
        )
    
    st.text_input("H/T Type (Fixed)", value="Sheath Heater", disabled=True, key="manifold_ht_fixed")
    
    # PISTON/CYLINDER
    st.markdown("---")
    st.markdown("### 🔧 CYLINDER & SENSOR")
    
    cylinder_col1, cylinder_col2 = st.columns(2)
    
    with cylinder_col1:
        cylinder_type = st.text_input("Cylinder Type", key="cylinder_type")
    
    with cylinder_col2:
        sensor_type = st.radio(
            "Sensor Type",
            ["J(I.C)", "K(C.A)"],
            horizontal=True,
            key="sensor_type"
        )
    
    # TIMER & CONNECTOR
    st.markdown("---")
    st.markdown("### 🔌 TIMER & CONNECTOR")
    
    timer_col1, timer_col2 = st.columns(2)
    
    with timer_col1:
        sol_volt = st.radio(
            "SOL Voltage",
            ["AC220V", "DC24V"],
            horizontal=True,
            key="sol_volt"
        )
        
        sol_control = st.radio(
            "SOL Control",
            ["Individual", "Integrated"],
            horizontal=True,
            key="sol_control"
        )
    
    with timer_col2:
        timer_pin_type = st.radio(
            "PIN Type",
            ["24PIN", "16PIN"],
            horizontal=True,
            key="timer_pin_type"
        )
        
        timer_buried = st.radio(
            "Buried",
            ["NO", "YES"],
            horizontal=True,
            key="timer_buried"
        )
    
    # Machine View 위치 선택
    timer_location = st.selectbox(
        "Location",
        ["G", "A", "B", "C", "D", "E", "F", "H", "I", "J", "K", "L", "UP"],
        key="timer_location"
    )
    
    # HEATER CONNECTOR
    st.markdown("---")
    st.markdown("### 🔥 HEATER CONNECTOR")
    
    heater_col1, heater_col2 = st.columns(2)
    
    with heater_col1:
        heater_pin_type = st.radio(
            "PIN Type",
            ["24PIN", "16PIN"],
            horizontal=True,
            key="heater_pin_type"
        )
        
        con_type = st.radio(
            "CON Type",
            ["BOX", "HOUSING"],
            horizontal=True,
            key="con_type"
        )
    
    with heater_col2:
        heater_buried = st.radio(
            "Buried",
            ["NO", "YES"],
            horizontal=True,
            key="heater_buried"
        )
        
        heater_location = st.selectbox(
            "Location",
            ["G", "A", "B", "C", "D", "E", "F", "H", "I", "J", "K", "L", "UP"],
            key="heater_location"
        )
    
    # ID CARD
    st.markdown("---")
    st.markdown("### 🆔 ID CARD")
    
    id_card_type = st.radio(
        "ID Card",
        ["Domestic", "Global"],
        horizontal=True,
        key="id_card_type"
    )
    
    # NL 정보
    st.markdown("---")
    st.markdown("### 📐 NL Information")
    
    nl_col1, nl_col2, nl_col3 = st.columns(3)
    
    with nl_col1:
        nl_phi = st.number_input("NL Φ", min_value=0.0, step=0.1, key="nl_phi")
    
    with nl_col2:
        nl_sr = st.number_input("NL S/R", min_value=0.0, step=0.1, key="nl_sr")
    
    with nl_col3:
        locate_ring = st.text_input("Locate Ring", key="locate_ring")
    
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
            'type': nozzle_type,
            'gate_close': gate_close,
            'qty': nozzle_qty,
            'ht_type': ht_type,
            'length': nozzle_length
        },
        'manifold_type': manifold_type,
        'manifold_standard': manifold_standard,
        'cylinder_type': cylinder_type,
        'sensor_type': sensor_type,
        'timer_connector': {
            'sol_volt': sol_volt,
            'sol_control': sol_control,
            'type': timer_pin_type,
            'buried': timer_buried == "YES",
            'location': timer_location
        },
        'heater_connector': {
            'type': heater_pin_type,
            'con_type': con_type,
            'buried': heater_buried == "YES",
            'location': heater_location
        },
        'id_card_type': id_card_type,
        'nl_phi': nl_phi,
        'nl_sr': nl_sr,
        'locate_ring': locate_ring
    }
    
    return technical_data