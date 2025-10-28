# app/components/specifications/gate_section.py

import streamlit as st
import pandas as pd
from utils.language_config import get_label

def render_gate_section(language='KO'):
    """Gate 정보 테이블 입력 섹션 - 실시간 미리보기"""
    
    st.markdown(f"### 📊 게이트 정보")
    
    # HRS 시스템 타입 확인
    hrs_system_type = st.session_state.get('hrs_system_type', 'Valve')
    
    # 노즐 수량 확인 (게이트 수 결정)
    nozzle_qty = st.session_state.get('nozzle_qty', 0)
    gate_count = min(max(nozzle_qty, 1), 20)  # 최소 1개, 최대 20개
    
    # Valve 타입일 때만 게이트 정보 입력
    if hrs_system_type == "Valve":
        st.info(f"✅ Valve 시스템: 노즐 수량({nozzle_qty})에 따라 게이트 {gate_count}개 활성화")
        
        # Gate 데이터 초기화
        if 'gate_data' not in st.session_state:
            st.session_state['gate_data'] = {
                f'G{i}': {'gate_phi': 0.0, 'length': 0.0, 'cylinder': 'None'}
                for i in range(1, 21)  # 최대 20개
            }
        
        # 실린더 옵션
        cylinder_options = ['None', 'FDY-50', 'FDY-60', 'FDY-70', 'FDY-80', 'CVS-85', 'CVS-105']
        
        # 2열 레이아웃으로 게이트 입력
        col1, col2 = st.columns(2)
        
        # 왼쪽 컬럼 (G1 ~ G10)
        with col1:
            st.markdown("#### G1 - G10")
            
            for i in range(1, 11):
                gate_no = f'G{i}'
                
                # 노즐 수량보다 많으면 비활성화
                if i <= gate_count:
                    st.markdown(f"**{gate_no}**")
                    
                    sub_col1, sub_col2, sub_col3 = st.columns(3)
                    
                    with sub_col1:
                        gate_phi = st.number_input(
                            f"게이트 Φ (mm)",
                            min_value=0.0,
                            step=0.1,
                            key=f"{gate_no}_phi",
                            value=st.session_state['gate_data'][gate_no]['gate_phi']
                        )
                        st.session_state['gate_data'][gate_no]['gate_phi'] = gate_phi
                    
                    with sub_col2:
                        gate_length = st.number_input(
                            f"길이 (mm)",
                            min_value=0.0,
                            step=0.1,
                            key=f"{gate_no}_length",
                            value=st.session_state['gate_data'][gate_no]['length']
                        )
                        st.session_state['gate_data'][gate_no]['length'] = gate_length
                    
                    with sub_col3:
                        # 실린더 선택
                        cylinder = st.selectbox(
                            "실린더",
                            cylinder_options,
                            index=cylinder_options.index(st.session_state['gate_data'][gate_no].get('cylinder', 'None')),
                            key=f"{gate_no}_cylinder"
                        )
                        st.session_state['gate_data'][gate_no]['cylinder'] = cylinder
                    
                    st.markdown("---")
                else:
                    # 비활성화 표시
                    st.markdown(f"**{gate_no}** (비활성)")
                    st.caption("노즐 수량을 초과하여 비활성화됨")
                    st.markdown("---")
        
        # 오른쪽 컬럼 (G11 ~ G20)
        with col2:
            st.markdown("#### G11 - G20")
            
            for i in range(11, 21):
                gate_no = f'G{i}'
                
                # 노즐 수량보다 많으면 비활성화
                if i <= gate_count:
                    st.markdown(f"**{gate_no}**")
                    
                    sub_col1, sub_col2, sub_col3 = st.columns(3)
                    
                    with sub_col1:
                        gate_phi = st.number_input(
                            f"게이트 Φ (mm)",
                            min_value=0.0,
                            step=0.1,
                            key=f"{gate_no}_phi",
                            value=st.session_state['gate_data'][gate_no]['gate_phi']
                        )
                        st.session_state['gate_data'][gate_no]['gate_phi'] = gate_phi
                    
                    with sub_col2:
                        gate_length = st.number_input(
                            f"길이 (mm)",
                            min_value=0.0,
                            step=0.1,
                            key=f"{gate_no}_length",
                            value=st.session_state['gate_data'][gate_no]['length']
                        )
                        st.session_state['gate_data'][gate_no]['length'] = gate_length
                    
                    with sub_col3:
                        # 실린더 선택
                        cylinder = st.selectbox(
                            "실린더",
                            cylinder_options,
                            index=cylinder_options.index(st.session_state['gate_data'][gate_no].get('cylinder', 'None')),
                            key=f"{gate_no}_cylinder"
                        )
                        st.session_state['gate_data'][gate_no]['cylinder'] = cylinder
                    
                    st.markdown("---")
                else:
                    # 비활성화 표시
                    st.markdown(f"**{gate_no}** (비활성)")
                    st.caption("노즐 수량을 초과하여 비활성화됨")
                    st.markdown("---")
        
        # 실시간 미리보기 테이블 (활성화된 게이트만)
        st.markdown("---")
        st.markdown(f"#### 📋 미리보기 테이블 (실시간)")
        
        # 활성화된 게이트 데이터만 추출
        active_gate_data = []
        for i in range(1, gate_count + 1):
            gate_no = f'G{i}'
            active_gate_data.append({
                'NO': gate_no,
                '게이트 Φ (mm)': st.session_state['gate_data'][gate_no]['gate_phi'],
                '길이 (mm)': st.session_state['gate_data'][gate_no]['length'],
                '실린더': st.session_state['gate_data'][gate_no].get('cylinder', 'None')
            })
        
        if active_gate_data:
            gate_df = pd.DataFrame(active_gate_data)
            
            st.dataframe(
                gate_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'NO': st.column_config.TextColumn('NO', width='small'),
                    '게이트 Φ (mm)': st.column_config.NumberColumn('게이트 Φ (mm)', format="%.1f"),
                    '길이 (mm)': st.column_config.NumberColumn('길이 (mm)', format="%.1f"),
                    '실린더': st.column_config.TextColumn('실린더', width='medium')
                }
            )
        else:
            st.info("노즐 수량을 입력하면 게이트 정보가 표시됩니다.")
    
    else:
        # Open 타입일 때는 게이트 정보 불필요
        st.info("ℹ️ Open 시스템: 게이트 정보 입력이 필요하지 않습니다.")
        
        # 빈 게이트 데이터
        if 'gate_data' not in st.session_state:
            st.session_state['gate_data'] = {
                f'G{i}': {'gate_phi': 0.0, 'length': 0.0, 'cylinder': 'None'}
                for i in range(1, 21)  # 최대 20개
            }
    
    # SPARE LIST & Special Notes
    st.markdown("---")
    st.markdown(f"### 📝 추가 정보")
    
    spare_list = st.text_area(
        "SPARE LIST",
        height=100,
        key="spare_list"
    )
    
    special_notes = st.text_area(
        "Special Notes",
        height=100,
        key="special_notes"
    )
    
    # 데이터 반환
    gate_data = {
        'gate_data': st.session_state['gate_data'],
        'spare_list': spare_list,
        'special_notes': special_notes,
        'hrs_system_type': hrs_system_type
    }
    
    return gate_data


def reset_gate_data():
    """Gate 데이터 초기화"""
    st.session_state['gate_data'] = {
        f'G{i}': {'gate_phi': 0.0, 'length': 0.0, 'cylinder': 'None'}
        for i in range(1, 21)  # 최대 20개
    }
