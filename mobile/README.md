# SafeMap Mobile App

실종자 안전지도 모바일 애플리케이션 - React Native (Expo)

## 📱 주요 기능

- **지도 화면**: 실종 사건 발생 위치를 지도에 표시
- **목록 화면**: 최근 실종 사건을 리스트로 확인
- **통계 화면**: 성별/지역별 실종 사건 통계 및 안전 정보

## 🛠 기술 스택

- **React Native**: 0.73
- **Expo**: ~50.0
- **React Navigation**: 네비게이션
- **React Native Maps**: 지도 표시
- **Expo Location**: 위치 서비스
- **Axios**: API 통신

## 📋 요구사항

- Node.js 18 이상
- npm 또는 yarn
- Expo Go 앱 (스마트폰에 설치)
- 백엔드 API 서버 실행 중

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
cd mobile
npm install
```

### 2. 백엔드 API URL 설정

`src/services/api.js` 파일을 열어 API URL을 수정하세요:

**Codespaces에서 실행 중인 경우:**
```javascript
export const API_BASE_URL = 'https://your-codespace-url.app.github.dev';
```

**로컬에서 실행 중인 경우:**
```javascript
export const API_BASE_URL = 'http://localhost:8000';
```

> **중요**: Codespaces 포트 8000의 공개 URL을 확인하려면:
> 1. Codespaces의 "PORTS" 탭 열기
> 2. 포트 8000의 "Forwarded Address" 복사
> 3. `src/services/api.js`의 API_BASE_URL에 붙여넣기

### 3. 앱 실행

```bash
npm start
# 또는
npx expo start
```

### 4. 스마트폰에서 테스트

1. **Expo Go 앱 설치**
   - iOS: App Store에서 "Expo Go" 검색
   - Android: Google Play에서 "Expo Go" 검색

2. **QR 코드 스캔**
   - iOS: 카메라 앱으로 터미널의 QR 코드 스캔
   - Android: Expo Go 앱에서 "Scan QR Code" 탭

3. **앱 로딩 대기**
   - 첫 실행은 시간이 걸릴 수 있습니다

## 📱 화면 구성

### 1. 지도 화면 (Map)
- 실종 사건 위치를 빨간 마커로 표시
- 현재 위치 표시
- 마커 클릭 시 상세 정보 팝업

### 2. 목록 화면 (List)
- 최신순으로 실종 사건 나열
- 날짜, 위치, 성별/나이 정보 표시
- Pull-to-refresh로 새로고침

### 3. 통계 화면 (Stats)
- 최근 30일 통계
- 성별 비율
- 상위 발생 지역
- 안전 수칙 정보

## 🔧 개발 팁

### 빠른 새로고침
개발 중 코드를 수정하면 자동으로 앱이 새로고침됩니다.

### 개발자 메뉴
- iOS: 기기를 흔들기
- Android: 기기를 흔들거나 `adb shell input keyevent 82`

### 로그 확인
```bash
npx expo start
# 터미널에서 로그 확인 가능
```

### 앱 리셋
문제가 생기면 캐시를 지우고 재시작:
```bash
npx expo start -c
```

## 🐛 문제 해결

### 문제: "Unable to connect to server"
**해결책:**
1. 백엔드 서버가 실행 중인지 확인
2. API URL이 올바른지 확인
3. Codespaces 포트가 공개(Public)로 설정되어 있는지 확인

### 문제: 지도가 표시되지 않음
**해결책:**
1. 위치 권한이 허용되었는지 확인
2. Google Maps API 키 설정 확인 (Android)
3. 인터넷 연결 확인

### 문제: 데이터가 표시되지 않음
**해결책:**
1. 백엔드에서 데이터 동기화 실행:
   ```bash
   curl -X POST http://localhost:8000/api/v1/sync/missing-persons
   ```
2. 앱에서 Pull-to-refresh

## 📁 프로젝트 구조

```
mobile/
├── App.js                      # 메인 앱 & 네비게이션
├── app.json                    # Expo 설정
├── package.json
├── babel.config.js
└── src/
    ├── screens/                # 화면 컴포넌트
    │   ├── MapScreen.js       # 지도 화면
    │   ├── ListScreen.js      # 목록 화면
    │   └── StatsScreen.js     # 통계 화면
    └── services/
        └── api.js             # API 통신
```

## 🔐 API 연동

백엔드 API 엔드포인트:
- `GET /api/v1/missing-persons` - 실종자 목록
- `GET /api/v1/missing-persons/stats` - 통계
- `GET /api/v1/safety-facilities` - 안전시설

## 🚀 배포 (추후)

### iOS App Store
```bash
expo build:ios
```

### Android Play Store
```bash
expo build:android
```

## 📝 다음 개발 예정

- [ ] 필터 기능 (날짜, 지역, 성별)
- [ ] 실종 경보 푸시 알림
- [ ] 안전시설 마커 표시
- [ ] 범죄 통계 데이터 추가
- [ ] 다크 모드 지원
- [ ] 오프라인 캐싱

## 🤝 기여

이슈나 풀 리퀘스트는 언제든 환영합니다!

## 📄 라이선스

교육 및 비상업적 목적으로 개발되었습니다.
데이터 출처: 경찰청 안전Dream
