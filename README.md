# 동서대학교 공지사항 알림 시스템

실시간으로 동서대학교 공지사항을 크롤링하고 웹 푸시 알림을 통해 사용자에게 새로운 공지사항을 알려주는 시스템입니다.

## 🚀 주요 기능

### ✅ 핵심 기능
- **실시간 공지사항 크롤링**: 동서대학교 웹사이트에서 자동으로 공지사항 수집
- **웹 푸시 알림**: OneSignal을 통한 실시간 알림 서비스
- **검색 및 필터링**: 공지사항 제목, 작성자 기반 검색
- **반응형 디자인**: 모바일/데스크톱 완벽 지원

### ⭐ 시연용 기능
- **시연용 관리 페이지**: `/demo` 경로로 접속 가능
- **임시 공지사항 생성**: 클릭 한 번으로 새 공지사항 + 자동 알림 발송
- **테스트 알림 발송**: 커스텀 제목/내용으로 알림 테스트
- **데이터 정리**: 시연용 공지사항 일괄 삭제
- **시스템 상태 모니터링**: OneSignal 연결 상태 실시간 확인

## 🛠️ 기술 스택

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite
- **Push Notification**: OneSignal
- **Web Crawling**: BeautifulSoup4, Requests
- **Deployment**: Render.com

## 📦 설치 및 실행

### 로컬 개발 환경

1. **프로젝트 클론**
   ```bash
   git clone <repository-url>
   cd dongseo_fixed_complete
   ```

2. **가상환경 생성 및 활성화**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **환경 변수 설정** (선택사항)
   ```bash
   # .env 파일 생성
   ONESIGNAL_APP_ID=412bf56c-7f9d-48a5-9bb1-ced8f7f93755
   ONESIGNAL_REST_API_KEY=your_rest_api_key_here
   ```

5. **애플리케이션 실행**
   ```bash
   python src/main.py
   ```

6. **브라우저에서 확인**
   - 메인 페이지: http://localhost:5000
   - 시연용 관리 페이지: http://localhost:5000/demo

### Render.com 배포

1. **GitHub 리포지토리 연결**
   - Render.com에서 "New Web Service" 선택
   - GitHub 리포지토리 연결

2. **배포 설정**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn src.main:app`
   - **Environment**: Python 3

3. **환경 변수 설정**
   | 변수명 | 값 |
   |--------|-----|
   | `ONESIGNAL_APP_ID` | `412bf56c-7f9d-48a5-9bb1-ced8f7f93755` |
   | `ONESIGNAL_REST_API_KEY` | OneSignal에서 발급받은 REST API Key |

## 🎬 시연 가이드

### 시연 시나리오 (총 3-4분)

1. **웹사이트 소개** (30초)
   - 실시간 공지사항 크롤링 확인
   - 검색/필터링 기능 시연

2. **알림 구독** (1분)
   - "알림 구독하기" 버튼 클릭
   - 브라우저 알림 권한 허용
   - 구독 완료 확인

3. **핵심 시연** (1분 30초)
   - 시연용 관리 페이지 접속 (`/demo`)
   - "공지사항 생성 및 알림 발송" 클릭
   - **브라우저 푸시 알림 팝업 확인** ⭐ (가장 중요!)
   - 메인 페이지에서 새 공지사항 확인

4. **추가 테스트** (30초)
   - 커스텀 알림 발송 테스트
   - 데이터 정리

### 촬영 팁

- **브라우저**: Chrome 또는 Edge 사용 (OneSignal 최적화)
- **중요**: 알림 팝업이 나타나는 순간을 놓치지 마세요!
- **음성 해설**: 각 단계별로 설명하며 진행
- **속도**: 너무 빠르지 않게, 시청자가 따라올 수 있는 속도로

## 🔧 문제 해결

### 알림이 오지 않는 경우
1. 브라우저 새로고침 후 재시도
2. 시크릿 모드가 아닌 일반 모드 사용
3. 브라우저 알림 설정 확인
4. OneSignal REST API Key 설정 확인

### 크롤링이 안 되는 경우
1. 동서대학교 웹사이트 접속 확인
2. 네트워크 연결 상태 확인
3. 새로고침 버튼 클릭

### 로컬 개발 환경 오류
1. 가상환경 활성화 확인
2. 의존성 재설치: `pip install -r requirements.txt`
3. Python 버전 확인 (3.8 이상 권장)

## 📁 프로젝트 구조

```
dongseo_fixed_complete/
├── src/
│   ├── main.py              # Flask 메인 애플리케이션
│   ├── crawler.py           # 웹 크롤링 모듈
│   ├── notification_service.py  # 알림 서비스
│   ├── templates/
│   │   ├── index.html       # 메인 페이지
│   │   └── demo.html        # 시연용 관리 페이지
│   ├── static/
│   │   ├── css/style.css    # 스타일시트
│   │   └── js/script.js     # JavaScript
│   └── schema.sql           # 데이터베이스 스키마
├── OneSignalSDKWorker.js    # OneSignal 워커 파일
├── requirements.txt         # Python 의존성
├── Procfile                # 배포 설정
├── README.md               # 프로젝트 문서
└── .gitignore              # Git 무시 파일
```

## 🌐 API 엔드포인트

- `GET /` - 메인 페이지
- `GET /demo` - 시연용 관리 페이지
- `GET /api/notices` - 공지사항 조회 API
- `GET /api/update` - 공지사항 업데이트 API
- `GET /api/onesignal/status` - OneSignal 상태 확인 API
- `POST /api/demo/create-notice` - 시연용 공지사항 생성 API
- `POST /api/demo/send-notification` - 테스트 알림 발송 API
- `POST /api/demo/clear` - 시연용 공지사항 삭제 API

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

## 👥 개발팀

동서대학교 공지사항 알림 시스템 개발팀

---

**최종 업데이트**: 2024년 6월

