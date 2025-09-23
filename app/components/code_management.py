"""
코드 관리 컴포넌트
7단계 제품 코드 체계 관리 시스템
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import time

class CodeManagementComponent:
    def __init__(self, supabase):
        self.supabase = supabase
    
    def generate_unique_key(self, prefix="code"):
        """고유한 위젯 키 생성"""
        timestamp = str(int(time.time() * 1000))
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_id}"
    
    def load_data_from_supabase(self, table, columns="*", filters=None):
        """Supabase에서 데이터 로드"""
        if not self.supabase:
            return []
        
        try:
            query = self.supabase.table(table).select(columns)
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"데이터 로드 실패 ({table}): {e}")
            return []
    
    def save_data_to_supabase(self, table, data):
        """Supabase에 데이터 저장"""
        if not self.supabase:
            return False
        
        try:
            response = self.supabase.table(table).insert(data).execute()
            return True
        except Exception as e:
            st.error(f"데이터 저장 실패 ({table}): {e}")
            return False
    
    def update_data_in_supabase(self, table, data, id_field="id"):
        """Supabase에서 데이터 업데이트"""
        if not self.supabase:
            return False
        
        try:
            item_id = data.pop(id_field)
            response = self.supabase.table(table).update(data).eq(id_field, item_id).execute()
            return True
        except Exception as e:
            st.error(f"데이터 업데이트 실패 ({table}): {e}")
            return False
    
    def delete_data_from_supabase(self, table, item_id, id_field="id"):
        """Supabase에서 데이터 삭제"""
        if not self.supabase:
            return False
        
        try:
            response = self.supabase.table(table).delete().eq(id_field, item_id).execute()
            return True
        except Exception as e:
            st.error(f"데이터 삭제 실패 ({table}): {e}")
            return False
    
    def get_current_user(self):
        """현재 로그인한 사용자 정보 반환"""
        if 'user_id' in st.session_state:
            users = self.load_data_from_supabase('employees', '*', {'id': st.session_state.user_id})
            return users[0] if users else None
        return None
    
    def _generate_preview_code(self, code01, code02, code03, code04, code05, code06, code07):
        """실시간 코드 미리보기 생성"""
        codes = [code01, code02, code03, code04, code05, code06, code07]
        # 빈 값 제거하고 하이픈으로 연결
        valid_codes = [code.strip() for code in codes if code and code.strip()]
        return "-".join(valid_codes) if valid_codes else ""
    
    def _save_product_code(self, category, code01, code02, code03, code04, code05, code06, code07, description):
        """제품 코드 저장"""
        user = self.get_current_user()
        if not user:
            st.error("❌ 사용자 정보를 확인할 수 없습니다.")
            return False
        
        # 카테고리 중복 확인
        existing_codes = self.load_data_from_supabase('product_codes')
        if any(code.get('category') == category for code in existing_codes):
            st.error(f"❌ 카테고리 '{category}'가 이미 존재합니다.")
            return False
        
        new_code = {
            'category': category,
            'code01': code01 or None,
            'code02': code02 or None,
            'code03': code03 or None,
            'code04': code04 or None,
            'code05': code05 or None,
            'code06': code06 or None,
            'code07': code07 or None,
            'description': description,
            'is_active': True,
            'created_by': user['id'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        if self.save_data_to_supabase('product_codes', new_code):
            st.success("✅ 제품 코드가 등록되었습니다!")
            return True
        else:
            st.error("❌ 제품 코드 등록에 실패했습니다.")
            return False
    
    def _update_product_code(self, code_id, category, code01, code02, code03, code04, code05, code06, code07, description):
        """제품 코드 수정"""
        # 카테고리 중복 확인 (자기 자신 제외)
        existing_codes = self.load_data_from_supabase('product_codes')
        if any(code.get('category') == category and code.get('id') != code_id for code in existing_codes):
            st.error(f"❌ 카테고리 '{category}'가 이미 존재합니다.")
            return False
        
        update_data = {
            'id': code_id,
            'category': category,
            'code01': code01 or None,
            'code02': code02 or None,
            'code03': code03 or None,
            'code04': code04 or None,
            'code05': code05 or None,
            'code06': code06 or None,
            'code07': code07 or None,
            'description': description,
            'updated_at': datetime.now().isoformat()
        }
        
        if self.update_data_in_supabase('product_codes', update_data):
            st.success("✅ 제품 코드가 수정되었습니다!")
            return True
        else:
            st.error("❌ 제품 코드 수정에 실패했습니다.")
            return False
    
    def _toggle_code_status(self, code_id, current_status):
        """코드 상태 변경"""
        new_status = not current_status
        update_data = {
            'id': code_id,
            'is_active': new_status,
            'updated_at': datetime.now().isoformat()
        }
        
        if self.update_data_in_supabase('product_codes', update_data):
            status_text = "활성화" if new_status else "비활성화"
            st.success(f"✅ 코드가 {status_text}되었습니다!")
            return True
        else:
            st.error("❌ 상태 변경에 실패했습니다.")
            return False
    
    def _download_codes_csv(self):
        """코드 데이터 CSV 다운로드"""
        codes = self.load_data_from_supabase('product_codes')
        if codes:
            # CSV용 데이터 가공
            csv_data = []
            for code in codes:
                csv_data.append({
                    '카테고리': code.get('category', ''),
                    'CODE01': code.get('code01', ''),
                    'CODE02': code.get('code02', ''),
                    'CODE03': code.get('code03', ''),
                    'CODE04': code.get('code04', ''),
                    'CODE05': code.get('code05', ''),
                    'CODE06': code.get('code06', ''),
                    'CODE07': code.get('code07', ''),
                    '전체코드': code.get('full_code', ''),
                    '설명': code.get('description', ''),
                    '상태': '활성' if code.get('is_active') else '비활성',
                    '등록일': code.get('created_at', '')[:10]
                })
            
            df = pd.DataFrame(csv_data)
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="📁 CSV 파일 다운로드",
                data=csv,
                file_name=f"product_codes_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key=self.generate_unique_key("download_csv")
            )
        else:
            st.info("다운로드할 데이터가 없습니다.")
    
    def get_active_categories(self):
        """활성 카테고리 목록 반환"""
        codes = self.load_data_from_supabase('product_codes', '*', {'is_active': True})
        categories = []
        for code in codes:
            categories.append({
                'value': code['category'],
                'display': f"{code['category']} - {code['description']}",
                'full_code': code.get('full_code', ''),
                'description': code['description']
            })
        return categories
    
    def _render_code_registration(self):
        """코드 등록 탭 렌더링"""
        st.subheader("📝 새 제품 코드 등록")
        
        with st.form("code_registration_form"):
            st.markdown("### 📋 기본 정보")
            
            category = st.text_input(
                "카테고리명",
                placeholder="예: A, B, HR, MP...",
                help="고유한 카테고리명을 입력하세요"
            )
            
            st.markdown("### 🏷️ 코드 구성 (7단계)")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                code01 = st.text_input("CODE01", placeholder="HR", max_chars=10)
                code02 = st.text_input("CODE02", placeholder="01", max_chars=10)
            with col2:
                code03 = st.text_input("CODE03", placeholder="02", max_chars=10)
                code04 = st.text_input("CODE04", placeholder="ST", max_chars=10)
            with col3:
                code05 = st.text_input("CODE05", placeholder="KR", max_chars=10)
                code06 = st.text_input("CODE06", placeholder="00", max_chars=10)
            with col4:
                code07 = st.text_input("CODE07", placeholder="", max_chars=10)
            
            # 실시간 미리보기
            preview_code = self._generate_preview_code(code01, code02, code03, code04, code05, code06, code07)
            if preview_code:
                st.markdown(f"### ✅ 미리보기: `{preview_code}`")
            else:
                st.markdown("### ⏳ 미리보기: (코드를 입력하세요)")
            
            description = st.text_area(
                "카테고리 설명",
                placeholder="예: 핫런너 시스템 표준형",
                help="이 카테고리에 대한 설명을 입력하세요"
            )
            
            if st.form_submit_button("💾 코드 등록", use_container_width=True):
                if category and description and (code01 or code02 or code03):
                    if self._save_product_code(category, code01, code02, code03, code04, code05, code06, code07, description):
                        st.rerun()
                else:
                    st.error("❌ 카테고리명, 설명, 그리고 최소 1개 이상의 코드를 입력해주세요.")
    
    def _render_code_list(self):
        """코드 목록 탭 렌더링"""
        st.subheader("📋 등록된 제품 코드 목록")
        
        # 상단 컨트롤
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            search_term = st.text_input(
                "🔍 검색", 
                placeholder="카테고리명 또는 설명으로 검색",
                key=self.generate_unique_key("search")
            )
        
        with col2:
            filter_status = st.selectbox(
                "상태", 
                ["전체", "활성만", "비활성만"],
                key=self.generate_unique_key("filter_status")
            )
        
        with col3:
            sort_order = st.selectbox(
                "정렬", 
                ["최신순", "카테고리순"],
                key=self.generate_unique_key("sort_order")
            )
        
        with col4:
            self._download_codes_csv()
        
        # 데이터 로드 및 필터링
        codes = self.load_data_from_supabase('product_codes')
        
        # 검색 필터링
        if search_term:
            codes = [
                code for code in codes 
                if (search_term.lower() in code.get('category', '').lower() or 
                    search_term.lower() in code.get('description', '').lower())
            ]
        
        # 상태 필터링
        if filter_status == "활성만":
            codes = [code for code in codes if code.get('is_active')]
        elif filter_status == "비활성만":
            codes = [code for code in codes if not code.get('is_active')]
        
        # 정렬
        if sort_order == "최신순":
            codes = sorted(codes, key=lambda x: x.get('created_at', ''), reverse=True)
        else:
            codes = sorted(codes, key=lambda x: x.get('category', ''))
        
        # 코드 목록 표시
        if codes:
            for code in codes:
                status_icon = "✅" if code.get('is_active') else "❌"
                status_text = "활성" if code.get('is_active') else "비활성"
                
                with st.expander(f"🏷️ {code.get('category')} - {code.get('full_code', 'N/A')} {status_icon}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**전체 코드:** `{code.get('full_code', 'N/A')}`")
                        st.write(f"**설명:** {code.get('description', 'N/A')}")
                        st.write(f"**상태:** {status_text}")
                        st.write(f"**등록일:** {code.get('created_at', 'N/A')[:10]}")
                        
                        # 코드 상세 정보
                        codes_detail = []
                        for i in range(1, 8):
                            code_value = code.get(f'code{i:02d}')
                            if code_value:
                                codes_detail.append(f"CODE{i:02d}: {code_value}")
                        
                        if codes_detail:
                            st.write(f"**코드 구성:** {' | '.join(codes_detail)}")
                    
                    with col2:
                        # 수정 버튼
                        edit_key = f"edit_{code.get('id')}_{int(time.time())}"
                        if st.button("📝 수정", key=edit_key):
                            st.session_state[f"editing_code_{code.get('id')}"] = True
                            st.rerun()
                        
                        # 상태 변경 버튼
                        status_key = f"status_{code.get('id')}_{int(time.time())}"
                        status_button_text = "🔄 비활성화" if code.get('is_active') else "🔄 활성화"
                        if st.button(status_button_text, key=status_key):
                            if self._toggle_code_status(code.get('id'), code.get('is_active')):
                                st.rerun()
                        
                        # 삭제 버튼
                        delete_key = f"delete_{code.get('id')}_{int(time.time())}"
                        if st.button("❌ 삭제", key=delete_key):
                            if self.delete_data_from_supabase('product_codes', code.get('id')):
                                st.success("✅ 삭제되었습니다!")
                                st.rerun()
                    
                    # 수정 폼 (조건부 표시)
                    if st.session_state.get(f"editing_code_{code.get('id')}", False):
                        st.markdown("---")
                        st.markdown("### ✏️ 코드 수정")
                        
                        with st.form(f"edit_form_{code.get('id')}"):
                            edit_category = st.text_input("카테고리명", value=code.get('category', ''))
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                edit_code01 = st.text_input("CODE01", value=code.get('code01', '') or '')
                                edit_code02 = st.text_input("CODE02", value=code.get('code02', '') or '')
                            with col2:
                                edit_code03 = st.text_input("CODE03", value=code.get('code03', '') or '')
                                edit_code04 = st.text_input("CODE04", value=code.get('code04', '') or '')
                            with col3:
                                edit_code05 = st.text_input("CODE05", value=code.get('code05', '') or '')
                                edit_code06 = st.text_input("CODE06", value=code.get('code06', '') or '')
                            with col4:
                                edit_code07 = st.text_input("CODE07", value=code.get('code07', '') or '')
                            
                            # 수정 미리보기
                            edit_preview = self._generate_preview_code(
                                edit_code01, edit_code02, edit_code03, edit_code04, 
                                edit_code05, edit_code06, edit_code07
                            )
                            if edit_preview:
                                st.markdown(f"**📋 미리보기:** `{edit_preview}`")
                            
                            edit_description = st.text_area("설명", value=code.get('description', ''))
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 저장", use_container_width=True):
                                    if edit_category and edit_description:
                                        if self._update_product_code(
                                            code.get('id'), edit_category, edit_code01, edit_code02, 
                                            edit_code03, edit_code04, edit_code05, edit_code06, edit_code07, 
                                            edit_description
                                        ):
                                            st.session_state[f"editing_code_{code.get('id')}"] = False
                                            st.rerun()
                                    else:
                                        st.error("❌ 카테고리명과 설명을 입력해주세요.")
                            
                            with col2:
                                if st.form_submit_button("❌ 취소", use_container_width=True):
                                    st.session_state[f"editing_code_{code.get('id')}"] = False
                                    st.rerun()
        else:
            st.info("등록된 제품 코드가 없습니다.")
    
    def render_code_management_page(self):
        """코드 관리 메인 페이지"""
        st.markdown("### 🏷️ 제품 코드 관리")
        st.markdown("7단계 체계적 제품 코드 시스템을 관리합니다.")
        
        # 탭 구성
        tab1, tab2 = st.tabs(["📝 코드 등록", "📋 코드 목록"])
        
        with tab1:
            self._render_code_registration()
        
        with tab2:
            self._render_code_list()