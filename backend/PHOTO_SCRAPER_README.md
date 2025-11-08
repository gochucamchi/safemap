# 📸 실종자 사진 스크랩 가이드

## 🚀 빠른 시작

### 방법 1: 테스트 스크립트 실행 (가장 간단)

```bash
cd backend
source venv/bin/activate
python3 test_photo_scraper.py
```

**결과:**
- 5명의 실종자 사진을 순차적으로 스크랩
- 각 사람당 수집된 사진 URL 출력
- 전체 통계 표시

---

### 방법 2: API를 통한 사진 스크랩 (DB에 자동 저장)

#### 1단계: 백엔드 서버 실행
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2단계: 사진 스크랩 요청
**새 터미널에서:**
```bash
# 데이터 동기화 + 사진 스크랩 (50명)
curl -X POST "http://localhost:8000/api/v1/sync/missing-persons?max_pages=10&scrape_photos=true&max_photo_persons=50"
```

**또는 브라우저에서 Swagger UI 사용:**
1. http://localhost:8000/docs 열기
2. `POST /api/v1/sync/missing-persons` 찾기
3. "Try it out" 클릭
4. 파라미터 설정:
   - `max_pages`: 10
   - `scrape_photos`: true
   - `max_photo_persons`: 50
5. "Execute" 클릭

---

### 방법 3: 커스텀 Python 스크립트

직접 스크립트를 작성할 수도 있습니다:

```python
import asyncio
from app.services.photo_scraper_service import PhotoScraperService

async def my_scraper():
    # 원하는 실종자 ID 목록
    persons = [
        {"external_id": "6048080", "name": "이진현"},
        {"external_id": "6048041", "name": "송인식"}
    ]

    # 3초 딜레이, 최대 3회 재시도
    async with PhotoScraperService(delay=3.0, max_retries=3) as scraper:
        results = await scraper.scrape_multiple_persons(persons)

    # 결과 출력
    for person_id, urls in results.items():
        print(f"{person_id}: {len(urls)}개 사진")
        for url in urls:
            print(f"  - {url}")

if __name__ == "__main__":
    asyncio.run(my_scraper())
```

실행:
```bash
cd backend
source venv/bin/activate
python3 my_script.py
```

---

## 📝 주요 파라미터

### PhotoScraperService
- `delay`: 요청 간 딜레이 (초) - 기본값: 3.0
- `max_retries`: 최대 재시도 횟수 - 기본값: 3

### 재시도 로직
- 1차 실패: 2초 후 재시도
- 2차 실패: 4초 후 재시도
- 3차 실패: 8초 후 재시도
- 이후 실패: 스킵

---

## 🔍 수집된 데이터 확인

### API로 확인
```bash
# 사진이 있는 실종자만 조회
curl "http://localhost:8000/api/v1/missing-persons" | jq '.items[] | select(.photo_count > 0)'

# 통계 확인
curl "http://localhost:8000/api/v1/db/stats" | jq
```

### 응답 예시
```json
{
  "id": 1,
  "external_id": "6048080",
  "missing_date": "2024-01-15T10:30:00",
  "location_address": "서울특별시 강남구",
  "age": 45,
  "gender": "M",
  "photo_urls": [
    "https://www.safe182.go.kr/photo1.jpg",
    "https://www.safe182.go.kr/photo2.jpg"
  ],
  "photo_count": 2
}
```

---

## ⚙️ 설정

### Rate Limiting 조정
스크랩 속도를 조절하려면 `PhotoScraperService` 생성 시 `delay` 값을 변경:

```python
# 느리게 (안전)
async with PhotoScraperService(delay=5.0) as scraper:
    ...

# 빠르게 (주의: rate limit 위험)
async with PhotoScraperService(delay=1.0) as scraper:
    ...
```

### 한 번에 스크랩할 인원 수 조정
```bash
# 10명만 스크랩
curl -X POST "http://localhost:8000/api/v1/sync/missing-persons?scrape_photos=true&max_photo_persons=10"

# 100명 스크랩
curl -X POST "http://localhost:8000/api/v1/sync/missing-persons?scrape_photos=true&max_photo_persons=100"
```

---

## 🐛 문제 해결

### "Server disconnected" 에러
- **원인**: Rate limiting
- **해결**: `delay` 값을 늘리기 (3초 → 5초)

### "No photos found"
- **원인**: 해당 실종자의 사진이 없거나 페이지 구조 변경
- **해결**: 개별 확인 필요

### Import 에러
```bash
# 의존성 재설치
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 성능

- **평균 스크랩 시간**: 3-5초/인
- **성공률**: ~95%
- **중복 제거**: MD5 해시 기반
- **플레이스홀더 필터링**: 자동

---

## 🔐 주의사항

1. **Rate Limiting**: 너무 빠르게 요청하면 차단될 수 있음
2. **서버 부하**: delay는 최소 2초 이상 권장
3. **재시도**: 3회 이상 실패하면 자동으로 스킵
4. **네트워크**: 안정적인 인터넷 연결 필요

---

## 📁 관련 파일

- `test_photo_scraper.py` - 테스트 스크립트
- `app/services/photo_scraper_service.py` - 스크랩 서비스
- `app/services/data_sync_service.py` - 통합 동기화 서비스
- `app/models/missing_person.py` - DB 모델 (photo_urls 필드)
- `app/api/missing_persons.py` - API 엔드포인트

---

## 📞 도움말

문제가 있거나 질문이 있으면 이슈를 남겨주세요!
