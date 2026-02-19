from typing import Optional

from sqlalchemy.orm import Session

from backend.models import User


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_or_create_demo_user(db: Session) -> User:
    user = get_user(db, 1)
    if user:
        return user
    user = User(name="Demo User", email="demo@arogyamitra.local")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

