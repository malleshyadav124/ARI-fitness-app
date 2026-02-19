from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.agents.aromi_agent import AromiAgent
from backend.auth.dependencies import get_current_user
from backend.database.session import get_db
from backend.models import User, WorkoutPlan
from backend.models.schemas import GeneratePlanRequest, WorkoutPlanResponse


router = APIRouter(prefix="/generate-plan", tags=["plans"])


@router.post("", response_model=WorkoutPlanResponse, status_code=status.HTTP_201_CREATED)
async def generate_plan(
    payload: GeneratePlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    payload = payload.model_copy(update={"user_id": current_user.id})
    agent = AromiAgent()
    plan = agent.generate_workout_plan(db, payload, current_user.id)
    return WorkoutPlanResponse.model_validate(plan)


@router.get("/{plan_id}", response_model=WorkoutPlanResponse)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return WorkoutPlanResponse.model_validate(plan)

