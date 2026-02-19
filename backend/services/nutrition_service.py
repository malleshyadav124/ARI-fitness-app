from typing import Any, Dict, Optional, Tuple

import json
import httpx
from sqlalchemy.orm import Session

from backend.models import MealLog
from backend.utils.config import CALORIE_NINJAS_API_KEY


CALORIE_NINJAS_URL = "https://api.calorieninjas.com/v1/nutrition"


async def fetch_nutrition_from_api(description: str) -> Dict[str, Any]:
    if not CALORIE_NINJAS_API_KEY:
        raise RuntimeError("CALORIE_NINJAS_API_KEY is not configured")

    headers = {"X-Api-Key": CALORIE_NINJAS_API_KEY}
    params = {"query": description}

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(CALORIE_NINJAS_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


def extract_macros(nutrition_data: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    items = nutrition_data.get("items") or nutrition_data.get("items".upper()) or []
    if not items:
        return None, None, None, None

    total_calories = sum(float(item.get("calories", 0.0)) for item in items)
    total_protein = sum(float(item.get("protein_g", 0.0)) for item in items)
    total_carbs = sum(float(item.get("carbohydrates_total_g", 0.0)) for item in items)
    total_fat = sum(float(item.get("fat_total_g", 0.0)) for item in items)
    return total_calories, total_protein, total_carbs, total_fat


async def log_meal(
    db: Session, user_id: Optional[int], description: str
) -> MealLog:
    nutrition_data = await fetch_nutrition_from_api(description)
    calories, protein_g, carbs_g, fat_g = extract_macros(nutrition_data)

    meal = MealLog(
        user_id=user_id,
        description=description,
        nutrition_json=json.dumps(nutrition_data),
        calories=calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
    )
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal

