"""
YMV ERP 시스템 데이터베이스 유틸리티
Database utilities for YMV ERP System
규칙 18: ConnectionWrapper 클래스 구현
"""

import streamlit as st
from datetime import datetime
import logging


class ConnectionWrapper:
    """
    데이터베이스 연결 관리 클래스 (규칙 18)
    Database connection management class
    """
    
    def __init__(self, supabase_client):
        """ConnectionWrapper 초기화"""
        self.client = supabase_client
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """로깅 설정"""
        logger = logging.getLogger('ymv_db')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def execute_query(self, operation, table, data=None, filters=None, columns="*"):
        """
        안전한 쿼리 실행
        Safe query execution with error handling
        """
        try:
            self.logger.info(f"Executing {operation} on table {table}")
            
            if operation == "SELECT":
                return self._execute_select(table, columns, filters)
            elif operation == "INSERT":
                return self._execute_insert(table, data)
            elif operation == "UPDATE":
                return self._execute_update(table, data, filters)
            elif operation == "DELETE":
                return self._execute_delete(table, filters)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            self.logger.error(f"Database operation failed: {str(e)}")
            self._handle_error(operation, table, e)
            return None
    
    def _execute_select(self, table, columns, filters):
        """SELECT 쿼리 실행"""
        query = self.client.table(table).select(columns)
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        response = query.execute()
        return response.data if response.data else []
    
    def _execute_insert(self, table, data):
        """INSERT 쿼리 실행"""
        if not data:
            raise ValueError("Insert data cannot be empty")
        
        response = self.client.table(table).insert(data).execute()
        return response.data if response.data else []
    
    def _execute_update(self, table, data, filters):
        """UPDATE 쿼리 실행"""
        if not data or not filters:
            raise ValueError("Update data and filters are required")
        
        # ID 필드 추출
        id_field = filters.get('id_field', 'id')
        record_id = data.get(id_field)
        
        if not record_id:
            raise ValueError(f"Record ID ({id_field}) is required for update")
        
        # 업데이트 데이터에서 ID 제거
        update_data = data.copy()
        update_data.pop(id_field, None)
        
        response = self.client.table(table).update(update_data).eq(id_field, record_id).execute()
        return response.data if response.data else []
    
    def _execute_delete(self, table, filters):
        """DELETE 쿼리 실행"""
        if not filters:
            raise ValueError("Delete filters are required")
        
        id_field = filters.get('id_field', 'id')
        record_id = filters.get('id')
        
        if not record_id:
            raise ValueError("Record ID is required for delete")
        
        response = self.client.table(table).delete().eq(id_field, record_id).execute()
        return True
    
    def _handle_error(self, operation, table, error):
        """에러 처리 및 사용자 알림"""
        error_msg = f"Database {operation} operation failed on table {table}: {str(error)}"
        self.logger.error(error_msg)
        st.error(f"데이터베이스 작업 실패: {str(error)}")
    
    def get_connection_status(self):
        """연결 상태 확인"""
        try:
            # 간단한 쿼리로 연결 테스트
            response = self.client.table("employees").select("id").limit(1).execute()
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False


class DatabaseOperations:
    """
    데이터베이스 작업 클래스
    Database operations class using ConnectionWrapper
    """
    
    def __init__(self, connection_wrapper):
        """DatabaseOperations 초기화"""
        self.db = connection_wrapper
    
    def load_data(self, table, columns="*", filters=None):
        """
        데이터 로드 (기존 load_data_from_supabase)
        Load data from database table
        """
        try:
            result = self.db.execute_query("SELECT", table, columns=columns, filters=filters)
            return result if result is not None else []
        except Exception as e:
            st.error(f"데이터 로드 실패 ({table}): {str(e)}")
            return []
    
    def save_data(self, table, data):
        """
        데이터 저장 (기존 save_data_to_supabase)
        Save data to database table
        """
        try:
            result = self.db.execute_query("INSERT", table, data=data)
            return len(result) > 0 if result else False
        except Exception as e:
            st.error(f"데이터 저장 실패 ({table}): {str(e)}")
            return False
    
    def update_data(self, table, data, id_field="id"):
        """
        데이터 업데이트 (기존 update_data_in_supabase)
        Update data in database table
        """
        try:
            filters = {'id_field': id_field, 'id': data.get(id_field)}
            result = self.db.execute_query("UPDATE", table, data=data, filters=filters)
            return result is not None and len(result) >= 0
        except Exception as e:
            st.error(f"데이터 업데이트 실패 ({table}): {str(e)}")
            return False
    
    def delete_data(self, table, item_id, id_field="id"):
        """
        데이터 삭제 (기존 delete_data_from_supabase)
        Delete data from database table
        """
        try:
            filters = {'id_field': id_field, 'id': item_id}
            result = self.db.execute_query("DELETE", table, filters=filters)
            return result is True
        except Exception as e:
            st.error(f"데이터 삭제 실패 ({table}): {str(e)}")
            return False
    
    def get_table_info(self, table):
        """테이블 정보 조회"""
        try:
            # 테이블의 첫 번째 레코드로 구조 파악
            result = self.load_data(table, columns="*")
            if result:
                return {
                    'columns': list(result[0].keys()),
                    'record_count': len(result),
                    'sample_record': result[0]
                }
            return {'columns': [], 'record_count': 0, 'sample_record': None}
        except Exception as e:
            st.error(f"테이블 정보 조회 실패 ({table}): {str(e)}")
            return None
    
    def bulk_insert(self, table, data_list):
        """대량 데이터 삽입"""
        try:
            result = self.db.execute_query("INSERT", table, data=data_list)
            return len(result) > 0 if result else False
        except Exception as e:
            st.error(f"대량 삽입 실패 ({table}): {str(e)}")
            return False
    
    def count_records(self, table, filters=None):
        """레코드 수 조회"""
        try:
            result = self.load_data(table, columns="id", filters=filters)
            return len(result) if result else 0
        except Exception as e:
            st.error(f"레코드 수 조회 실패 ({table}): {str(e)}")
            return 0


def create_database_operations(supabase_client):
    """
    DatabaseOperations 인스턴스 생성 헬퍼 함수
    Helper function to create DatabaseOperations instance
    """
    connection_wrapper = ConnectionWrapper(supabase_client)
    return DatabaseOperations(connection_wrapper)


# 하위 호환성을 위한 래퍼 함수들
def load_data_from_supabase(table, columns="*", filters=None, db_ops=None):
    """하위 호환성 래퍼 함수"""
    if db_ops:
        return db_ops.load_data(table, columns, filters)
    else:
        # 임시 처리 - main.py 리팩토링 완료 후 제거 예정
        st.warning("DatabaseOperations 인스턴스가 필요합니다.")
        return []

def save_data_to_supabase(table, data, db_ops=None):
    """하위 호환성 래퍼 함수"""
    if db_ops:
        return db_ops.save_data(table, data)
    else:
        st.warning("DatabaseOperations 인스턴스가 필요합니다.")
        return False

def update_data_in_supabase(table, data, id_field="id", db_ops=None):
    """하위 호환성 래퍼 함수"""
    if db_ops:
        return db_ops.update_data(table, data, id_field)
    else:
        st.warning("DatabaseOperations 인스턴스가 필요합니다.")
        return False

def delete_data_from_supabase(table, item_id, id_field="id", db_ops=None):
    """하위 호환성 래퍼 함수"""
    if db_ops:
        return db_ops.delete_data(table, item_id, id_field)
    else:
        st.warning("DatabaseOperations 인스턴스가 필요합니다.")
        return False