# app/config/settings.py
import os
from typing import Dict, Any

class Settings:
    """애플리케이션 설정 클래스"""
    
    # 애플리케이션 정보
    APP_NAME = "YMV Business Management System"
    APP_VERSION = "1.0.0"
    DEBUG = True
    
    # 보안 설정
    SECRET_KEY = "ymv-secret-key-change-in-production"
    
    # 파일 업로드 설정
    MAX_FILE_SIZE = 10485760  # 10MB
    ALLOWED_EXTENSIONS = ['csv', 'xlsx', 'xls', 'pdf', 'png', 'jpg', 'jpeg']
    
    # 디렉토리 설정
    UPLOAD_DIR = 'uploads'
    EXPORT_DIR = 'exports'
    LOG_DIR = 'logs'
    FONT_DIR = 'fonts'
    
    # 페이지네이션
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 다국어 설정
    SUPPORTED_LANGUAGES = ['ko', 'en', 'vn']
    DEFAULT_LANGUAGE = 'ko'
    
    # 통화 설정
    SUPPORTED_CURRENCIES = ['USD', 'VND', 'KRW', 'CNY', 'THB', 'JPY', 'EUR']
    DEFAULT_CURRENCY = 'USD'
    
    # 데이터베이스 설정 (나중에 Supabase 연결 시 사용)
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """모든 설정을 딕셔너리로 반환"""
        return {
            'app_name': cls.APP_NAME,
            'app_version': cls.APP_VERSION,
            'debug': cls.DEBUG,
            'max_file_size': cls.MAX_FILE_SIZE,
            'allowed_extensions': cls.ALLOWED_EXTENSIONS,
            'supported_languages': cls.SUPPORTED_LANGUAGES,
            'default_language': cls.DEFAULT_LANGUAGE,
            'supported_currencies': cls.SUPPORTED_CURRENCIES,
            'default_currency': cls.DEFAULT_CURRENCY,
        }

# 전역 설정 인스턴스
settings = Settings()