import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Base de données
    DB_URL = os.getenv("DB", "sqlite+aiosqlite:///data.db")

    # Clés secrètes
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JWT_SECRET = os.getenv("JWT_SECRET", "change-me-too")

    # Expirations JWT (en secondes)
    ACCESS_EXPIRES = int(os.getenv("ACCESS_EXPIRES_SECONDS", "900"))  # 15 min
    REFRESH_EXPIRES = int(os.getenv("REFRESH_EXPIRES_SECONDS", "1209600"))  # 14 jours

    # Frontend React
    FRONT_ORIGIN = os.getenv("FRONT_ORIGIN", "http://localhost:5174")

    # Cookies sécurisés (True en prod HTTPS)
    COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

    # Autres configs Quart
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # ✅ Correction du bug Quart + Flask-Sansio
    PROVIDE_AUTOMATIC_OPTIONS = True
