# corporate_account_management.py - 법인 계정 관리 시스템
import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional

def show_corporate_account_management(load_func, save_func, update_func, delete_func, 
                                     get_current_user_func):
    """법인 계정 관리 시스템 메인 함수"""
    
    st.title("🏢 법인 계정 관리")
    st.caption("Corporate Account Management - YMV Group")
    
    # 현재 사용자 정보 확인
    current_user = get_current_user_func()
    if not current_user:
        st.error("로그인이 필요합니다.")
        return
    
    # CEO만 접근 가능
    if current_user.get('role') != 'CEO':
        st.error("⚠️ 법인 계정 관리는 CEO만 접근 가능합니다.")
        return
    
    # 탭 구성
    tabs = st.tabs(["📋 계정 목록", "➕ 계정 등록/수정", "🔑 비밀번호 관리"])
    
    with tabs[0]:
        render_account_list(load_func, save_func, update_func, delete_func, current_user)
    
    with tabs[1]:
        render_account_form(load_func, save_func, update_func, current_user)
    
    with tabs[2]:
        render_password_management(load_func, update_func, current_user)

def render_account_list(load_func, save_func, update_func, delete_func, current_user):
    """법인 계정 목록 탭"""
    
    st.subheader("📋 법인 계정 목록")
    
    # 검색 및 필터 영역
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("검색", placeholder="법인명, 계정ID로 검색")
    
    with col2:
        country_filter = st.selectbox("국가 필터", ["전체", "Vietnam", "Thailand", "Korea", "China"])
    
    with col3:
        status_filter = st.selectbox("상태 필터", ["전체", "활성", "비활성"])
    
    # 법인 계정 데이터 로드
    try:
        accounts_data = load_func("corporate_accounts")
        if not accounts_data:
            st.info("등록된 법인 계정이 없습니다.")
            return
        
        accounts_df = pd.DataFrame(accounts_data)
        
        # 필터 적용
        filtered_df = apply_account_filters(accounts_df, search_term, 
                                           country_filter, status_filter)
        
        if filtered_df.empty:
            st.warning("검색 조건에 맞는 법인 계정이 없습니다.")
            return
        
        # 통계 정보
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 법인 계정", len(filtered_df))
        with col2:
            active_count = len(filtered_df[filtered_df['is_active'] == True])
            st.metric("활성 계정", active_count)
        with col3:
            country_count = filtered_df['country'].nunique()
            st.metric("국가 수", country_count)
        
        # CSV 다운로드 버튼
        if st.button("📥 CSV 다운로드"):
            csv_data = create_account_csv(filtered_df)
            st.download_button(
                label="법인 계정 목록 다운로드",
                data=csv_data,
                file_name=f"corporate_accounts_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # 법인 계정 목록 테이블
        display_account_table(filtered_df, current_user, update_func, delete_func)
        
    except Exception as e:
        st.error(f"법인 계정 목록 로드 중 오류 발생: {str(e)}")

def render_account_form(load_func, save_func, update_func, current_user):
    """법인 계정 등록/수정 폼"""
    
    st.subheader("법인 계정 등록/수정")
    
    # 수정할 계정 선택
    col1, col2 = st.columns([3, 1])
    
    with col1:
        accounts = load_func("corporate_accounts")
        account_options = ["신규 등록"] + [f"{acc['company_name']} ({acc['account_id']})" 
                                       for acc in accounts if accounts]
        selected_account = st.selectbox("법인 계정 선택", account_options)
    
    with col2:
        if selected_account != "신규 등록":
            if st.button("계정 삭제", type="secondary"):
                if st.session_state.get('confirm_delete_account'):
                    # 삭제 실행
                    account_id = extract_account_id_from_selection(selected_account, accounts)
                    if delete_account_with_validation(account_id, update_func):
                        st.success("법인 계정이 삭제되었습니다.")
                        st.rerun()
                else:
                    st.session_state['confirm_delete_account'] = True
                    st.warning("한 번 더 클릭하여 삭제를 확인하세요.")
    
    # 기존 데이터 로드 (수정 모드)
    existing_data = None
    if selected_account != "신규 등록":
        account_id = extract_account_id_from_selection(selected_account, accounts)
        existing_data = load_func("corporate_accounts", filters={"id": account_id})
        existing_data = existing_data[0] if existing_data else None
    
    # 폼 렌더링
    with st.form("account_form"):
        st.write("### 기본 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("법인명 (한글/베트남어) *", 
                                        value=existing_data.get('company_name', '') if existing_data else '')
            company_code = st.text_input("법인 코드 *", 
                                        value=existing_data.get('company_code', '') if existing_data else '',
                                        help="예: YMV, YMTH, YMK, YMC")
            account_id = st.text_input("로그인 ID *", 
                                      value=existing_data.get('account_id', '') if existing_data else '',
                                      help="로그인 시 사용할 계정 ID")
        
        with col2:
            company_name_en = st.text_input("법인명 (영문)", 
                                           value=existing_data.get('company_name_en', '') if existing_data else '')
            
            country_options = ["Vietnam", "Thailand", "Korea", "China"]
            country = st.selectbox("국가 *", country_options,
                                 index=country_options.index(existing_data.get('country', 'Vietnam'))
                                 if existing_data and existing_data.get('country') in country_options else 0)
            
            is_active = st.checkbox("활성 상태", 
                                   value=existing_data.get('is_active', True) if existing_data else True)
        
        st.write("### 권한 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            approval_authority = st.checkbox("승인 권한", 
                                            value=existing_data.get('approval_authority', True) if existing_data else True,
                                            help="지출 요청서 등의 승인 권한")
        
        with col2:
            # 비밀번호 (신규 등록시만)
            if not existing_data:
                st.write("**비밀번호 설정**")
                password = st.text_input("비밀번호 *", type="password")
                confirm_password = st.text_input("비밀번호 확인 *", type="password")
        
        st.write("### 추가 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            address = st.text_area("주소", 
                                  value=existing_data.get('address', '') if existing_data else '')
        
        with col2:
            notes = st.text_area("비고", 
                                value=existing_data.get('notes', '') if existing_data else '')
        
        # 제출 버튼
        submitted = st.form_submit_button("저장", type="primary")
        
        if submitted:
            # 유효성 검사
            validation_errors = validate_account_form(
                company_name, company_code, account_id, country,
                password if not existing_data else None,
                confirm_password if not existing_data else None
            )
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                # 데이터 준비
                account_data = {
                    'company_name': company_name,
                    'company_name_en': company_name_en,
                    'company_code': company_code,
                    'account_id': account_id,
                    'country': country,
                    'is_active': is_active,
                    'approval_authority': approval_authority,
                    'address': address,
                    'notes': notes,
                    'updated_at': datetime.now().isoformat()
                }
                
                if not existing_data:
                    account_data['password'] = password
                    account_data['created_at'] = datetime.now().isoformat()
                
                # 저장 실행
                try:
                    if existing_data:
                        account_data['id'] = existing_data['id']
                        update_func("corporate_accounts", account_data, "id")
                        st.success("법인 계정 정보가 수정되었습니다.")
                    else:
                        save_func("corporate_accounts", account_data)
                        st.success("새 법인 계정이 등록되었습니다.")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"저장 중 오류 발생: {str(e)}")

def render_password_management(load_func, update_func, current_user):
    """비밀번호 관리 탭"""
    
    st.subheader("🔑 법인 계정 비밀번호 관리")
    
    st.write("### 법인 계정 비밀번호 변경")
    
    # 법인 계정 목록 로드
    accounts = load_func("corporate_accounts")
    if not accounts:
        st.info("법인 계정 정보가 없습니다.")
        return
    
    # 법인 계정 선택
    account_options = {f"{acc.get('company_name', 'N/A')} ({acc.get('account_id', 'N/A')}) - {acc.get('country', 'N/A')}": acc 
                      for acc in accounts}
    
    selected_acc_key = st.selectbox("변경할 법인 계정 선택", list(account_options.keys()))
    selected_acc = account_options[selected_acc_key]
    
    st.info(f"선택된 법인: {selected_acc.get('company_name')} ({selected_acc.get('company_code')})")
    
    with st.form("account_password_change"):
        new_password = st.text_input("새 비밀번호", type="password")
        confirm_password = st.text_input("비밀번호 확인", type="password")
        
        submitted = st.form_submit_button("비밀번호 변경", type="primary")
        
        if submitted:
            if not new_password:
                st.error("새 비밀번호를 입력해주세요.")
            elif len(new_password) < 4:
                st.error("비밀번호는 최소 4자 이상이어야 합니다.")
            elif new_password != confirm_password:
                st.error("비밀번호가 일치하지 않습니다.")
            else:
                # 비밀번호 업데이트
                update_data = {
                    'id': selected_acc['id'],
                    'password': new_password,
                    'updated_at': datetime.now().isoformat()
                }
                
                if update_func("corporate_accounts", update_data, "id"):
                    st.success(f"✅ {selected_acc.get('company_name')} 법인 계정의 비밀번호가 변경되었습니다.")
                    st.balloons()
                else:
                    st.error("비밀번호 변경에 실패했습니다.")

# ==================== 헬퍼 함수들 ====================

def apply_account_filters(df: pd.DataFrame, search_term: str, 
                         country_filter: str, status_filter: str) -> pd.DataFrame:
    """법인 계정 목록 필터링"""
    filtered_df = df.copy()
    
    # 검색어 필터
    if search_term:
        search_cols = ['company_name', 'company_name_en', 'account_id', 'company_code']
        search_mask = False
        for col in search_cols:
            if col in filtered_df.columns:
                search_mask |= filtered_df[col].astype(str).str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[search_mask]
    
    # 국가 필터
    if country_filter != "전체":
        filtered_df = filtered_df[filtered_df['country'] == country_filter]
    
    # 상태 필터
    if status_filter != "전체":
        status_map = {"활성": True, "비활성": False}
        filtered_df = filtered_df[filtered_df['is_active'] == status_map[status_filter]]
    
    return filtered_df

def display_account_table(df: pd.DataFrame, current_user: Dict, 
                         update_func, delete_func):
    """법인 계정 목록 테이블 표시"""
    
    # 표시할 컬럼 선택
    display_columns = {
        'company_code': '법인코드',
        'company_name': '법인명',
        'company_name_en': '영문명',
        'account_id': '계정ID',
        'country': '국가',
        'is_active': '상태',
        'approval_authority': '승인권한',
        'created_at': '생성일'
    }
    
    # 데이터 준비
    display_df = df[[col for col in display_columns.keys() if col in df.columns]].copy()
    display_df.columns = [display_columns[col] for col in display_df.columns]
    
    # 상태 한글화
    if '상태' in display_df.columns:
        display_df['상태'] = display_df['상태'].map({True: "✅ 활성", False: "❌ 비활성"})
    
    # 승인권한 표시
    if '승인권한' in display_df.columns:
        display_df['승인권한'] = display_df['승인권한'].map({True: "⭐ 있음", False: "없음"})
    
    # 생성일 포맷팅
    if '생성일' in display_df.columns:
        display_df['생성일'] = pd.to_datetime(display_df['생성일']).dt.strftime('%Y-%m-%d')
    
    # 테이블 표시
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "생성일": st.column_config.DateColumn("생성일", format="YYYY-MM-DD"),
        }
    )

def validate_account_form(company_name: str, company_code: str, account_id: str, 
                         country: str, password: str = None, 
                         confirm_password: str = None) -> List[str]:
    """법인 계정 폼 유효성 검사"""
    errors = []
    
    if not company_name.strip():
        errors.append("법인명을 입력해주세요.")
    
    if not company_code.strip():
        errors.append("법인 코드를 입력해주세요.")
    
    if not account_id.strip():
        errors.append("로그인 ID를 입력해주세요.")
    
    if not country:
        errors.append("국가를 선택해주세요.")
    
    # 신규 등록시 비밀번호 검사
    if password is not None:
        if not password:
            errors.append("비밀번호를 입력해주세요.")
        elif len(password) < 4:
            errors.append("비밀번호는 4자 이상이어야 합니다.")
        elif password != confirm_password:
            errors.append("비밀번호가 일치하지 않습니다.")
    
    return errors

def create_account_csv(df: pd.DataFrame) -> str:
    """법인 계정 목록 CSV 생성"""
    return df.to_csv(index=False, encoding='utf-8-sig')

def extract_account_id_from_selection(selection: str, accounts: List[Dict]) -> int:
    """선택된 법인 계정 문자열에서 ID 추출"""
    account_id_str = selection.split('(')[1].split(')')[0]
    for acc in accounts:
        if acc['account_id'] == account_id_str:
            return acc['id']
    return None

def delete_account_with_validation(account_id: int, update_func) -> bool:
    """법인 계정 삭제 (소프트 삭제)"""
    try:
        # 실제 삭제 대신 비활성화
        update_data = {
            'id': account_id,
            'is_active': False,
            'updated_at': datetime.now().isoformat()
        }
        update_func("corporate_accounts", update_data, "id")
        return True
    except Exception as e:
        st.error(f"삭제 중 오류 발생: {str(e)}")
        return False