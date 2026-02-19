from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.agents.aromi_agent import AromiAgent
from backend.auth.dependencies import get_current_user
from backend.database.session import get_db
from backend.models import User
from backend.models.schemas import ChatRequest, ChatResponse


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def aromi_chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    # Use logged-in user only
    payload = payload.model_copy(update={"user_id": current_user.id})
    agent = AromiAgent()
    response, _ = await agent.chat(db, payload)
    return response

