import os

from dotenv import load_dotenv

load_dotenv()


GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
CALORIE_NINJAS_API_KEY: str = os.getenv("CALORIE_NINJAS_API_KEY", "")
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./arogyamitra.db")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# JWT auth
JWT_SECRET: str = os.getenv("JWT_SECRET", "arogyamitra-secret-change-in-production")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))

_default_origins = "http://localhost:3000,http://localhost:5173"
FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", _default_origins).split(",")
