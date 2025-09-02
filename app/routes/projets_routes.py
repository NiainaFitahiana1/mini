from quart import Blueprint, request, jsonify, make_response
from sqlalchemy.future import select
from functools import wraps
from ..db import get_db
from ..models.projets import Projets
from ..security import decode_token
from ..config import Config

bp = Blueprint("projets", __name__)

# -------- Middleware Auth ----------
def require_auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Autoriser OPTIONS avant auth
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
@bp.route("/projets", methods=["GET", "OPTIONS"])
async def get_projets():
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    async for session in get_db():
        result = await session.execute(select(Projets).where(Projets.user_id == 1))
        projets_list = result.scalars().all()
        return await cors_response([
            {
                "id": p.id,
                "title": p.title,
                "desc": p.desc,
                "type": p.type,
                "demo": p.demo,
                "repo": p.repo,
                "photo": p.photo
            } for p in projets_list
        ])

@bp.route("/projets", methods=["POST", "OPTIONS"])
@require_auth
async def create_projet():
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    data = await request.get_json() or {}
    required = {"title", "desc", "type"}
    missing = required - data.keys()
    if missing:
        return await cors_response({"error": f"Champs manquants: {missing}"}, 400)

    async for session in get_db():
        projet = Projets(
            user_id=1,
            title=data["title"],
            desc=data["desc"],
            type=data["type"],
            demo=data.get("demo", ""),
            repo=data.get("repo", ""),
            photo=data.get("photo", "")
        )
        session.add(projet)
        await session.commit()
        return await cors_response({"message": "Projet créé", "id": projet.id}, 201)

@bp.route("/projets/<int:id>", methods=["PUT", "OPTIONS"])
@require_auth
async def update_projet(id):
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    data = await request.get_json() or {}
    allowed = {"title", "desc", "type", "demo", "repo", "photo"}

    async for session in get_db():
        result = await session.execute(select(Projets).where(Projets.id == id, Projets.user_id == 1))
        projet = result.scalar_one_or_none()
        if not projet:
            return await cors_response({"error": "Projet non trouvé"}, 404)

        for k, v in data.items():
            if k in allowed:
                setattr(projet, k, v)

        await session.commit()
        return await cors_response({"message": "Projet mis à jour"})

@bp.route("/projets/<int:id>", methods=["DELETE", "OPTIONS"])
@require_auth
async def delete_projet(id):
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    async for session in get_db():
        result = await session.execute(select(Projets).where(Projets.id == id, Projets.user_id == 1))
        projet = result.scalar_one_or_none()
        if not projet:
            return await cors_response({"error": "Projet non trouvé"}, 404)

        await session.delete(projet)
        await session.commit()
        return await cors_response({"message": "Projet supprimé"})