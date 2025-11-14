#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB 마이그레이션 스크립트 - 사진 컬럼 추가
"""

import sqlite3
import os

DB_PATH = "safemap.db"

def migrate_database():
    """사진 관련 컬럼 추가"""
    print(f"🔄 DB 마이그레이션 시작: {DB_PATH}")

    if not os.path.exists(DB_PATH):
        print(f"❌ 데이터베이스 파일이 없습니다: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 기존 컬럼 확인
        cursor.execute("PRAGMA table_info(missing_persons)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 기존 컬럼: {', '.join(columns)}")

        # photo_urls 컬럼 추가
        if 'photo_urls' not in columns:
            cursor.execute("ALTER TABLE missing_persons ADD COLUMN photo_urls TEXT")
            print("✅ photo_urls 컬럼 추가")
        else:
            print("ℹ️  photo_urls 컬럼 이미 존재")

        # photo_count 컬럼 추가
        if 'photo_count' not in columns:
            cursor.execute("ALTER TABLE missing_persons ADD COLUMN photo_count INTEGER DEFAULT 0")
            print("✅ photo_count 컬럼 추가")
        else:
            print("ℹ️  photo_count 컬럼 이미 존재")

        # photos_downloaded 컬럼 추가
        if 'photos_downloaded' not in columns:
            cursor.execute("ALTER TABLE missing_persons ADD COLUMN photos_downloaded DATETIME")
            print("✅ photos_downloaded 컬럼 추가")
        else:
            print("ℹ️  photos_downloaded 컬럼 이미 존재")

        conn.commit()

        # 결과 확인
        cursor.execute("PRAGMA table_info(missing_persons)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"\n📋 업데이트된 컬럼: {', '.join(new_columns)}")

        print("\n✅ 마이그레이션 완료!")

    except Exception as e:
        conn.rollback()
        print(f"❌ 마이그레이션 실패: {e}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
