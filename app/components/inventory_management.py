import streamlit as st
from datetime import datetime, date, timedelta

def show_inventory_management(load_func, save_func, update_func, current_user):
    """재고 관리 (입고/검수/출고)"""
    
    st.subheader("📋 재고 관리")
    
    inventory_tabs = st.tabs(["📥 입고 관리", "🔍 검수 관리", "📤 출고 관리"])
    
    with inventory_tabs[0]:
        render_receiving_management(load_func, save_func, current_user)
    
    with inventory_tabs[1]:
        render_quality_inspection(load_func, save_func, update_func, current_user)
    
    with inventory_tabs[2]:
        render_shipping_management(load_func, save_func, update_func, current_user)

def render_receiving_management(load_func, save_func, current_user):
    """입고 관리"""
    
    st.write("### 📥 입고 관리")
    
    # 입고 대기 중인 발주서 조회
    try:
        purchase_orders = load_func("purchase_orders_to_supplier")
        if not purchase_orders:
            st.info("입고 대기 중인 발주서가 없습니다.")
            return
        
        # 입고 대기 중인 발주서만 필터링
        pending_orders = [po for po in purchase_orders if po.get('status') == 'ordered']
        
        if not pending_orders:
            st.info("입고 대기 중인 발주서가 없습니다.")
            return
        
        st.write(f"📦 입고 대기: **{len(pending_orders)}건**")
        
        # 입고 등록 폼
        with st.form("receiving_form"):
            st.subheader("🆕 새 입고 등록")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 발주서 선택
                po_options = [f"{po.get('po_number', 'N/A')} - {po.get('supplier_name', 'N/A')}" for po in pending_orders]
                selected_po_idx = st.selectbox("발주서 선택", range(len(po_options)), format_func=lambda x: po_options[x])
                selected_po = pending_orders[selected_po_idx] if pending_orders else None
                
                received_date = st.date_input("입고일", value=date.today())
                received_quantity = st.number_input("입고 수량", min_value=1, value=selected_po.get('quantity', 1) if selected_po else 1)
            
            with col2:
                warehouse_location = st.selectbox("창고 위치", ["창고A", "창고B", "창고C", "임시창고"])
                condition_notes = st.text_area("상태 메모", placeholder="포장 상태, 외관 등...")
            
            submitted = st.form_submit_button("📥 입고 등록", type="primary")
            
            if submitted and selected_po:
                # 입고 번호 생성
                receiving_number = generate_document_number('receiving', save_func)
                
                receiving_data = {
                    'receiving_number': receiving_number,
                    'po_supplier_id': selected_po.get('id'),
                    'sales_process_id': selected_po.get('sales_process_id'),
                    'received_date': received_date.isoformat(),
                    'received_by': current_user['id'],
                    'received_quantity': received_quantity,
                    'expected_quantity': selected_po.get('quantity', 0),
                    'warehouse_location': warehouse_location,
                    'condition_notes': condition_notes if condition_notes.strip() else None
                }
                
                if save_func("inventory_receiving", receiving_data):
                    # 발주서 상태 업데이트
                    update_purchase_order_status(selected_po['id'], 'received', update_func)
                    st.success(f"✅ 입고 등록 완료: {receiving_number}")
                    st.rerun()
                else:
                    st.error("❌ 입고 등록에 실패했습니다.")
        
        # 최근 입고 목록
        st.subheader("📋 최근 입고 목록")
        recent_receivings = load_func("inventory_receiving")
        if recent_receivings:
            for receiving in recent_receivings[-5:]:  # 최근 5건
                with st.expander(f"📦 {receiving.get('receiving_number', 'N/A')} - {receiving.get('warehouse_location', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**입고일**: {receiving.get('received_date', 'N/A')}")
                        st.write(f"**수량**: {receiving.get('received_quantity', 0):,}개")
                    with col2:
                        st.write(f"**창고**: {receiving.get('warehouse_location', 'N/A')}")
                        st.write(f"**담당자**: {receiving.get('received_by', 'N/A')}")
                    if receiving.get('condition_notes'):
                        st.write(f"**메모**: {receiving.get('condition_notes')}")
        
    except Exception as e:
        st.error(f"입고 관리 로드 중 오류: {str(e)}")

def render_quality_inspection(load_func, save_func, update_func, current_user):
    """검수 관리"""
    
    st.write("### 🔍 검수 관리")
    
    try:
        # 검수 대기 중인 입고 조회
        receivings = load_func("inventory_receiving")
        if not receivings:
            st.info("검수 대기 중인 입고가 없습니다.")
            return
        
        # 검수되지 않은 입고만 필터링
        inspections = load_func("quality_inspection")
        inspected_receiving_ids = [insp.get('receiving_id') for insp in inspections] if inspections else []
        pending_receivings = [r for r in receivings if r.get('id') not in inspected_receiving_ids]
        
        if not pending_receivings:
            st.info("검수 대기 중인 입고가 없습니다.")
            return
        
        st.write(f"🔍 검수 대기: **{len(pending_receivings)}건**")
        
        # 검수 등록 폼
        with st.form("inspection_form"):
            st.subheader("🆕 새 검수 등록")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 입고 선택
                receiving_options = [f"{r.get('receiving_number', 'N/A')} - {r.get('warehouse_location', 'N/A')}" for r in pending_receivings]
                selected_receiving_idx = st.selectbox("입고 선택", range(len(receiving_options)), format_func=lambda x: receiving_options[x])
                selected_receiving = pending_receivings[selected_receiving_idx] if pending_receivings else None
                
                inspection_date = st.date_input("검수일", value=date.today())
                inspection_method = st.selectbox("검수 방법", ["전수검사", "샘플검사", "육안검사", "기능검사"])
            
            with col2:
                total_quantity = selected_receiving.get('received_quantity', 0) if selected_receiving else 0
                st.write(f"**입고 수량**: {total_quantity:,}개")
                
                approved_quantity = st.number_input("승인 수량", min_value=0, max_value=total_quantity, value=total_quantity)
                rejected_quantity = total_quantity - approved_quantity
                st.write(f"**불량 수량**: {rejected_quantity:,}개")
                
                inspection_result = st.selectbox("검수 결과", ["합격", "부분합격", "불합격"])
                approved_for_shipment = st.checkbox("출고 승인", value=(inspection_result == "합격"))
            
            inspection_notes = st.text_area("검수 메모", placeholder="품질 상태, 불량 사유 등...")
            
            submitted = st.form_submit_button("🔍 검수 완료", type="primary")
            
            if submitted and selected_receiving:
                # 검수 번호 생성
                inspection_number = generate_document_number('quality_insp', save_func)
                
                inspection_data = {
                    'inspection_number': inspection_number,
                    'receiving_id': selected_receiving.get('id'),
                    'sales_process_id': selected_receiving.get('sales_process_id'),
                    'inspector_id': current_user['id'],
                    'inspection_date': inspection_date.isoformat(),
                    'inspection_method': inspection_method,
                    'total_quantity': total_quantity,
                    'approved_quantity': approved_quantity,
                    'rejected_quantity': rejected_quantity,
                    'inspection_result': inspection_result,
                    'approved_for_shipment': approved_for_shipment,
                    'inspection_notes': inspection_notes if inspection_notes.strip() else None
                }
                
                if save_func("quality_inspection", inspection_data):
                    st.success(f"✅ 검수 완료: {inspection_number}")
                    st.rerun()
                else:
                    st.error("❌ 검수 등록에 실패했습니다.")
        
        # 최근 검수 목록
        st.subheader("📋 최근 검수 목록")
        recent_inspections = load_func("quality_inspection")
        if recent_inspections:
            for inspection in recent_inspections[-5:]:  # 최근 5건
                with st.expander(f"🔍 {inspection.get('inspection_number', 'N/A')} - {inspection.get('inspection_result', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**검수일**: {inspection.get('inspection_date', 'N/A')}")
                        st.write(f"**방법**: {inspection.get('inspection_method', 'N/A')}")
                        st.write(f"**결과**: {inspection.get('inspection_result', 'N/A')}")
                    with col2:
                        st.write(f"**승인 수량**: {inspection.get('approved_quantity', 0):,}개")
                        st.write(f"**불량 수량**: {inspection.get('rejected_quantity', 0):,}개")
                        if inspection.get('approved_for_shipment'):
                            st.success("✅ 출고 승인")
                        else:
                            st.warning("⚠️ 출고 대기")
        
    except Exception as e:
        st.error(f"검수 관리 로드 중 오류: {str(e)}")

def render_shipping_management(load_func, save_func, update_func, current_user):
    """출고 관리"""
    
    st.write("### 📤 출고 관리")
    
    try:
        # 출고 승인된 검수 조회
        inspections = load_func("quality_inspection")
        if not inspections:
            st.info("출고 가능한 제품이 없습니다.")
            return
        
        # 출고 승인된 검수만 필터링
        approved_inspections = [insp for insp in inspections if insp.get('approved_for_shipment')]
        
        # 이미 출고된 것들 제외
        shipments = load_func("delivery_shipment")
        shipped_inspection_ids = [ship.get('inspection_id') for ship in shipments] if shipments else []
        pending_inspections = [insp for insp in approved_inspections if insp.get('id') not in shipped_inspection_ids]
        
        if not pending_inspections:
            st.info("출고 대기 중인 제품이 없습니다.")
            return
        
        st.write(f"📤 출고 대기: **{len(pending_inspections)}건**")
        
        # 출고 등록 폼
        with st.form("shipment_form"):
            st.subheader("🆕 새 출고 등록")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 검수 선택
                inspection_options = [f"{insp.get('inspection_number', 'N/A')} - 승인: {insp.get('approved_quantity', 0):,}개" for insp in pending_inspections]
                selected_inspection_idx = st.selectbox("검수 선택", range(len(inspection_options)), format_func=lambda x: inspection_options[x])
                selected_inspection = pending_inspections[selected_inspection_idx] if pending_inspections else None
                
                shipment_date = st.date_input("출고일", value=date.today())
                delivery_method = st.selectbox("배송 방법", ["직배송", "택배", "화물", "고객픽업"])
            
            with col2:
                delivery_address = st.text_area("배송 주소")
                delivery_contact = st.text_input("연락처")
                delivery_phone = st.text_input("전화번호")
            
            shipment_notes = st.text_area("출고 메모", placeholder="특별 지시사항, 포장 방법 등...")
            
            submitted = st.form_submit_button("📤 출고 등록", type="primary")
            
            if submitted and selected_inspection:
                # 출고 번호 생성
                shipment_number = generate_document_number('shipment', save_func)
                
                shipment_data = {
                    'shipment_number': shipment_number,
                    'sales_process_id': selected_inspection.get('sales_process_id'),
                    'inspection_id': selected_inspection.get('id'),
                    'shipment_date': shipment_date.isoformat(),
                    'shipped_by': current_user['id'],
                    'delivery_address': delivery_address if delivery_address.strip() else None,
                    'delivery_contact': delivery_contact if delivery_contact.strip() else None,
                    'delivery_phone': delivery_phone if delivery_phone.strip() else None,
                    'delivery_method': delivery_method,
                    'shipment_status': 'preparing',
                    'shipment_notes': shipment_notes if shipment_notes.strip() else None
                }
                
                if save_func("delivery_shipment", shipment_data):
                    st.success(f"✅ 출고 등록 완료: {shipment_number}")
                    st.rerun()
                else:
                    st.error("❌ 출고 등록에 실패했습니다.")
        
        # 최근 출고 목록
        st.subheader("📋 최근 출고 목록")
        recent_shipments = load_func("delivery_shipment")
        if recent_shipments:
            for shipment in recent_shipments[-5:]:  # 최근 5건
                with st.expander(f"📤 {shipment.get('shipment_number', 'N/A')} - {shipment.get('delivery_method', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**출고일**: {shipment.get('shipment_date', 'N/A')}")
                        st.write(f"**배송방법**: {shipment.get('delivery_method', 'N/A')}")
                        
                        status = shipment.get('shipment_status', 'unknown')
                        status_colors = {
                            'preparing': '🟡 준비중',
                            'shipped': '🔵 출고완료',
                            'in_transit': '🟠 배송중',
                            'delivered': '🟢 배송완료'
                        }
                        st.write(f"**상태**: {status_colors.get(status, f'⚪ {status}')}")
                    with col2:
                        st.write(f"**연락처**: {shipment.get('delivery_contact', 'N/A')}")
                        st.write(f"**전화**: {shipment.get('delivery_phone', 'N/A')}")
                        if shipment.get('delivery_address'):
                            st.write(f"**주소**: {shipment.get('delivery_address')[:30]}...")
                    
                    # 상태 업데이트 버튼들
                    if status == 'preparing':
                        if st.button("출고 완료", key=f"ship_{shipment['id']}"):
                            update_shipment_status(shipment['id'], 'shipped', update_func)
                    elif status == 'shipped':
                        if st.button("배송 완료", key=f"deliver_{shipment['id']}"):
                            update_shipment_status(shipment['id'], 'delivered', update_func)
        
    except Exception as e:
        st.error(f"출고 관리 로드 중 오류: {str(e)}")

# ==================== 헬퍼 함수들 ====================

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

def update_purchase_order_status(po_id, new_status, update_func):
    """발주서 상태 업데이트"""
    try:
        update_func("purchase_orders_to_supplier", {"status": new_status}, po_id)
        st.success(f"상태가 {new_status}로 업데이트되었습니다.")
        st.rerun()
    except Exception as e:
        st.error(f"상태 업데이트 중 오류: {str(e)}")

def update_shipment_status(shipment_id, new_status, update_func):
    """출고 상태 업데이트"""
    try:
        update_func("delivery_shipment", {"shipment_status": new_status}, shipment_id)
        st.success(f"상태가 {new_status}로 업데이트되었습니다.")
        st.rerun()
    except Exception as e:
        st.error(f"상태 업데이트 중 오류: {str(e)}")