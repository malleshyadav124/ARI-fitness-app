from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database.session import get_db
from backend.models import ChatHistory, MealLog, User, WorkoutPlan
from backend.models.schemas import DashboardData, HealthAssessmentResponse
from backend.services.health_assessment_service import get_latest_assessment


router = APIRouter(prefix="/dashboard-data", tags=["dashboard"])


@router.get("", response_model=DashboardData)
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    resolved_user_id = current_user.id
    latest_assessment = get_latest_assessment(db, resolved_user_id)
    latest_assessment_schema = (
        HealthAssessmentResponse.model_validate(latest_assessment)
        if latest_assessment
        else None
    )
    total_workouts = (
        db.query(func.count(WorkoutPlan.id))
        .filter(WorkoutPlan.user_id == resolved_user_id)
        .scalar()
        or 0
    )
    total_meals = (
        db.query(func.count(MealLog.id))
        .filter(MealLog.user_id == resolved_user_id)
        .scalar()
        or 0
    )
    total_messages = (
        db.query(func.count(ChatHistory.id))
        .filter(ChatHistory.user_id == resolved_user_id)
        .scalar()
        or 0
    )
    return DashboardData(
        latest_assessment=latest_assessment_schema,
        total_workouts=total_workouts,
        total_meals=total_meals,
        total_messages=total_messages,
    )

