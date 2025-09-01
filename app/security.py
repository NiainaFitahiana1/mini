import time
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from .config import Config

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(hash_: str, password: str) -> bool:
    try:
        ph.verify(hash_, password)
        return True
    except VerifyMismatchError:
        return False

def create_token(sub: str, ttl_seconds: int, typ: str):
    now = int(time.time())
    payload = {
        "sub": sub,
        "type": typ,
        "iat": now,
        "exp": now + ttl_seconds,
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

def decode_token(token: str):
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
