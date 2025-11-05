import streamlit as st
from datetime import datetime

def get_connection():
    """Supabase 연결 반환"""
    return st.session_state.get('supabase')

def get_all_pending_specs():
    """모든 법인의 승인 대기 중인 Hot Runner 주문서 조회"""
    supabase = get_connection()
    all_specs = []
    
    for company in ['ymv', 'ymk', 'ymth', 'ymc']:
        try:
            # Hot Runner 주문서 조회
            response = supabase.table(f"hot_runner_orders_{company}").select("""
                id,
                order_number,
                customer_id,
                customer_name,
                project_name,
                part_name,
                order_type,
                order_amount,
                status,
                created_at,
                created_by
            """).eq("status", "pending").order("created_at", desc=True).execute()
            
            if response.data:
                # 법인 코드 추가
                for spec in response.data:
                    spec['company_code'] = company.upper()
                    all_specs.append(spec)
        
        except Exception as e:
            st.warning(f"{company.upper()} 조회 실패: {str(e)}")
            continue
    
    return all_specs

def approve_spec_decision(spec_id, company_code, approver_id):
    """Hot Runner 주문서 승인"""
    supabase = get_connection()
    table_name = f"hot_runner_orders_{company_code.lower()}"
    
    try:
        update_data = {
            'id': spec_id,
            'status': 'approved',
            'reviewed_by': approver_id,
            'reviewed_at': datetime.now().isoformat()
        }
        
        response = supabase.table(table_name).update(update_data).eq("id", spec_id).execute()
        return response.data
    except Exception as e:
        st.error(f"승인 실패: {str(e)}")
        raise e

def reject_spec_decision(spec_id, company_code, approver_id, reason):
    """Hot Runner 주문서 반려"""
    supabase = get_connection()
    table_name = f"hot_runner_orders_{company_code.lower()}"
    
    try:
        update_data = {
            'id': spec_id,
            'status': 'rejected',
            'reviewed_by': approver_id,
            'reviewed_at': datetime.now().isoformat(),
            'rejection_reason': reason
        }
        
        response = supabase.table(table_name).update(update_data).eq("id", spec_id).execute()
        return response.data
    except Exception as e:
        st.error(f"반려 실패: {str(e)}")
        raise e

def spec_decision_approval():
    """Hot Runner 주문서 승인 페이지 (YMK/CEO 전용)"""
    st.subheader("✅ Hot Runner 주문서 승인 (YMK)")
    
    # 현재 유저 정보 가져오기
    current_user = st.session_state.get('current_user', {})
    user_company = current_user.get('company', 'YMV')
    user_role = current_user.get('role', 'Employee')
    
    # CEO는 모든 법인 접근 가능, 일반 유저는 YMK만
    if user_role != 'CEO' and user_company != 'YMK':
        st.error("⛔ YMK 법인 또는 CEO만 접근 가능합니다.")
        return
    
    # 승인 대기 목록 조회
    specs = get_all_pending_specs()
    
    if not specs:
        st.info("승인 대기 중인 주문서가 없습니다.")
        return
    
    st.write(f"**총 {len(specs)}건의 승인 대기 건이 있습니다.**")
    
    # 법인별 필터
    col1, col2 = st.columns([2, 8])
    with col1:
        company_filter = st.selectbox(
            "법인 필터",
            options=["전체", "YMV", "YMK", "YMTH", "YMC"]
        )
    
    # 필터 적용
    filtered_specs = specs if company_filter == "전체" else [s for s in specs if s['company_code'] == company_filter]
    
    if not filtered_specs:
        st.info(f"{company_filter} 법인의 승인 대기 건이 없습니다.")
        return
    
    # 테이블 데이터 준비
    table_data = []
    for spec in filtered_specs:
        table_data.append({
            '법인': spec['company_code'],
            '주문번호': spec['order_number'],
            '고객사': spec['customer_name'],
            '프로젝트': spec.get('project_name', 'N/A'),
            '부품명': spec.get('part_name', 'N/A'),
            '주문타입': spec.get('order_type', 'N/A'),
            '금액': f"{spec.get('order_amount', 0):,.0f}" if spec.get('order_amount') else 'N/A',
            '작성일': spec['created_at'][:10] if spec['created_at'] else ''
        })
    
    # 목록 표시
    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )
    
    # 상세 보기 및 승인/반려
    st.divider()
    st.subheader("📋 상세 검토 및 승인")
    
    spec_options = {f"{s['company_code']} - {s['order_number']}": (s['id'], s['company_code']) for s in filtered_specs}
    
    if not spec_options:
        return
    
    selected_spec = st.selectbox("검토할 주문서 선택", options=list(spec_options.keys()))
    
    if selected_spec:
        spec_id, company_code = spec_options[selected_spec]
        detail = next(s for s in filtered_specs if s['id'] == spec_id and s['company_code'] == company_code)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📋 기본 정보**")
            st.write(f"법인: {detail['company_code']}")
            st.write(f"주문번호: {detail['order_number']}")
            st.write(f"고객사: {detail['customer_name']}")
            st.write(f"프로젝트: {detail.get('project_name', 'N/A')}")
            st.write(f"부품명: {detail.get('part_name', 'N/A')}")
            st.write(f"주문타입: {detail.get('order_type', 'N/A')}")
            st.write(f"금액: {detail.get('order_amount', 0):,.0f}" if detail.get('order_amount') else "N/A")
        
        with col2:
            st.write("**📅 작성자 정보**")
            st.write(f"작성자: {detail['created_by']}")
            st.write(f"작성일: {detail['created_at'][:10] if detail['created_at'] else ''}")
        
        # 승인/반려 버튼
        st.divider()
        col1, col2, col3 = st.columns([3, 3, 4])
        
        with col1:
            if st.button("✅ 승인", type="primary", use_container_width=True):
                try:
                    approve_spec_decision(
                        spec_id, 
                        company_code, 
                        st.session_state.get('user_id')
                    )
                    st.success(f"✅ {detail['order_number']} 승인 완료!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 승인 실패: {str(e)}")
        
        with col2:
            if st.button("❌ 반려", type="secondary", use_container_width=True):
                st.session_state['show_reject_reason'] = True
        
        # 반려 사유 입력
        if st.session_state.get('show_reject_reason', False):
            st.write("**반려 사유 입력**")
            reject_reason = st.text_area("사유", height=100, key="reject_reason_input")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("반려 확정", type="primary"):
                    if not reject_reason.strip():
                        st.error("반려 사유를 입력해주세요.")
                    else:
                        try:
                            reject_spec_decision(
                                spec_id,
                                company_code,
                                st.session_state.get('user_id'),
                                reject_reason
                            )
                            st.success(f"❌ {detail['order_number']} 반려 완료!")
                            st.session_state['show_reject_reason'] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 반려 처리 실패: {str(e)}")
            
            with col2:
                if st.button("취소"):
                    st.session_state['show_reject_reason'] = False
                    st.rerun()