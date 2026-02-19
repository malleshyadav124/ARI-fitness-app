from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database.session import get_db
from backend.models import User
from backend.models.schemas import MealAnalysisRequest, MealAnalysisResponse
from backend.services.nutrition_service import log_meal


router = APIRouter(prefix="/meal-analysis", tags=["nutrition"])


@router.post("", response_model=MealAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_meal(
    payload: MealAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    if not payload.description:
        raise HTTPException(status_code=400, detail="description is required")
    meal = await log_meal(db, current_user.id, payload.description)

    return MealAnalysisResponse(
        calories=meal.calories,
        protein_g=meal.protein_g,
        carbs_g=meal.carbs_g,
        fat_g=meal.fat_g,
        raw={},  # keep payload small for dashboard; frontend can call another endpoint if needed
    )

