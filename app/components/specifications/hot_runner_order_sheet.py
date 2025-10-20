# app/components/specifications/hot_runner_order_sheet.py

import streamlit as st
from datetime import datetime
import json
from components.specifications.customer_section import render_customer_section, validate_customer_data
from components.specifications.technical_section import render_technical_section
from components.specifications.gate_section import render_gate_section, reset_gate_data
from components.specifications.ymk_approval_interface import render_ymk_approval_interface
from utils.language_config import get_label, get_supported_languages

def show_hot_runner_order_management(load_func, save_func, update_func, current_user):
    """규격 결정서 메인 관리 페이지 - 권한별 분기"""
    
    # 권한 확인
    current_user_role = current_user.get('role') if current_user else None
    
    # YMK 계정은 승인 화면으로 이동
    if current_user_role == 'YMK':
        render_ymk_approval_interface()
        return
    
    # 일반 사용자는 기존 작성 화면
    st.title("📋 규격 결정서 (Specification Decision Sheet)")
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs([
        f"📝 {get_label('new_specification', 'EN')}",
        f"📋 {get_label('specification_list', 'EN')}",
        f"🔍 {get_label('search_and_edit', 'EN')}"
    ])
    
    with tab1:
        render_order_form(load_func, save_func, current_user)
    
    with tab2:
        render_order_list(load_func, update_func, current_user)
    
    with tab3:
        render_search_edit(load_func, update_func, save_func, current_user)


def render_order_form(load_func, save_func, current_user):
    """주문서 작성 폼"""
    
    st.markdown(f"## {get_label('new_specification', 'EN')}")
    
    # 언어 선택 (최상단)
    col_lang1, col_lang2, col_lang3 = st.columns([5, 2, 1])
    
    with col_lang2:
        # UI 표시 언어
        supported_langs = get_supported_languages()
        ui_language = st.selectbox(
            f"🌍 {get_label('language', 'EN')}",
            options=list(supported_langs.keys()),
            format_func=lambda x: supported_langs[x],
            key="ui_language"
        )
    
    with col_lang3:
        # 출력 언어 (DB 저장용)
        output_language = st.selectbox(
            get_label('output_language', ui_language),
            ["EN", "VN"],
            key="output_language"
        )
    
    st.markdown("---")
    
    # 섹션별 입력
    with st.form("hot_runner_order_form"):
        
        # 1. 고객 정보
        customer_data = render_customer_section(load_func, save_func, ui_language)
        
        st.markdown("---")
        
        # 2. 기술 사양
        technical_data = render_technical_section(ui_language)
        
        st.markdown("---")
        
        # 3. Gate 정보
        gate_data = render_gate_section(ui_language)
        
        st.markdown("---")
        
        # 제출 버튼
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        
        with col_btn1:
            submitted = st.form_submit_button(
                f"💾 {get_label('save', ui_language)}",
                use_container_width=True,
                type="primary"
            )
        
        with col_btn2:
            preview = st.form_submit_button(
                f"👁️ {get_label('preview', ui_language)}",
                use_container_width=True
            )
        
        with col_btn3:
            reset = st.form_submit_button(
                f"🔄 {get_label('reset', ui_language)}",
                use_container_width=True
            )
    
    # ========== Form 밖에서 처리 ==========
    
    # 저장 처리
    if submitted:
        # 필수 입력 검증
        is_valid, message = validate_customer_data(customer_data)
        
        if not is_valid:
            st.error(f"❌ {message}")
        else:
            # 데이터 병합
            order_data = {
                **customer_data,
                **technical_data,
                **gate_data,
                'language': output_language,
                'status': 'draft',
                'created_by': current_user.get('id') if current_user else None,
                'company': current_user.get('company') if current_user else None,
                'created_at': datetime.now().isoformat()
            }
            
            # Order Number 생성
            order_number = generate_order_number(save_func)
            order_data['order_number'] = order_number
            
            # JSON 변환 (JSONB 필드용)
            order_data['base_dimensions'] = json.dumps(order_data['base_dimensions'])
            order_data['nozzle_specs'] = json.dumps(order_data['nozzle_specs'])
            order_data['timer_connector'] = json.dumps(order_data['timer_connector'])
            order_data['heater_connector'] = json.dumps(order_data['heater_connector'])
            order_data['gate_data'] = json.dumps(order_data['gate_data'])
            
            # DB 저장
            try:
                result = save_func('hot_runner_orders', order_data)
                
                if result:
                    st.success(f"✅ {get_label('success', ui_language)}! Order No: {order_number}")
                    st.balloons()
                    
                    # Gate 데이터 초기화
                    reset_gate_data()
                    
                    # 저장 후 출력 옵션
                    st.info(f"💡 Go to '{get_label('specification_list', ui_language)}' tab to print this specification")
                else:
                    st.error(f"❌ {get_label('error', ui_language)}")
            
            except Exception as e:
                st.error(f"❌ {get_label('error', ui_language)}: {str(e)}")
    
    # 미리보기 (Form 밖)
    if preview:
        st.markdown("---")
        st.markdown(f"### 👁️ {get_label('preview', ui_language)}")
        
        # 고객 정보
        st.markdown(f"#### 📋 {get_label('customer_and_project', ui_language)}")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.write(f"**{get_label('customer', ui_language)}:** {customer_data.get('customer_name', 'N/A')}")
            st.write(f"**{get_label('project_name', ui_language)}:** {customer_data.get('project_name', 'N/A')}")
            st.write(f"**{get_label('mold_no', ui_language)}:** {customer_data.get('mold_no', 'N/A')}")
        with col_p2:
            st.write(f"**{get_label('delivery_to', ui_language)}:** {customer_data.get('delivery_to', 'N/A')}")
            st.write(f"**{get_label('order_type', ui_language)}:** {customer_data.get('order_type', 'N/A')}")
            color_value = get_label('yes', ui_language) if customer_data.get('color_change') else get_label('no', ui_language)
            st.write(f"**{get_label('color_change', ui_language)}:** {color_value}")
        
        # 기술 사양
        st.markdown(f"#### 🔧 {get_label('technical_specifications', ui_language)}")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.write(f"**{get_label('nozzle_type', ui_language)}:** {technical_data.get('nozzle_specs', {}).get('type', 'N/A')}")
            st.write(f"**{get_label('quantity', ui_language)}:** {technical_data.get('nozzle_specs', {}).get('qty', 0)}")
        with col_t2:
            st.write(f"**{get_label('manifold_type', ui_language)}:** {technical_data.get('manifold_type', 'N/A')}")
            st.write(f"**{get_label('cylinder_type', ui_language)}:** {technical_data.get('cylinder_type', 'N/A')}")
        
        # Gate 정보
        st.markdown(f"#### 🎯 {get_label('gate_information', ui_language)}")
        gates = gate_data.get('gate_data', {})
        gate_count = sum(1 for g in gates.values() if g.get('gate_phi', 0) > 0)
        st.write(f"**{get_label('total', ui_language)} Gates:** {gate_count}")
    
    # 초기화
    if reset:
        reset_gate_data()
        st.rerun()


def render_order_list(load_func, update_func, current_user):
    """주문서 목록 조회 - 본인 company 문서만 조회"""
    
    st.markdown(f"## {get_label('specification_list', 'EN')}")
    
    # 프린트 모드 체크 (최우선)
    if st.session_state.get('print_hot_runner'):
        order = st.session_state['print_hot_runner']
        
        # 프린트 화면 표시
        from utils.helpers import PrintFormGenerator
        PrintFormGenerator.render_hot_runner_print(order, load_func)
        
        # 돌아가기 버튼
        if st.button(f"← {get_label('back', 'EN')}"):
            del st.session_state['print_hot_runner']
            st.rerun()
        
        return
    
    # 데이터 로드 (본인 company만 조회)
    orders = load_func('hot_runner_orders') if load_func else []
    
    # 현재 사용자 company로 필터링
    current_user_company = current_user.get('company') if current_user else None
    
    if current_user_company:
        orders = [o for o in orders if o.get('company') == current_user_company]
    
    if not orders:
        st.info(f"📋 {get_label('no_data', 'EN')}")
        return
    
    # 필터
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        status_filter = st.selectbox(
            get_label('status', 'EN'),
            [get_label('all', 'EN'), get_label('draft', 'EN'), get_label('submitted', 'EN'), 
             get_label('approved', 'EN'), get_label('rejected', 'EN')],
            key="status_filter"
        )
    
    with col_filter2:
        language_filter = st.selectbox(
            get_label('language', 'EN'),
            [get_label('all', 'EN'), "EN", "VN"],
            key="language_filter"
        )
    
    with col_filter3:
        search_query = st.text_input(
            get_label('search', 'EN'),
            key="search_query"
        )
    
    # 필터링
    filtered_orders = orders
    
    # 상태 필터 매핑
    status_map = {
        get_label('all', 'EN'): None,
        get_label('draft', 'EN'): 'draft',
        get_label('submitted', 'EN'): 'submitted',
        get_label('approved', 'EN'): 'approved',
        get_label('rejected', 'EN'): 'rejected'
    }
    
    selected_status = status_map.get(status_filter)
    if selected_status:
        filtered_orders = [o for o in filtered_orders if o.get('status') == selected_status]
    
    if language_filter != get_label('all', 'EN'):
        filtered_orders = [o for o in filtered_orders if o.get('language') == language_filter]
    
    if search_query:
        filtered_orders = [
            o for o in filtered_orders
            if search_query.lower() in o.get('order_number', '').lower()
            or search_query.lower() in o.get('customer_name', '').lower()
        ]
    
    # 목록 표시
    st.markdown(f"**{get_label('total', 'EN')}: {len(filtered_orders)} specifications**")
    
    for order in filtered_orders:
        with st.expander(
            f"📄 {order.get('order_number')} - {order.get('customer_name')} - {order.get('project_name')}",
            expanded=False
        ):
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.markdown(f"**{get_label('customer', 'EN')}:** {order.get('customer_name')}")
                st.markdown(f"**{get_label('project_name', 'EN')}:** {order.get('project_name')}")
                st.markdown(f"**{get_label('mold_no', 'EN')}:** {order.get('mold_no', 'N/A')}")
            
            with col_info2:
                st.markdown(f"**{get_label('order_type', 'EN')}:** {order.get('order_type')}")
                
                # 상태 표시 (다국어)
                status_display = {
                    'draft': get_label('draft', 'EN'),
                    'submitted': get_label('submitted', 'EN'),
                    'approved': get_label('approved', 'EN'),
                    'rejected': get_label('rejected', 'EN')
                }
                st.markdown(f"**{get_label('status', 'EN')}:** {status_display.get(order.get('status'), order.get('status'))}")
                st.markdown(f"**{get_label('language', 'EN')}:** {order.get('language')}")
            
            with col_info3:
                created_at = order.get('created_at', '')
                if created_at:
                    st.markdown(f"**Created:** {created_at[:10]}")
            
            # 버튼
            order_status = order.get('status')
            
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if st.button(f"🖨️ {get_label('print', 'EN')}", key=f"print_{order.get('id')}"):
                    st.session_state['print_hot_runner'] = order
                    st.rerun()
            
            with col_btn2:
                if st.button(f"✏️ {get_label('edit', 'EN')}", key=f"edit_{order.get('id')}"):
                    st.session_state['edit_order_id'] = order.get('id')
                    st.info(f"Go to '{get_label('search_and_edit', 'EN')}' tab")
            
            with col_btn3:
                # 제출 또는 재제출 버튼
                if order_status == 'draft':
                    if st.button(f"📤 {get_label('submit', 'EN')}", key=f"submit_{order.get('id')}"):
                        update_data = {
                            'status': 'submitted',
                            'submitted_at': datetime.now().isoformat()
                        }
                        update_func('hot_runner_orders', order.get('id'), update_data)
                        st.success(f"📤 {get_label('success', 'EN')}!")
                        st.rerun()
                
                elif order_status == 'rejected':
                    if st.button("🔄 Resubmit", key=f"resubmit_{order.get('id')}"):
                        update_data = {
                            'status': 'submitted',
                            'submitted_at': datetime.now().isoformat(),
                            'rejection_reason': None
                        }
                        update_func('hot_runner_orders', order.get('id'), update_data)
                        st.success(f"🔄 {get_label('success', 'EN')}!")
                        st.rerun()
            
            with col_btn4:
                if st.button(f"🗑️ {get_label('delete', 'EN')}", key=f"delete_{order.get('id')}"):
                    st.warning("Delete functionality - to be implemented")
            
            # 거부 사유 표시 (rejected 상태일 때)
            if order_status == 'rejected' and order.get('rejection_reason'):
                st.error(f"**Rejection Reason:** {order.get('rejection_reason')}")


def render_search_edit(load_func, update_func, save_func, current_user):
    """주문서 검색 및 수정"""
    
    st.markdown(f"## {get_label('search_and_edit', 'EN')}")
    
    # 검색
    search_order_no = st.text_input(
        "Enter Order Number",
        key="search_edit_order_no"
    )
    
    if search_order_no:
        orders = load_func('hot_runner_orders', {'order_number': search_order_no}) if load_func else []
        
        # 본인 company만 조회 가능
        current_user_company = current_user.get('company') if current_user else None
        
        if current_user_company:
            orders = [o for o in orders if o.get('company') == current_user_company]
        
        if orders:
            order = orders[0]
            
            st.success(f"✅ Found: {order.get('order_number')}")
            
            # 수정 폼 (render_order_form과 유사하게 구성)
            st.info("Edit functionality - Full implementation in next step")
            
            # 간단한 정보 표시
            st.json(order)
        else:
            st.error("❌ Specification not found or access denied")


def generate_order_number(save_func):
    """Order Number 생성 (HRS-YYYY-####)"""
    
    current_year = datetime.now().year
    prefix = f"HRS-{current_year}-"
    
    # 최근 번호 조회
    try:
        orders = save_func.client.table('hot_runner_orders')\
            .select('order_number')\
            .like('order_number', f'{prefix}%')\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if orders.data:
            last_number = int(orders.data[0]['order_number'].split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
    except:
        new_number = 1
    
    return f"{prefix}{new_number:04d}"


def generate_print_html(order, load_func):
    """출력용 HTML 생성 및 표시 (수정 버전)"""
    
    from utils.helpers import PrintFormGenerator
    
    # PrintFormGenerator 사용
    PrintFormGenerator.render_hot_runner_print(order, load_func)