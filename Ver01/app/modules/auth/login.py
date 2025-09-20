"""
YMV 비즈니스 시스템 - 사용자 인증 모듈
"""

import streamlit as st
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import os

# 공통 모듈 임포트
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.shared.database import get_db
from app.shared.utils import show_success_message, show_error_message

class AuthManager:
    """인증 관리 클래스"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'ymv_default_secret_key_2024')
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해시화"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """비밀번호 검증"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            return False
    
    def generate_jwt_token(self, user_data: Dict) -> str:
        """JWT 토큰 생성"""
        payload = {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'is_master': user_data.get('is_master', False),
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """사용자 인증"""
        # Master 계정 (하드코딩)
        if username == "Master" and password == "1023":
            return {
                'user_id': 1,
                'username': 'Master',
                'email': 'master@ymv.com',
                'full_name': 'System Master',
                'is_master': True,
                'is_active': True,
                'department': 'IT',
                'position': 'Administrator'
            }
        
        # 데이터베이스에서 사용자 조회
        db = get_db()
        if not db:
            return None
        
        user = db.get_user_by_username(username)
        if not user:
            return None
        
        # 비밀번호 검증
        if not self.verify_password(password, user.get('password_hash', '')):
            return None
        
        # 활성 사용자인지 확인
        if not user.get('is_active', False):
            return None
        
        return {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'is_master': user.get('is_master', False),
            'is_active': user['is_active'],
            'department': user.get('department'),
            'position': user.get('position')
        }
    
    def check_user_permission(self, user_id: int, menu_name: str) -> bool:
        """사용자 권한 확인"""
        # Master는 모든 권한
        if user_id == 1:  # Master user_id
            return True
        
        db = get_db()
        if not db:
            return False
        
        return db.verify_user_permissions(user_id, menu_name)
    
    def login_user(self, username: str, password: str) -> bool:
        """사용자 로그인 처리"""
        user_data = self.authenticate_user(username, password)
        
        if user_data:
            # 세션에 사용자 정보 저장
            st.session_state.authenticated = True
            st.session_state.user_info = user_data
            
            # JWT 토큰 생성 및 저장
            token = self.generate_jwt_token(user_data)
            st.session_state.jwt_token = token
            
            return True
        
        return False
    
    def logout_user(self):
        """사용자 로그아웃 처리"""
        # 세션 정보 삭제
        if 'authenticated' in st.session_state:
            del st.session_state.authenticated
        if 'user_info' in st.session_state:
            del st.session_state.user_info
        if 'jwt_token' in st.session_state:
            del st.session_state.jwt_token
    
    def get_current_user(self) -> Optional[Dict]:
        """현재 로그인된 사용자 정보"""
        if st.session_state.get('authenticated', False):
            return st.session_state.get('user_info')
        return None
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        return st.session_state.get('authenticated', False)
    
    def require_authentication(self, func):
        """인증 필요 데코레이터"""
        def wrapper(*args, **kwargs):
            if not self.is_authenticated():
                st.error("❌ 로그인이 필요합니다.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    
    def require_permission(self, menu_name: str):
        """권한 필요 데코레이터"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.is_authenticated():
                    st.error("❌ 로그인이 필요합니다.")
                    st.stop()
                
                user_info = self.get_current_user()
                if not user_info:
                    st.error("❌ 사용자 정보를 찾을 수 없습니다.")
                    st.stop()
                
                if not self.check_user_permission(user_info['user_id'], menu_name):
                    st.error("❌ 이 기능에 대한 접근 권한이 없습니다.")
                    st.stop()
                
                return func(*args, **kwargs)
            return wrapper
        return decorator

# 전역 인증 매니저 인스턴스
@st.cache_resource
def get_auth_manager():
    """인증 매니저 싱글톤 인스턴스"""
    return AuthManager()

# 편의 함수들
def login(username: str, password: str) -> bool:
    """로그인"""
    auth = get_auth_manager()
    return auth.login_user(username, password)

def logout():
    """로그아웃"""
    auth = get_auth_manager()
    auth.logout_user()

def is_authenticated() -> bool:
    """인증 상태 확인"""
    auth = get_auth_manager()
    return auth.is_authenticated()

def get_current_user() -> Optional[Dict]:
    """현재 사용자 정보"""
    auth = get_auth_manager()
    return auth.get_current_user()

def check_permission(menu_name: str) -> bool:
    """권한 확인"""
    auth = get_auth_manager()
    user = auth.get_current_user()
    if not user:
        return False
    return auth.check_user_permission(user['user_id'], menu_name)