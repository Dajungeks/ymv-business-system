import streamlit as st
from app.shared.database import get_db

st.title("데이터베이스 스키마 확인")

db = get_db()

if db and db.supabase:
    st.success("데이터베이스 연결 성공")
    
    # users 테이블 스키마 확인
    try:
        # 실제 users 테이블에서 하나의 레코드를 가져와서 컬럼 확인
        result = db.supabase.table("users").select("*").limit(1).execute()
        
        if result.data:
            st.write("**users 테이블 실제 컬럼:**")
            for key in result.data[0].keys():
                st.write(f"- {key}")
        else:
            st.warning("users 테이블에 데이터가 없습니다.")
            
        # 테이블 정보 직접 확인 (PostgreSQL 시스템 테이블)
        schema_result = db.supabase.rpc("get_table_columns", {"table_name": "users"}).execute()
        
    except Exception as e:
        st.error(f"스키마 확인 오류: {e}")
        
        # 대안: 빈 insert로 컬럼 확인
        try:
            st.write("**대안 방법으로 컬럼 확인 중...**")
            # 의도적으로 빈 데이터로 insert하여 에러 메시지에서 필수 컬럼 확인
            db.supabase.table("users").insert({}).execute()
        except Exception as insert_error:
            st.write(f"Insert 에러 (컬럼 정보 확인용): {insert_error}")

else:
    st.error("데이터베이스 연결 실패")