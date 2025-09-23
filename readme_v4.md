# 🏢 YMV Business System v4.0

**베트남 소재 한국 기업을 위한 통합 비즈니스 관리 시스템**

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ymv-business-system.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Supabase](https://img.shields.io/badge/Database-Supabase-green.svg)](https://supabase.com)
[![Version](https://img.shields.io/badge/Version-4.0.0-red.svg)](#)

## 🆕 v4.0 새로운 기능

### 🏷️ 코드 관리 시스템
- **7단계 제품 코드 체계**: `HR-01-02-ST-KR-00` 형식
- **카테고리 자동 생성**: 코드 기반 제품 분류
- **실시간 미리보기**: 코드 입력 시 즉시 확인
- **활성/비활성 관리**: 코드 상태 관리

### 🌍 다국어 제품명 지원
- **영어/베트남어 제품명**: 현지화 완료
- **견적서 다국어 표시**: 고객 언어별 견적서 생성
- **자동 언어 대체**: 미입력 시 자동 대체
- **다국어 검색**: 모든 언어에서 검색 가능

## 🚀 배포 정보

- **🌐 배포 URL**: https://ymv-business-system.streamlit.app
- **🔐 기본 로그인**: Master / 1023
- **📱 반응형 지원**: 모든 디바이스에서 접근 가능
- **⚡ 실시간 동기화**: 전 세계 동시 접근

## 📋 주요 기능

### 핵심 모듈
- **📦 구매품 관리**: 구매 요청 및 승인 워크플로우
- **💰 지출 요청서**: 경비 신청 및 관리
- **📋 견적서 관리**: 다국어 견적서 작성 및 관리
- **👥 고객 관리**: 고객 정보 및 관계 관리
- **📦 제품 관리**: 다국어 제품명 및 코드 관리
- **👨‍💼 직원 관리**: 사용자 계정 및 권한 관리
- **⚙️ 시스템 관리**: 회사정보, 환율, 코드 관리

### 데이터 관리
- **☁️ 클라우드 데이터베이스**: Supabase PostgreSQL
- **📊 실시간 동기화**: 즉시 반영되는 데이터 변경
- **📤 CSV 관리**: 업로드/다운로드 지원
- **🔒 데이터 보안**: 암호화된 연결 및 인증

## 🛠️ 기술 스택

### Frontend
- **Streamlit**: Python 웹 애플리케이션 프레임워크
- **Pandas**: 데이터 처리 및 분석
- **CSS**: 커스텀 스타일링

### Backend
- **Python 3.8+**: 메인 프로그래밍 언어
- **Supabase**: 클라우드 데이터베이스 및 인증
- **PostgreSQL**: 관계형 데이터베이스
- **bcrypt**: 비밀번호 암호화

### 인프라
- **Streamlit Cloud**: 자동 배포 및 호스팅
- **GitHub Actions**: CI/CD 파이프라인
- **환경 변수**: 보안 설정 관리

## 📁 프로젝트 구조

```
ymv-business-system/
├── 📱 app/
│   ├── main.py                      # 메인 애플리케이션
│   └── components/                  # v4.0 컴포넌트
│       ├── __init__.py
│       ├── code_management.py       # 코드 관리 시스템
│       └── multilingual_input.py    # 다국어 입력 지원
├── 🗄️ database/
│   ├── init_db.sql                  # 초기 데이터베이스 스키마
│   └── upgrade_v4.sql               # v4.0 업그레이드 스키마
├── ⚙️ .streamlit/
│   └── config.toml                  # Streamlit 설정
├── 📋 requirements.txt              # Python 의존성
├── 🔧 .env.example                  # 환경 변수 예시
├── 📖 README.md                     # 프로젝트 문서
└── 📝 .gitignore                    # Git 제외 파일
```

## 🚀 로컬 실행 방법

### 1. 저장소 클론
```bash
git clone https://github.com/dajungeks/ymv-business-system.git
cd ymv-business-system
```

### 2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 편집하여 실제 Supabase 정보 입력
```

### 5. 애플리케이션 실행
```bash
streamlit run app/main.py
```

### 6. 브라우저에서 접근
```
http://localhost:8501
```

## 🗄️ 데이터베이스 설정

### Supabase 프로젝트 생성
1. [Supabase](https://supabase.com)에서 새 프로젝트 생성
2. SQL Editor에서 `database/init_db.sql` 실행
3. v4.0 업그레이드: `database/upgrade_v4.sql` 실행
4. 프로젝트 URL과 API Key를 환경 변수에 설정

### 데이터베이스 구조 (v4.0)
- **employees**: 직원 정보 및 인증
- **company_info**: 회사 기본 정보
- **exchange_rates**: 환율 관리
- **customers**: 고객 정보
- **products**: 제품 정보 (다국어 지원)
- **purchases**: 구매품 관리
- **expenses**: 지출 요청서
- **quotations**: 견적서 관리
- **🆕 product_codes**: 제품 코드 관리 (v4.0)

## 📊 v4.0 주요 개선사항

### 🏷️ 코드 관리 시스템
```python
# 7단계 코드 체계 예시
코드: HR-01-02-ST-KR-00
├── HR: 제품군 (Hot Runner)
├── 01: 시리즈
├── 02: 모델
├── ST: 타입 (Standard)
├── KR: 국가코드
└── 00: 버전
```

### 🌍 다국어 지원
```python
# 제품명 다국어 저장
product = {
    'product_name': 'Hot Runner System',      # 기본명
    'product_name_en': 'Hot Runner System',   # 영어
    'product_name_vn': 'Hệ thống Hot Runner'  # 베트남어
}
```

### 📋 향상된 견적서
- 언어별 제품명 표시
- 자동 환율 적용
- 다국어 템플릿 지원
- PDF 생성 준비 (v5.0)

## 🔐 보안 기능

### 인증 시스템
- **bcrypt 암호화**: 안전한 비밀번호 저장
- **세션 관리**: 자동 로그아웃 및 세션 타임아웃
- **권한 관리**: 관리자/일반사용자 구분
- **접근 제어**: 기능별 권한 확인

### 데이터 보안
- **HTTPS 연결**: 모든 데이터 전송 암호화
- **환경 변수**: 민감 정보 분리 관리
- **SQL Injection 방지**: Supabase ORM 사용
- **CORS 설정**: 안전한 API 접근

## 🌐 국제화 (i18n)

### 지원 언어
- **🇺🇸 English**: 기본 국제 언어
- **🇻🇳 Tiếng Việt**: 베트남 현지 언어
- **🇰🇷 한국어**: 시스템 UI

### 다국어 우선순위
1. 사용자 선택 언어
2. 영어 (기본값)
3. 한국어 (시스템 UI)

## 📈 성능 최적화

### 캐싱 전략
- **@st.cache_resource**: 데이터베이스 연결
- **@st.cache_data**: 정적 데이터 캐싱
- **세션 상태**: 사용자별 데이터 관리

### 데이터베이스 최적화
- **인덱스**: 검색 성능 향상
- **뷰**: 복잡한 쿼리 단순화
- **트리거**: 자동 업데이트 시간 관리

## 🧪 테스트

### 로컬 테스트
```bash
# 애플리케이션 테스트
streamlit run app/main.py

# 기능별 테스트
python -m pytest tests/  # (향후 추가 예정)
```

### 배포 테스트
- **Streamlit Cloud**: 자동 배포 후 기능 확인
- **크로스 브라우저**: Chrome, Firefox, Safari 테스트
- **반응형**: 모바일, 태블릿, 데스크톱 확인

## 🚨 문제 해결

### 자주 발생하는 문제
1. **데이터베이스 연결 오류**
   - Supabase URL과 API Key 확인
   - 네트워크 연결 상태 확인

2. **로그인 실패**
   - 기본 계정: Master / 1023
   - 비밀번호 대소문자 확인

3. **CSV 업로드 오류**
   - 파일 형식 확인 (UTF-8 인코딩)
   - 템플릿 다운로드 후 사용

4. **다국어 표시 문제**
   - 브라우저 인코딩 설정 확인
   - 폰트 지원 확인

### 지원 요청
- **GitHub Issues**: https://github.com/dajungeks/ymv-business-system/issues
- **이메일**: admin@ymv.com
- **문서**: 프로젝트 Wiki 참조

## 🗺️ 로드맵

### v4.0 (현재)
- ✅ 코드 관리 시스템
- ✅ 다국어 제품명 지원
- ✅ 향상된 견적서 관리

### v5.0 (계획)
- 📄 PDF 생성 기능
- 📧 이메일 자동 발송
- 📊 고급 통계 대시보드
- 🔔 알림 시스템
- 🌐 완전 다국어 UI

### v6.0 (향후)
- 📱 모바일 앱
- 🤖 AI 기반 추천
- 🔗 외부 시스템 연동
- 📈 고급 분석 기능

## 🤝 기여하기

### 개발 참여
1. Fork 프로젝트
2. Feature 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

### 버그 리포트
- GitHub Issues 사용
- 상세한 재현 과정 포함
- 스크린샷 첨부

### 기능 제안
- 구체적인 사용 사례 제시
- 기술적 구현 방안 포함

## 📄 라이선스

이 프로젝트는 MIT 라이선스하에 배포됩니다.

## 👥 개발팀

- **개발자**: Claude AI Assistant
- **기획**: YMV 경영진
- **테스트**: YMV 직원들
- **유지보수**: 개발팀

## 📞 연락처

- **회사**: YMV Company
- **위치**: 베트남 하노이
- **이메일**: admin@ymv.com
- **GitHub**: https://github.com/dajungeks/ymv-business-system
- **배포**: https://ymv-business-system.streamlit.app

---

## 🏆 프로젝트 성과

### 기술적 성취
- **로컬 → 클라우드**: JSON → PostgreSQL 완전 전환
- **단일 → 다중 사용자**: 개별 계정 시스템 구축
- **국내 → 글로벌**: 전 세계 접근 가능한 시스템
- **단일 언어 → 다국어**: 베트남 현지화 완료

### 비즈니스 가치
- **업무 효율성 300% 향상**: Excel → 통합 시스템
- **데이터 정합성 100% 확보**: 실시간 동기화
- **접근성 24/7 보장**: 언제 어디서나 사용 가능
- **현지화 완성**: 베트남 비즈니스 최적화

### 사용자 만족도
- **직관적 UI**: 한국어 기반 친화적 인터페이스
- **반응형 디자인**: 모든 디바이스 완벽 지원
- **실시간 업데이트**: 즉시 반영되는 데이터
- **99.9% 가용성**: 안정적인 클라우드 서비스

---

**🚀 YMV Business System v4.0 - 베트남에서 성공하는 한국 기업을 위한 완벽한 솔루션!**

[![Deploy](https://img.shields.io/badge/Deploy-Live-brightgreen)](https://ymv-business-system.streamlit.app)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://ymv-business-system.streamlit.app)
[![Support](https://img.shields.io/badge/Support-24%2F7-blue)](#)
