"""
코드 관리 컴포넌트
7단계 제품 코드 체계 관리 시스템
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import time
from .code_management_ui import CodeManagementUI

class CodeManagementComponent:
    def __init__(self, supabase):
        self.supabase = supabase
        self.ui = CodeManagementUI(self)
    
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
            st.error("데이터베이스 연결이 없습니다.")
            return False
        
        if not item_id:
            st.error("삭제할 항목의 ID가 없습니다.")
            return False
        
        try:
            response = self.supabase.table(table).delete().eq(id_field, item_id).execute()
            
            if response.data:
                return True
            else:
                st.warning("삭제할 데이터를 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            st.error(f"데이터 삭제 실패 ({table}): {e}")
            return False
    
    def get_current_user(self):
        """현재 로그인한 사용자 정보 반환"""
        if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
            users = self.load_data_from_supabase('employees', '*', {'id': st.session_state.user_id})
            return users[0] if users else None
        
        if hasattr(st.session_state, 'logged_in') and st.session_state.logged_in:
            return {
                'id': 1,
                'name': 'Master',
                'department': 'Admin',
                'role': 'manager'
            }
        
        return None
    
    def _generate_preview_code(self, code01, code02, code03, code04, code05, code06, code07):
        """실시간 코드 미리보기 생성"""
        codes = [code01, code02, code03, code04, code05, code06, code07]
        valid_codes = [code.strip() for code in codes if code and code.strip()]
        return "-".join(valid_codes) if valid_codes else ""
    
    def _save_product_code(self, category, code01, code02, code03, code04, code05, code06, code07, description):
        """제품 코드 저장"""
        user = self.get_current_user()
        if not user:
            st.error("사용자 정보를 확인할 수 없습니다.")
            return False
        
        existing_codes = self.load_data_from_supabase('product_codes')
        if any(code.get('category') == category for code in existing_codes):
            st.error(f"카테고리 '{category}'가 이미 존재합니다.")
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
            st.success("제품 코드가 등록되었습니다!")
            return True
        else:
            st.error("제품 코드 등록에 실패했습니다.")
            return False
    
    def _update_product_code(self, code_id, category, code01, code02, code03, code04, code05, code06, code07, description):
        """제품 코드 수정"""
        existing_codes = self.load_data_from_supabase('product_codes')
        if any(code.get('category') == category and code.get('id') != code_id for code in existing_codes):
            st.error(f"카테고리 '{category}'가 이미 존재합니다.")
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
            st.success("제품 코드가 수정되었습니다!")
            return True
        else:
            st.error("제품 코드 수정에 실패했습니다.")
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
            st.success(f"코드가 {status_text}되었습니다!")
            return True
        else:
            st.error("상태 변경에 실패했습니다.")
            return False
    
    def _download_codes_csv(self):
        """코드 데이터 CSV 다운로드"""
        codes = self.load_data_from_supabase('product_codes')
        if codes:
            csv_data = []
            for code in codes:
                csv_data.append({
                    'category': code.get('category', ''),
                    'code01': code.get('code01', ''),
                    'code02': code.get('code02', ''),
                    'code03': code.get('code03', ''),
                    'code04': code.get('code04', ''),
                    'code05': code.get('code05', ''),
                    'code06': code.get('code06', ''),
                    'code07': code.get('code07', ''),
                    'full_code': code.get('full_code', ''),
                    'description': code.get('description', ''),
                    'is_active': 'TRUE' if code.get('is_active') else 'FALSE',
                    'created_at': code.get('created_at', '')[:10]
                })
            
            df = pd.DataFrame(csv_data)
            csv = df.to_csv(index=False, encoding='utf-8')
            
            st.download_button(
                label="📥 CSV 파일 다운로드",
                data=csv,
                file_name=f"product_codes_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key=self.generate_unique_key("download_csv")
            )
    
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
                    st.error("카테고리명, 설명, 그리고 최소 1개 이상의 코드를 입력해주세요.")
    
    def _upload_codes_csv(self):
        """CSV 파일 업로드"""
        st.subheader("📤 CSV 파일 업로드")
        
        st.markdown("### 🏷️ 카테고리 선택")
        existing_codes = self.load_data_from_supabase('product_codes')
        
        if existing_codes:
            categories = list(set([code.get('category') for code in existing_codes]))
            categories.sort()
            
            selected_category = st.selectbox(
                "업로드할 카테고리 선택",
                ["카테고리를 선택하세요..."] + categories,
                help="제품 코드를 추가할 카테고리를 선택하세요"
            )
            
            if selected_category == "카테고리를 선택하세요...":
                st.warning("먼저 카테고리를 선택해주세요.")
                st.info("새 카테고리가 필요하면 '코드 등록' 탭에서 카테고리와 첫 번째 제품 코드를 함께 등록하세요.")
                return
        else:
            st.warning("등록된 카테고리가 없습니다.")
            st.info("먼저 '코드 등록' 탭에서 카테고리와 첫 번째 제품 코드를 등록하세요.")
            return
        
        with st.expander("📋 CSV 파일 형식 가이드"):
            st.write("**필수 컬럼 (카테고리 제외):**")
            st.code("code01,code02,code03,code04,code05,code06,code07,description,is_active")
            
            st.write("**예시 데이터:**")
            st.code("""code01,code02,code03,code04,code05,code06,code07,description,is_active
HR,ST,OP,16,MAE,xx,00,Hot Runner Standard 16MAE,TRUE
HR,ST,OP,16,MCC,xx,00,Hot Runner Standard 16MCC,TRUE""")
            
            st.write("**주의사항:**")
            st.write("- category 컬럼은 포함하지 마세요")
            st.write("- is_active는 TRUE/FALSE로 입력")
            st.write("- 최소 1개 이상의 code 필드가 필요합니다")
        
        uploaded_file = st.file_uploader("CSV 파일 선택", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, dtype=str)
                df = df.fillna('')
                
                st.subheader("📊 업로드된 데이터 미리보기")
                st.dataframe(df.head(10))
                st.write(f"이 {len(df)}개의 레코드가 발견되었습니다.")
                st.info(f"선택된 카테고리: **{selected_category}**")
                
                validation_errors = self._validate_csv_data_no_category(df)
                duplicate_errors = self._check_duplicate_codes(df, selected_category)
                all_errors = validation_errors + duplicate_errors

                if all_errors:
                    st.error("데이터 검증 실패:")
                    for error in all_errors:
                        st.write(f"- {error}")
                else:
                    st.success("데이터 검증 및 중복 확인 통과")
                    
                    existing_category_codes = [code for code in existing_codes if code.get('category') == selected_category]
                    
                    if existing_category_codes:
                        st.warning(f"'{selected_category}' 카테고리에 이미 {len(existing_category_codes)}개의 제품 코드가 있습니다.")
                        
                        action = st.radio(
                            "처리 방법 선택",
                            ["기존 코드와 함께 추가", "기존 코드 삭제 후 새 데이터로 교체"],
                            key=self.generate_unique_key("category_action")
                        )
                        
                        if action == "기존 코드 삭제 후 새 데이터로 교체":
                            st.info(f"기존 {len(existing_category_codes)}개 코드를 삭제하고 {len(df)}개의 새 코드를 등록합니다.")
                            
                            if st.button("🔄 기존 삭제 후 새 데이터 등록", type="primary"):
                                deleted = self._delete_category_codes(selected_category)
                                if deleted:
                                    if self._bulk_save_codes_with_category(df, selected_category):
                                        st.success(f"'{selected_category}' 카테고리가 새 데이터로 교체되었습니다!")
                                        st.rerun()
                        else:
                            st.info(f"기존 {len(existing_category_codes)}개 코드에 {len(df)}개의 새 코드를 추가합니다.")
                            
                            if st.button("➕ 기존 코드와 함께 추가", type="primary"):
                                if self._bulk_save_codes_with_category(df, selected_category):
                                    st.success(f"'{selected_category}' 카테고리에 {len(df)}개의 제품 코드가 추가되었습니다!")
                                    st.rerun()
                    else:
                        st.success(f"'{selected_category}' 카테고리에 첫 번째 제품 코드들을 등록합니다.")
                        
                        if st.button("💾 모든 데이터 등록", type="primary"):
                            if self._bulk_save_codes_with_category(df, selected_category):
                                st.success(f"'{selected_category}' 카테고리에 {len(df)}개의 제품 코드가 등록되었습니다!")
                                st.rerun()
                            
            except Exception as e:
                st.error(f"CSV 파일 처리 중 오류: {str(e)}")
    
    def _validate_csv_data_no_category(self, df):
        """CSV 데이터 검증"""
        errors = []
        
        required_columns = ['description']
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"필수 컬럼 '{col}'이 없습니다.")
        
        if 'category' in df.columns:
            errors.append("CSV에 category 컬럼이 포함되어 있습니다. 이 컬럼은 제거하고 위에서 카테고리를 선택하세요.")
        
        if errors:
            return errors
        
        for idx, row in df.iterrows():
            row_num = idx + 2
            
            if pd.isna(row.get('description')) or str(row.get('description')).strip() == '':
                errors.append(f"행 {row_num}: 설명이 비어있습니다.")
            
            is_active = str(row.get('is_active', 'TRUE')).upper()
            if is_active not in ['TRUE', 'FALSE', '']:
                errors.append(f"행 {row_num}: is_active는 TRUE 또는 FALSE여야 합니다.")
            
            has_code = False
            for i in range(1, 8):
                code_col = f'code{i:02d}'
                if code_col in df.columns and not pd.isna(row.get(code_col)) and str(row.get(code_col)).strip():
                    has_code = True
                    break
            
            if not has_code:
                errors.append(f"행 {row_num}: 최소 1개 이상의 코드가 필요합니다.")
        
        return errors
    
    def _bulk_save_codes_with_category(self, df, category):
        """대량 코드 저장"""
        user = self.get_current_user()
        if not user:
            st.error("사용자 정보를 확인할 수 없습니다.")
            return False
        
        success_count = 0
        total_count = len(df)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, row in df.iterrows():
            try:
                new_code = {
                    'category': category,
                    'code01': str(row.get('code01', '')).strip() or None,
                    'code02': str(row.get('code02', '')).strip() or None,
                    'code03': str(row.get('code03', '')).strip() or None,
                    'code04': str(row.get('code04', '')).strip() or None,
                    'code05': str(row.get('code05', '')).strip() or None,
                    'code06': str(row.get('code06', '')).strip() or None,
                    'code07': str(row.get('code07', '')).strip() or None,
                    'description': str(row.get('description', '')).strip(),
                    'is_active': str(row.get('is_active', 'TRUE')).upper() == 'TRUE',
                    'created_by': user['id'],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                for key, value in new_code.items():
                    if value == '':
                        new_code[key] = None
                
                if self.save_data_to_supabase('product_codes', new_code):
                    success_count += 1
                
                progress = (idx + 1) / total_count
                progress_bar.progress(progress)
                status_text.text(f"처리 중... {idx + 1}/{total_count} ({success_count}개 성공)")
                
            except Exception as e:
                st.warning(f"행 {idx + 2} 처리 중 오류: {str(e)}")
        
        progress_bar.empty()
        status_text.empty()
        
        if success_count == total_count:
            return True
        elif success_count > 0:
            st.warning(f"부분 성공: {success_count}/{total_count}개 항목이 등록되었습니다.")
            return True
        else:
            st.error("모든 항목 등록에 실패했습니다.")
            return False
    
    def _delete_category_codes(self, category):
        """특정 카테고리 코드 삭제"""
        try:
            response = self.supabase.table('product_codes').delete().eq('category', category).execute()
            if response.data:
                st.info(f"기존 '{category}' 카테고리 {len(response.data)}개 코드가 삭제되었습니다.")
                return True
            else:
                st.warning(f"'{category}' 카테고리에서 삭제할 데이터를 찾을 수 없습니다.")
                return True
        except Exception as e:
            st.error(f"카테고리 삭제 실패: {e}")
            return False
    
    def _check_duplicate_codes(self, df, category):
        """코드 중복 확인"""
        duplicate_errors = []
        
        csv_codes = []
        for idx, row in df.iterrows():
            code_parts = []
            for i in range(1, 8):
                code_col = f'code{i:02d}'
                code_value = str(row.get(code_col, '')).strip()
                if code_value:
                    code_parts.append(code_value)
            
            if code_parts:
                full_code = "-".join(code_parts)
                csv_codes.append({
                    'row': idx + 2,
                    'full_code': full_code
                })
        
        seen_codes = {}
        for code_info in csv_codes:
            full_code = code_info['full_code']
            if full_code in seen_codes:
                duplicate_errors.append(
                    f"CSV 내부 중복: 행 {seen_codes[full_code]}와 행 {code_info['row']}에서 동일한 코드 '{full_code}'"
                )
            else:
                seen_codes[full_code] = code_info['row']
        
        existing_codes = self.load_data_from_supabase('product_codes')
        existing_full_codes = {}
        
        for existing_code in existing_codes:
            existing_parts = []
            for i in range(1, 8):
                code_value = existing_code.get(f'code{i:02d}')
                if code_value:
                    existing_parts.append(str(code_value).strip())
            
            if existing_parts:
                existing_full_code = "-".join(existing_parts)
                existing_full_codes[existing_full_code] = {
                    'category': existing_code.get('category'),
                    'id': existing_code.get('id')
                }
        
        for code_info in csv_codes:
            full_code = code_info['full_code']
            if full_code in existing_full_codes:
                existing_info = existing_full_codes[full_code]
                if existing_info['category'] == category:
                    duplicate_errors.append(
                        f"같은 카테고리 내 중복: 행 {code_info['row']}의 코드 '{full_code}'가 이미 존재함"
                    )
                else:
                    duplicate_errors.append(
                        f"다른 카테고리와 중복: 행 {code_info['row']}의 코드 '{full_code}'가 '{existing_info['category']}' 카테고리에 이미 존재함"
                    )
        
        return duplicate_errors
    
    def render_code_management_page(self):
        """코드 관리 메인 페이지"""
        st.markdown("### 🏷️ 제품 코드 관리")
        st.markdown("7단계 체계적 제품 코드 시스템을 관리합니다.")
        
        tab1, tab2, tab3 = st.tabs(["📝 코드 등록", "📋 코드 목록", "📤 CSV 업로드"])
        
        with tab1:
            self._render_code_registration()
        
        with tab2:
            self.ui.render_code_list_grouped()
        
        with tab3:
            self._upload_codes_csv()