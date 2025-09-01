from quart import Blueprint, request, jsonify
from sqlalchemy.future import select
from ..db import get_db
from ..models.user import User
from ..security import decode_token
from ..config import Config

bp = Blueprint("user", __name__)

def require_auth(func):
    async def wrapper(*args, **kwargs):
        from functools import wraps
        access = request.cookies.get("access_token")
        if not access:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            payload = decode_token(access)
            if payload.get("type") != "access":
                return jsonify({"error": "Unauthorized"}), 401
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
        return await func(*args, **kwargs)
    from functools import wraps
    return wraps(func)(wrapper)

@bp.get("/user")
async def get_user_public():
    # Exposition publique des champs non sensibles
    async for session in get_db():
        result = await session.execute(select(User).where(User.id == 1))
        user = result.scalar_one_or_none()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "nom": user.nom,
            "prenom": user.prenom,
            "bio": user.bio,
            "specialite": user.specialite,
            "lien_github": user.lien_github,
            "lien_linkedin": user.lien_linkedin,
            "lien_dribbble": user.lien_dribbble,
            "telephone": user.telephone,
            "email": user.email,
            "adresse": user.adresse,
            "disponibilite": user.disponibilite,
            "lien_avatar":user.lien_avatar,
        })

@bp.get("/me")
@require_auth
async def me():
    async for session in get_db():
        result = await session.execute(select(User).where(User.id == 1))
        user = result.scalar_one_or_none()
        return jsonify({"id": 1, "email": user.email})

@bp.put("/user")
@require_auth
async def update_user():
    data = await request.get_json() or {}
    whitelist = {
        "nom", "prenom", "bio", "specialite", "lien_github", "lien_linkedin",
        "lien_dribbble", "telephone", "email", "adresse", "disponibilite", "lien_avatar"
    }
    updates = {k: v for k, v in data.items() if k in whitelist}

    # Validation simple
    if "email" in updates and (not isinstance(updates["email"], str) or "@" not in updates["email"]):
        return jsonify({"error": "Email invalide"}), 400
    if "disponibilite" in updates and not isinstance(updates["disponibilite"], bool):
        return jsonify({"error": "Disponibilite doit être bool"}), 400

    async for session in get_db():
        result = await session.execute(select(User).where(User.id == 1))
        user = result.scalar_one_or_none()
        if not user:
            return jsonify({"error": "User not found"}), 404

        for k, v in updates.items():
            setattr(user, k, v)

        await session.commit()
        return jsonify({
            "message": "updated",
            "user": {c.name: getattr(user, c.name) for c in user.__table__.columns}
        })
