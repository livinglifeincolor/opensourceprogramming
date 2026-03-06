import os

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from db import close_db, init_db, query_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3000"],
)

app.teardown_appcontext(close_db)

POSTS_PER_PAGE = 10


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


# ──────────────────────── Post Routes ─────────────────────────


@app.route("/api/posts", methods=["GET"])
def get_posts():
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1

    offset = (page - 1) * POSTS_PER_PAGE

    # 전체 글 수
    count_result = query_db("SELECT COUNT(*) AS total FROM posts", one=True)
    total = count_result["total"] if count_result else 0

    # 글 목록 (최신순)
    posts = query_db(
        """
        SELECT p.id, p.title, p.created_at, p.updated_at,
               u.id AS user_id, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT %s OFFSET %s
        """,
        (POSTS_PER_PAGE, offset),
    )

    return jsonify(
        {
            "posts": [
                {
                    "id": post["id"],
                    "title": post["title"],
                    "author": post["username"],
                    "user_id": post["user_id"],
                    "created_at": post["created_at"].isoformat(),
                    "updated_at": post["updated_at"].isoformat(),
                }
                for post in posts
            ],
            "total": total,
            "page": page,
            "per_page": POSTS_PER_PAGE,
            "total_pages": max(1, -(-total // POSTS_PER_PAGE)),  # ceil division
        }
    )


@app.route("/api/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = query_db(
        """
        SELECT p.id, p.title, p.content, p.created_at, p.updated_at,
               u.id AS user_id, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = %s
        """,
        (post_id,),
        one=True,
    )

    if post is None:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    return jsonify(
        {
            "post": {
                "id": post["id"],
                "title": post["title"],
                "content": post["content"],
                "author": post["username"],
                "user_id": post["user_id"],
                "created_at": post["created_at"].isoformat(),
                "updated_at": post["updated_at"].isoformat(),
            }
        }
    )


@app.route("/api/posts", methods=["POST"])
def create_post():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    data = request.get_json()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not title or not content:
        return jsonify({"error": "제목과 내용을 모두 입력해주세요."}), 400

    if len(title) > 200:
        return jsonify({"error": "제목은 200자 이내로 입력해주세요."}), 400

    query_db(
        "INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)",
        (title, content, user_id),
    )

    return jsonify({"message": "게시글이 작성되었습니다."}), 201


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    post = query_db(
        "SELECT id, user_id FROM posts WHERE id = %s", (post_id,), one=True
    )
    if post is None:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    if post["user_id"] != user_id:
        return jsonify({"error": "수정 권한이 없습니다."}), 403

    data = request.get_json()
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not title or not content:
        return jsonify({"error": "제목과 내용을 모두 입력해주세요."}), 400

    if len(title) > 200:
        return jsonify({"error": "제목은 200자 이내로 입력해주세요."}), 400

    query_db(
        "UPDATE posts SET title = %s, content = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
        (title, content, post_id),
    )

    return jsonify({"message": "게시글이 수정되었습니다."})


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    post = query_db(
        "SELECT id, user_id FROM posts WHERE id = %s", (post_id,), one=True
    )
    if post is None:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    if post["user_id"] != user_id:
        return jsonify({"error": "삭제 권한이 없습니다."}), 403

    query_db("DELETE FROM posts WHERE id = %s", (post_id,))

    return jsonify({"message": "게시글이 삭제되었습니다."})


# ──────────────────────── Entry Point ─────────────────────────

with app.app_context():
    init_db(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
