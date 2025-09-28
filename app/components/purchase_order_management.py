import streamlit as st
from datetime import datetime, date, timedelta

def show_purchase_order_management(load_func, save_func, update_func, current_user):
    """발주 관리 - 고객 주문 발주 vs 재고 보충 발주"""
    
    st.subheader("📦 발주 관리")
    
    # 발주 유형 선택
    purchase_type = st.radio(
        "발주 유형 선택",
        ["고객 주문 기반 발주", "재고 보충 발주"],
        horizontal=True
    )
    
    if purchase_type == "고객 주문 기반 발주":
        render_customer_order_based_purchase(load_func, save_func, update_func, current_user)
    else:
        render_inventory_replenishment_purchase(load_func, save_func, update_func, current_user)
    
    # 전체 발주서 목록
    st.divider()
    render_all_purchase_orders(load_func, update_func)

def render_customer_order_based_purchase(load_func, save_func, update_func, current_user):
    """고객 주문 기반 발주 처리"""
    
    st.write("### 🎯 고객 주문 기반 발주")
    
    # 발주 처리 대기 중인 영업 프로세스 로드
    processes = load_func("sales_process")
    
    if not processes:
        st.info("처리할 영업 프로세스가 없습니다.")
        return
    
    # 발주 처리가 필요한 프로세스 필터링
    pending_processes = [p for p in processes if p.get('process_status') in ['approved', 'quotation']]
    
    if not pending_processes:
        st.info("발주 처리 대기 중인 프로세스가 없습니다.")
        return
    
    st.write(f"📋 발주 처리 대기: **{len(pending_processes)}건**")
    
    # 프로세스별 발주 처리 방식 선택
    for process in pending_processes:
        with st.expander(f"🔄 {process.get('process_number', 'N/A')} - {process.get('customer_company', 'N/A')}", expanded=True):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**고객사**: {process.get('customer_company', 'N/A')}")
                st.write(f"**상품**: {process.get('item_description', 'N/A')}")
                st.write(f"**수량**: {process.get('quantity', 0):,}개")
                st.write(f"**금액**: {float(process.get('total_amount', 0)):,.0f} VND")
            
            with col2:
                # 발주 처리 방식 선택
                processing_method = st.radio(
                    "처리 방식",
                    ["내부 재고 처리", "외주 발주"],
                    key=f"method_{process['id']}"
                )
                
                if processing_method == "내부 재고 처리":
                    if st.button("재고 처리", key=f"internal_{process['id']}", type="primary"):
                        process_internal_stock(process, current_user, save_func, update_func)
                
                elif processing_method == "외주 발주":
                    if st.button("외주 발주", key=f"external_{process['id']}", type="secondary"):
                        show_customer_order_external_form(process, current_user, save_func, update_func)

def render_inventory_replenishment_purchase(load_func, save_func, update_func, current_user):
    """재고 보충 발주"""
    
    st.write("### 📦 재고 보충 발주")
    st.caption("영업 프로세스와 무관한 재고 확보를 위한 발주")
    
    with st.form("inventory_replenishment_order"):
        st.subheader("📝 재고 보충 발주 생성")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 상품 정보
            item_code = st.text_input("상품 코드")
            item_name = st.text_input("상품명 *")
            item_description = st.text_area("상품 설명")
            category = st.selectbox("카테고리", ["원자재", "부품", "완제품", "소모품", "기타"])
            
            # 공급업체 정보
            supplier_name = st.text_input("공급업체명 *")
            supplier_contact = st.text_input("담당자")
            supplier_email = st.text_input("이메일")
            supplier_phone = st.text_input("전화번호")
        
        with col2:
            # 발주 정보
            order_date = st.date_input("발주일", value=date.today())
            expected_arrival = st.date_input("예상 입고일", value=date.today() + timedelta(days=14))
            
            quantity = st.number_input("발주 수량 *", min_value=1, value=1)
            unit_cost = st.number_input("단가 (USD) *", min_value=0.0, step=0.01)
            total_cost = unit_cost * quantity
            
            currency = st.selectbox("통화", ["USD", "VND", "EUR", "CNY"])
            payment_terms = st.text_input("결제 조건", value="NET 30")
            
            # 재고 관리 정보
            target_warehouse = st.selectbox("입고 예정 창고", ["창고A", "창고B", "창고C", "임시창고"])
            min_stock_level = st.number_input("최소 재고 수준", min_value=0, value=10)
            reorder_point = st.number_input("재주문점", min_value=0, value=20)
        
        st.write(f"**총 발주 금액**: {total_cost:,.2f} {currency}")
        
        # 발주 사유 및 메모
        purchase_reason = st.selectbox(
            "발주 사유",
            ["재고 부족", "예상 수요 증가", "안전 재고 확보", "신규 상품 도입", "계절성 준비", "기타"]
        )
        notes = st.text_area("발주 메모", placeholder="특별 요구사항, 품질 기준 등...")
        
        if st.form_submit_button("📦 재고 보충 발주 생성", type="primary"):
            if item_name and supplier_name and quantity > 0 and unit_cost > 0:
                create_inventory_replenishment_order(
                    item_code, item_name, item_description, category,
                    supplier_name, supplier_contact, supplier_email, supplier_phone,
                    order_date, expected_arrival, quantity, unit_cost, total_cost,
                    currency, payment_terms, target_warehouse, min_stock_level,
                    reorder_point, purchase_reason, notes, current_user, save_func
                )
            else:
                st.error("필수 항목을 모두 입력해주세요.")

def create_inventory_replenishment_order(item_code, item_name, item_description, category,
                                      supplier_name, supplier_contact, supplier_email, supplier_phone,
                                      order_date, expected_arrival, quantity, unit_cost, total_cost,
                                      currency, payment_terms, target_warehouse, min_stock_level,
                                      reorder_point, purchase_reason, notes, current_user, save_func):
    """재고 보충 발주서 생성"""
    
    try:
        # 발주서 번호 생성
        po_number = generate_document_number('po_inventory', save_func)
        
        # 발주서 데이터
        po_data = {
            'po_number': po_number,
            'purchase_type': 'inventory_replenishment',
            'sales_process_id': None,  # 재고 보충은 영업 프로세스와 무관
            
            # 상품 정보
            'item_code': item_code,
            'item_name': item_name,
            'item_description': item_description,
            'category': category,
            
            # 공급업체 정보
            'supplier_name': supplier_name,
            'supplier_contact': supplier_contact,
            'supplier_email': supplier_email,
            'supplier_phone': supplier_phone,
            
            # 발주 정보
            'order_date': order_date.isoformat(),
            'expected_arrival_date': expected_arrival.isoformat(),
            'quantity': quantity,
            'unit_cost': unit_cost,
            'total_cost': total_cost,
            'currency': currency,
            'payment_terms': payment_terms,
            'status': 'ordered',
            
            # 재고 관리 정보
            'target_warehouse': target_warehouse,
            'min_stock_level': min_stock_level,
            'reorder_point': reorder_point,
            'purchase_reason': purchase_reason,
            'notes': notes,
            
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'created_by': current_user['id']
        }
        
        # 발주서 저장
        save_func("purchase_orders_inventory", po_data)
        
        st.success(f"✅ 재고 보충 발주서 생성 완료: {po_number}")
        st.rerun()
        
    except Exception as e:
        st.error(f"재고 보충 발주서 생성 중 오류: {str(e)}")

def show_customer_order_external_form(process, current_user, save_func, update_func):
    """고객 주문 기반 외주 발주 폼"""
    
    with st.form(f"external_form_{process['id']}"):
        st.subheader(f"🏭 외주 발주 - {process.get('process_number')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            supplier_name = st.text_input("공급업체명 *")
            supplier_contact = st.text_input("담당자")
            supplier_email = st.text_input("이메일")
            supplier_phone = st.text_input("전화번호")
        
        with col2:
            order_date = st.date_input("발주일", value=date.today())
            expected_arrival = st.date_input("예상 입고일", value=date.today() + timedelta(days=14))
            unit_cost = st.number_input("단가 (USD)", min_value=0.0, step=0.01)
            payment_terms = st.text_input("결제 조건", value="NET 30")
        
        quantity = process.get('quantity', 1)
        total_cost = unit_cost * quantity
        
        st.write(f"**수량**: {quantity:,}개")
        st.write(f"**총 발주 금액**: ${total_cost:,.2f} USD")
        
        notes = st.text_area("발주 메모")
        
        if st.form_submit_button("🏭 외주 발주 생성"):
            if supplier_name and unit_cost > 0:
                create_customer_order_external_purchase(
                    process, supplier_name, supplier_contact, supplier_email, 
                    supplier_phone, order_date, expected_arrival, unit_cost, 
                    total_cost, payment_terms, notes, current_user, save_func, update_func
                )
            else:
                st.error("필수 항목을 모두 입력해주세요.")

def create_customer_order_external_purchase(process, supplier_name, supplier_contact, supplier_email,
                                          supplier_phone, order_date, expected_arrival, unit_cost,
                                          total_cost, payment_terms, notes, current_user, save_func, update_func):
    """고객 주문 기반 외주 발주서 생성"""
    
    try:
        # 발주서 번호 생성
        po_number = generate_document_number('po_customer', save_func)
        
        # 발주서 데이터
        po_data = {
            'po_number': po_number,
            'purchase_type': 'customer_order',
            'sales_process_id': process['id'],
            'supplier_name': supplier_name,
            'supplier_contact': supplier_contact,
            'supplier_email': supplier_email,
            'supplier_phone': supplier_phone,
            'order_date': order_date.isoformat(),
            'expected_arrival_date': expected_arrival.isoformat(),
            'item_description': process.get('item_description', ''),
            'quantity': process.get('quantity', 0),
            'unit_cost': unit_cost,
            'total_cost': total_cost,
            'currency': 'USD',
            'payment_terms': payment_terms,
            'status': 'ordered',
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 발주서 저장
        save_func("purchase_orders_to_supplier", po_data)
        
        # 영업 프로세스 상태 업데이트
        update_func("sales_process", {"process_status": "external_ordered"}, process['id'])
        
        st.success(f"✅ 외주 발주서 생성 완료: {po_number}")
        st.rerun()
        
    except Exception as e:
        st.error(f"발주서 생성 중 오류: {str(e)}")

def process_internal_stock(process, current_user, save_func, update_func):
    """내부 재고로 처리"""
    
    with st.form(f"internal_form_{process['id']}"):
        st.subheader(f"📦 내부 재고 처리 - {process.get('process_number')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            warehouse_location = st.selectbox("출고 창고", ["창고A", "창고B", "창고C"])
            processing_date = st.date_input("처리일", value=date.today())
            
        with col2:
            available_quantity = st.number_input("가용 재고", min_value=0, value=process.get('quantity', 0))
            notes = st.text_area("처리 메모", placeholder="재고 위치, 특이사항 등...")
        
        if st.form_submit_button("📦 내부 재고 처리 완료"):
            try:
                # 내부 처리 기록 생성
                internal_data = {
                    'sales_process_id': process['id'],
                    'processing_type': 'internal_stock',
                    'warehouse_location': warehouse_location,
                    'processed_quantity': available_quantity,
                    'processing_date': processing_date.isoformat(),
                    'processed_by': current_user['id'],
                    'notes': notes,
                    'created_at': datetime.now().isoformat()
                }
                
                # 내부 처리 기록 저장
                save_func("internal_processing", internal_data)
                
                # 영업 프로세스 상태 업데이트
                update_func("sales_process", {"process_status": "internal_processed"}, process['id'])
                
                st.success(f"✅ 내부 재고 처리 완료: {process.get('process_number')}")
                st.rerun()
                
            except Exception as e:
                st.error(f"내부 처리 중 오류: {str(e)}")

def render_all_purchase_orders(load_func, update_func):
    """전체 발주서 목록"""
    
    st.write("### 📋 전체 발주 내역")
    
    # 탭으로 발주 유형별 분리
    tab1, tab2, tab3 = st.tabs(["🎯 고객 주문 발주", "📦 재고 보충 발주", "🏠 내부 처리"])
    
    with tab1:
        render_customer_order_purchases(load_func, update_func)
    
    with tab2:
        render_inventory_replenishment_purchases(load_func, update_func)
    
    with tab3:
        render_internal_processings(load_func)

def render_customer_order_purchases(load_func, update_func):
    """고객 주문 기반 발주 목록"""
    
    try:
        purchase_orders = load_func("purchase_orders_to_supplier")
        
        if not purchase_orders:
            st.info("고객 주문 기반 발주서가 없습니다.")
        else:
            for po in purchase_orders:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{po.get('po_number', 'N/A')}**")
                        st.write(f"공급업체: {po.get('supplier_name', 'N/A')}")
                    
                    with col2:
                        st.write(f"품목: {po.get('item_description', 'N/A')[:20]}...")
                        st.write(f"수량: {po.get('quantity', 0):,}개")
                    
                    with col3:
                        amount = float(po.get('total_cost', 0))
                        currency = po.get('currency', 'USD')
                        st.write(f"**{amount:,.2f} {currency}**")
                        
                        status = po.get('status', 'unknown')
                        status_colors = {
                            'ordered': '🟡 발주완료',
                            'shipped': '🔵 배송중',
                            'received': '🟢 입고완료',
                            'cancelled': '🔴 취소됨'
                        }
                        st.write(status_colors.get(status, f"⚪ {status}"))
                    
                    with col4:
                        if status == 'ordered':
                            if st.button("입고 처리", key=f"receive_customer_{po['id']}"):
                                update_purchase_order_status(po['id'], 'received', update_func)
                    
                    st.divider()
        
    except Exception as e:
        st.error(f"고객 주문 발주 목록 로드 중 오류: {str(e)}")

def render_inventory_replenishment_purchases(load_func, update_func):
    """재고 보충 발주 목록"""
    
    try:
        inventory_orders = load_func("purchase_orders_inventory")
        
        if not inventory_orders:
            st.info("재고 보충 발주서가 없습니다.")
        else:
            for po in inventory_orders:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{po.get('po_number', 'N/A')}**")
                        st.write(f"공급업체: {po.get('supplier_name', 'N/A')}")
                        st.write(f"사유: {po.get('purchase_reason', 'N/A')}")
                    
                    with col2:
                        st.write(f"상품: {po.get('item_name', 'N/A')}")
                        st.write(f"카테고리: {po.get('category', 'N/A')}")
                        st.write(f"수량: {po.get('quantity', 0):,}개")
                    
                    with col3:
                        amount = float(po.get('total_cost', 0))
                        currency = po.get('currency', 'USD')
                        st.write(f"**{amount:,.2f} {currency}**")
                        st.write(f"입고창고: {po.get('target_warehouse', 'N/A')}")
                        
                        status = po.get('status', 'unknown')
                        status_colors = {
                            'ordered': '🟡 발주완료',
                            'shipped': '🔵 배송중',
                            'received': '🟢 입고완료',
                            'cancelled': '🔴 취소됨'
                        }
                        st.write(status_colors.get(status, f"⚪ {status}"))
                    
                    with col4:
                        if status == 'ordered':
                            if st.button("입고 처리", key=f"receive_inventory_{po['id']}"):
                                update_inventory_order_status(po['id'], 'received', update_func)
                    
                    st.divider()
        
    except Exception as e:
        st.error(f"재고 보충 발주 목록 로드 중 오류: {str(e)}")

def render_internal_processings(load_func):
    """내부 처리 목록"""
    
    try:
        internal_processings = load_func("internal_processing")
        
        if not internal_processings:
            st.info("내부 처리 내역이 없습니다.")
        else:
            for internal in internal_processings:
                with st.container():
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**영업 프로세스 ID**: {internal.get('sales_process_id', 'N/A')}")
                        st.write(f"**처리일**: {internal.get('processing_date', 'N/A')}")
                        st.write(f"**창고**: {internal.get('warehouse_location', 'N/A')}")
                    
                    with col2:
                        st.write(f"**처리 수량**: {internal.get('processed_quantity', 0):,}개")
                        st.write(f"**담당자**: {internal.get('processed_by', 'N/A')}")
                        if internal.get('notes'):
                            st.write(f"**메모**: {internal.get('notes')}")
                    
                    st.divider()
    
    except Exception as e:
        st.error(f"내부 처리 목록 로드 중 오류: {str(e)}")

def update_purchase_order_status(po_id, new_status, update_func):
    """고객 주문 발주서 상태 업데이트"""
    try:
        update_func("purchase_orders_to_supplier", {"status": new_status}, po_id)
        st.success(f"상태가 {new_status}로 업데이트되었습니다.")
        st.rerun()
    except Exception as e:
        st.error(f"상태 업데이트 중 오류: {str(e)}")

def update_inventory_order_status(po_id, new_status, update_func):
    """재고 보충 발주서 상태 업데이트"""
    try:
        update_func("purchase_orders_inventory", {"status": new_status}, po_id)
        st.success(f"상태가 {new_status}로 업데이트되었습니다.")
        st.rerun()
    except Exception as e:
        st.error(f"상태 업데이트 중 오류: {str(e)}")

def generate_document_number(doc_type, save_func):
    """동적 문서 번호 생성"""
    
    current_year = datetime.now().year
    
    # document_sequences에서 prefix 및 번호 가져오기
    sequences = save_func.load_data("document_sequences", filters={"document_type": doc_type})
    
    if not sequences:
        # 기본값 생성
        prefix_map = {
            'po_customer': 'POC-',
            'po_inventory': 'POI-',
            'po_supplier': 'POS-'
        }
        prefix = prefix_map.get(doc_type, f"{doc_type.upper()[:2]}-")
        last_number = 0
    else:
        seq = sequences[0]
        prefix = seq.get('date_prefix', f"{doc_type.upper()[:2]}-")
        last_number = seq.get('last_number', 0)
    
    # 다음 번호 계산
    next_number = last_number + 1
    
    # 문서 번호 생성: POC-2025-0001, POI-2025-0001
    document_number = f"{prefix}{current_year}-{next_number:04d}"
    
    # 번호 업데이트
    try:
        # document_sequences 업데이트 로직 (실제 구현시 update_func 사용)
        pass
    except:
        pass
    
    return document_number

def process_internal_stock(process, current_user, save_func, update_func):
    """내부 재고로 처리"""
    
    with st.form(f"internal_form_{process['id']}"):
        st.subheader(f"📦 내부 재고 처리 - {process.get('process_number')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            warehouse_location = st.selectbox("출고 창고", ["창고A", "창고B", "창고C"])
            processing_date = st.date_input("처리일", value=date.today())
            
        with col2:
            available_quantity = st.number_input("가용 재고", min_value=0, value=process.get('quantity', 0))
            notes = st.text_area("처리 메모", placeholder="재고 위치, 특이사항 등...")
        
        if st.form_submit_button("📦 내부 재고 처리 완료"):
            try:
                # 내부 처리 기록 생성
                internal_data = {
                    'sales_process_id': process['id'],
                    'processing_type': 'internal_stock',
                    'warehouse_location': warehouse_location,
                    'processed_quantity': available_quantity,
                    'processing_date': processing_date.isoformat(),
                    'processed_by': current_user['id'],
                    'notes': notes,
                    'created_at': datetime.now().isoformat()
                }
                
                # 내부 처리 기록 저장 (새 테이블: internal_processing)
                save_func("internal_processing", internal_data)
                
                # 영업 프로세스 상태 업데이트
                update_func("sales_process", {"process_status": "internal_processed"}, process['id'])
                
                st.success(f"✅ 내부 재고 처리 완료: {process.get('process_number')}")
                st.rerun()
                
            except Exception as e:
                st.error(f"내부 처리 중 오류: {str(e)}")

def show_external_order_form(process, current_user, save_func, update_func):
    """외주 발주 폼 표시"""
    
    with st.form(f"external_form_{process['id']}"):
        st.subheader(f"🏭 외주 발주 - {process.get('process_number')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            supplier_name = st.text_input("공급업체명 *")
            supplier_contact = st.text_input("담당자")
            supplier_email = st.text_input("이메일")
            supplier_phone = st.text_input("전화번호")
        
        with col2:
            order_date = st.date_input("발주일", value=date.today())
            expected_arrival = st.date_input("예상 입고일", value=date.today() + timedelta(days=14))
            unit_cost = st.number_input("단가 (USD)", min_value=0.0, step=0.01)
            payment_terms = st.text_input("결제 조건", value="NET 30")
        
        quantity = process.get('quantity', 1)
        total_cost = unit_cost * quantity
        
        st.write(f"**수량**: {quantity:,}개")
        st.write(f"**총 발주 금액**: ${total_cost:,.2f} USD")
        
        notes = st.text_area("발주 메모")
        
        if st.form_submit_button("🏭 외주 발주 생성"):
            if supplier_name and unit_cost > 0:
                create_external_purchase_order(
                    process, supplier_name, supplier_contact, supplier_email, 
                    supplier_phone, order_date, expected_arrival, unit_cost, 
                    total_cost, payment_terms, notes, current_user, save_func, update_func
                )
            else:
                st.error("필수 항목을 모두 입력해주세요.")

def create_external_purchase_order(process, supplier_name, supplier_contact, supplier_email,
                                 supplier_phone, order_date, expected_arrival, unit_cost,
                                 total_cost, payment_terms, notes, current_user, save_func, update_func):
    """외주 발주서 생성"""
    
    try:
        # 발주서 번호 생성
        po_number = generate_document_number('po_supplier', save_func)
        
        # 발주서 데이터
        po_data = {
            'po_number': po_number,
            'sales_process_id': process['id'],
            'supplier_name': supplier_name,
            'supplier_contact': supplier_contact,
            'supplier_email': supplier_email,
            'supplier_phone': supplier_phone,
            'order_date': order_date.isoformat(),
            'expected_arrival_date': expected_arrival.isoformat(),
            'item_description': process.get('item_description', ''),
            'quantity': process.get('quantity', 0),
            'unit_cost': unit_cost,
            'total_cost': total_cost,
            'currency': 'USD',
            'payment_terms': payment_terms,
            'status': 'ordered',
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 발주서 저장
        save_func("purchase_orders_to_supplier", po_data)
        
        # 영업 프로세스 상태 업데이트
        update_func("sales_process", {"process_status": "external_ordered"}, process['id'])
        
        st.success(f"✅ 외주 발주서 생성 완료: {po_number}")
        st.rerun()
        
    except Exception as e:
        st.error(f"발주서 생성 중 오류: {str(e)}")

def render_existing_purchase_orders(load_func, update_func):
    """기존 발주서 및 내부 처리 목록"""
    
    st.write("### 📋 처리 내역")
    
    # 탭으로 외주발주와 내부처리 분리
    tab1, tab2 = st.tabs(["🏭 외주 발주 목록", "📦 내부 처리 목록"])
    
    with tab1:
        try:
            purchase_orders = load_func("purchase_orders_to_supplier")
            
            if not purchase_orders:
                st.info("외주 발주서가 없습니다.")
            else:
                for po in purchase_orders:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                        
                        with col1:
                            st.write(f"**{po.get('po_number', 'N/A')}**")
                            st.write(f"공급업체: {po.get('supplier_name', 'N/A')}")
                        
                        with col2:
                            st.write(f"품목: {po.get('item_description', 'N/A')[:20]}...")
                            st.write(f"수량: {po.get('quantity', 0):,}개")
                        
                        with col3:
                            amount = float(po.get('total_cost', 0))
                            st.write(f"**${amount:,.2f} USD**")
                            
                            status = po.get('status', 'unknown')
                            status_colors = {
                                'ordered': '🟡 발주완료',
                                'shipped': '🔵 배송중',
                                'received': '🟢 입고완료',
                                'cancelled': '🔴 취소됨'
                            }
                            st.write(status_colors.get(status, f"⚪ {status}"))
                        
                        with col4:
                            if status == 'ordered':
                                if st.button("입고 처리", key=f"receive_{po['id']}"):
                                    update_purchase_order_status(po['id'], 'received', update_func)
                        
                        st.divider()
            
        except Exception as e:
            st.error(f"외주 발주 목록 로드 중 오류: {str(e)}")
    
    with tab2:
        try:
            internal_processings = load_func("internal_processing")
            
            if not internal_processings:
                st.info("내부 처리 내역이 없습니다.")
            else:
                for internal in internal_processings:
                    with st.container():
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**영업 프로세스 ID**: {internal.get('sales_process_id', 'N/A')}")
                            st.write(f"**처리일**: {internal.get('processing_date', 'N/A')}")
                            st.write(f"**창고**: {internal.get('warehouse_location', 'N/A')}")
                        
                        with col2:
                            st.write(f"**처리 수량**: {internal.get('processed_quantity', 0):,}개")
                            st.write(f"**담당자**: {internal.get('processed_by', 'N/A')}")
                            if internal.get('notes'):
                                st.write(f"**메모**: {internal.get('notes')}")
                        
                        st.divider()
        
        except Exception as e:
            st.error(f"내부 처리 목록 로드 중 오류: {str(e)}")

def update_purchase_order_status(po_id, new_status, update_func):
    """발주서 상태 업데이트"""
    try:
        update_func("purchase_orders_to_supplier", {"status": new_status}, po_id)
        st.success(f"상태가 {new_status}로 업데이트되었습니다.")
        st.rerun()
    except Exception as e:
        st.error(f"상태 업데이트 중 오류: {str(e)}")

def generate_document_number(doc_type, save_func):
    """동적 문서 번호 생성"""
    
    current_year = datetime.now().year
    
    # document_sequences에서 prefix 및 번호 가져오기
    sequences = save_func.load_data("document_sequences", filters={"document_type": doc_type})
    
    if not sequences:
        # 기본값 생성
        prefix = f"{doc_type.upper()[:2]}-"
        last_number = 0
    else:
        seq = sequences[0]
        prefix = seq.get('date_prefix', f"{doc_type.upper()[:2]}-")
        last_number = seq.get('last_number', 0)
    
    # 다음 번호 계산
    next_number = last_number + 1
    
    # 문서 번호 생성: SP-2025-0001
    document_number = f"{prefix}{current_year}-{next_number:04d}"
    
    # 번호 업데이트
    try:
        # document_sequences 업데이트 로직 (실제 구현시 update_func 사용)
        pass
    except:
        pass
    
    return document_number