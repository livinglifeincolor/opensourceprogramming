import os

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db, close_db, init_db, query_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3000"],
)

app.teardown_appcontext(close_db)


# ──────────────────────── Health Check ────────────────────────


@app.route("/")
def index():
    return jsonify({"message": "Welcome to My Development Journal API!"})


# ──────────────────────── Auth Routes ─────────────────────────


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    # 유효성 검사
    if not username or not email or not password:
        return jsonify({"error": "모든 필드를 입력해주세요."}), 400

    if len(password) < 6:
        return jsonify({"error": "비밀번호는 6자 이상이어야 합니다."}), 400

    # 중복 확인
    existing = query_db(
        "SELECT id FROM users WHERE email = %s OR username = %s",
        (email, username),
        one=True,
    )
    if existing:
        return jsonify({"error": "이미 사용 중인 이메일 또는 사용자명입니다."}), 409

    # 사용자 생성
    password_hash = generate_password_hash(password)
    query_db(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
        (username, email, password_hash),
    )

    return jsonify({"message": "회원가입이 완료되었습니다."}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "이메일과 비밀번호를 입력해주세요."}), 400

    user = query_db(
        "SELECT id, username, email, password_hash FROM users WHERE email = %s",
        (email,),
        one=True,
    )

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401

    # 세션에 사용자 정보 저장
    session["user_id"] = user["id"]
    session["username"] = user["username"]

    return jsonify(
        {
            "message": "로그인 성공",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
            },
        }
    )


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "로그아웃 되었습니다."})


@app.route("/api/auth/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    user = query_db(
        "SELECT id, username, email, created_at FROM users WHERE id = %s",
        (user_id,),
        one=True,
    )

    if user is None:
        session.clear()
        return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

    return jsonify(
        {
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "created_at": user["created_at"].isoformat(),
            }
        }
    )


# ──────────────────────── Entry Point ─────────────────────────

with app.app_context():
    init_db(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
