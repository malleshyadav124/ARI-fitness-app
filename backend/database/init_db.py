from sqlalchemy.orm import Session

from backend.database.session import Base, engine
from backend.models import User  # noqa: F401 (ensure models imported)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)

def ensure_demo_user(db: Session) -> int:
    existing = db.query(User).filter(User.email == "demo@arogyamitra.local").first()
    if existing:
        return existing.id

    user = User(
        name="Demo User",
        email="demo@arogyamitra.local",
        hashed_password="demo"  # required field
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id

