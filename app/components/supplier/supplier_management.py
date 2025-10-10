import streamlit as st
import pandas as pd
from datetime import datetime

def show_supplier_management(load_func, save_func, update_func, delete_func):
    """공급업체 관리 메인 함수"""
    st.title("🏭 공급업체 관리")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs([
        "📝 공급업체 등록", 
        "📋 공급업체 목록", 
        "📊 공급업체 통계"
    ])
    
    with tab1:
        render_supplier_registration(save_func)
    
    with tab2:
        render_supplier_list(load_func, update_func, delete_func)
    
    with tab3:
        render_supplier_statistics(load_func)

def render_supplier_registration(save_func):
    """공급업체 등록 폼"""
    st.subheader("🆕 새 공급업체 등록")
    
    with st.form("supplier_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**기본 정보**")
            name = st.text_input("공급업체명*", placeholder="예: 삼성전자")
            company_name = st.text_input("회사명*", placeholder="예: 삼성전자 주식회사")
            contact_person = st.text_input("담당자명", placeholder="예: 김철수")
            email = st.text_input("이메일", placeholder="예: contact@samsung.com")
            
        with col2:
            st.write("**연락처 정보**")
            phone = st.text_input("전화번호", placeholder="예: +84-123-456-789")
            address = st.text_area("주소", placeholder="베트남 하노이시...")
            business_type = st.selectbox("업종", [
                "제조업", "유통업", "서비스업", "IT", "화학", "전자", "기계", "기타"
            ])
            
        st.write("**거래 조건**")
        col3, col4 = st.columns(2)
        
        with col3:
            payment_terms = st.selectbox("결제 조건", [
                "T/T 30일", "T/T 60일", "L/C", "현금", "기타"
            ])
            delivery_terms = st.selectbox("배송 조건", [
                "FOB", "CIF", "EXW", "DDP", "기타"
            ])
            
        with col4:
            rating = st.selectbox("평가 등급", [1, 2, 3, 4, 5], index=4)
            is_active = st.checkbox("활성 상태", value=True)
        
        notes = st.text_area("비고", placeholder="특별 사항이나 추가 정보")
        
        # Submit 버튼
        submitted = st.form_submit_button("공급업체 등록", type="primary")
        
        if submitted:
            if not name or not company_name:
                st.error("공급업체명과 회사명을 입력하세요.")
                return
            
            supplier_data = {
                "name": name,
                "company_name": company_name,
                "contact_person": contact_person or "",
                "email": email or "",
                "phone": phone or "",
                "address": address or "",
                "business_type": business_type,
                "payment_terms": payment_terms,
                "delivery_terms": delivery_terms,
                "rating": rating,
                "notes": notes or "",
                "is_active": is_active,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            try:
                save_func("suppliers", supplier_data)
                st.success("✅ 공급업체가 성공적으로 등록되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"공급업체 등록 중 오류가 발생했습니다: {str(e)}")

def render_supplier_list(load_func, update_func, delete_func):
    """공급업체 목록 및 관리"""
    st.subheader("📋 공급업체 목록")
    
    # 검색 및 필터
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("공급업체 검색", key="search_supplier")
    with col2:
        business_filter = st.selectbox("업종 필터", [
            "전체", "제조업", "유통업", "서비스업", "IT", "화학", "전자", "기계", "기타"
        ])
    with col3:
        status_filter = st.selectbox("상태 필터", ["전체", "활성", "비활성"])
    
    # 공급업체 목록 로드
    suppliers = load_func("suppliers")
    
    if not suppliers:
        st.info("등록된 공급업체가 없습니다.")
        return
    
    # 필터링
    filtered_suppliers = suppliers
    
    if search_term:
        filtered_suppliers = [s for s in filtered_suppliers 
                            if search_term.lower() in s.get('name', '').lower() 
                            or search_term.lower() in s.get('company_name', '').lower()]
    
    if business_filter != "전체":
        filtered_suppliers = [s for s in filtered_suppliers 
                            if s.get('business_type') == business_filter]
    
    if status_filter != "전체":
        is_active = status_filter == "활성"
        filtered_suppliers = [s for s in filtered_suppliers 
                            if s.get('is_active', True) == is_active]
    
    # 공급업체 목록 표시
    if filtered_suppliers:
        for supplier in filtered_suppliers:
            status_icon = "✅" if supplier.get('is_active', True) else "❌"
            rating_stars = "⭐" * supplier.get('rating', 5)
            
            with st.expander(f"🏭 {supplier.get('name', 'N/A')} {status_icon} {rating_stars}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**회사명:** {supplier.get('company_name', 'N/A')}")
                    st.write(f"**업종:** {supplier.get('business_type', 'N/A')}")
                    st.write(f"**담당자:** {supplier.get('contact_person', 'N/A')}")
                    st.write(f"**연락처:** {supplier.get('phone', 'N/A')}")
                    st.write(f"**이메일:** {supplier.get('email', 'N/A')}")
                    
                with col2:
                    st.write(f"**결제조건:** {supplier.get('payment_terms', 'N/A')}")
                    st.write(f"**배송조건:** {supplier.get('delivery_terms', 'N/A')}")
                    st.write(f"**평가등급:** {supplier.get('rating', 5)}/5")
                    st.write(f"**상태:** {'활성' if supplier.get('is_active', True) else '비활성'}")
                    
                with col3:
                    # 수정 버튼
                    if st.button("📝 수정", key=f"edit_supplier_{supplier['id']}"):
                        st.session_state[f"editing_supplier_{supplier['id']}"] = True
                        st.rerun()
                    
                    # 삭제 버튼
                    if st.button("❌ 삭제", key=f"delete_supplier_{supplier['id']}"):
                        if st.session_state.get(f"confirm_delete_{supplier['id']}", False):
                            try:
                                delete_func("suppliers", supplier['id'])
                                st.success("공급업체가 삭제되었습니다!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"삭제 실패: {str(e)}")
                        else:
                            st.session_state[f"confirm_delete_{supplier['id']}"] = True
                            st.warning("다시 한번 삭제 버튼을 클릭하여 확인하세요.")
                
                # 주소와 비고
                if supplier.get('address'):
                    st.write(f"**주소:** {supplier['address']}")
                if supplier.get('notes'):
                    st.write(f"**비고:** {supplier['notes']}")
                
                # 수정 폼 (조건부 표시)
                if st.session_state.get(f"editing_supplier_{supplier['id']}", False):
                    st.markdown("---")
                    st.markdown("### ✏️ 공급업체 수정")
                    
                    with st.form(f"edit_supplier_form_{supplier['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("공급업체명", value=supplier.get('name', ''))
                            edit_company = st.text_input("회사명", value=supplier.get('company_name', ''))
                            edit_contact = st.text_input("담당자", value=supplier.get('contact_person', ''))
                            edit_email = st.text_input("이메일", value=supplier.get('email', ''))
                            
                        with col2:
                            edit_phone = st.text_input("전화번호", value=supplier.get('phone', ''))
                            edit_business = st.selectbox("업종", [
                                "제조업", "유통업", "서비스업", "IT", "화학", "전자", "기계", "기타"
                            ], index=["제조업", "유통업", "서비스업", "IT", "화학", "전자", "기계", "기타"].index(supplier.get('business_type', '제조업')))
                            edit_payment = st.selectbox("결제조건", [
                                "T/T 30일", "T/T 60일", "L/C", "현금", "기타"
                            ], index=["T/T 30일", "T/T 60일", "L/C", "현금", "기타"].index(supplier.get('payment_terms', 'T/T 30일')))
                            edit_delivery = st.selectbox("배송조건", [
                                "FOB", "CIF", "EXW", "DDP", "기타"
                            ], index=["FOB", "CIF", "EXW", "DDP", "기타"].index(supplier.get('delivery_terms', 'FOB')))
                        
                        edit_address = st.text_area("주소", value=supplier.get('address', ''))
                        edit_rating = st.selectbox("평가등급", [1, 2, 3, 4, 5], index=supplier.get('rating', 5) - 1)
                        edit_notes = st.text_area("비고", value=supplier.get('notes', ''))
                        edit_active = st.checkbox("활성상태", value=supplier.get('is_active', True))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 저장", use_container_width=True):
                                if edit_name and edit_company:
                                    update_data = {
                                        "name": edit_name,
                                        "company_name": edit_company,
                                        "contact_person": edit_contact,
                                        "email": edit_email,
                                        "phone": edit_phone,
                                        "address": edit_address,
                                        "business_type": edit_business,
                                        "payment_terms": edit_payment,
                                        "delivery_terms": edit_delivery,
                                        "rating": edit_rating,
                                        "notes": edit_notes,
                                        "is_active": edit_active,
                                        "updated_at": datetime.now().isoformat()
                                    }
                                    try:
                                        update_func("suppliers", supplier['id'], update_data)
                                        st.session_state[f"editing_supplier_{supplier['id']}"] = False
                                        st.success("수정이 완료되었습니다!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"수정 실패: {str(e)}")
                                else:
                                    st.error("공급업체명과 회사명을 입력하세요.")
                        
                        with col2:
                            if st.form_submit_button("❌ 취소", use_container_width=True):
                                st.session_state[f"editing_supplier_{supplier['id']}"] = False
                                st.rerun()
        
        st.info(f"총 {len(filtered_suppliers)}개 공급업체가 검색되었습니다.")
    else:
        st.info("검색 조건에 맞는 공급업체가 없습니다.")

def render_supplier_statistics(load_func):
    """공급업체 통계"""
    st.subheader("📊 공급업체 통계")
    
    suppliers = load_func("suppliers")
    
    if not suppliers:
        st.info("통계를 표시할 공급업체가 없습니다.")
        return
    
    # 기본 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_suppliers = len(suppliers)
        st.metric("총 공급업체 수", total_suppliers)
    
    with col2:
        active_suppliers = len([s for s in suppliers if s.get('is_active', True)])
        st.metric("활성 공급업체", active_suppliers)
    
    with col3:
        if suppliers:
            avg_rating = sum(s.get('rating', 5) for s in suppliers) / len(suppliers)
            st.metric("평균 평가", f"{avg_rating:.1f}/5")
    
    with col4:
        high_rating = len([s for s in suppliers if s.get('rating', 5) >= 4])
        st.metric("고평가 업체", f"{high_rating}개")
    
    # 업종별 분포
    if suppliers:
        df = pd.DataFrame(suppliers)
        
        if 'business_type' in df.columns:
            st.write("**업종별 공급업체 분포**")
            business_counts = df['business_type'].value_counts()
            st.bar_chart(business_counts)
        
        # 평가 등급 분포
        if 'rating' in df.columns:
            st.write("**평가 등급 분포**")
            rating_counts = df['rating'].value_counts().sort_index()
            st.bar_chart(rating_counts)
        
        # 지역별 분포 (주소 기반)
        if 'address' in df.columns:
            st.write("**지역별 분포**")
            # 주소에서 도시명 추출 (간단한 방식)
            cities = []
            for supplier in suppliers:
                address = supplier.get('address', '')
                if '하노이' in address or 'Hanoi' in address:
                    cities.append('하노이')
                elif '호치민' in address or 'Ho Chi Minh' in address:
                    cities.append('호치민')
                elif '다낭' in address or 'Da Nang' in address:
                    cities.append('다낭')
                else:
                    cities.append('기타')
            
            if cities:
                city_df = pd.DataFrame({'city': cities})
                city_counts = city_df['city'].value_counts()
                st.bar_chart(city_counts)