from quart import Blueprint, request, jsonify, make_response
from sqlalchemy.future import select
from functools import wraps
from ..db import get_db
from ..models.service import Service
from ..security import decode_token
from ..config import Config

bp = Blueprint("services", __name__)

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
@bp.route("/services", methods=["GET", "OPTIONS"])
async def get_services():
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    async for session in get_db():
        result = await session.execute(select(Service).where(Service.user_id == 1))
        services_list = result.scalars().all()
        return await cors_response([
            {
                "id": s.id,
                "icon": s.icon,
                "title": s.title,
                "desc": s.desc
            } for s in services_list
        ])

@bp.route("/services", methods=["POST", "OPTIONS"])
@require_auth
async def create_service():
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    data = await request.get_json() or {}
    required = {"icon", "title", "desc"}
    missing = required - data.keys()
    if missing:
        return await cors_response({"error": f"Champs manquants: {missing}"}, 400)

    async for session in get_db():
        service = Service(
            user_id=1,
            icon=data["icon"],
            title=data["title"],
            desc=data["desc"]
        )
        session.add(service)
        await session.commit()
        return await cors_response({"message": "Service créé", "id": service.id}, 201)

@bp.route("/services/<int:id>", methods=["PUT", "OPTIONS"])
@require_auth
async def update_service(id):
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    data = await request.get_json() or {}
    allowed = {"icon", "title", "desc"}

    async for session in get_db():
        result = await session.execute(select(Service).where(Service.id == id, Service.user_id == 1))
        service = result.scalar_one_or_none()
        if not service:
            return await cors_response({"error": "Service non trouvé"}, 404)

        for k, v in data.items():
            if k in allowed:
                setattr(service, k, v)

        await session.commit()
        return await cors_response({"message": "Service mis à jour"})

@bp.route("/services/<int:id>", methods=["DELETE", "OPTIONS"])
@require_auth
async def delete_service(id):
    if request.method == "OPTIONS":
        return await cors_response("", 200)

    async for session in get_db():
        result = await session.execute(select(Service).where(Service.id == id, Service.user_id == 1))
        service = result.scalar_one_or_none()
        if not service:
            return await cors_response({"error": "Service non trouvé"}, 404)

        await session.delete(service)
        await session.commit()
        return await cors_response({"message": "Service supprimé"})