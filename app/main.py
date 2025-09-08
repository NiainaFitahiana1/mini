from quart import Quart
from quart_cors import cors
from .config import Config
from .routes.auth_routes import bp as auth_bp
from .routes.user_routes import bp as user_bp
from .routes.parcours_route import bp as parcours_bp
from .routes.projets_routes import bp as projets_bp
from .routes.services_routes import bp as services_bp
from .routes.skill_route import bp as skills_bp

def create_app() -> Quart:
    app = Quart(__name__)

    # 🩹 Patch pour Quart ≥0.19 (avec flask-sansio)
    if "PROVIDE_AUTOMATIC_OPTIONS" not in app.config:
        app.config["PROVIDE_AUTOMATIC_OPTIONS"] = True

    # CORS global
    app = cors(
        app,
        allow_origin=Config.FRONT_ORIGIN,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Authorization"],
    )

    # Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(parcours_bp, url_prefix="/parc")
    app.register_blueprint(projets_bp, url_prefix="/pjt")
    app.register_blueprint(services_bp, url_prefix="/srv")
    app.register_blueprint(skills_bp, url_prefix="/skl")

    return app


app = create_app()
