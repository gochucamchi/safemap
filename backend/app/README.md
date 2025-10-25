# SafeMap Backend API

실종자 안전지도 프로젝트의 백엔드 API 서버입니다. 안전Dream OPEN API를 활용하여 실종자 정보와 안전시설 정보를 제공합니다.

## 🚀 주요 기능

- 실종자 정보 조회 및 필터링
- 실종 사건 통계 제공
- 안전시설 위치 정보 제공
- 안전Dream API 데이터 동기화
- 지도 시각화를 위한 REST API

## 📋 요구사항

- Python 3.9+
- PostgreSQL 또는 SQLite (개발용)
- 안전Dream API 키

## 🛠 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일을 열어 필요한 정보 입력:

```env
SAFE_DREAM_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./safemap.db
```

### 4. 안전Dream API 키 발급

1. [안전Dream 웹사이트](https://www.safe182.go.kr) 접속
2. OPEN API 메뉴 > API 키 발급 신청
3. 발급받은 키를 `.env` 파일에 입력

### 5. 서버 실행

```bash
# 방법 1: uvicorn 직접 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 방법 2: Python 모듈로 실행
python -m app.main
```

서버가 실행되면 다음 주소에서 확인 가능:
- API 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API 루트: http://localhost:8000/

## 📡 API 엔드포인트

### 실종자 정보

- `GET /api/v1/missing-persons` - 실종자 목록 조회
  - Query Parameters:
    - `skip`: 건너뛸 레코드 수 (기본값: 0)
    - `limit`: 최대 레코드 수 (기본값: 100, 최대: 500)
    - `start_date`: 실종일 시작 (YYYY-MM-DD)
    - `end_date`: 실종일 종료 (YYYY-MM-DD)
    - `gender`: 성별 필터 (M/F)

- `GET /api/v1/missing-persons/stats` - 실종 사건 통계
  - Query Parameters:
    - `days`: 최근 N일간의 통계 (기본값: 30)

### 안전시설

- `GET /api/v1/safety-facilities` - 안전시설 목록 조회
  - Query Parameters:
    - `skip`: 건너뛸 레코드 수
    - `limit`: 최대 레코드 수
    - `facility_type`: 시설 유형 필터

### 데이터 동기화

- `POST /api/v1/sync/missing-persons` - 안전Dream API에서 최신 데이터 동기화

### 상태 확인

- `GET /api/v1/health` - 서버 상태 확인
- `GET /api/info` - API 정보

## 📊 데이터베이스

### 개발 환경
SQLite 사용 (파일 기반 DB, 별도 설치 불필요)

### 프로덕션 환경
PostgreSQL 권장

PostgreSQL 설정:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/safemap_db
```

### 데이터베이스 초기화

서버 첫 실행 시 자동으로 테이블이 생성됩니다.

## 🔄 데이터 동기화

안전Dream API에서 최신 데이터를 가져오려면:

```bash
curl -X POST http://localhost:8000/api/v1/sync/missing-persons
```

또는 주기적으로 실행하는 크론잡 설정 가능.

## 📝 예제 요청

### 1. 최근 30일 실종자 조회

```bash
curl "http://localhost:8000/api/v1/missing-persons?start_date=2025-10-01&end_date=2025-10-25"
```

### 2. 통계 조회

```bash
curl "http://localhost:8000/api/v1/missing-persons/stats?days=30"
```

### 3. 안전시설 조회

```bash
curl "http://localhost:8000/api/v1/safety-facilities?limit=50"
```

## 🏗 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 메인 앱
│   ├── config.py            # 설정
│   ├── models/              # 데이터베이스 모델
│   │   ├── __init__.py
│   │   └── missing_person.py
│   ├── services/            # 비즈니스 로직
│   │   ├── __init__.py
│   │   └── safe_dream_api.py
│   ├── api/                 # API 라우터
│   │   ├── __init__.py
│   │   └── missing_persons.py
│   └── database/            # DB 설정
│       ├── __init__.py
│       └── db.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🔐 보안 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- API 키는 안전하게 보관하세요
- 프로덕션 환경에서는 HTTPS 사용 필수
- CORS 설정을 프로덕션 환경에 맞게 조정하세요

## 📄 라이선스

이 프로젝트는 교육 및 비상업적 목적으로 개발되었습니다.
데이터 출처: 경찰청 안전Dream

## 🤝 기여

이슈나 풀 리퀘스트는 언제든 환영합니다!

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
