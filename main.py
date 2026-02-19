from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import router as auth_router
from backend.database.init_db import create_tables
from backend.utils.config import FRONTEND_ORIGINS
from backend.routers import (
    health_assessment,
    chat,
    dashboard,
    meal_analysis,
    plans,
)


def create_app() -> FastAPI:
    app = FastAPI(title="ArogyaMitra API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=FRONTEND_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth_router)  # ✅ FIXED HERE
    app.include_router(health_assessment.router)
    app.include_router(chat.router)
    app.include_router(dashboard.router)
    app.include_router(meal_analysis.router)
    app.include_router(plans.router)

    @app.on_event("startup")
    async def _startup() -> None:
        create_tables()

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
