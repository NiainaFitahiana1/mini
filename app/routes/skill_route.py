from quart import Blueprint, request, jsonify, make_response
from sqlalchemy.future import select
from functools import wraps
from ..db import get_db
from ..models.skill import Skill
from ..security import decode_token
from ..config import Config

bp = Blueprint("skills", __name__)

# -------- Middleware Auth ----------
def require_auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return await cors_response("", 200)

        access = request.cookies.get("access_token")
        if not access:
            return await cors_response({"error": "Unauthorized"}, 401)
        try:
            payload = decode_token(access)
            if payload.get("type") != "access":
                return await cors_response({"error": "Unauthorized"}, 401)
        except Exception:
            return await cors_response({"error": "Unauthorized"}, 401)
        return await func(*args, **kwargs)
    return wrapper

# -------- CORS Helper ----------
async def cors_response(data, status=200):
    """Ajoute les headers CORS automatiquement"""
    if not isinstance(data, (str, bytes)):
        data = jsonify(data)
    resp = await make_response(data, status)
    resp.headers["Access-Control-Allow-Origin"] = Config.FRONT_ORIGIN
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp

# -------- Routes ----------
@bp.route("/skills", methods=["GET", "OPTIONS"])
async def get_skills():
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    async for session in get_db():
        result = await session.execute(select(Skill).where(Skill.user_id == 1))
        skills_list = result.scalars().all()
        return await cors_response([
            {
                "id": s.id,
                "icon": s.icon,
                "name": s.name,
                "level": s.level,
                "desc": s.desc
            } for s in skills_list
        ])

@bp.route("/skills", methods=["POST", "OPTIONS"])
@require_auth
async def create_skill():
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    data = await request.get_json() or {}
    required = {"icon", "name", "level"}
    missing = required - data.keys()
    if missing:
        return await cors_response({"error": f"Champs manquants: {missing}"}, 400)

    async for session in get_db():
        skill = Skill(
            user_id=1,
            icon=data["icon"],
            name=data["name"],
            level=data["level"],
            desc=data.get("desc")
        )
        session.add(skill)
        await session.commit()
        return await cors_response({"message": "Skill créé", "id": skill.id}, 201)

@bp.route("/skills/<int:id>", methods=["PUT", "OPTIONS"])
@require_auth
async def update_skill(id):
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    data = await request.get_json() or {}
    allowed = {"icon", "name", "level", "desc"}

    async for session in get_db():
        result = await session.execute(select(Skill).where(Skill.id == id, Skill.user_id == 1))
        skill = result.scalar_one_or_none()
        if not skill:
            return await cors_response({"error": "Skill non trouvé"}, 404)

        for k, v in data.items():
            if k in allowed:
                setattr(skill, k, v)

        await session.commit()
        return await cors_response({"message": "Skill mis à jour"})

@bp.route("/skills/<int:id>", methods=["DELETE", "OPTIONS"])
@require_auth
async def delete_skill(id):
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    async for session in get_db():
        result = await session.execute(select(Skill).where(Skill.id == id, Skill.user_id == 1))
        skill = result.scalar_one_or_none()
        if not skill:
            return await cors_response({"error": "Skill non trouvé"}, 404)

        await session.delete(skill)
        await session.commit()
        return await cors_response({"message": "Skill supprimé"})
