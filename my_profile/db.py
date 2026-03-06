import os
import psycopg2
import psycopg2.extras
from flask import g


def get_db():
    """현재 요청에 대한 DB 연결을 반환 (Flask g 객체에 캐싱)"""
    if "db" not in g:
        g.db = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ.get("DB_NAME", "knu_open"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "postgres"),
        )
        g.db.autocommit = True
    return g.db


def close_db(e=None):
    """요청 종료 시 DB 연결 닫기"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """schema.sql을 실행하여 테이블 초기화"""
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r") as f:
            cur.execute(f.read())
        cur.close()


def query_db(query, args=(), one=False):
    """SQL 쿼리 실행 후 딕셔너리 형태로 결과 반환"""
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query, args)
    if query.strip().upper().startswith("SELECT"):
        rv = cur.fetchall()
        cur.close()
        if one:
            return rv[0] if rv else None
        return rv
    else:
        cur.close()
        return None
