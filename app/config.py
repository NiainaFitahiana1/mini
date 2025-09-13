import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_URL = os.getenv("DB", "postgresql://minibase_user:Oo2nf57Bct1F20kIZ1aZXuqnHALoM1b7@dpg-d32iokemcj7s739kbl60-a.oregon-postgres.render.com/minibase")

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JWT_SECRET = os.getenv("JWT_SECRET", "change-me-too")

    ACCESS_EXPIRES = int(os.getenv("ACCESS_EXPIRES_SECONDS", "900"))  # 15 min
    REFRESH_EXPIRES = int(os.getenv("REFRESH_EXPIRES_SECONDS", "1209600"))  # 14 jours

    FRONT_ORIGIN = os.getenv("FRONT_ORIGIN", "https://mn-f-33e7.vercel.app/")

    COOKIE_SECURE = os.getenv("COOKIE_SECURE", "True").lower() == "true"

    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    PROVIDE_AUTOMATIC_OPTIONS = True
