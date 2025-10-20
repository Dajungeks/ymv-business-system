# app/components/specifications/hot_runner_order_sheet.py

import streamlit as st
from datetime import datetime
import json
from components.specifications.customer_section import render_customer_section, validate_customer_data
from components.specifications.technical_section import render_technical_section
from components.specifications.gate_section import render_gate_section, reset_gate_data

def show_hot_runner_order_management(load_func, save_func, update_func, current_user):
    """규격 결정서 메인 관리 페이지"""
    
    st.title("📋 규격 결정서 (Specification Decision Sheet)")
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs([
        "📝 New Specification",
        "📋 Specification List",
        "🔍 Search & Edit"
    ])
    
    with tab1:
        render_order_form(load_func, save_func, current_user)
    
    with tab2:
        render_order_list(load_func, update_func, current_user)
    
    with tab3:
        render_search_edit(load_func, update_func, save_func, current_user)

def render_order_form(load_func, save_func, current_user):
    """주문서 작성 폼"""
    
    st.markdown("## Create New Specification Decision Sheet")
    
    # 언어 선택
    col_lang1, col_lang2 = st.columns([3, 1])
    
    with col_lang2:
        output_language = st.selectbox(
            "Output Language",
            ["EN", "VN"],
            key="output_language"
        )
    
    st.markdown("---")
    
    # 섹션별 입력
    with st.form("hot_runner_order_form"):
        
        # 1. 고객 정보
        customer_data = render_customer_section(load_func, save_func)
        
        st.markdown("---")
        
        # 2. 기술 사양
        technical_data = render_technical_section()
        
        st.markdown("---")
        
        # 3. Gate 정보
        gate_data = render_gate_section()
        
        st.markdown("---")
        
        # 제출 버튼
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        
        with col_btn1:
            submitted = st.form_submit_button(
                "💾 Save Specification",
                use_container_width=True,
                type="primary"
            )
        
        with col_btn2:
            preview = st.form_submit_button(
                "👁️ Preview",
                use_container_width=True
            )
        
        with col_btn3:
            reset = st.form_submit_button(
                "🔄 Reset",
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
                    st.success(f"✅ Specification saved successfully! Order No: {order_number}")
                    st.balloons()
                    
                    # Gate 데이터 초기화
                    reset_gate_data()
                    
                    # 저장 후 출력 옵션
                    st.info("💡 Go to 'Specification List' tab to print this specification")
                else:
                    st.error("❌ Failed to save specification")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # 미리보기 (Form 밖)
    if preview:
        st.markdown("---")
        st.markdown("### 👁️ Preview")
        
        # 고객 정보
        st.markdown("#### 📋 Customer Information")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.write(f"**Customer:** {customer_data.get('customer_name', 'N/A')}")
            st.write(f"**Project:** {customer_data.get('project_name', 'N/A')}")
            st.write(f"**Mold No:** {customer_data.get('mold_no', 'N/A')}")
        with col_p2:
            st.write(f"**Delivery To:** {customer_data.get('delivery_to', 'N/A')}")
            st.write(f"**Order Type:** {customer_data.get('order_type', 'N/A')}")
            st.write(f"**Color Change:** {'YES' if customer_data.get('color_change') else 'NO'}")
        
        # 기술 사양
        st.markdown("#### 🔧 Technical Specifications")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.write(f"**Nozzle Type:** {technical_data.get('nozzle_specs', {}).get('type', 'N/A')}")
            st.write(f"**Nozzle Qty:** {technical_data.get('nozzle_specs', {}).get('qty', 0)}")
        with col_t2:
            st.write(f"**Manifold Type:** {technical_data.get('manifold_type', 'N/A')}")
            st.write(f"**Cylinder Type:** {technical_data.get('cylinder_type', 'N/A')}")
        
        # Gate 정보
        st.markdown("#### 🎯 Gate Information")
        gates = gate_data.get('gate_data', {})
        gate_count = sum(1 for g in gates.values() if g.get('gate_phi', 0) > 0)
        st.write(f"**Total Gates:** {gate_count}")
    
    # 초기화
    if reset:
        reset_gate_data()
        st.rerun()

def render_order_list(load_func, update_func, current_user):
    """주문서 목록 조회"""
    
    st.markdown("## Specification Decision Sheet List")
    
    # 프린트 모드 체크 (최우선)
    if st.session_state.get('print_hot_runner'):
        order = st.session_state['print_hot_runner']
        
        # 프린트 화면 표시
        from utils.helpers import PrintFormGenerator
        PrintFormGenerator.render_hot_runner_print(order, load_func)
        
        # 돌아가기 버튼
        if st.button("← Back to List"):
            del st.session_state['print_hot_runner']
            st.rerun()
        
        return  # 프린트 모드일 때는 목록 표시 안 함
    
    # 데이터 로드 (YMK는 submitted 상태만 조회)
    orders = load_func('hot_runner_orders') if load_func else []
    
    current_user_role = current_user.get('role') if current_user else None
    
    if current_user_role == 'YMK':
        # YMK 계정은 submitted 상태만 조회
        orders = [o for o in orders if o.get('status') == 'submitted']
    
    if not orders:
        st.info("📋 No specifications found")
        return
    
    # 필터
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        status_filter = st.selectbox(
            "Status",
            ["All", "draft", "submitted", "approved", "rejected"],
            key="status_filter"
        )
    
    with col_filter2:
        language_filter = st.selectbox(
            "Language",
            ["All", "EN", "VN"],
            key="language_filter"
        )
    
    with col_filter3:
        search_query = st.text_input(
            "Search (Order No, Customer)",
            key="search_query"
        )
    
    # 필터링
    filtered_orders = orders
    
    if status_filter != "All":
        filtered_orders = [o for o in filtered_orders if o.get('status') == status_filter]
    
    if language_filter != "All":
        filtered_orders = [o for o in filtered_orders if o.get('language') == language_filter]
    
    if search_query:
        filtered_orders = [
            o for o in filtered_orders
            if search_query.lower() in o.get('order_number', '').lower()
            or search_query.lower() in o.get('customer_name', '').lower()
        ]
    
    # 목록 표시
    st.markdown(f"**Total: {len(filtered_orders)} specifications**")
    
    for order in filtered_orders:
        with st.expander(
            f"📄 {order.get('order_number')} - {order.get('customer_name')} - {order.get('project_name')}",
            expanded=False
        ):
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.markdown(f"**Customer:** {order.get('customer_name')}")
                st.markdown(f"**Project:** {order.get('project_name')}")
                st.markdown(f"**Mold No:** {order.get('mold_no', 'N/A')}")
            
            with col_info2:
                st.markdown(f"**Order Type:** {order.get('order_type')}")
                st.markdown(f"**Status:** {order.get('status')}")
                st.markdown(f"**Language:** {order.get('language')}")
            
            with col_info3:
                created_at = order.get('created_at', '')
                if created_at:
                    st.markdown(f"**Created:** {created_at[:10]}")
            
            # 버튼 (현재 사용자 역할에 따라 다르게 표시)
            order_status = order.get('status')
            
            if current_user_role == 'YMK':
                # YMK 계정 전용 버튼
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button("🖨️ Print", key=f"print_{order.get('id')}"):
                        st.session_state['print_hot_runner'] = order
                        st.rerun()
                
                with col_btn2:
                    if order_status == 'submitted':
                        if st.button("✅ Approve", key=f"approve_{order.get('id')}"):
                            # 승인 처리
                            update_data = {
                                'status': 'approved',
                                'reviewed_by': current_user.get('id'),
                                'reviewed_at': datetime.now().isoformat()
                            }
                            update_func('hot_runner_orders', order.get('id'), update_data)
                            st.success("✅ Specification approved!")
                            st.rerun()
                
                with col_btn3:
                    if order_status == 'submitted':
                        if st.button("❌ Reject", key=f"reject_{order.get('id')}"):
                            st.session_state[f'reject_modal_{order.get("id")}'] = True
                            st.rerun()
                
                # 거부 사유 입력 모달
                if st.session_state.get(f'reject_modal_{order.get("id")}'):
                    with st.form(key=f"reject_form_{order.get('id')}"):
                        st.markdown("### ❌ Rejection Reason")
                        rejection_reason = st.text_area(
                            "Please enter the reason for rejection:",
                            height=150,
                            key=f"rejection_reason_{order.get('id')}"
                        )
                        
                        col_submit, col_cancel = st.columns(2)
                        
                        with col_submit:
                            if st.form_submit_button("Submit Rejection", type="primary"):
                                if rejection_reason.strip():
                                    update_data = {
                                        'status': 'rejected',
                                        'reviewed_by': current_user.get('id'),
                                        'reviewed_at': datetime.now().isoformat(),
                                        'rejection_reason': rejection_reason
                                    }
                                    update_func('hot_runner_orders', order.get('id'), update_data)
                                    del st.session_state[f'reject_modal_{order.get("id")}']
                                    st.success("❌ Specification rejected!")
                                    st.rerun()
                                else:
                                    st.error("Please enter a rejection reason")
                        
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                del st.session_state[f'reject_modal_{order.get("id")}']
                                st.rerun()
            
            else:
                # 일반 사용자 버튼
                col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                
                with col_btn1:
                    if st.button("🖨️ Print", key=f"print_{order.get('id')}"):
                        st.session_state['print_hot_runner'] = order
                        st.rerun()
                
                with col_btn2:
                    if st.button("✏️ Edit", key=f"edit_{order.get('id')}"):
                        st.session_state['edit_order_id'] = order.get('id')
                        st.info("Go to 'Search & Edit' tab")
                
                with col_btn3:
                    # 제출 또는 재제출 버튼
                    if order_status == 'draft':
                        if st.button("📤 Submit", key=f"submit_{order.get('id')}"):
                            update_data = {
                                'status': 'submitted',
                                'submitted_at': datetime.now().isoformat()
                            }
                            update_func('hot_runner_orders', order.get('id'), update_data)
                            st.success("📤 Specification submitted for approval!")
                            st.rerun()
                    
                    elif order_status == 'rejected':
                        if st.button("🔄 Resubmit", key=f"resubmit_{order.get('id')}"):
                            update_data = {
                                'status': 'submitted',
                                'submitted_at': datetime.now().isoformat(),
                                'rejection_reason': None  # 재제출 시 거부 사유 초기화
                            }
                            update_func('hot_runner_orders', order.get('id'), update_data)
                            st.success("🔄 Specification resubmitted for approval!")
                            st.rerun()
                
                with col_btn4:
                    if st.button("🗑️ Delete", key=f"delete_{order.get('id')}"):
                        st.warning("Delete functionality - to be implemented")
            
            # 거부 사유 표시 (rejected 상태일 때)
            if order_status == 'rejected' and order.get('rejection_reason'):
                st.error(f"**Rejection Reason:** {order.get('rejection_reason')}")


def render_search_edit(load_func, update_func, save_func, current_user):
    """주문서 검색 및 수정"""
    
    st.markdown("## Search & Edit Specification Decision Sheet")
    
    # 검색
    search_order_no = st.text_input(
        "Enter Order Number",
        key="search_edit_order_no"
    )
    
    if search_order_no:
        orders = load_func('hot_runner_orders', {'order_number': search_order_no}) if load_func else []
        
        if orders:
            order = orders[0]
            
            st.success(f"✅ Found: {order.get('order_number')}")
            
            # 수정 폼 (render_order_form과 유사하게 구성)
            st.info("Edit functionality - Full implementation in next step")
            
            # 간단한 정보 표시
            st.json(order)
        else:
            st.error("❌ Specification not found")


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