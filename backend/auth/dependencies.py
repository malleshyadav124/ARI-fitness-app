from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models import User
from backend.utils.auth import decode_access_token

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=True)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(OAUTH2_SCHEME),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    sub = payload.get("sub")
    if not sub:
        raise credentials_exception
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if user.hashed_password is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account must be used with login (no password set)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
