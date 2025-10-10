"""
제품 코드 관리 UI 컴포넌트
지출 요청서와 동일한 스타일의 카테고리 그룹핑 UI
"""

import streamlit as st
import pandas as pd
from datetime import datetime

class CodeManagementUI:
    def __init__(self, parent_component):
        """
        parent_component: CodeManagementComponent 인스턴스
        """
        self.parent = parent_component
    
    def render_code_list_grouped(self):
        """카테고리별 그룹핑된 제품 코드 목록"""
        st.subheader("📋 등록된 제품 코드 목록")
        
        # 데이터 로드
        all_codes = self.parent.load_data_from_supabase('product_codes')
        
        if not all_codes:
            st.info("등록된 제품 코드가 없습니다.")
            return
        
        # 상단 필터 및 통계
        self._render_filters_and_stats(all_codes)
        
        # 필터링된 데이터 가져오기
        filtered_codes = self._apply_filters(all_codes)
        
        if not filtered_codes:
            st.warning("검색 결과가 없습니다.")
            return
        
        # 카테고리별 그룹핑
        categories = self._group_by_category(filtered_codes)
        
        # 카테고리별 렌더링
        for category, codes in categories.items():
            self._render_category_card(category, codes)
    
    def _render_filters_and_stats(self, all_codes):
        """필터 및 통계 정보"""
        # 통계 계산
        total_count = len(all_codes)
        active_count = len([c for c in all_codes if c.get('is_active')])
        inactive_count = total_count - active_count
        category_count = len(set([c.get('category') for c in all_codes]))
        
        # 통계 표시
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("전체 코드", f"{total_count}개")
        with col2:
            st.metric("활성 코드", f"{active_count}개", delta=None)
        with col3:
            st.metric("비활성 코드", f"{inactive_count}개")
        with col4:
            st.metric("카테고리", f"{category_count}개")
        
        st.markdown("---")
        
        # 필터 컨트롤
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            search_term = st.text_input(
                "🔍 검색",
                placeholder="카테고리, 코드, 설명으로 검색",
                key="code_search_grouped"
            )
            if search_term:
                st.session_state['code_search_term'] = search_term
            elif 'code_search_term' in st.session_state:
                del st.session_state['code_search_term']
        
        with col2:
            categories = sorted(set([c.get('category') for c in all_codes]))
            selected_category = st.selectbox(
                "카테고리",
                ["전체"] + categories,
                key="code_category_filter"
            )
            st.session_state['selected_category'] = selected_category
        
        with col3:
            status_filter = st.selectbox(
                "상태",
                ["전체", "활성만", "비활성만"],
                key="code_status_filter"
            )
            st.session_state['status_filter'] = status_filter
        
        with col4:
            sort_order = st.selectbox(
                "정렬",
                ["카테고리순", "최신순"],
                key="code_sort_order"
            )
            st.session_state['sort_order'] = sort_order
    
    def _apply_filters(self, all_codes):
        """필터 적용"""
        filtered = all_codes.copy()
        
        # 검색어 필터
        if 'code_search_term' in st.session_state and st.session_state['code_search_term']:
            search_term = st.session_state['code_search_term'].lower()
            filtered = [
                code for code in filtered
                if (search_term in code.get('category', '').lower() or
                    search_term in code.get('full_code', '').lower() or
                    search_term in code.get('description', '').lower())
            ]
        
        # 카테고리 필터
        if st.session_state.get('selected_category', '전체') != '전체':
            filtered = [
                code for code in filtered
                if code.get('category') == st.session_state['selected_category']
            ]
        
        # 상태 필터
        status_filter = st.session_state.get('status_filter', '전체')
        if status_filter == "활성만":
            filtered = [code for code in filtered if code.get('is_active')]
        elif status_filter == "비활성만":
            filtered = [code for code in filtered if not code.get('is_active')]
        
        # 정렬
        sort_order = st.session_state.get('sort_order', '카테고리순')
        if sort_order == "최신순":
            filtered = sorted(filtered, key=lambda x: x.get('created_at', ''), reverse=True)
        else:
            filtered = sorted(filtered, key=lambda x: (x.get('category', ''), x.get('full_code', '')))
        
        return filtered
    
    def _group_by_category(self, codes):
        """카테고리별 그룹핑"""
        categories = {}
        for code in codes:
            category = code.get('category', 'Unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(code)
        
        # 카테고리명으로 정렬
        return dict(sorted(categories.items()))
    
    def _render_category_card(self, category, codes):
        """카테고리 카드 렌더링"""
        # 카테고리 정보
        active_count = len([c for c in codes if c.get('is_active')])
        total_count = len(codes)
        category_desc = codes[0].get('description', '') if codes else ''
        
        # 카드 헤더
        status_icon = "✅" if active_count > 0 else "⚠️"
        
        with st.expander(
            f"📦 **{category}** - {category_desc[:30]}{'...' if len(category_desc) > 30 else ''} "
            f"({active_count}/{total_count}개 활성) {status_icon}",
            expanded=False
        ):
            # 테이블 헤더
            header_cols = st.columns([3, 4, 1, 1.5, 2])
            with header_cols[0]:
                st.markdown("**전체 코드**")
            with header_cols[1]:
                st.markdown("**설명**")
            with header_cols[2]:
                st.markdown("**상태**")
            with header_cols[3]:
                st.markdown("**등록일**")
            with header_cols[4]:
                st.markdown("**액션**")
            
            st.markdown("---")
            
            # 코드 목록
            for code in codes:
                self._render_code_row(code)
    
    def _render_code_row(self, code):
        """개별 코드 행 렌더링"""
        cols = st.columns([3, 4, 1, 1.5, 2])
        
        # 전체 코드
        with cols[0]:
            full_code = code.get('full_code', 'N/A')
            st.markdown(f"<span style='font-size:16px;'><code>{full_code}</code></span>", unsafe_allow_html=True)
        
        # 설명
        with cols[1]:
            description = code.get('description', 'N/A')
            display_desc = description[:50] + ('...' if len(description) > 50 else '')
            st.markdown(f"<span style='font-size:15px;'>{display_desc}</span>", unsafe_allow_html=True)
        
        # 상태
        with cols[2]:
            if code.get('is_active'):
                st.markdown("<span style='font-size:15px;'>🟢 활성</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='font-size:15px;'>🔴 비활성</span>", unsafe_allow_html=True)
        
        # 등록일
        with cols[3]:
            created_at = code.get('created_at', 'N/A')
            if created_at != 'N/A':
                date_str = created_at[:10]
                st.markdown(f"<span style='font-size:14px;'>{date_str}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='font-size:14px;'>N/A</span>", unsafe_allow_html=True)
        
        # 액션 버튼
        with cols[4]:
            btn_cols = st.columns(3)
            
            # 상세보기 버튼
            with btn_cols[0]:
                if st.button("📄", key=f"view_{code.get('id')}", help="상세보기"):
                    st.session_state[f"viewing_code_{code.get('id')}"] = True
                    st.rerun()
            
            # 수정 버튼
            with btn_cols[1]:
                if st.button("✏️", key=f"edit_{code.get('id')}", help="수정"):
                    st.session_state[f"editing_code_{code.get('id')}"] = True
                    st.rerun()
            
            # 삭제 버튼
            with btn_cols[2]:
                if st.button("🗑️", key=f"delete_{code.get('id')}", help="삭제"):
                    if self.parent.delete_data_from_supabase('product_codes', code.get('id')):
                        st.success("삭제되었습니다!")
                        st.rerun()
        
        # 상세보기 모달
        if st.session_state.get(f"viewing_code_{code.get('id')}", False):
            self._render_code_detail_modal(code)
        
        # 수정 모달
        if st.session_state.get(f"editing_code_{code.get('id')}", False):
            self._render_code_edit_modal(code)
        
        # 간격 축소 (기존 --- 대신 얇은 선)
        st.markdown("<div style='margin: 8px 0; border-bottom: 1px solid #e0e0e0;'></div>", unsafe_allow_html=True)
    
    def _render_code_detail_modal(self, code):
        """코드 상세보기 모달"""
        st.markdown("#### 📋 제품 코드 상세 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**카테고리:** {code.get('category', 'N/A')}")
            st.write(f"**전체 코드:** `{code.get('full_code', 'N/A')}`")
            st.write(f"**설명:** {code.get('description', 'N/A')}")
            st.write(f"**상태:** {'🟢 활성' if code.get('is_active') else '🔴 비활성'}")
        
        with col2:
            st.write(f"**등록일:** {code.get('created_at', 'N/A')[:10]}")
            st.write(f"**수정일:** {code.get('updated_at', 'N/A')[:10]}")
            
            # 코드 구성 상세
            st.write("**코드 구성:**")
            for i in range(1, 8):
                code_value = code.get(f'code{i:02d}')
                if code_value:
                    st.write(f"- CODE{i:02d}: {code_value}")
        
        if st.button("닫기", key=f"close_view_{code.get('id')}"):
            del st.session_state[f"viewing_code_{code.get('id')}"]
            st.rerun()
    
    def _render_code_edit_modal(self, code):
        """코드 수정 모달"""
        st.markdown("#### ✏️ 제품 코드 수정")
        
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
            
            # 미리보기
            edit_preview = self.parent._generate_preview_code(
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
                        if self.parent._update_product_code(
                            code.get('id'), edit_category, edit_code01, edit_code02,
                            edit_code03, edit_code04, edit_code05, edit_code06, edit_code07,
                            edit_description
                        ):
                            del st.session_state[f"editing_code_{code.get('id')}"]
                            st.rerun()
                    else:
                        st.error("카테고리명과 설명을 입력해주세요.")
            
            with col2:
                if st.form_submit_button("❌ 취소", use_container_width=True):
                    del st.session_state[f"editing_code_{code.get('id')}"]
                    st.rerun()