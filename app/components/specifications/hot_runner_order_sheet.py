# app/components/specifications/hot_runner_order_sheet.py
# 수정: 법인별 테이블 분리 적용 (V12)

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from components.specifications.customer_section import (
    render_quotation_selection,
    render_customer_search,
    render_customer_section,
    validate_customer_data
)
from components.specifications.technical_section import render_technical_section
from components.specifications.gate_section import render_gate_section
from utils.language_config import get_label


def clear_order_form_session():
    """규격 결정서 작성 관련 세션만 초기화 (로그인 정보는 유지)"""
    keys_to_clear = [
        'quotation_id', 'selected_customer_id', 'auto_quantity',
        'auto_customer_name', 'auto_delivery_to', 'auto_project_name',
        'auto_part_name', 'auto_mold_no', 'auto_sales_rep_id', 'auto_resin',
        'viewing_order_id', 'printing_order_id', 'editing_order_id',
        'ymk_rejecting', 'quotation_mode', 'selected_customer_name',
        'auto_item_code', 'auto_order_amount'
    ]
    
    # gate_data 관련 키들도 삭제
    gate_keys = [k for k in st.session_state.keys() if k.startswith('gate_')]
    keys_to_clear.extend(gate_keys)
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def check_quotation_already_linked(load_func, quotation_id, hot_runner_table):
    """견적서가 이미 규격 결정서와 연결되어 있는지 확인"""
    if not quotation_id:
        return False, None
    
    # 법인별 테이블에서 해당 견적서로 생성된 규격 결정서 조회
    orders = load_func(hot_runner_table, 
                       filters={'quotation_id': quotation_id})
    
    if orders and len(orders) > 0:
        # 삭제되지 않은 규격 결정서가 있는지 확인
        active_orders = [o for o in orders if o.get('status') != 'deleted']
        if active_orders:
            return True, active_orders[0].get('order_number')
    
    return False, None   


def show_hot_runner_order_management(load_func, save_func, update_func, current_user):
    """규격 결정서 관리 메인 함수"""
    
    st.title("🔥 Hot Runner 규격 결정서 관리")
    
    # 법인별 테이블명 생성
    from utils.helpers import get_company_table
    
    company_code = current_user.get('company')
    if not company_code:
        st.error("법인 정보가 없습니다.")
        return
    
    hot_runner_table = get_company_table('hot_runner_orders', company_code)
    
    # YMK 계정 확인
    is_ymk = current_user.get('username', '').upper() == 'YMK'
    
    if is_ymk:
        st.info("🔐 YMK 승인 모드로 접속하셨습니다.")
        # YMK는 승인 전용
        render_ymk_approval_page(load_func, update_func, current_user, hot_runner_table)
    else:
        # 일반 사용자: 작성, 목록, 수정
        tab1, tab2 = st.tabs(["📝 작성", "📋 목록"])
        
        with tab1:
            render_order_form(load_func, save_func, current_user, hot_runner_table)
        
        with tab2:
            render_order_list(load_func, update_func, current_user, hot_runner_table)
        

def generate_order_number(load_func, hot_runner_table, quotation_id=None):
    """주문번호 생성 (HRO-YYMMDD-NNN) + Revision 처리"""
    from datetime import datetime
    
    today = datetime.now().strftime("%y%m%d")
    prefix = f"HRO-{today}-"
    
    # 법인별 테이블에서 오늘 생성된 주문 조회
    all_orders = load_func(hot_runner_table) or []
    today_orders = [o for o in all_orders 
                    if o.get('order_number', '').startswith(prefix)]
    
    # 다음 번호 계산
    if today_orders:
        numbers = []
        for order in today_orders:
            order_num = order.get('order_number', '')
            try:
                # HRO-YYMMDD-NNN 형식에서 NNN 추출
                num = int(order_num.split('-')[-1])
                numbers.append(num)
            except:
                continue
        next_num = max(numbers) + 1 if numbers else 1
    else:
        next_num = 1
    
    order_number = f"{prefix}{next_num:03d}"
    
    # Revision 계산
    revision = "RV01"
    if quotation_id:
        # 동일 견적서의 기존 규격 결정서 조회
        existing = load_func(hot_runner_table, 
                           filters={'quotation_id': quotation_id})
        if existing:
            # 가장 높은 revision 찾기
            revisions = [o.get('revision', 'RV01') for o in existing]
            max_rev = max(revisions)
            # RV01 → RV02
            rev_num = int(max_rev[2:]) + 1
            revision = f"RV{rev_num:02d}"
    
    return order_number, revision


def render_order_form(load_func, save_func, current_user, hot_runner_table):
    """규격 결정서 작성 폼"""
    
    st.markdown("### 📝 새 규격 결정서 작성")
    
    # 견적서 중복 체크
    if st.session_state.get('quotation_id'):
        is_linked, linked_order = check_quotation_already_linked(
            load_func, 
            st.session_state.get('quotation_id'),
            hot_runner_table
        )
        if is_linked:
            st.error(f"❌ 이 견적서는 이미 규격 결정서 [{linked_order}]와 연결되어 있습니다.")
            if st.button("🔙 다시 선택"):
                del st.session_state['quotation_id']
                st.rerun()
            return
    
    # Form 밖: 견적서 선택 또는 고객 검색
    if not st.session_state.get('quotation_id') and not st.session_state.get('selected_customer_id'):
        render_quotation_selection(load_func, language='KO')
        render_customer_search(load_func, language='KO')
        return
    
    # Form 안: 입력 필드
    with st.form("order_form", clear_on_submit=False):
        st.markdown("---")
        
        # 고객 정보
        customer_data = render_customer_section(load_func, save_func, language='KO')
        
        st.markdown("---")
        
        # 기술 사양
        technical_data = render_technical_section(load_func, language='KO')
        
        st.markdown("---")
        
        # 게이트 정보
        gate_data = render_gate_section(language='KO')
        
        st.markdown("---")
        
        # 제출 버튼
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            submit_draft = st.form_submit_button("💾 임시 저장 (Draft)", use_container_width=True)
        
        with col2:
            submit_button = st.form_submit_button("✅ 제출 (Submit)", type="primary", use_container_width=True)
        
        with col3:
            cancel_button = st.form_submit_button("❌ 취소", use_container_width=True)
    
    # Form 밖: 저장 처리
    if cancel_button:
        # 세션 초기화 (로그인 정보는 유지)
        clear_order_form_session()
        st.success("✅ 취소되었습니다.")
        st.rerun()
    
    if submit_draft or submit_button:
        # 필수 입력 검증
        is_valid, message = validate_customer_data(customer_data)
        
        if not is_valid:
            st.error(f"❌ {message}")
            return
        
        # 주문번호 및 revision 생성
        order_number, revision = generate_order_number(
            load_func,
            hot_runner_table,
            customer_data.get('quotation_id')
        )
        
        # 상태 결정
        status = 'submitted' if submit_button else 'draft'
        
        # 발주 금액 계산 (견적서 연결 시)
        order_amount = None
        if customer_data.get('quotation_id'):
            quotation = load_func('quotations', 
                                 filters={'id': customer_data.get('quotation_id')})
            if quotation and len(quotation) > 0:
                order_amount = quotation[0].get('final_amount') or quotation[0].get('total_amount')
        
        # 데이터 병합 - 명시적 필드 매핑
        order_data = {
            'order_number': order_number,
            'revision': revision,
            'quotation_id': customer_data.get('quotation_id'),
            'customer_id': customer_data.get('customer_id'),
            'customer_name': customer_data.get('customer_name'),
            'delivery_to': customer_data.get('delivery_to'),
            'project_name': customer_data.get('project_name'),
            'part_name': customer_data.get('part_name'),
            'mold_no': customer_data.get('mold_no'),
            'ymv_no': customer_data.get('ymv_no'),
            'sales_contact': customer_data.get('sales_contact'),
            'injection_ton': customer_data.get('injection_ton'),
            'resin': customer_data.get('resin'),
            'additive': customer_data.get('additive'),
            'color_change': customer_data.get('color_change'),
            'order_type': customer_data.get('order_type'),
            'quotation_mode': customer_data.get('quotation_mode'),
            'order_amount': order_amount,
            'is_quotation_linked': True if customer_data.get('quotation_id') else False,
            
            # 기술 사양 - JSONB 필드
            'base_dimensions': json.dumps(technical_data.get('base_dimensions')),
            'base_processor': technical_data.get('base_processor'),
            'cooling_pt_tap': technical_data.get('cooling_pt_tap'),
            'nozzle_specs': json.dumps(technical_data.get('nozzle_specs')),
            'manifold_type': technical_data.get('manifold_type'),
            'manifold_standard': technical_data.get('manifold_standard'),
            'sensor_type': technical_data.get('sensor_type'),
            'timer_connector': json.dumps(technical_data.get('timer_connector')),
            'heater_connector': json.dumps(technical_data.get('heater_connector')),
            'id_card_type': technical_data.get('id_card_type'),
            'nl_phi': technical_data.get('nl_phi'),
            'nl_sr': technical_data.get('nl_sr'),
            'locate_ring': technical_data.get('locate_ring'),
            
            # HRS 시스템 타입 (별도 컬럼)
            'hrs_system_type': technical_data.get('nozzle_specs', {}).get('hrs_system_type'),
            
            # 게이트 정보 - JSONB 필드
            'gate_data': json.dumps(gate_data.get('gate_data')),
            'spare_list': gate_data.get('spare_list'),
            'special_notes': gate_data.get('special_notes'),
            
            # 상태 및 메타
            'status': status,
            'created_by': current_user.get('id'),
            'company': current_user.get('company', 'YMV'),
            'submitted_at': datetime.now().isoformat() if status == 'submitted' else None,
            'auto_quantity': st.session_state.get('auto_quantity', 0)
        }
        
        # 법인별 테이블에 DB 저장
        try:
            result = save_func(hot_runner_table, order_data)
            
            if status == 'submitted':
                st.success(f"✅ 규격 결정서 {order_number} ({revision})가 제출되었습니다! (YMK 승인 대기)")
            else:
                st.success(f"✅ 규격 결정서 {order_number} ({revision})가 임시 저장되었습니다!")
            
            # 세션 초기화 (로그인 정보는 유지)
            clear_order_form_session()
            st.rerun()
        
        except Exception as e:
            st.error(f"❌ 저장 실패: {str(e)}")


def render_order_list(load_func, update_func, current_user, hot_runner_table):
    """규격 결정서 목록 조회 (제품 CODE, 수량, 금액 포함)"""
    
    st.markdown("### 📋 규격 결정서 목록")
    
    # 법인별 테이블에서 데이터 로드
    orders = load_func(hot_runner_table) if load_func else []
    
    if not orders:
        st.info("등록된 규격 결정서가 없습니다.")
        return
    
    # 삭제된 항목 제외
    orders = [o for o in orders if o.get('status') != 'deleted']
    
    if not orders:
        st.info("등록된 규격 결정서가 없습니다.")
        return
    
    # 고객사, 영업담당 매핑
    customers = {c.get('id'): c.get('company_name_original', 'N/A') for c in load_func('customers')}
    employees = {e.get('id'): e.get('name', 'N/A') for e in load_func('employees')}
    
    # 검색 및 필터
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 검색", placeholder="주문번호, 고객사, 프로젝트명...")
    
    with col2:
        status_filter = st.selectbox("상태", 
                                     ["전체", "draft", "submitted", "approved", "rejected", "completed"])
    
    with col3:
        mode_filter = st.selectbox("모드", ["전체", "모드A", "모드B"])
    
    # 필터링
    filtered_orders = orders
    
    if search_query:
        filtered_orders = [
            o for o in filtered_orders
            if search_query.lower() in str(o.get('order_number', '')).lower()
            or search_query.lower() in str(o.get('customer_name', '')).lower()
            or search_query.lower() in str(o.get('project_name', '')).lower()
        ]
    
    if status_filter != "전체":
        filtered_orders = [o for o in filtered_orders if o.get('status') == status_filter]
    
    if mode_filter == "모드A":
        filtered_orders = [o for o in filtered_orders if o.get('quotation_mode') == 'A']
    elif mode_filter == "모드B":
        filtered_orders = [o for o in filtered_orders if o.get('quotation_mode') == 'B']
    
    # 테이블 데이터 생성
    table_data = []
    for order in filtered_orders:
        # 제품 CODE 추출 (nozzle_specs JSONB에서)
        nozzle_specs = order.get('nozzle_specs')
        product_code = 'N/A'
        if isinstance(nozzle_specs, dict):
            product_code = nozzle_specs.get('code', 'N/A')
        elif isinstance(nozzle_specs, str):
            try:
                nozzle_dict = json.loads(nozzle_specs)
                product_code = nozzle_dict.get('code', 'N/A')
            except:
                pass
        
        # 수량
        quantity = order.get('auto_quantity', 0)
        
        # 금액
        order_amount = order.get('order_amount', 0)
        amount_display = f"{order_amount:,.0f}" if order_amount else "N/A"
        
        # 상태 배지
        status = order.get('status', 'draft')
        status_badge = {
            'draft': '📝 작성중',
            'submitted': '⏳ 승인대기',
            'approved': '✅ 승인됨',
            'rejected': '❌ 부결됨',
            'completed': '🎉 완료'
        }.get(status, status)
        
        # 모드 배지
        mode = order.get('quotation_mode', 'B')
        mode_badge = '🔗 모드A' if mode == 'A' else '📝 모드B'
        
        # 영업담당
        sales_name = employees.get(order.get('sales_contact'), 'N/A')
        
        table_data.append({
            'ID': order.get('id'),
            '주문번호': order.get('order_number', 'N/A'),
            'Revision': order.get('revision', 'RV01'),
            '고객사': order.get('customer_name', 'N/A'),
            '프로젝트': order.get('project_name', 'N/A'),
            '제품 CODE': product_code,
            '수량': quantity,
            '발주금액': amount_display,
            '영업담당': sales_name,
            '상태': status_badge,
            '모드': mode_badge,
            '생성일': order.get('created_at', '')[:10] if order.get('created_at') else 'N/A',
            '제출일': order.get('submitted_at', '')[:10] if order.get('submitted_at') else 'N/A'
        })
    
    # 테이블 표시
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        
        st.markdown("---")
        st.markdown("#### 🎯 작업 선택")
        
        # ID 입력 및 버튼 (1개 입력, 4개 버튼)
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            selected_id = st.number_input("ID 입력", min_value=1, step=1, key="selected_order_id")
        
        with col2:
            if st.button("📄 상세", key="view_btn_list", use_container_width=True):
                st.session_state['viewing_order_id'] = selected_id
                st.rerun()
        
        with col3:
            if st.button("🖨️ 프린트", key="print_btn_list", use_container_width=True):
                st.session_state['printing_order_id'] = selected_id
                st.rerun()
        
        with col4:
            # 수정 가능 여부 확인
            selected_order = next((o for o in filtered_orders if o.get('id') == selected_id), None)
            can_edit = selected_order and selected_order.get('status') in ['draft', 'rejected']
            
            if st.button("✏️ 수정", key="edit_btn_list", disabled=not can_edit, use_container_width=True):
                st.session_state['editing_order_id'] = selected_id
                st.rerun()
        
        with col5:
            # 삭제 가능 여부 확인 (본인이 작성한 것만)
            can_delete = selected_order and selected_order.get('created_by') == current_user.get('id')
            
            if st.button("🗑️ 삭제", key="delete_btn_list", disabled=not can_delete, use_container_width=True):
                st.session_state['deleting_order_id'] = selected_id
                st.rerun()
        
        # 삭제 확인
        if st.session_state.get('deleting_order_id'):
            st.warning(f"⚠️ ID {st.session_state['deleting_order_id']}를 정말 삭제하시겠습니까?")
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("✅ 확인", type="primary", key="confirm_delete_list"):
                    update_data = {'status': 'deleted'}
                    if update_func(hot_runner_table, st.session_state['deleting_order_id'], update_data):
                        st.success("✅ 삭제되었습니다!")
                        del st.session_state['deleting_order_id']
                        st.rerun()
                    else:
                        st.error("❌ 삭제 실패")
            
            with col_b:
                if st.button("❌ 취소", key="cancel_delete_list"):
                    del st.session_state['deleting_order_id']
                    st.rerun()
    else:
        st.info("조건에 맞는 규격 결정서가 없습니다.")
    
    # 상세 보기 모달
    if st.session_state.get('viewing_order_id'):
        render_order_detail(load_func, st.session_state['viewing_order_id'], hot_runner_table)
        if st.button("❌ 닫기", key="close_view_list"):
            del st.session_state['viewing_order_id']
            st.rerun()
    
    # 프린트 미리보기 모달
    if st.session_state.get('printing_order_id'):
        render_print_preview(load_func, st.session_state['printing_order_id'], hot_runner_table)
        if st.button("❌ 닫기", key="close_print_list"):
            del st.session_state['printing_order_id']
    
    # 수정 모달
    if st.session_state.get("editing_order_id"):
        render_edit_form(load_func, update_func, current_user, hot_runner_table, st.session_state["editing_order_id"])
        if st.button("❌ 닫기", key="close_edit_list"):
            del st.session_state["editing_order_id"]
            st.rerun()
            st.rerun()


def render_order_detail(load_func, order_id, hot_runner_table):
    """규격 결정서 상세 보기"""
    
    st.markdown("---")
    st.markdown(f"### 📄 규격 결정서 상세 (ID: {order_id})")
    
    # 법인별 테이블에서 데이터 로드
    orders = load_func(hot_runner_table) if load_func else []
    order = next((o for o in orders if o.get('id') == order_id), None)
    
    if not order:
        st.error("❌ 해당 주문을 찾을 수 없습니다.")
        return
    
    # 기본 정보
    st.markdown("#### 📋 기본 정보")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**주문번호:** {order.get('order_number', 'N/A')}")
        st.write(f"**고객사:** {order.get('customer_name', 'N/A')}")
        st.write(f"**프로젝트:** {order.get('project_name', 'N/A')}")
    
    with col2:
        st.write(f"**납품처:** {order.get('delivery_to', 'N/A')}")
        st.write(f"**부품명:** {order.get('part_name', 'N/A')}")
        st.write(f"**금형번호:** {order.get('mold_no', 'N/A')}")
    
    with col3:
        st.write(f"**상태:** {order.get('status', 'N/A')}")
        st.write(f"**모드:** {'모드A' if order.get('quotation_mode') == 'A' else '모드B'}")
        st.write(f"**생성일:** {order.get('created_at', 'N/A')[:10] if order.get('created_at') else 'N/A'}")
    
    # 기술 사양
    st.markdown("---")
    st.markdown("#### 🔧 기술 사양")
    
    nozzle_specs = json.loads(order.get('nozzle_specs', '{}')) if order.get('nozzle_specs') else {}
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.write(f"**제품 CODE:** {nozzle_specs.get('code', 'N/A')}")
        st.write(f"**HRS 시스템:** {order.get('hrs_system_type', 'N/A')}")
        st.write(f"**수량:** {nozzle_specs.get('qty', 0)}")
    
    with col5:
        st.write(f"**MANIFOLD:** {order.get('manifold_type', 'N/A')}")
        st.write(f"**센서:** {order.get('sensor_type', 'N/A')}")
        st.write(f"**ID 카드:** {order.get('id_card_type', 'N/A')}")
    
    # 게이트 정보
    st.markdown("---")
    st.markdown("#### 📊 게이트 정보")
    
    gate_data = json.loads(order.get('gate_data', '{}')) if order.get('gate_data') else {}
    
    if gate_data and order.get('hrs_system_type') == 'Valve':
        gate_df_data = []
        for gate_no, gate_info in gate_data.items():
            if gate_info.get('gate_phi', 0) > 0 or gate_info.get('length', 0) > 0:
                gate_df_data.append({
                    'NO': gate_no,
                    '게이트 Φ': gate_info.get('gate_phi', 0),
                    '길이': gate_info.get('length', 0),
                    '실린더': gate_info.get('cylinder', 'None')
                })
        
        if gate_df_data:
            gate_df = pd.DataFrame(gate_df_data)
            st.dataframe(gate_df, use_container_width=True, hide_index=True)
        else:
            st.info("게이트 정보 없음")
    else:
        st.info("Open 시스템: 게이트 정보 없음")
    
    # 추가 정보
    st.markdown("---")
    st.markdown("#### 📝 추가 정보")
    
    st.text_area("SPARE LIST", value=order.get('spare_list', ''), height=100, disabled=True)
    st.text_area("Special Notes", value=order.get('special_notes', ''), height=100, disabled=True)
    
    # 부결 사유
    if order.get('status') == 'rejected':
        st.markdown("---")
        st.error(f"**부결 사유:** {order.get('rejection_reason', 'N/A')}")


def render_print_preview(load_func, order_id, hot_runner_table):
    """프린트 미리보기 (견적서와 유사한 구성)"""
    
    st.markdown("---")
    st.markdown(f"### 🖨️ 프린트 미리보기 (ID: {order_id})")
    
    # 법인별 테이블에서 데이터 로드
    orders = load_func(hot_runner_table) if load_func else []
    order = next((o for o in orders if o.get('id') == order_id), None)
    
    if not order:
        st.error("❌ 해당 주문을 찾을 수 없습니다.")
        return
    
    st.info("📄 실제 프린트 기능은 PDF 생성 라이브러리를 사용하여 구현됩니다.")
    
    # 프린트 내용 미리보기
    st.markdown(f"""
    # Hot Runner 규격 결정서
    
    **주문번호:** {order.get('order_number', 'N/A')}  
    **고객사:** {order.get('customer_name', 'N/A')}  
    **프로젝트:** {order.get('project_name', 'N/A')}  
    **납품처:** {order.get('delivery_to', 'N/A')}  
    
    ---
    
    ## 기술 사양
    - 제품 CODE: {json.loads(order.get('nozzle_specs', '{}')).get('code', 'N/A') if order.get('nozzle_specs') else 'N/A'}
    - HRS 시스템: {order.get('hrs_system_type', 'N/A')}
    - 수량: {json.loads(order.get('nozzle_specs', '{}')).get('qty', 0) if order.get('nozzle_specs') else 0}
    
    ---
    
    ## 게이트 정보
    _(게이트 테이블 표시)_
    
    ---
    
    **작성일:** {order.get('created_at', 'N/A')[:10] if order.get('created_at') else 'N/A'}  
    **승인자:** {order.get('reviewed_by', '-')}  
    """)


def render_search_edit(load_func, update_func, save_func, current_user, hot_runner_table):
    """검색 및 수정 (부결된 항목 재수정 + 삭제 가능)"""
    
    st.markdown("### 🔍 규격 결정서 검색/수정")
    
    # 법인별 테이블에서 본인이 작성한 규격 결정서만 조회
    orders = load_func(hot_runner_table) if load_func else []
    my_orders = [o for o in orders 
                 if o.get('created_by') == current_user.get('id')
                 and o.get('status') != 'deleted']
    
    if not my_orders:
        st.info("작성한 규격 결정서가 없습니다.")
        return
    
    # 수정 가능한 항목 (draft, rejected만)
    editable_orders = [o for o in my_orders 
                       if o.get('status') in ['draft', 'rejected']]
    
    # 상태별 필터
    status_filter = st.selectbox("상태 필터", 
                                 ["전체", "draft", "rejected", "submitted", "approved"])
    
    if status_filter != "전체":
        display_orders = [o for o in my_orders if o.get('status') == status_filter]
    else:
        display_orders = my_orders
    
    # 테이블 표시
    table_data = []
    for order in display_orders:
        status = order.get('status', 'draft')
        status_badge = {
            'draft': '📝 작성중',
            'submitted': '⏳ 승인대기',
            'approved': '✅ 승인됨',
            'rejected': '❌ 부결됨',
            'completed': '🎉 완료'
        }.get(status, status)
        
        editable = '✅ 수정가능' if status in ['draft', 'rejected'] else '🔒 수정불가'
        
        table_data.append({
            'ID': order.get('id'),
            '주문번호': order.get('order_number', 'N/A'),
            'Revision': order.get('revision', 'RV01'),
            '프로젝트': order.get('project_name', 'N/A'),
            '상태': status_badge,
            '수정가능': editable,
            '생성일': order.get('created_at', '')[:10] if order.get('created_at') else 'N/A',
            '부결사유': order.get('rejection_reason', '')[:30] + '...' if order.get('rejection_reason') and len(order.get('rejection_reason', '')) > 30 else order.get('rejection_reason', '')
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 수정/삭제 버튼
        col1, col2, col3 = st.columns(3)
        
        with col1:
            edit_id = st.number_input("ID 입력 (수정)", min_value=1, step=1, key="edit_id_input")
            if st.button("✏️ 수정", key="edit_btn_search"):
                selected = [o for o in editable_orders if o.get('id') == edit_id]
                if selected:
                    st.session_state['editing_order_id'] = edit_id
                    st.rerun()
                else:
                    st.error("❌ 수정할 수 없는 항목입니다. (draft 또는 rejected 상태만 가능)")
        
        with col2:
            delete_id = st.number_input("ID 입력 (삭제)", min_value=1, step=1, key="delete_id_input")
            confirm_delete = st.checkbox("삭제 확인", key="confirm_delete")
            
            if st.button("🗑️ 삭제", disabled=not confirm_delete, key="delete_btn_search"):
                selected = [o for o in my_orders if o.get('id') == delete_id]
                if selected:
                    # 실제 삭제 대신 status를 'deleted'로 변경
                    update_data = {'status': 'deleted'}
                    if update_func(hot_runner_table, delete_id, update_data):
                        st.success("✅ 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 삭제 실패")
                else:
                    st.error("❌ 해당 ID를 찾을 수 없습니다.")
        
        with col3:
            view_id = st.number_input("ID 입력 (보기)", min_value=1, step=1, key="view_id_input")
            if st.button("📄 상세 보기", key="view_btn_search"):
                st.session_state['viewing_order_id'] = view_id
                st.rerun()
        
        # 상세 보기
        if st.session_state.get('viewing_order_id'):
            render_order_detail(load_func, st.session_state['viewing_order_id'], hot_runner_table)
            if st.button("❌ 닫기", key="close_view_search"):
                del st.session_state['viewing_order_id']
                st.rerun()
        
    else:
        st.info("조건에 맞는 규격 결정서가 없습니다.")


def render_ymk_approval_page(load_func, update_func, current_user, hot_runner_table):
    """YMK 승인 전용 페이지 (승인 후 재수정 지원)"""
    
    st.markdown("### 🔐 YMK 승인 페이지")
    
    # 법인별 테이블에서 submitted 상태 규격 결정서 조회
    orders = load_func(hot_runner_table, 
                       filters={'status': 'submitted'}) if load_func else []
    
    if not orders:
        st.info("승인 대기 중인 규격 결정서가 없습니다.")
        return
    
    # 영업담당 매핑
    employees = {e.get('id'): e.get('name', 'N/A') for e in load_func('employees')}
    
    st.write(f"📋 승인 대기 목록: **{len(orders)}건**")
    
    # 테이블 데이터 생성
    table_data = []
    for order in orders:
        # 제품 CODE 추출
        nozzle_specs = order.get('nozzle_specs')
        product_code = 'N/A'
        if isinstance(nozzle_specs, dict):
            product_code = nozzle_specs.get('code', 'N/A')
        elif isinstance(nozzle_specs, str):
            try:
                nozzle_dict = json.loads(nozzle_specs)
                product_code = nozzle_dict.get('code', 'N/A')
            except:
                pass
        
        table_data.append({
            'ID': order.get('id'),
            '주문번호': order.get('order_number', 'N/A'),
            'Revision': order.get('revision', 'RV01'),
            '고객사': order.get('customer_name', 'N/A'),
            '프로젝트': order.get('project_name', 'N/A'),
            '제품 CODE': product_code,
            '수량': order.get('auto_quantity', 0),
            '영업담당': 'YMV',
            '제출일': order.get('submitted_at', '')[:10] if order.get('submitted_at') else 'N/A'
        })
    
    # 테이블 표시
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 승인/부결 처리
        col1, col2 = st.columns(2)
        
        with col1:
            order_id = st.number_input("ID 입력", min_value=1, step=1, key="ymk_order_id")
        
        with col2:
            if st.button("📄 상세 보기", key="view_btn_ymk"):
                st.session_state['viewing_order_id'] = order_id
                st.rerun()
        
        # 상세 보기 후 승인/부결
        if st.session_state.get('viewing_order_id'):
            selected_order = [o for o in orders if o.get('id') == st.session_state['viewing_order_id']]
            
            if selected_order:
                order = selected_order[0]
                render_order_detail(load_func, order.get('id'), hot_runner_table)
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("✅ 승인", type="primary", use_container_width=True, key="approve_btn_ymk"):
                        update_data = {
                            'status': 'approved',
                            'reviewed_by': current_user.get('id'),
                            'reviewed_at': datetime.now().isoformat(),
                            'rejection_reason': None
                        }
                        
                        if update_func(hot_runner_table, order.get('id'), update_data):
                            st.success("✅ 승인되었습니다!")
                            del st.session_state['viewing_order_id']
                            st.rerun()
                        else:
                            st.error("❌ 승인 처리 실패")
                
                with col2:
                    if st.button("❌ 부결", use_container_width=True, key="reject_btn_ymk"):
                        st.session_state['ymk_rejecting'] = order.get('id')
                        st.rerun()
                
                with col3:
                    if st.button("🔙 닫기", use_container_width=True, key="close_btn_ymk"):
                        del st.session_state['viewing_order_id']
                        if 'ymk_rejecting' in st.session_state:
                            del st.session_state['ymk_rejecting']
                        st.rerun()
                
                # 부결 사유 입력
                if st.session_state.get('ymk_rejecting') == order.get('id'):
                    st.markdown("---")
                    st.markdown("### ❌ 부결 사유 입력")
                    
                    rejection_reason = st.text_area("부결 사유 *", height=100)
                    
                    if st.button("💾 부결 처리", type="primary", key="confirm_reject_ymk"):
                        if not rejection_reason.strip():
                            st.error("❌ 부결 사유를 입력해주세요.")
                        else:
                            update_data = {
                                'status': 'rejected',
                                'reviewed_by': current_user.get('id'),
                                'reviewed_at': datetime.now().isoformat(),
                                'rejection_reason': rejection_reason
                            }
                            
                            if update_func(hot_runner_table, order.get('id'), update_data):
                                st.success("✅ 부결 처리되었습니다!")
                                del st.session_state['viewing_order_id']
                                del st.session_state['ymk_rejecting']
                                st.rerun()
                            else:
                                st.error("❌ 부결 처리 실패")        # 수정 폼
        if st.session_state.get('editing_order_id'):
            order_to_edit = [o for o in editable_orders 
                           if o.get('id') == st.session_state['editing_order_id']]
            
            if order_to_edit:
                render_edit_form(load_func, update_func, current_user, hot_runner_table, st.session_state['editing_order_id'])
    else:
        st.info("조건에 맞는 규격 결정서가 없습니다.")



def render_edit_form(load_func, update_func, current_user, hot_runner_table, order_id):
    """규격 결정서 수정 폼 (전체 필드)"""
    
    st.markdown("---")
    st.markdown("### ✏️ 규격 결정서 수정")
    
    # 기존 데이터 로드
    orders = load_func(hot_runner_table) if load_func else []
    order = next((o for o in orders if o.get('id') == order_id), None)
    
    if not order:
        st.error("❌ 해당 주문을 찾을 수 없습니다.")
        return
    
    # 부결 사유 표시
    if order.get('status') == 'rejected' and order.get('rejection_reason'):
        st.error(f"**부결 사유:** {order.get('rejection_reason')}")
    
    # 기존 데이터를 세션에 로드
    if 'edit_loaded' not in st.session_state:
        st.session_state['selected_customer_name'] = order.get('customer_name', '')
        st.session_state['selected_customer_id'] = order.get('customer_id')
        st.session_state['auto_project_name'] = order.get('project_name', '')
        st.session_state['auto_part_name'] = order.get('part_name', '')
        st.session_state['auto_mold_no'] = order.get('mold_no', '')
        st.session_state['auto_sales_rep_id'] = order.get('sales_contact')
        st.session_state['auto_resin'] = order.get('resin', '')
        st.session_state['quotation_mode'] = order.get('quotation_mode', 'B')
        st.session_state['edit_loaded'] = True
    
    # Form 안: 입력 필드 (작성 폼과 동일)
    with st.form("edit_order_form", clear_on_submit=False):
        st.markdown("---")
        
        # 고객 정보
        from components.specifications.customer_section import render_customer_section, validate_customer_data
        customer_data = render_customer_section_edit(load_func, None, order, language='KO')
        
        st.markdown("---")
        
        # 기술 사양

        from components.specifications.technical_section import render_technical_section
        technical_data = render_technical_section(load_func, language='KO', key_prefix='edit_')
        
        st.markdown("---")
        
        # 게이트 정보
        from components.specifications.gate_section import render_gate_section
        gate_data = render_gate_section(language='KO', key_prefix='edit_')
        
        st.markdown("---")
        
        # 제출 버튼
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            save_button = st.form_submit_button("💾 수정 저장", type="primary", use_container_width=True)
        
        with col2:
            resubmit_button = st.form_submit_button("📤 재제출", use_container_width=True)
        
        with col3:
            cancel_button = st.form_submit_button("❌ 취소", use_container_width=True)
    
    # Form 밖: 저장 처리
    if cancel_button:
        del st.session_state['editing_order_id']
        del st.session_state['edit_loaded']
        clear_order_form_session()
        st.rerun()
    
    if save_button or resubmit_button:
        # 필수 입력 검증
        is_valid, message = validate_customer_data(customer_data)
        
        if not is_valid:
            st.error(f"❌ {message}")
            return
        
        # 데이터 병합
        update_data = {
            'customer_id': customer_data.get('customer_id'),
            'customer_name': customer_data.get('customer_name'),
            'delivery_to': customer_data.get('delivery_to'),
            'project_name': customer_data.get('project_name'),
            'part_name': customer_data.get('part_name'),
            'mold_no': customer_data.get('mold_no'),
            'ymv_no': customer_data.get('ymv_no'),
            'sales_contact': customer_data.get('sales_contact'),
            'injection_ton': customer_data.get('injection_ton'),
            'resin': customer_data.get('resin'),
            'additive': customer_data.get('additive'),
            'color_change': customer_data.get('color_change'),
            'order_type': customer_data.get('order_type'),
            
            # 기술 사양
            'base_dimensions': json.dumps(technical_data.get('base_dimensions')),
            'base_processor': technical_data.get('base_processor'),
            'cooling_pt_tap': technical_data.get('cooling_pt_tap'),
            'nozzle_specs': json.dumps(technical_data.get('nozzle_specs')),
            'manifold_type': technical_data.get('manifold_type'),
            'manifold_standard': technical_data.get('manifold_standard'),
            'sensor_type': technical_data.get('sensor_type'),
            'timer_connector': json.dumps(technical_data.get('timer_connector')),
            'heater_connector': json.dumps(technical_data.get('heater_connector')),
            'id_card_type': technical_data.get('id_card_type'),
            'nl_phi': technical_data.get('nl_phi'),
            'nl_sr': technical_data.get('nl_sr'),
            'locate_ring': technical_data.get('locate_ring'),
            'hrs_system_type': technical_data.get('nozzle_specs', {}).get('hrs_system_type'),
            
            # 게이트 정보
            'gate_data': json.dumps(gate_data.get('gate_data')),
            'spare_list': gate_data.get('spare_list'),
            'special_notes': gate_data.get('special_notes')
        }
        
        # 재제출일 경우 상태 변경
        if resubmit_button:
            update_data['status'] = 'submitted'
            update_data['submitted_at'] = datetime.now().isoformat()
            update_data['rejection_reason'] = None
        
        # DB 업데이트
        try:
            update_data['id'] = order_id
            if update_func(hot_runner_table, update_data):
                if resubmit_button:
                    st.success(f"✅ 수정 및 재제출되었습니다! (YMK 승인 대기)")
                else:
                    st.success("✅ 수정되었습니다!")
                del st.session_state['editing_order_id']
                del st.session_state['edit_loaded']
                clear_order_form_session()
                st.rerun()
            else:
                st.error("❌ 수정 실패")
        except Exception as e:
            st.error(f"❌ 수정 실패: {str(e)}")


def render_customer_section_edit(load_func, save_func, order, language='KO'):
    """수정용 고객 정보 섹션 (key 중복 방지)"""
    
    st.markdown(f"### 📋 고객 및 프로젝트 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input(
            f"🔴 고객사 *",
            value=order.get('customer_name', ''),
            key="edit_customer_name_input"
        )
        
        project_name = st.text_input(
            f"🔴 프로젝트명 *",
            value=order.get('project_name', ''),
            key="edit_project_name"
        )
        
        mold_no = st.text_input(
            "금형번호",
            value=order.get('mold_no', ''),
            key="edit_mold_no"
        )
    
    with col2:
        delivery_to = st.text_input(
            f"🔴 납품처 *",
            value=order.get('delivery_to', ''),
            key="edit_delivery_to"
        )
        
        part_name = st.text_input(
            "부품명",
            value=order.get('part_name', ''),
            key="edit_part_name"
        )
        
        ymv_no = st.text_input(
            "YMV 번호",
            value=order.get('ymv_no', ''),
            key="edit_ymv_no"
        )
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        employees = load_func('employees') if load_func else []
        sales_employees = [e for e in employees if e.get('role') in ['Manager', 'Admin', 'CEO']]
        
        current_sales_id = order.get('sales_contact')
        default_index = 0
        for idx, emp in enumerate(sales_employees):
            if emp.get('id') == current_sales_id:
                default_index = idx
                break
        
        employee_options = [f"{e.get('name', 'N/A')} - {e.get('position', '')}" for e in sales_employees]
        selected_employee = st.selectbox(
            f"🔴 영업담당 *",
            employee_options,
            index=default_index,
            key="edit_sales_contact"
        )
        sales_contact_id = sales_employees[employee_options.index(selected_employee)].get('id')
        
        resin = st.text_input("수지", value=order.get('resin', ''), key="edit_resin")
    
    with col4:
        injection_ton = st.number_input(
            "사출기 TON",
            value=int(order.get('injection_ton', 0)),
            min_value=0,
            step=10,
            key="edit_injection_ton"
        )
        
        additive = st.text_input("첨가제", value=order.get('additive', ''), key="edit_additive")
    
    st.markdown("---")
    st.markdown(f"### 🔧 주문 옵션")
    
    col5, col6 = st.columns(2)
    
    with col5:
        color_change_val = 1 if order.get('color_change') else 0
        color_change = st.radio(
            f"🔴 색상 변경 *",
            ["없음", "있음"],
            index=color_change_val,
            horizontal=True,
            key="edit_color_change"
        )
    
    with col6:
        order_type_options = ["SYSTEM", "SEMI", "TOTAL"]
        order_type_index = order_type_options.index(order.get('order_type', 'SYSTEM')) if order.get('order_type') in order_type_options else 0
        order_type = st.radio(
            f"🔴 주문 타입 *",
            order_type_options,
            index=order_type_index,
            horizontal=True,
            key="edit_order_type"
        )
    
    return {
        'customer_id': order.get('customer_id'),
        'customer_name': customer_name,
        'delivery_to': delivery_to,
        'project_name': project_name,
        'part_name': part_name,
        'mold_no': mold_no,
        'ymv_no': ymv_no,
        'sales_contact': sales_contact_id,
        'injection_ton': injection_ton,
        'resin': resin,
        'additive': additive,
        'color_change': color_change == "있음",
        'order_type': order_type
    }