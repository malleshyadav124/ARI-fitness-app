from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthAssessmentCreate(BaseModel):
    user_id: Optional[int] = None
    answers: List[str] = Field(..., min_length=12, max_length=12)
    metadata: Optional[Dict[str, Any]] = None


class HealthAssessmentResponse(BaseModel):
    id: int
    user_id: int
    summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    user_id: Optional[int] = None
    message: str
    session_id: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    reply: str
    tool_used: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None


class MealAnalysisRequest(BaseModel):
    user_id: Optional[int] = None
    description: str


class MealAnalysisResponse(BaseModel):
    calories: Optional[float]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    raw: Dict[str, Any]


class GeneratePlanRequest(BaseModel):
    user_id: Optional[int] = None
    goal: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class WorkoutPlanResponse(BaseModel):
    id: int
    user_id: int
    goal: Optional[str]
    plan_json: str
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardData(BaseModel):
    latest_assessment: Optional[HealthAssessmentResponse] = None
    total_workouts: int = 0
    total_meals: int = 0
    total_messages: int = 0

