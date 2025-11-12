import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import logging

# 활동 유형 매핑
ACTIVITY_TYPES = {
    'meeting': '🤝 미팅 / Họp',
    'visit': '🏢 방문 / Thăm',
    'call': '📞 통화 / Gọi',
    'email': '📧 이메일 / Email',
    'quotation': '💰 견적 / Báo giá',
    'demo': '🎬 데모 / Demo',
    'negotiation': '🤝 협상 / Đàm phán',
    'contract': '📝 계약 / Hợp đồng',
    'complaint': '⚠️ 클레임 / Khiếu nại',
    'followup': '📋 팔로업 / Theo dõi',
    'other': '📌 기타 / Khác'
}

# 활동 유형 역매핑
ACTIVITY_TYPES_REVERSE = {v: k for k, v in ACTIVITY_TYPES.items()}

# 중요도
IMPORTANCE_LEVELS = {
    'high': '🔴 높음 / Cao',
    'normal': '🟡 보통 / Bình thường',
    'low': '🟢 낮음 / Thấp'
}

IMPORTANCE_REVERSE = {v: k for k, v in IMPORTANCE_LEVELS.items()}

# 상태
STATUS_OPTIONS = {
    'scheduled': '📅 예정 / Đã lên lịch',
    'completed': '✅ 완료 / Hoàn thành',
    'cancelled': '❌ 취소 / Đã hủy'
}

STATUS_REVERSE = {v: k for k, v in STATUS_OPTIONS.items()}

def render_activity_edit_form(activity, update_func, activity_table, customer_table, load_customers_func):
    """영업 활동 수정 폼"""
    activity_id = activity['id']
    st.subheader(f"✏️ 영업 활동 수정 / Chỉnh sửa hoạt động")
    
    # 안전한 값 가져오기
    def safe_get(key, default=''):
        value = activity.get(key)
        if pd.isna(value) or value is None:
            return default
        return str(value).strip() if str(value).strip() else default
    
    # 고객 정보 로드
    customers = load_customers_func(customer_table)
    customer_id = activity.get('customer_id')
    
    # 고객명 찾기
    customer_name = 'N/A'
    for customer in customers:
        if customer['id'] == customer_id:
            customer_name = customer.get('company_name_short') or customer.get('company_name_original')
            break
    
    st.info(f"✅ **고객:** {customer_name}")
    
    with st.form("activity_edit_form"):
        st.markdown("#### 📋 기본 정보 / Thông tin cơ bản")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 활동 유형
            current_type = safe_get('activity_type')
            type_ui_value = ACTIVITY_TYPES.get(current_type, list(ACTIVITY_TYPES.values())[0])
            type_list = list(ACTIVITY_TYPES.values())
            type_index = type_list.index(type_ui_value) if type_ui_value in type_list else 0
            
            activity_type_ui = st.selectbox(
                "활동 유형 * / Loại hoạt động *",
                options=type_list,
                index=type_index,
                key="edit_activity_type"
            )
            
            # 활동 날짜
            current_date = safe_get('activity_date')
            if current_date:
                try:
                    activity_date = st.date_input(
                        "활동 날짜 * / Ngày hoạt động *",
                        value=pd.to_datetime(current_date).date(),
                        key="edit_activity_date"
                    )
                except:
                    activity_date = st.date_input(
                        "활동 날짜 * / Ngày hoạt động *",
                        value=date.today(),
                        key="edit_activity_date"
                    )
            else:
                activity_date = st.date_input(
                    "활동 날짜 * / Ngày hoạt động *",
                    value=date.today(),
                    key="edit_activity_date"
                )
        
        with col2:
            # 중요도
            current_importance = safe_get('importance', 'normal')
            importance_ui_value = IMPORTANCE_LEVELS.get(current_importance, list(IMPORTANCE_LEVELS.values())[1])
            importance_list = list(IMPORTANCE_LEVELS.values())
            importance_index = importance_list.index(importance_ui_value) if importance_ui_value in importance_list else 1
            
            importance_ui = st.selectbox(
                "중요도 / Mức độ quan trọng",
                options=importance_list,
                index=importance_index,
                key="edit_activity_importance"
            )
            
            # 상태
            current_status = safe_get('status', 'completed')
            status_ui_value = STATUS_OPTIONS.get(current_status, list(STATUS_OPTIONS.values())[1])
            status_list = list(STATUS_OPTIONS.values())
            status_index = status_list.index(status_ui_value) if status_ui_value in status_list else 1
            
            status_ui = st.selectbox(
                "상태 / Trạng thái",
                options=status_list,
                index=status_index,
                key="edit_activity_status"
            )
        
        # 제목
        subject = st.text_input(
            "제목 * / Tiêu đề *",
            value=safe_get('subject'),
            key="edit_activity_subject"
        )
        
        st.markdown("#### 👥 미팅 정보 / Thông tin cuộc họp")
        
        col1, col2 = st.columns(2)
        
        with col1:
            meeting_with = st.text_input(
                "만난 사람 (고객 측) / Người gặp",
                value=safe_get('meeting_with'),
                key="edit_meeting_with"
            )
            
            meeting_with_position = st.text_input(
                "직책/부서 / Chức vụ",
                value=safe_get('meeting_with_position'),
                key="edit_meeting_with_position"
            )
        
        with col2:
            meeting_location = st.text_input(
                "미팅 장소 / Địa điểm",
                value=safe_get('meeting_location'),
                key="edit_meeting_location"
            )
            
            primary_contact = st.text_input(
                "주 담당자 (우리 측) / Người phụ trách",
                value=safe_get('primary_contact'),
                key="edit_primary_contact"
            )
        
        # 우리 측 참석자
        our_attendees_value = activity.get('our_attendees')
        if our_attendees_value:
            if isinstance(our_attendees_value, list):
                our_attendees_str = ', '.join(our_attendees_value)
            else:
                our_attendees_str = str(our_attendees_value)
        else:
            our_attendees_str = ''
        
        our_attendees = st.text_area(
            "우리 측 참석자 (쉼표로 구분) / Người tham dự",
            value=our_attendees_str,
            key="edit_our_attendees",
            height=60
        )
        
        st.markdown("#### 📄 활동 내용 / Nội dung hoạt động")
        
        description = st.text_area(
            "상세 내용 / Chi tiết",
            value=safe_get('description'),
            key="edit_activity_description",
            height=150
        )
        
        st.markdown("#### 📊 결과 및 후속 조치 / Kết quả và hành động tiếp theo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            outcome = st.text_area(
                "미팅 결과 / Kết quả",
                value=safe_get('outcome'),
                key="edit_activity_outcome",
                height=100
            )
        
        with col2:
            next_action = st.text_area(
                "다음 액션 / Hành động tiếp theo",
                value=safe_get('next_action'),
                key="edit_next_action",
                height=100
            )
        
        # 다음 액션 예정일
        next_action_date_value = activity.get('next_action_date')
        if next_action_date_value:
            try:
                next_action_date = st.date_input(
                    "다음 액션 예정일 / Ngày dự kiến",
                    value=pd.to_datetime(next_action_date_value).date(),
                    key="edit_next_action_date"
                )
            except:
                next_action_date = st.date_input(
                    "다음 액션 예정일 / Ngày dự kiến",
                    value=None,
                    key="edit_next_action_date"
                )
        else:
            next_action_date = st.date_input(
                "다음 액션 예정일 / Ngày dự kiến",
                value=None,
                key="edit_next_action_date"
            )
        
        # 태그
        tags_value = activity.get('tags')
        if tags_value:
            if isinstance(tags_value, list):
                tags_str = ', '.join(tags_value)
            else:
                tags_str = str(tags_value)
        else:
            tags_str = ''
        
        tags_input = st.text_input(
            "태그 (쉼표로 구분) / Tags",
            value=tags_str,
            key="edit_activity_tags"
        )
        
        # 버튼
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 수정 저장 / Lưu thay đổi", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ 취소 / Hủy", use_container_width=True)
        
        if cancelled:
            st.session_state[f"edit_activity_{activity_id}"] = False
            st.rerun()
        
        if submitted:
            if not subject:
                st.error("❌ 제목은 필수 항목입니다.")
                return
            
            # 업데이트 데이터 구성
            updated_data = {
                'id': activity_id,
                'customer_id': customer_id,
                'activity_date': activity_date.isoformat(),
                'activity_type': ACTIVITY_TYPES_REVERSE.get(activity_type_ui),
                'subject': subject.strip(),
                'description': description.strip() if description and description.strip() else None,
                'meeting_with': meeting_with.strip() if meeting_with and meeting_with.strip() else None,
                'meeting_with_position': meeting_with_position.strip() if meeting_with_position and meeting_with_position.strip() else None,
                'meeting_location': meeting_location.strip() if meeting_location and meeting_location.strip() else None,
                'primary_contact': primary_contact.strip() if primary_contact and primary_contact.strip() else None,
                'our_attendees': [a.strip() for a in our_attendees.split(',')] if our_attendees and our_attendees.strip() else None,
                'outcome': outcome.strip() if outcome and outcome.strip() else None,
                'next_action': next_action.strip() if next_action and next_action.strip() else None,
                'next_action_date': next_action_date.isoformat() if next_action_date else None,
                'status': STATUS_REVERSE.get(status_ui),
                'importance': IMPORTANCE_REVERSE.get(importance_ui),
                'tags': [t.strip() for t in tags_input.split(',')] if tags_input and tags_input.strip() else None,
                'updated_at': datetime.now().isoformat()
            }
            
            # 데이터 업데이트
            result = update_func(activity_table, updated_data)
            
            if result:
                st.success("✅ 영업 활동이 성공적으로 수정되었습니다.")
                st.session_state[f"edit_activity_{activity_id}"] = False
                st.rerun()
            else:
                st.error("❌ 수정 중 오류가 발생했습니다.")


def show_sales_activity(load_func, save_func, update_func, delete_func, 
                        load_customers_func, current_user):
    """영업 활동 관리 메인 페이지"""
    st.title("📅 영업 활동 관리 / Quản lý hoạt động bán hàng")
    
    # 법인별 테이블명
    from utils.helpers import get_company_table
    
    company_code = current_user.get('company')
    if not company_code:
        st.error("법인 정보가 없습니다.")
        return
    
    activity_table = get_company_table('sales_activities', company_code)
    customer_table = get_company_table('customers', company_code)
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "활동 등록 / Đăng ký",
        "활동 목록 / Danh sách",
        "고객별 타임라인 / Timeline KH",
        "방문 통계 / Thống kê"
    ])
    
    with tab1:
        render_activity_form(save_func, activity_table, customer_table, load_customers_func)
    
    with tab2:
        render_activity_list(load_func, update_func, delete_func, 
                            activity_table, customer_table, load_customers_func)
    
    with tab3:
        render_customer_timeline_search(load_func, activity_table, customer_table, load_customers_func)
    
    with tab4:
        render_visit_statistics(load_func, activity_table, customer_table, load_customers_func)

def render_activity_form(save_func, activity_table, customer_table, load_customers_func):
    """영업 활동 등록 폼 (고객 검색 방식)"""
    st.subheader("📝 영업 활동 등록 / Đăng ký hoạt động")
    
    # 고객 목록 로드
    customers = load_customers_func(customer_table)
    
    if not customers:
        st.warning("등록된 고객이 없습니다. 먼저 고객을 등록해주세요.")
        return
    
    # ⭐ 고객 검색 섹션 (폼 외부)
    st.markdown("#### 🔍 고객 검색 / Tìm khách hàng")
    
    search_col1, search_col2 = st.columns([4, 1])
    
    with search_col1:
        customer_search = st.text_input(
            "고객명 검색 / Tìm tên khách hàng",
            placeholder="회사명 입력 후 Enter (예: Samsung, LG, DUY TAN 등)",
            key="activity_customer_search"
        )
    
    with search_col2:
        search_btn = st.button("🔍 검색", use_container_width=True, type="secondary", key="btn_search_for_activity")
    
    # 검색 실행
    selected_customer_id = None
    selected_customer_name = None
    
    if customer_search and customer_search.strip():
        search_query = customer_search.strip().lower()
        
        # 고객 검색
        matched_customers = []
        for customer in customers:
            name_original = (customer.get('company_name_original') or '').lower()
            name_short = (customer.get('company_name_short') or '').lower()
            name_english = (customer.get('company_name_english') or '').lower()
            
            if (search_query in name_original or 
                search_query in name_short or 
                search_query in name_english):
                matched_customers.append(customer)
        
        # 검색 결과
        if matched_customers:
            st.success(f"✅ 검색 결과: **{len(matched_customers)}**개 고객")
            
            # 검색 결과에서 선택
            for customer in matched_customers[:5]:  # 최대 5개만 표시
                customer_id = customer['id']
                name = customer.get('company_name_short') or customer.get('company_name_original')
                country = customer.get('country', 'N/A')
                city = customer.get('city', 'N/A')
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{name}** ({country} - {city})")
                
                with col2:
                    if st.button("선택", key=f"select_customer_{customer_id}", use_container_width=True):
                        st.session_state['selected_customer_for_activity'] = {
                            'id': customer_id,
                            'name': name
                        }
                        st.rerun()
            
            if len(matched_customers) > 5:
                st.caption(f"...외 {len(matched_customers) - 5}개 고객 (검색어를 더 구체적으로 입력하세요)")
        else:
            st.warning(f"❌ '{customer_search}' 검색 결과가 없습니다.")
    
    # 선택된 고객 표시
    if 'selected_customer_for_activity' in st.session_state:
        selected_customer_id = st.session_state['selected_customer_for_activity']['id']
        selected_customer_name = st.session_state['selected_customer_for_activity']['name']
        
        st.info(f"✅ **선택된 고객:** {selected_customer_name}")
        
        if st.button("❌ 고객 선택 취소", key="btn_clear_customer"):
            del st.session_state['selected_customer_for_activity']
            st.rerun()
    
    st.markdown("---")
    
    # 고객이 선택되지 않으면 폼 비활성화
    if not selected_customer_id:
        st.warning("⚠️ 먼저 고객을 검색하고 선택해주세요.")
        return
    
    # ⭐ 활동 등록 폼 (고객 선택 후에만 표시)
    with st.form("activity_form", clear_on_submit=True):
        st.markdown("#### 📋 기본 정보 / Thông tin cơ bản")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 활동 유형
            activity_type_ui = st.selectbox(
                "활동 유형 * / Loại hoạt động *",
                options=list(ACTIVITY_TYPES.values()),
                key="activity_type"
            )
            
            # 활동 날짜
            activity_date = st.date_input(
                "활동 날짜 * / Ngày hoạt động *",
                value=date.today(),
                key="activity_date"
            )
        
        with col2:
            # 중요도
            importance_ui = st.selectbox(
                "중요도 / Mức độ quan trọng",
                options=list(IMPORTANCE_LEVELS.values()),
                index=1,
                key="activity_importance"
            )
            
            # 상태
            status_ui = st.selectbox(
                "상태 / Trạng thái",
                options=list(STATUS_OPTIONS.values()),
                index=1,
                key="activity_status"
            )
        
        # 제목
        subject = st.text_input(
            "제목 * / Tiêu đề *",
            placeholder="활동 제목 입력",
            key="activity_subject"
        )
        
        st.markdown("#### 👥 미팅 정보 / Thông tin cuộc họp")
        
        col1, col2 = st.columns(2)
        
        with col1:
            meeting_with = st.text_input(
                "만난 사람 (고객 측) / Người gặp",
                placeholder="Mr. Kim",
                key="meeting_with"
            )
            
            meeting_with_position = st.text_input(
                "직책/부서 / Chức vụ",
                placeholder="구매팀 차장",
                key="meeting_with_position"
            )
        
        with col2:
            meeting_location = st.text_input(
                "미팅 장소 / Địa điểm",
                placeholder="고객사 회의실",
                key="meeting_location"
            )
            
            primary_contact = st.text_input(
                "주 담당자 (우리 측) / Người phụ trách",
                placeholder="김영희",
                key="primary_contact"
            )
        
        # 우리 측 참석자
        our_attendees = st.text_area(
            "우리 측 참석자 (쉼표로 구분) / Người tham dự",
            placeholder="김영희, 이철수, 박민수",
            key="our_attendees",
            height=60
        )
        
        st.markdown("#### 📄 활동 내용 / Nội dung hoạt động")
        
        description = st.text_area(
            "상세 내용 / Chi tiết",
            placeholder="미팅 내용, 논의 사항 등을 입력하세요",
            key="activity_description",
            height=150
        )
        
        st.markdown("#### 📊 결과 및 후속 조치 / Kết quả và hành động tiếp theo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            outcome = st.text_area(
                "미팅 결과 / Kết quả",
                placeholder="미팅 결과, 의사결정 내용",
                key="activity_outcome",
                height=100
            )
        
        with col2:
            next_action = st.text_area(
                "다음 액션 / Hành động tiếp theo",
                placeholder="견적서 발송, 재방문 등",
                key="next_action",
                height=100
            )
        
        next_action_date = st.date_input(
            "다음 액션 예정일 / Ngày dự kiến",
            value=None,
            key="next_action_date"
        )
        
        # 태그
        tags_input = st.text_input(
            "태그 (쉼표로 구분) / Tags",
            placeholder="계약논의, 기술미팅, 클레임",
            key="activity_tags"
        )
        
        # 제출 버튼
        submitted = st.form_submit_button("💾 등록 / Đăng ký", use_container_width=True)
        
        if submitted:
            # 필수 항목 검증
            if not subject:
                st.error("❌ 제목은 필수 항목입니다.")
                return
            
            # 활동 데이터 구성
            activity_data = {
                'customer_id': selected_customer_id,
                'activity_date': activity_date.isoformat(),
                'activity_type': ACTIVITY_TYPES_REVERSE.get(activity_type_ui),
                'subject': subject.strip(),
                'description': description.strip() if description and description.strip() else None,
                'meeting_with': meeting_with.strip() if meeting_with and meeting_with.strip() else None,
                'meeting_with_position': meeting_with_position.strip() if meeting_with_position and meeting_with_position.strip() else None,
                'meeting_location': meeting_location.strip() if meeting_location and meeting_location.strip() else None,
                'primary_contact': primary_contact.strip() if primary_contact and primary_contact.strip() else None,
                'our_attendees': [a.strip() for a in our_attendees.split(',')] if our_attendees and our_attendees.strip() else None,
                'outcome': outcome.strip() if outcome and outcome.strip() else None,
                'next_action': next_action.strip() if next_action and next_action.strip() else None,
                'next_action_date': next_action_date.isoformat() if next_action_date else None,
                'status': STATUS_REVERSE.get(status_ui),
                'importance': IMPORTANCE_REVERSE.get(importance_ui),
                'tags': [t.strip() for t in tags_input.split(',')] if tags_input and tags_input.strip() else None,
                'created_at': datetime.now().isoformat()
            }
            
            # 데이터 저장
            result = save_func(activity_table, activity_data)
            
            if result:
                st.success("✅ 영업 활동이 성공적으로 등록되었습니다.")
                # 선택된 고객 초기화
                if 'selected_customer_for_activity' in st.session_state:
                    del st.session_state['selected_customer_for_activity']
                st.rerun()
            else:
                st.error("❌ 등록 중 오류가 발생했습니다.")

def render_activity_list(load_func, update_func, delete_func, 
                         activity_table, customer_table, load_customers_func):
    """영업 활동 목록"""
    st.subheader("📋 영업 활동 목록 / Danh sách hoạt động")
    
    try:
        # 활동 데이터 로드
        activities = load_func(activity_table)
        customers = load_customers_func(customer_table)
        
        if not activities:
            st.info("등록된 영업 활동이 없습니다.")
            return
        
        # 고객 ID -> 이름 매핑
        customer_map = {}
        for customer in customers:
            name = customer.get('company_name_short') or customer.get('company_name_original')
            customer_map[customer['id']] = name
        
        # DataFrame 변환
        activities_df = pd.DataFrame(activities)
        
        # 필터링
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            type_filter = st.selectbox(
                "활동 유형",
                ["전체"] + list(ACTIVITY_TYPES.values()),
                key="filter_type"
            )
        
        with col2:
            status_filter = st.selectbox(
                "상태",
                ["전체"] + list(STATUS_OPTIONS.values()),
                key="filter_status"
            )
        
        with col3:
            date_from = st.date_input(
                "시작일",
                value=None,
                key="filter_date_from"
            )
        
        with col4:
            date_to = st.date_input(
                "종료일",
                value=None,
                key="filter_date_to"
            )
        
        # 필터 적용
        filtered_df = activities_df.copy()
        
        if type_filter != "전체":
            type_db = ACTIVITY_TYPES_REVERSE.get(type_filter)
            filtered_df = filtered_df[filtered_df['activity_type'] == type_db]
        
        if status_filter != "전체":
            status_db = STATUS_REVERSE.get(status_filter)
            filtered_df = filtered_df[filtered_df['status'] == status_db]
        
        if date_from:
            filtered_df = filtered_df[pd.to_datetime(filtered_df['activity_date']).dt.date >= date_from]
        
        if date_to:
            filtered_df = filtered_df[pd.to_datetime(filtered_df['activity_date']).dt.date <= date_to]
        
        st.write(f"📊 총 {len(filtered_df)}건")
        
        st.markdown("---")
        
        if filtered_df.empty:
            st.warning("검색 조건에 맞는 활동이 없습니다.")
            return
        
        # 활동 목록 표시
        for idx, activity in filtered_df.iterrows():
            activity_id = activity.get('id')
            customer_id = activity.get('customer_id')
            customer_name = customer_map.get(customer_id, 'N/A')
            
            # ⭐ 수정 모드 확인
            if st.session_state.get(f"edit_activity_{activity_id}", False):
                render_activity_edit_form(activity, update_func, activity_table, customer_table, load_customers_func)
                st.markdown("---")
                continue
            
            # 활동 타입 아이콘
            activity_type = activity.get('activity_type')
            activity_type_ui = ACTIVITY_TYPES.get(activity_type, activity_type)
            
            # 날짜
            activity_date = pd.to_datetime(activity.get('activity_date')).strftime('%Y-%m-%d')
            
            # 제목
            subject = activity.get('subject', 'N/A')
            
            # 상태
            status = activity.get('status', 'completed')
            status_ui = STATUS_OPTIONS.get(status, status)
            
            # 중요도
            importance = activity.get('importance', 'normal')
            importance_ui = IMPORTANCE_LEVELS.get(importance, importance)
            
            # 한 줄 표시
            cols = st.columns([1.5, 2, 3, 1.5, 1, 0.8])
            
            cols[0].write(f"**{activity_date}**")
            cols[1].write(activity_type_ui.split()[0])  # 이모지만
            cols[2].write(f"**{customer_name}** - {subject}")
            cols[3].write(status_ui.split()[0])  # 이모지만
            cols[4].write(importance_ui.split()[0])  # 이모지만
            
            with cols[5]:
                if st.button("📄", key=f"detail_{activity_id}", use_container_width=True):
                    st.session_state[f'show_activity_{activity_id}'] = not st.session_state.get(f'show_activity_{activity_id}', False)
                    st.rerun()
            
            # 상세 정보
            if st.session_state.get(f'show_activity_{activity_id}', False):
                with st.container():
                    st.markdown("---")
                    
                    detail_cols = st.columns([3, 1])
                    
                    with detail_cols[0]:
                        st.write(f"**고객:** {customer_name}")
                        st.write(f"**날짜:** {activity_date}")
                        st.write(f"**유형:** {activity_type_ui}")
                        st.write(f"**제목:** {subject}")
                        
                        meeting_with = activity.get('meeting_with')
                        if meeting_with:
                            position = activity.get('meeting_with_position', '')
                            st.write(f"**만난 사람:** {meeting_with} {position}")
                        
                        location = activity.get('meeting_location')
                        if location:
                            st.write(f"**장소:** {location}")
                        
                        contact = activity.get('primary_contact')
                        if contact:
                            st.write(f"**담당자:** {contact}")
                        
                        description = activity.get('description')
                        if description:
                            st.write(f"**내용:** {description}")
                        
                        outcome = activity.get('outcome')
                        if outcome:
                            st.write(f"**결과:** {outcome}")
                        
                        next_action = activity.get('next_action')
                        if next_action:
                            st.write(f"**다음 액션:** {next_action}")
                            next_date = activity.get('next_action_date')
                            if next_date:
                                st.write(f"**예정일:** {next_date}")
                    
                    with detail_cols[1]:
                        st.write("**액션**")
                        
                        # ⭐ 수정 버튼 추가
                        if st.button("✏️ 수정", key=f"edit_{activity_id}", use_container_width=True, type="primary"):
                            st.session_state[f"edit_activity_{activity_id}"] = True
                            st.session_state[f'show_activity_{activity_id}'] = False
                            st.rerun()
                        
                        if st.button("🗑️ 삭제", key=f"delete_{activity_id}", use_container_width=True):
                            if delete_func(activity_table, activity_id):
                                st.success("삭제되었습니다.")
                                st.rerun()
                        
                        if st.button("❌ 닫기", key=f"close_{activity_id}", use_container_width=True):
                            st.session_state[f'show_activity_{activity_id}'] = False
                            st.rerun()
                    
                    st.markdown("---")
            
            st.markdown("<hr style='margin: 1px 0; border: none; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)
    
    except Exception as e:
        logging.error(f"활동 목록 로드 오류: {str(e)}")
        st.error(f"활동 목록 로딩 중 오류: {str(e)}")

def render_customer_timeline_search(load_func, activity_table, customer_table, load_customers_func):
    """고객별 타임라인 검색 (텍스트 검색 방식)"""
    st.subheader("🔍 고객별 영업 활동 타임라인 / Timeline theo KH")
    
    try:
        # 고객 목록 로드
        customers = load_customers_func(customer_table)
        
        if not customers:
            st.warning("등록된 고객이 없습니다.")
            return
        
        # 고객명 검색
        search_col1, search_col2 = st.columns([4, 1])
        
        with search_col1:
            search_name = st.text_input(
                "고객명 검색 / Tìm tên khách hàng",
                placeholder="회사명 입력 후 Enter (예: Samsung, LG, DUY TAN 등)",
                key="timeline_search_input"
            )
        
        with search_col2:
            if st.button("🔍 검색", use_container_width=True, type="primary", key="btn_search_customer"):
                if search_name and search_name.strip():
                    st.session_state['timeline_search_active'] = True
                st.rerun()
        
        # 검색 실행
        if search_name and search_name.strip():
            search_query = search_name.strip().lower()
            
            # 고객 검색
            matched_customers = []
            for customer in customers:
                name_original = (customer.get('company_name_original') or '').lower()
                name_short = (customer.get('company_name_short') or '').lower()
                name_english = (customer.get('company_name_english') or '').lower()
                
                if (search_query in name_original or 
                    search_query in name_short or 
                    search_query in name_english):
                    matched_customers.append(customer)
            
            # 검색 결과
            if matched_customers:
                st.success(f"🔍 검색 결과: **{len(matched_customers)}**개 고객 발견")
                
                # 검색 결과 리스트 (클릭 가능)
                st.markdown("---")
                st.write("**검색 결과 / Kết quả tìm kiếm**")
                
                for customer in matched_customers:
                    customer_id = customer['id']
                    name = customer.get('company_name_short') or customer.get('company_name_original')
                    country = customer.get('country', 'N/A')
                    city = customer.get('city', 'N/A')
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{name}** ({country} - {city})")
                    
                    with col2:
                        if st.button("📄 보기", key=f"view_{customer_id}", use_container_width=True):
                            st.session_state['timeline_customer_id'] = customer_id
                            st.rerun()
                
                st.markdown("---")
            else:
                st.warning(f"❌ '{search_name}' 검색 결과가 없습니다.")
        
        else:
            st.info("💡 고객명을 입력하고 검색 버튼을 클릭하거나 Enter를 누르세요.")
        
        # 선택된 고객의 타임라인 표시
        if 'timeline_customer_id' in st.session_state:
            customer_id = st.session_state['timeline_customer_id']
            
            st.markdown("---")
            st.markdown("---")
            
            # 고객 정보 헤더
            selected_customer = next((c for c in customers if c['id'] == customer_id), None)
            
            if selected_customer:
                name = selected_customer.get('company_name_short') or selected_customer.get('company_name_original')
                country = selected_customer.get('country', 'N/A')
                city = selected_customer.get('city', 'N/A')
                
                # 헤더
                header_col1, header_col2 = st.columns([4, 1])
                
                with header_col1:
                    st.subheader(f"📅 {name} - 영업 활동 타임라인")
                    st.caption(f"🌍 {country} / 🏙️ {city}")
                
                with header_col2:
                    if st.button("❌ 닫기", key="btn_close_timeline", use_container_width=True):
                        del st.session_state['timeline_customer_id']
                        st.rerun()
                
                st.markdown("---")
                
                # 활동 로드
                from utils.database import load_customer_activities
                
                activities = load_customer_activities(activity_table, customer_id)
                
                if not activities:
                    st.warning("📭 등록된 영업 활동이 없습니다.")
                    
                    if st.button("➕ 이 고객에 대한 활동 등록하러 가기", key="btn_new_activity"):
                        st.session_state.current_page = "영업 활동 관리"
                        del st.session_state['timeline_customer_id']
                        st.rerun()
                else:
                    st.write(f"📊 총 **{len(activities)}**건의 활동")
                    st.markdown("---")
                    
                    # 타임라인 표시
                    for activity in activities:
                        activity_date = pd.to_datetime(activity.get('activity_date')).strftime('%Y-%m-%d')
                        activity_type = activity.get('activity_type')
                        activity_type_ui = ACTIVITY_TYPES.get(activity_type, activity_type)
                        subject = activity.get('subject', '')
                        meeting_with = activity.get('meeting_with', '')
                        description = activity.get('description', '')
                        outcome = activity.get('outcome', '')
                        primary_contact = activity.get('primary_contact', '')
                        
                        with st.container():
                            cols = st.columns([1.5, 5])
                            
                            with cols[0]:
                                st.write(f"**{activity_date}**")
                                st.write(activity_type_ui)
                            
                            with cols[1]:
                                st.write(f"### {subject}")
                                
                                info_cols = st.columns(2)
                                with info_cols[0]:
                                    if meeting_with:
                                        st.write(f"👤 **고객 측:** {meeting_with}")
                                with info_cols[1]:
                                    if primary_contact:
                                        st.write(f"👔 **담당자:** {primary_contact}")
                                
                                if description:
                                    with st.expander("📄 상세 내용"):
                                        st.write(description)
                                
                                if outcome:
                                    with st.expander("📊 결과"):
                                        st.write(outcome)
                            
                            st.markdown("<hr style='margin: 10px 0; border-top: 2px solid #ddd;'>", unsafe_allow_html=True)
    
    except Exception as e:
        logging.error(f"타임라인 로드 오류: {str(e)}")
        st.error(f"타임라인 로딩 중 오류: {str(e)}")

def render_visit_statistics(load_func, activity_table, customer_table, load_customers_func):
    """방문 통계 (Top 10 + 미방문 고객)"""
    st.subheader("📊 고객 방문 통계 / Thống kê thăm khách hàng")
    
    try:
        # 데이터 로드
        activities = load_func(activity_table)
        customers = load_customers_func(customer_table)
        
        if not customers:
            st.warning("등록된 고객이 없습니다.")
            return
        
        # 고객 맵 생성
        customer_map = {}
        for customer in customers:
            name = customer.get('company_name_short') or customer.get('company_name_original')
            customer_map[customer['id']] = {
                'name': name,
                'status': customer.get('status', 'active')
            }
        
        # 활성 고객만 필터링
        active_customers = {k: v for k, v in customer_map.items() if v['status'] == 'active'}
        
        if not activities:
            st.info("등록된 영업 활동이 없습니다.")
            
            # 미방문 고객 전체 표시
            st.write(f"**미방문 고객: {len(active_customers)}개사**")
            
            not_visited_data = []
            for customer_id, info in active_customers.items():
                not_visited_data.append({
                    '고객명': info['name'],
                    '상태': '❌ 미방문',
                    '마지막 방문': '-',
                    '경과 일수': '-'
                })
            
            st.dataframe(
                pd.DataFrame(not_visited_data),
                use_container_width=True,
                hide_index=True
            )
            return
        
        # DataFrame 변환
        activities_df = pd.DataFrame(activities)
        
        # 방문/미팅 활동만 필터링
        visit_types = ['visit', 'meeting']
        visit_df = activities_df[activities_df['activity_type'].isin(visit_types)].copy()
        
        # 고객별 방문 횟수 및 마지막 방문일 계산
        customer_stats = {}
        
        for customer_id in active_customers.keys():
            customer_visits = visit_df[visit_df['customer_id'] == customer_id]
            
            if len(customer_visits) > 0:
                visit_count = len(customer_visits)
                last_visit = pd.to_datetime(customer_visits['activity_date']).max()
                days_since = (datetime.now() - last_visit).days
                
                customer_stats[customer_id] = {
                    'name': active_customers[customer_id]['name'],
                    'visit_count': visit_count,
                    'last_visit': last_visit,
                    'days_since': days_since
                }
            else:
                customer_stats[customer_id] = {
                    'name': active_customers[customer_id]['name'],
                    'visit_count': 0,
                    'last_visit': None,
                    'days_since': None
                }
        
        # 방문 횟수별 정렬
        sorted_stats = sorted(customer_stats.items(), key=lambda x: x[1]['visit_count'], reverse=True)
        
        # Top 10 방문 고객
        st.markdown("### 🏆 Top 10 방문 고객 / Top 10 KH được thăm nhiều nhất")
        
        top_10_data = []
        for i, (customer_id, stats) in enumerate(sorted_stats[:10]):
            if stats['visit_count'] > 0:
                # 1달(30일) 기준 경고
                if stats['days_since'] > 30:
                    status_icon = "⚠️ 재방문 필요"
                    status_color = "🔴"
                else:
                    status_icon = "✅ 정상"
                    status_color = "🟢"
                
                top_10_data.append({
                    '순위': f"{i+1}위",
                    '고객명': stats['name'],
                    '방문 횟수': stats['visit_count'],
                    '마지막 방문': stats['last_visit'].strftime('%Y-%m-%d'),
                    '경과 일수': f"{stats['days_since']}일",
                    '상태': f"{status_color} {status_icon}"
                })
        
        if top_10_data:
            st.dataframe(
                pd.DataFrame(top_10_data),
                use_container_width=True,
                hide_index=True,
                column_config={
                    '순위': st.column_config.TextColumn('순위', width='small'),
                    '고객명': st.column_config.TextColumn('고객명', width='large'),
                    '방문 횟수': st.column_config.NumberColumn('방문 횟수', width='small'),
                    '마지막 방문': st.column_config.TextColumn('마지막 방문', width='medium'),
                    '경과 일수': st.column_config.TextColumn('경과 일수', width='small'),
                    '상태': st.column_config.TextColumn('상태', width='medium')
                }
            )
        else:
            st.info("방문 기록이 있는 고객이 없습니다.")
        
        st.markdown("---")
        
        # 미방문 고객 리스트
        st.markdown("### ❌ 미방문 고객 / KH chưa được thăm")
        
        not_visited = [(cid, stats) for cid, stats in customer_stats.items() if stats['visit_count'] == 0]
        
        st.write(f"**총 {len(not_visited)}개사**")
        
        if not_visited:
            not_visited_data = []
            for customer_id, stats in not_visited:
                not_visited_data.append({
                    '고객명': stats['name'],
                    '상태': '❌ 미방문',
                    '비고': '첫 방문 필요'
                })
            
            st.dataframe(
                pd.DataFrame(not_visited_data),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("모든 활성 고객을 방문했습니다! 🎉")
        
        st.markdown("---")
        
        # 전체 통계
        st.markdown("### 📈 전체 통계 / Tổng quan")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 고객 수", len(active_customers))
        
        with col2:
            visited_count = len([s for s in customer_stats.values() if s['visit_count'] > 0])
            st.metric("방문 고객", visited_count)
        
        with col3:
            st.metric("미방문 고객", len(not_visited))
        
        with col4:
            # 30일 이상 미방문 고객
            overdue = len([s for s in customer_stats.values() if s['days_since'] and s['days_since'] > 30])
            st.metric("재방문 필요", overdue, delta="30일 초과", delta_color="inverse")
    
    except Exception as e:
        logging.error(f"방문 통계 로드 오류: {str(e)}")
        st.error(f"방문 통계 로딩 중 오류: {str(e)}")

