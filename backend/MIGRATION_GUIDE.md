# 📚 SafeMap 데이터베이스 마이그레이션 가이드

## 🎯 Alembic이란?
데이터베이스 스키마 변경을 안전하게 관리하는 도구입니다.
- ✅ 더 이상 DB 삭제하고 재생성 안 해도 됨
- ✅ 스키마 변경 이력 추적 가능
- ✅ 팀원과 스키마 동기화 쉬움
- ✅ PostgreSQL 전환 시에도 그대로 사용

---

## 📦 현재 상태 (SQLite + Alembic)

```bash
# 설치 완료
pip install alembic==1.13.1 psycopg2-binary==2.9.9

# 초기 마이그레이션 생성 완료
alembic revision --autogenerate -m "Initial schema"
```

---

## 🚀 기본 사용법

### 1️⃣ 모델 변경 시 (예: 새 컬럼 추가)

```python
# app/models/missing_person.py
class MissingPerson(Base):
    # ... 기존 필드들 ...

    # 새 필드 추가
    blood_type = Column(String, nullable=True)  # 혈액형
```

### 2️⃣ 마이그레이션 생성

```bash
cd backend
alembic revision --autogenerate -m "Add blood_type column"
```

### 3️⃣ 마이그레이션 적용

```bash
alembic upgrade head
```

**완료!** DB에 새 컬럼이 추가되었고, 기존 데이터는 보존됩니다.

---

## 📝 주요 명령어

```bash
# 현재 마이그레이션 버전 확인
alembic current

# 마이그레이션 이력 확인
alembic history

# 최신 버전으로 업그레이드
alembic upgrade head

# 한 단계 업그레이드
alembic upgrade +1

# 한 단계 다운그레이드 (롤백)
alembic downgrade -1

# 특정 버전으로 다운그레이드
alembic downgrade <revision_id>
```

---

## 🔄 PostgreSQL로 전환하기 (배포 전)

### Step 1: Docker Compose로 PostgreSQL 설정

`docker-compose.yml` 파일 생성:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: safemap-db
    environment:
      POSTGRES_DB: safemap
      POSTGRES_USER: safemap_user
      POSTGRES_PASSWORD: your_secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Step 2: PostgreSQL 시작

```bash
docker-compose up -d
```

### Step 3: 환경 변수 변경

`.env` 파일:

```bash
# SQLite (현재)
# DATABASE_URL=sqlite:///./safemap.db

# PostgreSQL (전환 후)
DATABASE_URL=postgresql://safemap_user:your_secure_password@localhost:5432/safemap
```

### Step 4: 마이그레이션 실행

```bash
# PostgreSQL에 테이블 생성
alembic upgrade head
```

### Step 5: 데이터 마이그레이션 (선택사항)

SQLite에서 PostgreSQL로 데이터 이동이 필요하면:

```bash
# 1. SQLite 데이터 덤프
python scripts/export_sqlite_data.py > data.json

# 2. PostgreSQL로 import
python scripts/import_to_postgres.py data.json
```

---

## 🛠️ 일반적인 시나리오

### 시나리오 1: 새 필드 추가

```bash
# 1. 모델 수정 (missing_person.py)
# 2. 마이그레이션 생성
alembic revision --autogenerate -m "Add new field"
# 3. 적용
alembic upgrade head
```

### 시나리오 2: 필드 타입 변경

```bash
# 1. 모델 수정
# 2. 마이그레이션 생성
alembic revision --autogenerate -m "Change field type"
# 3. 생성된 마이그레이션 파일 확인 및 수정 (필요 시)
# 4. 적용
alembic upgrade head
```

### 시나리오 3: 테이블 추가

```bash
# 1. 새 모델 클래스 생성
# 2. env.py에 import 추가 (autogenerate가 감지하도록)
# 3. 마이그레이션 생성
alembic revision --autogenerate -m "Add new table"
# 4. 적용
alembic upgrade head
```

### 시나리오 4: 실수했을 때 롤백

```bash
# 마지막 마이그레이션 취소
alembic downgrade -1

# 마이그레이션 파일 삭제 또는 수정

# 다시 적용
alembic upgrade head
```

---

## ⚠️ 주의사항

1. **프로덕션에서는 백업 먼저!**
   ```bash
   # SQLite 백업
   cp safemap.db safemap_backup_$(date +%Y%m%d).db

   # PostgreSQL 백업
   pg_dump safemap > backup_$(date +%Y%m%d).sql
   ```

2. **마이그레이션 파일은 git에 커밋**
   - `alembic/versions/*.py` 파일은 반드시 커밋
   - 팀원과 스키마 동기화에 필수

3. **Autogenerate 확인**
   - `--autogenerate`는 완벽하지 않음
   - 생성된 마이그레이션 파일을 항상 확인

4. **Down 마이그레이션 작성**
   - `upgrade()`뿐만 아니라 `downgrade()`도 작성
   - 롤백 가능하게 유지

---

## 🎓 학습 자료

- [Alembic 공식 문서](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)

---

## 🤝 팀 협업 워크플로우

```bash
# 1. 팀원이 스키마 변경
git pull

# 2. 새 마이그레이션 확인
alembic history

# 3. 로컬 DB 업데이트
alembic upgrade head

# 4. 서버 재시작
uvicorn app.main:app --reload
```

---

## 📞 문제 해결

### "Target database is not up to date" 에러

```bash
# 현재 버전 확인
alembic current

# 최신으로 업그레이드
alembic upgrade head
```

### "Can't locate revision identified by..." 에러

```bash
# 마이그레이션 히스토리 확인
alembic history

# DB 버전 테이블 확인
sqlite3 safemap.db "SELECT * FROM alembic_version"

# 필요 시 수동으로 버전 설정
alembic stamp head
```

### 마이그레이션 충돌

```bash
# 마이그레이션 병합
alembic merge heads -m "Merge branches"
```

---

**✅ 이제 스키마 변경이 쉬워졌습니다!**
