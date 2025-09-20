"""
YMV 비즈니스 관리 시스템
Streamlit Cloud 배포용 메인 엔트리 포인트
"""

import streamlit as st
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Streamlit 페이지 설정
st.set_page_config(
    page_title="YMV 비즈니스 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 메인 앱 실행
if __name__ == "__main__":
    try:
        # app.main 모듈 전체를 import하고 main 함수 실행
        import app.main as main_module
        main_module.main()
    except ImportError as e:
        st.error(f"모듈 임포트 오류: {e}")
        st.error("app/main.py 파일이 존재하는지 확인해주세요.")
    except Exception as e:
        st.error(f"애플리케이션 실행 오류: {e}")
        st.error("로그를 확인하고 개발자에게 문의해주세요.")