from quart import Blueprint, request, jsonify, make_response
from sqlalchemy.future import select
from ..db import get_db
from ..models.user import User
from ..security import verify_password, create_token, decode_token
from ..config import Config

bp = Blueprint("auth", __name__)

def set_auth_cookies(resp, access_token: str, refresh_token: str):
    # Cookies HttpOnly, SameSite, Secure selon .env
    # resp.set_cookie(
    #     "access_token",
    #     access_token,
    #     httponly=True,
    #     secure=Config.COOKIE_SECURE,
    #     samesite="None",
    #     path="/",
    # )
    # resp.set_cookie(
    #     "refresh_token",
    #     refresh_token,
    #     httponly=True,
    #     secure=Config.COOKIE_SECURE,
    #     samesite="None",   # <-- au lieu de Lax
    #     path="/api/auth/",
    # )
    resp.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        # secure=False,    # car localhost HTTP
        # samesite="Lax",  # ou "Strict"
        path="/",
    )
    resp.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        # secure=False,
        # samesite="Lax",
        path="/api/auth/",
    )
    return resp

def clear_auth_cookies(resp):
    resp.delete_cookie("access_token", path="/")
    resp.delete_cookie("refresh_token", path="/api/auth/")
    return resp

# --- LOGIN ---
@bp.route("/login", methods=["POST", "OPTIONS"])
async def login():
    if request.method == "OPTIONS":
        # réponse pour le preflight
        return "", 200

    data = await request.get_json()
    email = (data or {}).get("email", "").strip().lower()
    password = (data or {}).get("password", "")

    async for session in get_db():
        result = await session.execute(select(User).where(User.id == 1))
        user = result.scalar_one_or_none()

        if not user or user.email != email:
            return jsonify({"error": "Identifiants invalides"}), 401

        if not verify_password(user.password_hash, password):
            return jsonify({"error": "Identifiants invalides"}), 401

        access = create_token(sub=str(user.id), ttl_seconds=Config.ACCESS_EXPIRES, typ="access")
        refresh = create_token(sub=str(user.id), ttl_seconds=Config.REFRESH_EXPIRES, typ="refresh")

        resp = await make_response(
            jsonify({
                "message": "ok",
                "access_token": access,  # si frontend veut le stocker localement
            }),
            200,
        )
        return set_auth_cookies(resp, access, refresh)
    
@bp.route("/me", methods=["GET"])
async def me():
    access_cookie = request.cookies.get("access_token")
    if not access_cookie:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        payload = decode_token(access_cookie)
        if payload.get("type") != "access":
            return jsonify({"error": "Bad token type"}), 401
    except Exception:
        return jsonify({"error": "Invalid token"}), 401

    user_id = payload["sub"]

    async for session in get_db():
        result = await session.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "id": user.id,
            "nom": user.nom,
            "prenom": user.prenom,
            "email": user.email,
            "bio": user.bio,
            "specialite": user.specialite,
            "adresse": user.adresse,
            "telephone": user.telephone,
            "disponibilite": user.disponibilite,
            "lien_github": user.lien_github,
            "lien_linkedin": user.lien_linkedin,
            "lien_dribbble": user.lien_dribbble,
            "lien_avatar": user.lien_avatar,
        })

# --- REFRESH ---
@bp.route("/refresh", methods=["POST", "OPTIONS"])
async def refresh():
    if request.method == "OPTIONS":
        return "", 200

    refresh_cookie = request.cookies.get("refresh_token")
    if not refresh_cookie:
        return jsonify({"error": "No refresh token"}), 401

    try:
        payload = decode_token(refresh_cookie)
        if payload.get("type") != "refresh":
            return jsonify({"error": "Bad token type"}), 401
    except Exception:
        return jsonify({"error": "Invalid token"}), 401

    access = create_token(sub=payload["sub"], ttl_seconds=Config.ACCESS_EXPIRES, typ="access")
    resp = await make_response(jsonify({"message": "refreshed", "access_token": access}), 200)
    return set_auth_cookies(resp, access, refresh_cookie)


# --- LOGOUT ---
@bp.route("/logout", methods=["POST", "OPTIONS"])
async def logout():
    if request.method == "OPTIONS":
        return "", 200

    resp = await make_response(jsonify({"message": "bye"}), 200)
    return clear_auth_cookies(resp)
