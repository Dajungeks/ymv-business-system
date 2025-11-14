import streamlit as st
import pandas as pd
from datetime import datetime
import logging

# 국가별 주요 도시 (확장판)
CITIES_BY_COUNTRY = {
    "Vietnam": [
        "Hanoi", "Ho Chi Minh", "Da Nang", "Hai Phong", "Can Tho", 
        "Bien Hoa", "Dong Nai", "Vung Tau", "Nha Trang", "Hue", 
        "Buon Ma Thuot", "Qui Nhon", "Rach Gia", "Long Xuyen", "Thai Nguyen", 
        "Phan Thiet", "Bac Ninh", "Vinh", "Nam Dinh", "My Tho", 
        "Thanh Hoa", "Bac Giang", "Bac Lieu", "Cao Lanh", "Ben Tre", 
        "Hai Duong", "Quang Ninh", "Binh Duong", "Hung Yen", 
        "Ha Nam", "Thai Binh", "Ninh Binh", "Quang Nam", "기타"
    ],
    "Korea": [
        "Seoul", "Busan", "Incheon", "Daegu", "Daejeon", 
        "Gwangju", "Ulsan", "Suwon", "Changwon", "Seongnam",
        "Goyang", "Yongin", "Bucheon", "Ansan", "Cheongju",
        "Jeonju", "Anyang", "Cheonan", "Pohang", "Gimhae",
        "Jinju", "Paju", "Asan", "Gimpo", "Pyeongtaek",
        "Siheung", "Gwangmyeong", "Hanam", "Icheon", "기타"
    ],
    "Japan": [
        "Tokyo", "Osaka", "Yokohama", "Nagoya", "Sapporo",
        "Fukuoka", "Kobe", "Kyoto", "Kawasaki", "Saitama",
        "Hiroshima", "Sendai", "Chiba", "Kitakyushu", "Sakai",
        "Niigata", "Hamamatsu", "Kumamoto", "Okayama", "Shizuoka",
        "Sagamihara", "Kagoshima", "Hachioji", "Matsuyama", "기타"
    ],
    "China": [
        "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu",
        "Hangzhou", "Wuhan", "Tianjin", "Chongqing", "Xi'an",
        "Nanjing", "Suzhou", "Dongguan", "Shenyang", "Qingdao",
        "Zhengzhou", "Foshan", "Changsha", "Harbin", "Dalian",
        "Kunming", "Jinan", "Ningbo", "Wuxi", "Changchun",
        "Xiamen", "Fuzhou", "Nanchang", "Hefei", "기타"
    ],
    "Thailand": [
        "Bangkok", "Chiang Mai", "Phuket", "Pattaya", "Chon Buri",
        "Nakhon Ratchasima", "Hat Yai", "Udon Thani", "Khon Kaen", "Nakhon Si Thammarat",
        "Rayong", "Surat Thani", "Chiang Rai", "Ayutthaya", "Samut Prakan",
        "Nonthaburi", "기타"
    ],
    "USA": [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
        "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
        "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte",
        "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington DC",
        "Boston", "Detroit", "Nashville", "Portland", "Las Vegas",
        "Memphis", "Louisville", "Baltimore", "Milwaukee", "기타"
    ],
    "France": [
        "Paris", "Lyon", "Marseille", "Toulouse", "Nice", 
        "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille",
        "Rennes", "Reims", "Le Havre", "Saint-Étienne", "Toulon", "기타"
    ],
    "Hong Kong": ["Hong Kong", "Kowloon", "New Territories"],
    "Malaysia": [
        "Kuala Lumpur", "Penang", "Johor Bahru", "Malacca", "Ipoh",
        "Kuching", "Kota Kinabalu", "Shah Alam", "Petaling Jaya", "기타"
    ],
    "Singapore": ["Singapore", "Jurong", "Tampines", "Woodlands"],
    "Taiwan": [
        "Taipei", "Kaohsiung", "Taichung", "Tainan", "Hsinchu",
        "Keelung", "Chiayi", "Changhua", "Pingtung", "기타"
    ],
    "Other": ["기타"],
    "기타": ["기타"]
}

# 부서 목록 / Danh sách bộ phận / Departments
DEPARTMENTS = [
    "선택 안 함 / Không chọn / Not Selected",
    "법인장 / Giám đốc Pháp nhân / Corporate Head",
    "구매부서 / Phòng Mua hàng / Purchasing",
    "영업부서 / Phòng Kinh doanh / Sales",
    "생산부서 / Phòng Sản xuất / Production",
    "생산관리부서 / Phòng Quản lý SX / Production Management",
    "품질관리부서 / Phòng Quản lý Chất lượng / Quality Control",
    "품질보증부서 / Phòng Đảm bảo Chất lượng / Quality Assurance",
    "기술부서 / Phòng Kỹ thuật / Engineering",
    "금형부서 / Phòng Khuôn mẫu / Tooling",
    "사출부서 / Phòng Ép phun / Injection Molding",
    "설계부서 / Phòng Thiết kế / Design",
    "연구개발부서 / Phòng R&D / R&D",
    "자재부서 / Phòng Vật tư / Material",
    "물류부서 / Phòng Logistics / Logistics",
    "경영지원부서 / Phòng Hỗ trợ Kinh doanh / Management Support",
    "기타 / Khác / Other"
]

# 직책 목록 / Danh sách chức vụ / Positions
POSITION_OPTIONS = [
    "대표이사 / Giám đốc / CEO",
    "이사 / Giám đốc điều hành / Director",
    "부장 / Trưởng phòng / General Manager",
    "차장 / Phó phòng / Deputy Manager",
    "과장 / Trưởng nhóm / Manager",
    "대리 / Phó nhóm / Assistant Manager",
    "사원 / Nhân viên / Staff",
    "기타 / Khác / Other"
]

# 결제 조건 / Điều kiện thanh toán
PAYMENT_TERMS = [
    "30일 / 30 ngày",
    "60일 / 60 ngày",
    "90일 / 90 ngày",
    "현금 / Tiền mặt",
    "선불 / Trả trước",
    "후불 / Trả sau",
    "Net 30",
    "Net 60",
    "Net 90",
    "COD",
    "Prepaid",
    "Credit"
]
# 업종 매핑 (UI 표시 → DB 저장)
BUSINESS_TYPE_MAPPING = {
    "사출 / Ép phun": "Injection Molding",
    "사출&금형 / Ép phun & Khuôn": "Injection & Tooling",
    "금형 / Khuôn mẫu": "Tooling",
    "브랜드 / Thương hiệu": "Brand",
    "트레이딩 / Thương mại": "Trading",
    "End-User": "End-User",
    "기타 / Khác": "Other"
}

# 업종 역매핑 (DB → UI 표시)
BUSINESS_TYPE_REVERSE = {v: k for k, v in BUSINESS_TYPE_MAPPING.items()}

# 부서 매핑 (UI 표시 → DB 저장)
DEPARTMENT_MAPPING = {
    "선택 안 함 / Không chọn / Not Selected": None,
    "법인장 / Giám đốc Pháp nhân / Corporate Head": "Corporate Head",
    "구매부서 / Phòng Mua hàng / Purchasing": "Purchasing",
    "영업부서 / Phòng Kinh doanh / Sales": "Sales",
    "생산부서 / Phòng Sản xuất / Production": "Production",
    "생산관리부서 / Phòng Quản lý SX / Production Management": "Production Management",
    "품질관리부서 / Phòng Quản lý Chất lượng / Quality Control": "Quality Control",
    "품질보증부서 / Phòng Đảm bảo Chất lượng / Quality Assurance": "Quality Assurance",
    "기술부서 / Phòng Kỹ thuật / Engineering": "Engineering",
    "금형부서 / Phòng Khuôn mẫu / Tooling": "Tooling Department",
    "사출부서 / Phòng Ép phun / Injection Molding": "Injection Molding Department",
    "설계부서 / Phòng Thiết kế / Design": "Design",
    "연구개발부서 / Phòng R&D / R&D": "R&D",
    "자재부서 / Phòng Vật tư / Material": "Material",
    "물류부서 / Phòng Logistics / Logistics": "Logistics",
    "경영지원부서 / Phòng Hỗ trợ Kinh doanh / Management Support": "Management Support",
    "기타 / Khác / Other": "Other"
}

# 부서 역매핑 (DB → UI 표시)
DEPARTMENT_REVERSE = {v: k for k, v in DEPARTMENT_MAPPING.items() if v is not None}

# 직책 매핑 (UI 표시 → DB 저장)
POSITION_MAPPING = {
    "대표이사 / Giám đốc / CEO": "CEO",
    "이사 / Giám đốc điều hành / Director": "Director",
    "부장 / Trưởng phòng / General Manager": "General Manager",
    "차장 / Phó phòng / Deputy Manager": "Deputy Manager",
    "과장 / Trưởng nhóm / Manager": "Manager",
    "대리 / Phó nhóm / Assistant Manager": "Assistant Manager",
    "사원 / Nhân viên / Staff": "Staff",
    "기타 / Khác / Other": "Other"
}

# 직책 역매핑 (DB → UI 표시)
POSITION_REVERSE = {v: k for k, v in POSITION_MAPPING.items()}

def show_customer_management(load_func, save_func, update_func, delete_func, current_user):
    """고객 관리 메인 페이지"""
    st.title("고객 관리 / Quản lý khách hàng")
    
    # 법인별 테이블명 생성
    from utils.helpers import get_company_table
    
    company_code = current_user.get('company')
    if not company_code:
        st.error("법인 정보가 없습니다.")
        return
    
    customer_table = get_company_table('customers', company_code)
    
    # 탭 구성 (통계 탭 추가)
    tab1, tab2, tab3, tab4 = st.tabs([
        "고객 등록 / Đăng ký", 
        "고객 목록 / Danh sách",
        "통계 / Thống kê",
        "CSV 관리 / Quản lý CSV"
    ])
    
    with tab1:
        render_customer_form(save_func, customer_table)
    
    with tab2:
        render_customer_list(load_func, update_func, delete_func, customer_table)
    
    with tab3:
        render_customer_statistics(load_func, customer_table)
    
    with tab4:
        render_csv_management(load_func, save_func, customer_table)

def render_customer_form(save_func, customer_table):
    """고객 등록 폼"""
    st.subheader("🆕 고객 등록 / Đăng ký khách hàng")
    
    with st.form("customer_form", clear_on_submit=True):
        # 회사 정보 섹션
        st.markdown("#### 📋 회사 정보 / Thông tin công ty")
        col1, col2 = st.columns(2)
        
        with col1:
            company_name_original = st.text_input("회사명 (공식) * / Tên công ty (chính thức) *")
            company_name_short = st.text_input("회사명 (짧은) / Tên công ty (ngắn)")
            company_name_english = st.text_input("회사명 (영어) / Tên công ty (tiếng Anh)")
            tax_id = st.text_input("세금 ID / Mã số thuế")
            
        with col2:
            business_type_ui = st.selectbox(
                "업종 / Ngành nghề",
                list(BUSINESS_TYPE_MAPPING.keys())
            )
            
            country = st.selectbox(
                "국가 / Quốc gia",
                ["Vietnam", "Korea", "Japan", "China", "Thailand", "USA", "기타 / Khác"]
            )
            
            # 국가별 주요 도시
            cities = CITIES_BY_COUNTRY.get(country, ["기타"])
            city = st.selectbox("도시 / Thành phố", cities)
            
            address = st.text_area("주소 / Địa chỉ", height=80)
        
        # 고객 위치 정보 (최대 3개)
        st.markdown("#### 📍 고객 위치 (최대 3개) / Vị trí khách hàng (tối đa 3)")
        
        locations = []
        
        for i in range(3):
            st.write(f"**위치 {i+1} / Vị trí {i+1}**")
            col1, col2 = st.columns(2)
            
            with col1:
                location_name = st.text_input(
                    f"위치 이름 / Tên vị trí",
                    placeholder=f"예: 본사, 공장 {i+1}",
                    key=f"location_name_{i}"
                )
            
            with col2:
                map_link = st.text_input(
                    f"구글 지도 링크 / Link Google Maps",
                    placeholder="https://maps.google.com/...",
                    key=f"map_link_{i}"
                )
            
            if location_name and location_name.strip():
                locations.append({
                    'name': location_name.strip(),
                    'map_link': map_link.strip() if map_link and map_link.strip() else None
                })
            
            if i < 2:
                st.markdown("---")
        
        # 담당자 정보 섹션
        st.markdown("#### 👤 담당자 정보 / Thông tin người liên hệ")
        col1, col2 = st.columns(2)
        
        with col1:
            contact_person = st.text_input("담당자명 / Tên người liên hệ")
            
            contact_department_ui = st.selectbox(
                "담당자 부서 / Bộ phận",
                DEPARTMENTS,
                key="contact_department"
            )
            
            if contact_department_ui == "기타 / Khác / Other":
                contact_department_custom = st.text_input(
                    "부서 입력 / Nhập bộ phận",
                    key="contact_department_custom"
                )
                contact_department = contact_department_custom if contact_department_custom.strip() else None
            else:
                contact_department = DEPARTMENT_MAPPING.get(contact_department_ui)
            
            position_ui = st.selectbox(
                "직책 / Chức vụ",
                POSITION_OPTIONS,
                key="position"
            )
            
            if position_ui == "기타 / Khác / Other":
                position_custom = st.text_input(
                    "직책 입력 / Nhập chức vụ",
                    key="position_custom"
                )
                position = position_custom if position_custom.strip() else None
            else:
                position = POSITION_MAPPING.get(position_ui)
            
            email = st.text_input("이메일 / Email")
            
        with col2:
            phone = st.text_input("전화번호 / Số điện thoại")
            mobile = st.text_input("휴대폰 / Di động")
            payment_terms = st.selectbox(
                "결제 조건 / Điều kiện thanh toán",
                PAYMENT_TERMS,
                key="payment_terms"
            )
        
        # ⭐ 구매 직원 정보 섹션 (새로 추가)
        st.markdown("#### 🛒 구매 직원 정보 / Thông tin Nhân viên Mua hàng")
        col1, col2 = st.columns(2)
        
        with col1:
            purchasing_person = st.text_input("구매 직원명 / Tên NV Mua hàng")
            
            purchasing_department_ui = st.selectbox(
                "구매 직원 부서 / Bộ phận",
                DEPARTMENTS,
                key="purchasing_department"
            )
            
            if purchasing_department_ui == "기타 / Khác / Other":
                purchasing_department_custom = st.text_input(
                    "부서 입력 / Nhập bộ phận",
                    key="purchasing_department_custom"
                )
                purchasing_department = purchasing_department_custom if purchasing_department_custom.strip() else None
            else:
                purchasing_department = DEPARTMENT_MAPPING.get(purchasing_department_ui)
            
            purchasing_position_ui = st.selectbox(
                "구매 직원 직책 / Chức vụ",
                POSITION_OPTIONS,
                key="purchasing_position"
            )
            
            if purchasing_position_ui == "기타 / Khác / Other":
                purchasing_position_custom = st.text_input(
                    "직책 입력 / Nhập chức vụ",
                    key="purchasing_position_custom"
                )
                purchasing_position = purchasing_position_custom if purchasing_position_custom.strip() else None
            else:
                purchasing_position = POSITION_MAPPING.get(purchasing_position_ui)
            
            purchasing_email = st.text_input("구매 직원 이메일 / Email NV Mua hàng")
            
        with col2:
            purchasing_phone = st.text_input("구매 직원 연락처 / SĐT NV Mua hàng")
            purchasing_mobile = st.text_input("구매 직원 휴대폰 / Di động NV Mua hàng")
            purchasing_notes = st.text_area("구매 직원 메모 / Ghi chú", height=100)
        
        # KAM 정보 섹션
        st.markdown("#### 🎯 KAM 정보 / Thông tin KAM")
        col1, col2 = st.columns(2)
        
        with col1:
            kam_name = st.text_input("KAM 이름 / Tên KAM")
            
            kam_department_ui = st.selectbox(
                "KAM 부서 / Bộ phận KAM",
                DEPARTMENTS,
                key="kam_department"
            )
            
            if kam_department_ui == "기타 / Khác / Other":
                kam_department_custom = st.text_input(
                    "KAM 부서 입력 / Nhập bộ phận KAM",
                    key="kam_department_custom"
                )
                kam_department = kam_department_custom if kam_department_custom.strip() else None
            else:
                kam_department = DEPARTMENT_MAPPING.get(kam_department_ui)
            
            kam_position = st.text_input("KAM 직책 / Chức vụ KAM")
            kam_email = st.text_input("KAM 이메일 / Email KAM")
            
        with col2:
            kam_phone = st.text_input("KAM 연락처 / Số điện thoại KAM")
            kam_notes = st.text_area("KAM 메모 / Ghi chú KAM", height=100)
        
        # ⭐ KAM II 정보 섹션 (새로 추가)
        st.markdown("#### 🎯 KAM II 정보 / Thông tin KAM II")
        col1, col2 = st.columns(2)
        
        with col1:
            kam2_name = st.text_input("KAM II 이름 / Tên KAM II")
            
            kam2_department_ui = st.selectbox(
                "KAM II 부서 / Bộ phận KAM II",
                DEPARTMENTS,
                key="kam2_department"
            )
            
            if kam2_department_ui == "기타 / Khác / Other":
                kam2_department_custom = st.text_input(
                    "KAM II 부서 입력 / Nhập bộ phận KAM II",
                    key="kam2_department_custom"
                )
                kam2_department = kam2_department_custom if kam2_department_custom.strip() else None
            else:
                kam2_department = DEPARTMENT_MAPPING.get(kam2_department_ui)
            
            kam2_position = st.text_input("KAM II 직책 / Chức vụ KAM II")
            kam2_email = st.text_input("KAM II 이메일 / Email KAM II")
            
        with col2:
            kam2_phone = st.text_input("KAM II 연락처 / Số điện thoại KAM II")
            kam2_notes = st.text_area("KAM II 메모 / Ghi chú KAM II", height=100)
        
        # 기타 정보
        st.markdown("#### 📝 기타 정보 / Thông tin khác")
        col1, col2 = st.columns(2)
        
        with col1:
            status = st.selectbox(
                "상태 / Trạng thái",
                ["active", "inactive", "potential"],
                format_func=lambda x: {
                    "active": "활성 / Hoạt động",
                    "inactive": "비활성 / Không hoạt động",
                    "potential": "잠재 고객 / Tiềm năng"
                }[x]
            )
            
        with col2:
            notes = st.text_area("비고 / Ghi chú", height=100)
        
        submitted = st.form_submit_button("💾 등록 / Đăng ký", use_container_width=True)
        
        if submitted:
            if not company_name_original:
                st.error("❌ 회사명을 입력해주세요 / Vui lòng nhập tên công ty")
                return
            
            import json
            
            customer_data = {
                'company_name_original': company_name_original,
                'company_name_short': company_name_short.strip() if company_name_short and company_name_short.strip() else None,
                'company_name_english': company_name_english.strip() if company_name_english and company_name_english.strip() else None,
                'tax_id': tax_id.strip() if tax_id and tax_id.strip() else None,
                'business_type': BUSINESS_TYPE_MAPPING.get(business_type_ui),
                'country': country,
                'city': city,
                'address': address.strip() if address and address.strip() else None,
                'locations': json.dumps(locations) if locations else json.dumps([]),
                'contact_person': contact_person.strip() if contact_person and contact_person.strip() else None,
                'contact_department': contact_department,
                'position': position,
                'email': email.strip() if email and email.strip() else None,
                'phone': phone.strip() if phone and phone.strip() else None,
                'mobile': mobile.strip() if mobile and mobile.strip() else None,
                'payment_terms': payment_terms if payment_terms else None,
                # ⭐ 구매 직원 정보
                'purchasing_person': purchasing_person.strip() if purchasing_person and purchasing_person.strip() else None,
                'purchasing_department': purchasing_department,
                'purchasing_position': purchasing_position,
                'purchasing_email': purchasing_email.strip() if purchasing_email and purchasing_email.strip() else None,
                'purchasing_phone': purchasing_phone.strip() if purchasing_phone and purchasing_phone.strip() else None,
                'purchasing_mobile': purchasing_mobile.strip() if purchasing_mobile and purchasing_mobile.strip() else None,
                'purchasing_notes': purchasing_notes.strip() if purchasing_notes and purchasing_notes.strip() else None,
                # KAM 정보
                'kam_name': kam_name.strip() if kam_name and kam_name.strip() else None,
                'kam_department': kam_department,
                'kam_position': kam_position.strip() if kam_position and kam_position.strip() else None,
                'kam_email': kam_email.strip() if kam_email and kam_email.strip() else None,
                'kam_phone': kam_phone.strip() if kam_phone and kam_phone.strip() else None,
                'kam_notes': kam_notes.strip() if kam_notes and kam_notes.strip() else None,
                # ⭐ KAM II 정보
                'kam2_name': kam2_name.strip() if kam2_name and kam2_name.strip() else None,
                'kam2_department': kam2_department,
                'kam2_position': kam2_position.strip() if kam2_position and kam2_position.strip() else None,
                'kam2_email': kam2_email.strip() if kam2_email and kam2_email.strip() else None,
                'kam2_phone': kam2_phone.strip() if kam2_phone and kam2_phone.strip() else None,
                'kam2_notes': kam2_notes.strip() if kam2_notes and kam2_notes.strip() else None,
                'status': status,
                'notes': notes.strip() if notes and notes.strip() else None,
                'created_at': datetime.now().isoformat()
            }
            
            result = save_func(customer_table, customer_data)
            
            if result:
                st.success("✅ 고객이 성공적으로 등록되었습니다 / Đã đăng ký khách hàng thành công")
                st.rerun()
            else:
                st.error("❌ 등록 중 오류가 발생했습니다 / Có lỗi xảy ra khi đăng ký")

def render_customer_edit_form(customer, update_func, customer_table):
    """고객 정보 수정 폼"""
    customer_id = customer['id']
    st.subheader(f"✏️ 고객 정보 수정 / Chỉnh sửa thông tin khách hàng")
    
    def safe_get(key, default=''):
        value = customer.get(key)
        if pd.isna(value) or value is None:
            return default
        return str(value).strip() if str(value).strip() else default
    
    # 기존 위치 정보 로드
    import json
    existing_locations = []
    try:
        locations_data = customer.get('locations')
        if locations_data:
            if isinstance(locations_data, str):
                existing_locations = json.loads(locations_data)
            elif isinstance(locations_data, list):
                existing_locations = locations_data
    except:
        existing_locations = []
    
    while len(existing_locations) < 3:
        existing_locations.append({'name': '', 'map_link': ''})
    
    # ⭐ Form 밖에서 국가 선택 (동적 업데이트 위해)
    country_list = [
        "Vietnam", "Korea", "Japan", "China", "Thailand", "USA", 
        "France", "Hong Kong", "Malaysia", "Singapore", 
        "Taiwan", "Other", "기타"
    ]
    country_value = safe_get('country', 'Vietnam')
    country_index = country_list.index(country_value) if country_value in country_list else 0
    
    selected_country = st.selectbox(
        "🌍 국가 선택 (먼저 선택) / Chọn quốc gia",
        country_list,
        index=country_index,
        key=f"country_selector_{customer_id}"
    )
    
    # 선택된 국가의 도시 목록
    cities = CITIES_BY_COUNTRY.get(selected_country, ["기타"])
    
    st.markdown("---")
    
    with st.form("customer_edit_form"):
        # 회사 정보 섹션
        st.markdown("#### 📋 회사 정보 / Thông tin công ty")
        col1, col2 = st.columns(2)
        
        with col1:
            company_name_original = st.text_input(
                "회사명 (공식) * / Tên công ty (chính thức) *",
                value=safe_get('company_name_original')
            )
            company_name_short = st.text_input(
                "회사명 (짧은) / Tên công ty (ngắn)",
                value=safe_get('company_name_short')
            )
            company_name_english = st.text_input(
                "회사명 (영어) / Tên công ty (tiếng Anh)",
                value=safe_get('company_name_english')
            )
            tax_id = st.text_input(
                "세금 ID / Mã số thuế",
                value=safe_get('tax_id')
            )
            
        with col2:
            # 업종
            current_business_type = safe_get('business_type')
            business_type_ui_value = BUSINESS_TYPE_REVERSE.get(current_business_type, list(BUSINESS_TYPE_MAPPING.keys())[0])
            business_type_list = list(BUSINESS_TYPE_MAPPING.keys())
            business_type_index = business_type_list.index(business_type_ui_value) if business_type_ui_value in business_type_list else 0
            
            business_type_ui = st.selectbox(
                "업종 / Ngành nghề",
                business_type_list,
                index=business_type_index
            )
            
            # ⭐ 국가는 form 밖에서 선택됨 (읽기 전용 표시)
            st.info(f"선택된 국가 / Quốc gia: **{selected_country}**")
            
            # ⭐ 도시는 선택된 국가에 따라 자동 업데이트
            city_value = safe_get('city')
            city_index = cities.index(city_value) if city_value in cities else 0
            
            city = st.selectbox("도시 / Thành phố", cities, index=city_index)
            
            address = st.text_area(
                "주소 / Địa chỉ",
                value=safe_get('address'),
                height=80
            )
        
        # 고객 위치 정보 (최대 3개)
        st.markdown("#### 📍 고객 위치 (최대 3개) / Vị trí khách hàng (tối đa 3)")
        
        locations = []
        
        for i in range(3):
            st.write(f"**위치 {i+1} / Vị trí {i+1}**")
            col1, col2 = st.columns(2)
            
            existing_name = existing_locations[i].get('name', '') if i < len(existing_locations) else ''
            existing_link = existing_locations[i].get('map_link', '') if i < len(existing_locations) else ''
            
            with col1:
                location_name = st.text_input(
                    f"위치 이름 / Tên vị trí",
                    value=existing_name,
                    placeholder=f"예: 본사, 공장 {i+1}",
                    key=f"edit_location_name_{i}"
                )
            
            with col2:
                map_link = st.text_input(
                    f"구글 지도 링크 / Link Google Maps",
                    value=existing_link,
                    placeholder="https://maps.google.com/...",
                    key=f"edit_map_link_{i}"
                )
            
            if location_name and location_name.strip():
                locations.append({
                    'name': location_name.strip(),
                    'map_link': map_link.strip() if map_link and map_link.strip() else None
                })
            
            if i < 2:
                st.markdown("---")
        
        # 담당자 정보 (계속)...
        st.markdown("#### 👤 담당자 정보 / Thông tin người liên hệ")
        col1, col2 = st.columns(2)
        
        with col1:
            contact_person = st.text_input(
                "담당자명 / Tên người liên hệ",
                value=safe_get('contact_person')
            )
            
            current_contact_dept = safe_get('contact_department')
            contact_dept_ui_value = DEPARTMENT_REVERSE.get(current_contact_dept, "선택 안 함 / Không chọn / Not Selected")
            
            if contact_dept_ui_value in DEPARTMENTS:
                contact_dept_index = DEPARTMENTS.index(contact_dept_ui_value)
            else:
                contact_dept_index = DEPARTMENTS.index("기타 / Khác / Other")
            
            contact_department_ui = st.selectbox(
                "담당자 부서 / Bộ phận",
                DEPARTMENTS,
                index=contact_dept_index,
                key="edit_contact_department"
            )
            
            if contact_department_ui == "기타 / Khác / Other":
                default_dept = current_contact_dept if current_contact_dept not in DEPARTMENT_MAPPING.values() else ""
                contact_department_custom = st.text_input(
                    "부서 입력 / Nhập bộ phận",
                    value=default_dept,
                    key="edit_contact_department_custom"
                )
                contact_department = contact_department_custom.strip() if contact_department_custom and contact_department_custom.strip() else None
            else:
                contact_department = DEPARTMENT_MAPPING.get(contact_department_ui)
            
            current_position = safe_get('position')
            position_ui_value = POSITION_REVERSE.get(current_position, "기타 / Khác / Other")
            
            if position_ui_value in POSITION_OPTIONS:
                position_index = POSITION_OPTIONS.index(position_ui_value)
            else:
                position_index = POSITION_OPTIONS.index("기타 / Khác / Other")
            
            position_ui = st.selectbox(
                "직책 / Chức vụ",
                POSITION_OPTIONS,
                index=position_index,
                key="edit_position"
            )
            
            if position_ui == "기타 / Khác / Other":
                default_position = current_position if current_position not in POSITION_MAPPING.values() else ""
                position_custom = st.text_input(
                    "직책 입력 / Nhập chức vụ",
                    value=default_position,
                    key="edit_position_custom"
                )
                position = position_custom.strip() if position_custom and position_custom.strip() else None
            else:
                position = POSITION_MAPPING.get(position_ui)
            
            email = st.text_input(
                "이메일 / Email",
                value=safe_get('email')
            )
            
        with col2:
            phone = st.text_input(
                "전화번호 / Số điện thoại",
                value=safe_get('phone')
            )
            mobile = st.text_input(
                "휴대폰 / Di động",
                value=safe_get('mobile')
            )
            
            payment_terms_value = safe_get('payment_terms')
            payment_terms_index = PAYMENT_TERMS.index(payment_terms_value) if payment_terms_value in PAYMENT_TERMS else 0
            
            payment_terms = st.selectbox(
                "결제 조건 / Điều kiện thanh toán",
                PAYMENT_TERMS,
                index=payment_terms_index,
                key="edit_payment_terms"
            )
        
        # ⭐ 구매 직원 정보
        st.markdown("#### 🛒 구매 직원 정보 / Thông tin Nhân viên Mua hàng")
        col1, col2 = st.columns(2)
        
        with col1:
            purchasing_person = st.text_input(
                "구매 직원명 / Tên NV Mua hàng",
                value=safe_get('purchasing_person')
            )
            
            current_purchasing_dept = safe_get('purchasing_department')
            purchasing_dept_ui_value = DEPARTMENT_REVERSE.get(current_purchasing_dept, "선택 안 함 / Không chọn / Not Selected")
            
            if purchasing_dept_ui_value in DEPARTMENTS:
                purchasing_dept_index = DEPARTMENTS.index(purchasing_dept_ui_value)
            else:
                purchasing_dept_index = DEPARTMENTS.index("기타 / Khác / Other")
            
            purchasing_department_ui = st.selectbox(
                "구매 직원 부서 / Bộ phận",
                DEPARTMENTS,
                index=purchasing_dept_index,
                key="edit_purchasing_department"
            )
            
            if purchasing_department_ui == "기타 / Khác / Other":
                default_purchasing_dept = current_purchasing_dept if current_purchasing_dept not in DEPARTMENT_MAPPING.values() else ""
                purchasing_department_custom = st.text_input(
                    "부서 입력 / Nhập bộ phận",
                    value=default_purchasing_dept,
                    key="edit_purchasing_department_custom"
                )
                purchasing_department = purchasing_department_custom.strip() if purchasing_department_custom and purchasing_department_custom.strip() else None
            else:
                purchasing_department = DEPARTMENT_MAPPING.get(purchasing_department_ui)
            
            current_purchasing_position = safe_get('purchasing_position')
            purchasing_position_ui_value = POSITION_REVERSE.get(current_purchasing_position, "기타 / Khác / Other")
            
            if purchasing_position_ui_value in POSITION_OPTIONS:
                purchasing_position_index = POSITION_OPTIONS.index(purchasing_position_ui_value)
            else:
                purchasing_position_index = POSITION_OPTIONS.index("기타 / Khác / Other")
            
            purchasing_position_ui = st.selectbox(
                "구매 직원 직책 / Chức vụ",
                POSITION_OPTIONS,
                index=purchasing_position_index,
                key="edit_purchasing_position"
            )
            
            if purchasing_position_ui == "기타 / Khác / Other":
                default_purchasing_position = current_purchasing_position if current_purchasing_position not in POSITION_MAPPING.values() else ""
                purchasing_position_custom = st.text_input(
                    "직책 입력 / Nhập chức vụ",
                    value=default_purchasing_position,
                    key="edit_purchasing_position_custom"
                )
                purchasing_position = purchasing_position_custom.strip() if purchasing_position_custom and purchasing_position_custom.strip() else None
            else:
                purchasing_position = POSITION_MAPPING.get(purchasing_position_ui)
            
            purchasing_email = st.text_input(
                "구매 직원 이메일 / Email",
                value=safe_get('purchasing_email')
            )
            
        with col2:
            purchasing_phone = st.text_input(
                "구매 직원 연락처 / SĐT",
                value=safe_get('purchasing_phone')
            )
            purchasing_mobile = st.text_input(
                "구매 직원 휴대폰 / Di động",
                value=safe_get('purchasing_mobile')
            )
            purchasing_notes = st.text_area(
                "구매 직원 메모 / Ghi chú",
                value=safe_get('purchasing_notes'),
                height=100
            )
        
        # KAM 정보 (계속)...
        st.markdown("#### 🎯 KAM 정보 / Thông tin KAM")
        col1, col2 = st.columns(2)
        
        with col1:
            kam_name = st.text_input(
                "KAM 이름 / Tên KAM",
                value=safe_get('kam_name')
            )
            
            current_kam_dept = safe_get('kam_department')
            kam_dept_ui_value = DEPARTMENT_REVERSE.get(current_kam_dept, "선택 안 함 / Không chọn / Not Selected")
            
            if kam_dept_ui_value in DEPARTMENTS:
                kam_dept_index = DEPARTMENTS.index(kam_dept_ui_value)
            else:
                kam_dept_index = DEPARTMENTS.index("기타 / Khác / Other")
            
            kam_department_ui = st.selectbox(
                "KAM 부서 / Bộ phận KAM",
                DEPARTMENTS,
                index=kam_dept_index,
                key="edit_kam_department"
            )
            
            if kam_department_ui == "기타 / Khác / Other":
                default_kam_dept = current_kam_dept if current_kam_dept not in DEPARTMENT_MAPPING.values() else ""
                kam_department_custom = st.text_input(
                    "KAM 부서 입력 / Nhập bộ phận KAM",
                    value=default_kam_dept,
                    key="edit_kam_department_custom"
                )
                kam_department = kam_department_custom.strip() if kam_department_custom and kam_department_custom.strip() else None
            else:
                kam_department = DEPARTMENT_MAPPING.get(kam_department_ui)
            
            kam_position = st.text_input(
                "KAM 직책 / Chức vụ KAM",
                value=safe_get('kam_position')
            )
            
            kam_email = st.text_input(
                "KAM 이메일 / Email KAM",
                value=safe_get('kam_email')
            )
            
        with col2:
            kam_phone = st.text_input(
                "KAM 연락처 / Số điện thoại KAM",
                value=safe_get('kam_phone')
            )
            kam_notes = st.text_area(
                "KAM 메모 / Ghi chú KAM",
                value=safe_get('kam_notes'),
                height=100
            )
        
        # ⭐ KAM II 정보
        st.markdown("#### 🎯 KAM II 정보 / Thông tin KAM II")
        col1, col2 = st.columns(2)
        
        with col1:
            kam2_name = st.text_input(
                "KAM II 이름 / Tên KAM II",
                value=safe_get('kam2_name')
            )
            
            current_kam2_dept = safe_get('kam2_department')
            kam2_dept_ui_value = DEPARTMENT_REVERSE.get(current_kam2_dept, "선택 안 함 / Không chọn / Not Selected")
            
            if kam2_dept_ui_value in DEPARTMENTS:
                kam2_dept_index = DEPARTMENTS.index(kam2_dept_ui_value)
            else:
                kam2_dept_index = DEPARTMENTS.index("기타 / Khác / Other")
            
            kam2_department_ui = st.selectbox(
                "KAM II 부서 / Bộ phận KAM II",
                DEPARTMENTS,
                index=kam2_dept_index,
                key="edit_kam2_department"
            )
            
            if kam2_department_ui == "기타 / Khác / Other":
                default_kam2_dept = current_kam2_dept if current_kam2_dept not in DEPARTMENT_MAPPING.values() else ""
                kam2_department_custom = st.text_input(
                    "KAM II 부서 입력 / Nhập bộ phận KAM II",
                    value=default_kam2_dept,
                    key="edit_kam2_department_custom"
                )
                kam2_department = kam2_department_custom.strip() if kam2_department_custom and kam2_department_custom.strip() else None
            else:
                kam2_department = DEPARTMENT_MAPPING.get(kam2_department_ui)
            
            kam2_position = st.text_input(
                "KAM II 직책 / Chức vụ KAM II",
                value=safe_get('kam2_position')
            )
            
            kam2_email = st.text_input(
                "KAM II 이메일 / Email KAM II",
                value=safe_get('kam2_email')
            )
            
        with col2:
            kam2_phone = st.text_input(
                "KAM II 연락처 / Số điện thoại KAM II",
                value=safe_get('kam2_phone')
            )
            kam2_notes = st.text_area(
                "KAM II 메모 / Ghi chú KAM II",
                value=safe_get('kam2_notes'),
                height=100
            )
        
        # 기타 정보
        st.markdown("#### 📝 기타 정보 / Thông tin khác")
        col1, col2 = st.columns(2)
        
        with col1:
            status_list = ["active", "inactive", "potential"]
            status_value = safe_get('status', 'active')
            status_index = status_list.index(status_value) if status_value in status_list else 0
            
            status = st.selectbox(
                "상태 / Trạng thái",
                status_list,
                index=status_index,
                format_func=lambda x: {
                    "active": "활성 / Hoạt động",
                    "inactive": "비활성 / Không hoạt động",
                    "potential": "잠재 고객 / Tiềm năng"
                }[x]
            )
            
        with col2:
            notes = st.text_area(
                "비고 / Ghi chú",
                value=safe_get('notes'),
                height=100
            )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 수정 저장 / Lưu thay đổi", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ 취소 / Hủy", use_container_width=True)
        
        if cancelled:
            st.session_state[f"edit_customer_{customer_id}"] = False
            st.rerun()
        
        if submitted:
            if not company_name_original:
                st.error("❌ 회사명을 입력해주세요 / Vui lòng nhập tên công ty")
                return
            
            # 데이터 업데이트
            updated_data = {
                'id': customer_id,
                'company_name_original': company_name_original,
                'company_name_short': company_name_short.strip() if company_name_short and company_name_short.strip() else None,
                'company_name_english': company_name_english.strip() if company_name_english and company_name_english.strip() else None,
                'tax_id': tax_id.strip() if tax_id and tax_id.strip() else None,
                'business_type': BUSINESS_TYPE_MAPPING.get(business_type_ui),
                'country': selected_country,  # ⭐ form 밖에서 선택한 국가 사용
                'city': city,
                'address': address.strip() if address and address.strip() else None,
                'locations': json.dumps(locations) if locations else json.dumps([]),
                'contact_person': contact_person.strip() if contact_person and contact_person.strip() else None,
                'contact_department': contact_department,
                'position': position,
                'email': email.strip() if email and email.strip() else None,
                'phone': phone.strip() if phone and phone.strip() else None,
                'mobile': mobile.strip() if mobile and mobile.strip() else None,
                'payment_terms': payment_terms if payment_terms else None,
                # ⭐ 구매 직원 정보
                'purchasing_person': purchasing_person.strip() if purchasing_person and purchasing_person.strip() else None,
                'purchasing_department': purchasing_department,
                'purchasing_position': purchasing_position,
                'purchasing_email': purchasing_email.strip() if purchasing_email and purchasing_email.strip() else None,
                'purchasing_phone': purchasing_phone.strip() if purchasing_phone and purchasing_phone.strip() else None,
                'purchasing_mobile': purchasing_mobile.strip() if purchasing_mobile and purchasing_mobile.strip() else None,
                'purchasing_notes': purchasing_notes.strip() if purchasing_notes and purchasing_notes.strip() else None,
                # KAM 정보
                'kam_name': kam_name.strip() if kam_name and kam_name.strip() else None,
                'kam_department': kam_department,
                'kam_position': kam_position.strip() if kam_position and kam_position.strip() else None,
                'kam_email': kam_email.strip() if kam_email and kam_email.strip() else None,
                'kam_phone': kam_phone.strip() if kam_phone and kam_phone.strip() else None,
                'kam_notes': kam_notes.strip() if kam_notes and kam_notes.strip() else None,
                # ⭐ KAM II 정보
                'kam2_name': kam2_name.strip() if kam2_name and kam2_name.strip() else None,
                'kam2_department': kam2_department,
                'kam2_position': kam2_position.strip() if kam2_position and kam2_position.strip() else None,
                'kam2_email': kam2_email.strip() if kam2_email and kam2_email.strip() else None,
                'kam2_phone': kam2_phone.strip() if kam2_phone and kam2_phone.strip() else None,
                'kam2_notes': kam2_notes.strip() if kam2_notes and kam2_notes.strip() else None,
                'status': status,
                'notes': notes.strip() if notes and notes.strip() else None,
                'updated_at': datetime.now().isoformat()
            }
            
            result = update_func(customer_table, updated_data)
            
            if result:
                st.success("✅ 고객 정보가 성공적으로 수정되었습니다 / Đã cập nhật thông tin khách hàng")
                st.session_state[f"edit_customer_{customer_id}"] = False
                st.rerun()
            else:
                st.error("❌ 수정 중 오류가 발생했습니다 / Có lỗi xảy ra khi cập nhật")

def render_customer_list(load_func, update_func, delete_func, customer_table):
    """고객 목록 (테이블 형식)"""
    st.header("고객 목록 / Danh sách khách hàng")
    
    try:
        customers_data = load_func(customer_table)
        
        if not customers_data:
            st.info("등록된 고객이 없습니다. / Chưa có khách hàng nào.")
            return
        
        # DataFrame 변환
        if isinstance(customers_data, list):
            customers_df = pd.DataFrame(customers_data)
        else:
            customers_df = customers_data
        
        if customers_df.empty:
            st.info("등록된 고객이 없습니다. / Chưa có khách hàng nào.")
            return
        
        # 🔍 검색 패널 (항상 펼쳐진 상태)
        st.subheader("🔍 검색 / Tìm kiếm")
        
        search_col1, search_col2, search_col3, search_col4 = st.columns([3, 2, 2, 1])
        
        with search_col1:
            search_name = st.text_input(
                "회사명 검색 / Tìm tên công ty",
                placeholder="회사명 입력 / Nhập tên",
                key="search_customer_name",
                label_visibility="collapsed"
            )
        
        with search_col2:
            # 업종 필터
            business_types = ["전체 / Tất cả"]
            if 'business_type' in customers_df.columns:
                unique_types = customers_df['business_type'].dropna().unique().tolist()
                for db_type in unique_types:
                    ui_type = BUSINESS_TYPE_REVERSE.get(db_type, db_type)
                    if ui_type not in business_types:
                        business_types.append(ui_type)
            
            search_business_type = st.selectbox(
                "업종",
                business_types,
                key="search_business_type",
                label_visibility="collapsed"
            )
        
        with search_col3:
            # 국가 필터
            countries = ["전체 / Tất cả"]
            if 'country' in customers_df.columns:
                unique_countries = customers_df['country'].dropna().unique().tolist()
                countries.extend(sorted(unique_countries))
            
            search_country = st.selectbox(
                "국가",
                countries,
                key="search_country",
                label_visibility="collapsed"
            )
        
        with search_col4:
            if st.button("🔍 검색", use_container_width=True, type="primary"):
                pass  # 검색은 자동으로 적용됨
        
        # 추가 필터 (접을 수 있음)
        with st.expander("🔧 추가 필터 / Bộ lọc thêm"):
            filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
            
            with filter_col1:
                # 도시 필터
                cities = ["전체 / Tất cả"]
                if search_country != "전체 / Tất cả" and 'city' in customers_df.columns:
                    country_customers = customers_df[customers_df['country'] == search_country]
                    unique_cities = country_customers['city'].dropna().unique().tolist()
                    cities.extend(sorted(unique_cities))
                elif 'city' in customers_df.columns:
                    unique_cities = customers_df['city'].dropna().unique().tolist()
                    cities.extend(sorted(unique_cities))
                
                search_city = st.selectbox(
                    "도시 / Thành phố",
                    cities,
                    key="search_city"
                )
            
            with filter_col2:
                search_status = st.selectbox(
                    "상태 / Trạng thái",
                    ["전체 / Tất cả", "active", "inactive", "potential"],
                    key="search_status"
                )
            
            with filter_col3:
                search_kam = st.selectbox(
                    "KAM 할당",
                    ["전체 / Tất cả", "할당됨", "미할당"],
                    key="search_kam"
                )
            
            with filter_col4:
                search_contact = st.text_input(
                    "담당자명",
                    placeholder="담당자명",
                    key="search_contact_person"
                )
            
            # 등록일 범위
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                search_date_from = st.date_input(
                    "등록일 시작 / Từ ngày",
                    value=None,
                    key="search_date_from"
                )
            with date_col2:
                search_date_to = st.date_input(
                    "등록일 종료 / Đến ngày",
                    value=None,
                    key="search_date_to"
                )
            
            # 초기화 버튼
            if st.button("🔄 검색 초기화 / Đặt lại", use_container_width=True):
                for key in ['search_customer_name', 'search_business_type', 'search_status', 
                           'search_country', 'search_city', 'search_kam', 'search_contact_person',
                           'search_date_from', 'search_date_to']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        # 데이터 필터링
        filtered_df = customers_df.copy()
        
        # 1. 이름 검색
        if search_name and search_name.strip():
            search_term = search_name.strip().lower()
            mask = (
                filtered_df['company_name_original'].fillna('').str.lower().str.contains(search_term, na=False) |
                filtered_df['company_name_short'].fillna('').str.lower().str.contains(search_term, na=False) |
                filtered_df['company_name_english'].fillna('').str.lower().str.contains(search_term, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # 2. 업종 필터
        if search_business_type != "전체 / Tất cả":
            business_type_db = BUSINESS_TYPE_MAPPING.get(search_business_type, search_business_type)
            filtered_df = filtered_df[filtered_df['business_type'] == business_type_db]
        
        # 3. 국가 필터
        if search_country != "전체 / Tất cả":
            filtered_df = filtered_df[filtered_df['country'] == search_country]
        
        # 4. 도시 필터
        if search_city != "전체 / Tất cả":
            filtered_df = filtered_df[filtered_df['city'] == search_city]
        
        # 5. 상태 필터
        if search_status != "전체 / Tất cả":
            filtered_df = filtered_df[filtered_df['status'] == search_status]
        
        # 6. KAM 할당 필터
        if search_kam == "할당됨":
            filtered_df = filtered_df[filtered_df['kam_name'].notna()]
        elif search_kam == "미할당":
            filtered_df = filtered_df[filtered_df['kam_name'].isna()]
        
        # 7. 담당자명 검색
        if search_contact and search_contact.strip():
            contact_term = search_contact.strip().lower()
            filtered_df = filtered_df[
                filtered_df['contact_person'].fillna('').str.lower().str.contains(contact_term, na=False)
            ]
        
        # 8. 등록일 범위
        if search_date_from:
            filtered_df = filtered_df[
                pd.to_datetime(filtered_df['created_at']).dt.date >= search_date_from
            ]
        if search_date_to:
            filtered_df = filtered_df[
                pd.to_datetime(filtered_df['created_at']).dt.date <= search_date_to
            ]
        
        # 정렬
        filtered_df = filtered_df.sort_values('created_at', ascending=False)
        
        st.markdown("---")
        
        # 통계 및 다운로드
        result_col1, result_col2, result_col3 = st.columns([2, 2, 1])
        
        with result_col1:
            st.write(f"📋 검색 결과: **{len(filtered_df)}건** / Kết quả: **{len(filtered_df)}**")
        
        with result_col2:
            if len(filtered_df) != len(customers_df):
                st.info(f"전체 {len(customers_df)}건 중 {len(filtered_df)}건 표시")
        
        with result_col3:
            if not filtered_df.empty:
                csv_data = generate_customer_csv(filtered_df)
                st.download_button(
                    label="📥 CSV",
                    data=csv_data,
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # 검색 결과 없음
        if filtered_df.empty:
            st.warning("검색 조건에 맞는 고객이 없습니다. / Không tìm thấy khách hàng phù hợp.")
            return
        
        st.markdown("---")
        
        # ⭐ 상세 정보 확인 섹션 (검색 결과 밑으로 이동)
        st.subheader("📄 상세 정보 확인 / Xem chi tiết")
        
        detail_col1, detail_col2 = st.columns([2, 3])
        
        with detail_col1:
            # 고객 선택 (검색 결과에서)
            customer_options = {}
            for idx, customer in filtered_df.iterrows():
                customer_id = customer.get('id')
                display_name = customer.get('company_name_short') or customer.get('company_name_original') or 'N/A'
                customer_options[f"{customer_id} - {display_name}"] = customer_id
            
            selected_customer_key = st.selectbox(
                "고객 선택 / Chọn khách hàng",
                options=["선택하세요 / Chọn"] + list(customer_options.keys()),
                key="selected_customer_detail"
            )
        
        with detail_col2:
            if selected_customer_key != "선택하세요 / Chọn":
                if st.button("📄 상세보기 / Xem chi tiết", use_container_width=True, type="primary"):
                    selected_customer_id = customer_options[selected_customer_key]
                    st.session_state['show_customer_detail'] = selected_customer_id
                    st.rerun()
        
        # 선택된 고객 상세 정보 표시
        if 'show_customer_detail' in st.session_state and st.session_state['show_customer_detail']:
            customer_id = st.session_state['show_customer_detail']
            customer = filtered_df[filtered_df['id'] == customer_id].iloc[0]
            
            # 수정 모드 확인
            if st.session_state.get(f"edit_customer_{customer_id}", False):
                render_customer_edit_form(customer, update_func, customer_table)
            else:
                render_customer_detail_view(customer, update_func, delete_func, load_func, customer_table)
        
        st.markdown("---")
        st.markdown("---")
        
        # 📊 테이블 형식으로 고객 목록 표시 (맨 아래로 이동)
        st.subheader("📋 고객 테이블 / Bảng khách hàng")
        
        # 안전한 값 가져오기 함수
        def safe_get(row, key, default=''):
            value = row.get(key)
            if pd.isna(value) or value is None:
                return default
            return str(value).strip() if str(value).strip() else default
        
        # 테이블 데이터 준비
        table_data = []
        for idx, customer in filtered_df.iterrows():
            customer_id = customer.get('id')
            
            # 표시할 회사명
            display_name = safe_get(customer, 'company_name_short') or safe_get(customer, 'company_name_original') or 'N/A'
            
            # 업종 변환
            business_type_db = safe_get(customer, 'business_type')
            business_type_ui = BUSINESS_TYPE_REVERSE.get(business_type_db, business_type_db or '-')
            
            # 상태 아이콘
            status = safe_get(customer, 'status', 'active')
            status_icons = {
                "active": "✅",
                "inactive": "⏸️",
                "potential": "🌱"
            }
            status_icon = status_icons.get(status, "❓")
            
            table_data.append({
                'ID': customer_id,
                '회사명 / Tên CT': display_name,
                '업종 / Ngành': business_type_ui,
                '국가 / Quốc gia': safe_get(customer, 'country', '-'),
                '도시 / Thành phố': safe_get(customer, 'city', '-'),
                '담당자 / Người LH': safe_get(customer, 'contact_person', '-'),
                '전화 / SĐT': safe_get(customer, 'phone', '-'),
                '상태': status_icon,
                'KAM': safe_get(customer, 'kam_name', '-')
            })
        
        # DataFrame으로 변환
        table_df = pd.DataFrame(table_data)
        
        # Streamlit 데이터프레임 표시 (인터랙티브)
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "회사명 / Tên CT": st.column_config.TextColumn("회사명 / Tên CT", width="large"),
                "업종 / Ngành": st.column_config.TextColumn("업종 / Ngành", width="medium"),
                "국가 / Quốc gia": st.column_config.TextColumn("국가", width="small"),
                "도시 / Thành phố": st.column_config.TextColumn("도시", width="medium"),
                "담당자 / Người LH": st.column_config.TextColumn("담당자", width="medium"),
                "전화 / SĐT": st.column_config.TextColumn("전화", width="medium"),
                "상태": st.column_config.TextColumn("상태", width="small"),
                "KAM": st.column_config.TextColumn("KAM", width="medium")
            }
        )
    
    except Exception as e:
        logging.error(f"고객 목록 로드 오류: {str(e)}")
        st.error(f"고객 목록 로딩 중 오류가 발생했습니다 / Lỗi tải danh sách: {str(e)}")

def render_customer_detail_view(customer, update_func, delete_func, load_func, customer_table):
    """고객 상세 정보 확인"""
    customer_id = customer['id']
    
    st.markdown("---")
    st.markdown("---")
    
    # 고객 정보 헤더
    name = customer.get('company_name_short') or customer.get('company_name_original')
    
    # 헤더
    header_col1, header_col2 = st.columns([4, 1])
    
    with header_col1:
        st.subheader(f"📋 {name} - 상세 정보")
    
    with header_col2:
        if st.button("❌ 닫기", key="btn_close_customer_detail_main", use_container_width=True):
            if 'show_customer_detail' in st.session_state:
                del st.session_state['show_customer_detail']
            st.rerun()
    
    st.markdown("---")
    
    # 안전한 값 가져오기
    def safe_get(key, default=''):
        value = customer.get(key)
        if pd.isna(value) or value is None:
            return default
        return str(value).strip() if str(value).strip() else default
    
    # 기본 정보
    st.markdown("#### 🏢 기본 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**회사명 (원어):** {safe_get('company_name_original', 'N/A')}")
        st.write(f"**회사명 (약칭):** {safe_get('company_name_short', 'N/A')}")
        st.write(f"**회사명 (영문):** {safe_get('company_name_english', 'N/A')}")
        st.write(f"**세금 ID:** {safe_get('tax_id', 'N/A')}")
        
        # 업종 변환
        business_type_db = safe_get('business_type')
        business_type_ui = BUSINESS_TYPE_REVERSE.get(business_type_db, business_type_db or 'N/A')
        st.write(f"**업종:** {business_type_ui}")
    
    with col2:
        st.write(f"**국가:** {safe_get('country', 'N/A')}")
        st.write(f"**도시:** {safe_get('city', 'N/A')}")
        st.write(f"**주소:** {safe_get('address', 'N/A')}")
        
        status = safe_get('status', 'active')
        status_display = {
            "active": "✅ 활성",
            "inactive": "⏸️ 비활성",
            "potential": "🌱 잠재고객"
        }.get(status, status)
        st.write(f"**상태:** {status_display}")
    
    st.markdown("---")
    
    # 고객 위치 정보 (최대 3개)
    st.markdown("#### 📍 고객 위치")
    
    import json
    locations = []
    try:
        locations_data = customer.get('locations')
        if locations_data:
            if isinstance(locations_data, str):
                locations = json.loads(locations_data)
            elif isinstance(locations_data, list):
                locations = locations_data
    except:
        locations = []
    
    if locations:
        for i, location in enumerate(locations, 1):
            location_name = location.get('name', 'N/A')
            map_link = location.get('map_link')
            
            st.write(f"**위치 {i}: {location_name}**")
            if map_link and map_link.strip():
                st.markdown(f"  🗺️ [구글 지도 보기]({map_link})")
            else:
                st.write("  🗺️ 지도 링크 없음")
            
            if i < len(locations):
                st.write("")
    else:
        st.info("등록된 위치 정보가 없습니다.")
    
    st.markdown("---")
    
    # 담당자 정보
    st.markdown("#### 👤 담당자 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**담당자명:** {safe_get('contact_person', 'N/A')}")
        
        # 부서 변환
        dept_db = safe_get('contact_department')
        dept_ui = DEPARTMENT_REVERSE.get(dept_db, dept_db or 'N/A')
        st.write(f"**부서:** {dept_ui}")
        
        # 직책 변환
        position_db = safe_get('position')
        position_ui = POSITION_REVERSE.get(position_db, position_db or 'N/A')
        st.write(f"**직책:** {position_ui}")
    
    with col2:
        st.write(f"**이메일:** {safe_get('email', 'N/A')}")
        st.write(f"**연락처:** {safe_get('phone', 'N/A')}")
        st.write(f"**모바일:** {safe_get('mobile', 'N/A')}")
    
    st.markdown("---")
    
    # ⭐ 구매 직원 정보
    st.markdown("#### 🛒 구매 직원 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**구매 직원명:** {safe_get('purchasing_person', 'N/A')}")
        
        # 구매 직원 부서 변환
        purchasing_dept_db = safe_get('purchasing_department')
        purchasing_dept_ui = DEPARTMENT_REVERSE.get(purchasing_dept_db, purchasing_dept_db or 'N/A')
        st.write(f"**부서:** {purchasing_dept_ui}")
        
        # 구매 직원 직책 변환
        purchasing_position_db = safe_get('purchasing_position')
        purchasing_position_ui = POSITION_REVERSE.get(purchasing_position_db, purchasing_position_db or 'N/A')
        st.write(f"**직책:** {purchasing_position_ui}")
        
        st.write(f"**이메일:** {safe_get('purchasing_email', 'N/A')}")
    
    with col2:
        st.write(f"**연락처:** {safe_get('purchasing_phone', 'N/A')}")
        st.write(f"**모바일:** {safe_get('purchasing_mobile', 'N/A')}")
        
    # 구매 직원 메모
    purchasing_notes = safe_get('purchasing_notes')
    if purchasing_notes and purchasing_notes != 'N/A':
        st.write(f"**구매 직원 메모:**")
        st.info(purchasing_notes)
    
    st.markdown("---")
    
    # KAM 정보
    st.markdown("#### 🎯 KAM 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**KAM 이름:** {safe_get('kam_name', 'N/A')}")
        
        # KAM 부서 변환
        kam_dept_db = safe_get('kam_department')
        kam_dept_ui = DEPARTMENT_REVERSE.get(kam_dept_db, kam_dept_db or 'N/A')
        st.write(f"**KAM 부서:** {kam_dept_ui}")
        
        st.write(f"**KAM 직책:** {safe_get('kam_position', 'N/A')}")
        st.write(f"**KAM 이메일:** {safe_get('kam_email', 'N/A')}")
    
    with col2:
        st.write(f"**KAM 연락처:** {safe_get('kam_phone', 'N/A')}")
        
    # KAM 메모
    kam_notes = safe_get('kam_notes')
    if kam_notes and kam_notes != 'N/A':
        st.write(f"**KAM 메모:**")
        st.info(kam_notes)
    
    st.markdown("---")
    
    # ⭐ KAM II 정보
    st.markdown("#### 🎯 KAM II 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**KAM II 이름:** {safe_get('kam2_name', 'N/A')}")
        
        # KAM II 부서 변환
        kam2_dept_db = safe_get('kam2_department')
        kam2_dept_ui = DEPARTMENT_REVERSE.get(kam2_dept_db, kam2_dept_db or 'N/A')
        st.write(f"**KAM II 부서:** {kam2_dept_ui}")
        
        st.write(f"**KAM II 직책:** {safe_get('kam2_position', 'N/A')}")
        st.write(f"**KAM II 이메일:** {safe_get('kam2_email', 'N/A')}")
    
    with col2:
        st.write(f"**KAM II 연락처:** {safe_get('kam2_phone', 'N/A')}")
        
    # KAM II 메모
    kam2_notes = safe_get('kam2_notes')
    if kam2_notes and kam2_notes != 'N/A':
        st.write(f"**KAM II 메모:**")
        st.info(kam2_notes)
    
    st.markdown("---")
    
    # 거래 정보
    st.markdown("#### 💼 거래 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**결제 조건:** {safe_get('payment_terms', 'N/A')}")
    
    with col2:
        created_at = safe_get('created_at')
        if created_at and created_at != 'N/A':
            try:
                created_date = datetime.fromisoformat(created_at).strftime('%Y-%m-%d')
                st.write(f"**등록일:** {created_date}")
            except:
                st.write(f"**등록일:** {created_at}")
    
    # 메모
    notes = safe_get('notes')
    if notes and notes != 'N/A':
        st.markdown("---")
        st.markdown("#### 📝 메모")
        st.info(notes)
    
    st.markdown("---")
    
    # 액션 버튼
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("✏️ 수정 / Chỉnh sửa", use_container_width=True, type="primary"):
            st.session_state[f"edit_customer_{customer_id}"] = True
            st.rerun()
    
    with action_col2:
        # 삭제 확인
        if st.button("🗑️ 삭제 / Xóa", use_container_width=True, type="secondary"):
            st.session_state[f"confirm_delete_{customer_id}"] = True
            st.rerun()
    
    # 삭제 확인 다이얼로그
    if st.session_state.get(f"confirm_delete_{customer_id}", False):
        st.warning("⚠️ 정말 삭제하시겠습니까? / Bạn có chắc muốn xóa?")
        
        confirm_col1, confirm_col2, confirm_col3 = st.columns(3)
        
        with confirm_col1:
            if st.button("✅ 확인 / Xác nhận", key=f"confirm_yes_{customer_id}"):
                # 삭제 안전성 확인
                is_safe, message = check_customer_deletion_safety(customer_id, load_func)
                
                if is_safe:
                    result = delete_func(customer_table, customer_id)
                    
                    if result:
                        st.success("✅ 고객이 삭제되었습니다 / Đã xóa khách hàng")
                        if 'show_customer_detail' in st.session_state:
                            del st.session_state['show_customer_detail']
                        if f"confirm_delete_{customer_id}" in st.session_state:
                            del st.session_state[f"confirm_delete_{customer_id}"]
                        st.rerun()
                    else:
                        st.error("❌ 삭제 실패 / Xóa thất bại")
                else:
                    st.error(f"❌ 삭제 불가: {message}")
        
        with confirm_col2:
            if st.button("❌ 취소 / Hủy", key=f"confirm_no_{customer_id}"):
                del st.session_state[f"confirm_delete_{customer_id}"]
                st.rerun()

def render_customer_statistics(load_func, customer_table):
    """고객 통계 탭 (활성 고객만)"""
    st.header("고객 통계 / Thống kê khách hàng")
    
    try:
        customers_data = load_func(customer_table)
        
        if not customers_data:
            st.info("통계를 표시할 고객 데이터가 없습니다. / Không có dữ liệu để hiển thị thống kê.")
            return
        
        # DataFrame 변환
        if isinstance(customers_data, list):
            customers_df = pd.DataFrame(customers_data)
        else:
            customers_df = customers_data
        
        if customers_df.empty:
            st.info("통계를 표시할 고객 데이터가 없습니다. / Không có dữ liệu để hiển thị thống kê.")
            return
        
        # ⭐ 활성 고객만 필터링
        active_customers_df = customers_df[customers_df['status'] == 'active'].copy()
        
        if active_customers_df.empty:
            st.warning("⚠️ 활성 상태인 고객이 없습니다. 고객 상태를 '활성'으로 설정해주세요.")
            st.info(f"전체 고객: {len(customers_df)}개 (활성: 0개)")
            return
        
        # 전체 통계
        st.subheader("📊 전체 통계 / Tổng quan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("활성 고객 수 / KH hoạt động", len(active_customers_df))
        
        with col2:
            inactive_count = len(customers_df[customers_df['status'] == 'inactive'])
            st.metric("비활성 고객 / KH không hoạt động", inactive_count)
        
        with col3:
            potential_count = len(customers_df[customers_df['status'] == 'potential'])
            st.metric("잠재 고객 / KH tiềm năng", potential_count)
        
        st.caption(f"💡 통계는 **활성 고객 {len(active_customers_df)}개사**만 대상으로 합니다.")
        
        st.markdown("---")
        
        # 업종별 통계 (활성 고객만)
        st.subheader("🏭 업종별 통계 (활성) / Thống kê theo ngành nghề")
        
        if 'business_type' in active_customers_df.columns:
            business_counts = active_customers_df['business_type'].value_counts()
            
            if not business_counts.empty:
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    st.write("**업종별 고객 수 / Số KH theo ngành:**")
                    for business_type, count in business_counts.items():
                        percentage = (count / len(active_customers_df) * 100)
                        # DB 값을 UI 값으로 변환
                        business_type_ui = BUSINESS_TYPE_REVERSE.get(business_type, business_type)
                        st.write(f"• {business_type_ui}: **{count}개** ({percentage:.1f}%)")
                
                with col2:
                    st.bar_chart(business_counts)
            else:
                st.info("업종 데이터가 없습니다. / Không có dữ liệu ngành nghề.")
        else:
            st.info("업종 데이터가 없습니다. / Không có dữ liệu ngành nghề.")
        
        st.markdown("---")
        
        # 국가별 통계 (활성 고객만)
        st.subheader("🌍 국가별 통계 (활성) / Thống kê theo quốc gia")
        
        if 'country' in active_customers_df.columns:
            country_counts = active_customers_df['country'].value_counts()
            
            if not country_counts.empty:
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    st.write("**국가별 고객 수 / Số KH theo quốc gia:**")
                    for country, count in country_counts.items():
                        percentage = (count / len(active_customers_df) * 100)
                        st.write(f"• {country}: **{count}개** ({percentage:.1f}%)")
                
                with col2:
                    st.bar_chart(country_counts)
            else:
                st.info("국가 데이터가 없습니다. / Không có dữ liệu quốc gia.")
        else:
            st.info("국가 데이터가 없습니다. / Không có dữ liệu quốc gia.")
        
        st.markdown("---")
        
        # 도시별 통계 (활성 고객만)
        st.subheader("🏙️ 도시별 통계 (활성) / Thống kê theo thành phố")
        
        if 'city' in active_customers_df.columns:
            city_df = active_customers_df[active_customers_df['city'].notna()]
            
            if not city_df.empty:
                city_counts = city_df['city'].value_counts()
                
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    st.write("**도시별 고객 수 / Số KH theo thành phố:**")
                    for city, count in city_counts.head(10).items():
                        percentage = (count / len(city_df) * 100)
                        st.write(f"• {city}: **{count}개** ({percentage:.1f}%)")
                    
                    if len(city_counts) > 10:
                        st.caption(f"...외 {len(city_counts) - 10}개 도시 / ...và {len(city_counts) - 10} thành phố khác")
                
                with col2:
                    st.bar_chart(city_counts.head(10))
            else:
                st.info("도시 데이터가 없습니다. / Không có dữ liệu thành phố.")
        else:
            st.info("도시 데이터가 없습니다. / Không có dữ liệu thành phố.")
        
        st.markdown("---")
        
        # KAM 할당 통계 (활성 고객만)
        st.subheader("👥 KAM 할당 통계 (활성) / Thống kê phân công KAM")
        
        if 'kam_name' in active_customers_df.columns:
            kam_assigned = len(active_customers_df[active_customers_df['kam_name'].notna()])
            kam_unassigned = len(active_customers_df[active_customers_df['kam_name'].isna()])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("KAM 할당됨 / Đã gán KAM", kam_assigned)
            
            with col2:
                st.metric("KAM 미할당 / Chưa gán KAM", kam_unassigned)
            
            with col3:
                assignment_rate = (kam_assigned / len(active_customers_df) * 100) if len(active_customers_df) > 0 else 0
                st.metric("할당률 / Tỷ lệ phân công", f"{assignment_rate:.1f}%")
            
            # KAM별 담당 고객 수
            if kam_assigned > 0:
                st.write("")
                st.write("**KAM별 담당 고객 수 / Số KH theo KAM:**")
                
                kam_customers = active_customers_df[active_customers_df['kam_name'].notna()]
                kam_counts = kam_customers['kam_name'].value_counts()
                
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    for kam_name, count in kam_counts.items():
                        st.write(f"• {kam_name}: **{count}개 고객 / {count} KH**")
                
                with col2:
                    st.bar_chart(kam_counts)
        else:
            st.info("KAM 데이터가 없습니다. / Không có dữ liệu KAM.")
        
    except Exception as e:
        logging.error(f"통계 로드 오류: {str(e)}")
        st.error(f"통계 로딩 중 오류가 발생했습니다 / Lỗi tải thống kê: {str(e)}")

def render_csv_management(load_func, save_func, customer_table):
    """CSV 다운로드/업로드 관리"""
    st.header("CSV 파일 관리 / Quản lý file CSV")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CSV 다운로드 / Tải CSV")
        
        if st.button("고객 목록 CSV 다운로드 / Tải danh sách KH", type="primary"):
            try:
                customers_data = load_func(customer_table)
                
                if not customers_data:
                    st.warning("다운로드할 고객 데이터가 없습니다. / Không có dữ liệu để tải.")
                    return
                
                # DataFrame 변환
                if isinstance(customers_data, list):
                    customers_df = pd.DataFrame(customers_data)
                else:
                    customers_df = customers_data
                
                if customers_df.empty:
                    st.warning("다운로드할 고객 데이터가 없습니다. / Không có dữ liệu để tải.")
                    return
                
                # CSV 생성
                csv_data = generate_customer_csv(customers_df)
                
                # 다운로드 버튼
                st.download_button(
                    label="CSV 파일 다운로드 / Tải file CSV",
                    data=csv_data,
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_customers_csv"
                )
                
                st.success(f"총 {len(customers_df)}개의 고객 데이터를 내보낼 준비가 완료되었습니다. / Sẵn sàng xuất {len(customers_df)} KH.")
                
            except Exception as e:
                st.error(f"CSV 생성 중 오류 / Lỗi tạo CSV: {str(e)}")
    
    with col2:
        st.subheader("CSV 업로드 / Tải lên CSV")
        
        uploaded_file = st.file_uploader(
            "고객 데이터 CSV 파일 선택 / Chọn file CSV",
            type=['csv'],
            help="CSV 파일을 업로드하여 고객 데이터를 일괄 등록할 수 있습니다. / Tải lên file CSV để đăng ký hàng loạt."
        )
        
        if uploaded_file is not None:
            try:
                # CSV 파일 읽기 (여러 인코딩 시도)
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                except:
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, encoding='cp949')
                    except:
                        try:
                            uploaded_file.seek(0)
                            df = pd.read_csv(uploaded_file, encoding='euc-kr')
                        except:
                            uploaded_file.seek(0)
                            df = pd.read_csv(uploaded_file, encoding='latin1')
                
                st.write("업로드된 파일 미리보기 / Xem trước:")
                st.dataframe(df.head(10))
                
                st.write(f"총 {len(df)}개의 행이 발견되었습니다. / Tìm thấy {len(df)} hàng.")
                
                # 필수 컬럼 확인 (회사명만)
                required_columns = ['company_name_original']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"필수 컬럼이 누락되었습니다 / Thiếu cột bắt buộc: {', '.join(missing_columns)}")
                    st.info("필수 컬럼 / Cột bắt buộc: company_name_original")
                else:
                    # 업로드 옵션
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        update_existing = st.checkbox(
                            "기존 고객 업데이트 / Cập nhật KH hiện tại",
                            help="이메일이 같은 고객이 있으면 정보를 업데이트합니다. / Cập nhật nếu email trùng."
                        )
                    
                    with col2:
                        skip_errors = st.checkbox(
                            "오류 행 건너뛰기 / Bỏ qua lỗi",
                            value=True,
                            help="오류가 있는 행은 건너뛰고 나머지만 처리합니다. / Bỏ qua hàng lỗi."
                        )
                    
                    if st.button("CSV 데이터 업로드 / Tải lên dữ liệu", type="primary"):
                        upload_results = process_csv_upload(
                            df, save_func, load_func, update_existing, skip_errors, customer_table
                        )
                        
                        # 결과 표시
                        if upload_results['success_count'] > 0:
                            st.success(f"✅ 성공 / Thành công: {upload_results['success_count']}개")
                        
                        if upload_results['error_count'] > 0:
                            st.warning(f"⚠️ 실패 / Thất bại: {upload_results['error_count']}개")
                            
                            with st.expander("오류 세부사항 / Chi tiết lỗi", expanded=False):
                                for error in upload_results['errors']:
                                    st.write(f"- {error}")
                        
                        if upload_results['updated_count'] > 0:
                            st.info(f"🔄 업데이트 / Cập nhật: {upload_results['updated_count']}개")
                        
                        st.rerun()
                        
            except Exception as e:
                st.error(f"파일 처리 중 오류 / Lỗi xử lý file: {str(e)}")
    
    # CSV 템플릿 다운로드
    st.markdown("---")
    st.subheader("CSV 템플릿 / Mẫu CSV")
    
    if st.button("CSV 템플릿 다운로드 / Tải mẫu CSV"):
        template_data = create_csv_template()
        
        st.download_button(
            label="템플릿 CSV 다운로드 / Tải mẫu",
            data=template_data,
            file_name="customer_template.csv",
            mime="text/csv",
            key="download_template"
        )

def generate_customer_csv(customers_df):
    """고객 데이터를 CSV로 변환"""
    if customers_df.empty:
        return None
    
    # 안전한 값 처리 함수
    def safe_str(value):
        if pd.isna(value) or value is None:
            return ''
        return str(value).strip()
    
    # CSV 출력용 컬럼 선택 및 순서 지정
    export_columns = [
        'company_name_original', 'company_name_short', 'company_name_english',
        'business_number', 'business_type', 'country', 'city',
        'address', 'contact_person', 'contact_department', 'position',
        'email', 'phone', 'mobile',
        'tax_id', 'payment_terms', 
        'kam_name', 'kam_department', 'kam_position', 'kam_phone',
        'kam_notes', 'status', 'notes', 'created_at'
    ]
    
    # 존재하는 컬럼만 선택
    available_columns = [col for col in export_columns if col in customers_df.columns]
    export_df = customers_df[available_columns].copy()
    
    # 모든 값을 안전하게 변환
    for col in export_df.columns:
        export_df[col] = export_df[col].apply(safe_str)
    
    # 컬럼명 한글/베트남어로 변경
    column_mapping = {
        'company_name_original': '회사명(공식) / Tên công ty (chính thức)',
        'company_name_short': '회사명(짧은) / Tên công ty (ngắn)',
        'company_name_english': '회사명(영어) / Tên công ty (tiếng Anh)',
        'business_number': '사업자번호 / Mã số doanh nghiệp',
        'business_type': '업종 / Ngành nghề',
        'country': '국가 / Quốc gia',
        'city': '도시 / Thành phố',
        'address': '주소 / Địa chỉ',
        'contact_person': '담당자명 / Tên người liên hệ',
        'contact_department': '담당자부서 / Bộ phận người liên hệ',
        'position': '직책 / Chức vụ',
        'email': '이메일 / Email',
        'phone': '전화번호 / Số điện thoại',
        'mobile': '휴대폰 / Di động',
        'tax_id': '세금ID / Mã số thuế',
        'payment_terms': '결제조건 / Điều kiện thanh toán',
        'kam_name': 'KAM이름 / Tên KAM',
        'kam_department': 'KAM부서 / Bộ phận KAM',
        'kam_position': 'KAM직책 / Chức vụ KAM',
        'kam_phone': 'KAM연락처 / Số điện thoại KAM',
        'kam_notes': 'KAM메모 / Ghi chú KAM',
        'status': '상태 / Trạng thái',
        'notes': '비고 / Ghi chú',
        'created_at': '등록일 / Ngày đăng ký'
    }
    
    export_df = export_df.rename(columns=column_mapping)
    
    # CSV 문자열로 변환 (UTF-8 with BOM for Excel)
    csv_string = export_df.to_csv(index=False, encoding='utf-8-sig')
    return csv_string

def process_csv_upload(df, save_func, load_func, update_existing, skip_errors, customer_table):
    """CSV 데이터 업로드 처리"""
    
    results = {
        'success_count': 0,
        'error_count': 0,
        'updated_count': 0,
        'errors': []
    }
    
    # 기존 고객 데이터 로드 (업데이트 모드인 경우)
    existing_customers = {}
    if update_existing:
        try:
            existing_data = load_func(customer_table)
            if existing_data:
                for customer in existing_data:
                    email = customer.get('email', '').strip().lower()
                    if email:
                        existing_customers[email] = customer
        except Exception as e:
            results['errors'].append(f"기존 고객 데이터 로드 오류: {str(e)}")
    
    # 각 행 처리
    for idx, row in df.iterrows():
        try:
            # 필수 필드 확인 (회사명만)
            company_name = row.get('company_name_original')
            
            if pd.isna(company_name) or str(company_name).strip() == '':
                if skip_errors:
                    results['error_count'] += 1
                    results['errors'].append(f"행 {idx + 2}: 필수 필드 누락 (company_name_original)")
                    continue
                else:
                    raise ValueError(f"행 {idx + 2}: 필수 필드 누락 (company_name_original)")
            
            # 고객 데이터 구성
            customer_data = {
                'company_name_original': str(company_name).strip(),
                'company_name_short': str(row.get('company_name_short', '')).strip() if pd.notna(row.get('company_name_short')) else None,
                'company_name_english': str(row.get('company_name_english', '')).strip() if pd.notna(row.get('company_name_english')) else None,
                'business_number': str(row.get('business_number', '')).strip() if pd.notna(row.get('business_number')) else None,
                'business_type': str(row.get('business_type', '')).strip() if pd.notna(row.get('business_type')) else None,
                'country': str(row.get('country', 'Vietnam')).strip(),
                'city': str(row.get('city', '')).strip() if pd.notna(row.get('city')) else None,
                'address': str(row.get('address', '')).strip() if pd.notna(row.get('address')) else None,
                'contact_person': str(row.get('contact_person', '')).strip() if pd.notna(row.get('contact_person')) else None,
                'contact_department': str(row.get('contact_department', '')).strip() if pd.notna(row.get('contact_department')) else None,
                'position': str(row.get('position', '')).strip() if pd.notna(row.get('position')) else None,
                'email': str(row.get('email', '')).strip() if pd.notna(row.get('email')) else None,
                'phone': str(row.get('phone', '')).strip() if pd.notna(row.get('phone')) else None,
                'mobile': str(row.get('mobile', '')).strip() if pd.notna(row.get('mobile')) else None,
                'tax_id': str(row.get('tax_id', '')).strip() if pd.notna(row.get('tax_id')) else None,
                'payment_terms': str(row.get('payment_terms', '')).strip() if pd.notna(row.get('payment_terms')) else None,
                'kam_name': str(row.get('kam_name', '')).strip() if pd.notna(row.get('kam_name')) else None,
                'kam_department': str(row.get('kam_department', '')).strip() if pd.notna(row.get('kam_department')) else None,
                'kam_position': str(row.get('kam_position', '')).strip() if pd.notna(row.get('kam_position')) else None,
                'kam_phone': str(row.get('kam_phone', '')).strip() if pd.notna(row.get('kam_phone')) else None,
                'kam_notes': str(row.get('kam_notes', '')).strip() if pd.notna(row.get('kam_notes')) else None,
                'status': str(row.get('status', 'active')).strip(),
                'notes': str(row.get('notes', '')).strip() if pd.notna(row.get('notes')) else None,
            }
            
            # 이메일 기준 중복 체크 (이메일이 있는 경우만)
            email = customer_data.get('email')
            email_key = email.lower() if email else None
            existing_customer = existing_customers.get(email_key) if email_key else None
            
            if existing_customer and update_existing:
                # 기존 고객 업데이트
                customer_data['id'] = existing_customer['id']
                customer_data['updated_at'] = datetime.now().isoformat()
                
                # update_func 파라미터 사용 (법인별 테이블)
                result = update_func(customer_table, customer_data)
                
                if result:
                    results['updated_count'] += 1
                else:
                    results['error_count'] += 1
                    results['errors'].append(f"행 {idx + 2}: 업데이트 실패 ({email})")
                    
            elif existing_customer and not update_existing:
                # 중복 이메일이지만 업데이트 모드가 아님
                if skip_errors:
                    results['error_count'] += 1
                    results['errors'].append(f"행 {idx + 2}: 중복 이메일 ({email})")
                    continue
                else:
                    raise ValueError(f"행 {idx + 2}: 중복 이메일 ({email})")
                    
            else:
                # 신규 고객 등록 (법인별 테이블)
                customer_data['created_at'] = datetime.now().isoformat()
                result = save_func(customer_table, customer_data)
                
                if result:
                    results['success_count'] += 1
                else:
                    results['error_count'] += 1
                    results['errors'].append(f"행 {idx + 2}: 저장 실패")
                    
        except Exception as e:
            if skip_errors:
                results['error_count'] += 1
                results['errors'].append(f"행 {idx + 2}: {str(e)}")
                continue
            else:
                raise
    
    return results

def create_csv_template():
    """CSV 템플릿 생성"""
    template_data = {
        'company_name_original': ['Samsung Electronics Co., Ltd.', 'LG Display Co., Ltd.'],
        'company_name_short': ['삼성', 'LG디스플레이'],
        'company_name_english': ['Samsung Electronics', 'LG Display'],
        'business_number': ['123-45-67890', '098-76-54321'],
        'business_type': ['금형 / Khuôn mẫu', '사출 / Ép phun'],
        'country': ['Korea', 'Vietnam'],
        'city': ['Seoul', 'Hanoi'],
        'address': ['Seoul Gangnam', 'Hanoi Dong Da'],
        'contact_person': ['John Kim', 'Jane Lee'],
        'position': ['Manager', 'Director'],
        'email': ['john@sample.com', 'jane@sample.com'],
        'phone': ['02-1234-5678', '010-9876-5432'],
        'mobile': ['010-1234-5678', '010-8765-4321'],
        'tax_id': ['TAX123', 'TAX456'],
        'payment_terms': ['30일 / 30 ngày', '현금 / Tiền mặt'],
        'kam_name': ['KAM Kim', 'KAM Lee'],
        'kam_phone': ['010-1111-2222', '010-3333-4444'],
        'kam_position': ['Team Lead', 'Manager'],
        'kam_notes': ['Important client', 'New client'],
        'status': ['Active', 'Active'],
        'notes': ['Note 1', 'Note 2']
    }
    
    template_df = pd.DataFrame(template_data)
    return template_df.to_csv(index=False, encoding='utf-8-sig')


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
        
        return True, "삭제 가능"
        
    except Exception as e:
        logging.error(f"삭제 안전성 확인 오류: {str(e)}")
        return False, f"삭제 안전성 확인 중 오류: {str(e)}"