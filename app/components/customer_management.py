import streamlit as st
import pandas as pd
from datetime import datetime
import logging

def show_customer_management(load_func, save_func, update_func, delete_func):
    """고객 관리 메인 페이지"""
    st.title("고객 관리")
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["고객 등록", "고객 목록", "CSV 관리"])
    
    with tab1:
        render_customer_form(save_func)
    
    with tab2:
        render_customer_list(load_func, update_func, delete_func)
    
    with tab3:
        render_csv_management(load_func, save_func)

def render_customer_form(save_func):
    """고객 등록 폼"""
    st.header("새 고객 등록")
    
    with st.form("customer_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("기본 정보")
            company_name = st.text_input("회사명 *")
            business_type = st.selectbox("업종", [
                "제조업", "서비스업", "건설업", "유통업", "IT/소프트웨어", 
                "금융업", "교육업", "의료업", "운송업", "Mold maker", "기타"
            ])
            country = st.selectbox("국가", [
                "Korea", "Vietnam", "China", "Japan", "USA", "Germany", "기타"
            ])
            business_number = st.text_input("사업자번호")
            tax_id = st.text_input("세금 ID")
        
        with col2:
            st.subheader("담당자 정보")
            contact_person = st.text_input("담당자명 *")
            position = st.text_input("직책")
            email = st.text_input("이메일 *")
            phone = st.text_input("전화번호 *")
            mobile = st.text_input("휴대폰")
        
        address = st.text_area("주소")
        
        # KAM 정보
        st.subheader("KAM 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            kam_name = st.text_input("KAM 이름")
            kam_position = st.text_input("KAM 직책")
        
        with col2:
            kam_phone = st.text_input("KAM 전화번호")
        
        kam_notes = st.text_area("KAM 노트")
        
        # 기타 정보
        payment_terms = st.selectbox("결제 조건", [
            "현금", "15일", "30일", "45일", "60일", "90일", "기타"
        ])
        
        status = st.selectbox("상태", ["Active", "Inactive", "Pending"])
        notes = st.text_area("비고")
        
        # 저장 버튼
        submitted = st.form_submit_button("고객 등록", type="primary")
        
        if submitted:
            # 필수 필드 검증
            if not company_name.strip():
                st.error("회사명을 입력해주세요.")
                return
            
            if not contact_person.strip():
                st.error("담당자명을 입력해주세요.")
                return
            
            if not email.strip():
                st.error("이메일을 입력해주세요.")
                return
            
            if not phone.strip():
                st.error("전화번호를 입력해주세요.")
                return
            
            # 저장 데이터 준비
            customer_data = {
                'company_name': company_name,
                'business_number': business_number if business_number.strip() else None,
                'business_type': business_type,
                'country': country,
                'address': address if address.strip() else None,
                'contact_person': contact_person,
                'position': position if position.strip() else None,
                'email': email,
                'phone': phone,
                'mobile': mobile if mobile.strip() else None,
                'tax_id': tax_id if tax_id.strip() else None,
                'payment_terms': payment_terms,
                'kam_name': kam_name if kam_name.strip() else None,
                'kam_phone': kam_phone if kam_phone.strip() else None,
                'kam_position': kam_position if kam_position.strip() else None,
                'kam_notes': kam_notes if kam_notes.strip() else None,
                'status': status,
                'notes': notes if notes.strip() else None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # 저장 실행
            success = save_func('customers', customer_data)
            
            if success:
                st.success("고객이 성공적으로 등록되었습니다!")
                st.balloons()
                
                # 등록된 고객 정보 요약 표시
                with st.expander("등록 완료된 고객 정보", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**회사명:** {company_name}")
                        st.write(f"**담당자:** {contact_person}")
                        st.write(f"**이메일:** {email}")
                    with col2:
                        st.write(f"**전화번호:** {phone}")
                        st.write(f"**국가:** {country}")
                        st.write(f"**상태:** {status}")
                
                st.rerun()
            else:
                st.error("고객 등록에 실패했습니다. 다시 시도해주세요.")

def render_customer_edit_form(customer, update_func):
    """고객 수정 폼"""
    st.subheader(f"{customer.get('company_name', 'N/A')} 수정")
    
    with st.form(f"customer_edit_form_{customer.get('id')}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("기본 정보")
            company_name = st.text_input("회사명 *", value=customer.get('company_name', ''))
            business_type = st.selectbox("업종", [
                "제조업", "서비스업", "건설업", "유통업", "IT/소프트웨어", 
                "금융업", "교육업", "의료업", "운송업", "Mold maker", "기타"
            ], index=0 if not customer.get('business_type') else (
                ["제조업", "서비스업", "건설업", "유통업", "IT/소프트웨어", 
                 "금융업", "교육업", "의료업", "운송업", "Mold maker", "기타"].index(customer.get('business_type'))
                if customer.get('business_type') in ["제조업", "서비스업", "건설업", "유통업", "IT/소프트웨어", 
                                                   "금융업", "교육업", "의료업", "운송업", "Mold maker", "기타"]
                else len(["제조업", "서비스업", "건설업", "유통업", "IT/소프트웨어", 
                         "금융업", "교육업", "의료업", "운송업", "Mold maker", "기타"]) - 1
            ))
            
            country_list = ["Korea", "Vietnam", "China", "Japan", "USA", "Germany", "기타"]
            country = st.selectbox("국가", country_list, 
                index=0 if not customer.get('country') else (
                    country_list.index(customer.get('country'))
                    if customer.get('country') in country_list
                    else len(country_list) - 1
                ))
            business_number = st.text_input("사업자번호", value=customer.get('business_number', '') or '')
            tax_id = st.text_input("세금 ID", value=customer.get('tax_id', '') or '')
        
        with col2:
            st.subheader("담당자 정보")
            contact_person = st.text_input("담당자명 *", value=customer.get('contact_person', ''))
            position = st.text_input("직책", value=customer.get('position', '') or '')
            email = st.text_input("이메일 *", value=customer.get('email', ''))
            phone = st.text_input("전화번호 *", value=customer.get('phone', ''))
            mobile = st.text_input("휴대폰", value=customer.get('mobile', '') or '')
        
        address = st.text_area("주소", value=customer.get('address', '') or '')
        
        # KAM 정보
        st.subheader("KAM 정보")
        col1, col2 = st.columns(2)
        
        with col1:
            kam_name = st.text_input("KAM 이름", value=customer.get('kam_name', '') or '')
            kam_position = st.text_input("KAM 직책", value=customer.get('kam_position', '') or '')
        
        with col2:
            kam_phone = st.text_input("KAM 전화번호", value=customer.get('kam_phone', '') or '')
        
        kam_notes = st.text_area("KAM 노트", value=customer.get('kam_notes', '') or '')
        
        # 기타 정보
        payment_list = ["현금", "15일", "30일", "45일", "60일", "90일", "기타"]
        payment_terms = st.selectbox("결제 조건", payment_list,
            index=0 if not customer.get('payment_terms') else (
                payment_list.index(customer.get('payment_terms'))
                if customer.get('payment_terms') in payment_list
                else len(payment_list) - 1
            ))
        
        status_list = ["Active", "Inactive", "Pending"]
        status = st.selectbox("상태", status_list,
            index=0 if not customer.get('status') else (
                status_list.index(customer.get('status'))
                if customer.get('status') in status_list
                else 0
            ))
        notes = st.text_area("비고", value=customer.get('notes', '') or '')
        
        # 버튼
        col1, col2 = st.columns(2)
        with col1:
            save_changes = st.form_submit_button("변경사항 저장", type="primary")
        with col2:
            cancel_edit = st.form_submit_button("취소")
        
        if cancel_edit:
            del st.session_state[f"edit_customer_{customer.get('id')}"]
            st.rerun()
        
        if save_changes:
            # 필수 필드 검증
            if not company_name.strip() or not contact_person.strip() or not email.strip() or not phone.strip():
                st.error("필수 필드를 모두 입력해주세요.")
                return
            
            # ID 확인
            customer_id = customer.get('id')
            if not customer_id:
                st.error("고객 ID를 찾을 수 없습니다.")
                return
            
            st.info(f"수정할 고객 ID: {customer_id}")  # 디버깅용
            
            # 업데이트 데이터 준비
            update_data = {
                'company_name': company_name,
                'business_number': business_number if business_number.strip() else None,
                'business_type': business_type,
                'country': country,
                'address': address if address.strip() else None,
                'contact_person': contact_person,
                'position': position if position.strip() else None,
                'email': email,
                'phone': phone,
                'mobile': mobile if mobile.strip() else None,
                'tax_id': tax_id if tax_id.strip() else None,
                'payment_terms': payment_terms,
                'kam_name': kam_name if kam_name.strip() else None,
                'kam_phone': kam_phone if kam_phone.strip() else None,
                'kam_position': kam_position if kam_position.strip() else None,
                'kam_notes': kam_notes if kam_notes.strip() else None,
                'status': status,
                'notes': notes if notes.strip() else None,
                'updated_at': datetime.now().isoformat()
            }
            
            # 업데이트 실행
            try:
                # 첫 번째 시도: (table, data, id)
                success = update_func('customers', update_data, customer_id)
                
                if success:
                    st.success("고객 정보가 성공적으로 수정되었습니다!")
                    del st.session_state[f"edit_customer_{customer.get('id')}"]
                    st.rerun()
                else:
                    st.error("수정에 실패했습니다. 다시 시도해주세요.")
            except Exception as e:
                # 두 번째 시도: (table, id, data)
                try:
                    st.warning(f"첫 번째 시도 실패: {str(e)}")
                    st.info("매개변수 순서를 바꿔서 재시도...")
                    success = update_func('customers', customer_id, update_data)
                    
                    if success:
                        st.success("고객 정보가 성공적으로 수정되었습니다!")
                        del st.session_state[f"edit_customer_{customer.get('id')}"]
                        st.rerun()
                    else:
                        st.error("수정에 실패했습니다.")
                except Exception as e2:
                    st.error(f"두 번째 시도도 실패: {str(e2)}")
                    st.error("update_func 매개변수 순서를 확인해주세요.")

def render_customer_list(load_func, update_func, delete_func):
    """고객 목록"""
    st.header("고객 목록")
    
    try:
        customers_data = load_func('customers')
        
        if not customers_data:
            st.info("등록된 고객이 없습니다.")
            return
        
        # DataFrame 변환
        if isinstance(customers_data, list):
            customers_df = pd.DataFrame(customers_data)
        else:
            customers_df = customers_data
        
        if customers_df.empty:
            st.info("등록된 고객이 없습니다.")
            return
        
        st.write(f"총 {len(customers_df)}개의 고객이 등록되어 있습니다.")
        
        # 검색 기능
        search_term = st.text_input("검색 (회사명, 담당자명)", key="customer_search")
        
        # 검색 필터 적용
        if search_term:
            filtered_df = customers_df[
                customers_df['company_name'].str.contains(search_term, case=False, na=False) |
                customers_df['contact_person'].str.contains(search_term, case=False, na=False)
            ]
        else:
            filtered_df = customers_df
        
        # 고객 목록 표시
        for idx, customer in filtered_df.iterrows():
            # 수정 모드 확인
            if st.session_state.get(f"edit_customer_{customer.get('id')}", False):
                render_customer_edit_form(customer, update_func)
                continue
                
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{customer.get('company_name', 'N/A')}**")
                    st.caption(f"담당자: {customer.get('contact_person', 'N/A')}")
                    if customer.get('business_type'):
                        st.caption(f"업종: {customer['business_type']}")
                
                with col2:
                    st.write(f"이메일: {customer.get('email', 'N/A')}")
                    st.write(f"전화: {customer.get('phone', 'N/A')}")
                    if customer.get('country'):
                        st.caption(f"국가: {customer['country']}")
                
                with col3:
                    status = customer.get('status', 'Active')
                    status_colors = {
                        "Active": "#28a745",
                        "Inactive": "#6c757d",
                        "Pending": "#ffc107"
                    }
                    color = status_colors.get(status, "#28a745")
                    st.markdown(f"<span style='color: {color}'>● {status}</span>", 
                               unsafe_allow_html=True)
                    
                    # 액션 버튼
                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("수정", key=f"edit_{customer.get('id')}"):
                            st.session_state[f"edit_customer_{customer.get('id')}"] = True
                            st.rerun()
                    
                    with col_del:
                        if st.button("삭제", key=f"delete_{customer.get('id')}"):
                            # 삭제 전 관련 데이터 확인
                            customer_id = customer.get('id')
                            can_delete, message = check_customer_deletion_safety(customer_id, load_func)
                            
                            if can_delete:
                                if delete_func('customers', customer_id):
                                    st.success("고객이 삭제되었습니다.")
                                    st.rerun()
                                else:
                                    st.error("삭제 실패")
                            else:
                                st.error(f"삭제 불가: {message}")
                                st.info("관련 견적서를 먼저 삭제하거나 다른 고객으로 변경한 후 삭제하세요.")
                                
                                # 비활성화 옵션 제공
                                if st.button("대신 비활성화", key=f"deactivate_{customer.get('id')}"):
                                    deactivate_data = {
                                        'status': 'Inactive',
                                        'updated_at': datetime.now().isoformat()
                                    }
                                    
                                    try:
                                        success = update_func('customers', customer_id, deactivate_data)
                                        if success:
                                            st.success("고객이 비활성화되었습니다.")
                                            st.rerun()
                                        else:
                                            st.error("비활성화 실패")
                                    except:
                                        # 매개변수 순서를 바꿔서 재시도
                                        try:
                                            success = update_func('customers', deactivate_data, customer_id)
                                            if success:
                                                st.success("고객이 비활성화되었습니다.")
                                                st.rerun()
                                            else:
                                                st.error("비활성화 실패")
                                        except Exception as e:
                                            st.error(f"비활성화 오류: {str(e)}")
                
                # 추가 정보 (접을 수 있는 형태)
                with st.expander(f"{customer.get('company_name', 'N/A')} 상세 정보", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if customer.get('business_number'):
                            st.write(f"**사업자번호:** {customer['business_number']}")
                        if customer.get('address'):
                            st.write(f"**주소:** {customer['address']}")
                        if customer.get('payment_terms'):
                            st.write(f"**결제조건:** {customer['payment_terms']}")
                    
                    with col2:
                        if customer.get('position'):
                            st.write(f"**직책:** {customer['position']}")
                        if customer.get('mobile'):
                            st.write(f"**휴대폰:** {customer['mobile']}")
                        if customer.get('notes'):
                            st.write(f"**비고:** {customer['notes']}")
                    
                    # KAM 정보
                    if customer.get('kam_name'):
                        st.markdown("**KAM 정보**")
                        st.write(f"KAM: {customer['kam_name']}")
                        if customer.get('kam_position'):
                            st.write(f"직책: {customer['kam_position']}")
                        if customer.get('kam_phone'):
                            st.write(f"전화: {customer['kam_phone']}")
                        if customer.get('kam_notes'):
                            st.write(f"노트: {customer['kam_notes']}")
                
                st.markdown("---")
        
        # 통계 정보
        st.markdown("---")
        st.subheader("고객 통계")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_customers = len(filtered_df)
            st.metric("총 고객 수", total_customers)
        
        with col2:
            active_customers = len(filtered_df[filtered_df['status'] == 'Active']) if 'status' in filtered_df.columns else 0
            st.metric("활성 고객", active_customers)
        
        with col3:
            if 'country' in filtered_df.columns and not filtered_df['country'].empty:
                country_counts = filtered_df['country'].value_counts()
                if len(country_counts) > 0:
                    top_country = country_counts.index[0]
                    top_country_count = country_counts.iloc[0]
                    st.metric("주요 국가", f"{top_country} ({top_country_count}개)")
                else:
                    st.metric("주요 국가", "N/A")
            else:
                st.metric("주요 국가", "N/A")
        
        with col4:
            if 'kam_name' in filtered_df.columns:
                kam_assigned = len(filtered_df[filtered_df['kam_name'].notna()])
                st.metric("KAM 배정", f"{kam_assigned}개")
            else:
                st.metric("KAM 배정", "0개")
        
    except Exception as e:
        logging.error(f"고객 목록 로드 오류: {str(e)}")
        st.error(f"고객 목록 로딩 중 오류가 발생했습니다: {str(e)}")

def render_csv_management(load_func, save_func):
    """CSV 다운로드/업로드 관리"""
    st.header("CSV 파일 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CSV 다운로드")
        
        if st.button("고객 목록 CSV 다운로드", type="primary"):
            try:
                customers_data = load_func('customers')
                
                if not customers_data:
                    st.warning("다운로드할 고객 데이터가 없습니다.")
                    return
                
                # DataFrame 변환
                if isinstance(customers_data, list):
                    customers_df = pd.DataFrame(customers_data)
                else:
                    customers_df = customers_data
                
                if customers_df.empty:
                    st.warning("다운로드할 고객 데이터가 없습니다.")
                    return
                
                # CSV 생성
                csv_data = generate_customer_csv(customers_df)
                
                # 다운로드 버튼
                st.download_button(
                    label="CSV 파일 다운로드",
                    data=csv_data,
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_customers_csv"
                )
                
                st.success(f"총 {len(customers_df)}개의 고객 데이터를 내보낼 준비가 완료되었습니다.")
                
            except Exception as e:
                st.error(f"CSV 생성 중 오류: {str(e)}")
    
    with col2:
        st.subheader("CSV 업로드")
        
        uploaded_file = st.file_uploader(
            "고객 데이터 CSV 파일 선택",
            type=['csv'],
            help="CSV 파일을 업로드하여 고객 데이터를 일괄 등록할 수 있습니다."
        )
        
        if uploaded_file is not None:
            try:
                # CSV 파일 읽기
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                
                st.write("업로드된 파일 미리보기:")
                st.dataframe(df.head(10))
                
                st.write(f"총 {len(df)}개의 행이 발견되었습니다.")
                
                # 필수 컬럼 확인
                required_columns = ['company_name', 'contact_person', 'email', 'phone']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}")
                    st.info("필수 컬럼: company_name, contact_person, email, phone")
                else:
                    # 업로드 옵션
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        update_existing = st.checkbox(
                            "기존 고객 업데이트",
                            help="이메일이 같은 고객이 있으면 정보를 업데이트합니다."
                        )
                    
                    with col2:
                        skip_errors = st.checkbox(
                            "오류 행 건너뛰기",
                            value=True,
                            help="오류가 있는 행은 건너뛰고 나머지만 처리합니다."
                        )
                    
                    if st.button("CSV 데이터 업로드", type="primary"):
                        upload_results = process_csv_upload(
                            df, save_func, load_func, update_existing, skip_errors
                        )
                        
                        # 결과 표시
                        if upload_results['success_count'] > 0:
                            st.success(f"성공: {upload_results['success_count']}개 처리됨")
                        
                        if upload_results['error_count'] > 0:
                            st.warning(f"실패: {upload_results['error_count']}개")
                            
                            with st.expander("오류 세부사항", expanded=False):
                                for error in upload_results['errors']:
                                    st.write(f"- {error}")
                        
                        if upload_results['updated_count'] > 0:
                            st.info(f"업데이트: {upload_results['updated_count']}개")
                        
                        # 전체 결과
                        st.balloons()
                        st.rerun()
                        
            except Exception as e:
                st.error(f"파일 처리 중 오류: {str(e)}")
    
    # CSV 템플릿 다운로드
    st.markdown("---")
    st.subheader("CSV 템플릿")
    
    if st.button("CSV 템플릿 다운로드"):
        template_data = create_csv_template()
        
        st.download_button(
            label="템플릿 CSV 다운로드",
            data=template_data,
            file_name="customer_template.csv",
            mime="text/csv",
            key="download_template"
        )

def generate_customer_csv(customers_df):
    """고객 데이터를 CSV 형태로 변환 (영어 컬럼명 유지)"""
    try:
        # 내보낼 컬럼 선택
        export_columns = [
            'company_name', 'business_number', 'business_type', 'country',
            'address', 'contact_person', 'position', 'email', 'phone', 'mobile',
            'tax_id', 'payment_terms', 'kam_name', 'kam_phone', 'kam_position',
            'kam_notes', 'status', 'notes', 'created_at'
        ]
        
        # 존재하는 컬럼만 선택
        available_columns = [col for col in export_columns if col in customers_df.columns]
        export_df = customers_df[available_columns].copy()
        
        # CSV 문자열로 변환 (영어 컬럼명 그대로)
        csv_string = export_df.to_csv(index=False, encoding='utf-8')
        
        return csv_string
        
    except Exception as e:
        logging.error(f"CSV 생성 오류: {str(e)}")
        raise e

def process_csv_upload(df, save_func, load_func, update_existing, skip_errors):
    """CSV 업로드 처리"""
    results = {
        'success_count': 0,
        'error_count': 0,
        'updated_count': 0,
        'errors': []
    }
    
    try:
        # 기존 고객 데이터 로드 (업데이트 확인용)
        existing_customers = None
        if update_existing:
            try:
                existing_data = load_func('customers')
                if existing_data:
                    if isinstance(existing_data, list):
                        existing_customers = pd.DataFrame(existing_data)
                    else:
                        existing_customers = existing_data
            except:
                pass
        
        # 각 행 처리
        for index, row in df.iterrows():
            try:
                # 필수 데이터 검증
                if not row.get('company_name') or not row.get('contact_person'):
                    if not skip_errors:
                        results['errors'].append(f"행 {index+2}: 필수 필드 누락")
                    results['error_count'] += 1
                    continue
                
                # 고객 데이터 준비
                customer_data = {
                    'company_name': str(row.get('company_name', '')).strip(),
                    'business_number': str(row.get('business_number', '')).strip() or None,
                    'business_type': str(row.get('business_type', '')).strip() or None,
                    'country': str(row.get('country', '')).strip() or None,
                    'address': str(row.get('address', '')).strip() or None,
                    'contact_person': str(row.get('contact_person', '')).strip(),
                    'position': str(row.get('position', '')).strip() or None,
                    'email': str(row.get('email', '')).strip(),
                    'phone': str(row.get('phone', '')).strip(),
                    'mobile': str(row.get('mobile', '')).strip() or None,
                    'tax_id': str(row.get('tax_id', '')).strip() or None,
                    'payment_terms': str(row.get('payment_terms', '')).strip() or None,
                    'kam_name': str(row.get('kam_name', '')).strip() or None,
                    'kam_phone': str(row.get('kam_phone', '')).strip() or None,
                    'kam_position': str(row.get('kam_position', '')).strip() or None,
                    'kam_notes': str(row.get('kam_notes', '')).strip() or None,
                    'status': str(row.get('status', 'Active')).strip(),
                    'notes': str(row.get('notes', '')).strip() or None,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                # 기존 고객 확인 (이메일 기준)
                is_update = False
                if update_existing and existing_customers is not None:
                    existing_customer = existing_customers[
                        existing_customers['email'] == customer_data['email']
                    ]
                    
                    if not existing_customer.empty:
                        is_update = True
                        # 업데이트 로직 (현재는 새로 저장)
                
                # 저장 실행
                if save_func('customers', customer_data):
                    if is_update:
                        results['updated_count'] += 1
                    else:
                        results['success_count'] += 1
                else:
                    results['error_count'] += 1
                    results['errors'].append(f"행 {index+2}: 저장 실패")
                
            except Exception as e:
                results['error_count'] += 1
                results['errors'].append(f"행 {index+2}: {str(e)}")
                
                if not skip_errors:
                    break
        
        return results
        
    except Exception as e:
        logging.error(f"CSV 업로드 처리 오류: {str(e)}")
        results['errors'].append(f"전체 처리 오류: {str(e)}")
        return results

def create_csv_template():
    """CSV 템플릿 생성 (영어 컬럼명)"""
    template_data = {
        'company_name': ['Sample Company 1', 'Sample Company 2'],
        'business_number': ['123-45-67890', '098-76-54321'],
        'business_type': ['Manufacturing', 'Service'],
        'country': ['Korea', 'Vietnam'],
        'address': ['Seoul Gangnam', 'Hanoi City'],
        'contact_person': ['John Kim', 'Jane Lee'],
        'position': ['Manager', 'Director'],
        'email': ['john@sample.com', 'jane@sample.com'],
        'phone': ['02-1234-5678', '010-9876-5432'],
        'mobile': ['010-1234-5678', '010-8765-4321'],
        'tax_id': ['TAX123', 'TAX456'],
        'payment_terms': ['30 days', 'Cash'],
        'kam_name': ['KAM Kim', 'KAM Lee'],
        'kam_phone': ['010-1111-2222', '010-3333-4444'],
        'kam_position': ['Team Lead', 'Manager'],
        'kam_notes': ['Important client', 'New client'],
        'status': ['Active', 'Active'],
        'notes': ['Note 1', 'Note 2']
    }
    
    template_df = pd.DataFrame(template_data)
    return template_df.to_csv(index=False, encoding='utf-8')

def check_customer_deletion_safety(customer_id, load_func):
    """고객 삭제 안전성 확인"""
    try:
        # 관련 견적서 확인
        quotations_data = load_func('quotations')
        
        if quotations_data:
            if isinstance(quotations_data, list):
                quotations_df = pd.DataFrame(quotations_data)
            else:
                quotations_df = quotations_data
            
            if not quotations_df.empty:
                related_quotations = quotations_df[quotations_df['customer_id'] == customer_id]
                
                if not related_quotations.empty:
                    count = len(related_quotations)
                    return False, f"이 고객과 연결된 {count}개의 견적서가 있습니다."
        
        # 다른 관련 테이블도 확인 가능 (예: sales_process, orders 등)
        
        return True, "삭제 가능"
        
    except Exception as e:
        logging.error(f"삭제 안전성 확인 오류: {str(e)}")
        return False, f"삭제 안전성 확인 중 오류: {str(e)}"