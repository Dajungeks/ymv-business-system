# app/components/specifications/customer_section.py

import streamlit as st
import pandas as pd
from datetime import date
from utils.language_config import get_label

def render_quotation_selection(load_func, language='KO'):
    """견적서 연결 - 테이블 목록 선택 방식 (Form 밖에서 실행)"""
    
    st.markdown(f"### 🔗 견적서 연결 (선택사항)")
    
    # 모드 A: 견적서 연결
    st.info("💡 모드 A: Approved 상태의 견적서를 선택하여 고객 정보와 제품 CODE를 자동으로 가져옵니다.")
    
    # Approved 상태의 견적서만 조회
    all_quotations = load_func('quotations') if load_func else []
    approved_quotations = [q for q in all_quotations if q.get('status') == 'Approved']
    
    if not approved_quotations:
        st.warning("⚠️ Approved 상태의 견적서가 없습니다.")
        st.markdown("---")
        return
    
    st.write(f"📊 **Approved 견적서 목록** (총 {len(approved_quotations)}건)")
    
    # 데이터프레임 생성
    df_data = []
    for q in approved_quotations:
        df_data.append({
            'ID': q.get('id'),
            '견적번호': q.get('quote_number', 'N/A'),
            '리비전': q.get('revision', 'Rv00'),
            '고객사': q.get('customer_name', 'N/A'),
            '프로젝트': q.get('item_name_en', 'N/A'),
            '제품 CODE': q.get('item_code', 'N/A'),
            '품명': q.get('part_name', 'N/A'),
            '수지': q.get('resin_type', 'N/A'),
            '수량': q.get('quantity', 0),
            '금액': f"{q.get('final_amount', 0):,.0f}",
            '통화': q.get('currency', 'VND'),
            '날짜': q.get('created_at', 'N/A')[:10] if q.get('created_at') else 'N/A'
        })
    
    df = pd.DataFrame(df_data)
    
    # 테이블 표시
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'ID': st.column_config.NumberColumn('ID', width='small'),
            '견적번호': st.column_config.TextColumn('견적번호', width='medium'),
            '리비전': st.column_config.TextColumn('리비전', width='small'),
            '고객사': st.column_config.TextColumn('고객사', width='medium'),
            '프로젝트': st.column_config.TextColumn('프로젝트', width='medium'),
            '제품 CODE': st.column_config.TextColumn('제품 CODE', width='medium'),
            '품명': st.column_config.TextColumn('품명', width='medium'),
            '수지': st.column_config.TextColumn('수지', width='small'),
            '수량': st.column_config.NumberColumn('수량', width='small'),
            '금액': st.column_config.TextColumn('금액', width='small'),
            '통화': st.column_config.TextColumn('통화', width='small'),
            '날짜': st.column_config.TextColumn('날짜', width='small')
        }
    )
    
    st.markdown("---")
    
    # 견적서 선택
    col1, col2 = st.columns([3, 1])
    
    with col1:
        quotation_id_input = st.number_input(
            "선택할 견적서 ID를 입력하세요",
            min_value=1,
            step=1,
            key="quotation_id_input",
            help="위 테이블에서 ID를 확인하고 입력하세요"
        )
    
    with col2:
        st.write("")  # 버튼 정렬용 공백
        st.write("")  # 버튼 정렬용 공백
        if st.button("🔗 연결", type="primary", use_container_width=True):
            # 선택한 견적서 찾기
            selected_q = next((q for q in approved_quotations if q.get('id') == quotation_id_input), None)
            
            if selected_q:
                # 세션 저장
                st.session_state['quotation_id'] = selected_q.get('id')
                st.session_state['selected_customer_name'] = selected_q.get('customer_name', '')
                st.session_state['selected_customer_id'] = selected_q.get('customer_id')
                st.session_state['auto_project_name'] = selected_q.get('item_name_en', '')
                st.session_state['auto_part_name'] = selected_q.get('part_name', '')
                st.session_state['auto_mold_no'] = selected_q.get('mold_number', '')
                st.session_state['auto_sales_rep_id'] = selected_q.get('sales_rep_id')
                st.session_state['auto_resin'] = selected_q.get('resin_type', '')
                st.session_state['auto_product_code'] = selected_q.get('item_code', '')  # 제품 CODE
                st.session_state['auto_quantity'] = selected_q.get('quantity', 0)  # 수량 추가
                st.session_state['quotation_mode'] = 'A'  # 모드 A
                st.success(f"✅ 견적서 {selected_q.get('quote_number')} 연결 완료!")
                st.rerun()
            else:
                st.error(f"❌ 견적서 ID {quotation_id_input}를 찾을 수 없습니다. 위 목록에서 ID를 확인하세요.")
    
    # 선택된 견적서 표시
    if st.session_state.get('quotation_id'):
        st.success(f"✅ 연결된 견적서 ID: {st.session_state['quotation_id']}")
        st.info(f"📋 고객: {st.session_state.get('selected_customer_name', 'N/A')} | 프로젝트: {st.session_state.get('auto_project_name', 'N/A')}")
        
        if st.button("❌ 연결 해제"):
            # 세션 초기화
            st.session_state.pop('quotation_id', None)
            st.session_state.pop('selected_customer_name', None)
            st.session_state.pop('selected_customer_id', None)
            st.session_state.pop('auto_project_name', None)
            st.session_state.pop('auto_part_name', None)
            st.session_state.pop('auto_mold_no', None)
            st.session_state.pop('auto_sales_rep_id', None)
            st.session_state.pop('auto_resin', None)
            st.session_state.pop('auto_product_code', None)
            st.session_state.pop('auto_quantity', None)  # 수량 제거
            st.session_state.pop('quotation_mode', None)
            st.rerun()
    
    st.markdown("---")


def render_customer_search(load_func, language='KO'):
    """고객사 검색 (Form 밖에서 실행)"""
    
    # 모드 B: 독립 작성
    st.markdown(f"### 🔍 고객사 검색")
    st.info("💡 모드 B: 견적서 없이 독립적으로 작성합니다. 고객 정보와 제품 CODE를 직접 입력합니다.")
    
    customers = load_func('customers') if load_func else []
    
    if not customers:
        st.warning("등록된 고객사가 없습니다.")
        return
    
    # 검색창
    search_term = st.text_input(
        "고객사 이름 검색",
        placeholder="고객사 이름을 입력하세요...",
        key="customer_search_term"
    )
    
    # 검색 결과
    if search_term:
        filtered_customers = [
            c for c in customers 
            if (search_term.lower() in c.get('company_name_original', '').lower() or
                search_term.lower() in c.get('company_name_short', '').lower() or
                search_term.lower() in c.get('company_name_english', '').lower())
        ]
        
        if filtered_customers:
            st.markdown("**검색 결과:**")
            for cust in filtered_customers[:5]:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"{cust.get('company_name_original', 'N/A')}")
                
                with col2:
                    if st.button("✓ 선택", key=f"select_cust_{cust.get('id')}", use_container_width=True):
                        st.session_state['selected_customer_name'] = cust.get('company_name_original', '')
                        st.session_state['selected_customer_id'] = cust.get('id')
                        st.session_state['quotation_mode'] = 'B'  # 모드 B
                        st.rerun()
        else:
            st.warning("검색 결과 없음")
    
    # 선택된 고객 표시
    if st.session_state.get('selected_customer_id') and not st.session_state.get('quotation_id'):
        st.success(f"✅ 선택된 고객: {st.session_state.get('selected_customer_name')}")
        if st.button("❌ 선택 해제", key="clear_customer"):
            st.session_state.pop('selected_customer_name', None)
            st.session_state.pop('selected_customer_id', None)
            st.session_state.pop('quotation_mode', None)
            st.rerun()
    
    st.markdown("---")


def render_customer_section(load_func, save_func, language='KO'):
    """고객 및 프로젝트 정보 입력 섹션 (Form 안에서 실행)"""
    
    st.markdown(f"### 📋 고객 및 프로젝트 정보")
    
    # 현재 모드 표시
    current_mode = st.session_state.get('quotation_mode', None)
    if current_mode == 'A':
        st.info("🔗 모드 A: 견적서 연결 모드 (정보 자동 입력)")
    elif current_mode == 'B':
        st.info("📝 모드 B: 독립 작성 모드 (정보 직접 입력)")
    
    # 고객 정보 입력
    col1, col2 = st.columns(2)
    
    with col1:
        # 고객명 입력
        customer_name = st.text_input(
            f"🔴 고객사 *",
            value=st.session_state.get('selected_customer_name', ''),
            placeholder="고객사 이름을 입력하세요...",
            key="customer_name_input"
        )
        
        customer_id = st.session_state.get('selected_customer_id', None)
        
        if customer_id:
            st.success(f"✅ 고객 연결됨")
        
        # 프로젝트명
        project_name = st.text_input(
            f"🔴 프로젝트명 *",
            value=st.session_state.get('auto_project_name', ''),
            key="project_name"
        )
        
        # 금형번호
        mold_no = st.text_input(
            "금형번호",
            value=st.session_state.get('auto_mold_no', ''),
            key="mold_no"
        )
    
    with col2:
        # 납품처
        delivery_to = st.text_input(
            f"🔴 납품처 *",
            key="delivery_to"
        )
        
        # 부품명
        part_name = st.text_input(
            "부품명",
            value=st.session_state.get('auto_part_name', ''),
            key="part_name"
        )
        
        # YMV 번호
        ymv_no = st.text_input(
            "YMV 번호",
            key="ymv_no"
        )
    
    # 추가 정보
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # 영업담당
        employees = load_func('employees') if load_func else []
        
        if employees:
            sales_employees = [e for e in employees if e.get('role') in ['Manager', 'Admin', 'CEO']]
            
            # 자동 선택된 영업담당자 찾기
            auto_sales_id = st.session_state.get('auto_sales_rep_id')
            default_index = 0
            
            if auto_sales_id:
                for idx, emp in enumerate(sales_employees):
                    if emp.get('id') == auto_sales_id:
                        default_index = idx
                        break
            
            employee_options = [f"{e.get('name', 'N/A')} - {e.get('position', '')}" for e in sales_employees]
            
            selected_employee = st.selectbox(
                f"🔴 영업담당 *",
                employee_options,
                index=default_index,
                key="sales_contact"
            )
            
            sales_contact_id = sales_employees[employee_options.index(selected_employee)].get('id')
        else:
            sales_contact_text = st.text_input(
                f"🔴 영업담당 *",
                key="sales_contact_text"
            )
            sales_contact_id = None
        
        # Resin
        resin = st.text_input(
            "수지",
            value=st.session_state.get('auto_resin', ''),
            key="resin"
        )
    
    with col4:
        # 사출기 TON
        injection_ton = st.number_input(
            "사출기 TON",
            min_value=0,
            step=10,
            key="injection_ton"
        )
        
        # 첨가제
        additive = st.text_input(
            "첨가제",
            key="additive"
        )
    
    # 선택 옵션
    st.markdown("---")
    st.markdown(f"### 🔧 주문 옵션")
    
    col5, col6 = st.columns(2)
    
    with col5:
        color_change = st.radio(
            f"🔴 색상 변경 *",
            ["없음", "있음"],
            horizontal=True,
            key="color_change"
        )
    
    with col6:
        order_type = st.radio(
            f"🔴 주문 타입 *",
            ["SYSTEM", "SEMI", "TOTAL"],
            horizontal=True,
            key="order_type"
        )
    
    # 데이터 반환
    customer_data = {
        'quotation_id': st.session_state.get('quotation_id'),
        'customer_id': customer_id,
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
        'order_type': order_type,
        'quotation_mode': st.session_state.get('quotation_mode', None)
    }
    
    return customer_data


def validate_customer_data(data):
    """필수 입력 검증"""
    required_fields = {
        'customer_name': '고객사',
        'delivery_to': '납품처',
        'project_name': '프로젝트명',
        'sales_contact': '영업담당'
    }
    
    missing_fields = []
    
    for field, label in required_fields.items():
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing_fields.append(label)
    
    if missing_fields:
        return False, f"필수 항목 누락: {', '.join(missing_fields)}"
    
    return True, "OK"
