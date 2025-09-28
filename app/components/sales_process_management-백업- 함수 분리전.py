# sales_process_management.py - 영업 프로세스 관리 시스템
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple

def show_sales_process_management(load_func, save_func, update_func, delete_func, 
                                get_current_user_func, check_permission_func,
                                get_approval_status_info, calculate_statistics,
                                create_csv_download, render_print_form):
    """영업 프로세스 관리 시스템 메인 함수"""
    
    st.title("🔄 영업 프로세스 관리")
    st.caption("Sales Process Management - Quote to Cash")
    
    # 현재 사용자 정보 확인
    current_user = get_current_user_func()
    if not current_user:
        st.error("로그인이 필요합니다.")
        return
    
    # 탭 구성
    tabs = st.tabs(["📊 프로세스 현황", "⚡ 견적서 전환", "📦 발주 관리", "📋 재고 관리", "💰 수익 분석"])
    
    with tabs[0]:
        render_process_dashboard(load_func, current_user)
    
    with tabs[1]:
        render_quotation_conversion(load_func, save_func, current_user)
    
    with tabs[2]:
        render_purchase_order_management(load_func, save_func, update_func, current_user)
    
    with tabs[3]:
        render_inventory_management(load_func, save_func, update_func, current_user)
    
    with tabs[4]:
        render_profit_analysis(load_func, current_user)

def render_process_dashboard(load_func, current_user):
    """영업 프로세스 현황 대시보드"""
    
    st.subheader("📊 영업 프로세스 현황")
    
    try:
        # 영업 프로세스 데이터 로드
        processes = load_func("sales_process")
        
        if not processes:
            st.info("진행 중인 영업 프로세스가 없습니다.")
            st.write("견적서 전환 탭에서 새로운 프로세스를 시작해보세요.")
            return
        
        # 전체 통계
        total_processes = len(processes)
        total_amount = sum(float(p.get('total_amount', 0)) for p in processes)
        
        # 상태별 통계
        status_counts = {}
        for process in processes:
            status = process.get('process_status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 프로세스", total_processes)
        with col2:
            st.metric("총 거래액", f"{total_amount:,.0f} VND")
        with col3:
            completed = status_counts.get('completed', 0)
            completion_rate = (completed / total_processes * 100) if total_processes > 0 else 0
            st.metric("완료율", f"{completion_rate:.1f}%")
        with col4:
            in_progress = total_processes - completed
            st.metric("진행 중", in_progress)
        
        # 상태별 분포 차트
        if status_counts:
            st.write("### 📈 상태별 분포")
            
            # 상태명 한글화
            status_korean = {
                'quotation': '견적 단계',
                'approved': '승인됨',
                'ordered': '발주 완료',
                'received': '입고 완료',
                'inspected': '검수 완료',
                'shipped': '출고 완료',
                'completed': '완료'
            }
            
            chart_data = []
            for status, count in status_counts.items():
                chart_data.append({
                    '상태': status_korean.get(status, status),
                    '건수': count
                })
            
            if chart_data:
                chart_df = pd.DataFrame(chart_data)
                st.bar_chart(chart_df.set_index('상태'))
        
        # 프로세스 목록 테이블
        st.write("### 📋 진행 중인 프로세스")
        
        # 테이블용 데이터 준비
        display_data = []
        for process in processes:
            display_data.append({
                '프로세스 번호': process.get('process_number', 'N/A'),
                '고객사': process.get('customer_company', 'N/A'),
                '상품': process.get('item_description', 'N/A')[:30] + '...' if len(process.get('item_description', '')) > 30 else process.get('item_description', 'N/A'),
                '금액 (VND)': f"{float(process.get('total_amount', 0)):,.0f}",
                '상태': status_korean.get(process.get('process_status', ''), process.get('process_status', 'N/A')),
                '생성일': process.get('created_at', 'N/A')[:10] if process.get('created_at') else 'N/A'
            })
        
        if display_data:
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 지연 알림
        render_delay_alerts(processes)
        
    except Exception as e:
        st.error(f"대시보드 로드 중 오류 발생: {str(e)}")

def render_quotation_conversion(load_func, save_func, current_user):
    """견적서 → 영업 프로세스 전환"""
    
    st.subheader("⚡ 견적서 → 영업 프로세스 전환")
    
    # 권한 확인
    if current_user.get('role') not in ['admin', 'manager']:
        st.error("영업 프로세스 전환 권한이 없습니다.")
        return
    
    try:
        # 승인 가능한 견적서 로드 (작성중 또는 검토중 상태)
        quotations = load_func("quotations", filters={"status": ["작성중", "검토중", "승인대기"]})
        
        if not quotations:
            st.info("전환 가능한 견적서가 없습니다.")
            return
        
        # 견적서 선택
        st.write("### 📄 전환할 견적서 선택")
        
        # 견적서 목록 표시
        for quota in quotations:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**{quota.get('customer_name', 'N/A')} ({quota.get('company', 'N/A')})**")
                    st.write(f"상품: {quota.get('item_name', 'N/A')}")
                    st.write(f"수량: {quota.get('quantity', 0):,}개")
                
                with col2:
                    amount = float(quota.get('total_amount', 0))
                    currency = quota.get('currency', 'VND')
                    st.write(f"**금액: {amount:,.0f} {currency}**")
                    st.write(f"상태: {quota.get('status', 'N/A')}")
                    st.write(f"작성일: {quota.get('created_at', 'N/A')[:10] if quota.get('created_at') else 'N/A'}")
                
                with col3:
                    if st.button(f"전환하기", key=f"convert_{quota['id']}"):
                        convert_quotation_to_process(quota, current_user, save_func)
                
                st.divider()
        
    except Exception as e:
        st.error(f"견적서 로드 중 오류 발생: {str(e)}")

def convert_quotation_to_process(quotation, current_user, save_func):
    """견적서를 영업 프로세스로 전환"""
    
    try:
        # 프로세스 번호 생성
        process_number = generate_document_number('sales_process', save_func)
        
        # 영업 프로세스 데이터 생성
        process_data = {
            'process_number': process_number,
            'quotation_id': quotation['id'],
            'customer_name': quotation.get('customer_name', ''),
            'customer_company': quotation.get('company', ''),
            'customer_email': quotation.get('email', ''),
            'customer_phone': quotation.get('phone', ''),
            'sales_rep_id': current_user['id'],
            'process_status': 'approved',
            'item_description': quotation.get('item_name', ''),
            'quantity': quotation.get('quantity', 0),
            'unit_price': quotation.get('unit_price', 0),
            'total_amount': quotation.get('total_amount', 0),
            'currency': quotation.get('currency', 'VND'),
            'expected_delivery_date': (datetime.now() + timedelta(days=30)).date().isoformat(),
            'notes': quotation.get('notes', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 영업 프로세스 저장
        save_func("sales_process", process_data)
        
        # 견적서 상태 업데이트
        update_quotation_status(quotation['id'], '승인됨', save_func)
        
        # 프로세스 이력 기록
        record_process_history(
            process_number, None, 'approved', 
            current_user['id'], '견적서에서 전환', save_func
        )
        
        st.success(f"✅ 영업 프로세스가 생성되었습니다: {process_number}")
        st.balloons()
        st.rerun()
        
    except Exception as e:
        st.error(f"프로세스 전환 중 오류 발생: {str(e)}")

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

def render_purchase_order_management(load_func, save_func, update_func, current_user):
    """공급업체 발주 관리"""
    
    st.subheader("📦 공급업체 발주 관리")
    
    # 발주 가능한 영업 프로세스 로드
    processes = load_func("sales_process", filters={"process_status": "approved"})
    
    if not processes:
        st.info("발주 가능한 영업 프로세스가 없습니다.")
        return
    
    # 신규 발주서 생성
    with st.expander("📝 신규 발주서 생성", expanded=True):
        with st.form("new_purchase_order"):
            col1, col2 = st.columns(2)
            
            with col1:
                # 영업 프로세스 선택
                process_options = {
                    f"{p['process_number']} - {p['customer_company']}": p['id'] 
                    for p in processes
                }
                selected_process = st.selectbox("영업 프로세스 선택", list(process_options.keys()))
                
                supplier_name = st.text_input("공급업체명 *")
                supplier_contact = st.text_input("담당자")
                supplier_email = st.text_input("이메일")
                supplier_phone = st.text_input("전화번호")
            
            with col2:
                order_date = st.date_input("발주일", value=date.today())
                expected_arrival = st.date_input("예상 입고일", value=date.today() + timedelta(days=14))
                unit_cost = st.number_input("단가 (USD)", min_value=0.0, step=0.01)
                payment_terms = st.text_input("결제 조건", value="NET 30")
            
            item_description = st.text_area("발주 품목 설명")
            quantity = st.number_input("수량", min_value=1, value=1)
            total_cost = unit_cost * quantity
            
            st.write(f"**총 발주 금액: ${total_cost:,.2f} USD**")
            
            notes = st.text_area("발주 메모")
            
            if st.form_submit_button("📦 발주서 생성", type="primary"):
                if supplier_name and selected_process and unit_cost > 0:
                    create_purchase_order(
                        process_options[selected_process], supplier_name, supplier_contact,
                        supplier_email, supplier_phone, order_date, expected_arrival,
                        item_description, quantity, unit_cost, total_cost,
                        payment_terms, notes, current_user, save_func
                    )
                else:
                    st.error("필수 항목을 모두 입력해주세요.")
    
    # 기존 발주서 목록
    render_existing_purchase_orders(load_func, update_func)

def create_purchase_order(process_id, supplier_name, supplier_contact, supplier_email, 
                         supplier_phone, order_date, expected_arrival, item_description,
                         quantity, unit_cost, total_cost, payment_terms, notes, 
                         current_user, save_func):
    """발주서 생성"""
    
    try:
        # 발주서 번호 생성
        po_number = generate_document_number('po_supplier', save_func)
        
        # 발주서 데이터
        po_data = {
            'po_number': po_number,
            'sales_process_id': process_id,
            'supplier_name': supplier_name,
            'supplier_contact': supplier_contact,
            'supplier_email': supplier_email,
            'supplier_phone': supplier_phone,
            'order_date': order_date.isoformat(),
            'expected_arrival_date': expected_arrival.isoformat(),
            'item_description': item_description,
            'quantity': quantity,
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
        # update_func("sales_process", {"process_status": "ordered"}, process_id)
        
        st.success(f"✅ 발주서가 생성되었습니다: {po_number}")
        st.rerun()
        
    except Exception as e:
        st.error(f"발주서 생성 중 오류 발생: {str(e)}")

def render_existing_purchase_orders(load_func, update_func):
    """기존 발주서 목록"""
    
    st.write("### 📋 발주서 목록")
    
    try:
        purchase_orders = load_func("purchase_orders_to_supplier")
        
        if not purchase_orders:
            st.info("발주서가 없습니다.")
            return
        
        # 발주서 목록 표시
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
        st.error(f"발주서 목록 로드 중 오류 발생: {str(e)}")

def render_inventory_management(load_func, save_func, update_func, current_user):
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

def update_shipment_status(shipment_id, new_status, update_func):
    """출고 상태 업데이트"""
    try:
        update_func("delivery_shipment", {"shipment_status": new_status}, shipment_id)
        st.success(f"상태가 {new_status}로 업데이트되었습니다.")
        st.rerun()
    except Exception as e:
        st.error(f"상태 업데이트 중 오류: {str(e)}")

def render_profit_analysis(load_func, current_user):
    """수익 분석"""
    
    st.subheader("💰 수익 분석")
    
    try:
        # sales_process_analysis 뷰에서 데이터 로드
        analysis_data = load_func("sales_process_analysis")
        
        if not analysis_data:
            st.info("분석할 데이터가 없습니다.")
            return
        
        # 전체 수익 통계
        total_sales_vnd = sum(float(item.get('customer_amount_vnd', 0)) for item in analysis_data if item.get('customer_amount_vnd'))
        total_cost_usd = sum(float(item.get('supplier_cost_usd', 0)) for item in analysis_data if item.get('supplier_cost_usd'))
        
        # 환율 적용 (간단한 고정 환율 사용)
        exchange_rate = 24000  # 1 USD = 24,000 VND
        total_sales_usd = total_sales_vnd / exchange_rate
        total_profit_usd = total_sales_usd - total_cost_usd
        profit_margin = (total_profit_usd / total_cost_usd * 100) if total_cost_usd > 0 else 0
        
        # 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 매출 (USD)", f"${total_sales_usd:,.0f}")
        with col2:
            st.metric("총 원가 (USD)", f"${total_cost_usd:,.0f}")
        with col3:
            st.metric("총 수익 (USD)", f"${total_profit_usd:,.0f}")
        with col4:
            st.metric("수익률", f"{profit_margin:.1f}%")
        
        # 프로젝트별 수익률 표
        st.write("### 📊 프로젝트별 수익 분석")
        
        profit_data = []
        for item in analysis_data:
            if item.get('supplier_cost_usd'):
                profit_data.append({
                    '프로세스 번호': item.get('process_number', 'N/A'),
                    '고객사': item.get('customer_name', 'N/A'),
                    '매출 (VND)': f"{float(item.get('customer_amount_vnd', 0)):,.0f}",
                    '원가 (USD)': f"${float(item.get('supplier_cost_usd', 0)):,.0f}",
                    '수익률 (%)': f"{float(item.get('profit_margin_percent', 0)):.1f}%"
                })
        
        if profit_data:
            df = pd.DataFrame(profit_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"수익 분석 중 오류 발생: {str(e)}")

# ==================== 헬퍼 함수들 ====================

def render_delay_alerts(processes):
    """지연 알림"""
    
    st.write("### ⚠️ 지연 알림")
    
    today = date.today()
    delayed_processes = []
    
    for process in processes:
        expected_date = process.get('expected_delivery_date')
        if expected_date:
            try:
                expected = datetime.strptime(expected_date, '%Y-%m-%d').date()
                if expected < today and process.get('process_status') != 'completed':
                    days_delayed = (today - expected).days
                    delayed_processes.append({
                        'process_number': process.get('process_number', 'N/A'),
                        'customer_company': process.get('customer_company', 'N/A'),
                        'days_delayed': days_delayed,
                        'status': process.get('process_status', 'N/A')
                    })
            except:
                continue
    
    if delayed_processes:
        for delayed in delayed_processes:
            st.warning(
                f"🚨 **{delayed['process_number']}** ({delayed['customer_company']}) - "
                f"{delayed['days_delayed']}일 지연 (상태: {delayed['status']})"
            )
    else:
        st.success("✅ 지연된 프로세스가 없습니다.")

def update_quotation_status(quotation_id, new_status, update_func):
    """견적서 상태 업데이트"""
    try:
        # 실제 구현시 update_func 사용
        pass
    except:
        pass

def record_process_history(process_number, status_from, status_to, changed_by, reason, save_func):
    """프로세스 이력 기록"""
    
    history_data = {
        'sales_process_id': process_number,  # 실제로는 ID로 변경 필요
        'status_from': status_from,
        'status_to': status_to,
        'changed_by': changed_by,
        'change_date': datetime.now().isoformat(),
        'change_reason': reason
    }
    
    try:
        save_func("sales_process_history", history_data)
    except:
        pass

def update_purchase_order_status(po_id, new_status, update_func):
    """발주서 상태 업데이트"""
    try:
        update_func("purchase_orders_to_supplier", {"status": new_status}, po_id)
        st.success(f"상태가 {new_status}로 업데이트되었습니다.")
        st.rerun()
    except Exception as e:
        st.error(f"상태 업데이트 중 오류: {str(e)}")