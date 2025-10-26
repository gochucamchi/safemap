#!/usr/bin/env python3
"""테스트 데이터 추가"""
from datetime import datetime, timedelta
from app.database.db import SessionLocal, init_db
from app.models.missing_person import MissingPerson

init_db()
db = SessionLocal()

# 기존 데이터 삭제
db.query(MissingPerson).delete()

test_data = [
    {
        "external_id": "M202410250001",
        "missing_date": datetime.now() - timedelta(days=1),
        "location_address": "서울특별시 강남구 역삼동",
        "latitude": 37.5000,
        "longitude": 127.0367,
        "age": 7,
        "gender": "M",
        "location_detail": "청바지, 흰색 티셔츠 착용",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "external_id": "M202410240002",
        "missing_date": datetime.now() - timedelta(days=3),
        "location_address": "서울특별시 송파구 잠실동",
        "latitude": 37.5133,
        "longitude": 127.1028,
        "age": 30,
        "gender": "F",
        "location_detail": "검정 코트, 청바지",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "external_id": "M202410230003",
        "missing_date": datetime.now() - timedelta(days=5),
        "location_address": "경기도 성남시 분당구",
        "latitude": 37.3595,
        "longitude": 127.1052,
        "age": 65,
        "gender": "M",
        "location_detail": "회색 점퍼, 검정 바지",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "external_id": "M202410220004",
        "missing_date": datetime.now() - timedelta(days=7),
        "location_address": "인천광역시 연수구 송도동",
        "latitude": 37.3895,
        "longitude": 126.6386,
        "age": 45,
        "gender": "F",
        "location_detail": "빨간 원피스",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "external_id": "M202410210005",
        "missing_date": datetime.now() - timedelta(days=10),
        "location_address": "서울특별시 마포구 상암동",
        "latitude": 37.5794,
        "longitude": 126.8896,
        "age": 22,
        "gender": "M",
        "location_detail": "파란 후드티, 청바지",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
]

for data in test_data:
    db.add(MissingPerson(**data))

db.commit()
total = db.query(MissingPerson).count()
print(f"✅ 테스트 데이터 추가 완료!")
print(f"📊 총 {total}건의 데이터")
db.close()
