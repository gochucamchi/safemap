# Mobile App Photo Display Feature

## 개요
실종자 목록에서 사람을 클릭하면 상세 정보 모달이 열리며, 사진과 추가 정보를 표시하는 기능

## 구현 내용

### 1. PersonDetailModal 컴포넌트
**파일**: `mobile/src/components/PersonDetailModal.tsx`

**기능**:
- 실종자 사진 표시 (여러 장 지원)
- 사진 네비게이션 (이전/다음)
- 기본 정보 표시 (성별, 나이, 실종일, 상태)
- 위치 정보 표시 (주소, 상세 정보, 좌표)
- 사진이 없는 경우 플레이스홀더 표시

**주요 특징**:
- 이미지 캐러셀: 여러 사진을 좌/우 버튼으로 탐색
- 사진 카운터: 현재 사진/전체 사진 수 표시 (예: "1 / 3")
- 반응형 디자인: 화면 크기에 맞춰 사진 크기 조정
- 스크롤 가능: 정보가 많을 경우 스크롤로 모든 내용 확인

### 2. ListScreen 업데이트
**파일**: `mobile/src/screens/ListScreen.tsx`

**변경사항**:
- `PersonDetailModal` 컴포넌트 import
- 상태 추가: `selectedPerson`, `showDetailModal`
- 핸들러 추가: `handlePersonPress`, `handleCloseDetailModal`
- 카드에 `onPress` 이벤트 추가
- 모달 렌더링 추가

## 사용 방법

### 사용자 경험
1. 앱 실행 → "목록" 탭 선택
2. 실종자 카드 클릭
3. 상세 정보 모달 열림
4. 사진이 있는 경우:
   - 사진 표시
   - 좌/우 버튼으로 다른 사진 보기
   - 사진 번호 확인 (예: "2 / 4")
5. 추가 정보 확인:
   - 기본 정보 (성별, 나이, 실종일, 상태)
   - 위치 정보 (주소, 상세 정보, 좌표)
6. ✕ 버튼 또는 모달 외부 클릭하여 닫기

### 개발자 테스트

#### 1. 백엔드 준비
```bash
# 백엔드 실행 (Codespaces)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 데이터 동기화 (사진 포함)
curl -X POST "http://localhost:8000/api/v1/sync/missing-persons?scrape_photos=true&max_photo_persons=10"
```

#### 2. 모바일 앱 실행
```bash
# 모바일 앱 실행
cd mobile
npm start

# 또는
npx expo start
```

#### 3. API 응답 확인
```bash
# 실종자 목록 조회 (photo_urls, photo_count 필드 확인)
curl "http://localhost:8000/api/v1/missing-persons?limit=5"

# 예상 응답:
{
  "total": 100,
  "items": [
    {
      "id": 1,
      "external_id": "6048080",
      "photo_urls": ["/photos/6048080/photo_0.jpg", "/photos/6048080/photo_1.jpg"],
      "photo_count": 2,
      ...
    }
  ]
}
```

#### 4. 사진 접근 확인
```bash
# 브라우저에서 직접 접근 테스트
# https://nightmarish-vampire-pqxqw7gv7v7hrq7p-8000.app.github.dev/photos/6048080/photo_0.jpg
```

## 데이터 흐름

```
1. ListScreen
   ↓ 사용자가 카드 클릭

2. handlePersonPress(item)
   ↓ selectedPerson = item
   ↓ showDetailModal = true

3. PersonDetailModal 렌더링
   ↓ person.photo_urls 확인

4. 사진 로드
   ↓ <Image source={{ uri: `${API_BASE_URL}${photo_urls[0]}` }} />

5. 백엔드 요청
   ↓ GET https://xxx.github.dev/photos/6048080/photo_0.jpg

6. FastAPI StaticFiles
   ↓ downloaded_photos/6048080/photo_0.jpg 파일 서빙

7. 모바일 앱에 이미지 표시
```

## API 엔드포인트

### GET /api/v1/missing-persons
**응답 필드** (photo 관련):
```json
{
  "photo_urls": ["/photos/{external_id}/photo_0.jpg", ...],
  "photo_count": 2
}
```

### GET /photos/{external_id}/{filename}
**설명**: 정적 파일 서빙 (FastAPI StaticFiles)
**예시**: `/photos/6048080/photo_0.jpg`

## 파일 구조

```
mobile/
├── src/
│   ├── components/
│   │   ├── PersonDetailModal.tsx  ← 새로 추가
│   │   ├── DateFilter.tsx
│   │   └── AdvancedFilterModal.tsx
│   ├── screens/
│   │   ├── ListScreen.tsx         ← 업데이트
│   │   ├── MapScreen.tsx
│   │   └── StatsScreen.js
│   └── services/
│       └── api.js

backend/
├── downloaded_photos/             ← 사진 저장 위치
│   └── {external_id}/
│       ├── photo_0.jpg
│       ├── photo_1.jpg
│       └── ...
└── app/
    └── main.py                    ← StaticFiles 마운트
```

## 트러블슈팅

### 문제 1: 사진이 표시되지 않음
**원인**:
- 백엔드가 실행되지 않음
- 사진 스크랩이 완료되지 않음
- API_BASE_URL이 잘못 설정됨

**해결**:
```bash
# 1. 백엔드 상태 확인
curl http://localhost:8000/api/v1/health

# 2. 사진 스크랩 실행
curl -X POST "http://localhost:8000/api/v1/sync/missing-persons?scrape_photos=true&max_photo_persons=5"

# 3. API_BASE_URL 확인 (mobile/src/services/api.js)
export const API_BASE_URL = 'https://nightmarish-vampire-pqxqw7v7hrq7p-8000.app.github.dev';
```

### 문제 2: 403 Forbidden (Codespaces)
**원인**: GitHub Codespaces 네트워크 제한

**해결**: 로컬 환경에서 실행
```bash
# 로컬에서 백엔드 실행
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# API_BASE_URL을 localhost로 변경
export const API_BASE_URL = 'http://localhost:8000';
```

### 문제 3: 이미지 로딩이 느림
**원인**: 고해상도 이미지

**해결**:
- 이미지 크기 최적화 (향후 개선)
- 로딩 인디케이터 추가 (현재 구현됨)

### 문제 4: 모달이 열리지 않음
**원인**: TypeScript 에러

**해결**:
```bash
# TypeScript 에러 확인
cd mobile
npm run tsc --noEmit

# 에러가 있으면 수정 후 재시작
```

## 향후 개선 사항

1. **이미지 캐싱**: 한 번 로드한 이미지를 캐싱하여 재로드 방지
2. **이미지 최적화**: 썸네일 생성으로 로딩 속도 개선
3. **풀스크린 모드**: 사진을 확대하여 볼 수 있는 기능
4. **스와이프 제스처**: 좌/우 스와이프로 사진 전환
5. **공유 기능**: 실종자 정보를 공유하는 기능
6. **즐겨찾기**: 특정 실종자를 즐겨찾기에 추가

## 참고 자료

- [FastAPI StaticFiles](https://fastapi.tiangolo.com/tutorial/static-files/)
- [React Native Image](https://reactnative.dev/docs/image)
- [Expo Image](https://docs.expo.dev/versions/latest/sdk/image/)
