"""
YMV ERP 시스템 인증 관리 유틸리티
Authentication utilities for YMV ERP System
"""

import streamlit as st
import time
from datetime import datetime


class AuthManager:
    """
    인증 관리 클래스
    Authentication management class
    """
    
    def __init__(self, db_operations):
        """AuthManager 초기화"""
        self.db = db_operations

    def login_user(self, employee_id, password, login_type="employee"):
        """
        사용자 로그인 (직원 또는 법인)
        User login authentication (employee or company)
        """
        try:
            if not employee_id or not password:
                st.error("아이디와 비밀번호를 입력해주세요.")
                return False
            
            if login_type == "employee":
                # 직원 로그인
                employees = self.db.load_data("employees")
                if not employees:
                    st.error("직원 정보를 불러올 수 없습니다.")
                    return False
                
                # 사용자 인증
                for employee in employees:
                    if (employee.get("employee_id") == employee_id and 
                        employee.get("password") == password):
                        
                        # 활성 계정 확인
                        if not employee.get('is_active', True):
                            st.error("비활성화된 계정입니다.")
                            return False
                        
                        # 세션에 사용자 정보 저장
                        st.session_state.logged_in = True
                        st.session_state.user_info = employee
                        st.session_state.user_type = "employee"
                        
                        # 로그인 시간 기록
                        self._record_login_activity(employee.get('id'))
                        
                        return True
                
                # 인증 실패
                st.error("잘못된 사번 또는 비밀번호입니다.")
                return False
            
            elif login_type == "company":
                # 법인 로그인
                companies = self.db.load_data("companies")
                if not companies:
                    st.error("법인 정보를 불러올 수 없습니다.")
                    return False
                
                # 법인 인증
                for company in companies:
                    if (company.get("login_id") == employee_id and 
                        company.get("login_password") == password):
                        
                        # 활성 계정 확인
                        if not company.get('is_active', True):
                            st.error("비활성화된 법인입니다.")
                            return False
                        
                        # 세션에 법인 정보 저장 (직원 형식으로 변환)
                        st.session_state.logged_in = True
                        st.session_state.user_info = {
                            'id': company.get('id'),
                            'name': company.get('company_name'),
                            'employee_id': company.get('login_id'),
                            'role': 'Company',
                            'department': company.get('company_name_en'),
                            'company_code': company.get('company_code'),
                            'company_role': company.get('role'),
                            'is_active': company.get('is_active', True)
                        }
                        st.session_state.user_type = "company"
                        
                        return True
                
                # 인증 실패
                st.error("잘못된 로그인 ID 또는 비밀번호입니다.")
                return False
                
        except Exception as e:
            st.error(f"로그인 오류: {str(e)}")
            return False
        
    def logout_user(self):
        """
        사용자 로그아웃
        User logout
        """
        try:
            # 로그아웃 활동 기록
            current_user = self.get_current_user()
            if current_user:
                self._record_logout_activity(current_user.get('id'))
            
            # 세션 정리
            st.session_state.logged_in = False
            st.session_state.user_info = None
            
            # 관련 세션 상태 정리
            keys_to_remove = [key for key in st.session_state.keys() 
                            if key.startswith(('edit_', 'confirm_', 'comment_'))]
            for key in keys_to_remove:
                del st.session_state[key]
            
            st.rerun()
            
        except Exception as e:
            st.error(f"로그아웃 오류: {str(e)}")
    
    def get_current_user(self):
        """
        현재 로그인된 사용자 정보 반환
        Get current logged-in user information
        """
        return st.session_state.get("user_info")
    
    def is_logged_in(self):
        """로그인 상태 확인"""
        return st.session_state.get("logged_in", False)
    
    def check_permission(self, required_role=None, required_permissions=None):
        """
        권한 확인 (master, admin, manager 지원)
        Check user permissions
        """
        current_user = self.get_current_user()
        if not current_user:
            return False
        
        # 역할 기반 권한 확인
        if required_role:
            user_role = current_user.get('role', 'employee')
            # Master는 모든 권한, CEO와 Admin도 높은 권한
            if user_role == 'Master':
                return True
            if user_role != required_role and user_role not in ['CEO', 'Admin']:
                return False
        
        # 특정 권한 확인 (향후 확장용)
        if required_permissions:
            user_permissions = current_user.get('permissions', [])
            for permission in required_permissions:
                if permission not in user_permissions:
                    return False
        
        return True
    
    def require_login(self):
        """
        로그인 필수 데코레이터 기능
        Require login decorator functionality
        """
        if not self.is_logged_in():
            st.warning("로그인이 필요합니다.")
            return False
        return True
    
    def require_manager_role(self):
        """
        관리자 권한 필수 (Master, CEO)
        Require manager role
        """
        current_user = self.get_current_user()
        if not current_user or current_user.get('role') not in ['Master', 'CEO']:
            st.warning("관리자 권한이 필요합니다.")
            return False
        return True
    
    def _record_login_activity(self, user_id):
        """로그인 활동 기록"""
        try:
            activity_data = {
                'user_id': user_id,
                'activity_type': 'login',
                'activity_time': datetime.now().isoformat(),
                'ip_address': self._get_client_ip(),
                'user_agent': self._get_user_agent()
            }
            
            # 활동 로그 테이블이 있다면 기록
            # self.db.save_data("user_activities", activity_data)
            
        except Exception as e:
            # 로그인 성공에 영향을 주지 않도록 에러는 무시
            pass
    
    def _record_logout_activity(self, user_id):
        """로그아웃 활동 기록"""
        try:
            activity_data = {
                'user_id': user_id,
                'activity_type': 'logout',
                'activity_time': datetime.now().isoformat()
            }
            
            # 활동 로그 테이블이 있다면 기록
            # self.db.save_data("user_activities", activity_data)
            
        except Exception as e:
            # 로그아웃에 영향을 주지 않도록 에러는 무시
            pass
    
    def _get_client_ip(self):
        """클라이언트 IP 주소 가져오기 (제한적)"""
        try:
            # Streamlit에서는 직접적인 IP 접근이 제한적
            return "unknown"
        except:
            return "unknown"
    
    def _get_user_agent(self):
        """사용자 에이전트 정보 가져오기 (제한적)"""
        try:
            # Streamlit에서는 직접적인 User-Agent 접근이 제한적
            return "unknown"
        except:
            return "unknown"
    
    def get_user_display_name(self, user_id=None):
        """
        사용자 표시명 가져오기
        Get user display name
        """
        if user_id is None:
            current_user = self.get_current_user()
            if not current_user:
                return "알 수 없음"
            return current_user.get('name', '이름 없음')
        
        # 특정 사용자 ID의 이름 조회
        try:
            employees = self.db.load_data("employees", filters={'id': user_id})
            if employees:
                return employees[0].get('name', '이름 없음')
            return "알 수 없음"
        except:
            return "알 수 없음"
    
    def update_user_profile(self, user_data):
        """
        사용자 프로필 업데이트
        Update user profile
        """
        try:
            current_user = self.get_current_user()
            if not current_user:
                return False
            
            # 업데이트 가능한 필드만 허용
            allowed_fields = ['name', 'email', 'phone', 'department']
            update_data = {k: v for k, v in user_data.items() if k in allowed_fields}
            update_data['id'] = current_user['id']
            update_data['updated_at'] = datetime.now().isoformat()
            
            success = self.db.update_data("employees", update_data)
            
            if success:
                # 세션의 사용자 정보도 업데이트
                for key, value in update_data.items():
                    if key in st.session_state.user_info:
                        st.session_state.user_info[key] = value
            
            return success
            
        except Exception as e:
            st.error(f"프로필 업데이트 실패: {str(e)}")
            return False
    
    def change_password(self, current_password, new_password):
        """
        비밀번호 변경
        Change password
        """
        try:
            current_user = self.get_current_user()
            if not current_user:
                return False
            
            # 현재 비밀번호 확인
            if current_user.get('password') != current_password:
                st.error("현재 비밀번호가 올바르지 않습니다.")
                return False
            
            # 새 비밀번호 검증
            if len(new_password) < 4:
                st.error("새 비밀번호는 최소 4자 이상이어야 합니다.")
                return False
            
            # 비밀번호 업데이트
            update_data = {
                'id': current_user['id'],
                'password': new_password,
                'updated_at': datetime.now().isoformat()
            }
            
            success = self.db.update_data("employees", update_data)
            
            if success:
                # 세션의 사용자 정보도 업데이트
                st.session_state.user_info['password'] = new_password
                st.success("비밀번호가 성공적으로 변경되었습니다.")
            
            return success
            
        except Exception as e:
            st.error(f"비밀번호 변경 실패: {str(e)}")
            return False


# 하위 호환성을 위한 래퍼 함수들
def login_user(employee_id, password, auth_manager=None):
    """하위 호환성 래퍼 함수 (employee_id 사용)"""
    if auth_manager:
        return auth_manager.login_user(employee_id, password)
    else:
        st.warning("AuthManager 인스턴스가 필요합니다.")
        return False

def logout_user(auth_manager=None):
    """하위 호환성 래퍼 함수"""
    if auth_manager:
        return auth_manager.logout_user()
    else:
        st.warning("AuthManager 인스턴스가 필요합니다.")

def get_current_user(auth_manager=None):
    """하위 호환성 래퍼 함수"""
    if auth_manager:
        return auth_manager.get_current_user()
    else:
        # 임시 처리 - 기존 방식 유지
        return st.session_state.get("user_info")