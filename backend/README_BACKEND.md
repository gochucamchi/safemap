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

✅ 테스트 데이터 5건 추가됨
✅ 데이터베이스 초기화 완료
⏳ 안전Dream API 연동 대기 (Codespaces 네트워크 제한)

## 🔑 안전Dream API 정보

- **API 키**: `4fd2a9d68b504580`
- **발급 ID**: `10000855`
- **엔드포인트**: `https://www.safe182.go.kr/api/lcm/findChildList.do`

### API 연동 방법

**Codespaces에서는 네트워크 제한으로 API 호출 불가**

로컬 PC에서 실행 필요:

```bash
# 로컬 PC에서
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# .env 파일 생성
cat > .env << EOF
SAFE_DREAM_API_KEY=4fd2a9d68b504580
DATABASE_URL=sqlite:///./safemap.db
EOF

# 서버 실행
uvicorn app.main:app --reload

# 데이터 동기화
curl -X POST http://localhost:8000/api/v1/sync/missing-persons
```

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── api/
│   │   └── missing_persons.py   # API 라우터
│   ├── models/
│   │   └── missing_person.py    # 데이터 모델
│   ├── services/
│   │   └── safe_dream_api.py    # 안전Dream API 클라이언트
│   ├── database/
│   │   └── db.py                # 데이터베이스 설정
│   └── main.py                  # FastAPI 앱
├── requirements.txt
├── .env
└── safemap.db                   # SQLite 데이터베이스
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
