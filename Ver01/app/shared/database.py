"""
YMV 비즈니스 시스템 - 데이터베이스 연결 및 유틸리티
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd
from typing import Dict, List, Any, Optional
import json

# 환경변수 로드
load_dotenv()

class DatabaseManager:
    """데이터베이스 연결 및 관리 클래스"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.connect()
    
    def connect(self):
        """Supabase 연결"""
        try:
            # Streamlit Secrets 우선 사용 (배포 환경)
            if hasattr(st, 'secrets') and 'connections' in st.secrets:
                url = st.secrets.connections.supabase.SUPABASE_URL
                key = st.secrets.connections.supabase.SUPABASE_ANON_KEY
            else:
                # 로컬 환경에서는 .env 파일 사용
                url = os.getenv('SUPABASE_URL')
                key = os.getenv('SUPABASE_ANON_KEY')
            
            if not url or not key:
                st.error("❌ Supabase 연결 정보가 없습니다. .env 파일을 확인해주세요.")
                return
            
            self.supabase = create_client(url, key)
            
        except Exception as e:
            st.error(f"❌ 데이터베이스 연결 실패: {e}")
    
    def execute_query(self, table: str, operation: str = "select", 
                     data: Dict = None, conditions: Dict = None, 
                     columns: str = "*") -> Optional[List[Dict]]:
        """범용 쿼리 실행 함수"""
        try:
            if not self.supabase:
                return None
            
            if operation == "select":
                query = self.supabase.table(table).select(columns)
                if conditions:
                    for key, value in conditions.items():
                        query = query.eq(key, value)
                result = query.execute()
                return result.data
            
            elif operation == "insert":
                result = self.supabase.table(table).insert(data).execute()
                return result.data
            
            elif operation == "update":
                query = self.supabase.table(table).update(data)
                if conditions:
                    for key, value in conditions.items():
                        query = query.eq(key, value)
                result = query.execute()
                return result.data
            
            elif operation == "delete":
                query = self.supabase.table(table).delete()
                if conditions:
                    for key, value in conditions.items():
                        query = query.eq(key, value)
                result = query.execute()
                return result.data
                
        except Exception as e:
            st.error(f"쿼리 실행 오류: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """사용자명으로 사용자 조회"""
        result = self.execute_query("users", conditions={"username": username})
        return result[0] if result else None
    
    def verify_user_permissions(self, user_id: int, menu_name: str) -> bool:
        """사용자 권한 확인"""
        result = self.execute_query(
            "user_permissions", 
            conditions={"user_id": user_id, "menu_name": menu_name}
        )
        if result:
            return result[0].get("can_access", False)
        return False

# 전역 데이터베이스 매니저 인스턴스
@st.cache_resource
def get_database_manager():
    """데이터베이스 매니저 싱글톤 인스턴스"""
    return DatabaseManager()

# 편의 함수들
def get_db():
    """데이터베이스 매니저 가져오기"""
    return get_database_manager()

def execute_query(table: str, operation: str = "select", 
                 data: Dict = None, conditions: Dict = None, 
                 columns: str = "*") -> Optional[List[Dict]]:
    """데이터베이스 쿼리 실행"""
    db = get_db()
    return db.execute_query(table, operation, data, conditions, columns)