"""
물류사 관리 시스템
- 물류사 등록/수정/삭제
- 운송방식별 비용 관리
- 총 물류비 자동 계산
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def show_logistics_management(load_func, save_func, update_func, delete_func):
    """물류사 관리 메인 페이지"""
    st.title("🚚 물류사 관리")
    
    tab1, tab2 = st.tabs(["물류사 등록", "물류사 목록"])
    
    with tab1:
        render_logistics_form(save_func, load_func)
    
    with tab2:
        render_logistics_list(load_func, update_func, delete_func)


def render_logistics_form(save_func, load_func):
    """물류사 등록 폼"""
    st.header("📝 물류사 등록")
    
    with st.form("logistics_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("기본 정보")
            company_name = st.text_input("물류사명 *", placeholder="예: AAA 물류")
            transport_type = st.selectbox(
                "운송방식 *", 
                ["육로", "항공", "해운"],
                index=0
            )
        
        with col2:
            st.subheader("활성 상태")
            is_active = st.checkbox("활성화", value=True)
            st.caption("비활성화 시 견적서 작성에서 선택 불가")
        
        st.markdown("---")
        st.subheader("💰 비용 정보 (USD)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            china_inland = st.number_input(
                "중국 내륙 물류",
                min_value=0.0,
                value=0.0,
                step=10.0,
                format="%.2f"
            )
        
        with col2:
            china_customs = st.number_input(
                "중국 통관",
                min_value=0.0,
                value=0.0,
                step=10.0,
                format="%.2f"
            )
        
        with col3:
            vietnam_customs = st.number_input(
                "베트남 통관",
                min_value=0.0,
                value=0.0,
                step=10.0,
                format="%.2f"
            )
        
        with col4:
            vietnam_inland = st.number_input(
                "베트남 내륙 물류",
                min_value=0.0,
                value=0.0,
                step=10.0,
                format="%.2f"
            )
        
        # 총 물류비 계산
        total_cost = china_inland + china_customs + vietnam_customs + vietnam_inland
        
        st.markdown("---")
        st.info(f"💵 **총 물류비: ${total_cost:,.2f} USD**")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 저장", type="primary", use_container_width=True)
        
        with col2:
            reset = st.form_submit_button("🔄 초기화", use_container_width=True)
        
        if submitted:
            if not company_name.strip():
                st.error("❌ 물류사명을 입력해주세요.")
                return
            
            logistics_data = {
                'company_name': company_name.strip(),
                'transport_type': transport_type,
                'china_inland_cost': china_inland,
                'china_customs_cost': china_customs,
                'vietnam_customs_cost': vietnam_customs,
                'vietnam_inland_cost': vietnam_inland,
                'total_cost': total_cost,
                'is_active': is_active,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                if save_func('logistics_companies', logistics_data):
                    st.success("✅ 물류사가 성공적으로 등록되었습니다!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ 저장 실패")
            except Exception as e:
                st.error(f"❌ 저장 중 오류: {str(e)}")
        
        if reset:
            st.rerun()


def render_logistics_list(load_func, update_func, delete_func):
    """물류사 목록"""
    st.header("📋 물류사 목록")
    
    try:
        logistics_data = load_func('logistics_companies')
        
        if not logistics_data:
            st.info("등록된 물류사가 없습니다.")
            return
        
        logistics_df = pd.DataFrame(logistics_data)
        
        # 검색 필터
        st.markdown("### 🔍 검색")
        col1, col2, col3 = st.columns([3, 1.5, 1.5])
        
        with col1:
            search_term = st.text_input("검색", placeholder="물류사명", key="logistics_search")
        
        with col2:
            transport_filter = st.selectbox("운송방식", ["전체", "육로", "항공", "해운"], key="transport_filter")
        
        with col3:
            status_filter = st.selectbox("상태", ["전체", "활성", "비활성"], key="status_filter")
        
        st.markdown("---")
        
        # 수정/삭제 컨트롤
        render_logistics_edit_delete_controls(load_func, update_func, delete_func)
        
        # 필터링
        filtered_df = logistics_df.copy()
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['company_name'].str.contains(search_term, case=False, na=False)
            ]
        
        if transport_filter != "전체":
            filtered_df = filtered_df[filtered_df['transport_type'] == transport_filter]
        
        if status_filter == "활성":
            filtered_df = filtered_df[filtered_df['is_active'] == True]
        elif status_filter == "비활성":
            filtered_df = filtered_df[filtered_df['is_active'] == False]
        
        # 수정 폼 표시
        if st.session_state.get('show_edit_form_logistics'):
            render_logistics_edit_form(update_func)
        
        # 테이블 표시
        render_logistics_table(filtered_df)
    
    except Exception as e:
        st.error(f"❌ 목록 로드 중 오류: {str(e)}")


def render_logistics_edit_delete_controls(load_func, update_func, delete_func):
    """수정/삭제 컨트롤"""
    col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
    
    with col1:
        logistics_id_input = st.text_input("수정/삭제할 물류사 ID", placeholder="물류사 ID 입력", key="logistics_id_input")
    
    with col2:
        if st.button("✏️ 수정", use_container_width=True, type="primary"):
            if logistics_id_input and logistics_id_input.strip().isdigit():
                logistics_id = int(logistics_id_input.strip())
                logistics_list = load_func('logistics_companies') or []
                found = next((l for l in logistics_list if l.get('id') == logistics_id), None)
                
                if found:
                    st.session_state.editing_logistics_id = logistics_id
                    st.session_state.editing_logistics_data = found
                    st.session_state.show_edit_form_logistics = True
                    st.rerun()
                else:
                    st.error(f"❌ ID {logistics_id}를 찾을 수 없습니다.")
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    with col3:
        if st.button("🗑️ 삭제", use_container_width=True):
            if logistics_id_input and logistics_id_input.strip().isdigit():
                st.session_state.deleting_logistics_id = int(logistics_id_input.strip())
                st.rerun()
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    if st.session_state.get('deleting_logistics_id'):
        st.warning(f"⚠️ ID {st.session_state.deleting_logistics_id} 물류사를 삭제하시겠습니까?")
        
        del_col1, del_col2, _ = st.columns([1, 1, 4])
        
        with del_col1:
            if st.button("✅ 예", key="confirm_del_logistics"):
                if delete_func('logistics_companies', st.session_state.deleting_logistics_id):
                    st.success("✅ 삭제 완료!")
                    st.session_state.pop('deleting_logistics_id', None)
                    st.rerun()
        
        with del_col2:
            if st.button("❌ 아니오", key="cancel_del_logistics"):
                st.session_state.pop('deleting_logistics_id', None)
                st.rerun()
    
    st.markdown("---")


def render_logistics_edit_form(update_func):
    """물류사 수정 폼"""
    logistics = st.session_state.editing_logistics_data
    logistics_id = logistics.get('id')
    
    with st.expander(f"▼ 물류사 수정 (ID: {logistics_id})", expanded=True):
        with st.form(f"edit_logistics_{logistics_id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_company_name = st.text_input("물류사명", value=logistics.get('company_name', ''))
                new_transport_type = st.selectbox(
                    "운송방식",
                    ["육로", "항공", "해운"],
                    index=["육로", "항공", "해운"].index(logistics.get('transport_type', '육로'))
                )
            
            with col2:
                new_is_active = st.checkbox("활성화", value=logistics.get('is_active', True))
            
            st.markdown("---")
            st.subheader("💰 비용 정보 (USD)")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                new_china_inland = st.number_input(
                    "중국 내륙 물류",
                    min_value=0.0,
                    value=float(logistics.get('china_inland_cost', 0)),
                    step=10.0,
                    format="%.2f"
                )
            
            with col2:
                new_china_customs = st.number_input(
                    "중국 통관",
                    min_value=0.0,
                    value=float(logistics.get('china_customs_cost', 0)),
                    step=10.0,
                    format="%.2f"
                )
            
            with col3:
                new_vietnam_customs = st.number_input(
                    "베트남 통관",
                    min_value=0.0,
                    value=float(logistics.get('vietnam_customs_cost', 0)),
                    step=10.0,
                    format="%.2f"
                )
            
            with col4:
                new_vietnam_inland = st.number_input(
                    "베트남 내륙 물류",
                    min_value=0.0,
                    value=float(logistics.get('vietnam_inland_cost', 0)),
                    step=10.0,
                    format="%.2f"
                )
            
            new_total_cost = new_china_inland + new_china_customs + new_vietnam_customs + new_vietnam_inland
            
            st.markdown("---")
            st.info(f"💵 **총 물류비: ${new_total_cost:,.2f} USD**")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                save_btn = st.form_submit_button("💾 저장", type="primary", use_container_width=True)
            
            with col2:
                cancel_btn = st.form_submit_button("❌ 취소", use_container_width=True)
            
            if save_btn:
                if not new_company_name.strip():
                    st.error("물류사명 필수")
                    return
                
                update_data = {
                    'id': logistics_id,
                    'company_name': new_company_name.strip(),
                    'transport_type': new_transport_type,
                    'china_inland_cost': new_china_inland,
                    'china_customs_cost': new_china_customs,
                    'vietnam_customs_cost': new_vietnam_customs,
                    'vietnam_inland_cost': new_vietnam_inland,
                    'total_cost': new_total_cost,
                    'is_active': new_is_active,
                    'updated_at': datetime.now().isoformat()
                }
                
                if update_func('logistics_companies', update_data):
                    st.success("✅ 수정 완료!")
                    st.session_state.show_edit_form_logistics = False
                    st.session_state.pop('editing_logistics_id', None)
                    st.session_state.pop('editing_logistics_data', None)
                    st.rerun()
                else:
                    st.error("❌ 수정 실패")
            
            if cancel_btn:
                st.session_state.show_edit_form_logistics = False
                st.session_state.pop('editing_logistics_id', None)
                st.session_state.pop('editing_logistics_data', None)
                st.rerun()


def render_logistics_table(logistics_df):
    """물류사 테이블"""
    if logistics_df.empty:
        st.info("조건에 맞는 물류사가 없습니다.")
        return
    
    table_data = []
    for _, row in logistics_df.iterrows():
        table_data.append({
            'ID': row.get('id', ''),
            '물류사명': row.get('company_name', ''),
            '운송방식': row.get('transport_type', ''),
            '중국내륙': f"${row.get('china_inland_cost', 0):,.2f}",
            '중국통관': f"${row.get('china_customs_cost', 0):,.2f}",
            '베트남통관': f"${row.get('vietnam_customs_cost', 0):,.2f}",
            '베트남내륙': f"${row.get('vietnam_inland_cost', 0):,.2f}",
            '총물류비': f"${row.get('total_cost', 0):,.2f}",
            '상태': '✅ 활성' if row.get('is_active') else '❌ 비활성'
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"📊 총 **{len(logistics_df)}개** 물류사")