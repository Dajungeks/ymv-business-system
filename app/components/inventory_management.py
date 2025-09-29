import streamlit as st
from datetime import datetime, date, timedelta

def show_inventory_management(load_func, save_func, update_func, current_user):
    """재고 관리 메인 함수"""
    st.header("📋 재고 관리")
    
    tab1, tab2, tab3 = st.tabs(["📥 입고 관리", "🔍 검수 관리", "📤 출고 관리"])
    
    with tab1:
        render_receiving_management(load_func, save_func, current_user)
    
    with tab2:
        render_quality_inspection(load_func, save_func, update_func, current_user)
    
    with tab3:
        render_shipping_management(load_func, save_func, update_func, current_user)

def render_receiving_management(load_func, save_func, current_user):
    """입고 관리"""
    st.subheader("📥 입고 관리")
    
    # 입고 대상 발주서 조회
    customer_orders = load_func('purchase_orders_to_supplier') or []
    inventory_orders = load_func('purchase_orders_inventory') or []
    
    # 입고 가능한 발주서 필터링 (shipped, received 상태)
    available_orders = []
    
    for order in customer_orders:
        if order.get('status') in ['shipped', 'received']:
            available_orders.append({
                'type': 'customer_order',
                'data': order,
                'display': f"[고객주문] {order.get('po_number', 'N/A')} - {order.get('supplier_name', 'N/A')}"
            })
    
    for order in inventory_orders:
        if order.get('status') in ['shipped', 'received']:
            available_orders.append({
                'type': 'inventory_order',
                'data': order,
                'display': f"[재고보충] {order.get('po_number', 'N/A')} - {order.get('item_name', 'N/A')}"
            })
    
    if not available_orders:
        st.info("입고 처리 가능한 발주서가 없습니다. (shipped 또는 received 상태인 발주서만 입고 처리 가능)")
        return
    
    # 발주서 선택
    selected_order_display = st.selectbox(
        "입고 처리할 발주서 선택:",
        [order['display'] for order in available_orders]
    )
    
    if selected_order_display:
        selected_order = next(order for order in available_orders if order['display'] == selected_order_display)
        order_data = selected_order['data']
        
        # 발주서 정보 표시
        with st.expander("📋 발주서 정보", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**발주서 번호**: {order_data.get('po_number', 'N/A')}")
                st.write(f"**공급업체**: {order_data.get('supplier_name', 'N/A')}")
                if selected_order['type'] == 'customer_order':
                    st.write(f"**상품명**: {order_data.get('item_description', 'N/A')}")
                else:
                    st.write(f"**상품명**: {order_data.get('item_name', 'N/A')}")
            with col2:
                st.write(f"**주문 수량**: {order_data.get('quantity', 'N/A')}")
                st.write(f"**현재 상태**: {order_data.get('status', 'N/A')}")
                st.write(f"**예상 도착일**: {order_data.get('expected_arrival_date', 'N/A')}")
        
        # 입고 처리 폼
        with st.form("receiving_form"):
            st.write("**입고 정보 입력**")
            
            col1, col2 = st.columns(2)
            with col1:
                received_date = st.date_input("입고 날짜", value=date.today())
                received_quantity = st.number_input(
                    "실제 입고 수량", 
                    min_value=1, 
                    value=int(order_data.get('quantity', 1)),
                    max_value=int(order_data.get('quantity', 1))
                )
            
            with col2:
                warehouse_location = st.text_input("창고 위치", placeholder="예: 창고A-구역1-선반3")
                condition_notes = st.text_area("상태 메모", placeholder="상품 상태, 포장 상태 등")
            
            submitted = st.form_submit_button("✅ 입고 처리 완료", use_container_width=True)
            
            if submitted:
                if warehouse_location:
                    # 입고 번호 생성
                    receiving_number = generate_document_number('RCV', save_func)
                    
                    # 입고 데이터 생성
                    receiving_data = {
                        'receiving_number': receiving_number,
                        'po_supplier_id': order_data['id'] if selected_order['type'] == 'customer_order' else None,
                        'po_inventory_id': order_data['id'] if selected_order['type'] == 'inventory_order' else None,
                        'sales_process_id': order_data.get('sales_process_id'),
                        'received_date': received_date,
                        'received_by': current_user['id'],
                        'received_quantity': received_quantity,
                        'warehouse_location': warehouse_location,
                        'condition_notes': condition_notes,
                        'created_at': datetime.now()
                    }
                    
                    # 입고 기록 저장
                    save_func('inventory_receiving', receiving_data)
                    
                    # 발주서 상태 업데이트
                    table_name = 'purchase_orders_to_supplier' if selected_order['type'] == 'customer_order' else 'purchase_orders_inventory'
                    update_purchase_order_status(order_data['id'], 'received', update_func, table_name)
                    
                    st.success(f"✅ 입고 처리가 완료되었습니다! (입고번호: {receiving_number})")
                    st.rerun()
                else:
                    st.error("창고 위치를 입력해주세요.")
    
    # 입고 기록 조회
    st.subheader("📋 최근 입고 기록")
    receivings = load_func('inventory_receiving')
    
    if receivings:
        import pandas as pd
        df = pd.DataFrame(receivings)
        # 최근 10개 기록만 표시
        recent_receivings = df.tail(10) if len(df) > 10 else df
        st.dataframe(recent_receivings, use_container_width=True)
    else:
        st.info("입고 기록이 없습니다.")

def render_quality_inspection(load_func, save_func, update_func, current_user):
    """검수 관리"""
    st.subheader("🔍 검수 관리")
    
    # 검수 대상 입고 기록 조회
    receivings = load_func('inventory_receiving')
    
    if not receivings:
        st.info("검수 대상인 입고 기록이 없습니다.")
        return
    
    # 아직 검수되지 않은 입고 기록 필터링
    inspections = load_func('quality_inspection') or []
    inspected_receiving_ids = [insp.get('receiving_id') for insp in inspections]
    
    pending_receivings = [
        rec for rec in receivings 
        if rec['id'] not in inspected_receiving_ids
    ]
    
    if not pending_receivings:
        st.info("검수 대기 중인 입고 기록이 없습니다.")
    else:
        # 입고 기록 선택
        receiving_options = {
            f"{rec['receiving_number']} - {rec.get('warehouse_location', 'N/A')} (수량: {rec.get('received_quantity', 'N/A')})": rec
            for rec in pending_receivings
        }
        
        selected_receiving_key = st.selectbox(
            "검수할 입고 기록 선택:",
            list(receiving_options.keys())
        )
        
        if selected_receiving_key:
            selected_receiving = receiving_options[selected_receiving_key]
            
            # 입고 정보 표시
            with st.expander("📋 입고 정보", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**입고번호**: {selected_receiving['receiving_number']}")
                    st.write(f"**입고날짜**: {selected_receiving.get('received_date', 'N/A')}")
                    st.write(f"**입고수량**: {selected_receiving.get('received_quantity', 'N/A')}")
                with col2:
                    st.write(f"**창고위치**: {selected_receiving.get('warehouse_location', 'N/A')}")
                    st.write(f"**상태메모**: {selected_receiving.get('condition_notes', 'N/A')}")
            
            # 검수 처리 폼
            with st.form("inspection_form"):
                st.write("**검수 정보 입력**")
                
                col1, col2 = st.columns(2)
                with col1:
                    inspection_date = st.date_input("검수 날짜", value=date.today())
                    inspection_method = st.selectbox(
                        "검수 방법",
                        ["전수검사", "샘플검사", "외관검사", "기능검사"]
                    )
                    total_quantity = st.number_input(
                        "총 검수 수량",
                        min_value=1,
                        value=int(selected_receiving.get('received_quantity', 1)),
                        max_value=int(selected_receiving.get('received_quantity', 1))
                    )
                
                with col2:
                    approved_quantity = st.number_input(
                        "승인 수량",
                        min_value=0,
                        value=int(selected_receiving.get('received_quantity', 1)),
                        max_value=total_quantity
                    )
                    rejected_quantity = st.number_input(
                        "불량 수량",
                        min_value=0,
                        value=0,
                        max_value=total_quantity
                    )
                    approved_for_shipment = st.checkbox("출고 승인", value=True)
                
                inspection_notes = st.text_area("검수 메모", placeholder="검수 결과, 불량 사유 등")
                
                submitted = st.form_submit_button("✅ 검수 완료", use_container_width=True)
                
                if submitted:
                    if approved_quantity + rejected_quantity <= total_quantity:
                        # 검수 번호 생성
                        inspection_number = generate_document_number('QC', save_func)
                        
                        # 검수 데이터 생성
                        inspection_data = {
                            'inspection_number': inspection_number,
                            'receiving_id': selected_receiving['id'],
                            'sales_process_id': selected_receiving.get('sales_process_id'),
                            'inspector_id': current_user['id'],
                            'inspection_date': inspection_date,
                            'inspection_method': inspection_method,
                            'total_quantity': total_quantity,
                            'approved_quantity': approved_quantity,
                            'rejected_quantity': rejected_quantity,
                            'inspection_result': 'approved' if approved_quantity > 0 else 'rejected',
                            'approved_for_shipment': approved_for_shipment,
                            'inspection_notes': inspection_notes,
                            'created_at': datetime.now()
                        }
                        
                        # 검수 기록 저장
                        save_func('quality_inspection', inspection_data)
                        
                        # 영업 프로세스 상태 업데이트 (해당하는 경우)
                        if selected_receiving.get('sales_process_id') and approved_for_shipment:
                            update_func('sales_process', selected_receiving['sales_process_id'], {
                                'process_status': 'received',
                                'updated_at': datetime.now()
                            })
                        
                        st.success(f"✅ 검수가 완료되었습니다! (검수번호: {inspection_number})")
                        st.rerun()
                    else:
                        st.error("승인 수량 + 불량 수량이 총 검수 수량을 초과할 수 없습니다.")
    
    # 검수 기록 조회
    st.subheader("📋 최근 검수 기록")
    inspections = load_func('quality_inspection')
    
    if inspections:
        import pandas as pd
        df = pd.DataFrame(inspections)
        # 최근 10개 기록만 표시
        recent_inspections = df.tail(10) if len(df) > 10 else df
        st.dataframe(recent_inspections, use_container_width=True)
    else:
        st.info("검수 기록이 없습니다.")

def render_shipping_management(load_func, save_func, update_func, current_user):
    """출고 관리"""
    st.subheader("📤 출고 관리")
    
    # 출고 대상 검수 기록 조회 (출고 승인된 것)
    inspections = load_func('quality_inspection')
    
    if not inspections:
        st.info("출고 대상인 검수 기록이 없습니다.")
        return
    
    # 출고 승인된 검수 기록 필터링
    approved_inspections = [
        insp for insp in inspections 
        if insp.get('approved_for_shipment') and insp.get('approved_quantity', 0) > 0
    ]
    
    # 이미 출고된 것 제외
    shipments = load_func('delivery_shipment') or []
    shipped_inspection_ids = [ship.get('inspection_id') for ship in shipments]
    
    pending_inspections = [
        insp for insp in approved_inspections 
        if insp['id'] not in shipped_inspection_ids
    ]
    
    if not pending_inspections:
        st.info("출고 대기 중인 검수 기록이 없습니다.")
    else:
        # 검수 기록 선택
        inspection_options = {
            f"{insp['inspection_number']} - 승인수량: {insp.get('approved_quantity', 'N/A')}": insp
            for insp in pending_inspections
        }
        
        selected_inspection_key = st.selectbox(
            "출고할 검수 기록 선택:",
            list(inspection_options.keys())
        )
        
        if selected_inspection_key:
            selected_inspection = inspection_options[selected_inspection_key]
            
            # 검수 정보 표시
            with st.expander("📋 검수 정보", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**검수번호**: {selected_inspection['inspection_number']}")
                    st.write(f"**검수날짜**: {selected_inspection.get('inspection_date', 'N/A')}")
                    st.write(f"**승인수량**: {selected_inspection.get('approved_quantity', 'N/A')}")
                with col2:
                    st.write(f"**검수결과**: {selected_inspection.get('inspection_result', 'N/A')}")
                    st.write(f"**출고승인**: {'예' if selected_inspection.get('approved_for_shipment') else '아니오'}")
            
            # 출고 처리 폼
            with st.form("shipping_form"):
                st.write("**출고 정보 입력**")
                
                col1, col2 = st.columns(2)
                with col1:
                    shipment_date = st.date_input("출고 날짜", value=date.today())
                    delivery_method = st.selectbox(
                        "배송 방법",
                        ["직접 배송", "택배", "화물", "고객 직접 수령"]
                    )
                    shipment_quantity = st.number_input(
                        "출고 수량",
                        min_value=1,
                        value=int(selected_inspection.get('approved_quantity', 1)),
                        max_value=int(selected_inspection.get('approved_quantity', 1))
                    )
                
                with col2:
                    delivery_address = st.text_area("배송 주소", placeholder="배송지 주소")
                    delivery_contact = st.text_input("수령인 연락처", placeholder="연락처")
                    tracking_number = st.text_input("송장번호", placeholder="택배 송장번호 (선택)")
                
                shipment_notes = st.text_area("출고 메모", placeholder="배송 관련 특이사항")
                
                submitted = st.form_submit_button("✅ 출고 처리 완료", use_container_width=True)
                
                if submitted:
                    if delivery_address or delivery_method == "고객 직접 수령":
                        # 출고 번호 생성
                        shipment_number = generate_document_number('SHIP', save_func)
                        
                        # 출고 데이터 생성
                        shipment_data = {
                            'shipment_number': shipment_number,
                            'sales_process_id': selected_inspection.get('sales_process_id'),
                            'inspection_id': selected_inspection['id'],
                            'shipment_date': shipment_date,
                            'shipped_by': current_user['id'],
                            'shipment_quantity': shipment_quantity,
                            'delivery_address': delivery_address,
                            'delivery_contact': delivery_contact,
                            'delivery_method': delivery_method,
                            'tracking_number': tracking_number,
                            'shipment_status': 'shipped',
                            'shipment_notes': shipment_notes,
                            'created_at': datetime.now()
                        }
                        
                        # 출고 기록 저장
                        save_func('delivery_shipment', shipment_data)
                        
                        # 영업 프로세스 상태 업데이트 (해당하는 경우)
                        if selected_inspection.get('sales_process_id'):
                            update_func('sales_process', selected_inspection['sales_process_id'], {
                                'process_status': 'completed',
                                'updated_at': datetime.now()
                            })
                        
                        st.success(f"✅ 출고 처리가 완료되었습니다! (출고번호: {shipment_number})")
                        st.rerun()
                    else:
                        st.error("배송 주소를 입력해주세요.")
    
    # 출고 기록 조회
    st.subheader("📋 최근 출고 기록")
    shipments = load_func('delivery_shipment')
    
    if shipments:
        import pandas as pd
        df = pd.DataFrame(shipments)
        
        # 출고 상태 업데이트 기능
        st.write("**출고 상태 관리**")
        for shipment in shipments[-5:]:  # 최근 5개만 표시
            with st.expander(f"📦 {shipment['shipment_number']} - {shipment.get('delivery_method', 'N/A')}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**출고날짜**: {shipment.get('shipment_date', 'N/A')}")
                    st.write(f"**배송방법**: {shipment.get('delivery_method', 'N/A')}")
                    st.write(f"**출고수량**: {shipment.get('shipment_quantity', 'N/A')}")
                    st.write(f"**송장번호**: {shipment.get('tracking_number', 'N/A')}")
                
                with col2:
                    st.write(f"**현재상태**: {shipment.get('shipment_status', 'N/A')}")
                    st.write(f"**배송주소**: {shipment.get('delivery_address', 'N/A')}")
                
                with col3:
                    new_status = st.selectbox(
                        "배송 상태:",
                        ["shipped", "in_transit", "delivered", "returned"],
                        index=["shipped", "in_transit", "delivered", "returned"].index(shipment.get('shipment_status', 'shipped')),
                        key=f"ship_status_{shipment['id']}"
                    )
                    
                    if st.button("상태 업데이트", key=f"ship_update_{shipment['id']}"):
                        update_shipment_status(shipment['id'], new_status, update_func)
                        st.success("배송 상태가 업데이트되었습니다!")
                        st.rerun()
        
        # 전체 출고 기록 테이블
        st.write("**전체 출고 기록**")
        recent_shipments = df.tail(10) if len(df) > 10 else df
        st.dataframe(recent_shipments, use_container_width=True)
    else:
        st.info("출고 기록이 없습니다.")

def update_purchase_order_status(po_id, new_status, update_func, table_name):
    """발주서 상태 업데이트"""
    update_func(table_name, po_id, {
        'status': new_status,
        'updated_at': datetime.now()
    })

def update_shipment_status(shipment_id, new_status, update_func):
    """출고 상태 업데이트"""
    update_func('delivery_shipment', shipment_id, {
        'shipment_status': new_status,
        'updated_at': datetime.now()
    })

def generate_document_number(doc_type, save_func):
    """문서 번호 생성"""
    current_year = datetime.now().year
    
    prefixes = {
        'RCV': f"RCV-{current_year}-",    # Receiving
        'QC': f"QC-{current_year}-",      # Quality Control
        'SHIP': f"SHIP-{current_year}-"   # Shipment
    }
    
    prefix = prefixes.get(doc_type, f"{doc_type}-{current_year}-")
    
    # 간단한 순차 번호 생성
    try:
        import random
        next_number = random.randint(1, 9999)
        return f"{prefix}{next_number:04d}"
    except:
        return f"{prefix}0001"