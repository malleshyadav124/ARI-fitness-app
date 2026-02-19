from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.agents.aromi_agent import AromiAgent
from backend.auth.dependencies import get_current_user
from backend.database.session import get_db
from backend.models import User
from backend.models.schemas import HealthAssessmentCreate, HealthAssessmentResponse
from backend.services.health_assessment_service import create_health_assessment


router = APIRouter(prefix="/health-assessment", tags=["health-assessment"])


@router.post(
    "",
    response_model=HealthAssessmentResponse,
    status_code=201,
)
async def submit_assessment(
    payload: HealthAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    # Use logged-in user only
    payload = payload.model_copy(update={"user_id": current_user.id})
    agent = AromiAgent()
    summary = await agent.analyze_health_assessment(db, payload, current_user.id)
    assessment = create_health_assessment(db, payload, summary=summary)
    return HealthAssessmentResponse.model_validate(assessment)

