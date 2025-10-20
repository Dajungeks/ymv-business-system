"""
제품 코드 관리 시스템 V4
- 7단계 코드 체계 관리
- 대량 등록/수정
- 가격 관리 제거 (제품 관리로 이동)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io

def show_product_code_management(load_func, save_func, update_func, delete_func):
    """제품 코드 관리 메인"""
    st.title("🏷️ 제품 코드 관리")
    
    # 탭 구성 (가격 관리 제거)
    tab1, tab2, tab3 = st.tabs([
        "📝 코드 등록",
        "📋 코드 목록", 
        "📤 대량 등록/수정"
    ])
    
    with tab1:
        render_code_registration(save_func, load_func)
    
    with tab2:
        render_code_list_table_view(load_func, update_func, delete_func)
    
    with tab3:
        render_bulk_operations(load_func, save_func, update_func, delete_func)


# ==========================================
# 코드 등록
# ==========================================

def render_code_registration(save_func, load_func):
    """코드 등록 폼"""
    st.header("📝 새 제품 코드 등록")
    
    st.info("💡 7단계 코드를 생성합니다. 각 단계는 최대 10자까지 입력 가능합니다.")
    
    with st.form("code_registration_form"):
        st.subheader("📋 기본 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.text_input(
                "카테고리명 *",
                placeholder="예: HR, ROBOT, CONTROLLER",
                help="카테고리 코드를 입력하세요 (같은 카테고리에 여러 제품 등록 가능)",
                max_chars=50
            )
        
        with col2:
            description = st.text_input(
                "제품 설명 *",
                placeholder="예: 핫런너 시스템 MCC 타입",
                help="이 제품 코드에 대한 설명을 입력하세요"
            )
        
        st.subheader("🏷️ 코드 구성 (7단계)")
        st.caption("하이픈(-)으로 자동 연결됩니다. 빈 칸은 건너뜁니다.")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            code01 = st.text_input("CODE01", placeholder="HR", max_chars=10, key="reg_code01")
            code02 = st.text_input("CODE02", placeholder="HRS", max_chars=10, key="reg_code02")
        
        with col2:
            code03 = st.text_input("CODE03", placeholder="YMO", max_chars=10, key="reg_code03")
            code04 = st.text_input("CODE04", placeholder="ST", max_chars=10, key="reg_code04")
        
        with col3:
            code05 = st.text_input("CODE05", placeholder="20", max_chars=10, key="reg_code05")
            code06 = st.text_input("CODE06", placeholder="MCC", max_chars=10, key="reg_code06")
        
        with col4:
            code07 = st.text_input("CODE07", placeholder="xx", max_chars=10, key="reg_code07")
        
        preview_code = generate_full_code(code01, code02, code03, code04, code05, code06, code07)
        if preview_code:
            st.success(f"✅ 미리보기: **{preview_code}**")
        else:
            st.warning("⏳ 최소 1개 이상의 코드를 입력하세요")
        
        submitted = st.form_submit_button("💾 코드 등록", type="primary", use_container_width=True)
        
        if submitted:
            if not category.strip():
                st.error("❌ 카테고리명을 입력해주세요.")
                return
            
            if not description.strip():
                st.error("❌ 제품 설명을 입력해주세요.")
                return
            
            if not preview_code:
                st.error("❌ 최소 1개 이상의 코드를 입력해주세요.")
                return
            
            existing_codes = load_func('product_codes') or []
            
            if any(code.get('full_code') == preview_code for code in existing_codes):
                st.error(f"❌ 코드 '{preview_code}'가 이미 존재합니다.")
                st.info("💡 같은 카테고리라도 코드 조합이 달라야 합니다.")
                return
            
            code_data = {
                'category': category,
                'code01': code01.strip() if code01.strip() else None,
                'code02': code02.strip() if code02.strip() else None,
                'code03': code03.strip() if code03.strip() else None,
                'code04': code04.strip() if code04.strip() else None,
                'code05': code05.strip() if code05.strip() else None,
                'code06': code06.strip() if code06.strip() else None,
                'code07': code07.strip() if code07.strip() else None,
                'full_code': preview_code,
                'description': description.strip(),
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            if save_func('product_codes', code_data):
                st.success(f"✅ 제품 코드 '{preview_code}'가 등록되었습니다!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ 등록에 실패했습니다.")


# ==========================================
# 코드 목록 (테이블 뷰)
# ==========================================

def render_code_list_table_view(load_func, update_func, delete_func):
    """코드 목록 - 테이블 뷰"""
    st.header("📋 등록된 코드 목록")
    
    codes = load_func('product_codes') or []
    
    if not codes:
        st.info("등록된 제품 코드가 없습니다.")
        return
    
    if 'show_edit_form' not in st.session_state:
        st.session_state.show_edit_form = False
    if 'editing_code_id' not in st.session_state:
        st.session_state.editing_code_id = None
    
    render_search_filters(codes)
    render_edit_delete_controls(load_func, update_func, delete_func)
    
    if st.session_state.show_edit_form and st.session_state.get('editing_code_data'):
        render_edit_form_expandable(update_func)
    
    filtered_codes = get_filtered_codes(codes)
    render_code_table(filtered_codes)


def render_search_filters(codes):
    """검색 및 필터"""
    col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
    
    with col1:
        st.text_input("🔍 검색", placeholder="카테고리/코드/설명 검색", key="search_term")
    
    with col2:
        categories = sorted(list(set([code.get('category', '') for code in codes])))
        st.selectbox("카테고리", ["전체"] + categories, key="selected_category")
    
    with col3:
        st.selectbox("상태", ["전체", "활성", "비활성"], key="status_filter")
    
    with col4:
        st.write("")
        st.write("")
        if st.button("📥 CSV", use_container_width=True):
            csv_data = generate_codes_csv(codes)
            st.download_button(
                "다운로드",
                csv_data,
                f"codes_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )


def render_edit_delete_controls(load_func, update_func, delete_func):
    """수정/삭제 입력 컨트롤"""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
    
    with col1:
        code_id_input = st.text_input("수정/삭제할 코드 ID", placeholder="코드 ID를 입력하세요", key="code_id_input")
    
    with col2:
        if st.button("✏️ 수정", use_container_width=True, type="primary"):
            if code_id_input and code_id_input.strip().isdigit():
                code_id = int(code_id_input.strip())
                codes = load_func('product_codes') or []
                found_code = next((c for c in codes if c.get('id') == code_id), None)
                
                if found_code:
                    st.session_state.editing_code_id = code_id
                    st.session_state.show_edit_form = True
                    st.session_state.editing_code_data = found_code
                    st.rerun()
                else:
                    st.error(f"❌ ID {code_id}를 찾을 수 없습니다.")
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    with col3:
        if st.button("🗑️ 삭제", use_container_width=True):
            if code_id_input and code_id_input.strip().isdigit():
                st.session_state.deleting_code_id = int(code_id_input.strip())
                st.rerun()
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    if st.session_state.get('deleting_code_id'):
        st.warning(f"⚠️ ID {st.session_state.deleting_code_id} 코드를 정말 삭제하시겠습니까?")
        
        del_col1, del_col2, _ = st.columns([1, 1, 4])
        
        with del_col1:
            if st.button("✅ 예", key="confirm_delete", use_container_width=True):
                if delete_func('product_codes', st.session_state.deleting_code_id):
                    st.success("✅ 삭제되었습니다!")
                    st.session_state.pop('deleting_code_id', None)
                    st.rerun()
        
        with del_col2:
            if st.button("❌ 아니오", key="cancel_delete", use_container_width=True):
                st.session_state.pop('deleting_code_id', None)
                st.rerun()
    
    st.markdown("---")


def render_edit_form_expandable(update_func):
    """펼침/접힘 수정 폼"""
    code = st.session_state.editing_code_data
    code_id = code.get('id')
    
    with st.expander(f"▼ 코드 수정 (ID: {code_id})", expanded=True):
        with st.form(f"edit_form_{code_id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_category = st.text_input("카테고리", value=code.get('category', ''))
            
            with col2:
                new_description = st.text_input("설명", value=code.get('description', ''))
            
            st.markdown("**코드 세그먼트:**")
            code_cols = st.columns(7)
            
            new_codes = []
            for i in range(1, 8):
                with code_cols[i-1]:
                    new_code = st.text_input(
                        f"Code{i:02d}",
                        value=code.get(f'code{i:02d}', '') or '',
                        max_chars=10,
                        key=f"edit_code{i:02d}_{code_id}"
                    )
                    new_codes.append(new_code)
            
            new_full_code = generate_full_code(*new_codes)
            if new_full_code:
                st.info(f"🔄 새 코드: **{new_full_code}**")
            
            new_is_active = st.checkbox("활성 상태", value=code.get('is_active', True))
            
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                save_btn = st.form_submit_button("💾 저장", type="primary", use_container_width=True)
            
            with col_cancel:
                cancel_btn = st.form_submit_button("❌ 취소", use_container_width=True)
            
            if save_btn:
                if not new_full_code:
                    st.error("최소 1개 이상의 코드를 입력하세요.")
                    return
                
                update_data = {
                    'id': code_id,
                    'category': new_category.strip(),
                    'code01': new_codes[0].strip() or None,
                    'code02': new_codes[1].strip() or None,
                    'code03': new_codes[2].strip() or None,
                    'code04': new_codes[3].strip() or None,
                    'code05': new_codes[4].strip() or None,
                    'code06': new_codes[5].strip() or None,
                    'code07': new_codes[6].strip() or None,
                    'full_code': new_full_code,
                    'description': new_description.strip(),
                    'is_active': new_is_active,
                    'updated_at': datetime.now().isoformat()
                }
                
                if update_func('product_codes', update_data):
                    st.success("✅ 수정되었습니다!")
                    st.session_state.show_edit_form = False
                    st.session_state.editing_code_id = None
                    st.session_state.pop('editing_code_data', None)
                    st.rerun()
                else:
                    st.error("❌ 수정 실패")
            
            if cancel_btn:
                st.session_state.show_edit_form = False
                st.session_state.editing_code_id = None
                st.session_state.pop('editing_code_data', None)
                st.rerun()


def get_filtered_codes(codes):
    """필터 적용"""
    filtered = codes.copy()
    
    search_term = st.session_state.get('search_term', '')
    if search_term:
        filtered = [
            code for code in filtered
            if search_term.lower() in str(code.get('category', '')).lower()
            or search_term.lower() in str(code.get('full_code', '')).lower()
            or search_term.lower() in str(code.get('description', '')).lower()
        ]
    
    selected_category = st.session_state.get('selected_category', '전체')
    if selected_category != "전체":
        filtered = [code for code in filtered if code.get('category') == selected_category]
    
    status_filter = st.session_state.get('status_filter', '전체')
    if status_filter == "활성":
        filtered = [code for code in filtered if code.get('is_active')]
    elif status_filter == "비활성":
        filtered = [code for code in filtered if not code.get('is_active')]
    
    filtered = sorted(filtered, key=lambda x: (x.get('category', ''), x.get('full_code', '')))
    
    return filtered


def render_code_table(codes):
    """코드 테이블"""
    if not codes:
        st.info("조건에 맞는 코드가 없습니다.")
        return
    
    table_data = []
    
    for code in codes:
        table_data.append({
            'ID': code.get('id', ''),
            'Category': code.get('category', ''),
            'Code01': code.get('code01', ''),
            'Code02': code.get('code02', ''),
            'Code03': code.get('code03', ''),
            'Code04': code.get('code04', ''),
            'Code05': code.get('code05', ''),
            'Code06': code.get('code06', ''),
            'Code07': code.get('code07', ''),
            'Full Code': code.get('full_code', ''),
            'Description': code.get('description', ''),
            'Active': '✅' if code.get('is_active') else '❌'
        })
    
    df = pd.DataFrame(table_data)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"📊 총 **{len(codes)}개** 코드")


# ==========================================
# 대량 등록/수정
# ==========================================

def render_bulk_operations(load_func, save_func, update_func, delete_func):
    """대량 등록/수정"""
    st.header("📤 CSV 대량 등록/수정")
    
    bulk_tab1, bulk_tab2 = st.tabs(["📥 템플릿 다운로드", "📤 CSV 업로드"])
    
    with bulk_tab1:
        render_csv_template_download()
    
    with bulk_tab2:
        render_csv_upload(load_func, save_func, update_func, delete_func)


def render_csv_template_download():
    """CSV 템플릿 다운로드"""
    st.subheader("📥 CSV 템플릿 다운로드")
    
    st.info("💡 템플릿을 다운로드하여 Excel에서 편집 후 업로드하세요.")
    
    template_data = {
        'category': ['HR', 'HR', 'MP'],
        'code01': ['HR', 'HR', 'MP'],
        'code02': ['01', '02', 'AA'],
        'code03': ['02', '03', 'BB'],
        'code04': ['ST', 'ST', 'CC'],
        'code05': ['KR', 'VN', ''],
        'code06': ['00', '00', ''],
        'code07': ['', '', ''],
        'description': ['핫런너 표준형', '핫런너 고급형', '몰드 플레이트'],
        'is_active': ['TRUE', 'TRUE', 'TRUE']
    }
    
    template_df = pd.DataFrame(template_data)
    
    st.write("**템플릿 미리보기:**")
    st.dataframe(template_df, use_container_width=True)
    
    csv_buffer = io.StringIO()
    template_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    csv_data = csv_buffer.getvalue()
    
    st.download_button(
        "📥 템플릿 다운로드 (CSV)",
        csv_data,
        "product_codes_template.csv",
        "text/csv",
        type="primary",
        use_container_width=True
    )


def render_csv_upload(load_func, save_func, update_func, delete_func):
    """CSV 업로드"""
    st.subheader("📤 CSV 파일 업로드")
    
    uploaded_file = st.file_uploader("CSV 파일 선택", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, dtype=str)
            df = df.fillna('')
            
            st.write("**업로드된 데이터:**")
            st.dataframe(df, use_container_width=True)
            st.write(f"총 {len(df)}개 행")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 신규 등록", type="primary", use_container_width=True):
                    errors = validate_csv_data(df, load_func, mode='insert')
                    
                    if errors:
                        st.error("❌ 데이터 검증 실패:")
                        for error in errors:
                            st.write(f"- {error}")
                    else:
                        success_count = bulk_insert_codes(df, save_func)
                        if success_count > 0:
                            st.success(f"✅ {success_count}개 코드가 등록되었습니다!")
                            st.balloons()
                            st.rerun()
            
            with col2:
                if st.button("🔄 업데이트", use_container_width=True):
                    errors = validate_csv_data(df, load_func, mode='update')
                    
                    if errors:
                        st.error("❌ 데이터 검증 실패:")
                        for error in errors:
                            st.write(f"- {error}")
                    else:
                        result = bulk_upsert_codes(df, load_func, save_func, update_func)
                        st.success(f"✅ 신규: {result['inserted']}개, 수정: {result['updated']}개")
                        st.balloons()
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ CSV 처리 오류: {str(e)}")


# ==========================================
# 유틸리티 함수
# ==========================================

def generate_full_code(code01, code02, code03, code04, code05, code06, code07):
    """전체 코드 생성"""
    codes = [code01, code02, code03, code04, code05, code06, code07]
    valid_codes = [c.strip() for c in codes if c and c.strip()]
    return "-".join(valid_codes) if valid_codes else ""


def generate_codes_csv(codes):
    """코드 데이터를 CSV로 변환"""
    csv_data = []
    
    for code in codes:
        csv_data.append({
            'id': code.get('id', ''),
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
            'is_active': 'TRUE' if code.get('is_active') else 'FALSE'
        })
    
    df = pd.DataFrame(csv_data)
    return df.to_csv(index=False, encoding='utf-8-sig')


def validate_csv_data(df, load_func, mode='insert'):
    """CSV 데이터 검증"""
    errors = []
    
    required_columns = ['category', 'description']
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"필수 컬럼 '{col}'이 없습니다.")
    
    if errors:
        return errors
    
    existing_codes = load_func('product_codes') or []
    existing_full_codes = [code.get('full_code') for code in existing_codes]
    
    csv_full_codes = []
    
    for idx, row in df.iterrows():
        row_num = idx + 2
        
        category = str(row.get('category', '')).strip()
        description = str(row.get('description', '')).strip()
        
        if not category:
            errors.append(f"행 {row_num}: 카테고리가 비어있습니다.")
        
        if not description:
            errors.append(f"행 {row_num}: 설명이 비어있습니다.")
        
        has_code = False
        for i in range(1, 8):
            code_col = f'code{i:02d}'
            if code_col in df.columns:
                code_val = str(row.get(code_col, '')).strip()
                if code_val:
                    has_code = True
                    if len(code_val) > 10:
                        errors.append(f"행 {row_num}: {code_col}이 10자를 초과합니다.")
        
        if not has_code:
            errors.append(f"행 {row_num}: 최소 1개 이상의 코드가 필요합니다.")
        
        full_code = generate_full_code(
            str(row.get('code01', '')),
            str(row.get('code02', '')),
            str(row.get('code03', '')),
            str(row.get('code04', '')),
            str(row.get('code05', '')),
            str(row.get('code06', '')),
            str(row.get('code07', ''))
        )
        
        if full_code:
            if full_code in csv_full_codes:
                errors.append(f"행 {row_num}: 코드 '{full_code}'가 CSV 내에서 중복됩니다.")
            else:
                csv_full_codes.append(full_code)
            
            if mode == 'insert' and full_code in existing_full_codes:
                errors.append(f"행 {row_num}: 코드 '{full_code}'가 이미 DB에 존재합니다.")
    
    return errors


def bulk_insert_codes(df, save_func):
    """대량 코드 삽입"""
    success_count = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, row in df.iterrows():
        try:
            full_code = generate_full_code(
                str(row.get('code01', '')),
                str(row.get('code02', '')),
                str(row.get('code03', '')),
                str(row.get('code04', '')),
                str(row.get('code05', '')),
                str(row.get('code06', '')),
                str(row.get('code07', ''))
            )
            
            code_data = {
                'category': str(row.get('category', '')).strip(),
                'code01': str(row.get('code01', '')).strip() or None,
                'code02': str(row.get('code02', '')).strip() or None,
                'code03': str(row.get('code03', '')).strip() or None,
                'code04': str(row.get('code04', '')).strip() or None,
                'code05': str(row.get('code05', '')).strip() or None,
                'code06': str(row.get('code06', '')).strip() or None,
                'code07': str(row.get('code07', '')).strip() or None,
                'full_code': full_code,
                'description': str(row.get('description', '')).strip(),
                'is_active': str(row.get('is_active', 'TRUE')).upper() == 'TRUE',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            if save_func('product_codes', code_data):
                success_count += 1
            
            progress = (idx + 1) / len(df)
            progress_bar.progress(progress)
            status_text.text(f"처리 중... {idx + 1}/{len(df)}")
        
        except Exception as e:
            st.warning(f"행 {idx + 2} 처리 오류: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    
    return success_count


def bulk_upsert_codes(df, load_func, save_func, update_func):
    """대량 코드 Upsert"""
    inserted_count = 0
    updated_count = 0
    
    existing_codes = load_func('product_codes') or []
    existing_dict = {code.get('full_code'): code for code in existing_codes}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, row in df.iterrows():
        try:
            full_code = generate_full_code(
                str(row.get('code01', '')),
                str(row.get('code02', '')),
                str(row.get('code03', '')),
                str(row.get('code04', '')),
                str(row.get('code05', '')),
                str(row.get('code06', '')),
                str(row.get('code07', ''))
            )
            
            code_data = {
                'category': str(row.get('category', '')).strip(),
                'code01': str(row.get('code01', '')).strip() or None,
                'code02': str(row.get('code02', '')).strip() or None,
                'code03': str(row.get('code03', '')).strip() or None,
                'code04': str(row.get('code04', '')).strip() or None,
                'code05': str(row.get('code05', '')).strip() or None,
                'code06': str(row.get('code06', '')).strip() or None,
                'code07': str(row.get('code07', '')).strip() or None,
                'full_code': full_code,
                'description': str(row.get('description', '')).strip(),
                'is_active': str(row.get('is_active', 'TRUE')).upper() == 'TRUE',
                'updated_at': datetime.now().isoformat()
            }
            
            if full_code in existing_dict:
                existing_code = existing_dict[full_code]
                code_data['id'] = existing_code.get('id')
                
                if update_func('product_codes', code_data):
                    updated_count += 1
            else:
                code_data['created_at'] = datetime.now().isoformat()
                
                if save_func('product_codes', code_data):
                    inserted_count += 1
            
            progress = (idx + 1) / len(df)
            progress_bar.progress(progress)
            status_text.text(f"처리 중... {idx + 1}/{len(df)} (신규: {inserted_count}, 수정: {updated_count})")
        
        except Exception as e:
            st.warning(f"행 {idx + 2} 처리 오류: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    
    return {
        'inserted': inserted_count,
        'updated': updated_count
    }