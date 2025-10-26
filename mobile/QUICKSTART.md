# SafeMap 프로젝트 빠른 시작 가이드

## 📋 전체 프로젝트 구조

```
safemap/
├── backend/          # FastAPI 백엔드 서버
└── mobile/           # React Native 모바일 앱
```

## 🚀 Codespaces에서 실행하기

### Step 1: 백엔드 서버 실행

```bash
# 터미널 1
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면:
- `http://localhost:8000/docs` 에서 API 문서 확인
- Codespaces "PORTS" 탭에서 포트 8000을 **Public**으로 설정

### Step 2: 데이터 동기화 (선택사항)

안전Dream API 키가 있다면:

```bash
# 새 터미널 2
cd backend
source venv/bin/activate

# .env 파일 편집
nano .env
# SAFE_DREAM_API_KEY=여기에_API_키_입력

# 데이터 동기화
curl -X POST http://localhost:8000/api/v1/sync/missing-persons
```

### Step 3: React Native 앱 설정 및 실행

```bash
# 새 터미널 3
cd mobile

# 의존성 설치
npm install

# API URL 설정
# src/services/api.js 파일을 열어서
# API_BASE_URL을 Codespaces 포트 8000의 공개 URL로 변경

# 앱 실행
npm start
```

### Step 4: 스마트폰에서 테스트

1. **Expo Go 앱 설치**
   - iOS: App Store에서 "Expo Go"
   - Android: Play Store에서 "Expo Go"

2. **QR 코드 스캔**
   - 터미널에 나타난 QR 코드를 스캔

3. **앱 실행**
   - 앱이 로딩되면 3개 탭 확인:
     - 지도: 실종 사건 위치
     - 목록: 실종 사건 리스트
     - 통계: 통계 및 분석

## ⚠️ 주의사항

### Codespaces 포트 설정
1. 하단 "PORTS" 탭 클릭
2. 포트 8000 찾기
3. 우클릭 → "Port Visibility" → "Public" 선택
4. "Forwarded Address" 열의 URL 복사
5. `mobile/src/services/api.js`의 `API_BASE_URL`에 붙여넣기

### 네트워크 문제
- Codespaces와 스마트폰이 같은 네트워크에 있을 필요는 없습니다
- 포트가 Public으로 설정되어 있으면 인터넷을 통해 접근 가능

### 데이터가 없을 때
백엔드에서 데이터 동기화를 실행하지 않으면 앱에 데이터가 표시되지 않습니다.
테스트용 더미 데이터가 필요하다면 별도로 추가 가능합니다.

## 🎯 개발 워크플로우

### 백엔드 수정 시
1. `backend/app/` 폴더의 파일 수정
2. uvicorn이 자동으로 재시작됨
3. 브라우저에서 `/docs`로 확인

### 프론트엔드 수정 시
1. `mobile/src/` 폴더의 파일 수정
2. Expo가 자동으로 Hot Reload
3. 스마트폰에서 즉시 확인

## 📝 다음 단계

1. **안전Dream API 키 발급**
   - https://www.safe182.go.kr
   - OPEN API 메뉴에서 신청

2. **기능 추가**
   - 필터 기능
   - 푸시 알림
   - 범죄 통계 추가

3. **배포 준비**
   - 프로덕션 데이터베이스 설정
   - API 서버 배포 (AWS, GCP, Heroku)
   - 앱 빌드 및 스토어 출시

## 🆘 문제 해결

### "Cannot connect to server"
→ API URL이 올바른지 확인, 포트가 Public인지 확인

### "No data to display"
→ 백엔드에서 데이터 동기화 실행

### 지도가 안 보임
→ 위치 권한 허용 확인

### Expo 앱이 열리지 않음
→ 같은 WiFi 사용 또는 터널링 사용 (`npx expo start --tunnel`)

## 📞 도움이 필요하면

프로젝트에 이슈를 남겨주세요!
