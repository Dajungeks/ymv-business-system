import streamlit as st
from datetime import datetime, date, timedelta

def show_purchase_order_management(load_func, save_func, update_func, current_user):
    """발주 관리 메인 함수"""
    st.header("📦 발주 관리")
    
    # 발주 유형 선택 (코드별 분할 발주 추가)
    purchase_type = st.radio(
        "발주 유형 선택:",
        ["🎯 고객 주문 기반 발주", "📦 재고 보충 발주", "🔧 코드별 분할 발주", "🏠 내부 처리"],
        horizontal=True
    )
    
    if purchase_type == "🎯 고객 주문 기반 발주":
        render_customer_order_based_purchase(load_func, save_func, update_func, current_user)
    elif purchase_type == "📦 재고 보충 발주":
        render_inventory_replenishment_purchase(load_func, save_func, update_func, current_user)
    elif purchase_type == "🔧 코드별 분할 발주":
        render_breakdown_based_purchase(load_func, save_func, update_func, current_user)
    else:  # 내부 처리
        render_all_purchase_orders(load_func, update_func)

def render_breakdown_based_purchase(load_func, save_func, update_func, current_user):
    """코드별 분할 기반 발주"""
    st.subheader("🔧 코드별 분할 발주")
    st.info("영업 프로세스에서 분할된 코드별 아이템의 외주 발주를 처리합니다.")
    
    # 분할된 아이템 중 외주 발주 대상 조회
    breakdowns = load_func('process_item_breakdown') or []
    external_items = [
        item for item in breakdowns 
        if item.get('processing_type') in ['external', 'mixed'] 
        and item.get('external_quantity', 0) > 0
        and item.get('external_order_id') is None  # 아직 발주되지 않은 것
    ]
    
    if not external_items:
        st.info("외주 발주 대상인 분할 아이템이 없습니다.")
        st.write("**외주 발주 조건:**")
        st.write("- 코드별 분할이 완료된 아이템")
        st.write("- 처리 방식이 '외주' 또는 '혼합'인 아이템")
        st.write("- 아직 발주되지 않은 아이템")
        return
    
    st.write(f"📋 **외주 발주 대상**: {len(external_items)}건")
    
    # 아이템별 발주 처리
    for item in external_items:
        render_breakdown_external_order_form(item, load_func, save_func, update_func, current_user)

def render_breakdown_external_order_form(item, load_func, save_func, update_func, current_user):
    """분할 아이템 외주 발주 폼"""
    with st.expander(f"🏭 {item.get('item_code', 'N/A')} - 외주 {item.get('external_quantity', 0)}개", expanded=True):
        
        # 아이템 정보 표시
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**상품 코드**: {item.get('item_code', 'N/A')}")
            st.write(f"**설명**: {item.get('item_description', 'N/A')}")
            st.write(f"**총 수량**: {item.get('quantity', 0)}개")
            st.write(f"**외주 수량**: {item.get('external_quantity', 0)}개")
        
        with col2:
            # 관련 영업 프로세스 정보
            process_id = item.get('sales_process_id')
            if process_id:
                processes = load_func('sales_process') or []
                process = next((p for p in processes if p.get('id') == process_id), None)
                if process:
                    st.write(f"**프로세스**: {process.get('process_number', 'N/A')}")
                    st.write(f"**고객**: {process.get('customer_name', 'N/A')}")
        
        # 발주 폼
        with st.form(f"external_order_{item['id']}"):
            st.write("**공급업체 정보**")
            
            # 기존 공급업체 목록에서 선택 또는 신규 입력
            suppliers = load_func('suppliers') or []
            if suppliers:
                supplier_options = ["신규 입력"] + [f"{s.get('name', 'N/A')} ({s.get('company_name', 'N/A')})" for s in suppliers]
                selected_supplier_option = st.selectbox(
                    "공급업체 선택:",
                    supplier_options,
                    key=f"supplier_option_{item['id']}"
                )
                
                if selected_supplier_option != "신규 입력":
                    # 기존 공급업체 선택
                    selected_supplier = suppliers[supplier_options.index(selected_supplier_option) - 1]
                    supplier_name = selected_supplier.get('name', '')
                    supplier_contact = selected_supplier.get('contact_person', '')
                    supplier_email = selected_supplier.get('email', '')
                    supplier_phone = selected_supplier.get('phone', '')
                    
                    st.write(f"**선택된 공급업체**: {supplier_name}")
                    st.write(f"**담당자**: {supplier_contact}")
                    st.write(f"**연락처**: {supplier_email}, {supplier_phone}")
                else:
                    # 신규 입력
                    col3, col4 = st.columns(2)
                    with col3:
                        supplier_name = st.text_input("공급업체명*", key=f"new_supplier_{item['id']}")
                        supplier_contact = st.text_input("담당자명", key=f"new_contact_{item['id']}")
                    with col4:
                        supplier_email = st.text_input("이메일", key=f"new_email_{item['id']}")
                        supplier_phone = st.text_input("전화번호", key=f"new_phone_{item['id']}")
            else:
                # 공급업체 목록이 없는 경우 직접 입력
                col3, col4 = st.columns(2)
                with col3:
                    supplier_name = st.text_input("공급업체명*", key=f"supplier_{item['id']}")
                    supplier_contact = st.text_input("담당자명", key=f"contact_{item['id']}")
                with col4:
                    supplier_email = st.text_input("이메일", key=f"email_{item['id']}")
                    supplier_phone = st.text_input("전화번호", key=f"phone_{item['id']}")
            
            st.write("**발주 정보**")
            col5, col6 = st.columns(2)
            with col5:
                order_date = st.date_input("발주일", value=date.today(), key=f"order_date_{item['id']}")
                expected_arrival = st.date_input("예상 도착일", value=date.today() + timedelta(days=7), key=f"arrival_{item['id']}")
            
            with col6:
                unit_cost = st.number_input("단가 (USD)", min_value=0.0, format="%.2f", key=f"unit_cost_{item['id']}")
                total_cost = unit_cost * item.get('external_quantity', 0)
                st.write(f"**총 금액**: ${total_cost:.2f}")
            
            payment_terms = st.text_input("결제 조건", value="30일 후 지급", key=f"payment_{item['id']}")
            notes = st.text_area("비고", placeholder="코드별 분할 발주 관련 메모", key=f"notes_{item['id']}")
            
            submitted = st.form_submit_button("📤 외주 발주 등록", type="primary")
            
            if submitted and supplier_name and unit_cost > 0:
                create_breakdown_external_order(
                    item, supplier_name, supplier_contact, supplier_email, 
                    supplier_phone, order_date, expected_arrival, unit_cost, 
                    total_cost, payment_terms, notes, save_func, update_func, current_user
                )
                st.success(f"✅ {item.get('item_code', 'N/A')} 외주 발주가 완료되었습니다!")
                st.rerun()
            elif submitted:
                st.error("공급업체명과 단가를 입력해주세요.")

def create_breakdown_external_order(item, supplier_name, supplier_contact, supplier_email, 
                                   supplier_phone, order_date, expected_arrival, unit_cost, 
                                   total_cost, payment_terms, notes, save_func, update_func, current_user):
    """분할 아이템 외주 발주 생성"""
    # 발주서 번호 생성 (코드별 분할 발주용)
    po_number = generate_document_number('POB', save_func)  # Purchase Order Breakdown
    
    order_data = {
        'po_number': po_number,
        'purchase_type': 'breakdown_external',
        'sales_process_id': item.get('sales_process_id'),
        'breakdown_item_id': item.get('id'),  # 분할 아이템 연결
        'supplier_name': supplier_name,
        'supplier_contact': supplier_contact,
        'supplier_email': supplier_email,
        'supplier_phone': supplier_phone,
        'item_description': f"[코드: {item.get('item_code', 'N/A')}] {item.get('item_description', '')}",
        'quantity': item.get('external_quantity', 0),
        'unit_cost': unit_cost,
        'total_cost': total_cost,
        'order_date': order_date,
        'expected_arrival_date': expected_arrival,
        'payment_terms': payment_terms,
        'status': 'ordered',
        'notes': f"코드별 분할 발주 - {notes}",
        'created_at': datetime.now(),
        'created_by': current_user['id']
    }
    
    # 발주서 저장
    result = save_func('purchase_orders_to_supplier', order_data)
    
    if result:
        # breakdown 아이템에 발주서 ID 연결
        update_func('process_item_breakdown', item['id'], {
            'external_order_id': result.get('id') if isinstance(result, dict) else None,
            'item_status': 'completed',
            'updated_at': datetime.now()
        })

def render_customer_order_based_purchase(load_func, save_func, update_func, current_user):
    """고객 주문 기반 발주"""
    st.subheader("🎯 고객 주문 기반 발주")
    
    # 승인된 영업 프로세스 조회
    processes = load_func('sales_process')
    if not processes:
        st.warning("승인된 영업 프로세스가 없습니다.")
        return
    
    # 발주 대상 프로세스 필터링 (approved 상태)
    approved_processes = [p for p in processes if p.get('process_status') == 'approved']
    
    if not approved_processes:
        st.info("발주 대상인 승인된 프로세스가 없습니다.")
        return
    
    # 프로세스 선택
    process_options = {
        f"{p['process_number']} - {p.get('customer_name', 'N/A')} ({p.get('item_description', 'N/A')})": p
        for p in approved_processes
    }
    
    selected_process_key = st.selectbox(
        "발주할 프로세스 선택:",
        list(process_options.keys())
    )
    
    if selected_process_key:
        selected_process = process_options[selected_process_key]
        
        # 프로세스 정보 표시
        with st.expander("📋 선택된 프로세스 정보", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**프로세스 번호**: {selected_process['process_number']}")
                st.write(f"**고객명**: {selected_process.get('customer_name', 'N/A')}")
                st.write(f"**상품명**: {selected_process.get('item_description', 'N/A')}")
            with col2:
                st.write(f"**수량**: {selected_process.get('quantity', 'N/A')}")
                st.write(f"**금액**: ${selected_process.get('total_amount', 0):,.2f}")
                st.write(f"**예상 배송일**: {selected_process.get('expected_delivery_date', 'N/A')}")
        
        # 발주 방식 선택
        st.subheader("📦 발주 방식 선택")
        order_method = st.radio(
            "발주 방식:",
            ["🏠 내부 재고 처리", "🏭 외주 발주"],
            horizontal=True
        )
        
        if order_method == "🏠 내부 재고 처리":
            process_internal_stock(selected_process, current_user, save_func, update_func)
        else:  # 외주 발주
            show_customer_order_external_form(selected_process, current_user, save_func, update_func)

def process_internal_stock(process, current_user, save_func, update_func):
    """내부 재고 처리"""
    st.subheader("🏠 내부 재고 처리")
    
    with st.form("internal_stock_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            warehouse_location = st.text_input("창고 위치", placeholder="예: 창고A-구역1")
            processed_quantity = st.number_input("처리 수량", min_value=1, value=int(process.get('quantity', 1)))
        
        with col2:
            processing_date = st.date_input("처리 날짜", value=date.today())
            notes = st.text_area("비고", placeholder="내부 재고 처리 관련 메모")
        
        submitted = st.form_submit_button("✅ 내부 재고 처리 완료", use_container_width=True)
        
        if submitted:
            if warehouse_location:
                # 내부 처리 기록 저장
                internal_data = {
                    'sales_process_id': process['id'],
                    'processing_type': 'internal_stock',
                    'warehouse_location': warehouse_location,
                    'processed_quantity': processed_quantity,
                    'processing_date': processing_date,
                    'processed_by': current_user['id'],
                    'notes': notes,
                    'created_at': datetime.now()
                }
                
                # 내부 처리 테이블에 저장
                save_func('internal_processing', internal_data)
                
                # 영업 프로세스 상태 업데이트
                update_func('sales_process', process['id'], {
                    'process_status': 'internal_processed',
                    'updated_at': datetime.now()
                })
                
                st.success("✅ 내부 재고 처리가 완료되었습니다!")
                st.rerun()
            else:
                st.error("창고 위치를 입력해주세요.")

def show_customer_order_external_form(process, current_user, save_func, update_func):
    """외주 발주 폼"""
    st.subheader("🏭 외주 발주")
    
    with st.form("external_order_form"):
        st.write("**공급업체 정보**")
        col1, col2 = st.columns(2)
        
        with col1:
            supplier_name = st.text_input("공급업체명*", placeholder="공급업체 이름")
            supplier_contact = st.text_input("담당자명", placeholder="담당자 이름")
        
        with col2:
            supplier_email = st.text_input("이메일", placeholder="담당자 이메일")
            supplier_phone = st.text_input("전화번호", placeholder="담당자 전화번호")
        
        st.write("**발주 정보**")
        col3, col4 = st.columns(2)
        
        with col3:
            order_date = st.date_input("발주 날짜", value=date.today())
            expected_arrival = st.date_input("예상 도착일", value=date.today() + timedelta(days=7))
        
        with col4:
            unit_cost = st.number_input("단가 (USD)", min_value=0.0, format="%.2f")
            total_cost = st.number_input("총 금액 (USD)", min_value=0.0, format="%.2f")
        
        payment_terms = st.text_input("결제 조건", placeholder="예: 30일 후 지급")
        notes = st.text_area("비고", placeholder="발주 관련 특이사항")
        
        submitted = st.form_submit_button("📤 외주 발주 등록", use_container_width=True)
        
        if submitted:
            if supplier_name and unit_cost > 0:
                create_customer_order_external_purchase(
                    process, supplier_name, supplier_contact, supplier_email, 
                    supplier_phone, order_date, expected_arrival, unit_cost, 
                    total_cost, payment_terms, notes, current_user, save_func, update_func
                )
            else:
                st.error("공급업체명과 단가를 입력해주세요.")

def create_customer_order_external_purchase(process, supplier_name, supplier_contact, supplier_email, 
                                          supplier_phone, order_date, expected_arrival, unit_cost, 
                                          total_cost, payment_terms, notes, current_user, save_func, update_func):
    """고객 주문 외주 발주 생성"""
    # 발주서 번호 생성
    po_number = generate_document_number('POC', save_func)
    
    purchase_data = {
        'po_number': po_number,
        'sales_process_id': process['id'],
        'supplier_name': supplier_name,
        'supplier_contact': supplier_contact,
        'supplier_email': supplier_email,
        'supplier_phone': supplier_phone,
        'item_description': process.get('item_description', ''),
        'quantity': process.get('quantity', 1),
        'unit_cost': unit_cost,
        'total_cost': total_cost,
        'order_date': order_date,
        'expected_arrival_date': expected_arrival,
        'payment_terms': payment_terms,
        'status': 'ordered',
        'notes': notes,
        'created_at': datetime.now(),
        'created_by': current_user['id']
    }
    
    # 발주서 저장
    save_func('purchase_orders_to_supplier', purchase_data)
    
    # 영업 프로세스 상태 업데이트
    update_func('sales_process', process['id'], {
        'process_status': 'external_ordered',
        'updated_at': datetime.now()
    })
    
    st.success(f"✅ 발주서 {po_number}가 등록되었습니다!")
    st.rerun()

def render_inventory_replenishment_purchase(load_func, save_func, update_func, current_user):
    """재고 보충 발주"""
    st.subheader("📦 재고 보충 발주")
    st.info("영업 프로세스와 무관한 재고 확보를 위한 발주입니다.")
    
    with st.form("inventory_purchase_form"):
        st.write("**상품 정보**")
        col1, col2 = st.columns(2)
        
        with col1:
            item_code = st.text_input("상품 코드", placeholder="예: ITEM-001")
            item_name = st.text_input("상품명*", placeholder="상품 이름")
            category = st.text_input("카테고리", placeholder="예: 전자부품")
        
        with col2:
            item_description = st.text_area("상품 설명", placeholder="상품 상세 설명")
        
        st.write("**공급업체 정보**")
        col3, col4 = st.columns(2)
        
        with col3:
            supplier_name = st.text_input("공급업체명*", placeholder="공급업체 이름")
            supplier_contact = st.text_input("담당자명", placeholder="담당자 이름")
        
        with col4:
            supplier_email = st.text_input("이메일", placeholder="담당자 이메일")
            supplier_phone = st.text_input("전화번호", placeholder="담당자 전화번호")
        
        st.write("**발주 정보**")
        col5, col6 = st.columns(2)
        
        with col5:
            order_date = st.date_input("발주 날짜", value=date.today())
            expected_arrival = st.date_input("예상 도착일", value=date.today() + timedelta(days=7))
            quantity = st.number_input("발주 수량", min_value=1, value=1)
        
        with col6:
            unit_cost = st.number_input("단가 (USD)", min_value=0.0, format="%.2f")
            total_cost = st.number_input("총 금액 (USD)", min_value=0.0, format="%.2f")
            currency = st.selectbox("통화", ["USD", "VND"], index=0)
        
        st.write("**재고 관리 정보**")
        col7, col8 = st.columns(2)
        
        with col7:
            target_warehouse = st.text_input("목표 창고", placeholder="예: 창고A")
            min_stock_level = st.number_input("최소 재고 수준", min_value=0, value=10)
        
        with col8:
            reorder_point = st.number_input("재주문 포인트", min_value=0, value=20)
            purchase_reason = st.text_input("발주 사유", placeholder="예: 재고 부족")
        
        payment_terms = st.text_input("결제 조건", placeholder="예: 30일 후 지급")
        notes = st.text_area("비고", placeholder="발주 관련 특이사항")
        
        submitted = st.form_submit_button("📦 재고 보충 발주 등록", use_container_width=True)
        
        if submitted:
            if item_name and supplier_name and quantity > 0 and unit_cost > 0:
                create_inventory_replenishment_order(
                    item_code, item_name, item_description, category,
                    supplier_name, supplier_contact, supplier_email, supplier_phone,
                    order_date, expected_arrival, quantity, unit_cost, total_cost,
                    currency, payment_terms, target_warehouse, min_stock_level,
                    reorder_point, purchase_reason, notes, current_user, save_func
                )
            else:
                st.error("필수 항목(상품명, 공급업체명, 수량, 단가)을 모두 입력해주세요.")

def create_inventory_replenishment_order(item_code, item_name, item_description, category,
                                       supplier_name, supplier_contact, supplier_email, supplier_phone,
                                       order_date, expected_arrival, quantity, unit_cost, total_cost,
                                       currency, payment_terms, target_warehouse, min_stock_level,
                                       reorder_point, purchase_reason, notes, current_user, save_func):
    """재고 보충 발주 생성"""
    # 발주서 번호 생성
    po_number = generate_document_number('POI', save_func)
    
    inventory_order_data = {
        'po_number': po_number,
        'purchase_type': 'inventory_replenishment',
        'sales_process_id': None,
        'item_code': item_code,
        'item_name': item_name,
        'item_description': item_description,
        'category': category,
        'supplier_name': supplier_name,
        'supplier_contact': supplier_contact,
        'supplier_email': supplier_email,
        'supplier_phone': supplier_phone,
        'order_date': order_date,
        'expected_arrival_date': expected_arrival,
        'quantity': quantity,
        'unit_cost': unit_cost,
        'total_cost': total_cost,
        'currency': currency,
        'payment_terms': payment_terms,
        'status': 'ordered',
        'target_warehouse': target_warehouse,
        'min_stock_level': min_stock_level,
        'reorder_point': reorder_point,
        'purchase_reason': purchase_reason,
        'notes': notes,
        'created_at': datetime.now(),
        'created_by': current_user['id']
    }
    
    # 재고 보충 발주 저장
    save_func('purchase_orders_inventory', inventory_order_data)
    
    st.success(f"✅ 재고 보충 발주서 {po_number}가 등록되었습니다!")
    st.rerun()

def render_all_purchase_orders(load_func, update_func):
    """모든 발주서 조회"""
    st.subheader("📋 발주서 현황")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 고객 주문 발주", "📦 재고 보충 발주", "🔧 코드별 분할 발주", "🏠 내부 처리"])
    
    with tab1:
        render_customer_order_purchases(load_func, update_func)
    
    with tab2:
        render_inventory_replenishment_purchases(load_func, update_func)
    
    with tab3:
        render_breakdown_order_purchases(load_func, update_func)
    
    with tab4:
        render_internal_processings(load_func)

def render_breakdown_order_purchases(load_func, update_func):
    """코드별 분할 발주 목록"""
    st.subheader("🔧 코드별 분할 발주 현황")
    
    # 코드별 분할 발주만 필터링
    orders = load_func('purchase_orders_to_supplier') or []
    breakdown_orders = [order for order in orders if order.get('purchase_type') == 'breakdown_external']
    
    if breakdown_orders:
        st.write(f"**총 {len(breakdown_orders)}건의 코드별 분할 발주**")
        
        for order in breakdown_orders:
            with st.expander(f"📋 {order.get('po_number', 'N/A')} - {order.get('supplier_name', 'N/A')}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**발주번호**: {order.get('po_number', 'N/A')}")
                    st.write(f"**공급업체**: {order.get('supplier_name', 'N/A')}")
                    st.write(f"**상품**: {order.get('item_description', 'N/A')}")
                    st.write(f"**수량**: {order.get('quantity', 'N/A')}")
                    st.write(f"**총 금액**: ${order.get('total_cost', 0):,.2f}")
                
                with col2:
                    st.write(f"**현재 상태**: {order.get('status', 'N/A')}")
                    st.write(f"**발주일**: {order.get('order_date', 'N/A')}")
                    st.write(f"**예상 도착일**: {order.get('expected_arrival_date', 'N/A')}")
                    st.write(f"**영업 프로세스 ID**: {order.get('sales_process_id', 'N/A')}")
                
                with col3:
                    new_status = st.selectbox(
                        "상태 변경:",
                        ["ordered", "confirmed", "shipped", "received", "completed"],
                        index=["ordered", "confirmed", "shipped", "received", "completed"].index(order.get('status', 'ordered')),
                        key=f"breakdown_status_{order['id']}"
                    )
                    
                    if st.button("상태 업데이트", key=f"breakdown_update_{order['id']}"):
                        update_purchase_order_status(order['id'], new_status, update_func)
                        st.success("상태가 업데이트되었습니다!")
                        st.rerun()
    else:
        st.info("등록된 코드별 분할 발주가 없습니다.")

def render_customer_order_purchases(load_func, update_func):
    """고객 주문 발주 목록"""
    orders = load_func('purchase_orders_to_supplier')
    # 일반 고객 주문 발주만 표시 (코드별 분할 발주 제외)
    customer_orders = [order for order in orders if order.get('purchase_type') != 'breakdown_external']
    
    if customer_orders:
        import pandas as pd
        df = pd.DataFrame(customer_orders)
        
        # 상태 업데이트 기능
        for idx, order in enumerate(customer_orders):
            with st.expander(f"📋 {order['po_number']} - {order.get('supplier_name', 'N/A')}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**공급업체**: {order.get('supplier_name', 'N/A')}")
                    st.write(f"**상품**: {order.get('item_description', 'N/A')}")
                    st.write(f"**수량**: {order.get('quantity', 'N/A')}")
                    st.write(f"**총 금액**: ${order.get('total_cost', 0):,.2f}")
                
                with col2:
                    st.write(f"**현재 상태**: {order.get('status', 'N/A')}")
                    st.write(f"**발주일**: {order.get('order_date', 'N/A')}")
                    st.write(f"**예상 도착일**: {order.get('expected_arrival_date', 'N/A')}")
                
                with col3:
                    new_status = st.selectbox(
                        "상태 변경:",
                        ["ordered", "confirmed", "shipped", "received", "completed"],
                        index=["ordered", "confirmed", "shipped", "received", "completed"].index(order.get('status', 'ordered')),
                        key=f"status_{order['id']}"
                    )
                    
                    if st.button("상태 업데이트", key=f"update_{order['id']}"):
                        update_purchase_order_status(order['id'], new_status, update_func)
                        st.success("상태가 업데이트되었습니다!")
                        st.rerun()
    else:
        st.info("등록된 고객 주문 발주가 없습니다.")

def render_inventory_replenishment_purchases(load_func, update_func):
    """재고 보충 발주 목록"""
    orders = load_func('purchase_orders_inventory')
    
    if orders:
        import pandas as pd
        df = pd.DataFrame(orders)
        
        # 상태 업데이트 기능
        for idx, order in enumerate(orders):
            with st.expander(f"📦 {order['po_number']} - {order.get('item_name', 'N/A')}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**상품명**: {order.get('item_name', 'N/A')}")
                    st.write(f"**공급업체**: {order.get('supplier_name', 'N/A')}")
                    st.write(f"**수량**: {order.get('quantity', 'N/A')}")
                    st.write(f"**총 금액**: {order.get('total_cost', 0):,.2f} {order.get('currency', 'USD')}")
                
                with col2:
                    st.write(f"**현재 상태**: {order.get('status', 'N/A')}")
                    st.write(f"**발주일**: {order.get('order_date', 'N/A')}")
                    st.write(f"**예상 도착일**: {order.get('expected_arrival_date', 'N/A')}")
                    st.write(f"**목표 창고**: {order.get('target_warehouse', 'N/A')}")
                
                with col3:
                    new_status = st.selectbox(
                        "상태 변경:",
                        ["ordered", "confirmed", "shipped", "received", "completed"],
                        index=["ordered", "confirmed", "shipped", "received", "completed"].index(order.get('status', 'ordered')),
                        key=f"inv_status_{order['id']}"
                    )
                    
                    if st.button("상태 업데이트", key=f"inv_update_{order['id']}"):
                        update_inventory_order_status(order['id'], new_status, update_func)
                        st.success("상태가 업데이트되었습니다!")
                        st.rerun()
    else:
        st.info("등록된 재고 보충 발주가 없습니다.")

def render_internal_processings(load_func):
    """내부 처리 목록"""
    processings = load_func('internal_processing')
    
    if processings:
        import pandas as pd
        df = pd.DataFrame(processings)
        
        st.write("**내부 재고 처리 현황**")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("내부 재고 처리 기록이 없습니다.")

def update_purchase_order_status(po_id, new_status, update_func):
    """고객 주문 발주 상태 업데이트"""
    update_func('purchase_orders_to_supplier', po_id, {
        'status': new_status,
        'updated_at': datetime.now()
    })

def update_inventory_order_status(po_id, new_status, update_func):
    """재고 보충 발주 상태 업데이트"""
    update_func('purchase_orders_inventory', po_id, {
        'status': new_status,
        'updated_at': datetime.now()
    })

def generate_document_number(doc_type, save_func):
    """문서 번호 생성"""
    current_year = datetime.now().year
    
    if doc_type == 'POC':  # Purchase Order Customer
        prefix = f"POC-{current_year}-"
        table_name = 'purchase_orders_to_supplier'
    elif doc_type == 'POI':  # Purchase Order Inventory
        prefix = f"POI-{current_year}-"
        table_name = 'purchase_orders_inventory'
    elif doc_type == 'POB':  # Purchase Order Breakdown
        prefix = f"POB-{current_year}-"
        table_name = 'purchase_orders_to_supplier'
    else:
        prefix = f"{doc_type}-{current_year}-"
        table_name = 'purchase_orders_to_supplier'
    
    # 기존 번호 조회하여 다음 번호 생성
    try:
        # 간단한 순차 번호 생성 (실제로는 DB에서 MAX 값을 조회해야 함)
        import random
        next_number = random.randint(1, 9999)
        return f"{prefix}{next_number:04d}"
    except:
        return f"{prefix}0001"