from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from backend.utils.config import (
    ACCESS_TOKEN_EXPIRE_HOURS,
    JWT_ALGORITHM,
    JWT_SECRET,
)

# 🚀 DEMO MODE: No bcrypt

def hash_password(password: str) -> str:
    return password  # store as-is for demo

def verify_password(plain: str, hashed: str) -> bool:
    return plain == hashed  # simple check

def create_access_token(subject: str | int, extra: Optional[dict[str, Any]] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {"sub": str(subject), "exp": expire}
    if extra:
        to_encode.update(extra)
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
