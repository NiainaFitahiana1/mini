from quart import Blueprint, request, jsonify, make_response
from sqlalchemy.future import select
from functools import wraps
from ..db import get_db
from ..models.parcours import Parcours
from ..security import decode_token

bp = Blueprint("parcours", __name__)

# -------- Middleware Auth ----------
def require_auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
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
    return wrapper


# -------- Helper CORS ----------
def cors_response(data, status=200):
    """Ajoute les headers CORS automatiquement"""
    resp = make_response(data, status)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp


# -------- Routes ----------
@bp.route("/parcours", methods=["GET", "OPTIONS"])
async def get_parcours():
    if request.method == "OPTIONS":
        return cors_response("", 200)

    async for session in get_db():
        result = await session.execute(select(Parcours).where(Parcours.user_id == 1))
        parcours_list = result.scalars().all()
        return cors_response(jsonify([{
            "id": p.id,
            "year": p.year,
            "role": p.role,
            "company": p.company,
            "description": p.description,
            "stack": p.stack.split(",") if p.stack else []  # 🔥 split string -> liste
        } for p in parcours_list]))


@bp.route("/parcours", methods=["POST", "OPTIONS"])
@require_auth
async def create_parcours():
    if request.method == "OPTIONS":
        return cors_response("", 200)

    data = await request.get_json() or {}
    required = {"year", "role", "company", "description"}
    if not required.issubset(data.keys()):
        return cors_response(
            jsonify({"error": f"Champs manquants: {required - set(data.keys())}"}), 400
        )

    async for session in get_db():
        parcours = Parcours(
            user_id=1,
            year=data["year"],
            role=data["role"],
            company=data["company"],
            description=data["description"],
            stack=",".join(data.get("stack", [])) if isinstance(data.get("stack"), list) else data.get("stack", "")
        )
        session.add(parcours)
        await session.commit()
        return cors_response(jsonify({"message": "Parcours créé", "id": parcours.id}), 201)


@bp.route("/parcours/<int:id>", methods=["PUT", "OPTIONS"])
@require_auth
async def update_parcours(id):
    if request.method == "OPTIONS":
        return cors_response("", 200)

    data = await request.get_json() or {}
    allowed = {"year", "role", "company", "description", "stack"}

    async for session in get_db():
        result = await session.execute(select(Parcours).where(Parcours.id == id, Parcours.user_id == 1))
        parcours = result.scalar_one_or_none()
        if not parcours:
            return cors_response(jsonify({"error": "Parcours non trouvé"}), 404)

        for k, v in data.items():
            if k in allowed:
                if k == "stack" and isinstance(v, list):
                    setattr(parcours, k, ",".join(v))  # 🔥 on stock en string
                else:
                    setattr(parcours, k, v)

        await session.commit()
        return cors_response(jsonify({"message": "Parcours mis à jour"}))


@bp.route("/parcours/<int:id>", methods=["DELETE", "OPTIONS"])
@require_auth
async def delete_parcours(id):
    if request.method == "OPTIONS":
        return cors_response("", 200)

    async for session in get_db():
        result = await session.execute(select(Parcours).where(Parcours.id == id, Parcours.user_id == 1))
        parcours = result.scalar_one_or_none()
        if not parcours:
            return cors_response(jsonify({"error": "Parcours non trouvé"}), 404)

        await session.delete(parcours)
        await session.commit()
        return cors_response(jsonify({"message": "Parcours supprimé"}))
