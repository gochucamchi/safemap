# SafeMap 백엔드 서버

## 🚀 빠른 시작

### 1. 백엔드 서버 실행

```bash
cd /workspaces/safemap/backend
source venv/bin/activate  # 또는 . venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. API 확인

브라우저에서:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/api/v1/missing-persons (데이터 확인)

### 3. 데이터 확인

```bash
# 실종자 목록
curl http://localhost:8000/api/v1/missing-persons

# 통계
curl http://localhost:8000/api/v1/missing-persons/stats
```

## 📊 현재 상태

✅ 자동 데이터 동기화 (30분마다)
✅ 자동 사진 스크랩 (시작 시 + 30분마다)
✅ 데이터베이스 초기화 완료
✅ 안전Dream API 연동 완료

## 🔑 안전Dream API 정보

- **API 키**: `4fd2a9d68b504580`
- **발급 ID**: `10000855`
- **엔드포인트**: `https://www.safe182.go.kr/api/lcm/findChildList.do`

### 자동 동기화 (서버 시작 시)

백엔드 서버가 시작되면 **자동으로 다음 작업이 실행됩니다**:

1. **데이터 동기화**: 안전Dream API에서 최신 실종자 정보 가져오기
2. **사진 스크랩**: 사진이 없는 실종자들의 사진 다운로드 (최대 100명)
3. **정기 갱신**: 30분마다 위 작업 반복

```bash
# 서버만 켜면 자동으로 실행됩니다!
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 출력 예시:
# ✅ Database initialized
# 🔄 Initializing auto-sync service...
# ✅ Auto-sync enabled (30-minute interval)
# 📊 현재 DB: 250건
# 📸 사진 스크랩: 45명 성공, 178장 다운로드
```

### 수동 동기화 (필요 시)

자동 동기화 외에 수동으로 즉시 동기화도 가능합니다:

```bash
# 간단한 방법 (사진 포함)
curl -X POST "http://localhost:8000/api/v1/sync/trigger"

# 사진 제외하고 데이터만
curl -X POST "http://localhost:8000/api/v1/sync/trigger?scrape_photos=false"

# 사진 인원수 조정
curl -X POST "http://localhost:8000/api/v1/sync/trigger?max_photo_persons=200"
```

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── api/
│   │   └── missing_persons.py      # API 라우터
│   ├── models/
│   │   └── missing_person.py       # 데이터 모델
│   ├── services/
│   │   ├── safe_dream_api.py       # 안전Dream API 클라이언트
│   │   ├── data_sync_service.py    # 데이터 동기화 서비스
│   │   └── photo_scraper_service.py # 사진 스크랩 서비스
│   ├── database/
│   │   └── db.py                   # 데이터베이스 설정
│   └── main.py                     # FastAPI 앱 (자동 동기화)
├── downloaded_photos/              # 다운로드된 사진 저장
│   └── {실종자_ID}/
│       ├── photo_0.jpg
│       ├── photo_1.jpg
│       └── ...
├── requirements.txt
├── .env
└── safemap.db                      # SQLite 데이터베이스
```

## 🔧 문제 해결

### 데이터가 없을 때

```bash
python add_test_data.py
```

### 데이터베이스 초기화

```bash
rm safemap.db
python -c "from app.database.db import init_db; init_db()"
python add_test_data.py
```

## 📝 API 엔드포인트

- `GET /api/v1/health` - 헬스 체크
- `GET /api/v1/missing-persons` - 실종자 목록
- `GET /api/v1/missing-persons/stats` - 통계
- `POST /api/v1/sync/missing-persons` - 안전Dream API 동기화
