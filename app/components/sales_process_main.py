import streamlit as st
from components.sales_process_dashboard import show_sales_process_dashboard
from components.purchase_order_management import show_purchase_order_management
from components.inventory_management import show_inventory_management
from components.profit_analysis import show_profit_analysis
from datetime import datetime, date, timedelta
from components.document_number import generate_document_number

def show_sales_process_management(load_func, save_func, update_func, delete_func, 
                                get_current_user_func, check_permission_func, 
                                get_approval_status_info, calculate_statistics, 
                                create_csv_download, render_print_form):
    """영업 프로세스 관리 메인 함수 - 모듈 통합 버전"""
    
    # 현재 사용자 정보 가져오기
    current_user = get_current_user_func()
    
    if not current_user:
        st.error("로그인이 필요합니다.")
        return
    
    st.title("🎯 영업 프로세스 관리")
    
    # 탭 구성 (코드별 발주 탭 추가)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 영업 현황", 
        "📦 발주 관리", 
        "📋 재고 관리", 
        "💰 수익 분석",
        "🔧 코드별 발주"
    ])
    
    with tab1:
        # 영업 프로세스 현황 + 코드별 발주 분할 기능
        show_enhanced_sales_dashboard(load_func, save_func, update_func, current_user)
    
    with tab2:
        # 발주 관리 (고객 주문 기반 + 재고 보충)
        show_purchase_order_management(load_func, save_func, update_func, current_user)
    
    with tab3:
        # 재고 관리 (입고/검수/출고)
        show_inventory_management(load_func, save_func, update_func, current_user)
    
    with tab4:
        # 수익 분석
        show_profit_analysis(load_func)
    
    with tab5:
        # 신규: 코드별 발주 통합 관리
        show_code_breakdown_management(load_func, save_func, update_func, current_user)
    
    # 하단 정보 표시
    render_system_info(load_func, current_user)

def show_enhanced_sales_dashboard(load_func, save_func, update_func, current_user):
    """향상된 영업 대시보드 - 상태 변경 + 코드별 발주 기능"""
    st.header("📊 영업 프로세스 현황")
    
    # 데이터 로드
    processes = load_func('sales_process') or []
    
    if processes:
        import pandas as pd
        df = pd.DataFrame(processes)
        
        # 메트릭 카드
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 프로세스", len(df))
        
        with col2:
            total_amount = df['total_amount'].sum() if 'total_amount' in df.columns else 0
            st.metric("총 거래액", f"${total_amount:,.0f}")
        
        with col3:
            completed = len(df[df['process_status'] == 'completed']) if 'process_status' in df.columns else 0
            completion_rate = (completed / len(df) * 100) if len(df) > 0 else 0
            st.metric("완료율", f"{completion_rate:.1f}%")
        
        with col4:
            in_progress = len(df[df['process_status'].isin(['approved', 'ordered', 'received'])]) if 'process_status' in df.columns else 0
            st.metric("진행 중", in_progress)
        
        # 상태별 분포 차트
        if 'process_status' in df.columns:
            st.subheader("📈 상태별 분포")
            status_counts = df['process_status'].value_counts()
            st.bar_chart(status_counts)
        
        # 프로세스 목록 - 상태 변경 및 코드별 발주 기능
        st.subheader("📋 프로세스 관리")
        
        for process in processes:
            with st.expander(f"📋 {process.get('process_number', 'N/A')} - {process.get('customer_name', 'N/A')}"):
                # 기본 정보와 상태 변경을 왼쪽에, 코드별 발주 기능을 오른쪽에 배치
                left_col, right_col = st.columns([3, 1])
                
                with left_col:
                    # 프로세스 정보와 상태 변경
                    info_col, status_col = st.columns([2, 1])
                    
                    with info_col:
                        st.write(f"**고객명**: {process.get('customer_name', 'N/A')}")
                        st.write(f"**품목**: {process.get('item_description', 'N/A')}")
                        st.write(f"**수량**: {process.get('quantity', 0):,}개")
                        st.write(f"**총 금액**: ${process.get('total_amount', 0):,.2f}")
                        st.write(f"**예상 납기**: {process.get('expected_delivery_date', 'N/A')}")
                        st.write(f"**현재 상태**: {process.get('process_status', 'N/A')}")
                    
                    with status_col:
                        # 상태 변경 기능
                        current_status = process.get('process_status', 'approved')
                        status_options = ['approved', 'completed', 'ordered', 'received', 'closed']
                        
                        try:
                            current_index = status_options.index(current_status)
                        except ValueError:
                            current_index = 0
                        
                        new_status = st.selectbox(
                            "상태 변경:",
                            status_options,
                            index=current_index,
                            key=f"status_{process['id']}"
                        )
                        
                        if st.button(f"상태 저장", key=f"save_{process['id']}"):
                            update_func('sales_process', process['id'], {
                                'process_status': new_status,
                                'updated_at': datetime.now()
                            })
                            st.success(f"상태를 {new_status}로 변경했습니다!")
                            # 세션 상태 초기화
                            for key in list(st.session_state.keys()):
                                if key.startswith(f"breakdown_{process['id']}") or key.startswith(f"show_breakdown_{process['id']}"):
                                    del st.session_state[key]
                            st.rerun()
                
                with right_col:
                    # 코드별 발주 분할 기능 (오른쪽)
                    st.write("**코드별 발주**")
                    
                    # 기존 분할 내역 확인
                    existing_breakdowns = load_func('process_item_breakdown') or []
                    existing_items = [item for item in existing_breakdowns if item.get('sales_process_id') == process.get('id')]
                    
                    if existing_items:
                        st.success(f"분할 완료\n({len(existing_items)}개 코드)")
                        if st.button(f"분할 내역 보기", key=f"view_{process['id']}"):
                            st.session_state[f'show_breakdown_detail_{process["id"]}'] = True
                            st.rerun()
                    elif new_status in ['completed', 'ordered']:
                        if st.button(f"📦 코드별 분할 시작", key=f"breakdown_{process['id']}"):
                            st.session_state[f'show_breakdown_{process["id"]}'] = True
                            st.rerun()
                    else:
                        st.info("상태를 'completed' 또는 'ordered'로 변경 후 분할 가능")
                
                # 코드별 분할 폼 표시
                if st.session_state.get(f'show_breakdown_{process["id"]}', False):
                    render_code_breakdown_form(process, load_func, save_func, update_func, current_user)
                
                # 기존 분할 내역 상세 표시
                if st.session_state.get(f'show_breakdown_detail_{process["id"]}', False):
                    render_existing_breakdown_detail(existing_items, load_func, update_func, current_user)
    else:
        st.info("등록된 영업 프로세스가 없습니다.")
        
        # 빈 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 프로세스", "0")
        with col2:
            st.metric("총 거래액", "$0")
        with col3:
            st.metric("완료율", "0%")
        with col4:
            st.metric("진행 중", "0")

def render_code_breakdown_form(process, load_func, save_func, update_func, current_user):
    """코드 분할 입력 폼"""
    st.markdown("---")
    st.subheader("📦 코드별 발주 분할 입력")
    
    # 견적서에서 코드 자동 가져오기
    quotation_id = process.get('quotation_id')
    auto_codes = []
    
    if quotation_id:
        quotations = load_func('quotations_detail') or []
        quotation_items = [q for q in quotations if q.get('quotation_id') == quotation_id or q.get('id') == quotation_id]
        
        for item in quotation_items:
            if item.get('item_code'):
                auto_codes.append({
                    'item_code': item.get('item_code', ''),
                    'quantity': item.get('quantity', 1),
                    'description': item.get('item_name', '')
                })
    
    with st.form(f"breakdown_form_{process['id']}"):
        st.write(f"**프로세스**: {process.get('process_number', 'N/A')}")
        
        if auto_codes:
            st.success(f"견적서에서 {len(auto_codes)}개 코드를 자동으로 가져왔습니다.")
            breakdown_items = []
            
            for i, auto_code in enumerate(auto_codes):
                st.write(f"**코드 {i+1}**")
                col1, col2, col3 = st.columns([3, 2, 3])
                
                with col1:
                    item_code = st.text_input(f"상품 코드", value=auto_code['item_code'], key=f"code_{process['id']}_{i}")
                
                with col2:
                    quantity = st.number_input(f"수량", min_value=1, value=auto_code['quantity'], key=f"qty_{process['id']}_{i}")
                
                with col3:
                    description = st.text_input(f"설명", value=auto_code['description'], key=f"desc_{process['id']}_{i}")
                
                breakdown_items.append({
                    'item_code': item_code,
                    'quantity': quantity,
                    'description': description
                })
        else:
            # 수동 입력
            num_codes = st.number_input("분할할 코드 개수", min_value=1, max_value=10, value=2)
            breakdown_items = []
            
            for i in range(num_codes):
                st.write(f"**코드 {i+1}**")
                col1, col2, col3 = st.columns([3, 2, 3])
                
                with col1:
                    item_code = st.text_input(f"상품 코드", placeholder="예: HR-ST-OP-16", key=f"code_{process['id']}_{i}")
                
                with col2:
                    quantity = st.number_input(f"수량", min_value=1, value=1, key=f"qty_{process['id']}_{i}")
                
                with col3:
                    description = st.text_input(f"설명", placeholder="상품 설명", key=f"desc_{process['id']}_{i}")
                
                if item_code:
                    breakdown_items.append({
                        'item_code': item_code,
                        'quantity': quantity,
                        'description': description
                    })
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("✅ 분할 저장", type="primary"):
                if breakdown_items:
                    save_breakdown_items(process, breakdown_items, save_func, current_user)
                    st.success("코드별 분할이 저장되었습니다!")
                    st.session_state[f'show_breakdown_{process["id"]}'] = False
                    st.rerun()
                else:
                    st.error("최소 하나의 코드를 입력해주세요.")
        
        with col2:
            if st.form_submit_button("❌ 취소"):
                st.session_state[f'show_breakdown_{process["id"]}'] = False
                st.rerun()

def render_existing_breakdown_detail(existing_items, load_func, update_func, current_user):
    """기존 분할 내역 상세 표시"""
    st.markdown("---")
    st.subheader("📋 분할 내역 상세")
    
    for item in existing_items:
        with st.expander(f"📦 {item.get('item_code', 'N/A')} - {item.get('quantity', 0)}개"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**코드**: {item.get('item_code', 'N/A')}")
                st.write(f"**설명**: {item.get('item_description', 'N/A')}")
                st.write(f"**수량**: {item.get('quantity', 0)}개")
                st.write(f"**단가**: ${item.get('unit_price', 0):,.2f}")
            
            with col2:
                st.write(f"**총액**: ${item.get('line_total', 0):,.2f}")
                st.write(f"**현재 재고**: {item.get('current_stock', 0)}개")
                st.write(f"**처리 방식**: {item.get('processing_type', 'N/A')}")
                st.write(f"**상태**: {item.get('item_status', 'N/A')}")
            
            with col3:
                current_status = item.get('item_status', 'pending')
                if current_status == 'stock_checked':
                    if st.button(f"🚀 발주 처리", key=f"process_item_{item['id']}"):
                        # 간단한 처리 - 외주 발주로 설정
                        update_func('process_item_breakdown', item['id'], {
                            'item_status': 'processed',
                            'processing_type': 'external',
                            'external_quantity': item.get('quantity', 0),
                            'updated_at': datetime.now()
                        })
                        st.success("발주 처리 완료!")
                        st.rerun()
                else:
                    st.success("✅ 처리 완료")

def save_breakdown_items(process, breakdown_items, save_func, current_user):
    """코드별 분할 저장"""
    for item in breakdown_items:
        breakdown_data = {
            'sales_process_id': process['id'],
            'item_code': item['item_code'],
            'item_description': item['description'],
            'quantity': item['quantity'],
            'unit_price': process.get('unit_price', 0),
            'line_total': item['quantity'] * process.get('unit_price', 0),
            'current_stock': 0,
            'available_stock': 0,
            'item_status': 'stock_checked',
            'created_by': current_user['id'],
            'created_at': datetime.now()
        }
        
        save_func('process_item_breakdown', breakdown_data)

def show_code_breakdown_management(load_func, save_func, update_func, current_user):
    """코드별 발주 통합 관리"""
    st.subheader("🔧 코드별 발주 통합 관리")
    
    # 전체 분할 내역 조회
    breakdowns = load_func('process_item_breakdown') or []
    
    if not breakdowns:
        st.info("등록된 코드별 분할 내역이 없습니다.")
        st.write("**사용법:**")
        st.write("1. 영업 현황 탭에서 프로세스 상태를 'completed' 또는 'ordered'로 변경")
        st.write("2. '📦 코드별 분할 시작' 버튼 클릭")
        st.write("3. 상품 코드별로 수량 입력")
        return
    
    # 통계 표시
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 분할 코드", len(breakdowns))
    with col2:
        pending_count = len([b for b in breakdowns if b.get('item_status') == 'stock_checked'])
        st.metric("처리 대기", pending_count)
    with col3:
        processed_count = len([b for b in breakdowns if b.get('item_status') == 'processed'])
        st.metric("처리 완료", processed_count)
    with col4:
        completed_count = len([b for b in breakdowns if b.get('item_status') == 'completed'])
        st.metric("발주 완료", completed_count)
    
    # 분할 내역 목록
    st.write("### 📋 분할 내역 목록")
    
    for breakdown in breakdowns:
        with st.expander(f"📦 {breakdown.get('item_code', 'N/A')} - {breakdown.get('quantity', 0)}개"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**영업 프로세스 ID**: {breakdown.get('sales_process_id', 'N/A')}")
                st.write(f"**코드**: {breakdown.get('item_code', 'N/A')}")
                st.write(f"**설명**: {breakdown.get('item_description', 'N/A')}")
                st.write(f"**수량**: {breakdown.get('quantity', 0)}개")
            
            with col2:
                st.write(f"**단가**: ${breakdown.get('unit_price', 0):,.2f}")
                st.write(f"**총액**: ${breakdown.get('line_total', 0):,.2f}")
                st.write(f"**상태**: {breakdown.get('item_status', 'N/A')}")
                st.write(f"**생성일**: {breakdown.get('created_at', 'N/A')}")
            
            with col3:
                if breakdown.get('item_status') == 'stock_checked':
                    if st.button(f"🚀 발주 처리", key=f"process_breakdown_{breakdown['id']}"):
                        # 간단한 처리 - 외주 발주로 설정
                        update_func('process_item_breakdown', breakdown['id'], {
                            'item_status': 'processed',
                            'processing_type': 'external',
                            'external_quantity': breakdown.get('quantity', 0),
                            'updated_at': datetime.now()
                        })
                        st.success("발주 처리 완료!")
                        st.rerun()
                else:
                    st.success("✅ 처리 완료")

def render_system_info(load_func, current_user):
    """시스템 정보 표시"""
    with st.expander("ℹ️ 시스템 정보", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**현재 사용자**")
            st.write(f"- 이름: {current_user.get('name', 'N/A')}")
            st.write(f"- 역할: {current_user.get('role', 'N/A')}")
            st.write(f"- 부서: {current_user.get('department', 'N/A')}")
        
        with col2:
            st.write("**시스템 현황**")
            try:
                processes = load_func('sales_process') or []
                breakdowns = load_func('process_item_breakdown') or []
                
                st.write(f"- 영업 프로세스: {len(processes)}개")
                st.write(f"- 코드별 분할: {len(breakdowns)}개")
                
            except Exception as e:
                st.write(f"시스템 정보 로드 중 오류: {str(e)}")

# 기존 코드들...
def render_legacy_functions():
    """기존 함수들과의 호환성을 위한 백업 함수들"""
    pass

PROCESS_STATUSES = {
    'approved': '승인됨',
    'internal_processed': '내부 재고 처리됨',
    'external_ordered': '외주 발주됨',
    'ordered': '발주됨',
    'received': '입고됨',
    'completed': '완료됨'
}

PURCHASE_ORDER_STATUSES = {
    'ordered': '발주됨',
    'confirmed': '확정됨',
    'shipped': '출고됨',
    'received': '입고됨',
    'completed': '완료됨'
}

SHIPMENT_STATUSES = {
    'shipped': '출고됨',
    'in_transit': '배송중',
    'delivered': '배송완료',
    'returned': '반품됨'
}

BREAKDOWN_STATUSES = {
    'pending': '대기중',
    'stock_checked': '재고 확인됨',
    'processed': '처리됨',
    'completed': '완료됨'
}

def get_status_display_name(status, status_type='process'):
    """상태 코드를 한국어 표시명으로 변환"""
    status_maps = {
        'process': PROCESS_STATUSES,
        'purchase': PURCHASE_ORDER_STATUSES,
        'shipment': SHIPMENT_STATUSES,
        'breakdown': BREAKDOWN_STATUSES
    }
    return status_maps.get(status_type, {}).get(status, status)

MODULE_FUNCTIONS = {
    'dashboard': show_enhanced_sales_dashboard,
    'purchase_order': show_purchase_order_management,
    'inventory': show_inventory_management,
    'profit_analysis': show_profit_analysis,
    'code_breakdown': show_code_breakdown_management
}

MAIN_FUNCTION_INFO = {
    'function_name': 'show_sales_process_management',
    'description': '영업 프로세스 관리 통합 메인 함수 - 5개 탭 + 코드별 발주 기능',
    'tabs': [
        '📊 영업 현황',
        '📦 발주 관리', 
        '📋 재고 관리',
        '💰 수익 분석',
        '🔧 코드별 발주'
    ]
}