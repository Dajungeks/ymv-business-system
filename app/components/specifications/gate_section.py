# app/components/specifications/gate_section.py

import streamlit as st
import pandas as pd
from utils.language_config import get_label

def render_gate_section(language='EN'):
    """Gate 정보 테이블 입력 섹션"""
    
    st.markdown(f"### 📊 {get_label('gate_information', language)}")
    
    # Gate 데이터 초기화
    if 'gate_data' not in st.session_state:
        st.session_state['gate_data'] = {
            f'G{i}': {'gate_phi': 0.0, 'length': 0.0}
            for i in range(1, 11)
        }
    
    # 2열 레이아웃 (G1-G5 | G6-G10)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### G1 - G5")
        
        for i in range(1, 6):
            gate_no = f'G{i}'
            st.markdown(f"**{gate_no}**")
            
            sub_col1, sub_col2 = st.columns(2)
            
            with sub_col1:
                gate_phi = st.number_input(
                    f"{get_label('gate_phi', language)} (mm)",
                    min_value=0.0,
                    step=0.1,
                    key=f"{gate_no}_phi",
                    value=st.session_state['gate_data'][gate_no]['gate_phi']
                )
                st.session_state['gate_data'][gate_no]['gate_phi'] = gate_phi
            
            with sub_col2:
                gate_length = st.number_input(
                    f"{get_label('length', language)} (mm)",
                    min_value=0.0,
                    step=0.1,
                    key=f"{gate_no}_length",
                    value=st.session_state['gate_data'][gate_no]['length']
                )
                st.session_state['gate_data'][gate_no]['length'] = gate_length
            
            st.markdown("---")
    
    with col2:
        st.markdown("#### G6 - G10")
        
        for i in range(6, 11):
            gate_no = f'G{i}'
            st.markdown(f"**{gate_no}**")
            
            sub_col1, sub_col2 = st.columns(2)
            
            with sub_col1:
                gate_phi = st.number_input(
                    f"{get_label('gate_phi', language)} (mm)",
                    min_value=0.0,
                    step=0.1,
                    key=f"{gate_no}_phi",
                    value=st.session_state['gate_data'][gate_no]['gate_phi']
                )
                st.session_state['gate_data'][gate_no]['gate_phi'] = gate_phi
            
            with sub_col2:
                gate_length = st.number_input(
                    f"{get_label('length', language)} (mm)",
                    min_value=0.0,
                    step=0.1,
                    key=f"{gate_no}_length",
                    value=st.session_state['gate_data'][gate_no]['length']
                )
                st.session_state['gate_data'][gate_no]['length'] = gate_length
            
            st.markdown("---")
    
    # 미리보기 테이블
    st.markdown(f"#### {get_label('preview_table', language)}")
    
    gate_df = pd.DataFrame([
        {
            'NO': gate_no,
            get_label('gate_phi', language): st.session_state['gate_data'][gate_no]['gate_phi'],
            get_label('length', language): st.session_state['gate_data'][gate_no]['length']
        }
        for gate_no in [f'G{i}' for i in range(1, 11)]
    ])
    
    st.dataframe(gate_df, use_container_width=True, hide_index=True)
    
    # SPARE LIST & Special Notes
    st.markdown("---")
    st.markdown(f"### 📝 {get_label('additional_information', language)}")
    
    spare_list = st.text_area(
        get_label('spare_list', language),
        height=100,
        key="spare_list"
    )
    
    special_notes = st.text_area(
        get_label('special_notes', language),
        height=100,
        key="special_notes"
    )
    
    # 데이터 반환
    gate_data = {
        'gate_data': st.session_state['gate_data'],
        'spare_list': spare_list,
        'special_notes': special_notes
    }
    
    return gate_data


def reset_gate_data():
    """Gate 데이터 초기화"""
    st.session_state['gate_data'] = {
        f'G{i}': {'gate_phi': 0.0, 'length': 0.0}
        for i in range(1, 11)
    }