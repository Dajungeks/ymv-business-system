import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def get_db_client():
    """Supabase 클라이언트 가져오기"""
    if 'supabase' not in st.session_state:
        st.error("Supabase 연결이 초기화되지 않았습니다.")
        return None
    return st.session_state.supabase


def render_ymk_approval_interface():
    """YMK 승인 인터페이스 - 제출된 규격 결정서 승인/반려"""
    
    st.title("🔍 규격 결정서 승인 관리")
    st.markdown("---")
    
    # 세션 상태 초기화
    if 'selected_orders' not in st.session_state:
        st.session_state.selected_orders = []
    if 'expanded_order_id' not in st.session_state:
        st.session_state.expanded_order_id = None
    
    # 검색 필터
    render_search_filters()
    
    # 목록 조회
    orders_df = fetch_submitted_orders()
    
    if orders_df.empty:
        st.info("📋 제출된 규격 결정서가 없습니다.")
        return
    
    # 목록 표시
    render_orders_table(orders_df)
    
    # 일괄 처리 버튼
    render_bulk_actions(orders_df)


def render_search_filters():
    """검색 필터 영역"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        company_filter = st.selectbox(
            "법인",
            options=["전체", "YMV", "YMTH", "YMK"],
            key="company_filter"
        )
    
    with col2:
        status_filter = st.selectbox(
            "상태",
            options=["전체", "제출됨", "승인됨", "반려됨"],
            key="status_filter"
        )
    
    with col3:
        date_from = st.date_input(
            "시작일",
            value=datetime.now() - timedelta(days=30),
            key="date_from"
        )
    
    with col4:
        date_to = st.date_input(
            "종료일",
            value=datetime.now(),
            key="date_to"
        )
    
    # 검색어
    search_text = st.text_input(
        "🔍 검색 (주문번호, 프로젝트명, 고객사)",
        placeholder="검색어를 입력하세요",
        key="search_text"
    )


def fetch_submitted_orders():
    """제출된 규격 결정서 조회"""
    
    client = get_db_client()
    if not client:
        return pd.DataFrame()
    
    try:
        # 기본 쿼리
        query = client.table('hot_runner_orders').select(
            'id, order_number, project_name, customer_name, part_name, '
            'status, submitted_at, created_at, company, '
            'reviewed_at, rejection_reason'
        )
        
        # 상태 필터
        status_filter = st.session_state.get('status_filter', '전체')
        if status_filter == '제출됨':
            query = query.eq('status', 'submitted')
        elif status_filter == '승인됨':
            query = query.eq('status', 'approved')
        elif status_filter == '반려됨':
            query = query.eq('status', 'rejected')
        else:
            query = query.in_('status', ['submitted', 'approved', 'rejected'])
        
        # 법인 필터
        company_filter = st.session_state.get('company_filter', '전체')
        if company_filter != '전체':
            query = query.eq('company', company_filter)
        
        # 날짜 필터
        date_from = st.session_state.get('date_from')
        date_to = st.session_state.get('date_to')
        
        if date_from:
            query = query.gte('submitted_at', date_from.isoformat())
        
        if date_to:
            query = query.lte('submitted_at', date_to.isoformat())
        
        # 검색어 필터
        search_text = st.session_state.get('search_text', '').strip()
        if search_text:
            query = query.or_(
                f'order_number.ilike.%{search_text}%,'
                f'project_name.ilike.%{search_text}%,'
                f'customer_name.ilike.%{search_text}%'
            )
        
        query = query.order('submitted_at', desc=True)
        
        response = query.execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        # 날짜 컬럼 변환
        if 'submitted_at' in df.columns:
            df['submitted_at'] = pd.to_datetime(df['submitted_at'])
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        if 'reviewed_at' in df.columns:
            df['reviewed_at'] = pd.to_datetime(df['reviewed_at'])
        
        return df
        
    except Exception as e:
        st.error(f"❌ 데이터 조회 오류: {e}")
        return pd.DataFrame()


def render_orders_table(orders_df):
    """규격 결정서 목록 테이블"""
    
    st.markdown("### 📋 규격 결정서 목록")
    st.markdown(f"**총 {len(orders_df)}건**")
    
    # 전체 선택 체크박스
    col_select_all, col_label = st.columns([1, 20])
    with col_select_all:
        select_all = st.checkbox("전체", key="select_all_orders")
    
    if select_all:
        st.session_state.selected_orders = orders_df['id'].tolist()
    
    # 테이블 헤더
    header_cols = st.columns([1, 3, 2, 3, 3, 2, 2, 2])
    headers = ["선택", "주문번호", "법인", "프로젝트명", "고객사", "제출일", "상태", "상세"]
    
    for col, header in zip(header_cols, headers):
        col.markdown(f"**{header}**")
    
    st.markdown("---")
    
    # 데이터 행
    for idx, row in orders_df.iterrows():
        render_order_row(row, idx)


def render_order_row(row, idx):
    """개별 주문 행 렌더링"""
    
    cols = st.columns([1, 3, 2, 3, 3, 2, 2, 2])
    
    # 체크박스
    with cols[0]:
        is_selected = st.checkbox(
            "선택",
            value=row['id'] in st.session_state.selected_orders,
            key=f"check_{row['id']}",
            label_visibility="collapsed"
        )
        
        if is_selected and row['id'] not in st.session_state.selected_orders:
            st.session_state.selected_orders.append(row['id'])
        elif not is_selected and row['id'] in st.session_state.selected_orders:
            st.session_state.selected_orders.remove(row['id'])
    
    # 주문번호
    with cols[1]:
        st.text(row['order_number'] if row['order_number'] else '-')
    
    # 법인
    with cols[2]:
        st.markdown(f"**{row['company']}**")
    
    # 프로젝트명
    with cols[3]:
        st.text(row['project_name'] if row['project_name'] else '-')
    
    # 고객사
    with cols[4]:
        st.text(row['customer_name'] if row['customer_name'] else '-')
    
    # 제출일
    with cols[5]:
        if pd.notna(row['submitted_at']):
            st.text(row['submitted_at'].strftime('%Y-%m-%d'))
        else:
            st.text('-')
    
    # 상태
    with cols[6]:
        status_display = {
            'submitted': '🟡 제출됨',
            'approved': '🟢 승인됨',
            'rejected': '🔴 반려됨'
        }
        st.markdown(status_display.get(row['status'], row['status']))
    
    # 상세보기 버튼
    with cols[7]:
        if st.button("📄 상세", key=f"detail_{row['id']}"):
            if st.session_state.expanded_order_id == row['id']:
                st.session_state.expanded_order_id = None
            else:
                st.session_state.expanded_order_id = row['id']
            st.rerun()
    
    # 상세보기 확장
    if st.session_state.expanded_order_id == row['id']:
        render_order_detail(row['id'])
    
    st.markdown("---")


def render_order_detail(order_id):
    """규격 결정서 상세 정보"""
    
    with st.container():
        st.markdown("#### 📋 규격 결정서 상세")
        
        # 상세 정보 조회
        order_detail = fetch_order_detail(order_id)
        
        if not order_detail:
            st.error("상세 정보를 불러올 수 없습니다.")
            return
        
        # 기본 정보
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**주문번호:** {order_detail.get('order_number', '-')}")
            st.markdown(f"**법인:** {order_detail.get('company', '-')}")
            st.markdown(f"**고객사:** {order_detail.get('customer_name', '-')}")
        
        with col2:
            st.markdown(f"**프로젝트명:** {order_detail.get('project_name', '-')}")
            st.markdown(f"**품명:** {order_detail.get('part_name', '-')}")
            st.markdown(f"**금형번호:** {order_detail.get('mold_no', '-')}")
        
        with col3:
            st.markdown(f"**YMV No:** {order_detail.get('ymv_no', '-')}")
            submitted_at = order_detail.get('submitted_at')
            if submitted_at:
                st.markdown(f"**제출일:** {submitted_at.strftime('%Y-%m-%d') if isinstance(submitted_at, datetime) else submitted_at}")
            st.markdown(f"**상태:** {order_detail.get('status', '-')}")
        
        st.markdown("---")
        
        # 기술 사양
        st.markdown("##### 기술 사양")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**사출기 톤수:** {order_detail.get('injection_ton', '-')}")
            st.markdown(f"**수지:** {order_detail.get('resin', '-')}")
            st.markdown(f"**주문 유형:** {order_detail.get('order_type', '-')}")
        
        with col2:
            st.markdown(f"**매니폴드 타입:** {order_detail.get('manifold_type', '-')}")
            st.markdown(f"**실린더 타입:** {order_detail.get('cylinder_type', '-')}")
            st.markdown(f"**센서 타입:** {order_detail.get('sensor_type', '-')}")
        
        st.markdown("---")
        
        # 승인/반려 버튼 (제출됨 상태일 때만)
        if order_detail.get('status') == 'submitted':
            col1, col2, col3 = st.columns([1, 1, 8])
            
            with col1:
                if st.button("✅ 승인", key=f"approve_detail_{order_id}", type="primary"):
                    approve_orders([order_id])
                    st.session_state.expanded_order_id = None
                    st.rerun()
            
            with col2:
                if st.button("❌ 반려", key=f"reject_detail_{order_id}"):
                    st.session_state[f'show_reject_reason_{order_id}'] = True
            
            # 반려 사유 입력
            if st.session_state.get(f'show_reject_reason_{order_id}', False):
                rejection_reason = st.text_area(
                    "반려 사유",
                    key=f"rejection_reason_{order_id}",
                    placeholder="반려 사유를 입력하세요"
                )
                
                col_confirm, col_cancel, _ = st.columns([1, 1, 8])
                
                with col_confirm:
                    if st.button("확인", key=f"confirm_reject_{order_id}"):
                        if rejection_reason.strip():
                            reject_orders([order_id], rejection_reason)
                            st.session_state.expanded_order_id = None
                            del st.session_state[f'show_reject_reason_{order_id}']
                            st.rerun()
                        else:
                            st.error("반려 사유를 입력하세요.")
                
                with col_cancel:
                    if st.button("취소", key=f"cancel_reject_{order_id}"):
                        del st.session_state[f'show_reject_reason_{order_id}']
                        st.rerun()
        
        # 승인/반려 정보 표시
        elif order_detail.get('status') in ['approved', 'rejected']:
            st.markdown("##### 처리 정보")
            reviewed_at = order_detail.get('reviewed_at')
            if reviewed_at:
                st.markdown(f"**처리일:** {reviewed_at.strftime('%Y-%m-%d') if isinstance(reviewed_at, datetime) else reviewed_at}")
            
            if order_detail.get('status') == 'rejected':
                st.markdown(f"**반려 사유:** {order_detail.get('rejection_reason', '-')}")


def fetch_order_detail(order_id):
    """규격 결정서 상세 조회"""
    
    client = get_db_client()
    if not client:
        return None
    
    try:
        response = client.table('hot_runner_orders').select('*').eq('id', order_id).execute()
        
        if response.data:
            return response.data[0]
        
        return None
        
    except Exception as e:
        st.error(f"❌ 상세 정보 조회 오류: {e}")
        return None


def render_bulk_actions(orders_df):
    """일괄 처리 버튼 영역"""
    
    if not st.session_state.selected_orders:
        return
    
    st.markdown("---")
    st.markdown(f"### 선택된 항목: **{len(st.session_state.selected_orders)}건**")
    
    col1, col2, col3 = st.columns([2, 2, 6])
    
    with col1:
        if st.button("✅ 선택 항목 일괄 승인", type="primary", use_container_width=True):
            approve_orders(st.session_state.selected_orders)
            st.session_state.selected_orders = []
            st.rerun()
    
    with col2:
        if st.button("❌ 선택 항목 일괄 반려", use_container_width=True):
            st.session_state.show_bulk_reject = True
    
    # 일괄 반려 사유 입력
    if st.session_state.get('show_bulk_reject', False):
        st.markdown("---")
        
        bulk_rejection_reason = st.text_area(
            "반려 사유 (일괄 적용)",
            key="bulk_rejection_reason",
            placeholder="반려 사유를 입력하세요"
        )
        
        col_confirm, col_cancel, _ = st.columns([1, 1, 8])
        
        with col_confirm:
            if st.button("확인", key="confirm_bulk_reject"):
                if bulk_rejection_reason.strip():
                    reject_orders(st.session_state.selected_orders, bulk_rejection_reason)
                    st.session_state.selected_orders = []
                    st.session_state.show_bulk_reject = False
                    st.rerun()
                else:
                    st.error("반려 사유를 입력하세요.")
        
        with col_cancel:
            if st.button("취소", key="cancel_bulk_reject"):
                st.session_state.show_bulk_reject = False
                st.rerun()


def approve_orders(order_ids):
    """규격 결정서 승인 처리"""
    
    client = get_db_client()
    if not client:
        return
    
    try:
        # 현재 사용자 정보
        user_id = st.session_state.user_info['id']
        reviewed_at = datetime.now().isoformat()
        
        for order_id in order_ids:
            client.table('hot_runner_orders').update({
                'status': 'approved',
                'reviewed_by': user_id,
                'reviewed_at': reviewed_at,
                'updated_at': reviewed_at
            }).eq('id', order_id).eq('status', 'submitted').execute()
        
        st.success(f"✅ {len(order_ids)}건의 규격 결정서가 승인되었습니다.")
        
    except Exception as e:
        st.error(f"❌ 승인 처리 오류: {e}")


def reject_orders(order_ids, rejection_reason):
    """규격 결정서 반려 처리"""
    
    client = get_db_client()
    if not client:
        return
    
    try:
        # 현재 사용자 정보
        user_id = st.session_state.user_info['id']
        reviewed_at = datetime.now().isoformat()
        
        for order_id in order_ids:
            client.table('hot_runner_orders').update({
                'status': 'rejected',
                'reviewed_by': user_id,
                'reviewed_at': reviewed_at,
                'rejection_reason': rejection_reason,
                'updated_at': reviewed_at
            }).eq('id', order_id).eq('status', 'submitted').execute()
        
        st.success(f"✅ {len(order_ids)}건의 규격 결정서가 반려되었습니다.")
        
    except Exception as e:
        st.error(f"❌ 반려 처리 오류: {e}")