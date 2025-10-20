"""
법인 관리 시스템
- 법인 목록 조회
- 법인 등록/수정
- 비밀번호 변경
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def show_company_management(load_func, save_func, update_func, delete_func, get_current_user_func):
    """법인 관리 메인 페이지"""
    st.title("🏢 법인 관리")
    
    # 권한 체크 (Master만 접근 가능)
    current_user = get_current_user_func()
    if not current_user or current_user.get('role') != 'Master':
        st.warning("⚠️ 법인 관리는 Master 권한이 필요합니다.")
        return
    
    tab1, tab2, tab3 = st.tabs([
        "📋 법인 목록",
        "➕ 법인 등록/수정",
        "🔑 비밀번호 변경"
    ])
    
    with tab1:
        render_company_list(load_func, update_func, delete_func)
    
    with tab2:
        render_company_form(save_func, load_func, update_func)
    
    with tab3:
        render_password_change(load_func, update_func)


# ==========================================
# 법인 목록
# ==========================================

def render_company_list(load_func, update_func, delete_func):
    """법인 목록 조회"""
    st.header("📋 법인 목록")
    
    try:
        companies = load_func('companies') or []
        
        if not companies:
            st.info("등록된 법인이 없습니다.")
            return
        
        # 테이블 생성
        table_data = []
        for company in companies:
            table_data.append({
                'ID': company.get('id', ''),
                '법인코드': company.get('company_code', ''),
                '법인명': company.get('company_name', ''),
                '영문명': company.get('company_name_en', ''),
                '로그인ID': company.get('login_id', ''),
                '역할': company.get('role', ''),
                '상태': '✅ 활성' if company.get('is_active') else '❌ 비활성'
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"📊 총 **{len(companies)}개** 법인")
        
        # 수정/삭제 컨트롤
        st.markdown("---")
        render_edit_delete_controls(load_func, update_func, delete_func, companies)
        
    except Exception as e:
        st.error(f"❌ 법인 목록 로드 중 오류: {str(e)}")


def render_edit_delete_controls(load_func, update_func, delete_func, companies):
    """수정/삭제 컨트롤"""
    col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
    
    with col1:
        company_id_input = st.text_input("수정/삭제할 법인 ID", placeholder="법인 ID 입력", key="company_id_input")
    
    with col2:
        if st.button("✏️ 수정", use_container_width=True, type="primary"):
            if company_id_input and company_id_input.strip().isdigit():
                company_id = int(company_id_input.strip())
                found = next((c for c in companies if c.get('id') == company_id), None)
                
                if found:
                    st.session_state.editing_company_id = company_id
                    st.session_state.editing_company_data = found
                    st.success("✅ 수정 모드: '법인 등록/수정' 탭으로 이동하세요.")
                else:
                    st.error(f"❌ ID {company_id}를 찾을 수 없습니다.")
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    with col3:
        if st.button("🗑️ 삭제", use_container_width=True):
            if company_id_input and company_id_input.strip().isdigit():
                st.session_state.deleting_company_id = int(company_id_input.strip())
                st.rerun()
            else:
                st.error("❌ 올바른 ID를 입력하세요.")
    
    if st.session_state.get('deleting_company_id'):
        st.warning(f"⚠️ ID {st.session_state.deleting_company_id} 법인을 삭제하시겠습니까?")
        
        del_col1, del_col2, _ = st.columns([1, 1, 4])
        
        with del_col1:
            if st.button("✅ 예", key="confirm_del_company"):
                if delete_func('companies', st.session_state.deleting_company_id):
                    st.success("✅ 삭제 완료!")
                    st.session_state.pop('deleting_company_id', None)
                    st.rerun()
        
        with del_col2:
            if st.button("❌ 아니오", key="cancel_del_company"):
                st.session_state.pop('deleting_company_id', None)
                st.rerun()


# ==========================================
# 법인 등록/수정
# ==========================================

def render_company_form(save_func, load_func, update_func):
    """법인 등록/수정 폼"""
    
    # 수정 모드 체크
    editing_company = st.session_state.get('editing_company_data')
    
    if editing_company:
        st.header(f"✏️ 법인 수정 (ID: {editing_company.get('id')})")
    else:
        st.header("➕ 법인 등록")
    
    with st.form("company_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 기본 정보")
            
            company_code = st.text_input(
                "법인 코드 *",
                value=editing_company.get('company_code', '') if editing_company else '',
                placeholder="예: YMK, YMV, YMTH",
                disabled=bool(editing_company)
            )
            
            company_name = st.text_input(
                "법인명 (한글) *",
                value=editing_company.get('company_name', '') if editing_company else '',
                placeholder="예: 유몰드코리아"
            )
            
            company_name_en = st.text_input(
                "법인명 (영문) *",
                value=editing_company.get('company_name_en', '') if editing_company else '',
                placeholder="예: YUMOLD Korea"
            )
            
            company_name_vn = st.text_input(
                "법인명 (베트남어)",
                value=editing_company.get('company_name_vn', '') if editing_company else '',
                placeholder="예: YUMOLD Việt Nam"
            )
        
        with col2:
            st.subheader("🔐 로그인 정보")
            
            login_id = st.text_input(
                "로그인 ID *",
                value=editing_company.get('login_id', '') if editing_company else '',
                placeholder="예: ymk_admin",
                disabled=bool(editing_company)
            )
            
            if not editing_company:
                login_password = st.text_input(
                    "비밀번호 *",
                    type="password",
                    placeholder="비밀번호 입력"
                )
                
                login_password_confirm = st.text_input(
                    "비밀번호 확인 *",
                    type="password",
                    placeholder="비밀번호 재입력"
                )
            else:
                st.info("💡 비밀번호 변경은 '비밀번호 변경' 탭에서 가능합니다.")
            
            role = st.selectbox(
                "역할 *",
                ["Approver", "Spec_Writer"],
                index=0 if not editing_company else (0 if editing_company.get('role') == 'Approver' else 1)
            )
            
            is_active = st.checkbox(
                "활성 상태",
                value=editing_company.get('is_active', True) if editing_company else True
            )
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button(
                "💾 수정 저장" if editing_company else "➕ 법인 등록",
                type="primary",
                use_container_width=True
            )
        
        with col_cancel:
            cancel = st.form_submit_button("❌ 취소", use_container_width=True)
        
        if cancel:
            st.session_state.pop('editing_company_id', None)
            st.session_state.pop('editing_company_data', None)
            st.rerun()
        
        if submitted:
            # 유효성 검사
            if not company_code.strip():
                st.error("❌ 법인 코드를 입력해주세요.")
                return
            
            if not company_name.strip():
                st.error("❌ 법인명(한글)을 입력해주세요.")
                return
            
            if not company_name_en.strip():
                st.error("❌ 법인명(영문)을 입력해주세요.")
                return
            
            if not login_id.strip():
                st.error("❌ 로그인 ID를 입력해주세요.")
                return
            
            # 신규 등록 시 비밀번호 체크
            if not editing_company:
                if not login_password or not login_password_confirm:
                    st.error("❌ 비밀번호를 입력해주세요.")
                    return
                
                if login_password != login_password_confirm:
                    st.error("❌ 비밀번호가 일치하지 않습니다.")
                    return
                
                # 중복 체크
                try:
                    existing_companies = load_func('companies') or []
                    existing_codes = [c.get('company_code', '') for c in existing_companies]
                    existing_ids = [c.get('login_id', '') for c in existing_companies]
                    
                    if company_code in existing_codes:
                        st.error(f"❌ 법인 코드 '{company_code}'가 이미 존재합니다.")
                        return
                    
                    if login_id in existing_ids:
                        st.error(f"❌ 로그인 ID '{login_id}'가 이미 존재합니다.")
                        return
                except Exception as e:
                    st.warning(f"중복 확인 중 오류: {str(e)}")
            
            # 데이터 저장
            try:
                if editing_company:
                    # 수정
                    update_data = {
                        'id': editing_company.get('id'),
                        'company_name': company_name.strip(),
                        'company_name_en': company_name_en.strip(),
                        'company_name_vn': company_name_vn.strip() if company_name_vn.strip() else None,
                        'role': role,
                        'is_active': is_active,
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    if update_func('companies', update_data):
                        st.success("✅ 법인 정보가 수정되었습니다!")
                        st.balloons()
                        st.session_state.pop('editing_company_id', None)
                        st.session_state.pop('editing_company_data', None)
                        st.rerun()
                    else:
                        st.error("❌ 수정에 실패했습니다.")
                else:
                    # 신규 등록
                    company_data = {
                        'company_code': company_code.strip(),
                        'company_name': company_name.strip(),
                        'company_name_en': company_name_en.strip(),
                        'company_name_vn': company_name_vn.strip() if company_name_vn.strip() else None,
                        'login_id': login_id.strip(),
                        'login_password': login_password,
                        'role': role,
                        'is_active': is_active,
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    if save_func('companies', company_data):
                        st.success("✅ 법인이 등록되었습니다!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ 등록에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 저장 중 오류: {str(e)}")


# ==========================================
# 비밀번호 변경
# ==========================================

def render_password_change(load_func, update_func):
    """비밀번호 변경"""
    st.header("🔑 법인 비밀번호 변경")
    
    try:
        companies = load_func('companies') or []
        
        if not companies:
            st.info("등록된 법인이 없습니다.")
            return
        
        with st.form("password_change_form"):
            company_options = {f"{c.get('company_code')} - {c.get('company_name')}": c.get('id') 
                             for c in companies}
            
            selected_company = st.selectbox(
                "법인 선택 *",
                options=list(company_options.keys())
            )
            
            new_password = st.text_input(
                "새 비밀번호 *",
                type="password",
                placeholder="새 비밀번호 입력"
            )
            
            new_password_confirm = st.text_input(
                "새 비밀번호 확인 *",
                type="password",
                placeholder="새 비밀번호 재입력"
            )
            
            submitted = st.form_submit_button("🔑 비밀번호 변경", type="primary", use_container_width=True)
            
            if submitted:
                if not new_password or not new_password_confirm:
                    st.error("❌ 비밀번호를 입력해주세요.")
                    return
                
                if new_password != new_password_confirm:
                    st.error("❌ 비밀번호가 일치하지 않습니다.")
                    return
                
                company_id = company_options[selected_company]
                
                update_data = {
                    'id': company_id,
                    'login_password': new_password,
                    'updated_at': datetime.now().isoformat()
                }
                
                if update_func('companies', update_data):
                    st.success("✅ 비밀번호가 변경되었습니다!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ 비밀번호 변경에 실패했습니다.")
    
    except Exception as e:
        st.error(f"❌ 비밀번호 변경 중 오류: {str(e)}")