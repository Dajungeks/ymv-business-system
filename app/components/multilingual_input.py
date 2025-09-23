"""
다국어 입력 컴포넌트
영어/베트남어 제품명 지원 시스템
"""

import streamlit as st
import uuid
import time

class MultilingualInputComponent:
    def __init__(self, supabase):
        self.supabase = supabase
    
    def generate_unique_key(self, prefix="ml"):
        """고유한 위젯 키 생성"""
        timestamp = str(int(time.time() * 1000))
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_id}"
    
    def render_multilingual_input(self, prefix="product", default_en="", default_vn="", required=True):
        """다국어 입력 폼 렌더링"""
        st.markdown("### 🌍 다국어 제품명")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name_en = st.text_input(
                "🇺🇸 제품명 (English)",
                value=default_en,
                placeholder="Product Name in English",
                key=self.generate_unique_key(f"{prefix}_name_en"),
                help="영어 제품명은 필수입니다."
            )
        
        with col2:
            name_vn = st.text_input(
                "🇻🇳 제품명 (Tiếng Việt)",
                value=default_vn,
                placeholder="Tên sản phẩm bằng tiếng Việt",
                key=self.generate_unique_key(f"{prefix}_name_vn"),
                help="베트남어 제품명 (선택사항)"
            )
        
        # 입력 검증
        if required and not name_en:
            st.error("❌ 영어 제품명은 필수입니다.")
            return None, None
        
        return name_en, name_vn
    
    def render_language_selector(self, key_prefix="lang"):
        """언어 선택기 렌더링"""
        language = st.selectbox(
            "🌍 표시 언어 선택",
            options=["en", "vn"],
            format_func=lambda x: {
                "en": "🇺🇸 English",
                "vn": "🇻🇳 Tiếng Việt"
            }[x],
            key=self.generate_unique_key(key_prefix)
        )
        return language
    
    def get_display_name(self, product, language="en"):
        """언어별 제품명 반환"""
        if language == "vn":
            return (
                product.get('product_name_vn') or 
                product.get('product_name_en') or 
                product.get('product_name') or 
                "이름 없음"
            )
        elif language == "en":
            return (
                product.get('product_name_en') or 
                product.get('product_name') or 
                "No Name"
            )
        else:
            return product.get('product_name') or "기본명"
    
    def render_product_selector_with_multilingual(self, products, language="en", key_prefix="product_sel"):
        """다국어 제품 선택기"""
        if not products:
            st.warning("선택할 수 있는 제품이 없습니다.")
            return None
        
        # 제품 옵션 생성
        product_options = []
        for product in products:
            display_name = self.get_display_name(product, language)
            product_code = product.get('product_code', 'N/A')
            unit_price = product.get('unit_price', 0)
            
            option_text = f"{product_code} - {display_name} (${unit_price:.2f})"
            product_options.append((option_text, product))
        
        # 선택기 렌더링
        selected_option = st.selectbox(
            f"🌍 제품 선택 ({language.upper()})",
            options=range(len(product_options)),
            format_func=lambda x: product_options[x][0],
            key=self.generate_unique_key(key_prefix)
        )
        
        if selected_option is not None:
            return product_options[selected_option][1]
        
        return None
    
    def render_multilingual_display_card(self, product, show_both_languages=True):
        """다국어 제품 정보 카드"""
        if not product:
            return
        
        product_code = product.get('product_code', 'N/A')
        name_en = product.get('product_name_en', '')
        name_vn = product.get('product_name_vn', '')
        category = product.get('category', 'N/A')
        unit_price = product.get('unit_price', 0)
        unit_price_vnd = product.get('unit_price_vnd', 0)
        stock = product.get('stock_quantity', 0)
        
        with st.container():
            st.markdown(f"### 📦 {product_code}")
            
            if show_both_languages:
                if name_en:
                    st.markdown(f"**🇺🇸 English:** {name_en}")
                if name_vn:
                    st.markdown(f"**🇻🇳 Tiếng Việt:** {name_vn}")
                else:
                    st.markdown("**🇻🇳 Tiếng Việt:** *(베트남어명 없음)*")
            else:
                display_name = name_en or product.get('product_name', 'N/A')
                st.markdown(f"**제품명:** {display_name}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**🏷️ 카테고리:** {category}")
            with col2:
                st.markdown(f"**💰 단가:** ${unit_price:.2f}")
                if unit_price_vnd > 0:
                    st.caption(f"₫{unit_price_vnd:,.0f}")
            with col3:
                st.markdown(f"**📊 재고:** {stock}")
    
    def validate_multilingual_input(self, name_en, name_vn):
        """다국어 입력 검증"""
        errors = []
        
        # 영어명 필수 체크
        if not name_en or not name_en.strip():
            errors.append("영어 제품명은 필수입니다.")
        
        # 길이 체크
        if name_en and len(name_en) > 200:
            errors.append("영어 제품명은 200자 이내로 입력해주세요.")
        
        if name_vn and len(name_vn) > 200:
            errors.append("베트남어 제품명은 200자 이내로 입력해주세요.")
        
        # 특수문자 체크 (기본적인 검증)
        if name_en and any(char in name_en for char in ['<', '>', '"', "'"]):
            errors.append("영어 제품명에 특수문자(<, >, \", ')를 사용할 수 없습니다.")
        
        if name_vn and any(char in name_vn for char in ['<', '>', '"', "'"]):
            errors.append("베트남어 제품명에 특수문자(<, >, \", ')를 사용할 수 없습니다.")
        
        return errors
    
    def format_multilingual_data(self, name_en, name_vn, base_name=None):
        """다국어 데이터 포맷팅"""
        # 기본명 설정 (영어명을 기본으로 사용)
        if not base_name:
            base_name = name_en
        
        return {
            'product_name': base_name,           # 기본명
            'product_name_en': name_en,         # 영어명
            'product_name_vn': name_vn or None  # 베트남어명 (없으면 None)
        }
    
    def get_search_terms(self, product):
        """검색용 텀 생성"""
        terms = []
        
        # 기본명
        if product.get('product_name'):
            terms.append(product['product_name'].lower())
        
        # 영어명
        if product.get('product_name_en'):
            terms.append(product['product_name_en'].lower())
        
        # 베트남어명
        if product.get('product_name_vn'):
            terms.append(product['product_name_vn'].lower())
        
        # 제품 코드
        if product.get('product_code'):
            terms.append(product['product_code'].lower())
        
        return ' '.join(terms)
    
    def render_multilingual_search(self, products, key_prefix="search"):
        """다국어 검색 기능"""
        search_term = st.text_input(
            "🔍 제품 검색 (다국어 지원)",
            placeholder="제품 코드, 영어명, 베트남어명으로 검색",
            key=self.generate_unique_key(key_prefix)
        )
        
        if not search_term:
            return products
        
        # 검색 실행
        filtered_products = []
        search_lower = search_term.lower()
        
        for product in products:
            search_text = self.get_search_terms(product)
            if search_lower in search_text:
                filtered_products.append(product)
        
        return filtered_products
    
    def render_language_priority_info(self):
        """언어 우선순위 정보 표시"""
        with st.expander("🌍 다국어 표시 규칙"):
            st.markdown("""
            **언어별 우선순위:**
            
            **영어 선택 시:**
            1. 영어명 (product_name_en)
            2. 기본명 (product_name)
            
            **베트남어 선택 시:**
            1. 베트남어명 (product_name_vn)
            2. 영어명 (product_name_en)
            3. 기본명 (product_name)
            
            **검색 시:**
            - 모든 언어의 제품명에서 검색
            - 제품 코드도 검색 대상에 포함
            """)
    
    def get_multilingual_display_options(self):
        """다국어 표시 옵션 반환"""
        return {
            "en": {
                "name": "🇺🇸 English",
                "placeholder": "Product Name in English",
                "help": "영어 제품명 (필수)"
            },
            "vn": {
                "name": "🇻🇳 Tiếng Việt", 
                "placeholder": "Tên sản phẩm bằng tiếng Việt",
                "help": "베트남어 제품명 (선택사항)"
            }
        }