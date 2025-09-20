"""
YMV 비즈니스 시스템 - 6단계 카테고리 관리 시스템 (개선된 편집 기능)
Level 1 카테고리명 표시, 즉시 삭제, 제품 등록 기능, 다중 필드 편집
"""

import streamlit as st
import pandas as pd
import sys
import os

# app 폴더를 Python 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.database import get_db
from shared.utils import show_success_message, show_error_message

def category_management_page():
    """카테고리 관리 메인 페이지"""
    st.markdown("# 6단계 카테고리 관리")
    
    tab1, tab2, tab3 = st.tabs(["코드 생성", "코드 목록", "통계"])
    
    with tab1:
        create_category_interface()
    
    with tab2:
        category_list_interface()
    
    with tab3:
        statistics_interface()

def create_category_interface():
    """카테고리 생성 인터페이스"""
    st.markdown("### 📝 카테고리 코드 생성")
    st.info("상위 레벨을 선택한 후 새로운 하위 코드를 생성하세요.")
    
    # 생성할 레벨 선택
    level_to_create = st.selectbox(
        "생성할 레벨 선택", 
        [1, 2, 3, 4, 5, 6],
        format_func=lambda x: f"Level {x}"
    )
    
    with st.form("create_category_form"):
        if level_to_create == 1:
            # Level 1: 대분류 생성
            create_level1_form()
        else:
            # Level 2~6: 하위 레벨 생성
            create_child_form(level_to_create)

def create_level1_form():
    """Level 1 생성 폼"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        main_category = st.selectbox("대분류", ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'])
    
    with col2:
        code_number = st.text_input("코드 번호", placeholder="HR, IT, MFG", max_chars=5)
    
    category_name = st.text_input("카테고리명", placeholder="예: Hot Runner")
    description = st.text_area("설명 (선택사항)")
    
    # 미리보기
    if code_number and category_name:
        preview_code = f"{main_category}-{code_number}"
        st.info(f"🔍 생성될 코드: **{preview_code}**")
    
    submitted = st.form_submit_button("🚀 Level 1 카테고리 생성", use_container_width=True)
    
    if submitted:
        create_level1_category(main_category, code_number, category_name, description)

def create_child_form(level):
    """하위 레벨 생성 폼"""
    parent_codes = get_available_parent_codes(level - 1)
    
    if not parent_codes:
        st.warning(f"Level {level-1} 코드가 없습니다. 먼저 상위 레벨을 생성해주세요.")
        st.form_submit_button("생성", disabled=True)
        return
    
    parent_code = st.selectbox(
        f"상위 Level {level-1} 코드 선택",
        parent_codes,
        format_func=lambda x: f"{x['category_code']} - {x['category_name']}"
    )
    
    code_number = st.text_input("코드 번호", placeholder="VV, 20, MAE", max_chars=5)
    category_name = st.text_input("카테고리명")
    description = st.text_area("설명 (선택사항)")
    
    # 미리보기
    if parent_code and code_number and category_name:
        preview_code = f"{parent_code['category_code']}-{code_number}"
        st.info(f"🔍 생성될 코드: **{preview_code}**")
    
    submitted = st.form_submit_button(f"🚀 Level {level} 카테고리 생성", use_container_width=True)
    
    if submitted:
        create_child_category(parent_code, code_number, category_name, description, level)

def get_available_parent_codes(parent_level):
    """상위 레벨 코드 목록 조회"""
    db = get_db()
    if not db:
        return []
    
    try:
        parent_codes = db.execute_query(
            "product_categories",
            conditions={
                "category_level": parent_level,
                "is_active": True
            }
        )
        if parent_codes:
            parent_codes = sorted(parent_codes, key=lambda x: x['category_code'])
        return parent_codes or []
    except Exception as e:
        st.error(f"상위 코드 조회 오류: {str(e)}")
        return []

def create_level1_category(main_category, code_number, category_name, description):
    """Level 1 카테고리 생성"""
    if not code_number or not category_name:
        show_error_message("코드 번호와 카테고리명을 입력해주세요.")
        return
    
    if not (2 <= len(code_number) <= 5):
        show_error_message("코드 번호는 2~5자리여야 합니다.")
        return
    
    category_code = f"{main_category}-{code_number}"
    
    db = get_db()
    if not db:
        show_error_message("데이터베이스 연결 실패")
        return
    
    try:
        # 중복 확인
        existing = db.execute_query("product_categories", conditions={"category_code": category_code})
        if existing:
            show_error_message(f"코드 '{category_code}'가 이미 존재합니다.")
            return
        
        # 카테고리 데이터 준비
        cat_data = {
            'category_code': category_code,
            'category_name': category_name,
            'category_level': 1,
            'parent_category_id': None,
            'description': description if description else None,
            'is_active': True
        }
        
        # 데이터베이스에 삽입
        result = db.execute_query("product_categories", "insert", data=cat_data)
        
        if result:
            show_success_message(f"✅ Level 1 카테고리가 생성되었습니다!\n코드: {category_code}\n카테고리명: {category_name}")
            st.rerun()
        else:
            show_error_message("카테고리 생성에 실패했습니다.")
    
    except Exception as e:
        show_error_message(f"카테고리 생성 오류: {str(e)}")

def create_child_category(parent_code, code_number, category_name, description, level):
    """하위 레벨 카테고리 생성"""
    if not code_number or not category_name:
        show_error_message("코드 번호와 카테고리명을 입력해주세요.")
        return
    
    if not (2 <= len(code_number) <= 5):
        show_error_message("코드 번호는 2~5자리여야 합니다.")
        return
    
    category_code = f"{parent_code['category_code']}-{code_number}"
    
    db = get_db()
    if not db:
        show_error_message("데이터베이스 연결 실패")
        return
    
    try:
        # 중복 확인
        existing = db.execute_query("product_categories", conditions={"category_code": category_code})
        if existing:
            show_error_message(f"코드 '{category_code}'가 이미 존재합니다.")
            return
        
        # 카테고리 데이터 준비
        cat_data = {
            'category_code': category_code,
            'category_name': category_name,
            'category_level': level,
            'parent_category_id': parent_code['category_id'],
            'description': description if description else None,
            'is_active': True
        }
        
        # 데이터베이스에 삽입
        result = db.execute_query("product_categories", "insert", data=cat_data)
        
        if result:
            show_success_message(f"✅ Level {level} 카테고리가 생성되었습니다!\n코드: {category_code}\n카테고리명: {category_name}")
            st.rerun()
        else:
            show_error_message("카테고리 생성에 실패했습니다.")
    
    except Exception as e:
        show_error_message(f"카테고리 생성 오류: {str(e)}")

def category_list_interface():
    """카테고리 목록 인터페이스"""
    st.markdown("### 📋 카테고리 목록")
    
    # 필터 영역
    col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
    
    with col1:
        level_filter = st.selectbox(
            "레벨 필터", 
            ["전체"] + [f"Level {i}" for i in range(1, 7)]
        )
    
    with col2:
        search_term = st.text_input("검색", placeholder="코드 또는 카테고리명")
    
    with col3:
        st.write("")  # 빈 공간
    
    with col4:
        if st.button("🔄", help="새로고침"):
            st.rerun()
    
    # 카테고리 목록 로드
    categories = load_filtered_categories(level_filter, search_term)
    
    if not categories:
        st.warning("표시할 카테고리가 없습니다.")
        return
    
    # Level 1 매핑 생성
    level1_mapping = create_level1_mapping()
    
    # 목록 테이블
    display_category_table(categories, level1_mapping)

def load_filtered_categories(level_filter, search_term):
    """필터링된 카테고리 목록 로드"""
    db = get_db()
    if not db:
        return []
    
    try:
        conditions = {"is_active": True}
        
        # 레벨 필터
        if level_filter != "전체":
            level_num = int(level_filter.split()[-1])
            conditions["category_level"] = level_num
        
        categories = db.execute_query("product_categories", conditions=conditions)
        
        if categories:
            # 검색어 필터링
            if search_term:
                categories = [
                    cat for cat in categories 
                    if search_term.lower() in cat['category_code'].lower() 
                    or search_term.lower() in (cat['category_name'] or '').lower()
                ]
            
            # 정렬
            categories = sorted(categories, key=lambda x: (x['category_level'], x['category_code']))
        
        return categories or []
    
    except Exception as e:
        st.error(f"카테고리 목록 로드 오류: {str(e)}")
        return []

def create_level1_mapping():
    """Level 1 카테고리명 매핑 생성"""
    db = get_db()
    if not db:
        return {}
    
    try:
        level1_categories = db.execute_query(
            "product_categories",
            conditions={"category_level": 1, "is_active": True}
        )
        
        mapping = {}
        if level1_categories:
            for cat in level1_categories:
                main_code = cat['category_code'].split('-')[0]
                mapping[main_code] = cat['category_name']
        
        return mapping
    
    except Exception as e:
        st.error(f"Level 1 매핑 생성 오류: {str(e)}")
        return {}

def get_level1_name(category_code, level1_mapping):
    """카테고리 코드에서 Level 1 이름 추출"""
    main_code = category_code.split('-')[0]
    return level1_mapping.get(main_code, main_code)

def display_category_table(categories, level1_mapping):
    """카테고리 테이블 표시"""
    # 테이블 헤더
    col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 2, 2, 1, 1.5])
    
    with col1:
        st.markdown("**레벨**")
    with col2:
        st.markdown("**카테고리 코드**")
    with col3:
        st.markdown("**제품명 (Level 1)**")
    with col4:
        st.markdown("**자체 카테고리명**")
    with col5:
        st.markdown("**등록상태**")
    with col6:
        st.markdown("**액션**")
    
    st.markdown("---")
    
    # 카테고리 행 표시
    for cat in categories:
        display_category_row(cat, level1_mapping)

def display_category_row(category, level1_mapping):
    """카테고리 행 표시 - 개선된 편집 기능"""
    col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 2, 2, 1, 1.5])
    
    # 편집 모드 확인
    edit_key = f"edit_mode_{category['category_id']}"
    is_editing = st.session_state.get(edit_key, False)
    
    with col1:
        st.write(f"L{category['category_level']}")
    
    with col2:
        st.code(category['category_code'])
    
    with col3:
        level1_name = get_level1_name(category['category_code'], level1_mapping)
        st.write(level1_name)
    
    with col4:
        if is_editing:
            # 편집 모드: 카테고리명 입력창
            new_name = st.text_input(
                "카테고리명", 
                value=category['category_name'] or "", 
                key=f"name_input_{category['category_id']}"
            )
        else:
            # 일반 모드: 카테고리명 표시
            st.write(category['category_name'] or "")
    
    with col5:
        # 제품 등록 상태 확인
        is_product_registered = check_product_registration(category['category_code'])
        if is_product_registered:
            st.success("등록완료")
        else:
            st.info("미등록")
    
    with col6:
        if is_editing:
            # 편집 모드: 저장/취소 버튼
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                if st.button("💾", key=f"save_{category['category_id']}", help="저장"):
                    # 편집된 데이터 가져오기
                    new_name = st.session_state.get(f"name_input_{category['category_id']}", "")
                    new_desc = st.session_state.get(f"desc_input_{category['category_id']}", "")
                    
                    # 데이터 업데이트
                    update_category_data(category['category_id'], new_name, new_desc)
            
            with col_cancel:
                if st.button("❌", key=f"cancel_{category['category_id']}", help="취소"):
                    # 편집 모드 종료 (변경사항 취소)
                    st.session_state[edit_key] = False
                    st.rerun()
        else:
            # 일반 모드: 편집/삭제/제품등록 버튼
            if category['category_level'] == 6:
                # Level 6: 편집, 삭제, 제품등록
                col_edit, col_delete, col_product = st.columns(3)
                
                with col_edit:
                    if st.button("✏️", key=f"edit_{category['category_id']}", help="편집"):
                        st.session_state[edit_key] = True
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️", key=f"delete_{category['category_id']}", help="삭제"):
                        delete_category_immediate(category['category_id'])
                
                with col_product:
                    if not is_product_registered:
                        if st.button("📦", key=f"product_{category['category_id']}", help="제품등록"):
                            st.session_state[f"product_modal_{category['category_id']}"] = True
                            st.rerun()
                    else:
                        st.write("✅")
            else:
                # Level 1~5: 편집, 삭제만
                col_edit, col_delete, col_space = st.columns(3)
                
                with col_edit:
                    if st.button("✏️", key=f"edit_{category['category_id']}", help="편집"):
                        st.session_state[edit_key] = True
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️", key=f"delete_{category['category_id']}", help="삭제"):
                        delete_category_immediate(category['category_id'])
                
                with col_space:
                    st.write("")  # 빈 공간
    
    # 편집 모드에서 설명 필드 추가
    if is_editing:
        st.markdown("**설명 수정:**")
        new_desc = st.text_area(
            "설명", 
            value=category.get('description', '') or '',
            key=f"desc_input_{category['category_id']}",
            height=80
        )
        st.markdown("---")
    
    # 제품 등록 모달창 표시
    if st.session_state.get(f"product_modal_{category['category_id']}", False):
        show_product_registration_modal(category)
    
    if not is_editing:
        st.markdown("---")

def update_category_data(category_id, new_name, new_description):
    """카테고리 데이터 업데이트 (이름 + 설명)"""
    if not new_name.strip():
        show_error_message("카테고리명을 입력해주세요.")
        return
    
    db = get_db()
    if not db:
        show_error_message("데이터베이스 연결 실패")
        return
    
    try:
        # 업데이트할 데이터 준비
        update_data = {
            "category_name": new_name.strip(),
            "description": new_description.strip() if new_description.strip() else None
        }
        
        # 데이터베이스 업데이트
        result = db.execute_query(
            "product_categories",
            "update",
            data=update_data,
            conditions={"category_id": category_id}
        )
        
        if result is not None:
            show_success_message("✅ 카테고리 정보가 수정되었습니다!")
            # 편집 모드 종료
            st.session_state[f"edit_mode_{category_id}"] = False
            # 페이지 새로고침
            st.rerun()
        else:
            show_error_message("카테고리 수정에 실패했습니다.")
    
    except Exception as e:
        show_error_message(f"수정 오류: {str(e)}")

def check_product_registration(category_code):
    """카테고리 코드가 제품으로 등록되었는지 확인"""
    db = get_db()
    if not db:
        return False
    
    try:
        # 제품 코드 형식: A-HR-ST-VV-20-MAE-00-PRD
        product_code = f"{category_code}-PRD"
        existing_product = db.execute_query("products", conditions={"product_code": product_code})
        return len(existing_product) > 0 if existing_product else False
    except Exception as e:
        st.error(f"제품 등록 상태 확인 오류: {str(e)}")
        return False

def show_product_registration_modal(category):
    """제품 등록 모달창 표시"""
    st.markdown("---")
    st.markdown(f"### 📦 제품 등록: {category['category_code']}")
    
    with st.form(f"product_registration_{category['category_id']}"):
        st.info(f"카테고리: {category['category_code']} → 제품 코드: {category['category_code']}-PRD")
        
        # 제품 정보 입력
        col1, col2 = st.columns([2, 1])
        
        with col1:
            product_name = st.text_input("제품명 *", placeholder="예: Hot Runner Revision")
        
        with col2:
            unit = st.selectbox("단위", ["EA", "Set", "Pcs", "Box", "Kg", "M", "L"])
        
        product_description = st.text_area("제품 설명", placeholder="제품의 상세 설명을 입력하세요")
        
        col3, col4 = st.columns([1, 1])
        
        with col3:
            cost_price = st.number_input("기본 원가 (USD)", min_value=0.0, step=0.01, value=0.0)
        
        with col4:
            selling_price = st.number_input("판매가 (USD)", min_value=0.0, step=0.01, value=0.0)
        
        # 버튼
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submitted = st.form_submit_button("✅ 제품 등록", use_container_width=True)
        
        with col_cancel:
            cancelled = st.form_submit_button("❌ 취소", use_container_width=True)
        
        if submitted:
            register_product(category, product_name, product_description, unit, cost_price, selling_price)
        
        if cancelled:
            st.session_state[f"product_modal_{category['category_id']}"] = False
            st.rerun()

def register_product(category, product_name, product_description, unit, cost_price, selling_price):
    """제품 등록 처리"""
    if not product_name:
        show_error_message("제품명을 입력해주세요.")
        return
    
    db = get_db()
    if not db:
        show_error_message("데이터베이스 연결 실패")
        return
    
    try:
        # 제품 코드 생성
        product_code = f"{category['category_code']}-PRD"
        
        # 중복 확인
        existing_product = db.execute_query("products", conditions={"product_code": product_code})
        if existing_product:
            show_error_message(f"제품 코드 '{product_code}'가 이미 존재합니다.")
            return
        
        # 제품 데이터 준비
        product_data = {
            'product_code': product_code,
            'product_name': product_name,
            'category_code': category['category_code'],  # 카테고리 코드 연결
            'description': product_description if product_description else None,
            'unit': unit,
            'cost_price': cost_price,
            'selling_price_usd': selling_price,
            'is_active': True
        }
        
        # products 테이블에 삽입
        result = db.execute_query("products", "insert", data=product_data)
        
        if result:
            show_success_message(f"✅ 제품이 등록되었습니다!\n제품 코드: {product_code}\n제품명: {product_name}")
            st.session_state[f"product_modal_{category['category_id']}"] = False
            st.rerun()
        else:
            show_error_message("제품 등록에 실패했습니다.")
    
    except Exception as e:
        show_error_message(f"제품 등록 오류: {str(e)}")

def delete_category_immediate(category_id):
    """즉시 삭제 처리 - 데이터베이스에서 완전 삭제"""
    db = get_db()
    if not db:
        show_error_message("데이터베이스 연결 실패")
        return
    
    try:
        # 삭제 전 카테고리 정보 확인
        category = db.execute_query("product_categories", conditions={"category_id": category_id})
        if not category:
            show_error_message("카테고리를 찾을 수 없습니다.")
            return
        
        category_code = category[0]['category_code']
        
        # 하위 카테고리들 완전 삭제
        children = db.execute_query("product_categories", conditions={"parent_category_id": category_id})
        if children:
            for child in children:
                delete_children_recursive(child['category_id'])
        
        # 자기 자신 완전 삭제 - 직접 Supabase 쿼리 사용
        try:
            result = db.supabase.table("product_categories").delete().eq("category_id", category_id).execute()
            
            if result.data or len(result.data) >= 0:  # Supabase delete는 빈 배열도 성공
                show_success_message(f"카테고리 '{category_code}'가 완전히 삭제되었습니다!")
                st.rerun()
            else:
                show_error_message("카테고리 삭제에 실패했습니다.")
        except Exception as delete_error:
            show_error_message(f"삭제 실행 오류: {str(delete_error)}")
    
    except Exception as e:
        show_error_message(f"삭제 오류: {str(e)}")

def delete_children_recursive(parent_id):
    """하위 카테고리들 재귀적으로 완전 삭제"""
    db = get_db()
    if not db:
        return
    
    try:
        children = db.execute_query(
            "product_categories",
            conditions={"parent_category_id": parent_id}
        )
        
        if children:
            for child in children:
                # 자식들의 자식들도 삭제
                delete_children_recursive(child['category_id'])
                
                # 현재 자식 완전 삭제 - 직접 Supabase 쿼리 사용
                try:
                    db.supabase.table("product_categories").delete().eq("category_id", child['category_id']).execute()
                except Exception as child_delete_error:
                    st.error(f"하위 카테고리 삭제 오류: {str(child_delete_error)}")
    
    except Exception as e:
        st.error(f"하위 카테고리 조회 오류: {str(e)}")

def statistics_interface():
    """통계 인터페이스"""
    st.markdown("### 📊 카테고리 통계")
    
    db = get_db()
    if not db:
        st.error("데이터베이스 연결 실패")
        return
    
    try:
        all_categories = db.execute_query("product_categories", conditions={"is_active": True})
        
        if not all_categories:
            st.info("등록된 카테고리가 없습니다.")
            return
        
        # 전체 통계
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("전체 카테고리", len(all_categories))
        
        with col2:
            # Level 6 (완성된) 카테고리 수
            level6_count = len([cat for cat in all_categories if cat['category_level'] == 6])
            st.metric("완성 카테고리 (Level 6)", level6_count)
        
        # 레벨별 통계
        st.markdown("#### 레벨별 통계")
        
        level_stats = {}
        for cat in all_categories:
            level = cat['category_level']
            if level not in level_stats:
                level_stats[level] = 0
            level_stats[level] += 1
        
        cols = st.columns(6)
        for i, level in enumerate(range(1, 7)):
            with cols[i]:
                count = level_stats.get(level, 0)
                st.metric(f"Level {level}", count)
        
        # 대분류별 통계
        st.markdown("#### 대분류별 통계")
        
        main_stats = {}
        level1_mapping = create_level1_mapping()
        
        for cat in all_categories:
            main_code = cat['category_code'].split('-')[0]
            if main_code not in main_stats:
                main_stats[main_code] = 0
            main_stats[main_code] += 1
        
        if main_stats:
            df_data = []
            for main_code, count in sorted(main_stats.items()):
                name = level1_mapping.get(main_code, main_code)
                df_data.append({
                    '대분류': main_code,
                    '제품명': name,
                    '카테고리 수': count
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        
        # 제품 등록 통계 추가
        st.markdown("#### 제품 등록 통계")
        
        level6_categories = [cat for cat in all_categories if cat['category_level'] == 6]
        if level6_categories:
            registered_count = 0
            for cat in level6_categories:
                if check_product_registration(cat['category_code']):
                    registered_count += 1
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Level 6 카테고리", len(level6_categories))
            
            with col2:
                st.metric("제품 등록 완료", registered_count)
            
            with col3:
                unregistered = len(level6_categories) - registered_count
                st.metric("제품 등록 대기", unregistered)
    
    except Exception as e:
        st.error(f"통계 조회 오류: {str(e)}")

if __name__ == "__main__":
    category_management_page()