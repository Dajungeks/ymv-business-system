"""
YMV Business System v4.0 Components Package

컴포넌트 모듈 패키지
- 코드 관리 시스템
- 다국어 입력 지원
"""

from .code_management import CodeManagementComponent
from .multilingual_input import MultilingualInputComponent

__version__ = "4.0.0"
__all__ = [
    "CodeManagementComponent",
    "MultilingualInputComponent"
]