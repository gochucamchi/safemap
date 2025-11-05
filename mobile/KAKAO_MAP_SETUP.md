# Kakao Maps 지도 기능 설정 가이드

SafeMap의 지도 기능은 Kakao Maps API를 사용합니다.

## 📋 필요한 패키지 설치

```bash
cd mobile
npx expo install react-native-webview
```

## 🔑 Kakao Developers API 키 발급

### 1. Kakao Developers 가입 및 앱 생성
1. [Kakao Developers](https://developers.kakao.com/) 접속
2. 로그인 후 "내 애플리케이션" 메뉴 선택
3. "애플리케이션 추가하기" 클릭
4. 앱 이름 입력 (예: SafeMap) 후 생성

### 2. JavaScript 키 발급
1. 생성한 애플리케이션 선택
2. 좌측 메뉴에서 "앱 키" 선택
3. **"JavaScript 키"** 복사

### 3. 플랫폼 등록 (Web)
1. 좌측 메뉴에서 "플랫폼" 선택
2. "Web 플랫폼 등록" 클릭
3. 사이트 도메인 입력:
   - 개발: `http://localhost:19006`
   - 운영: 실제 도메인 입력

## 🔧 API 키 설정

### MapScreen.tsx 파일 수정

`mobile/src/screens/MapScreen.tsx` 파일을 열고 84번째 줄의 `YOUR_APP_KEY`를 발급받은 JavaScript 키로 교체:

```javascript
// 변경 전
<script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=YOUR_APP_KEY&libraries=clusterer"></script>

// 변경 후 (예시)
<script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=1234567890abcdefghij1234567890ab&libraries=clusterer"></script>
```

## 🗺️ 기능 설명

### 1. 실종자 마커
- 🔴 **빨간색 별 마커**: 실종 중인 사람
- 🟢 **초록색 핀 마커**: 실종 해제된 사람
- 마커 클릭 시 상세 정보 표시

### 2. 위험 지역 표시
지역별 실종 사건 빈도에 따라 원형으로 표시:

- 🔴 **빨간색 원 (고위험)**: 5건 이상 (반경 5km)
- 🟧 **주황색 원 (중위험)**: 3-4건 (반경 4km)
- 🟡 **노란색 원 (저위험)**: 2건 (반경 3km)

### 3. 위험도 계산 알고리즘
```typescript
// 위치 기반 그리드 시스템 (0.05도 ≈ 5km)
- 실종 중인 사람만 계산
- 같은 그리드 내 사건 개수로 위험도 판단
- 2건 이상일 때만 위험 지역으로 표시
```

### 4. 필터 기능
- **탭 필터**: 전체 / 실종 중 / 실종 해제
- **고급 필터**: 날짜, 성별, 나이, 장애 여부

## 🎨 범례
지도 우측 상단에 범례가 표시되어 각 색상의 의미를 확인할 수 있습니다.

## 🐛 문제 해결

### API 키 오류
```
⚠️ Kakao Maps API 키 필요
```
→ MapScreen.tsx의 84번째 줄에서 `YOUR_APP_KEY`를 올바른 키로 교체했는지 확인

### 지도가 표시되지 않음
1. WebView 패키지 설치 확인: `npx expo install react-native-webview`
2. 인터넷 연결 확인
3. Kakao Developers에서 플랫폼이 올바르게 등록되었는지 확인

### 마커가 표시되지 않음
→ 백엔드에서 실종자 데이터에 위도(latitude)와 경도(longitude) 정보가 있는지 확인

## 📊 통계 정보

화면 상단에 다음 정보가 표시됩니다:
- 전체 데이터 개수
- 위치 정보가 있는 데이터 개수
- 실종 중 / 실종 해제 개수
- 위험 지역 개수

## 🚀 추가 개선 아이디어

1. **히트맵 추가**: 실종 사건 밀집도를 색상으로 표시
2. **클러스터링**: 줌 아웃 시 마커를 그룹화
3. **실시간 업데이트**: WebSocket으로 실시간 데이터 갱신
4. **경로 분석**: 연속된 실종 사건의 패턴 분석
5. **알림 기능**: 특정 지역에 새 사건 발생 시 알림

## 📝 참고 문서

- [Kakao Maps API 문서](https://apis.map.kakao.com/web/)
- [Kakao Developers](https://developers.kakao.com/)
- [React Native WebView](https://github.com/react-native-webview/react-native-webview)
